#!/usr/bin/env python3
"""Eval shim: trigger evaluation for devpace skills.

Uses Claude Agent SDK (`claude_agent_sdk.query()`) for trigger detection.
The SDK runs the same agent loop as interactive Claude Code, with programmatic
plugin loading and typed message objects (ToolUseBlock), eliminating the need
for stream-json parsing.

Previous approach (`claude -p` + subprocess) consistently yielded 0% positive
trigger rate due to missing skill routing context in single-turn mode.
See docs/research/trigger-eval-postmortem-2026-03-15.md for root cause analysis.

Usage:
  python3 eval/shim.py trigger --skill pace-dev [--runs N] [--timeout T]
  python3 eval/shim.py loop    --skill pace-dev --model MODEL [--iterations N]
  python3 eval/shim.py regress [--threshold 0.1]
  python3 eval/shim.py baseline save --skill pace-dev
  python3 eval/shim.py baseline diff --skill pace-dev
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ToolUseBlock,
    query as sdk_query,
)

DEVPACE_ROOT = Path(__file__).resolve().parent.parent
EVAL_DATA_DIR = DEVPACE_ROOT / "tests" / "evaluation"
SKILLS_DIR = DEVPACE_ROOT / "skills"
DEFAULT_TIMEOUT = 90
DEFAULT_RUNS = 3

# Remove CLAUDECODE to allow SDK to spawn claude subprocess without
# "nested session" error when running inside a Claude Code session.
os.environ.pop("CLAUDECODE", None)

_CLAUDE_CLI = shutil.which("claude") or "claude"


# ---------------------------------------------------------------------------
# Skill helpers
# ---------------------------------------------------------------------------

def read_description(skill_dir: Path) -> str:
    """Extract description from SKILL.md frontmatter."""
    content = (skill_dir / "SKILL.md").read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                parts = []
                for cont in lines[i + 1:]:
                    if cont.startswith("  ") or cont.startswith("\t"):
                        parts.append(cont.strip())
                    else:
                        break
                return " ".join(parts)
            return value.strip('"').strip("'")
    return ""


def description_hash(skill_dir: Path) -> str:
    """SHA256 prefix of the current description."""
    return hashlib.sha256(read_description(skill_dir).encode()).hexdigest()[:16]


def _replace_description_in_file(skill_md: Path, new_desc: str) -> str:
    """Replace description in SKILL.md frontmatter. Returns original content."""
    original = skill_md.read_text()
    lines = original.split("\n")
    if lines[0].strip() != "---":
        return original

    desc_start = None
    desc_end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            if desc_start is not None and desc_end is None:
                desc_end = i
            break
        if line.startswith("description:"):
            desc_start = i
            value = line[len("description:"):].strip()
            if value not in (">", "|", ">-", "|-"):
                desc_end = i + 1
            continue
        if desc_start is not None and desc_end is None:
            if line.startswith("  ") or line.startswith("\t"):
                continue
            else:
                desc_end = i

    if desc_start is None:
        return original
    if desc_end is None:
        desc_end = desc_start + 1

    if len(new_desc) <= 200:
        new_lines = [f"description: {new_desc}"]
    else:
        new_lines = ["description: >"]
        words = new_desc.split()
        current_line = "  "
        for word in words:
            if len(current_line) + len(word) + 1 > 80 and len(current_line) > 2:
                new_lines.append(current_line)
                current_line = "  " + word
            else:
                current_line += (" " if len(current_line) > 2 else "") + word
        if current_line.strip():
            new_lines.append(current_line)

    result_lines = lines[:desc_start] + new_lines + lines[desc_end:]
    skill_md.write_text("\n".join(result_lines))
    return original


# ---------------------------------------------------------------------------
# SDK-based trigger detection
# ---------------------------------------------------------------------------

async def _run_single_query_sdk(
    query_text: str,
    skill_name: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
) -> bool:
    """Run one query via Agent SDK and detect if a Skill matching skill_name fires.

    Uses claude_agent_sdk.query() which runs the same agent loop as interactive
    Claude Code, with full plugin loading and skill auto-triggering support.
    Returns True if any ToolUseBlock with name="Skill" contains skill_name.
    """
    options = ClaudeAgentOptions(
        cwd=project_root,
        permission_mode="bypassPermissions",
        max_turns=3,
        model=model,
        plugins=[{"type": "local", "path": project_root}],
    )

    triggered = False
    try:
        async for message in sdk_query(prompt=query_text, options=options):
            if triggered:
                continue  # drain remaining messages for clean shutdown
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name == "Skill":
                        if skill_name in json.dumps(block.input):
                            triggered = True
                            break
    except Exception:
        pass
    return triggered


async def _run_eval_set_async(
    eval_set: list[dict],
    skill_name: str,
    num_workers: int,
    timeout: int,
    project_root: str,
    runs_per_query: int = 1,
    model: str | None = None,
) -> list[tuple[dict, bool]]:
    """Run eval set concurrently with asyncio.Semaphore. Returns (item, result) pairs."""
    sem = asyncio.Semaphore(num_workers)

    async def _run(item: dict) -> tuple[dict, bool]:
        async with sem:
            try:
                result = await asyncio.wait_for(
                    _run_single_query_sdk(
                        item["query"], skill_name, timeout, project_root, model,
                    ),
                    timeout=timeout,
                )
                return (item, result)
            except asyncio.TimeoutError:
                return (item, False)
            except Exception:
                return (item, False)

    tasks = [_run(item) for item in eval_set for _ in range(runs_per_query)]
    return await asyncio.gather(*tasks)


def _run_eval_set(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: str,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    verbose: bool = True,
) -> dict:
    """Run the full eval set. Returns results dict."""
    raw_results = asyncio.run(
        _run_eval_set_async(
            eval_set=eval_set,
            skill_name=skill_name,
            num_workers=num_workers,
            timeout=timeout,
            project_root=project_root,
            runs_per_query=runs_per_query,
            model=model,
        )
    )

    query_triggers: dict[str, list[bool]] = {}
    query_items: dict[str, dict] = {}
    for item, triggered in raw_results:
        q = item["query"]
        query_items[q] = item
        query_triggers.setdefault(q, [])
        query_triggers[q].append(triggered)

    results = []
    for q, triggers in query_triggers.items():
        item = query_items[q]
        rate = sum(triggers) / len(triggers)
        should = item["should_trigger"]
        passed = (rate >= trigger_threshold) if should else (rate < trigger_threshold)
        results.append({
            "query": q, "should_trigger": should,
            "trigger_rate": rate, "triggers": sum(triggers),
            "runs": len(triggers), "pass": passed,
        })

    n_pass = sum(1 for r in results if r["pass"])
    total = len(results)

    if verbose:
        print(f"Results: {n_pass}/{total} passed", file=sys.stderr)
        for r in results:
            tag = "PASS" if r["pass"] else "FAIL"
            print(f"  [{tag}] rate={r['triggers']}/{r['runs']} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    return {
        "skill_name": skill_name, "description": description,
        "results": results,
        "summary": {"total": total, "passed": n_pass, "failed": total - n_pass},
    }


# ---------------------------------------------------------------------------
# Description optimization (loop)
# ---------------------------------------------------------------------------

def _generate_improved_description(
    current_desc: str,
    eval_results: dict,
    model: str,
) -> str | None:
    """Generate improved skill description using claude -p based on eval failures."""
    false_negatives = [r for r in eval_results["results"]
                       if r["should_trigger"] and not r["pass"]]
    false_positives = [r for r in eval_results["results"]
                       if not r["should_trigger"] and not r["pass"]]

    if not false_negatives and not false_positives:
        return None  # perfect score

    fn_queries = json.dumps([r["query"] for r in false_negatives], ensure_ascii=False)
    fp_queries = json.dumps([r["query"] for r in false_positives], ensure_ascii=False)

    prompt = (
        "You are optimizing a Claude Code skill description for auto-triggering accuracy.\n\n"
        f"Current description:\n{current_desc}\n\n"
        f"False negatives (should trigger but didn't):\n{fn_queries}\n\n"
        f"False positives (shouldn't trigger but did):\n{fp_queries}\n\n"
        "Generate an improved description that:\n"
        "1. Better captures the missed positive cases\n"
        "2. Better excludes the wrongly matched negative cases\n"
        "3. Starts with 'Use when'\n"
        "4. Includes specific trigger keywords in quotes\n"
        "5. Includes NOT-for exclusions\n"
        "6. Does not exceed 500 characters\n\n"
        "Output ONLY the improved description text. No markdown, no quotes around it, no explanation."
    )

    cmd = [_CLAUDE_CLI, "-p", prompt, "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=str(DEVPACE_ROOT),
        )
        if result.returncode != 0:
            print(f"  generation failed (exit {result.returncode}): {result.stderr[:200]}", file=sys.stderr)
            return None
        desc = result.stdout.strip()
        if not desc:
            print("  generation returned empty output", file=sys.stderr)
            return None
        # Sanity: strip stray quotes/backticks the model may wrap it in
        if desc.startswith('"') and desc.endswith('"'):
            desc = desc[1:-1]
        if desc.startswith("`") and desc.endswith("`"):
            desc = desc[1:-1]
        return desc
    except subprocess.TimeoutExpired:
        print("  generation timed out (120s)", file=sys.stderr)
    except Exception as e:
        print(f"  generation error: {e}", file=sys.stderr)
    return None


def _eval_score(results: dict) -> float:
    """Compute a single score from eval results (0.0 - 1.0)."""
    s = results.get("summary", {})
    total = s.get("total", 0)
    return s.get("passed", 0) / max(total, 1)


# ---------------------------------------------------------------------------
# Results persistence
# ---------------------------------------------------------------------------

def results_dir_for(skill_name: str) -> Path:
    d = EVAL_DATA_DIR / skill_name / "results"
    d.mkdir(parents=True, exist_ok=True)
    (d / "history").mkdir(exist_ok=True)
    (d / "loop").mkdir(exist_ok=True)
    return d


def save_trigger_results(skill_name: str, raw: dict) -> Path:
    rdir = results_dir_for(skill_name)
    res = raw.get("results", [])
    pos = [r for r in res if r.get("should_trigger")]
    neg = [r for r in res if not r.get("should_trigger")]

    structured = {
        "skill": skill_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description_hash": description_hash(SKILLS_DIR / skill_name),
        "summary": raw.get("summary", {}),
        "positive": {"total": len(pos), "passed": sum(1 for r in pos if r["pass"]), "failed": sum(1 for r in pos if not r["pass"])},
        "negative": {"total": len(neg), "passed": sum(1 for r in neg if r["pass"]), "failed": sum(1 for r in neg if not r["pass"])},
        "false_negatives": [{"id": i, "query": r["query"]} for i, r in enumerate(pos) if not r["pass"]],
        "false_positives": [{"id": i, "query": r["query"]} for i, r in enumerate(neg) if not r["pass"]],
        "runs_per_query": res[0].get("runs", 1) if res else 1,
        "raw_results": res,
    }

    latest = rdir / "latest.json"
    latest.write_text(json.dumps(structured, indent=2, ensure_ascii=False))
    ts = datetime.now().strftime("%Y-%m-%dT%H-%M")
    (rdir / "history" / f"{ts}.json").write_text(json.dumps(structured, indent=2, ensure_ascii=False))
    return latest


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def run_trigger(args: argparse.Namespace) -> int:
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
    timeout = getattr(args, "timeout", DEFAULT_TIMEOUT)
    runs = getattr(args, "runs", DEFAULT_RUNS)

    print(f"  skill: {skill_name}", file=sys.stderr)
    print(f"  timeout: {timeout}s, runs: {runs}, queries: {len(eval_set)}", file=sys.stderr)

    raw = _run_eval_set(
        eval_set=eval_set, skill_name=skill_name, description=description,
        num_workers=min(10, len(eval_set)), timeout=timeout,
        project_root=str(DEVPACE_ROOT),
        runs_per_query=runs, model=getattr(args, "model", None),
    )

    latest = save_trigger_results(skill_name, raw)
    s = raw["summary"]
    print(f"  results: {latest.relative_to(DEVPACE_ROOT)}", file=sys.stderr)
    print(f"\n  {skill_name}: {s['passed']}/{s['total']} passed", file=sys.stderr)
    print(json.dumps(raw, indent=2, ensure_ascii=False))
    return 0 if s["failed"] == 0 else 1


def run_loop(args: argparse.Namespace) -> int:
    """Run description optimization loop.

    Each iteration: generate improved description via claude -p, temporarily
    swap it into SKILL.md, evaluate with SDK, keep the better version.
    """
    skill_name = args.skill
    skill_dir = SKILLS_DIR / skill_name
    skill_md = skill_dir / "SKILL.md"
    eval_file = EVAL_DATA_DIR / skill_name / "trigger-evals.json"

    if not skill_dir.is_dir():
        print(f"Error: skill directory not found: {skill_dir}", file=sys.stderr)
        return 1
    if not eval_file.exists():
        print(f"Error: eval file not found: {eval_file}", file=sys.stderr)
        return 1

    model = args.model
    iterations = getattr(args, "iterations", 5)
    timeout = getattr(args, "timeout", DEFAULT_TIMEOUT)
    runs = getattr(args, "runs", DEFAULT_RUNS)
    eval_set = json.loads(eval_file.read_text())
    rdir = results_dir_for(skill_name)
    project_root = str(DEVPACE_ROOT)

    best_desc = read_description(skill_dir)
    print(f"  skill: {skill_name}, iterations: {iterations}", file=sys.stderr)
    print(f"  initial description ({len(best_desc)} chars): {best_desc[:80]}...", file=sys.stderr)

    # --- Initial eval ---
    print(f"\n  [0/{iterations}] evaluating current description...", file=sys.stderr)
    best_results = _run_eval_set(
        eval_set=eval_set, skill_name=skill_name, description=best_desc,
        num_workers=min(5, len(eval_set)), timeout=timeout,
        project_root=project_root, runs_per_query=runs, model=model,
        verbose=False,
    )
    best_score = _eval_score(best_results)
    print(f"  [0/{iterations}] score: {best_score:.0%}", file=sys.stderr)

    history = [{"iteration": 0, "description": best_desc, "score": best_score}]

    if best_score >= 1.0:
        print("  perfect score, nothing to optimize", file=sys.stderr)
    else:
        for i in range(1, iterations + 1):
            print(f"\n  [{i}/{iterations}] generating improved description...", file=sys.stderr)
            candidate = _generate_improved_description(best_desc, best_results, model)
            if candidate is None or candidate == best_desc:
                print(f"  [{i}/{iterations}] no improvement generated, skipping", file=sys.stderr)
                history.append({"iteration": i, "description": best_desc, "score": best_score, "skipped": True})
                continue

            print(f"  [{i}/{iterations}] candidate ({len(candidate)} chars): {candidate[:80]}...", file=sys.stderr)

            # Temporarily swap description for eval
            original_content = _replace_description_in_file(skill_md, candidate)
            try:
                print(f"  [{i}/{iterations}] evaluating candidate...", file=sys.stderr)
                candidate_results = _run_eval_set(
                    eval_set=eval_set, skill_name=skill_name, description=candidate,
                    num_workers=min(5, len(eval_set)), timeout=timeout,
                    project_root=project_root, runs_per_query=runs, model=model,
                    verbose=False,
                )
            finally:
                # Always restore original SKILL.md
                skill_md.write_text(original_content)

            candidate_score = _eval_score(candidate_results)
            print(f"  [{i}/{iterations}] score: {candidate_score:.0%} (best: {best_score:.0%})", file=sys.stderr)

            if candidate_score > best_score:
                print(f"  [{i}/{iterations}] improved! {best_score:.0%} -> {candidate_score:.0%}", file=sys.stderr)
                best_desc = candidate
                best_score = candidate_score
                best_results = candidate_results

            history.append({"iteration": i, "description": candidate, "score": candidate_score})

            if best_score >= 1.0:
                print(f"  [{i}/{iterations}] perfect score reached, stopping early", file=sys.stderr)
                break

    # --- Save results ---
    loop_results = {
        "skill": skill_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "best_description": best_desc,
        "best_score": best_score,
        "iterations": len(history) - 1,
        "history": history,
    }

    loop_dir = rdir / "loop"
    (loop_dir / "results.json").write_text(json.dumps(loop_results, indent=2, ensure_ascii=False))
    (loop_dir / "best-description.txt").write_text(best_desc)

    original_desc = read_description(skill_dir)
    print(f"\n  loop complete: {best_score:.0%}", file=sys.stderr)
    if best_desc != original_desc:
        print(f"  improved description saved to: {loop_dir.relative_to(DEVPACE_ROOT)}/best-description.txt", file=sys.stderr)
        print(f"  apply with: make eval-fix-apply S={skill_name}", file=sys.stderr)
    else:
        print(f"  no improvement found over current description", file=sys.stderr)

    print(json.dumps(loop_results, indent=2, ensure_ascii=False))
    return 0


def run_regress(args: argparse.Namespace) -> int:
    """Check for regressions across all skills with baselines."""
    threshold = getattr(args, "threshold", 0.1)
    any_fail = False
    for d in sorted(EVAL_DATA_DIR.iterdir()):
        if d.name.startswith("_") or not d.is_dir():
            continue
        bl = d / "results" / "baseline.json"
        lt = d / "results" / "latest.json"
        if not bl.exists() or not lt.exists():
            continue
        bl_d, lt_d = json.loads(bl.read_text()), json.loads(lt.read_text())
        bl_r = bl_d["summary"]["passed"] / max(bl_d["summary"]["total"], 1)
        lt_r = lt_d["summary"]["passed"] / max(lt_d["summary"]["total"], 1)
        delta = lt_r - bl_r
        if delta < -threshold:
            print(f"  REGRESSION {d.name}: {bl_r:.0%} -> {lt_r:.0%} (down {abs(delta):.0%})")
            any_fail = True
        else:
            print(f"  OK {d.name}: {bl_r:.0%} -> {lt_r:.0%}")
    return 1 if any_fail else 0


def run_baseline(args: argparse.Namespace) -> int:
    """Manage baselines."""
    rdir = EVAL_DATA_DIR / args.skill / "results"
    latest, baseline = rdir / "latest.json", rdir / "baseline.json"

    if args.baseline_action == "save":
        if not latest.exists():
            print(f"Error: no latest.json for {args.skill}", file=sys.stderr)
            return 1
        shutil.copy2(latest, baseline)
        print(f"  baseline saved: {baseline.relative_to(DEVPACE_ROOT)}")
        return 0

    if args.baseline_action == "diff":
        if not baseline.exists() or not latest.exists():
            print(f"Missing baseline or latest for {args.skill}", file=sys.stderr)
            return 1
        bl, lt = json.loads(baseline.read_text()), json.loads(latest.read_text())
        print(f"  {args.skill}: baseline {bl['summary']['passed']}/{bl['summary']['total']}"
              f" -> latest {lt['summary']['passed']}/{lt['summary']['total']}")
        return 0
    return 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Eval shim for devpace skills")
    sub = p.add_subparsers(dest="command", required=True)

    t = sub.add_parser("trigger")
    t.add_argument("--skill", "-s", required=True)
    t.add_argument("--runs", "-r", type=int, default=DEFAULT_RUNS)
    t.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT)
    t.add_argument("--model", "-m")
    t.add_argument("--smoke", action="store_true")
    t.add_argument("--smoke-n", type=int, default=5)

    lo = sub.add_parser("loop")
    lo.add_argument("--skill", "-s", required=True)
    lo.add_argument("--model", "-m", required=True)
    lo.add_argument("--iterations", "-n", type=int, default=5)
    lo.add_argument("--runs", "-r", type=int, default=DEFAULT_RUNS)
    lo.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT)

    r = sub.add_parser("regress")
    r.add_argument("--threshold", type=float, default=0.1)

    b = sub.add_parser("baseline")
    b.add_argument("baseline_action", choices=["save", "diff"])
    b.add_argument("--skill", "-s", required=True)

    args = p.parse_args()
    handlers = {"trigger": run_trigger, "loop": run_loop, "regress": run_regress, "baseline": run_baseline}
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
