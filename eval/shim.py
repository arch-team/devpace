#!/usr/bin/env python3
"""Eval shim: trigger evaluation for devpace skills.

Self-contained implementation that runs `claude -p` with stream-json parsing.
Scans ALL tool_use events across ALL turns for Skill calls matching the target
skill name — unlike skill-creator's run_eval.py which early-exits on the first
non-Skill tool.

PLATFORM LIMITATION:
  `claude -p` is a single-turn stateless API. It does NOT replicate the
  interactive session's skill auto-triggering pipeline (where skills like
  using-superpowers activate at session start and persistently route queries
  to matching skills). In -p mode, Claude processes queries directly without
  the skill routing context, so trigger_rate for positive cases is consistently
  0%. Negative cases (should_trigger=false) work correctly because absence of
  triggering is the expected behavior.

  Proper trigger eval requires either:
  - An interactive-mode testing API from Claude Code (not yet available)
  - A mock that simulates the skill routing logic offline
  - Running eval in a real interactive session with programmatic input

  Despite this limitation, the infrastructure (results persistence, regression
  comparison, baseline management, tiered testing) is complete and ready for
  when a proper testing API becomes available.

Usage:
  python3 eval/shim.py trigger --skill pace-dev [--runs N] [--timeout T]
  python3 eval/shim.py loop    --skill pace-dev --model MODEL [--iterations N]
  python3 eval/shim.py regress [--threshold 0.1]
  python3 eval/shim.py baseline save --skill pace-dev
  python3 eval/shim.py baseline diff --skill pace-dev
"""

import argparse
import hashlib
import json
import os
import select
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

DEVPACE_ROOT = Path(__file__).resolve().parent.parent
EVAL_DATA_DIR = DEVPACE_ROOT / "tests" / "evaluation"
SKILLS_DIR = DEVPACE_ROOT / "skills"
DEFAULT_TIMEOUT = 90
DEFAULT_RUNS = 3

_REAL_CLAUDE = shutil.which("claude") or "claude"


# ---------------------------------------------------------------------------
# Skill helpers
# ---------------------------------------------------------------------------

def find_sc_scripts_root() -> Path | None:
    """Discover skill-creator scripts directory (for loop mode)."""
    sc_base = Path.home() / ".claude" / "plugins" / "cache" / "claude-plugins-official" / "skill-creator"
    if sc_base.is_dir():
        for hash_dir in sorted(sc_base.iterdir(), reverse=True):
            candidate = hash_dir / "skills" / "skill-creator"
            if (candidate / "scripts" / "run_eval.py").exists():
                return candidate
    vendor = Path(__file__).parent / "vendor" / "skill-creator"
    if (vendor / "scripts" / "run_eval.py").exists():
        return vendor
    return None


def patch_skill_md(src_dir: Path, dst_dir: Path, name: str) -> None:
    """Copy skill directory and inject name: into SKILL.md frontmatter."""
    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
    skill_md = dst_dir / "SKILL.md"
    content = skill_md.read_text()
    lines = content.split("\n")
    if lines[0].strip() == "---":
        has_name = any(l.startswith("name:") for l in lines[1:] if l.strip() == "---" or l.startswith("name:"))
        # More precise: check only frontmatter lines
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("name:"):
                has_name = True
                break
        if not has_name:
            lines.insert(1, f"name: {name}")
            skill_md.write_text("\n".join(lines))


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


# ---------------------------------------------------------------------------
# Self-contained trigger detection
# ---------------------------------------------------------------------------

