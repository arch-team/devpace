#!/usr/bin/env python3
"""Gate check: verify Agent SDK can detect skill triggering.

Runs 3 queries (2 positive, 1 negative) to validate the SDK path works.
Gate passes if >= 1 positive query triggers the target skill.

Usage:
  python3 eval/_gate_sdk.py
"""

import asyncio
import json
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ToolUseBlock,
    query,
)

from eval.core.llm_client import ensure_sdk_env
from eval.core.results import DEVPACE_ROOT as _DEVPACE_ROOT_PATH

DEVPACE_ROOT = str(_DEVPACE_ROOT_PATH)

ensure_sdk_env()

GATE_QUERIES = [
    {"query": "帮我开始做用户认证功能", "skill": "pace-dev", "should_trigger": True},
    {"query": "帮我实现登录页面的前端代码", "skill": "pace-dev", "should_trigger": True},
    {"query": "今天天气怎么样", "skill": "pace-dev", "should_trigger": False},
]


async def check_skill_trigger(prompt: str, skill_name: str, timeout: int = 120) -> bool:
    """Run a single query and check if the target skill is triggered."""
    options = ClaudeAgentOptions(
        cwd=DEVPACE_ROOT,
        permission_mode="bypassPermissions",
        max_turns=3,
        plugins=[{"type": "local", "path": DEVPACE_ROOT}],
    )

    triggered = False
    try:
        async for message in query(prompt=prompt, options=options):
            if triggered:
                continue  # drain remaining messages for clean shutdown
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name == "Skill":
                        input_str = json.dumps(block.input)
                        if skill_name in input_str:
                            triggered = True
                            break
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
    return triggered


async def main():
    print("Agent SDK Gate Check", file=sys.stderr)
    print(f"  cwd: {DEVPACE_ROOT}", file=sys.stderr)
    print(f"  queries: {len(GATE_QUERIES)}", file=sys.stderr)
    print(file=sys.stderr)

    positive_pass = 0
    negative_pass = 0

    for item in GATE_QUERIES:
        q = item["query"]
        skill = item["skill"]
        should = item["should_trigger"]

        print(f"  Testing: {q[:50]}...", file=sys.stderr)
        try:
            triggered = await asyncio.wait_for(
                check_skill_trigger(q, skill),
                timeout=120,
            )
        except asyncio.TimeoutError:
            print(f"    TIMEOUT", file=sys.stderr)
            triggered = False

        if should:
            passed = triggered
            if passed:
                positive_pass += 1
            print(f"    {'PASS' if passed else 'FAIL'}: expected=trigger, got={'trigger' if triggered else 'no-trigger'}", file=sys.stderr)
        else:
            passed = not triggered
            if passed:
                negative_pass += 1
            print(f"    {'PASS' if passed else 'FAIL'}: expected=no-trigger, got={'trigger' if triggered else 'no-trigger'}", file=sys.stderr)

    print(file=sys.stderr)
    total_positive = sum(1 for q in GATE_QUERIES if q["should_trigger"])
    total_negative = sum(1 for q in GATE_QUERIES if not q["should_trigger"])
    print(f"  Positive: {positive_pass}/{total_positive}", file=sys.stderr)
    print(f"  Negative: {negative_pass}/{total_negative}", file=sys.stderr)

    gate_passed = positive_pass >= 1
    print(file=sys.stderr)
    print(f"  Gate: {'PASSED' if gate_passed else 'FAILED'}", file=sys.stderr)
    return 0 if gate_passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
