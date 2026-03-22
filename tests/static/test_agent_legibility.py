"""TC-AL: Agent legibility checks from harness-engineering.md S2/S4.

Encodes the Harness quality detection commands that were previously manual-only:
- TC-AL-01 (G1): Hook .mjs output includes ACTION repair instructions (HE-4)
- TC-AL-02 (G2): Procedure files have no ambiguous wording (HE-3)
- TC-AL-03 (G3): Schema table field names are self-explanatory (HE-3)
"""
import re

import pytest

from tests.conftest import DEVPACE_ROOT, SKILL_NAMES, SCHEMA_DIR, _is_workspace_path

HOOKS_DIR = DEVPACE_ROOT / "hooks"
SKILLS_DIR = DEVPACE_ROOT / "skills"

FENCE_RE = re.compile(r"```[^\n]*\n.*?```", re.DOTALL)


def _strip_fences(content: str) -> str:
    """Replace fenced code blocks with equal-length newlines to preserve line numbers."""
    return FENCE_RE.sub(lambda m: "\n" * m.group().count("\n"), content)


@pytest.mark.static
class TestHookRepairInstructions:
    """G1/HE-4: Hook output messages must be Agent-executable repair instructions."""

    def test_tc_al_01_console_output_has_action(self):
        """TC-AL-01: console.log/error in hooks .mjs (outside lib/) includes ACTION or devpace:.

        Ref: harness-engineering.md S4 HE-4.
        Format: devpace:<tag> <status>. ACTION: <step1>; <step2>; <alt path>.
        """
        console_re = re.compile(r"console\.(log|error)\s*\(")
        action_re = re.compile(r"ACTION:|devpace:")
        violations = []

        for f in HOOKS_DIR.rglob("*.mjs"):
            # Skip lib/ (shared utilities, not user-facing output)
            rel = f.relative_to(HOOKS_DIR)
            if rel.parts and rel.parts[0] == "lib":
                continue

            lines = f.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines, 1):
                if not console_re.search(line):
                    continue
                # Check a window of +/-3 lines for multi-line template literals
                window_start = max(0, i - 4)
                window_end = min(len(lines), i + 3)
                window = "\n".join(lines[window_start:window_end])
                if not action_re.search(window):
                    violations.append(
                        f"{f.relative_to(DEVPACE_ROOT)}:{i}: {line.strip()[:120]}"
                    )

        assert not violations, (
            f"Hook console output without ACTION repair instructions ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nACTION: Add 'ACTION: <repair steps>' to every hook console.log/error. "
            "Format: 'devpace:<tag> <status>. ACTION: <step1>; <step2>.'"
        )


@pytest.mark.static
class TestProcedureClarity:
    """G2/HE-3: Procedure instructions must be precise and unambiguous."""

    AMBIGUOUS_TERMS = ["自行判断", "酌情", "适当时"]

    def test_tc_al_02_no_ambiguous_wording(self):
        """TC-AL-02: Procedure files contain no ambiguous wording.

        Ref: harness-engineering.md S4 HE-3.
        These terms leave execution to LLM judgment instead of explicit conditions.
        """
        pattern = re.compile("|".join(re.escape(t) for t in self.AMBIGUOUS_TERMS))
        violations = []

        for name in SKILL_NAMES:
            for proc in (SKILLS_DIR / name).glob("*-procedures*.md"):
                if _is_workspace_path(proc):
                    continue
                text = _strip_fences(proc.read_text(encoding="utf-8"))
                for i, line in enumerate(text.splitlines(), 1):
                    m = pattern.search(line)
                    if m:
                        violations.append(
                            f"{proc.relative_to(DEVPACE_ROOT)}:{i}: "
                            f"'{m.group()}' in: {line.strip()[:100]}"
                        )

        assert not violations, (
            f"Procedures use ambiguous wording ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nACTION: Replace with explicit conditions -- "
            "'自行判断' -> 'if X then A; else B'; "
            "'酌情' -> specific criteria; "
            "'适当时' -> concrete trigger condition."
        )


@pytest.mark.static
class TestSchemaFieldNames:
    """G3/HE-3: Schema table field names must be self-explanatory, not abbreviated."""

    # Short names that are universally understood domain terms, not abbreviations
    ALLOWED_SHORT = {"id", "url", "uri", "ip", "os", "ci", "cd", "biz", "pm", "ops", "dev"}

    def test_tc_al_03_no_abbreviated_field_names(self):
        """TC-AL-03: Schema table first-column entries are not 1-3 char abbreviations.

        Ref: harness-engineering.md S2 HE-3.
        Use acceptance_criteria not ac, blocked_reason not reason.
        """
        field_re = re.compile(r"^\|\s*([a-z]{1,3})\s*\|")
        violations = []

        for f in SCHEMA_DIR.rglob("*.md"):
            if f.name == "README.md":
                continue
            text = _strip_fences(f.read_text(encoding="utf-8"))
            for i, line in enumerate(text.splitlines(), 1):
                m = field_re.match(line)
                if m and m.group(1) not in self.ALLOWED_SHORT:
                    violations.append(
                        f"{f.relative_to(DEVPACE_ROOT)}:{i}: "
                        f"field '{m.group(1)}' in: {line.strip()[:100]}"
                    )

        assert not violations, (
            f"Schema has abbreviated field names ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nACTION: Use self-explanatory names "
            "(e.g., 'acceptance_criteria' not 'ac'). "
            "If the name is universally understood, add it to ALLOWED_SHORT in this test."
        )
