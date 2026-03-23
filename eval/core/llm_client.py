"""Shared Anthropic API client initialization and environment helpers.

Supports both direct Anthropic API and AWS Bedrock.
Used by trigger/improve.py, behavior/grader.py, and behavior/comparator.py.
"""
from __future__ import annotations

import os
import sys

_claudecode_cleared = False


def ensure_sdk_env() -> None:
    """Remove CLAUDECODE env var to allow Agent SDK subprocess spawning.

    Safe to call multiple times — only mutates os.environ once.
    """
    global _claudecode_cleared
    if not _claudecode_cleared:
        os.environ.pop("CLAUDECODE", None)
        _claudecode_cleared = True


def get_anthropic_client(*, require: bool = True):
    """Get an Anthropic client, supporting both direct API and AWS Bedrock.

    Args:
        require: If True, print errors when client unavailable.

    Returns:
        (client, is_bedrock) tuple, or (None, False) if unavailable.
    """
    try:
        import anthropic
    except ImportError:
        if require:
            print(
                "Error: anthropic package not installed. "
                "Run: pip install 'anthropic>=0.50.0'",
                file=sys.stderr,
            )
        return None, False

    # Try AWS Bedrock first if configured
    if os.environ.get("AWS_REGION") and not os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return anthropic.AnthropicBedrock(), True
        except Exception:
            pass

    # Fall back to direct API
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        if require:
            print(
                "Error: ANTHROPIC_API_KEY not set and AWS Bedrock not configured.",
                file=sys.stderr,
            )
        return None, False

    return anthropic.Anthropic(api_key=api_key), False


# Bedrock model ID mapping
BEDROCK_MODEL_MAP = {
    "claude-haiku-4-5-20251001": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "claude-sonnet-4-20250514": "us.anthropic.claude-sonnet-4-20250514-v1:0",
}


def resolve_model_id(model: str, is_bedrock: bool) -> str:
    """Resolve model ID for the client type (direct vs Bedrock)."""
    if is_bedrock:
        return BEDROCK_MODEL_MAP.get(model, model)
    return model
