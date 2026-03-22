"""Agent SDK-based trigger detection for skill evaluation.

Uses claude_agent_sdk.query() to run queries and detect whether
a target skill is triggered via ToolUseBlock inspection.

Enhancements over original shim.py:
- P2.1: max_turns default raised from 3 to 5
- P2.2: Structured ToolUseBlock matching via block.input.get("skill")
- P2.2: All ToolUseBlock names recorded for debugging
- P2.3: Wilson score confidence interval for statistical stability
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import sys
import time

from eval.core.results import build_metadata, eval_score, save_trigger_results
from eval.core.skill_io import read_description

# Remove CLAUDECODE to allow SDK to spawn claude subprocess without
# "nested session" error when running inside a Claude Code session.
os.environ.pop("CLAUDECODE", None)

DEFAULT_TIMEOUT = 90
DEFAULT_RUNS = 3
DEFAULT_MAX_TURNS = 5


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score confidence interval for a proportion.

    Returns (lower, upper) bounds at the given z-level (default 95%).
    """
    if total == 0:
        return (0.0, 0.0)
    p = successes / total
    denom = 1 + z * z / total
    centre = p + z * z / (2 * total)
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total)
    return (
        round((centre - spread) / denom, 4),
        round((centre + spread) / denom, 4),
    )


async def run_single_query(
    query_text: str,
    skill_name: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> dict:
    """Run one query via Agent SDK and detect if a Skill matching skill_name fires.

    Returns a dict with:
        triggered: bool
        tool_uses: list of all ToolUseBlock names seen (for debugging)
    """
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ToolUseBlock,
        query as sdk_query,
    )

    options = ClaudeAgentOptions(
        cwd=project_root,
        permission_mode="bypassPermissions",
        max_turns=max_turns,
        model=model,
        plugins=[{"type": "local", "path": project_root}],
    )

    triggered = False
    tool_uses: list[str] = []

    try:
        async for message in sdk_query(prompt=query_text, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if not isinstance(block, ToolUseBlock):
                        continue
                    tool_uses.append(block.name)
                    if triggered:
                        continue
                    if block.name == "Skill":
                        # P2.2: Structured matching — check input dict first,
                        # fall back to JSON string search for robustness
                        inp = block.input if isinstance(block.input, dict) else {}
                        if inp.get("skill") == skill_name:
                            triggered = True
                        elif skill_name in json.dumps(inp):
                            triggered = True
    except Exception:
        pass

    return {"triggered": triggered, "tool_uses": tool_uses}


async def run_eval_set_async(
    eval_set: list[dict],
    skill_name: str,
    num_workers: int,
    timeout: int,
    project_root: str,
    runs_per_query: int = 1,
    model: str | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> list[tuple[dict, dict]]:
    """Run eval set concurrently. Returns (item, result_dict) pairs."""
    sem = asyncio.Semaphore(num_workers)

    async def _run(item: dict) -> tuple[dict, dict]:
        async with sem:
            try:
                result = await asyncio.wait_for(
                    run_single_query(
                        item["query"], skill_name, timeout,
                        project_root, model, max_turns,
                    ),
                    timeout=timeout,
                )
                return (item, result)
            except asyncio.TimeoutError:
                return (item, {"triggered": False, "tool_uses": []})
            except Exception:
                return (item, {"triggered": False, "tool_uses": []})

    tasks = [_run(item) for item in eval_set for _ in range(runs_per_query)]
    return await asyncio.gather(*tasks)


def run_eval_set(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: str,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
    verbose: bool = True,
) -> dict:
    """Run the full eval set. Returns results dict with per-query details."""
    start_time = time.monotonic()

    raw_results = asyncio.run(
        run_eval_set_async(
            eval_set=eval_set,
            skill_name=skill_name,
            num_workers=num_workers,
            timeout=timeout,
            project_root=project_root,
            runs_per_query=runs_per_query,
            model=model,
            max_turns=max_turns,
        )
    )

    duration = time.monotonic() - start_time

    # Aggregate per-query results
    query_triggers: dict[str, list[bool]] = {}
    query_items: dict[str, dict] = {}
    query_tool_uses: dict[str, list[list[str]]] = {}

    for item, result in raw_results:
        q = item["query"]
        query_items[q] = item
        query_triggers.setdefault(q, []).append(result["triggered"])
        query_tool_uses.setdefault(q, []).append(result["tool_uses"])

    results = []
    for q, triggers in query_triggers.items():
        item = query_items[q]
        rate = sum(triggers) / len(triggers)
        should = item["should_trigger"]
        passed = (rate >= trigger_threshold) if should else (rate < trigger_threshold)
        ci_lower, ci_upper = _wilson_interval(sum(triggers), len(triggers))

        results.append({
            "query": q,
            "should_trigger": should,
            "trigger_rate": rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": passed,
            "confidence_interval": [ci_lower, ci_upper],
            "tool_uses_seen": query_tool_uses.get(q, []),
        })

    n_pass = sum(1 for r in results if r["pass"])
    total = len(results)

    if verbose:
        print(f"Results: {n_pass}/{total} passed", file=sys.stderr)
        for r in results:
            tag = "PASS" if r["pass"] else "FAIL"
            ci = r["confidence_interval"]
            print(
                f"  [{tag}] rate={r['triggers']}/{r['runs']}"
                f" CI=[{ci[0]:.2f},{ci[1]:.2f}]"
                f" expected={r['should_trigger']}: {r['query'][:70]}",
                file=sys.stderr,
            )

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {"total": total, "passed": n_pass, "failed": total - n_pass},
        "duration_seconds": round(duration, 1),
    }
