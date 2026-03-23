"""TC-CS: Verify conftest.py constants stay in sync with filesystem."""
import pytest
from tests.conftest import (
    DEVPACE_ROOT,
    SKILL_NAMES,
    TEMPLATE_FILES,
    SCHEMA_FILES,
)


@pytest.mark.static
class TestConftestSync:
    def test_tc_cs_01_skill_names_match_filesystem(self):
        """TC-CS-01: SKILL_NAMES matches actual skills/ subdirectories."""
        skills_dir = DEVPACE_ROOT / "skills"
        actual_skills = sorted(
            d.name
            for d in skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        )
        expected_skills = sorted(SKILL_NAMES)
        assert actual_skills == expected_skills, (
            f"SKILL_NAMES out of sync with filesystem.\n"
            f"  In filesystem but not in SKILL_NAMES: {set(actual_skills) - set(expected_skills)}\n"
            f"  In SKILL_NAMES but not in filesystem: {set(expected_skills) - set(actual_skills)}"
        )

    def test_tc_cs_02_template_files_match_filesystem(self):
        """TC-CS-02: TEMPLATE_FILES matches actual templates/ directory."""
        template_dir = DEVPACE_ROOT / "skills" / "pace-init" / "templates"
        actual_templates = sorted(
            f.name for f in template_dir.glob("*.md") if f.is_file()
        )
        expected_templates = sorted(TEMPLATE_FILES)
        assert actual_templates == expected_templates, (
            f"TEMPLATE_FILES out of sync with filesystem.\n"
            f"  In filesystem but not in TEMPLATE_FILES: {set(actual_templates) - set(expected_templates)}\n"
            f"  In TEMPLATE_FILES but not in filesystem: {set(expected_templates) - set(actual_templates)}"
        )

    def test_tc_cs_03_schema_files_match_filesystem(self):
        """TC-CS-03: SCHEMA_FILES matches actual _schema/ directory."""
        schema_dir = DEVPACE_ROOT / "knowledge" / "_schema"
        actual_schemas = sorted(
            str(f.relative_to(schema_dir))
            for f in schema_dir.rglob("*.md")
            if f.is_file() and f.name != "README.md"
        )
        expected_schemas = sorted(SCHEMA_FILES)
        assert actual_schemas == expected_schemas, (
            f"SCHEMA_FILES out of sync with filesystem.\n"
            f"  In filesystem but not in SCHEMA_FILES: {set(actual_schemas) - set(expected_schemas)}\n"
            f"  In SCHEMA_FILES but not in filesystem: {set(expected_schemas) - set(actual_schemas)}"
        )
