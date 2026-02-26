"""TC-TP: Template placeholder validation."""
import re
import pytest
from tests.conftest import DEVPACE_ROOT, TEMPLATE_FILES, PRODUCT_DIRS

PLACEHOLDER_RE = re.compile(r'\{\{([^}]+)\}\}')
UPPER_SNAKE_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
UNCLOSED_OPEN = re.compile(r'\{\{(?!.*\}\})')
UNCLOSED_CLOSE = re.compile(r'(?<!\{\{)\}\}')

TEMPLATE_DIR = DEVPACE_ROOT / "skills" / "pace-init" / "templates"

KNOWN_PLACEHOLDERS = {
    "OBJECTIVE", "MOS_SUMMARY", "ITERATION_ID", "ITERATION_GOAL",
    "TOTAL_PF", "NEXT_ACTION", "PROJECT_NAME", "PROJECT_DESCRIPTION",
    "OBJECTIVE_ID", "OBJECTIVE_DESCRIPTION", "MOS_1", "MOS_2",
    "STEP_1", "BR_1", "BR_2", "PF_1", "PF_2", "PF_3",
    "TITLE", "CR_ID", "PF_TITLE", "PF_ID", "BR_TITLE", "BR_ID",
    "APPLICATION", "BRANCH_NAME", "USER_REQUEST", "DATE", "NOTE",
    "GATE_NAME_1", "GATE_NAME_2", "DESCRIPTION", "CHECK_COMMAND",
    "GATE_NAME_CMD_1", "GATE_NAME_CMD_2", "GATE_NAME_NL_1", "GATE_NAME_NL_2",
    "DESCRIPTION_CMD", "DESCRIPTION_NL", "NL_RULE",
    "START_DATE", "END_DATE", "PLANNED_PF_COUNT",
    "PROJECT_POSITIONING", "OBJECTIVES_AND_MOS",
    "CR_TYPE", "CR_SEVERITY", "RELEASE_ID", "ROOT_CAUSE_SECTION",
    "VERSION", "TARGET_ENV",
    "ENV_NAME", "ENV_PURPOSE", "CICD_TOOL", "CICD_TRIGGER",
    "TECH_STACK", "CODING_CONVENTIONS", "PROJECT_CONVENTIONS",
    "VERSION_FILE", "VERSION_FORMAT", "VERSION_FIELD",
}

@pytest.mark.static
class TestTemplatePlaceholders:
    def test_tc_tp_01_upper_snake_case(self):
        """TC-TP-01: All placeholders use UPPER_SNAKE_CASE."""
        violations = []
        for name in TEMPLATE_FILES:
            path = TEMPLATE_DIR / name
            if not path.exists():
                continue
            for m in PLACEHOLDER_RE.finditer(path.read_text(encoding="utf-8")):
                ph = m.group(1).strip()
                if not UPPER_SNAKE_RE.match(ph):
                    violations.append(f"{name}: {{{{{ph}}}}}")
        assert not violations, f"Non-UPPER_SNAKE_CASE placeholders:\n" + "\n".join(violations)

    def test_tc_tp_02_no_unclosed_braces(self):
        """TC-TP-02: No unclosed {{ or }}."""
        violations = []
        for name in TEMPLATE_FILES:
            path = TEMPLATE_DIR / name
            if not path.exists():
                continue
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                opens = line.count("{{")
                closes = line.count("}}")
                if opens != closes:
                    violations.append(f"{name}:{i}: {{ count={opens}, }} count={closes}")
        assert not violations, f"Unclosed braces:\n" + "\n".join(violations)

    def test_tc_tp_03_known_placeholders(self):
        """TC-TP-03: All placeholders are in the known set (detect new ones needing test update)."""
        unknown = []
        for name in TEMPLATE_FILES:
            path = TEMPLATE_DIR / name
            if not path.exists():
                continue
            for m in PLACEHOLDER_RE.finditer(path.read_text(encoding="utf-8")):
                ph = m.group(1).strip()
                if ph not in KNOWN_PLACEHOLDERS:
                    unknown.append(f"{name}: {{{{{ph}}}}}")
        assert not unknown, (
            f"Unknown placeholders (add to KNOWN_PLACEHOLDERS in test):\n" + "\n".join(unknown)
        )

    def test_tc_tp_04_no_placeholders_in_non_template_product(self):
        """TC-TP-04: Non-template product files have no {{ }} placeholders."""
        violations = []
        for d in PRODUCT_DIRS:
            dirpath = DEVPACE_ROOT / d
            if not dirpath.is_dir():
                continue
            for f in dirpath.rglob("*.md"):
                # Skip template directory, SKILL.md, and procedure files (which document placeholder syntax)
                if "templates" in f.parts or f.name == "SKILL.md" or "procedures" in f.name:
                    continue
                content = f.read_text(encoding="utf-8")
                matches = PLACEHOLDER_RE.findall(content)
                if matches:
                    violations.append(f"{f.relative_to(DEVPACE_ROOT)}: {matches}")
        assert not violations, f"Placeholders in non-template product files:\n" + "\n".join(violations)
