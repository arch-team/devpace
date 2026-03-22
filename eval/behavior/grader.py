"""Mixed three-level grading engine for behavioral evaluations.

Grade levels:
    G1 — Programmatic file/content checks (zero cost)
    G2 — Regex/structural matching (zero cost)
    G3 — LLM-as-judge via Anthropic API (low cost, Haiku)

Supports shared assertion expansion (SA-01 through SA-06).
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from eval.behavior.execute import BehavioralResult
from eval.behavior._grader_checks import (
    KEYWORD_CONTENT_CHECKS,
    KEYWORD_FILE_CHECKS,
    KEYWORD_OUTPUT_CHECKS,
    NAMED_CONTENT_CHECKS,
    NAMED_FILE_CHECKS,
    NAMED_OUTPUT_CHECKS,
)
from eval.core.llm_client import get_anthropic_client, resolve_model_id
from eval.core.results import EVAL_DATA_DIR, results_dir_for

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class GradingResult:
    """Result of grading a single assertion."""
    text: str
    type: str
    grade_level: str  # G1, G2, G3
    passed: bool
    evidence: str
    shared_pattern: str | None = None

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "type": self.type,
            "grade_level": self.grade_level,
            "passed": self.passed,
            "evidence": self.evidence,
            "shared_pattern": self.shared_pattern,
        }


# ---------------------------------------------------------------------------
# Shared assertion definitions (SA-01 through SA-06)
# ---------------------------------------------------------------------------

SHARED_ASSERTIONS: dict[str, list[dict]] = {
    "SA-01": [
        {
            "text": "state.md current-work field reflects latest operation result",
            "type": "content_check",
            "check": "state_current_work",
        },
        {
            "text": "state.md next-step field contains a next-step suggestion",
            "type": "content_check",
            "check": "state_next_step",
        },
        {
            "text": "state.md last-updated timestamp has been updated",
            "type": "content_check",
            "check": "state_last_updated",
        },
    ],
    "SA-02": [
        {
            "text": "CR status follows state machine (created->developing->verifying->...)",
            "type": "content_check",
            "check": "cr_status_valid",
        },
        {
            "text": "CR events list has new entries for status transitions",
            "type": "content_check",
            "check": "cr_events_updated",
        },
        {
            "text": "Event records include timestamp and trigger reason",
            "type": "content_check",
            "check": "cr_events_have_timestamp",
        },
    ],
    "SA-03": [
        {
            "text": "Output does not expose internal IDs (CR-xxx, PF-xxx format)",
            "type": "output_check",
            "check": "no_internal_ids",
        },
        {
            "text": "Output does not use state machine terminology (developing, in_review)",
            "type": "output_check",
            "check": "no_state_machine_terms",
        },
        {
            "text": "Output uses natural language descriptions",
            "type": "output_check",
            "check": "natural_language",
        },
    ],
    "SA-04": [
        {
            "text": "Default output is 3 lines or less overview",
            "type": "output_check",
            "check": "output_concise",
        },
    ],
    "SA-05": [
        {
            "text": "Git commit after meaningful work unit",
            "type": "behavior_check",
            "check": "git_committed",
        },
        {
            "text": "Commit message follows <type>(<scope>): <description> format",
            "type": "behavior_check",
            "check": "commit_format",
        },
    ],
    "SA-06": [
        {
            "text": "Output file Markdown structure matches _schema/ format",
            "type": "file_check",
            "check": "schema_compliant_structure",
        },
        {
            "text": "All required fields present in output file",
            "type": "content_check",
            "check": "required_fields_present",
        },
    ],
}


# ---------------------------------------------------------------------------
# Grader
# ---------------------------------------------------------------------------

class Grader:
    """Mixed G1/G2/G3 grading engine."""

    def __init__(self, *, llm_model: str | None = None):
        self._llm_model_override = llm_model
        self._llm_model: str | None = None  # resolved after client init
        self._client = None  # lazy init for G3
        self._is_bedrock = False

    def grade(
        self,
        assertion: dict,
        result: BehavioralResult,
    ) -> GradingResult:
        """Grade a single assertion against a behavioral result."""
        atype = assertion.get("type", "output_check")

        if atype == "file_check":
            return self._grade_file(assertion, result)
        elif atype == "content_check":
            return self._grade_content(assertion, result)
        elif atype == "behavior_check":
            return self._grade_behavior_llm(assertion, result)
        else:  # output_check
            return self._grade_output(assertion, result)

    def grade_all(
        self,
        assertions: list[dict],
        result: BehavioralResult,
    ) -> list[GradingResult]:
        """Grade all assertions, expanding shared patterns."""
        expanded = self._expand_shared_assertions(assertions)
        return [self.grade(a, result) for a in expanded]

    # -------------------------------------------------------------------
    # Shared assertion expansion
    # -------------------------------------------------------------------

    def _expand_shared_assertions(
        self,
        assertions: list[dict],
    ) -> list[dict]:
        """Expand shared_pattern references into concrete assertions."""
        expanded: list[dict] = []
        for assertion in assertions:
            pattern = assertion.get("shared_pattern")
            if pattern and pattern in SHARED_ASSERTIONS:
                # Add the original assertion first
                expanded.append(assertion)
                # Then add expanded sub-assertions
                for sub in SHARED_ASSERTIONS[pattern]:
                    expanded.append({
                        "text": sub["text"],
                        "type": sub["type"],
                        "shared_pattern": pattern,
                        "_check": sub.get("check"),
                    })
            else:
                expanded.append(assertion)
        return expanded

    # -------------------------------------------------------------------
    # G1: Programmatic file checks
    # -------------------------------------------------------------------

    def _grade_file(
        self,
        assertion: dict,
        result: BehavioralResult,
    ) -> GradingResult:
        """G1: Programmatic file existence and creation checks."""
        diff = result.devpace_diff

        # 1. Try named check from _check field
        check_name = assertion.get("_check", "")
        if check_name and check_name in NAMED_FILE_CHECKS:
            rv = NAMED_FILE_CHECKS[check_name](assertion, diff)
            if rv is not None:
                return GradingResult(
                    text=assertion["text"], type="file_check", grade_level="G1",
                    passed=rv[0], evidence=rv[1],
                    shared_pattern=assertion.get("shared_pattern"),
                )

        # 2. Try keyword-based checks
        for check_fn in KEYWORD_FILE_CHECKS:
            rv = check_fn(assertion, diff)
            if rv is not None:
                return GradingResult(
                    text=assertion["text"], type="file_check", grade_level="G1",
                    passed=rv[0], evidence=rv[1],
                    shared_pattern=assertion.get("shared_pattern"),
                )

        # 3. Generic fallback — any devpace file changes
        all_changed = diff.get("files_created", []) + diff.get("files_modified", [])
        passed = len(all_changed) > 0
        evidence = (
            f"Files changed: {', '.join(all_changed[:5])}"
            if passed
            else "No .devpace/ file changes detected"
        )
        return GradingResult(
            text=assertion["text"], type="file_check", grade_level="G1",
            passed=passed, evidence=evidence,
            shared_pattern=assertion.get("shared_pattern"),
        )

    # -------------------------------------------------------------------
    # G1/G2: Content and field checks
    # -------------------------------------------------------------------

    def _grade_content(
        self,
        assertion: dict,
        result: BehavioralResult,
    ) -> GradingResult:
        """G1/G2: Content field matching via regex/structural checks."""
        full_transcript = "\n".join(result.transcript_text)
        diff = result.devpace_diff

        # 1. Try named check from _check field
        check_name = assertion.get("_check", "")
        if check_name and check_name in NAMED_CONTENT_CHECKS:
            rv = NAMED_CONTENT_CHECKS[check_name](assertion, diff, full_transcript)
            if rv is not None:
                return GradingResult(
                    text=assertion["text"], type="content_check", grade_level="G1",
                    passed=rv[0], evidence=rv[1],
                    shared_pattern=assertion.get("shared_pattern"),
                )

        # 2. Try keyword-based checks
        for check_fn in KEYWORD_CONTENT_CHECKS:
            rv = check_fn(assertion, diff, full_transcript)
            if rv is not None:
                return GradingResult(
                    text=assertion["text"], type="content_check", grade_level="G1",
                    passed=rv[0], evidence=rv[1],
                    shared_pattern=assertion.get("shared_pattern"),
                )

        # 3. Fallback: G2 regex keyword scan, then G3 LLM
        return self._grade_content_fallback(assertion, result)

    def _grade_content_fallback(
        self,
        assertion: dict,
        result: BehavioralResult,
    ) -> GradingResult:
        """G2 fallback: attempt regex matching on transcript, else escalate to G3."""
        text = assertion["text"]
        full_transcript = "\n".join(result.transcript_text)

        # Try to extract key terms from assertion and search transcript
        key_terms = [w for w in text.lower().split() if len(w) > 3 and w not in {
            "that", "this", "with", "from", "into", "have", "been", "should",
            "must", "does", "includes", "contains", "section", "field",
        }]

        matches = sum(1 for term in key_terms if term in full_transcript.lower())
        match_ratio = matches / max(len(key_terms), 1)

        if match_ratio >= 0.5:
            return GradingResult(
                text=text,
                type="content_check",
                grade_level="G2",
                passed=True,
                evidence=f"Matched {matches}/{len(key_terms)} key terms in transcript (ratio={match_ratio:.2f})",
                shared_pattern=assertion.get("shared_pattern"),
            )

        # Escalate to G3 if available
        return self._grade_via_llm(assertion, result, "content_check")

    # -------------------------------------------------------------------
    # G2: Output checks (regex/structural)
    # -------------------------------------------------------------------

    def _grade_output(
        self,
        assertion: dict,
        result: BehavioralResult,
    ) -> GradingResult:
        """G2: Regex and structural matching on agent output."""
        full_transcript = "\n".join(result.transcript_text)

        # 1. Try named check from _check field
        check_name = assertion.get("_check", "")
        if check_name and check_name in NAMED_OUTPUT_CHECKS:
            rv = NAMED_OUTPUT_CHECKS[check_name](assertion, full_transcript)
            if rv is not None:
                return GradingResult(
                    text=assertion["text"], type="output_check", grade_level="G2",
                    passed=rv[0], evidence=rv[1],
                    shared_pattern=assertion.get("shared_pattern"),
                )

        # 2. Try keyword-based checks
        for check_fn in KEYWORD_OUTPUT_CHECKS:
            rv = check_fn(assertion, full_transcript)
            if rv is not None:
                return GradingResult(
                    text=assertion["text"], type="output_check", grade_level="G2",
                    passed=rv[0], evidence=rv[1],
                    shared_pattern=assertion.get("shared_pattern"),
                )

        # 3. Fallback: G2 keyword scan, then G3 LLM
        return self._grade_output_fallback(assertion, result)

    def _grade_output_fallback(
        self,
        assertion: dict,
        result: BehavioralResult,
    ) -> GradingResult:
        """G2 fallback for unmatched output checks: keyword scan then G3."""
        text = assertion["text"]
        full_transcript = "\n".join(result.transcript_text)

        key_terms = [w for w in text.lower().split() if len(w) > 3 and w not in {
            "that", "this", "with", "from", "into", "have", "been", "should",
            "must", "does", "output", "check",
        }]

        matches = sum(1 for term in key_terms if term in full_transcript.lower())
        match_ratio = matches / max(len(key_terms), 1)

        if match_ratio >= 0.5:
            return GradingResult(
                text=text,
                type="output_check",
                grade_level="G2",
                passed=True,
                evidence=f"Matched {matches}/{len(key_terms)} key terms (ratio={match_ratio:.2f})",
                shared_pattern=assertion.get("shared_pattern"),
            )

        return self._grade_via_llm(assertion, result, "output_check")

    # -------------------------------------------------------------------
    # G3: LLM-as-judge (behavior checks + escalated content/output)
    # -------------------------------------------------------------------

    def _grade_behavior_llm(
        self,
        assertion: dict,
        result: BehavioralResult,
    ) -> GradingResult:
        """G3: LLM judge for behavior assertions."""
        check = assertion.get("_check", "")

        # Try programmatic checks first for known behavior patterns
        if check == "git_committed":
            passed = len(result.git_log) > 0
            return GradingResult(
                text=assertion["text"],
                type="behavior_check",
                grade_level="G1",
                passed=passed,
                evidence=(
                    f"Git commits found: {', '.join(result.git_log[:3])}"
                    if passed
                    else "No git commits created during execution"
                ),
                shared_pattern=assertion.get("shared_pattern"),
            )

        if check == "commit_format":
            conventional = r"^[a-f0-9]+ (feat|fix|docs|refactor|test|chore)\(.+\): .+"
            matching = [c for c in result.git_log if re.match(conventional, c)]
            passed = len(matching) > 0
            return GradingResult(
                text=assertion["text"],
                type="behavior_check",
                grade_level="G1",
                passed=passed,
                evidence=(
                    f"Conventional commits: {', '.join(matching[:3])}"
                    if passed
                    else f"No conventional format commits. Git log: {result.git_log[:3]}"
                ),
                shared_pattern=assertion.get("shared_pattern"),
            )

        # Check tool calls for behavioral evidence
        text = assertion["text"].lower()

        # Branch creation check
        if "branch" in text and ("created" in text or "name" in text or "prefix" in text):
            bash_calls = [tc for tc in result.tool_calls if tc.name == "Bash"]
            git_branch_calls = [
                tc for tc in bash_calls
                if "branch" in json.dumps(tc.input).lower()
                or "checkout" in json.dumps(tc.input).lower()
            ]
            passed = len(git_branch_calls) > 0
            return GradingResult(
                text=assertion["text"],
                type="behavior_check",
                grade_level="G1",
                passed=passed,
                evidence=(
                    f"Git branch operations found: {len(git_branch_calls)} calls"
                    if passed
                    else "No git branch operations detected"
                ),
                shared_pattern=assertion.get("shared_pattern"),
            )

        # Read/locate checks
        if "reads" in text or "locates" in text or "loads" in text or "detects" in text:
            read_calls = [tc for tc in result.tool_calls if tc.name == "Read"]
            if read_calls:
                return GradingResult(
                    text=assertion["text"],
                    type="behavior_check",
                    grade_level="G1",
                    passed=True,
                    evidence=f"Read tool called {len(read_calls)} times",
                    shared_pattern=assertion.get("shared_pattern"),
                )

        # "Does not" negative checks
        if "does not" in text or "not start" in text or "does not reference" in text:
            # Negative assertions are hard to check programmatically
            # Escalate to G3
            return self._grade_via_llm(assertion, result, "behavior_check")

        # Fall through to LLM
        return self._grade_via_llm(assertion, result, "behavior_check")

    # -------------------------------------------------------------------
    # G3: LLM judge (shared)
    # -------------------------------------------------------------------

    _HAIKU_DEFAULT = "claude-haiku-4-5-20251001"

    def _get_llm_client(self):
        """Lazy-init Anthropic client for G3 grading."""
        if self._client is not None:
            return self._client

        client, is_bedrock = get_anthropic_client(require=False)
        if client is None:
            return None

        self._client = client
        self._is_bedrock = is_bedrock
        base_model = self._llm_model_override or self._HAIKU_DEFAULT
        self._llm_model = resolve_model_id(base_model, is_bedrock)
        return self._client

    def _grade_via_llm(
        self,
        assertion: dict,
        result: BehavioralResult,
        assertion_type: str,
    ) -> GradingResult:
        """G3: Use LLM to judge whether assertion passes."""
        client = self._get_llm_client()

        if client is None:
            return GradingResult(
                text=assertion["text"],
                type=assertion_type,
                grade_level="G3",
                passed=False,
                evidence="G3 unavailable: no Anthropic API client configured",
                shared_pattern=assertion.get("shared_pattern"),
            )

        # Build concise context for the LLM
        transcript_summary = "\n".join(result.transcript_text[:20])
        if len(transcript_summary) > 4000:
            transcript_summary = transcript_summary[:4000] + "\n... (truncated)"

        tool_summary = ", ".join(
            f"{tc.name}(turn={tc.turn})" for tc in result.tool_calls[:30]
        )

        diff_summary = json.dumps(result.devpace_diff, indent=2)
        git_summary = "\n".join(result.git_log[:10]) if result.git_log else "(no commits)"

        prompt = f"""You are an eval grader for a Claude Code plugin called "devpace".
