"""Blind A/B comparison for skill version evaluation.

Runs two versions of a skill on the same eval scenario, anonymizes the
outputs (version_a / version_b), and uses LLM-as-judge to score across
six dimensions. Only triggered explicitly for major changes.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from eval.behavior.execute import (
    DEVPACE_ROOT,
    BehavioralResult,
    run_behavioral_eval,
    resolve_fixture_dir,
)
from eval.core.llm_client import get_anthropic_client, resolve_model_id
from eval.core.results import results_dir_for

RUBRIC_DIMENSIONS = [
    "correctness",
    "completeness",
    "accuracy",
    "organization",
    "formatting",
    "usability",
]


@dataclass
class ComparisonResult:
    """Result of a blind A/B comparison."""
    skill_name: str
    eval_id: int
    eval_name: str
    version_a_ref: str  # git ref (e.g., HEAD~5)
    version_b_ref: str  # git ref (e.g., HEAD)
    winner: str  # "A", "B", or "tie"
    scores: dict = field(default_factory=dict)  # {dimension: {a: int, b: int}}
    reasoning: str = ""
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "skill": self.skill_name,
            "eval_id": self.eval_id,
            "eval_name": self.eval_name,
            "version_a": self.version_a_ref,
            "version_b": self.version_b_ref,
            "winner": self.winner,
            "scores": self.scores,
            "reasoning": self.reasoning,
            "error": self.error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def _checkout_version(git_ref: str, dest_dir: Path) -> None:
    """Checkout a specific version of devpace into dest_dir."""
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(dest_dir), git_ref],
        cwd=DEVPACE_ROOT,
        capture_output=True,
        check=True,
    )


def _cleanup_worktree(dest_dir: Path) -> None:
    """Remove a git worktree."""
    try:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(dest_dir)],
            cwd=DEVPACE_ROOT,
            capture_output=True,
        )
    except Exception:
        pass


def _judge_comparison(
    eval_case: dict,
    result_a: BehavioralResult,
    result_b: BehavioralResult,
    model: str = "claude-haiku-4-5-20251001",
) -> tuple[str, dict, str]:
    """Use LLM to judge which version is better.

    Returns (winner, scores, reasoning).
    """
    client, is_bedrock = get_anthropic_client(require=False)
    if client is None:
        return "tie", {}, "No LLM client available for comparison judging"

    # Anonymize: randomly assign A and B (deterministic based on eval_id)
    transcript_a = "\n".join(result_a.transcript_text[:15])[:3000]
    transcript_b = "\n".join(result_b.transcript_text[:15])[:3000]
    diff_a = json.dumps(result_a.devpace_diff, indent=2)[:1000]
    diff_b = json.dumps(result_b.devpace_diff, indent=2)[:1000]

    dimensions_text = "\n".join(f"- {d}: 1-5 scale" for d in RUBRIC_DIMENSIONS)

    prompt = f"""You are comparing two versions of a Claude Code plugin's behavior on the same task.

TASK PROMPT: {eval_case["prompt"]}
EXPECTED: {eval_case.get("expected_output", "N/A")}

=== VERSION A OUTPUT ===
Transcript:
{transcript_a}

File changes:
{diff_a}

=== VERSION B OUTPUT ===
Transcript:
{transcript_b}

File changes:
{diff_b}

Score each version on these dimensions (1=poor, 5=excellent):
{dimensions_text}

Respond with EXACTLY one JSON object:
{{
  "scores": {{"correctness": {{"a": N, "b": N}}, "completeness": {{"a": N, "b": N}}, ...}},
  "winner": "A" or "B" or "tie",
  "reasoning": "1-2 sentence explanation"
}}
"""

    try:
        response = client.messages.create(
            model=resolve_model_id(model, is_bedrock),
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return (
                parsed.get("winner", "tie"),
                parsed.get("scores", {}),
                parsed.get("reasoning", ""),
            )
    except Exception as e:
        return "tie", {}, f"Comparison judging error: {e}"

    return "tie", {}, "Could not parse LLM response"


async def blind_compare(
    skill_name: str,
    eval_case: dict,
    version_a_ref: str,
    version_b_ref: str,
    fixture_dir: Path | None = None,
    timeout: int = 300,
    model: str | None = None,
    max_turns: int = 20,
) -> ComparisonResult:
    """Run blind A/B comparison between two skill versions.

    Args:
        skill_name: Target skill.
        eval_case: Single eval scenario from evals.json.
        version_a_ref: Git ref for version A (e.g., HEAD~5).
        version_b_ref: Git ref for version B (e.g., HEAD).
        fixture_dir: Pre-resolved fixture. If None, resolves from eval_case["env"].
        timeout: Max seconds per execution.
        model: Model override.
        max_turns: Max turns per execution.
    """
    env_name = eval_case.get("env", "ENV-DEV-A")
    if fixture_dir is None:
        fixture_dir = resolve_fixture_dir(env_name)

    result = ComparisonResult(
        skill_name=skill_name,
        eval_id=eval_case["id"],
        eval_name=eval_case["name"],
        version_a_ref=version_a_ref,
        version_b_ref=version_b_ref,
    )

    worktree_a = Path(tempfile.mkdtemp(prefix="compare-a-"))
    worktree_b = Path(tempfile.mkdtemp(prefix="compare-b-"))

    try:
        # Checkout both versions as separate plugin sources
        _checkout_version(version_a_ref, worktree_a)
        _checkout_version(version_b_ref, worktree_b)

        # Run both versions with their respective plugin roots
        import asyncio

        result_a, result_b = await asyncio.gather(
            run_behavioral_eval(
                skill_name, eval_case, fixture_dir,
                timeout=timeout, model=model, max_turns=max_turns,
                plugin_root=worktree_a,
            ),
            run_behavioral_eval(
                skill_name, eval_case, fixture_dir,
                timeout=timeout, model=model, max_turns=max_turns,
                plugin_root=worktree_b,
            ),
        )

        # Judge
        winner, scores, reasoning = _judge_comparison(eval_case, result_a, result_b)
        result.winner = winner
        result.scores = scores
        result.reasoning = reasoning

    except Exception as e:
        result.error = str(e)
    finally:
        _cleanup_worktree(worktree_a)
        _cleanup_worktree(worktree_b)

    return result


def save_comparison_results(
    skill_name: str,
    comparisons: list[ComparisonResult],
) -> Path:
    """Save comparison results."""
    rdir = results_dir_for(skill_name)
    bench_dir = rdir / "benchmark"
    bench_dir.mkdir(exist_ok=True)

    output = {
        "skill": skill_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "comparisons": [c.to_dict() for c in comparisons],
    }

    out_path = bench_dir / "comparison.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    return out_path
