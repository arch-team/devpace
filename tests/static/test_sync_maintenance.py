"""TC-SM: Cross-file sync maintenance checks.

Detects drift between known cross-file synchronization points:
- Command table in devpace-rules.md vs actual skill directories
- accept capability keywords in pace-test/SKILL.md vs devpace-rules.md
- Schema mapping table in devpace-rules.md vs _schema/ directory
"""
import re

import pytest

from tests.conftest import DEVPACE_ROOT, SKILL_NAMES, SCHEMA_FILES

RULES_FILE = DEVPACE_ROOT / "rules" / "devpace-rules.md"
PACE_TEST_SKILL = DEVPACE_ROOT / "skills" / "pace-test" / "SKILL.md"
SCHEMA_DIR = DEVPACE_ROOT / "knowledge" / "_schema"


def _read_text(path):
    """Read file content as UTF-8 text."""
    return path.read_text(encoding="utf-8")


@pytest.mark.static
class TestSyncMaintenance:
    """Cross-file synchronization drift detection."""

    def test_tc_sm_01_command_table_sync(self):
        """TC-SM-01: section 0 command table matches skill directories.

        The '### 命令分层' table in devpace-rules.md lists all skills
        organised by tier.  Every listed name must exist as a skill
        directory, and every skill directory must appear in the table.
        """
        rules_text = _read_text(RULES_FILE)

        # Locate the command table section (### 命令分层)
        section_match = re.search(
            r"### 命令分层\s*\n(.*?)(?=\n### |\n## |\Z)",
            rules_text,
            re.DOTALL,
        )
        assert section_match, "Could not find '### 命令分层' section in devpace-rules.md"

        section_text = section_match.group(1)

        # Extract all pace-xxx names from table rows.
        # Patterns include: /pace-xxx, pace-xxx (with or without leading /)
        names_in_table = set(re.findall(r"/?(?:pace-[a-z]+)", section_text))
        # Normalise: strip leading slash
        names_in_table = {n.lstrip("/") for n in names_in_table}

        skill_names_set = set(SKILL_NAMES)

        missing_from_table = skill_names_set - names_in_table
        extra_in_table = names_in_table - skill_names_set

        assert not missing_from_table, (
            f"Skills present in skills/ but missing from command table: {sorted(missing_from_table)}"
        )
        assert not extra_in_table, (
            f"Names in command table but no matching skill directory: {sorted(extra_in_table)}"
        )

    def test_tc_sm_02_accept_capabilities_sync(self):
        """TC-SM-02: accept capability keywords consistent across files.

        pace-test/SKILL.md defines 4 fine-grained capabilities for
        'accept'.  devpace-rules.md section 15 teaching table echoes
        these same concepts.  Verify both files mention the same
        core keywords so they stay in sync.
        """
        skill_text = _read_text(PACE_TEST_SKILL)
        rules_text = _read_text(RULES_FILE)

        # Extract the accept section from SKILL.md (between ### accept
        # and the next ### or ## heading)
        accept_section_match = re.search(
            r"### accept.*?\n(.*?)(?=\n###|\n##|\Z)",
            skill_text,
            re.DOTALL,
        )
        assert accept_section_match, (
            "Could not find '### accept' section in pace-test/SKILL.md"
        )
        accept_skill_text = accept_section_match.group(1)

        # Locate section 15 teaching table, then find the accept row.
        # The accept row has `accept` in the last (标记值) column.
        section15_match = re.search(
            r"## §15 渐进教学\s*\n(.*?)(?=\n## |\Z)",
            rules_text,
            re.DOTALL,
        )
        assert section15_match, (
            "Could not find '## §15 渐进教学' section in devpace-rules.md"
        )
        section15_text = section15_match.group(1)

        # Match the table row whose last column (标记值) contains `accept`.
        # Row format: | 行为 | 触发时机 | 教学内容 | `accept` |
        accept_row_match = re.search(
            r"\|([^|]+\|[^|]+\|[^|]+)\|\s*`accept`\s*\|",
            section15_text,
        )
        assert accept_row_match, (
            "Could not find accept teaching row (标记值=accept) "
            "in devpace-rules.md section 15 teaching table"
        )
        # The matched group contains the first 3 columns; the teaching
        # content is in column 3.  We check against the whole row to
        # be resilient to column reordering.
        accept_rules_text = accept_row_match.group(1)

        # The 4 core concepts that must appear in BOTH locations.
        # Each concept is defined by a list of alternative keywords
        # (at least one must appear in each file).  This handles
        # minor wording differences (e.g. "预言" vs "断言") while
        # still detecting real drift where a concept is dropped.
        concept_checks = [
            (["逐条"], "line-by-line acceptance criteria with evidence"),
            (["三级判定"], "three-level verdict"),
            (["预言", "断言"], "test oracle / assertion substance review"),
            (["降级"], "weak coverage auto-downgrade"),
        ]

        for keywords, description in concept_checks:
            skill_hit = any(kw in accept_skill_text for kw in keywords)
            rules_hit = any(kw in accept_rules_text for kw in keywords)
            assert skill_hit, (
                f"Concept '{description}' (keywords: {keywords}) missing "
                f"from pace-test/SKILL.md accept section"
            )
            assert rules_hit, (
                f"Concept '{description}' (keywords: {keywords}) missing "
                f"from devpace-rules.md section 15 accept teaching row"
            )

    def test_tc_sm_03_schema_mapping_completeness(self):
        """TC-SM-03: section 0 schema mapping matches _schema/ directory.

        The '### Schema 映射' table in devpace-rules.md references
        schema names.  Every referenced schema file must exist in
        knowledge/_schema/, and every file in that directory must be
        referenced in the mapping table.
        """
        rules_text = _read_text(RULES_FILE)

        # Locate the schema mapping section
        section_match = re.search(
            r"### Schema 映射\s*\n(.*?)(?=\n### |\n## |\Z)",
            rules_text,
            re.DOTALL,
        )
        assert section_match, (
            "Could not find '### Schema 映射' section in devpace-rules.md"
        )

        section_text = section_match.group(1)

        # Extract schema names from the "Schema 文件" column.
        # Table rows look like: | ... | state-format | ... |
        # or: | ... | cr-format + cr-reference | ... |
        # We extract all xxx-format / xxx-reference patterns from
        # the second column of each table row.
        table_rows = re.findall(r"\|[^|]+\|([^|]+)\|[^|]+\|", section_text)

        schema_names_in_table = set()
        for cell in table_rows:
            # Skip header rows (containing "Schema" or dashes)
            if "Schema" in cell or re.match(r"\s*-+\s*$", cell.strip()):
                continue
            # Extract individual schema names: word-word patterns
            # e.g. "cr-format + cr-reference" -> ["cr-format", "cr-reference"]
            names = re.findall(r"([a-z]+-[a-z]+(?:-[a-z]+)?)", cell)
            schema_names_in_table.update(names)

        # Add .md suffix to compare with actual files
        schema_files_in_table = {f"{name}.md" for name in schema_names_in_table}

        actual_schema_files = set(SCHEMA_FILES)

        missing_from_table = actual_schema_files - schema_files_in_table
        extra_in_table = schema_files_in_table - actual_schema_files

        assert not missing_from_table, (
            f"Schema files in _schema/ but not referenced in mapping table: "
            f"{sorted(missing_from_table)}"
        )
        assert not extra_in_table, (
            f"Schema names in mapping table but no file in _schema/: "
            f"{sorted(extra_in_table)}"
        )
