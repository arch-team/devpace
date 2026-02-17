"""TC-SM: State machine consistency across files."""
import re
import pytest
from tests.conftest import (
    DEVPACE_ROOT, CR_STATES, FORWARD_TRANSITIONS, REJECT_TRANSITIONS,
)

WORKFLOW_TEMPLATE = DEVPACE_ROOT / "skills" / "pace-init" / "templates" / "workflow.md"
CHECKS_TEMPLATE = DEVPACE_ROOT / "skills" / "pace-init" / "templates" / "checks.md"
CR_SCHEMA = DEVPACE_ROOT / "knowledge" / "_schema" / "cr-format.md"


@pytest.mark.static
class TestStateMachine:
    def test_tc_sm_01_seven_states_defined(self):
        """TC-SM-01: workflow.md defines all 7 states."""
        content = WORKFLOW_TEMPLATE.read_text(encoding="utf-8")
        missing = [s for s in CR_STATES if s not in content]
        assert not missing, f"workflow.md missing states: {missing}"

    def test_tc_sm_02_forward_transitions(self):
        """TC-SM-02: Forward transitions are complete."""
        content = WORKFLOW_TEMPLATE.read_text(encoding="utf-8")
        for src, dst in FORWARD_TRANSITIONS:
            pattern = f"{src}.*{dst}"
            assert re.search(pattern, content, re.DOTALL), \
                f"workflow.md missing forward transition: {src} → {dst}"

    def test_tc_sm_03_reject_transition(self):
        """TC-SM-03: Rejection transition (in_review→developing) exists."""
        content = WORKFLOW_TEMPLATE.read_text(encoding="utf-8")
        for src, dst in REJECT_TRANSITIONS:
            assert src in content and dst in content, \
                f"workflow.md missing reject transition: {src} → {dst}"

    def test_tc_sm_04_paused_transitions(self):
        """TC-SM-04: Paused transitions (any→paused, paused→resume) defined."""
        content = WORKFLOW_TEMPLATE.read_text(encoding="utf-8")
        assert "paused" in content, "workflow.md missing paused state"
        # Should mention that any state can go to paused
        has_any_to_paused = (
            "任何状态" in content or
            "any" in content.lower() or
            "⇄ paused" in content
        )
        assert has_any_to_paused, "workflow.md missing any→paused transition rule"
        # Should mention restoration
        has_resume = "恢复" in content or "resume" in content.lower()
        assert has_resume, "workflow.md missing paused→resume rule"

    def test_tc_sm_05_checks_align_with_workflow(self):
        """TC-SM-05: checks.md gates align with workflow.md transitions."""
        checks = CHECKS_TEMPLATE.read_text(encoding="utf-8")
        # Gate 1: developing → verifying
        assert "developing" in checks and "verifying" in checks, \
            "checks.md missing developing→verifying gate"
        # Gate 2: verifying → in_review
        assert "in_review" in checks or "review" in checks.lower(), \
            "checks.md missing verifying→in_review gate"

    def test_tc_sm_06_cr_schema_states_consistent(self):
        """TC-SM-06: cr-format.md status values match workflow.md states."""
        cr_content = CR_SCHEMA.read_text(encoding="utf-8")
        for state in CR_STATES:
            assert state in cr_content, \
                f"cr-format.md missing state: {state}"
