"""TC-IR: Iron Rule enforcement mapping from ia-principles-details.md S7.

Verifies that each Iron Rule (IR-N) declared in devpace-rules.md has:
- Presence in the S0 core index (TC-IR-01)
- Anti-rationalization text where applicable (TC-IR-02)
- Documented and existing enforcement artifacts for critical rules (TC-IR-03, TC-IR-04)
"""
import re

import pytest

from tests.conftest import DEVPACE_ROOT, RULES_FILE

HOOKS_DIR = DEVPACE_ROOT / "hooks"
KNOWLEDGE_DIR = DEVPACE_ROOT / "knowledge"

# All declared Iron Rules
IR_IDS = ["IR-1", "IR-2", "IR-3", "IR-4", "IR-5"]

# Critical IRs that must have explicit anti-rationalization in S0
IR_WITH_ANTI_RATIONALIZATION = ["IR-1", "IR-2"]


def _rules_content():
    return RULES_FILE.read_text(encoding="utf-8")


def _section0_text(content):
    """Extract S0 text (everything before ## S1)."""
    match = re.search(r"\n## §1[ \n]", content)
    return content[:match.start()] if match else content[:2000]


@pytest.mark.static
class TestIronRuleIndex:
    """TC-IR-01/02: Iron Rule index completeness and anti-rationalization."""

    def test_tc_ir_01_all_irs_in_section0(self):
        """TC-IR-01: S0 核心铁律 section lists all IR-1 through IR-5."""
        s0 = _section0_text(_rules_content())
        missing = [ir for ir in IR_IDS if ir not in s0]
        assert not missing, (
            f"S0 核心铁律 missing: {missing}. "
            f"ACTION: Add missing IR entries to the '### 核心铁律' section in S0."
        )

    def test_tc_ir_02_critical_irs_have_anti_rationalization(self):
        """TC-IR-02: Critical IRs (IR-1, IR-2) have anti-rationalization text in S0.

        Ref: ia-principles-details.md S9 — iron rules must have anti-rationalization lists.
        """
        s0 = _section0_text(_rules_content())
        missing = []
        for ir_id in IR_WITH_ANTI_RATIONALIZATION:
            # Find the IR line and check it has 预防 text
            pattern = re.compile(rf"\*\*{ir_id}\*\*.*预防", re.DOTALL)
            # Search within a reasonable window after the IR marker
            ir_pos = s0.find(f"**{ir_id}**")
            if ir_pos == -1:
                missing.append(f"{ir_id}: not found in S0")
                continue
            # Check the same line or next few lines for 预防
            window = s0[ir_pos:ir_pos + 300]
            if "预防" not in window:
                missing.append(f"{ir_id}: no '预防' (anti-rationalization) text")
        assert not missing, (
            f"Critical Iron Rules missing anti-rationalization:\n"
            + "\n".join(f"  {m}" for m in missing)
            + "\nACTION: Add '预防：<common excuse> → <rebuttal>' after each critical IR in S0."
        )


@pytest.mark.static
class TestIronRuleEnforcement:
    """TC-IR-03/04: Enforcement artifacts exist for critical Iron Rules."""

    def test_tc_ir_03_ir2_hook_enforcement(self):
        """TC-IR-03: IR-2 (Gate 3 human approval) has Hook enforcement mechanism.

        IR-2 is enforced by pre-tool-use.mjs and documented in hook-architecture.md.
        """
        content = _rules_content()
        # Verify rules reference the Hook mechanism for IR-2 (may be in S0 or body)
        # Search all lines mentioning IR-2 for Hook enforcement keywords
        ir2_lines = [line for line in content.splitlines() if "IR-2" in line]
        ir2_text = "\n".join(ir2_lines)
        assert "pre-tool-use" in ir2_text or "Hook" in ir2_text, (
            "IR-2 section does not reference Hook enforcement mechanism. "
            "ACTION: Document 'IR-2 Hook 执行机制' referencing pre-tool-use.mjs."
        )
        # Verify enforcement artifacts exist on disk
        hook_script = HOOKS_DIR / "pre-tool-use.mjs"
        assert hook_script.exists(), (
            f"IR-2 enforcement artifact missing: {hook_script}. "
            "ACTION: Create pre-tool-use.mjs Hook to enforce Gate 3 human approval."
        )
        hook_arch = KNOWLEDGE_DIR / "_guides" / "hook-architecture.md"
        assert hook_arch.exists(), (
            f"IR-2 architecture doc missing: {hook_arch}. "
            "ACTION: Document Gate 3 Hook enforcement in hook-architecture.md."
        )

    def test_tc_ir_04_ir1_scope_enforcement(self):
        """TC-IR-04: IR-1 (explore mode no .devpace/ writes) has scope enforcement.

        IR-1 is enforced by skill-level scope-check hooks and skill-eval.mjs (UserPromptSubmit).
        """
        content = _rules_content()
        # Verify IR-1 is referenced in rules body (not just S0)
        body_ir1_count = content.count("IR-1")
        assert body_ir1_count >= 3, (
            f"IR-1 referenced only {body_ir1_count} times — expected ≥3 (S0 + body + cross-refs). "
            "ACTION: Ensure IR-1 is reinforced in S2 (dual mode) and relevant procedure references."
        )
        # Verify scope-check hooks exist (enforce .devpace/ write protection)
        scope_hooks = list(HOOKS_DIR.glob("skill/*-scope-check*"))
        assert len(scope_hooks) >= 1, (
            "No skill-level scope-check hooks found for IR-1 enforcement. "
            "ACTION: Create scope-check hooks to prevent .devpace/ writes in explore mode."
        )
        # Verify skill-eval hook exists (subsumes intent-detect for mode transitions)
        skill_eval_hook = HOOKS_DIR / "skill-eval.mjs"
        assert skill_eval_hook.exists(), (
            f"IR-1 supporting artifact missing: {skill_eval_hook}. "
            "ACTION: skill-eval.mjs handles intent detection (subsumes intent-detect.mjs)."
        )
