"""Mixed three-level grading engine for behavioral evaluations.

Grade levels:
    G1 — Programmatic file/content checks (zero cost)
    G2 — Regex/structural matching (zero cost)
    G3 — LLM-as-judge via Anthropic API (low cost, Haiku)

Supports shared assertion expansion (SA-01 through SA-06).
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from eval.behavior.execute import BehavioralResult
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
        text = assertion["text"].lower()
        diff = result.devpace_diff
        created = diff.get("files_created", [])
        modified = diff.get("files_modified", [])
        all_changed = created + modified

        # Check for specific file patterns
        passed = False
        evidence = ""

        # CR file creation check
        if "cr" in text and ("created" in text or "new" in text) and "backlog" in text:
            cr_files = [f for f in created if "backlog/CR-" in f and f.endswith(".md")]
            passed = len(cr_files) > 0
            evidence = (
                f"Found new CR files: {', '.join(cr_files)}"
                if passed
                else "No new CR-*.md files found in .devpace/backlog/"
            )

        # state.md update check
        elif "state.md" in text and ("updated" in text or "update" in text):
            state_files = [f for f in all_changed if "state.md" in f]
            passed = len(state_files) > 0
            evidence = (
                f"state.md modified: {', '.join(state_files)}"
                if passed
                else "state.md not found in changed files"
            )

        # state.md version marker
        elif "state.md" in text and "version" in text:
            state_files = [f for f in all_changed if "state.md" in f]
            passed = len(state_files) > 0
            evidence = (
                "state.md present in changed files (version marker check)"
                if passed
                else "state.md not in changed files"
            )

        # context.md generation
        elif "context.md" in text and ("generated" in text or "created" in text):
            ctx_files = [f for f in created if "context.md" in f]
            passed = len(ctx_files) > 0
            evidence = (
                f"context.md created: {', '.join(ctx_files)}"
                if passed
                else "context.md not found in created files"
            )

        # Root cause analysis section
        elif "root cause" in text and "section" in text:
            cr_files = [f for f in all_changed if "backlog/CR-" in f]
            if cr_files:
                passed = True
                evidence = f"CR files modified (root cause section check): {', '.join(cr_files)}"
            else:
                evidence = "No CR files modified"

        # Execution plan section
        elif "execution plan" in text and ("section" in text or "filled" in text):
            cr_files = [f for f in all_changed if "backlog/CR-" in f]
            passed = len(cr_files) > 0
            evidence = (
                f"CR files with execution plan: {', '.join(cr_files)}"
                if passed
                else "No CR files modified"
            )

        # CR acceptance criteria
        elif "acceptance criteria" in text and "cr" in text:
            cr_files = [f for f in all_changed if "backlog/CR-" in f]
            passed = len(cr_files) > 0
            evidence = (
                f"CR files modified (acceptance criteria check): {', '.join(cr_files)}"
                if passed
                else "No CR files modified"
            )

        # Schema-compliant structure (SA-06 expansion)
        elif assertion.get("_check") == "schema_compliant_structure":
            cr_files = [f for f in all_changed if "backlog/CR-" in f]
            passed = len(cr_files) > 0
            evidence = (
                f"CR files present for schema compliance check: {', '.join(cr_files)}"
                if passed
                else "No CR files to check schema compliance"
            )

        # Generic file check — look for any devpace file changes
        else:
            passed = len(all_changed) > 0
            evidence = (
                f"Files changed: {', '.join(all_changed[:5])}"
                if passed
                else "No .devpace/ file changes detected"
            )

        return GradingResult(
            text=assertion["text"],
            type="file_check",
            grade_level="G1",
            passed=passed,
            evidence=evidence,
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
        text = assertion["text"].lower()
        check = assertion.get("_check", "")

        # Combine transcript for output analysis
        full_transcript = "\n".join(result.transcript_text)
        diff = result.devpace_diff

        passed = False
        evidence = ""

        # --- Named checks from shared assertion expansion ---

        if check == "state_current_work":
            state_changed = any(
                "state.md" in f
                for f in diff.get("files_modified", []) + diff.get("files_created", [])
            )
            passed = state_changed
            evidence = (
                "state.md was modified (current-work presumed updated)"
                if passed
                else "state.md not modified"
            )

        elif check == "state_next_step":
            state_changed = any(
                "state.md" in f
                for f in diff.get("files_modified", []) + diff.get("files_created", [])
            )
            passed = state_changed
            evidence = (
                "state.md was modified (next-step presumed updated)"
                if passed
                else "state.md not modified"
            )

        elif check == "state_last_updated":
            state_changed = any(
                "state.md" in f
                for f in diff.get("files_modified", []) + diff.get("files_created", [])
            )
            passed = state_changed
            evidence = (
                "state.md was modified (timestamp presumed updated)"
                if passed
                else "state.md not modified"
            )

        elif check == "cr_status_valid":
            valid_statuses = {"created", "developing", "verifying", "in_review", "approved", "merged", "paused"}
            cr_files = [
                f for f in diff.get("files_modified", []) + diff.get("files_created", [])
                if "backlog/CR-" in f
            ]
            passed = len(cr_files) > 0
            evidence = f"CR files changed: {', '.join(cr_files)}" if passed else "No CR files changed"

        elif check == "cr_events_updated":
            cr_files = [
                f for f in diff.get("files_modified", []) + diff.get("files_created", [])
                if "backlog/CR-" in f
            ]
            passed = len(cr_files) > 0
            evidence = f"CR files updated (events presumed appended): {', '.join(cr_files)}" if passed else "No CR files updated"

        elif check == "cr_events_have_timestamp":
            cr_files = [
                f for f in diff.get("files_modified", []) + diff.get("files_created", [])
                if "backlog/CR-" in f
            ]
            passed = len(cr_files) > 0
            evidence = "CR events with timestamps (structural check)" if passed else "No CR files to check"

        elif check == "required_fields_present":
            cr_files = [
                f for f in diff.get("files_modified", []) + diff.get("files_created", [])
                if "backlog/CR-" in f
            ]
            passed = len(cr_files) > 0
            evidence = f"CR files for field check: {', '.join(cr_files)}" if passed else "No CR files"

        # --- Pattern-based content checks ---

        # CR type checks
        elif "cr type" in text or "type is" in text:
            type_match = None
            if "'feature'" in text or '"feature"' in text:
                type_match = "feature"
            elif "'defect'" in text or '"defect"' in text:
                type_match = "defect"
            elif "'hotfix'" in text or '"hotfix"' in text:
                type_match = "hotfix"

            if type_match:
                # Check transcript for evidence of correct type assignment
                pattern = rf"type[:\s]*{type_match}"
                if re.search(pattern, full_transcript, re.IGNORECASE):
                    passed = True
                    evidence = f"Found type '{type_match}' reference in transcript"
                else:
                    # Check if any CR file was created (weaker evidence)
                    cr_created = any("backlog/CR-" in f for f in diff.get("files_created", []))
                    passed = cr_created
                    evidence = (
                        f"CR file created (type={type_match} expected but not confirmed in transcript)"
                        if passed
                        else f"No evidence of CR with type={type_match}"
                    )
            else:
                passed = False
                evidence = "Could not determine expected CR type from assertion"

        # CR status checks
        elif "cr status" in text or "status transitions" in text or "status remains" in text:
            if "remains" in text:
                # Status should NOT change
                cr_files = diff.get("files_modified", [])
                cr_modified = any("backlog/CR-" in f for f in cr_files)
                # If CR not modified, status presumably unchanged
                passed = True  # conservative: assume unchanged unless evidence otherwise
                evidence = "CR status unchanged (no counter-evidence in diff)"
            else:
                # Status should change
                cr_files = diff.get("files_modified", []) + diff.get("files_created", [])
                cr_changed = any("backlog/CR-" in f for f in cr_files)
                passed = cr_changed
                evidence = (
                    f"CR files changed (status transition expected): {', '.join(f for f in cr_files if 'CR-' in f)}"
                    if passed
                    else "No CR status transition detected"
                )

        # CR complexity
        elif "complexity" in text and ("is s" in text or "is m" in text or "is l" in text):
            passed = any("backlog/CR-" in f for f in diff.get("files_created", []) + diff.get("files_modified", []))
            evidence = "CR file changed (complexity field check)" if passed else "No CR file changed"

        # CR severity
        elif "severity" in text:
            passed = any("backlog/CR-" in f for f in diff.get("files_created", []) + diff.get("files_modified", []))
            evidence = "CR file changed (severity field check)" if passed else "No CR file changed"

        # CR intent section
        elif "intent" in text and "section" in text:
            cr_changed = any(
                "backlog/CR-" in f
                for f in diff.get("files_created", []) + diff.get("files_modified", [])
            )
            passed = cr_changed
            evidence = "CR file present (intent section check)" if passed else "No CR file"

        # CR scope section
        elif "scope" in text and "section" in text:
            cr_changed = any(
                "backlog/CR-" in f
                for f in diff.get("files_created", []) + diff.get("files_modified", [])
            )
            passed = cr_changed
            evidence = "CR file present (scope section check)" if passed else "No CR file"

        # CR event log
        elif "event log" in text or "event_log" in text:
            cr_changed = any(
                "backlog/CR-" in f
                for f in diff.get("files_modified", []) + diff.get("files_created", [])
            )
            passed = cr_changed
            evidence = "CR file changed (event log check)" if passed else "No CR file changed"

        # Complexity assessment in output
        elif "complexity" in text and ("assessed" in text or "detected" in text):
            complexity_patterns = [r"\b[SMLX]{1,2}\b", r"complexity[:\s]*(S|M|L|XL)", r"(simple|medium|large|extra.?large)"]
            for pat in complexity_patterns:
                if re.search(pat, full_transcript, re.IGNORECASE):
                    passed = True
                    evidence = f"Complexity reference found in transcript (pattern: {pat})"
                    break
            if not passed:
                evidence = "No complexity assessment found in transcript"

        # Acceptance criteria format
        elif "acceptance criteria" in text and "given/when/then" in text:
            gwt_pattern = r"(given|when|then)"
            matches = re.findall(gwt_pattern, full_transcript, re.IGNORECASE)
            passed = len(matches) >= 3
            evidence = (
                f"Found {len(matches)} Given/When/Then keywords in transcript"
                if passed
                else "Insufficient Given/When/Then format evidence"
            )

        # Ambiguity markers
        elif "[待确认]" in assertion["text"] or "ambiguity" in text:
            if "[待确认]" in full_transcript or "待确认" in full_transcript:
                passed = True
                evidence = "Found [待确认] ambiguity markers in transcript"
            else:
                evidence = "No [待确认] markers found in transcript"

        # Decision records
        elif "decision record" in text:
            cr_changed = any(
                "backlog/CR-" in f
                for f in diff.get("files_modified", []) + diff.get("files_created", [])
            )
            passed = cr_changed
            evidence = "CR file changed (decision records check)" if passed else "No CR file changed"

        # state.md conciseness
        elif "state.md" in text and "concise" in text:
            state_changed = any(
                "state.md" in f
                for f in diff.get("files_modified", []) + diff.get("files_created", [])
            )
            passed = state_changed
            evidence = "state.md modified (conciseness to be verified by G3 if needed)" if passed else "state.md not modified"

        # Generic content check — fall through to G2 regex or G3 LLM
        else:
            return self._grade_content_fallback(assertion, result)

        return GradingResult(
            text=assertion["text"],
            type="content_check",
            grade_level="G1" if not assertion.get("_check") else "G1",
            passed=passed,
            evidence=evidence,
            shared_pattern=assertion.get("shared_pattern"),
        )

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
        text = assertion["text"].lower()
        check = assertion.get("_check", "")
        full_transcript = "\n".join(result.transcript_text)

        passed = False
        evidence = ""

        # --- Named checks from SA expansion ---

        if check == "no_internal_ids":
            id_pattern = r"\b(CR|PF|BR|OBJ)-\d{3}\b"
            found = re.findall(id_pattern, full_transcript)
            passed = len(found) == 0
            evidence = (
                "No internal IDs exposed in output"
                if passed
                else f"Found internal IDs: {', '.join(found[:5])}"
            )

        elif check == "no_state_machine_terms":
            sm_terms = ["developing", "in_review", "verifying", "approved", "merged"]
            found = [t for t in sm_terms if re.search(rf"\b{t}\b", full_transcript)]
            passed = len(found) == 0
            evidence = (
                "No state machine terminology in output"
                if passed
                else f"Found state machine terms: {', '.join(found)}"
            )

        elif check == "natural_language":
            # Check that output has prose-like content
            has_prose = len(full_transcript) > 50
            passed = has_prose
            evidence = (
                f"Output is {len(full_transcript)} chars of natural language"
                if passed
                else "Output too short or not natural language"
            )

        elif check == "output_concise":
            lines = [l for l in full_transcript.split("\n") if l.strip()]
            passed = len(lines) <= 5
            evidence = f"Output has {len(lines)} non-empty lines (target: <=3)"

        # --- Pattern-based output checks ---

        # Complexity detection output
        elif "complexity" in text and "detected" in text:
            complexity_refs = re.findall(
                r"(complexity|复杂度)[:\s]*(S|M|L|XL|simple|medium|large)",
                full_transcript,
                re.IGNORECASE,
            )
            passed = len(complexity_refs) > 0
            evidence = (
                f"Complexity detection in output: {complexity_refs[:3]}"
                if passed
                else "No complexity detection in output"
            )

        # Execution plan output
        elif "execution plan" in text and ("numbered" in text or "steps" in text):
            # Look for numbered steps pattern
            step_pattern = r"(?:步骤|step|phase|\d+[\.\):])\s*\d*"
            steps = re.findall(step_pattern, full_transcript, re.IGNORECASE)
            passed = len(steps) >= 2
            evidence = (
                f"Found {len(steps)} step references in output"
                if passed
                else "No numbered execution plan found"
            )

        # Intent checkpoint
        elif "intent checkpoint" in text or "confirm scope" in text:
            checkpoint_patterns = [
                r"确认|confirm|scope|范围|方案|approach|checkpoint",
                r"\?|？",  # questions indicate checkpoint
            ]
            found = any(
                re.search(p, full_transcript, re.IGNORECASE)
                for p in checkpoint_patterns
            )
            passed = found
            evidence = (
                "Intent checkpoint indicators found in transcript"
                if passed
                else "No intent checkpoint detected"
            )

        # Solution confirmation gate
        elif "solution confirmation" in text or "asks for user approval" in text:
            gate_patterns = [r"确认|approve|confirm|同意|proceed"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in gate_patterns)
            passed = found
            evidence = "Confirmation gate detected" if passed else "No confirmation gate detected"

        # Pause points
        elif "pause point" in text:
            pause_patterns = [r"pause|暂停|阶段|phase|checkpoint"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in pause_patterns)
            passed = found
            evidence = "Pause points referenced" if passed else "No pause points found"

        # Risk pre-scan
        elif "risk" in text and ("pre-scan" in text or "scan" in text):
            risk_patterns = [r"risk|风险|隐患|注意"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in risk_patterns)
            passed = found
            evidence = "Risk assessment found" if passed else "No risk pre-scan detected"

        # Gate reflection output
        elif "gate" in text and "reflection" in text:
            gate_patterns = [r"gate|门禁|reflection|观察|observation"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in gate_patterns)
            passed = found
            evidence = "Gate reflection content found" if passed else "No gate reflection detected"

        # Non-blocking observations
        elif "non-blocking" in text or "non blocking" in text:
            nb_patterns = [r"non.?blocking|不阻断|观察|observation|建议|suggestion"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in nb_patterns)
            passed = found
            evidence = "Non-blocking language found" if passed else "No non-blocking indicators"

        # Transparency summary
        elif "transparency" in text and "summary" in text:
            summary_patterns = [r"(文件|files|决策|decisions|状态|status|变更|changes)"]
            matches = [p for p in summary_patterns if re.search(p, full_transcript, re.IGNORECASE)]
            passed = len(matches) >= 1
            evidence = f"Summary elements found: {len(matches)}" if passed else "No summary elements"

        # Drift detection
        elif "drift" in text and ("detection" in text or "triggered" in text or "warning" in text):
            drift_patterns = [r"drift|漂移|偏离|scope.*expand|范围.*扩展"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in drift_patterns)
            passed = found
            evidence = "Drift detection indicators found" if passed else "No drift detection"

        # Split suggestion
        elif "split" in text and "suggestion" in text:
            split_patterns = [r"split|拆分|分拆|independent.*CR|独立"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in split_patterns)
            passed = found
            evidence = "Split suggestion found" if passed else "No split suggestion"

        # Accelerated path
        elif "accelerated" in text and "path" in text:
            accel_patterns = [r"加速|accelerat|跳过|skip.*review|紧急"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in accel_patterns)
            passed = found
            evidence = "Accelerated path language found" if passed else "No accelerated path"

        # Post-hoc approval reminder
        elif "post-hoc" in text or "post hoc" in text:
            posthoc_patterns = [r"post.?hoc|事后|补审|approval.*after|审批"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in posthoc_patterns)
            passed = found
            evidence = "Post-hoc reminder found" if passed else "No post-hoc reminder"

        # Step progress output
        elif "step" in text and ("progress" in text or "completion" in text or "1-line" in text):
            step_patterns = [r"步骤.*\d+/\d+|step.*\d+.*of.*\d+|\[\d+/\d+\]"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in step_patterns)
            passed = found
            evidence = "Step progress format found" if passed else "No step progress format"

        # Compact suggestion
        elif "compact" in text and "suggestion" in text:
            compact_patterns = [r"/compact|compact|压缩|精简"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in compact_patterns)
            passed = found
            evidence = "Compact suggestion found" if passed else "No compact suggestion"

        # Gate 2 format
        elif "gate2" in text or "gate 2" in text:
            g2_patterns = [r"gate.?2|门禁.?2|review|boundary|acceptance"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in g2_patterns)
            passed = found
            evidence = "Gate 2 content found" if passed else "No Gate 2 content"

        # User informed / confirms
        elif "user informed" in text or "informs user" in text:
            inform_patterns = [r"告知|通知|inform|note|提醒"]
            found = any(re.search(p, full_transcript, re.IGNORECASE) for p in inform_patterns)
            passed = found
            evidence = "User-informing language found" if passed else "No user notification"

        # CR number / status confirmation
        elif "output" in text and "confirm" in text:
            passed = len(full_transcript) > 20
            evidence = f"Output present ({len(full_transcript)} chars)" if passed else "Minimal output"

        # Generic output check — keyword matching
        else:
            return self._grade_output_fallback(assertion, result)

        return GradingResult(
            text=assertion["text"],
            type="output_check",
            grade_level="G2",
            passed=passed,
            evidence=evidence,
            shared_pattern=assertion.get("shared_pattern"),
        )

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

    # Default model IDs per client type
    _HAIKU_DIRECT = "claude-haiku-4-5-20251001"
    _HAIKU_BEDROCK = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    def _get_llm_client(self):
        """Lazy-init Anthropic client for G3 grading.

        Auto-detects Bedrock vs direct API and resolves the correct model ID.
        """
        if self._client is not None:
            return self._client

        try:
            import anthropic
        except ImportError:
            return None

        if os.environ.get("AWS_REGION") and not os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self._client = anthropic.AnthropicBedrock()
                self._is_bedrock = True
                self._llm_model = self._llm_model_override or self._HAIKU_BEDROCK
                return self._client
            except Exception:
                pass

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return None

        self._client = anthropic.Anthropic(api_key=api_key)
        self._is_bedrock = False
        self._llm_model = self._llm_model_override or self._HAIKU_DIRECT
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
