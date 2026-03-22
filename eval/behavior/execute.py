"""Behavioral evaluation execution engine.

Runs eval prompts in isolated fixture environments via Agent SDK,
collects transcripts, .devpace/ diffs, git logs, and timing metrics.

Uses the same Agent SDK patterns as trigger/detect.py but with:
- Longer max_turns (behavioral evals need multi-step execution)
- Fixture-based environment isolation (copy fixture -> tempdir)
- Rich result collection (transcript, file diffs, git history)
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from eval.core.results import DEVPACE_ROOT, EVAL_DATA_DIR, results_dir_for

DEFAULT_TIMEOUT = 300
DEFAULT_MAX_TURNS = 20
DEFAULT_CONCURRENCY = 2
FIXTURES_DIR = EVAL_DATA_DIR / "_fixtures"


@dataclass
class ToolCall:
    """A single tool invocation from the agent transcript."""
    name: str
    input: dict
    turn: int


@dataclass
class BehavioralResult:
    """Result of a single behavioral eval execution."""
    eval_id: int
    eval_name: str
    skill_name: str
    prompt: str
    # Execution transcript
    transcript_text: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    # .devpace/ state changes
    devpace_diff: dict = field(default_factory=dict)
    # Git history created during execution
    git_log: list[str] = field(default_factory=list)
    # Timing and cost
    duration_seconds: float = 0.0
    total_turns: int = 0
    total_tokens: int = 0
    # Error tracking
    error: str | None = None
    # Working directory (for post-execution inspection)
    work_dir: Path | None = None

    def to_dict(self) -> dict:
        """Serialize for JSON output."""
        return {
            "eval_id": self.eval_id,
            "eval_name": self.eval_name,
            "skill_name": self.skill_name,
            "prompt": self.prompt,
            "transcript_text": self.transcript_text,
            "tool_calls": [
                {"name": tc.name, "input": tc.input, "turn": tc.turn}
                for tc in self.tool_calls
            ],
            "devpace_diff": self.devpace_diff,
            "git_log": self.git_log,
            "duration_seconds": round(self.duration_seconds, 1),
            "total_turns": self.total_turns,
            "total_tokens": self.total_tokens,
            "error": self.error,
        }


def _copy_fixture(fixture_dir: Path, work_dir: Path) -> None:
    """Copy fixture directory to isolated working directory."""
    if work_dir.exists():
        shutil.rmtree(work_dir)
    shutil.copytree(fixture_dir, work_dir, symlinks=True)


def _init_git_if_needed(work_dir: Path) -> None:
    """Ensure work_dir has a git repo (fixture may or may not have .git)."""
    git_dir = work_dir / ".git"
    if git_dir.exists():
        return
    subprocess.run(
        ["git", "init", "-q"],
        cwd=work_dir, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "eval@devpace.test"],
        cwd=work_dir, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "eval-runner"],
        cwd=work_dir, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "add", "-A"],
        cwd=work_dir, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "chore: fixture baseline", "--allow-empty"],
        cwd=work_dir, capture_output=True, check=True,
    )


def _collect_devpace_diff(fixture_dir: Path, work_dir: Path) -> dict:
    """Compare .devpace/ state between fixture and post-execution."""
    fixture_devpace = fixture_dir / ".devpace"
    work_devpace = work_dir / ".devpace"

    diff: dict = {
        "files_created": [],
        "files_modified": [],
        "files_deleted": [],
    }

    if not work_devpace.exists():
        if fixture_devpace.exists():
            diff["files_deleted"] = [
                str(f.relative_to(fixture_dir))
                for f in fixture_devpace.rglob("*") if f.is_file()
            ]
        return diff

    # Collect all files in both states
    fixture_files: dict[str, str] = {}
    if fixture_devpace.exists():
        for f in fixture_devpace.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(fixture_dir))
                try:
                    fixture_files[rel] = f.read_text()
                except (UnicodeDecodeError, PermissionError):
                    fixture_files[rel] = "<binary>"

    work_files: dict[str, str] = {}
    for f in work_devpace.rglob("*"):
        if f.is_file():
            rel = str(f.relative_to(work_dir))
            try:
                work_files[rel] = f.read_text()
            except (UnicodeDecodeError, PermissionError):
                work_files[rel] = "<binary>"

    for rel, content in work_files.items():
        if rel not in fixture_files:
            diff["files_created"].append(rel)
        elif content != fixture_files[rel]:
            diff["files_modified"].append(rel)

    for rel in fixture_files:
        if rel not in work_files:
            diff["files_deleted"].append(rel)

    return diff


def _collect_git_log(work_dir: Path) -> list[str]:
    """Collect git commits created during execution (after fixture baseline)."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--no-decorate"],
            cwd=work_dir, capture_output=True, text=True, check=True,
        )
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        # Skip the fixture baseline commit(s) — return all except the last
        # (fixture commits were created before eval execution)
        if len(lines) > 1:
            return lines[:-1]
        return []
    except subprocess.CalledProcessError:
        return []


