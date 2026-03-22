"""Unified CLI entry point for devpace eval toolkit.

Usage:
  python3 -m eval trigger   --skill pace-dev [--runs N] [--timeout T] [--max-turns M]
  python3 -m eval loop      --skill pace-dev --model MODEL [--iterations N]
  python3 -m eval regress   [--threshold 0.1]
  python3 -m eval baseline  save|diff --skill pace-dev
  python3 -m eval changed   [--base origin/main]
  python3 -m eval behavior  --skill pace-dev [--case N] [--smoke] [--timeout T]
  python3 -m eval benchmark --skill pace-dev [--runs N]
  python3 -m eval report    [--open]
  python3 -m eval viewer    --skill pace-dev [--port P]
  python3 -m eval note      --skill pace-dev --case N --note "..."
  python3 -m eval notes     [--skill pace-dev] [--pending] [--stale]
  python3 -m eval compare   --skill pace-dev --old HEAD~5 --new HEAD
  python3 -m eval analyze   [--skill pace-dev]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .core import (
    DEVPACE_ROOT, EVAL_DATA_DIR, SKILLS_DIR,
    build_metadata, read_description, save_trigger_results,
)
from .trigger import DEFAULT_MAX_TURNS, DEFAULT_RUNS, DEFAULT_TIMEOUT, run_eval_set
from .regression import detect_changed_skills, run_regress, diff_baseline, save_baseline


def _load_eval_cases(skill_name: str) -> list[dict] | None:
    """Load behavioral eval cases for a skill. Returns None if not found."""
    eval_file = EVAL_DATA_DIR / skill_name / "evals.json"
    if not eval_file.exists():
        print(f"Error: {eval_file} not found", file=sys.stderr)
        return None
    data = json.loads(eval_file.read_text())
    return data.get("evals", [])


def cmd_trigger(args: argparse.Namespace) -> int:
    """Run trigger evaluation."""
    skill_name = args.skill
    skill_dir = SKILLS_DIR / skill_name
    eval_file = EVAL_DATA_DIR / skill_name / "trigger-evals.json"

    if not skill_dir.is_dir():
        print(f"Error: skill directory not found: {skill_dir}", file=sys.stderr)
        return 1
    if not eval_file.exists():
        print(f"Error: eval file not found: {eval_file}", file=sys.stderr)
        return 1

    eval_set = json.loads(eval_file.read_text())
    if args.smoke:
        pos = [e for e in eval_set if e.get("should_trigger")]
        neg = [e for e in eval_set if not e.get("should_trigger")]
        eval_set = pos[:3] + neg[:max(args.smoke_n - 3, 2)]

    description = read_description(skill_dir)
    timeout = args.timeout
    runs = args.runs
    max_turns = args.max_turns

    mode = "with-hooks (e2e)" if args.with_hooks else "description-only"
    print(f"  skill: {skill_name} [{mode}]", file=sys.stderr)
    print(f"  timeout: {timeout}s, runs: {runs}, max_turns: {max_turns}, queries: {len(eval_set)}", file=sys.stderr)

    raw = run_eval_set(
        eval_set=eval_set, skill_name=skill_name, description=description,
        num_workers=min(10, len(eval_set)), timeout=timeout,
        project_root=str(DEVPACE_ROOT),
        runs_per_query=runs, model=args.model,
        max_turns=max_turns,
        with_hooks=args.with_hooks,
    )

    metadata = build_metadata(
        model=args.model,
        max_turns=max_turns,
        timeout=timeout,
        runs_per_query=runs,
        duration_seconds=raw.get("duration_seconds"),
    )
    latest = save_trigger_results(skill_name, raw, metadata=metadata)

    s = raw["summary"]
    print(f"  results: {latest.relative_to(DEVPACE_ROOT)}", file=sys.stderr)
    print(f"\n  {skill_name}: {s['passed']}/{s['total']} passed", file=sys.stderr)
    print(json.dumps(raw, indent=2, ensure_ascii=False))
    return 0 if s["failed"] == 0 else 1


def cmd_loop(args: argparse.Namespace) -> int:
    """Run description optimization loop."""
    from .trigger import run_loop
    return run_loop(
        skill_name=args.skill,
        model=args.model,
        iterations=args.iterations,
        timeout=args.timeout,
        runs=args.runs,
        max_turns=args.max_turns,
        holdout=args.holdout,
        seed=args.seed,
    )


def cmd_regress(args: argparse.Namespace) -> int:
    """Run regression check."""
    return run_regress(threshold=args.threshold)


def cmd_baseline(args: argparse.Namespace) -> int:
    """Manage baselines."""
    if args.baseline_action == "save":
        return save_baseline(args.skill)
    if args.baseline_action == "diff":
        return diff_baseline(args.skill)
    return 1


def cmd_changed(args: argparse.Namespace) -> int:
    """Show changed skills relative to a git ref."""
    changed = detect_changed_skills(args.base)
    if not changed:
        print("  no skill changes detected")
        return 0
    for s in changed:
        print(f"  changed: {s}")
    return 0


def cmd_behavior(args: argparse.Namespace) -> int:
    """Run behavioral evaluation."""
    from .behavior import run_behavioral_eval_set, save_behavioral_results
    from .behavior.grader import Grader, grade_eval_case, save_grading_results

    skill_name = args.skill
    eval_cases = _load_eval_cases(skill_name)
    if eval_cases is None:
        return 1

    case_ids = [args.case] if args.case is not None else None
    timeout = args.timeout
    model = args.model

    print(f"Running behavioral eval for {skill_name}...", file=sys.stderr)
    results = asyncio.run(
        run_behavioral_eval_set(
            skill_name=skill_name,
            eval_cases=eval_cases,
            timeout=timeout,
            model=model,
            case_ids=case_ids,
            smoke=args.smoke,
        )
    )

    save_behavioral_results(skill_name, results)

    # Grade results
    grader = Grader()
    grading_outputs = []
    for r in results:
        case = next((c for c in eval_cases if c["id"] == r.eval_id), None)
        if case:
            grading_outputs.append(grade_eval_case(grader, case, r))

    if grading_outputs:
        out_path = save_grading_results(skill_name, grading_outputs)
        print(f"Grading saved: {out_path.relative_to(DEVPACE_ROOT)}", file=sys.stderr)

    # Summary
    total_a = sum(g["summary"]["total"] for g in grading_outputs)
    total_p = sum(g["summary"]["passed"] for g in grading_outputs)
    print(f"\n{skill_name}: {total_p}/{total_a} assertions passed across {len(results)} cases", file=sys.stderr)
    print(json.dumps(grading_outputs, indent=2, ensure_ascii=False))
    return 0 if total_p == total_a else 1


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Run with/without benchmark comparison."""
    from .behavior.benchmark import run_benchmark, save_benchmark_results

    skill_name = args.skill
    eval_cases = _load_eval_cases(skill_name)
    if eval_cases is None:
        return 1
    runs = args.runs
    model = args.model

    print(f"Running benchmark for {skill_name} ({runs} runs per case)...", file=sys.stderr)
    result = asyncio.run(
        run_benchmark(
            skill_name=skill_name,
            eval_cases=eval_cases,
            runs_per_case=runs,
            model=model,
        )
    )

    out_path = save_benchmark_results(skill_name, result)
    print(f"Benchmark saved: {out_path.relative_to(DEVPACE_ROOT)}", file=sys.stderr)

    output = result.to_dict()
    wp = output["configurations"]["with_plugin"]["pass_rate"]
    wo = output["configurations"]["without_plugin"]["pass_rate"]
    delta = output["configurations"]["delta"]
    print(f"\nWith plugin:    {wp['mean']:.1%} +/- {wp['stddev']:.1%}", file=sys.stderr)
    print(f"Without plugin: {wo['mean']:.1%} +/- {wo['stddev']:.1%}", file=sys.stderr)
    print(f"Delta:          {delta['pass_rate']}", file=sys.stderr)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Generate static HTML dashboard."""
    from .review.report import write_dashboard

    html_path = write_dashboard()
    print(f"Dashboard: {html_path}", file=sys.stderr)
    if args.open:
        import webbrowser
        webbrowser.open(f"file://{html_path}")
    return 0


def cmd_viewer(args: argparse.Namespace) -> int:
    """Start interactive eval viewer server."""
    from .review.viewer import start_viewer
    from .core.results import results_dir_for

    skill_name = args.skill
    workspace = results_dir_for(skill_name)
    port = args.port
    start_viewer(workspace_dir=workspace, port=port)
    return 0


def cmd_note(args: argparse.Namespace) -> int:
    """Add an eval feedback note."""
    from .review.feedback import append_note

    append_note(
        skill=args.skill,
        eval_id=args.case,
        note=args.note,
        note_type=args.type,
        author=args.author,
    )
    print("Note added.", file=sys.stderr)
    return 0


def cmd_notes(args: argparse.Namespace) -> int:
    """List eval feedback notes."""
    from .review.feedback import list_notes, list_pending, list_stale

    skill = args.skill
    pending = args.pending
    stale = args.stale

    if pending:
        notes = list_pending(skill=skill)
    elif stale and skill:
        notes = list_stale(skill=skill)
    elif skill:
        notes = list_notes(skill=skill)
    else:
        notes = list_pending()

    for n in notes:
        status = "OPEN" if not n.resolved else "RESOLVED"
        text = n.note[:80] if n.note else ""
        print(f"[{status}] {n.skill}#{n.eval_id}: {text}")

    print(f"\nTotal: {len(notes)} notes", file=sys.stderr)
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """Run blind A/B comparison between skill versions."""
    from .behavior.comparator import blind_compare, save_comparison_results

    skill_name = args.skill
    eval_cases = _load_eval_cases(skill_name)
    if eval_cases is None:
        return 1

    case_ids = [args.case] if args.case is not None else None
    cases = [c for c in eval_cases if case_ids is None or c["id"] in case_ids][:3]

    async def _run_comparisons():
        return await asyncio.gather(*(
            blind_compare(
                skill_name=skill_name,
                eval_case=case,
                version_a_ref=args.old,
                version_b_ref=args.new,
            )
            for case in cases
        ), return_exceptions=True)

    raw_results = asyncio.run(_run_comparisons())
    results = []
    for case, r in zip(cases, raw_results):
        if isinstance(r, Exception):
            print(f"Case {case['id']} error: {r}", file=sys.stderr)
            continue
        results.append(r)
        winner = r.winner
        print(f"Case {case['id']} ({case['name']}): winner={winner}", file=sys.stderr)

    out_path = save_comparison_results(skill_name, results)
    print(f"\nComparison saved: {out_path.relative_to(DEVPACE_ROOT)}", file=sys.stderr)
    print(json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Run assertion quality analysis."""
    from .review.analyzer import analyze_assertion_quality

    skill = args.skill

    # Collect behavior results from grading/ directories
    behavior_results: list[dict] = []
    search_dir = EVAL_DATA_DIR
    if skill:
        grading_file = search_dir / skill / "results" / "grading" / "grading.json"
        if grading_file.exists():
            data = json.loads(grading_file.read_text())
            behavior_results = data.get("cases", [])
    else:
        for skill_dir in search_dir.iterdir():
            grading_file = skill_dir / "results" / "grading" / "grading.json"
            if grading_file.exists():
                data = json.loads(grading_file.read_text())
                behavior_results.extend(data.get("cases", []))

    if not behavior_results:
        print("No behavior results found. Run behavioral eval first.", file=sys.stderr)
        return 1

    report = analyze_assertion_quality(behavior_results)

    output = {
        "total_assertions": report.total_assertions,
        "total_runs": report.total_runs,
        "issue_count": report.issue_count,
        "summary": report.summary,
        "issues": [
            {
                "skill": i.skill,
                "eval_id": i.eval_id,
                "eval_name": i.eval_name,
                "assertion_idx": i.assertion_idx,
                "assertion_text": i.assertion_text,
                "issue_type": i.issue_type,
                "detail": i.detail,
                "severity": i.severity,
            }
            for i in report.issues
        ],
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    p = argparse.ArgumentParser(
        prog="python3 -m eval",
        description="devpace skill evaluation toolkit",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # trigger
    t = sub.add_parser("trigger", help="Run trigger evaluation")
    t.add_argument("--skill", "-s", required=True)
    t.add_argument("--runs", "-r", type=int, default=DEFAULT_RUNS)
    t.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT)
    t.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    t.add_argument("--model", "-m")
    t.add_argument("--smoke", action="store_true")
    t.add_argument("--smoke-n", type=int, default=5)
    t.add_argument("--with-hooks", action="store_true",
                   help="Attach eval hooks (slash cmd + forced eval) for e2e trigger rate")

    # loop
    lo = sub.add_parser("loop", help="Run description optimization loop")
    lo.add_argument("--skill", "-s", required=True)
    lo.add_argument("--model", "-m", required=True)
    lo.add_argument("--iterations", "-n", type=int, default=5)
    lo.add_argument("--runs", "-r", type=int, default=DEFAULT_RUNS)
    lo.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT)
    lo.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    lo.add_argument("--holdout", type=float, default=0.3)
    lo.add_argument("--seed", type=int, default=42)

    # regress
    r = sub.add_parser("regress", help="Check for regressions")
    r.add_argument("--threshold", type=float, default=0.1)

    # baseline
    b = sub.add_parser("baseline", help="Manage baselines")
    b.add_argument("baseline_action", choices=["save", "diff"])
    b.add_argument("--skill", "-s", required=True)

    # changed
    c = sub.add_parser("changed", help="Detect changed skills")
    c.add_argument("--base", default="origin/main")

    # behavior
    bh = sub.add_parser("behavior", help="Run behavioral evaluation")
    bh.add_argument("--skill", "-s", required=True)
    bh.add_argument("--case", type=int, help="Run single case by ID")
    bh.add_argument("--smoke", action="store_true", help="Run 3 representative cases")
    bh.add_argument("--timeout", "-t", type=int, default=300)
    bh.add_argument("--model", "-m")

    # benchmark
    bm = sub.add_parser("benchmark", help="Run with/without benchmark")
    bm.add_argument("--skill", "-s", required=True)
    bm.add_argument("--runs", "-r", type=int, default=3)
    bm.add_argument("--model", "-m")

    # report
    rp = sub.add_parser("report", help="Generate static HTML dashboard")
    rp.add_argument("--open", action="store_true", help="Open in browser")

    # viewer
    vw = sub.add_parser("viewer", help="Start interactive eval viewer")
    vw.add_argument("--skill", "-s", required=True)
    vw.add_argument("--port", "-p", type=int, default=8420)

    # note
    nt = sub.add_parser("note", help="Add eval feedback note")
    nt.add_argument("--skill", "-s", required=True)
    nt.add_argument("--case", type=int, required=True)
    nt.add_argument("--note", "-n", required=True)
    nt.add_argument("--type", default="observation",
                    choices=["observation", "fix_suggestion", "assertion_issue", "skip_reason"])
    nt.add_argument("--author", default="cli")

    # notes
    ns = sub.add_parser("notes", help="List eval feedback notes")
    ns.add_argument("--skill", "-s")
    ns.add_argument("--pending", action="store_true")
    ns.add_argument("--stale", action="store_true")

    # compare
    cp = sub.add_parser("compare", help="Blind A/B skill version comparison")
    cp.add_argument("--skill", "-s", required=True)
    cp.add_argument("--old", required=True, help="Git ref for version A")
    cp.add_argument("--new", required=True, help="Git ref for version B")
    cp.add_argument("--case", type=int, help="Single case ID")

    # analyze
    az = sub.add_parser("analyze", help="Assertion quality analysis")
    az.add_argument("--skill", "-s")

    return p


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "trigger": cmd_trigger,
        "loop": cmd_loop,
        "regress": cmd_regress,
        "baseline": cmd_baseline,
        "changed": cmd_changed,
        "behavior": cmd_behavior,
        "benchmark": cmd_benchmark,
        "report": cmd_report,
        "viewer": cmd_viewer,
        "note": cmd_note,
        "notes": cmd_notes,
        "compare": cmd_compare,
        "analyze": cmd_analyze,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