An agent was given this prompt: "{result.prompt}"

Your task: determine whether this assertion PASSES or FAILS.

ASSERTION: {assertion["text"]}
TYPE: {assertion_type}

EVIDENCE:
--- Agent transcript (last 20 turns) ---
{transcript_summary}

--- Tool calls ---
{tool_summary}

--- .devpace/ file changes ---
{diff_summary}

--- Git log ---
{git_summary}

Respond with EXACTLY one JSON object (no other text):
{{"passed": true/false, "evidence": "brief explanation (1-2 sentences)"}}
"""

        try:
            response = client.messages.create(
                model=self._llm_model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            # Parse JSON from response (handle possible markdown wrapping)
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return GradingResult(
                    text=assertion["text"],
                    type=assertion_type,
                    grade_level="G3",
                    passed=bool(parsed.get("passed", False)),
                    evidence=parsed.get("evidence", raw),
                    shared_pattern=assertion.get("shared_pattern"),
                )
        except Exception as e:
            return GradingResult(
                text=assertion["text"],
                type=assertion_type,
                grade_level="G3",
                passed=False,
                evidence=f"G3 grading error: {e}",
                shared_pattern=assertion.get("shared_pattern"),
            )

        return GradingResult(
            text=assertion["text"],
            type=assertion_type,
            grade_level="G3",
            passed=False,
            evidence=f"G3 could not parse LLM response: {raw[:200]}",
            shared_pattern=assertion.get("shared_pattern"),
        )


# ---------------------------------------------------------------------------
# Batch grading + persistence
# ---------------------------------------------------------------------------

def grade_eval_case(
    grader: Grader,
    eval_case: dict,
    result: BehavioralResult,
) -> dict:
    """Grade a single eval case, producing grading.json-compatible output."""
    assertions = eval_case.get("assertions", [])
    gradings = grader.grade_all(assertions, result)

    by_grade: dict[str, dict] = {}
    for g in gradings:
        level = g.grade_level
        if level not in by_grade:
            by_grade[level] = {"total": 0, "passed": 0}
        by_grade[level]["total"] += 1
        if g.passed:
            by_grade[level]["passed"] += 1

    # Aggregate tool call counts
    tool_counts: dict[str, int] = {}
    for tc in result.tool_calls:
        tool_counts[tc.name] = tool_counts.get(tc.name, 0) + 1

    return {
        "skill": result.skill_name,
        "eval_id": result.eval_id,
        "eval_name": result.eval_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "assertions": [g.to_dict() for g in gradings],
        "summary": {
            "total": len(gradings),
            "passed": sum(1 for g in gradings if g.passed),
            "failed": sum(1 for g in gradings if not g.passed),
            "by_grade": by_grade,
        },
        "execution_metrics": {
            "tool_calls": tool_counts,
            "total_turns": result.total_turns,
            "total_tokens": result.total_tokens,
            "duration_seconds": result.duration_seconds,
            "errors_encountered": 1 if result.error else 0,
        },
        "devpace_diff": result.devpace_diff,
    }


def save_grading_results(
    skill_name: str,
    grading_outputs: list[dict],
) -> Path:
    """Save grading results to grading/ directory."""
    rdir = results_dir_for(skill_name)
    grading_dir = rdir / "grading"
    grading_dir.mkdir(exist_ok=True)

    output = {
        "skill": skill_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cases": grading_outputs,
        "summary": {
            "total_cases": len(grading_outputs),
            "total_assertions": sum(c["summary"]["total"] for c in grading_outputs),
            "total_passed": sum(c["summary"]["passed"] for c in grading_outputs),
            "total_failed": sum(c["summary"]["failed"] for c in grading_outputs),
        },
    }

    out_path = grading_dir / "grading.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    return out_path