def _run_single_query(
    query: str,
    skill_name: str,
    description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
) -> bool:
    """Run one query via `claude -p` and detect if a Skill matching skill_name fires.

    Scans ALL tool_use events across ALL turns. Returns True if any Skill call's
    input JSON contains skill_name.
    """
    cmd = [
        _REAL_CLAUDE, "--dangerously-skip-permissions",
        "-p", query,
        "--output-format", "stream-json",
        "--verbose", "--include-partial-messages",
    ]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        cwd=project_root, env=env,
    )

    start = time.time()
    buffer = ""
    cur_tool = None
    cur_json = ""

    try:
        while time.time() - start < timeout:
            if process.poll() is not None:
                rest = process.stdout.read()
                if rest:
                    buffer += rest.decode("utf-8", errors="replace")
                break

            ready, _, _ = select.select([process.stdout], [], [], 1.0)
            if not ready:
                continue
            chunk = os.read(process.stdout.fileno(), 8192)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if ev.get("type") == "stream_event":
                    se = ev["event"]
                    st = se.get("type", "")

                    if st == "content_block_start":
                        cb = se.get("content_block", {})
                        if cb.get("type") == "tool_use" and cb.get("name") == "Skill":
                            cur_tool = "Skill"
                            cur_json = ""
                        else:
                            cur_tool = None

                    elif st == "content_block_delta" and cur_tool == "Skill":
                        d = se.get("delta", {})
                        if d.get("type") == "input_json_delta":
                            cur_json += d.get("partial_json", "")
                            if skill_name in cur_json:
                                return True

                    elif st == "content_block_stop":
                        if cur_tool == "Skill" and skill_name in cur_json:
                            return True
                        cur_tool = None
                        cur_json = ""

                elif ev.get("type") == "assistant":
                    for item in ev.get("message", {}).get("content", []):
                        if item.get("type") == "tool_use" and item.get("name") == "Skill":
                            if skill_name in json.dumps(item.get("input", {})):
                                return True
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()

    return False


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
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for _ in range(runs_per_query):
                future = executor.submit(
                    _run_single_query, item["query"], skill_name,
                    description, timeout, project_root, model,
                )
                future_to_info[future] = item

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item = future_to_info[future]
            q = item["query"]
            query_items[q] = item
            query_triggers.setdefault(q, [])
            try:
                query_triggers[q].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[q].append(False)

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
    """Run optimization loop (delegates to skill-creator's run_loop.py)."""
    skill_name = args.skill
    skill_dir = SKILLS_DIR / skill_name
    eval_file = EVAL_DATA_DIR / skill_name / "trigger-evals.json"

    if not getattr(args, "model", None):
        print("Error: --model is required for loop mode", file=sys.stderr)
        return 1

    sc_root = find_sc_scripts_root()
    if sc_root is None:
        print("Error: skill-creator scripts not found", file=sys.stderr)
        return 1

    tmp_dir = Path(tempfile.mkdtemp())
    patched = tmp_dir / skill_name
    patch_skill_md(skill_dir, patched, skill_name)
    rdir = results_dir_for(skill_name)

    try:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        env["PYTHONPATH"] = f"{sc_root}:{env.get('PYTHONPATH', '')}"

        cmd = [
            sys.executable, "-m", "scripts.run_loop",
            "--skill-path", str(patched),
            "--eval-set", str(eval_file.resolve()),
            "--model", args.model,
            "--num-iterations", str(getattr(args, "iterations", 5)),
            "--timeout", str(getattr(args, "timeout", DEFAULT_TIMEOUT)),
            "--runs-per-query", str(getattr(args, "runs", DEFAULT_RUNS)),
            "--output-dir", str(rdir / "loop"),
        ]
        result = subprocess.run(cmd, cwd=str(DEVPACE_ROOT), env=env)

        best_file = rdir / "loop" / "results.json"
        if best_file.exists():
            data = json.loads(best_file.read_text())
            if "best_description" in data:
                (rdir / "loop" / "best-description.txt").write_text(data["best_description"])

        return result.returncode
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


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

    l = sub.add_parser("loop")
    l.add_argument("--skill", "-s", required=True)
    l.add_argument("--model", "-m", required=True)
    l.add_argument("--iterations", "-n", type=int, default=5)
    l.add_argument("--runs", "-r", type=int, default=DEFAULT_RUNS)
    l.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT)

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
