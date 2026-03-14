#!/usr/bin/env python3
"""Eval shim: adapts devpace skills for skill-creator evaluation scripts.

Fixes known issues with running skill-creator's run_eval/run_loop directly:
  1. Injects missing `name:` frontmatter field (skill-creator requires it)
  2. Uses PYTHONPATH instead of cd (preserves correct project_root discovery)
  3. Temporarily disables ALL plugins + hides user CLAUDE.md to eliminate
     global skill competition and system-level skill mandates
  4. Increases timeout to account for MCP server initialization (~36s)
  5. Injects --dangerously-skip-permissions via PATH wrapper (prevents
     silent blocking of Skill tool calls in non-interactive -p mode)
  6. Injects --allowedTools "Skill" (intent: force Skill-only routing)

KNOWN LIMITATION (upstream):
  run_eval.py's detection returns False on the first non-Skill/Read tool_use
  (line 141). Claude Code's built-in tools (ToolSearch, Glob, Bash) are exempt
  from --allowedTools and always fire before Skill, causing 0% positive trigger
  rate. Negative eval (should_trigger=false) works correctly. Positive eval
  requires upstream fix to run_eval.py's stream detection logic — it should
  scan ALL tool_use events across turns, not early-exit on the first non-match.

Usage:
  python3 eval/shim.py trigger --skill pace-dev [--runs N] [--timeout T] [--model M]
  python3 eval/shim.py loop    --skill pace-dev --model MODEL [--iterations N]
  python3 eval/shim.py regress [--threshold 0.1]
  python3 eval/shim.py baseline save --skill pace-dev
  python3 eval/shim.py baseline diff --skill pace-dev
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEVPACE_ROOT = Path(__file__).resolve().parent.parent
EVAL_DATA_DIR = DEVPACE_ROOT / "tests" / "evaluation"
SKILLS_DIR = DEVPACE_ROOT / "skills"
DEFAULT_TIMEOUT = 90
DEFAULT_RUNS = 3
PLUGIN_NAME = "devpace"

# The real claude binary path (resolved once to avoid wrapper recursion)
_REAL_CLAUDE = shutil.which("claude") or "claude"


def create_claude_wrapper(tmp_dir: Path) -> Path:
    """Create a claude wrapper that injects eval-critical flags.

    run_eval.py hardcodes `subprocess.Popen(["claude", ...])`. We can't modify
    it, so we place a wrapper script earlier in PATH that transparently injects
    flags. Two flags are essential:

    --dangerously-skip-permissions: prevents permission checks from silently
        blocking tool calls in non-interactive `-p` mode.

    --allowedTools "Skill": restricts Claude to ONLY the Skill tool.
        Without this, Claude calls ToolSearch/Bash/Edit before Skill, and
        run_eval.py's detection (line 141) returns False on the first
        non-Skill tool_use event. By restricting to Skill only, Claude's
        sole way to act is to invoke the Skill tool — which is exactly
        what trigger eval needs to detect. ToolSearch and Read are excluded
        because they fire before Skill and trip the early-exit check.
    """
    wrapper_dir = tmp_dir / "_bin"
    wrapper_dir.mkdir(exist_ok=True)
    wrapper = wrapper_dir / "claude"
    wrapper.write_text(
        f"#!/bin/bash\n"
        f'exec "{_REAL_CLAUDE}" --dangerously-skip-permissions'
        f' --allowedTools "Skill" "$@"\n'
    )
    wrapper.chmod(0o755)
    return wrapper_dir


def find_sc_scripts_root() -> Path | None:
    """Discover skill-creator scripts directory.

    Priority: 1) plugin cache (latest) 2) eval/vendor/ fallback
    """
    sc_base = Path.home() / ".claude" / "plugins" / "cache" / "claude-plugins-official" / "skill-creator"
    if sc_base.is_dir():
        for hash_dir in sorted(sc_base.iterdir(), reverse=True):
            candidate = hash_dir / "skills" / "skill-creator"
            if (candidate / "scripts" / "run_eval.py").exists():
                return candidate
    # Vendor fallback
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
        # Check if name: already exists
        has_name = False
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("name:"):
                has_name = True
                break
        if not has_name:
            lines.insert(1, f"name: {name}")
            skill_md.write_text("\n".join(lines))


def description_hash(skill_dir: Path) -> str:
    """SHA256 of the current SKILL.md description field."""
    content = (skill_dir / "SKILL.md").read_text()
    for line in content.split("\n"):
        if line.startswith("description:"):
            desc = line[len("description:"):].strip()
            return hashlib.sha256(desc.encode()).hexdigest()[:16]
    return "unknown"


_USER_CLAUDE_MD = Path.home() / ".claude" / "CLAUDE.md"
_USER_CLAUDE_MD_BAK = Path.home() / ".claude" / "CLAUDE.md.eval-bak"


def _claude_env() -> dict:
    return {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}


def isolate_user_config() -> bool:
    """Temporarily hide user-level CLAUDE.md to prevent global skill mandates
    (e.g. SuperClaude's brainstorming) from hijacking Skill routing during eval.
    Returns True if CLAUDE.md was moved (needs restore)."""
    if _USER_CLAUDE_MD.exists() and not _USER_CLAUDE_MD_BAK.exists():
        _USER_CLAUDE_MD.rename(_USER_CLAUDE_MD_BAK)
        return True
    return False


def restore_user_config() -> None:
    """Restore user-level CLAUDE.md after eval."""
    if _USER_CLAUDE_MD_BAK.exists():
        _USER_CLAUDE_MD_BAK.rename(_USER_CLAUDE_MD)


def plugins_list_enabled() -> list[str]:
    """Return list of currently enabled plugin names."""
    result = subprocess.run(
        ["claude", "plugin", "list"],
        capture_output=True, text=True, env=_claude_env(),
    )
    enabled = []
    for line in result.stdout.splitlines():
        # Enabled plugins have > marker: "  > plugin-name@marketplace"
        if ">" in line:
            # Extract plugin name before @
            name = line.split(">")[-1].strip().split("@")[0].strip()
            if name:
                enabled.append(name)
    return enabled


def plugins_disable_all() -> list[str]:
    """Disable ALL plugins. Returns list of previously enabled plugins for restore."""
    enabled = plugins_list_enabled()
    if enabled:
        subprocess.run(
            ["claude", "plugin", "disable", "--all"],
            capture_output=True, text=True, env=_claude_env(),
        )
    return enabled


def plugins_restore(names: list[str]) -> None:
    """Re-enable a list of plugins."""
    for name in names:
        subprocess.run(
            ["claude", "plugin", "enable", name],
            capture_output=True, text=True, env=_claude_env(),
        )


def results_dir_for(skill_name: str) -> Path:
    """Get or create the results directory for a skill."""
    d = EVAL_DATA_DIR / skill_name / "results"
    d.mkdir(parents=True, exist_ok=True)
    (d / "history").mkdir(exist_ok=True)
    (d / "loop").mkdir(exist_ok=True)
    return d


def save_trigger_results(skill_name: str, raw_output: dict) -> Path:
    """Save trigger eval results to latest.json + history."""
    rdir = results_dir_for(skill_name)
    summary = raw_output.get("summary", {})
    results_list = raw_output.get("results", [])

    positive = [r for r in results_list if r.get("should_trigger")]
    negative = [r for r in results_list if not r.get("should_trigger")]

    structured = {
        "skill": skill_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description_hash": description_hash(SKILLS_DIR / skill_name),
        "summary": summary,
        "positive": {
            "total": len(positive),
            "passed": sum(1 for r in positive if r.get("pass")),
            "failed": sum(1 for r in positive if not r.get("pass")),
        },
        "negative": {
            "total": len(negative),
            "passed": sum(1 for r in negative if r.get("pass")),
            "failed": sum(1 for r in negative if not r.get("pass")),
        },
        "false_negatives": [
            {"id": i, "query": r["query"]}
            for i, r in enumerate(positive) if not r.get("pass")
        ],
        "false_positives": [
            {"id": i, "query": r["query"]}
            for i, r in enumerate(negative) if not r.get("pass")
        ],
        "runs_per_query": results_list[0].get("runs", 1) if results_list else 1,
        "raw_results": results_list,
    }

    latest = rdir / "latest.json"
    latest.write_text(json.dumps(structured, indent=2, ensure_ascii=False))

    ts = datetime.now().strftime("%Y-%m-%dT%H-%M")
    history = rdir / "history" / f"{ts}.json"
    history.write_text(json.dumps(structured, indent=2, ensure_ascii=False))

    return latest


def run_trigger(args: argparse.Namespace) -> int:
    """Run trigger evaluation for a skill."""
    skill_name = args.skill
    skill_dir = SKILLS_DIR / skill_name
    eval_file = EVAL_DATA_DIR / skill_name / "trigger-evals.json"

    if not skill_dir.is_dir():
        print(f"Error: skill directory not found: {skill_dir}", file=sys.stderr)
        return 1
    if not eval_file.exists():
        print(f"Error: eval file not found: {eval_file}", file=sys.stderr)
        return 1

    sc_root = find_sc_scripts_root()
    if sc_root is None:
        print("Error: skill-creator scripts not found (no plugin cache or vendor)", file=sys.stderr)
        return 1

    # Select eval subset for smoke mode
    eval_set_path = str(eval_file.resolve())
    if getattr(args, "smoke", False):
        full_set = json.loads(eval_file.read_text())
        positive = [e for e in full_set if e.get("should_trigger")]
        negative = [e for e in full_set if not e.get("should_trigger")]
        smoke_n = getattr(args, "smoke_n", 5)
        subset = positive[:3] + negative[:max(smoke_n - 3, 2)]
        tmp_eval = Path(tempfile.mktemp(suffix=".json"))
        tmp_eval.write_text(json.dumps(subset))
        eval_set_path = str(tmp_eval)

    # Create patched skill copy
    tmp_dir = Path(tempfile.mkdtemp())
    patched_skill = tmp_dir / skill_name
    patch_skill_md(skill_dir, patched_skill, skill_name)

    # Create clean eval project (isolated from devpace plugins)
    eval_proj = Path(tempfile.mkdtemp())
    (eval_proj / ".claude").mkdir()

    # Isolate eval environment:
    # 1. Hide user CLAUDE.md (prevents SuperClaude brainstorming mandate)
    # 2. Disable ALL plugins (prevents competing skills)
    config_moved = isolate_user_config()
    previously_enabled = plugins_disable_all()

    try:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        env["PYTHONPATH"] = f"{sc_root}:{env.get('PYTHONPATH', '')}"

        # Inject --dangerously-skip-permissions and --allowedTools via PATH wrapper.
        wrapper_dir = create_claude_wrapper(tmp_dir)
        env["PATH"] = f"{wrapper_dir}:{env.get('PATH', '')}"

        timeout = getattr(args, "timeout", DEFAULT_TIMEOUT)
        runs = getattr(args, "runs", DEFAULT_RUNS)
        cmd = [
            sys.executable, "-m", "scripts.run_eval",
            "--eval-set", eval_set_path,
            "--skill-path", str(patched_skill),
            "--verbose",
            "--num-workers", "10",
            "--timeout", str(timeout),
            "--runs-per-query", str(runs),
        ]
        if getattr(args, "model", None):
            cmd.extend(["--model", args.model])

        print(f"  skill: {skill_name}", file=sys.stderr)
        print(f"  timeout: {timeout}s, runs: {runs}", file=sys.stderr)
        print(f"  project: {eval_proj}", file=sys.stderr)
        print(f"  permissions: skip (via wrapper)", file=sys.stderr)

        result = subprocess.run(
            cmd, cwd=eval_proj, env=env,
            capture_output=True, text=True,
            timeout=timeout * 40 + 60,  # total timeout: per-query * max-queries + buffer
        )

        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            print(f"run_eval.py failed (exit {result.returncode})", file=sys.stderr)
            if result.stdout:
                print(result.stdout)
            return result.returncode

        # Parse and persist results
        try:
            raw_output = json.loads(result.stdout)
        except json.JSONDecodeError:
            print("Error: could not parse run_eval.py output as JSON", file=sys.stderr)
            print(result.stdout)
            return 1

        latest = save_trigger_results(skill_name, raw_output)
        print(f"  results saved: {latest.relative_to(DEVPACE_ROOT)}", file=sys.stderr)

        # Print summary
        summary = raw_output.get("summary", {})
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        print(f"\n  {skill_name}: {passed}/{total} passed", file=sys.stderr)

        # Also print full JSON to stdout for pipeline use
        print(json.dumps(raw_output, indent=2, ensure_ascii=False))
        return 0 if summary.get("failed", 0) == 0 else 1

    except subprocess.TimeoutExpired:
        print(f"Error: eval timed out", file=sys.stderr)
        return 1
    finally:
        restore_user_config()
        plugins_restore(previously_enabled)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        shutil.rmtree(eval_proj, ignore_errors=True)
        if getattr(args, "smoke", False) and "tmp_eval" in dir():
            tmp_eval.unlink(missing_ok=True)


def run_loop(args: argparse.Namespace) -> int:
    """Run optimization loop for a skill's description."""
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

    # Create patched skill copy
    tmp_dir = Path(tempfile.mkdtemp())
    patched_skill = tmp_dir / skill_name
    patch_skill_md(skill_dir, patched_skill, skill_name)

    rdir = results_dir_for(skill_name)
    config_moved = isolate_user_config()
    previously_enabled = plugins_disable_all()

    try:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        env["PYTHONPATH"] = f"{sc_root}:{env.get('PYTHONPATH', '')}"

        # Inject --dangerously-skip-permissions via PATH wrapper
        wrapper_dir = create_claude_wrapper(tmp_dir)
        env["PATH"] = f"{wrapper_dir}:{env.get('PATH', '')}"

        # Create clean eval project
        eval_proj = Path(tempfile.mkdtemp())
        (eval_proj / ".claude").mkdir()

        iterations = getattr(args, "iterations", 5)
        timeout = getattr(args, "timeout", DEFAULT_TIMEOUT)
        cmd = [
            sys.executable, "-m", "scripts.run_loop",
            "--skill-path", str(patched_skill),
            "--eval-set", str(eval_file.resolve()),
            "--model", args.model,
            "--num-iterations", str(iterations),
            "--timeout", str(timeout),
            "--runs-per-query", str(getattr(args, "runs", DEFAULT_RUNS)),
            "--output-dir", str(rdir / "loop"),
        ]

        print(f"  skill: {skill_name}, model: {args.model}", file=sys.stderr)
        print(f"  iterations: {iterations}, timeout: {timeout}s", file=sys.stderr)
        print(f"  permissions: skip (via wrapper)", file=sys.stderr)

        result = subprocess.run(cmd, cwd=eval_proj, env=env)

        # Copy best description if available
        best_desc = rdir / "loop" / "best-description.txt"
        if (rdir / "loop" / "results.json").exists():
            loop_results = json.loads((rdir / "loop" / "results.json").read_text())
            if "best_description" in loop_results:
                best_desc.write_text(loop_results["best_description"])
                print(f"  best description saved: {best_desc.relative_to(DEVPACE_ROOT)}", file=sys.stderr)

        return result.returncode

    finally:
        restore_user_config()
        plugins_restore(previously_enabled)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        if "eval_proj" in dir():
            shutil.rmtree(eval_proj, ignore_errors=True)


def run_regress(args: argparse.Namespace) -> int:
    """Check for regressions across all skills with baselines."""
    threshold = getattr(args, "threshold", 0.1)
    any_regression = False

    for skill_dir in sorted(EVAL_DATA_DIR.iterdir()):
        if skill_dir.name.startswith("_") or not skill_dir.is_dir():
            continue
        baseline = skill_dir / "results" / "baseline.json"
        latest = skill_dir / "results" / "latest.json"
        if not baseline.exists() or not latest.exists():
            continue

        bl = json.loads(baseline.read_text())
        lt = json.loads(latest.read_text())
        bl_total = bl.get("summary", {}).get("total", 1)
        lt_total = lt.get("summary", {}).get("total", 1)
        bl_rate = bl.get("summary", {}).get("passed", 0) / max(bl_total, 1)
        lt_rate = lt.get("summary", {}).get("passed", 0) / max(lt_total, 1)
        delta = lt_rate - bl_rate

        skill = skill_dir.name
        if delta < -threshold:
            print(f"  REGRESSION {skill}: {bl_rate:.0%} -> {lt_rate:.0%} (down {abs(delta):.0%})")
            any_regression = True
        else:
            symbol = "up" if delta > 0 else "same" if delta == 0 else "down"
            print(f"  OK {skill}: {bl_rate:.0%} -> {lt_rate:.0%} ({symbol} {abs(delta):.0%})")

    return 1 if any_regression else 0


def run_baseline(args: argparse.Namespace) -> int:
    """Manage baselines: save or diff."""
    action = args.baseline_action
    skill_name = args.skill

    rdir = EVAL_DATA_DIR / skill_name / "results"
    latest = rdir / "latest.json"
    baseline = rdir / "baseline.json"

    if action == "save":
        if not latest.exists():
            print(f"Error: no latest.json for {skill_name}. Run eval first.", file=sys.stderr)
            return 1
        shutil.copy2(latest, baseline)
        print(f"  baseline saved: {baseline.relative_to(DEVPACE_ROOT)}")
        return 0

    elif action == "diff":
        if not baseline.exists():
            print(f"No baseline for {skill_name}", file=sys.stderr)
            return 1
        if not latest.exists():
            print(f"No latest results for {skill_name}", file=sys.stderr)
            return 1

        bl = json.loads(baseline.read_text())
        lt = json.loads(latest.read_text())
        bl_s = bl.get("summary", {})
        lt_s = lt.get("summary", {})
        print(f"  {skill_name}:")
        print(f"    baseline: {bl_s.get('passed',0)}/{bl_s.get('total',0)} passed")
        print(f"    latest:   {lt_s.get('passed',0)}/{lt_s.get('total',0)} passed")
        print(f"    description_hash: {bl.get('description_hash','')} -> {lt.get('description_hash','')}")
        return 0

    return 1


def main():
    parser = argparse.ArgumentParser(description="Eval shim for devpace skills")
    sub = parser.add_subparsers(dest="command", required=True)

    # trigger
    p_trigger = sub.add_parser("trigger", help="Run trigger evaluation")
    p_trigger.add_argument("--skill", "-s", required=True, help="Skill name (e.g. pace-dev)")
    p_trigger.add_argument("--runs", "-r", type=int, default=DEFAULT_RUNS, help="Runs per query")
    p_trigger.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="Timeout per query (seconds)")
    p_trigger.add_argument("--model", "-m", help="Model override")
    p_trigger.add_argument("--smoke", action="store_true", help="Smoke test mode (5 queries)")
    p_trigger.add_argument("--smoke-n", type=int, default=5, help="Queries for smoke mode")

    # loop
    p_loop = sub.add_parser("loop", help="Run optimization loop")
    p_loop.add_argument("--skill", "-s", required=True, help="Skill name")
    p_loop.add_argument("--model", "-m", required=True, help="Model ID (required)")
    p_loop.add_argument("--iterations", "-n", type=int, default=5, help="Loop iterations")
    p_loop.add_argument("--runs", "-r", type=int, default=DEFAULT_RUNS, help="Runs per query")
    p_loop.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="Timeout per query")

    # regress
    p_regress = sub.add_parser("regress", help="Check for regressions across skills")
    p_regress.add_argument("--threshold", type=float, default=0.1, help="Regression threshold")

    # baseline
    p_baseline = sub.add_parser("baseline", help="Manage baselines")
    p_baseline.add_argument("baseline_action", choices=["save", "diff"])
    p_baseline.add_argument("--skill", "-s", required=True, help="Skill name")

    args = parser.parse_args()

    if args.command == "trigger":
        return run_trigger(args)
    elif args.command == "loop":
        return run_loop(args)
    elif args.command == "regress":
        return run_regress(args)
    elif args.command == "baseline":
        return run_baseline(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