def _resolve_fixture_dir(env_name: str) -> Path:
    """Resolve fixture directory from env name, creating if needed."""
    fixture_dir = FIXTURES_DIR / env_name
    if not fixture_dir.exists():
        # Try to generate via setup script
        setup_script = FIXTURES_DIR / "setup-fixtures.sh"
        if setup_script.exists():
            subprocess.run(
                ["bash", str(setup_script), env_name],
                capture_output=True, check=True,
            )
    if not fixture_dir.exists():
        raise FileNotFoundError(
            f"Fixture {env_name} not found at {fixture_dir}. "
            f"Run: bash tests/evaluation/_fixtures/setup-fixtures.sh {env_name}"
        )
    return fixture_dir


async def run_behavioral_eval(
    skill_name: str,
    eval_case: dict,
    fixture_dir: Path | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    model: str | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
    keep_workdir: bool = False,
    plugin_root: Path | None = None,
    plugins: list[dict] | None = None,
) -> BehavioralResult:
    """Execute a single behavioral eval in an isolated fixture environment.

    Args:
        skill_name: Target skill (e.g. "pace-dev").
        eval_case: Single entry from evals.json (id, name, prompt, env, assertions).
        fixture_dir: Pre-resolved fixture directory. If None, resolves from eval_case["env"].
        timeout: Max seconds for agent execution.
        model: Claude model override.
        max_turns: Max agent conversation turns.
        keep_workdir: If True, do not clean up temp working directory.
        plugin_root: Alternative plugin directory (e.g. a git worktree).
        plugins: Explicit plugin list override. Empty list = no plugins.

    Returns:
        BehavioralResult with transcript, diffs, git log, and timing.
    """
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        TextBlock,
        ToolUseBlock,
        query as sdk_query,
    )

    eval_id = eval_case["id"]
    eval_name = eval_case["name"]
    prompt = eval_case["prompt"]
    env_name = eval_case.get("env", "ENV-DEV-A")

    if fixture_dir is None:
        fixture_dir = _resolve_fixture_dir(env_name)

    # Remove CLAUDECODE to allow SDK to spawn claude subprocess without
    # "nested session" error when running inside a Claude Code session.
    os.environ.pop("CLAUDECODE", None)

    result = BehavioralResult(
        eval_id=eval_id,
        eval_name=eval_name,
        skill_name=skill_name,
        prompt=prompt,
    )

    # Create isolated working directory
    tmp_root = tempfile.mkdtemp(prefix=f"eval-{skill_name}-{eval_id}-")
    work_dir = Path(tmp_root) / "project"

    try:
        _copy_fixture(fixture_dir, work_dir)
        _init_git_if_needed(work_dir)

        if plugins is not None:
            _plugins = plugins
        elif plugin_root is not None:
            _plugins = [{"type": "local", "path": str(plugin_root)}]
        else:
            _plugins = [{"type": "local", "path": str(DEVPACE_ROOT)}]

        options = ClaudeAgentOptions(
            cwd=str(work_dir),
            plugins=_plugins,
            permission_mode="bypassPermissions",
            max_turns=max_turns,
            model=model,
        )

        start = time.monotonic()
        turn = 0

        async for message in sdk_query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                turn += 1
                for block in message.content:
                    if isinstance(block, TextBlock):
                        result.transcript_text.append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        inp = block.input if isinstance(block.input, dict) else {}
                        result.tool_calls.append(
                            ToolCall(name=block.name, input=inp, turn=turn)
                        )

        result.duration_seconds = time.monotonic() - start
        result.total_turns = turn

        # Collect post-execution state
        result.devpace_diff = _collect_devpace_diff(fixture_dir, work_dir)
        result.git_log = _collect_git_log(work_dir)

        if keep_workdir:
            result.work_dir = work_dir

    except asyncio.TimeoutError:
        result.error = f"Timeout after {timeout}s"
        result.duration_seconds = timeout
    except Exception as e:
        result.error = str(e)
    finally:
        if not keep_workdir:
            shutil.rmtree(tmp_root, ignore_errors=True)

    return result


