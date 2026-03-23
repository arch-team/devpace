"""Unit tests for eval.behavior.grader — G1 file checks and G2 content/output matching."""
from __future__ import annotations

import pytest
from eval.behavior.execute import BehavioralResult, ToolCall
from eval.behavior.grader import Grader, GradingResult, SHARED_ASSERTIONS, grade_eval_case


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(**overrides) -> BehavioralResult:
    """Create a BehavioralResult with sensible defaults."""
    defaults = dict(
        eval_id=1,
        eval_name="test-case",
        skill_name="pace-dev",
        prompt="test prompt",
        transcript_text=["Created CR-004 in .devpace/backlog/"],
        tool_calls=[],
        devpace_diff={
            "files_created": [".devpace/backlog/CR-004.md"],
            "files_modified": [".devpace/state.md"],
            "files_deleted": [],
        },
        git_log=["abc1234 feat(api): add time endpoint"],
        duration_seconds=42.0,
        total_turns=5,
    )
    defaults.update(overrides)
    return BehavioralResult(**defaults)


# ---------------------------------------------------------------------------
# G1: File checks
# ---------------------------------------------------------------------------

class TestG1FileChecks:
    def setup_method(self):
        self.grader = Grader()

    def test_cr_file_created_pass(self):
        result = _make_result()
        assertion = {"text": "New CR file created in .devpace/backlog/ with CR-xxx.md naming", "type": "file_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True
        assert gr.grade_level == "G1"
        assert "CR-004.md" in gr.evidence

    def test_cr_file_created_fail(self):
        result = _make_result(devpace_diff={
            "files_created": [],
            "files_modified": [".devpace/state.md"],
            "files_deleted": [],
        })
        assertion = {"text": "New CR file created in .devpace/backlog/ with CR-xxx.md naming", "type": "file_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is False
        assert gr.grade_level == "G1"

    def test_state_md_updated_pass(self):
        result = _make_result()
        assertion = {"text": "state.md updated with current-work referencing the CR", "type": "file_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True

    def test_state_md_updated_fail(self):
        result = _make_result(devpace_diff={
            "files_created": [".devpace/backlog/CR-004.md"],
            "files_modified": [],
            "files_deleted": [],
        })
        assertion = {"text": "state.md updated with current-work", "type": "file_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is False

    def test_context_md_generated(self):
        result = _make_result(devpace_diff={
            "files_created": [".devpace/context.md"],
            "files_modified": [],
            "files_deleted": [],
        })
        assertion = {"text": "context.md auto-generated if enough conventions detected", "type": "file_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True


# ---------------------------------------------------------------------------
# G1/G2: Content checks
# ---------------------------------------------------------------------------

class TestG1G2ContentChecks:
    def setup_method(self):
        self.grader = Grader()

    def test_cr_type_feature_pass(self):
        result = _make_result(
            transcript_text=["Creating CR with type: feature, complexity: S"],
        )
        assertion = {"text": "CR type is 'feature'", "type": "content_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True
        assert "feature" in gr.evidence.lower()

    def test_cr_type_defect_pass(self):
        result = _make_result(
            transcript_text=["This is a defect. Creating CR with type: defect"],
        )
        assertion = {"text": "CR type is 'defect' (not 'feature')", "type": "content_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True

    def test_cr_status_transition(self):
        result = _make_result()
        assertion = {"text": "CR status transitions from created to developing", "type": "content_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True  # CR file was created+modified

    def test_complexity_detected(self):
        result = _make_result(
            transcript_text=["Detected complexity: M (multiple components)"],
        )
        assertion = {"text": "Complexity detected as M or higher (multiple components)", "type": "content_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True


# ---------------------------------------------------------------------------
# G2: Output checks
# ---------------------------------------------------------------------------

class TestG2OutputChecks:
    def setup_method(self):
        self.grader = Grader()

    def test_no_internal_ids_pass(self):
        result = _make_result(
            transcript_text=["I created a change request for the new API endpoint."],
        )
        assertion = {"text": "Output uses natural language, no internal IDs exposed", "type": "output_check", "_check": "no_internal_ids"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True

    def test_no_internal_ids_fail(self):
        result = _make_result(
            transcript_text=["Created CR-004 and linked to PF-002."],
        )
        assertion = {"text": "Output check", "type": "output_check", "_check": "no_internal_ids"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is False
        assert "CR" in gr.evidence or "PF" in gr.evidence

    def test_execution_plan_detected(self):
        result = _make_result(
            transcript_text=["Here is my plan:\n1. Design schema\n2. Implement API\n3. Add tests"],
        )
        assertion = {"text": "Execution plan generated with numbered steps", "type": "output_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True

    def test_intent_checkpoint_detected(self):
        result = _make_result(
            transcript_text=["Before starting, let me confirm the scope with you. Does this approach work?"],
        )
        assertion = {"text": "Intent checkpoint performed: asks user to confirm scope/approach", "type": "output_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True


# ---------------------------------------------------------------------------
# Behavior checks (G1 programmatic path)
# ---------------------------------------------------------------------------

class TestBehaviorChecks:
    def setup_method(self):
        self.grader = Grader()

    def test_git_committed_pass(self):
        result = _make_result(git_log=["abc1234 feat(api): add time endpoint"])
        assertion = {"text": "Git commit after implementation", "type": "behavior_check", "_check": "git_committed"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True
        assert gr.grade_level == "G1"

    def test_git_committed_fail(self):
        result = _make_result(git_log=[])
        assertion = {"text": "Git commit after implementation", "type": "behavior_check", "_check": "git_committed"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is False

    def test_commit_format_pass(self):
        result = _make_result(git_log=["abc1234 feat(api): add time endpoint"])
        assertion = {"text": "Commit format check", "type": "behavior_check", "_check": "commit_format"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True
        assert gr.grade_level == "G1"

    def test_commit_format_fail(self):
        result = _make_result(git_log=["abc1234 added stuff"])
        assertion = {"text": "Commit format check", "type": "behavior_check", "_check": "commit_format"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is False

    def test_branch_creation_detected(self):
        result = _make_result(
            tool_calls=[
                ToolCall(name="Bash", input={"command": "git checkout -b feature/api-time"}, turn=2),
            ],
        )
        assertion = {"text": "Feature branch created with naming convention", "type": "behavior_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True

    def test_reads_cr_file(self):
        result = _make_result(
            tool_calls=[
                ToolCall(name="Read", input={"path": ".devpace/backlog/CR-003.md"}, turn=1),
            ],
        )
        assertion = {"text": "Locates and reads CR-003 from .devpace/backlog/", "type": "behavior_check"}
        gr = self.grader.grade(assertion, result)
        assert gr.passed is True
        assert gr.grade_level == "G1"


# ---------------------------------------------------------------------------
# Shared assertion expansion
# ---------------------------------------------------------------------------

class TestSharedAssertions:
    def setup_method(self):
        self.grader = Grader()

    def test_sa01_expansion(self):
        assertions = [
            {"text": "state.md updated", "type": "file_check", "shared_pattern": "SA-01"},
        ]
        result = _make_result()
        gradings = self.grader.grade_all(assertions, result)
        # Original + 3 expanded SA-01 sub-assertions = 4
        assert len(gradings) == 4

    def test_sa05_expansion(self):
        assertions = [
            {"text": "Git commit with format", "type": "behavior_check", "shared_pattern": "SA-05"},
        ]
        result = _make_result(git_log=["abc1234 feat(api): add endpoint"])
        gradings = self.grader.grade_all(assertions, result)
        # Original + 2 expanded SA-05 sub-assertions = 3
        assert len(gradings) == 3

    def test_no_expansion_without_pattern(self):
        assertions = [
            {"text": "Simple check", "type": "file_check"},
        ]
        result = _make_result()
        gradings = self.grader.grade_all(assertions, result)
        assert len(gradings) == 1

    def test_all_shared_patterns_defined(self):
        """Ensure all SA patterns referenced in design exist."""
        for sa_id in ["SA-01", "SA-02", "SA-03", "SA-04", "SA-05", "SA-06"]:
            assert sa_id in SHARED_ASSERTIONS, f"Missing shared assertion {sa_id}"


# ---------------------------------------------------------------------------
# grade_eval_case integration
# ---------------------------------------------------------------------------

class TestGradeEvalCase:
    def test_full_case_grading(self):
        grader = Grader()
        eval_case = {
            "id": 1,
            "name": "new-feature-simple",
            "prompt": "test",
            "assertions": [
                {"text": "New CR file created in .devpace/backlog/ with CR-xxx.md naming", "type": "file_check"},
                {"text": "CR type is 'feature'", "type": "content_check"},
                {"text": "state.md updated", "type": "file_check", "shared_pattern": "SA-01"},
            ],
        }
        result = _make_result(
            transcript_text=["Creating feature CR with type: feature"],
        )
        output = grade_eval_case(grader, eval_case, result)

        assert output["skill"] == "pace-dev"
        assert output["eval_id"] == 1
        assert output["summary"]["total"] > 0
        assert "assertions" in output
        assert "execution_metrics" in output
        assert "devpace_diff" in output
        # Should have 3 original + 3 expanded SA-01 = 6
        assert output["summary"]["total"] == 6
