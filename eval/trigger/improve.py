"""Anthropic API-based description generation (P1.2).

Replaces the old `claude -p` subprocess approach with direct Anthropic API
calls, gaining:
- Extended thinking (budget_tokens=10000) for better reasoning
- Full SKILL.md content context (not just description)
- History of previous attempts to prevent repetition
- Hard limit of 1024 characters on generated descriptions
- Support for ANTHROPIC_API_KEY or AWS Bedrock via environment
"""
from __future__ import annotations

import json
import sys

from eval.core.llm_client import get_anthropic_client, resolve_model_id

MAX_DESCRIPTION_LENGTH = 1024


def _build_prompt(
    skill_name: str,
    current_desc: str,
    skill_md_content: str,
    eval_results: dict,
    history: list[dict] | None = None,
) -> str:
    """Build the improvement prompt with full context."""
    false_negatives = [
        r for r in eval_results.get("results", [])
        if r.get("should_trigger") and not r.get("pass")
    ]
    false_positives = [
        r for r in eval_results.get("results", [])
        if not r.get("should_trigger") and not r.get("pass")
    ]

    fn_queries = json.dumps(
        [r["query"] for r in false_negatives], ensure_ascii=False
    )
    fp_queries = json.dumps(
        [r["query"] for r in false_positives], ensure_ascii=False
    )

    # Build history context
    history_text = ""
    if history:
        prev_attempts = []
        for h in history[-5:]:  # last 5 attempts
            score = h.get("score", "?")
            desc = h.get("description", "?")[:200]
            prev_attempts.append(f"  - score={score}: {desc}")
        if prev_attempts:
            history_text = (
                "\n\nPrevious attempts (do NOT repeat these):\n"
                + "\n".join(prev_attempts)
            )

    return f"""You are optimizing a Claude Code skill description for auto-triggering accuracy.

SKILL NAME: {skill_name}

CURRENT DESCRIPTION:
{current_desc}

FULL SKILL.MD CONTENT (for context on what this skill does):
{skill_md_content[:3000]}

FALSE NEGATIVES (should trigger but didn't):
{fn_queries}

FALSE POSITIVES (shouldn't trigger but did):
{fp_queries}
{history_text}

Generate an improved description that:
1. Better captures the missed positive cases (false negatives)
2. Better excludes the wrongly matched negative cases (false positives)
3. Starts with "Use when"
4. Includes specific trigger keywords in quotes (Chinese and English)
5. Includes NOT-for exclusions to prevent false positives
6. Does NOT exceed {MAX_DESCRIPTION_LENGTH} characters
7. Does NOT describe what the skill does (no internal steps)
8. Only describes WHEN it should trigger

Output ONLY the improved description text. No markdown, no quotes around it, no explanation."""


def generate_improved_description(
    skill_name: str,
    current_desc: str,
    skill_md_content: str,
    eval_results: dict,
    model: str = "claude-sonnet-4-20250514",
    history: list[dict] | None = None,
) -> str | None:
    """Generate an improved skill description using Anthropic API.

    Returns the improved description string, or None on failure.
    """
    client, is_bedrock = get_anthropic_client()
    if client is None:
        return None

    prompt = _build_prompt(
        skill_name, current_desc, skill_md_content, eval_results, history
    )

    try:
        # Use extended thinking for better reasoning
        response = client.messages.create(
            model=resolve_model_id(model, is_bedrock),
            max_tokens=8000,
            thinking={
                "type": "enabled",
                "budget_tokens": 10000,
            },
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from response (skip thinking blocks)
        desc = ""
        for block in response.content:
            if block.type == "text":
                desc = block.text.strip()
                break

        if not desc:
            print("  generation returned empty output", file=sys.stderr)
            return None

        # Clean up common wrapping artifacts
        if desc.startswith('"') and desc.endswith('"'):
            desc = desc[1:-1]
        if desc.startswith("`") and desc.endswith("`"):
            desc = desc[1:-1]
        if desc.startswith("```") and desc.endswith("```"):
            desc = desc[3:-3].strip()

        # Hard limit enforcement
        if len(desc) > MAX_DESCRIPTION_LENGTH:
            print(
                f"  generated description too long ({len(desc)} chars), "
                f"truncating to {MAX_DESCRIPTION_LENGTH}",
                file=sys.stderr,
            )
            # Truncate at last space before limit
            desc = desc[:MAX_DESCRIPTION_LENGTH]
            last_space = desc.rfind(" ")
            if last_space > MAX_DESCRIPTION_LENGTH * 0.8:
                desc = desc[:last_space]

        return desc

    except Exception as e:
        print(f"  generation error: {e}", file=sys.stderr)
        return None