async def run_behavioral_eval_set(
    skill_name: str,
    eval_cases: list[dict],
    timeout: int = DEFAULT_TIMEOUT,
    model: str | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
    concurrency: int = DEFAULT_CONCURRENCY,
    keep_workdirs: bool = False,
    case_ids: list[int] | None = None,
    smoke: bool = False,
) -> list[BehavioralResult]:
    """Run multiple behavioral evals with concurrency control.

    Args:
        skill_name: Target skill.
        eval_cases: Full list from evals.json.
        timeout: Per-case timeout.
        model: Model override.
        max_turns: Max turns per case.
        concurrency: Max parallel executions.
        keep_workdirs: Keep temp directories for inspection.
        case_ids: Run only specific case IDs. None = all.
        smoke: Run only 3 representative cases (ids 1, 4, 7 if available).

    Returns:
        List of BehavioralResult, one per executed case.
    """
    # Filter cases
    if case_ids is not None:
        cases = [c for c in eval_cases if c["id"] in case_ids]
    elif smoke:
        smoke_ids = {1, 4, 7}
        cases = [c for c in eval_cases if c["id"] in smoke_ids]
        if not cases:
            cases = eval_cases[:3]
    else:
        cases = eval_cases

    # Pre-resolve fixtures (generate if needed)
    env_names = {c.get("env", "ENV-DEV-A") for c in cases}
    fixture_dirs: dict[str, Path] = {}
    for env_name in env_names:
        fixture_dirs[env_name] = _resolve_fixture_dir(env_name)

    sem = asyncio.Semaphore(concurrency)

    async def _run_one(case: dict) -> BehavioralResult:
        async with sem:
            env = case.get("env", "ENV-DEV-A")
            return await asyncio.wait_for(
                run_behavioral_eval(
                    skill_name=skill_name,
                    eval_case=case,
                    fixture_dir=fixture_dirs[env],
                    timeout=timeout,
                    model=model,
                    max_turns=max_turns,
                    keep_workdir=keep_workdirs,
                ),
                timeout=timeout + 30,  # grace period for cleanup
            )

    tasks = [_run_one(case) for case in cases]
    results: list[BehavioralResult] = []

    for coro in asyncio.as_completed(tasks):
        try:
            r = await coro
            results.append(r)
        except asyncio.TimeoutError:
            pass

    # Sort by eval_id for stable output
    results.sort(key=lambda r: r.eval_id)
    return results


def save_behavioral_results(
    skill_name: str,
    results: list[BehavioralResult],
) -> Path:
    """Save behavioral eval results to grading/ directory.

    Returns path to the saved JSON file.
    """
    rdir = results_dir_for(skill_name)
    grading_dir = rdir / "grading"
    grading_dir.mkdir(exist_ok=True)

    ts = datetime.now(timezone.utc).isoformat()
    output = {
        "skill": skill_name,
        "timestamp": ts,
        "results": [r.to_dict() for r in results],
        "summary": {
            "total": len(results),
            "succeeded": sum(1 for r in results if r.error is None),
            "errored": sum(1 for r in results if r.error is not None),
        },
    }

    out_path = grading_dir / "behavioral-results.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    return out_path
