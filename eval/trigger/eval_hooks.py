"""Eval-specific hooks for trigger evaluation.

Two hooks for improving trigger detection accuracy:

1. slash_command_hook: Intercepts /pace-dev style commands and injects
   additionalContext telling Claude to use the Skill tool.

2. forced_eval_hook: Injects a "commitment mechanism" prompting Claude
   to evaluate whether a devpace skill should be used before acting.

These are NOT product hooks (those live in hooks/).  They are only used
during eval runs with --with-hooks to measure end-to-end trigger rates
in conditions closer to real deployment.
"""
from __future__ import annotations

import re


async def slash_command_hook(input_data, tool_name, context):
    """Intercept /pace-* slash commands and convert to Skill invocation hint.

    In real Claude Code, slash commands are resolved by the CLI layer
    before reaching the model.  Agent SDK's query() doesn't have that
    layer, so /pace-dev arrives as plain text.  This hook bridges the gap.
    """
    prompt = input_data.get("prompt", "")

    # Match /pace-xxx or /devpace:pace-xxx at the start
    m = re.match(r"^/(?:devpace:)?(pace-\w+)\s*(.*)", prompt, re.DOTALL)
    if not m:
        return {}

    skill_name = m.group(1)
    args = m.group(2).strip()

    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                f"The user invoked /{skill_name} as a slash command. "
                f"You MUST use the Skill tool to invoke devpace:{skill_name}"
                + (f" with these arguments: {args}" if args else "")
                + ". Do NOT attempt to handle the request directly."
            ),
        }
    }


async def forced_eval_hook(input_data, tool_name, context):
    """Force Claude to evaluate devpace skills before acting.

    Implements a "commitment mechanism" (Scott Spence, 2026):
    Claude must explicitly consider whether a devpace skill applies
    before using basic tools (Bash, Read, Write, etc.) directly.

    This addresses the under-triggering problem where Claude skips
    skills for tasks it believes it can handle directly.
    """
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                "IMPORTANT: Before responding to this request, you must evaluate "
                "whether any devpace skill should be used. The devpace plugin "
                "provides development workflow management (CR creation, status "
                "tracking, quality gates, change management, etc.). "
                "If the user is asking to implement, fix, refactor, build, "
                "develop, or continue coding work, you MUST invoke the Skill "
                "tool with the appropriate devpace:pace-* skill BEFORE using "
                "any other tools like Bash, Read, Write, Edit, or Grep. "
                "Only skip the skill if the request is clearly unrelated to "
                "development workflow (e.g., general questions, non-coding tasks)."
            ),
        }
    }


def build_eval_hooks() -> dict:
    """Build hooks dict for ClaudeAgentOptions.

    Returns a hooks configuration that chains both eval hooks on
    the UserPromptSubmit event.
    """
    # Import here to avoid hard dependency on SDK at module level
    from claude_agent_sdk import HookMatcher

    return {
        "UserPromptSubmit": [
            HookMatcher(hooks=[slash_command_hook, forced_eval_hook]),
        ]
    }
