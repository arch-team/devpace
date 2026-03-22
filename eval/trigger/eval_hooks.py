"""Eval-specific hooks for trigger evaluation.

Improves trigger detection accuracy via two mechanisms:

1. system_prompt injection: For slash commands (/pace-dev), prepend an
   explicit Skill invocation directive to the prompt.

2. PreToolUse hook: Intercepts the FIRST tool call.  If Claude tries to
   use Bash/Read/Write/etc. before invoking the Skill tool, the hook
   blocks the call and reminds Claude to evaluate devpace skills first.
   This implements the "commitment mechanism" from Scott Spence (2026).

Note: UserPromptSubmit hooks do NOT fire in Agent SDK query() — the
prompt is an API parameter, not a "user submit" event.  That's why we
use system_prompt + PreToolUse instead.

These are NOT product hooks (those live in hooks/).  They are only used
during eval runs with --with-hooks to measure end-to-end trigger rates.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Mechanism 1: Prompt rewriting for slash commands
# ---------------------------------------------------------------------------

_SLASH_RE = re.compile(r"^/(?:devpace:)?(pace-\w+)\s*(.*)", re.DOTALL)

FORCED_EVAL_SYSTEM_PROMPT = (
    "IMPORTANT: The devpace plugin is loaded. Before using Bash, Read, Write, "
    "Edit, Grep, Glob, or any file/code tool, you MUST first check whether a "
    "devpace skill applies by invoking the Skill tool. Development-related "
    "requests (implement, fix, refactor, build, develop, continue coding) "
    "should ALWAYS go through devpace:pace-dev. Only skip if the request is "
    "clearly unrelated to development workflow."
)


def rewrite_slash_command(prompt: str) -> str | None:
    """If prompt is a slash command, rewrite to natural language + directive.

    Returns rewritten prompt, or None if not a slash command.
    """
    m = _SLASH_RE.match(prompt)
    if not m:
        return None

    skill_name = m.group(1)
    args = m.group(2).strip()

    return (
        f"Use the Skill tool to invoke devpace:{skill_name}"
        + (f" with these arguments: {args}" if args else "")
        + ". This was requested via a slash command — do NOT handle it "
        "directly with other tools."
    )


# ---------------------------------------------------------------------------
# Mechanism 2: PreToolUse hook — block non-Skill tools on first call
# ---------------------------------------------------------------------------

# Tools that are OK to call before Skill (they're used for discovery)
_ALLOWED_BEFORE_SKILL = {"ToolSearch", "Skill"}

# Track whether Skill has been called (per-session state via closure)
_skill_invoked = False


async def pre_tool_guard(input_data, tool_name, context):
    """Block non-Skill tools until Claude has evaluated devpace skills.

    On the first non-discovery tool call (Bash, Read, Write, etc.),
    return a block decision with a reminder to use the Skill tool first.
    Once Skill has been called, allow all subsequent tools freely.
    """
    global _skill_invoked

    tool = input_data.get("tool_name", tool_name or "")

    # If Skill was already called, allow everything
    if _skill_invoked:
        return {}

    # Mark if this IS a Skill call
    if tool == "Skill":
        _skill_invoked = True
        return {}

    # Allow discovery tools (ToolSearch) — they help Claude find Skills
    if tool in _ALLOWED_BEFORE_SKILL:
        return {}

    # Block: Claude is trying to use a code tool before evaluating Skills
    _skill_invoked = True  # Only block once to avoid infinite loop
    return {
        "decision": "block",
        "reason": (
            f"Blocked {tool}: You must evaluate whether a devpace skill "
            "applies before using code tools. Use the Skill tool to invoke "
            "the appropriate devpace:pace-* skill first. If no skill applies, "
            "you may then use other tools."
        ),
    }


def reset_hook_state():
    """Reset per-query state.  Called before each eval query."""
    global _skill_invoked
    _skill_invoked = False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_eval_hooks() -> dict:
    """Build hooks dict for ClaudeAgentOptions.

    Returns a PreToolUse hook configuration.  The slash command rewriting
    is handled separately via prompt transformation in detect.py.
    """
    from claude_agent_sdk import HookMatcher

    return {
        "PreToolUse": [
            HookMatcher(hooks=[pre_tool_guard]),
        ]
    }
