"""Unified CLI entry point for devpace eval toolkit.

Usage:
  python3 -m eval trigger  --skill pace-dev [--runs N] [--timeout T] [--max-turns M]
  python3 -m eval loop     --skill pace-dev --model MODEL [--iterations N]
  python3 -m eval regress  [--threshold 0.1]
  python3 -m eval baseline save|diff --skill pace-dev
  python3 -m eval changed  [--base origin/main]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .baseline import diff_baseline, save_baseline
from .regress import detect_changed_skills, run_regress
from .results import DEVPACE_ROOT, EVAL_DATA_DIR, SKILLS_DIR, build_metadata, save_trigger_results
from .skill_io import read_description
from .trigger import DEFAULT_MAX_TURNS, DEFAULT_RUNS, DEFAULT_TIMEOUT, run_eval_set


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
    if getattr(args, "smoke", False):
        pos = [e for e in eval_set if e.get("should_trigger")]
        neg = [e for e in eval_set if not e.get("should_trigger")]
        n = getattr(args, "smoke_n", 5)
        eval_set = pos[:3] + neg[:max(n - 3, 2)]

    description = read_description(skill_dir)
    timeout = args.timeout
    runs = args.runs
    max_turns = args.max_turns

    print(f"  skill: {skill_name}", file=sys.stderr)
    print(f"  timeout: {timeout}s, runs: {runs}, max_turns: {max_turns}, queries: {len(eval_set)}", file=sys.stderr)

    raw = run_eval_set(
        eval_set=eval_set, skill_name=skill_name, description=description,
        num_workers=min(10, len(eval_set)), timeout=timeout,
        project_root=str(DEVPACE_ROOT),
        runs_per_query=runs, model=getattr(args, "model", None),
        max_turns=max_turns,
    )

    metadata = build_metadata(
        model=getattr(args, "model", None),
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
    from .loop import run_loop
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
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
