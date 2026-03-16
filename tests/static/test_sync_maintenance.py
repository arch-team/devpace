"""TC-SYN: Cross-file sync maintenance checks.

Detects drift between known cross-file synchronization points:
- Command table in devpace-rules.md vs actual skill directories
- accept capability keywords in pace-test/SKILL.md vs devpace-rules.md
- Schema mapping table in devpace-rules.md vs _schema/ directory
- Feature docs sub-command list vs SKILL.md
"""
import re

import pytest

from tests.conftest import DEVPACE_ROOT, SKILL_NAMES, SCHEMA_FILES, RULES_FILE, SCHEMA_DIR

PACE_TEST_SKILL = DEVPACE_ROOT / "skills" / "pace-test" / "SKILL.md"
FEATURES_DIR = DEVPACE_ROOT / "docs" / "features"
SKILLS_DIR = DEVPACE_ROOT / "skills"


def _read_text(path):
    """Read file content as UTF-8 text."""
    return path.read_text(encoding="utf-8")


@pytest.mark.static
class TestSyncMaintenance:
    """Cross-file synchronization drift detection."""

    def test_tc_syn_01_command_table_sync(self):
        """TC-SYN-01: section 0 command table matches skill directories.

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

    def test_tc_syn_02_accept_capabilities_sync(self):
        """TC-SYN-02: accept capability keywords in SKILL.md + rules reference.

        pace-test/SKILL.md (authority) defines 4 fine-grained capabilities
        for 'accept'.  devpace-rules.md section 15 uses a generalized
        teaching text that references /pace-test instead of enumerating
        capabilities.  Verify:
        1. SKILL.md still contains all 4 core capability concepts
        2. Rules §15 accept row references /pace-test (authority delegation)
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

        # Verify SKILL.md (authority) still has all 4 core concepts.
        concept_checks = [
            (["逐条"], "line-by-line acceptance criteria with evidence"),
            (["三级判定"], "three-level verdict"),
            (["预言", "断言"], "test oracle / assertion substance review"),
            (["降级"], "weak coverage auto-downgrade"),
        ]

        for keywords, description in concept_checks:
            skill_hit = any(kw in accept_skill_text for kw in keywords)
            assert skill_hit, (
                f"Concept '{description}' (keywords: {keywords}) missing "
                f"from pace-test/SKILL.md accept section"
            )

        # Locate section 15 teaching table, then find the accept row.
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
        accept_row_match = re.search(
            r"\|([^|]+\|[^|]+\|[^|]+)\|\s*`accept`\s*\|",
            section15_text,
        )
        assert accept_row_match, (
            "Could not find accept teaching row (标记值=accept) "
            "in devpace-rules.md section 15 teaching table"
        )
        accept_rules_text = accept_row_match.group(1)

        # Rules §15 uses generalized text referencing /pace-test (authority
        # delegation) instead of enumerating specific capabilities.
        assert "/pace-test" in accept_rules_text, (
            "Rules §15 accept teaching row should reference '/pace-test' "
            "(authority delegation) instead of enumerating capabilities"
        )

    def test_tc_syn_03_schema_files_exist(self):
        """TC-SYN-03: all expected schema files exist in _schema/ directory.

        The Schema 映射 table was removed from devpace-rules.md §0
        (OPT-2 token optimization). Schema files are now discovered
        directly from knowledge/_schema/ or specified in Skill procedures.
        This test validates that the expected schema files exist.
        """
        assert SCHEMA_DIR.is_dir(), f"Schema directory not found: {SCHEMA_DIR}"

        actual_files = {
            str(f.relative_to(SCHEMA_DIR))
            for f in SCHEMA_DIR.rglob("*.md")
            if f.is_file() and f.name != "README.md"
        }
        expected_files = set(SCHEMA_FILES)

        missing = expected_files - actual_files
        assert not missing, (
            f"Expected schema files missing from _schema/: {sorted(missing)}"
        )

    def test_tc_syn_04_feature_docs_subcommand_sync(self):
        """TC-SYN-04: feature docs sub-command list matches SKILL.md.

        For each skill that has a docs/features/<name>.md, verify that
        the sub-commands listed in the feature doc match those in SKILL.md.
        """
        if not FEATURES_DIR.is_dir():
            pytest.skip("docs/features/ directory does not exist yet")

        # Find all EN feature docs (exclude _zh translations)
        feature_docs = [
            f for f in FEATURES_DIR.iterdir()
            if f.suffix == ".md"
            and f.stem.startswith("pace-")
            and not f.stem.endswith("_zh")
        ]

        if not feature_docs:
            pytest.skip("No feature docs found in docs/features/")

        errors = []
        for doc_path in feature_docs:
            skill_name = doc_path.stem  # e.g., "pace-sync"
            skill_md = SKILLS_DIR / skill_name / "SKILL.md"

            if not skill_md.exists():
                errors.append(
                    f"Feature doc {doc_path.name} has no matching "
                    f"skills/{skill_name}/SKILL.md"
                )
                continue

            # Extract sub-commands from SKILL.md (table rows in ### 子命令)
            skill_text = skill_md.read_text(encoding="utf-8")
            subcmd_section = re.search(
                r"### 子命令\s*\n(.*?)(?=\n### |\n## |\Z)",
                skill_text,
                re.DOTALL,
            )
            if not subcmd_section:
                continue  # No sub-command table, skip

            # Extract sub-command names from table rows: | name | ...
            skill_subcmds = set(
                re.findall(r"^\|\s*(\w+)\s*\|", subcmd_section.group(1), re.MULTILINE)
            )
            # Remove table header words
            skill_subcmds -= {"子命令", "---"}

            # Extract sub-commands from feature doc (### `name` headings
            # under ## Command Reference)
            doc_text = doc_path.read_text(encoding="utf-8")
            cmd_ref_section = re.search(
                r"## Command Reference\s*\n(.*?)(?=\n## [^#]|\Z)",
                doc_text,
                re.DOTALL,
            )
            if not cmd_ref_section:
                # Try Chinese heading
                cmd_ref_section = re.search(
                    r"## 命令参考\s*\n(.*?)(?=\n## [^#]|\Z)",
                    doc_text,
                    re.DOTALL,
                )
            if not cmd_ref_section:
                continue

            doc_subcmds = set(
                re.findall(r"### `(\w+)`", cmd_ref_section.group(1))
            )

            # Filter to only MVP sub-commands (marked ✅ in SKILL.md)
            mvp_lines = re.findall(
                r"^\|\s*(\w+)\s*\|.*?\|\s*✅\s*\|",
                subcmd_section.group(1),
                re.MULTILINE,
            )
            skill_mvp_subcmds = set(mvp_lines) if mvp_lines else skill_subcmds

            missing_in_doc = skill_mvp_subcmds - doc_subcmds
            extra_in_doc = doc_subcmds - skill_subcmds

            if missing_in_doc:
                errors.append(
                    f"{doc_path.name}: MVP sub-commands in SKILL.md but "
                    f"missing from feature doc: {sorted(missing_in_doc)}"
                )
            if extra_in_doc:
                errors.append(
                    f"{doc_path.name}: sub-commands in feature doc but "
                    f"not in SKILL.md: {sorted(extra_in_doc)}"
                )

        assert not errors, (
            "Feature doc ↔ SKILL.md sub-command drift detected:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    def test_tc_syn_06_feature_docs_bilingual_completeness(self):
        """TC-SYN-06: every EN feature doc has a corresponding _zh.md translation.

        CLAUDE.md sync point: SKILL.md → docs/features/<name>.md → <name>_zh.md
        """
        if not FEATURES_DIR.is_dir():
            pytest.skip("docs/features/ directory does not exist yet")

        en_docs = [
            f for f in FEATURES_DIR.iterdir()
            if f.suffix == ".md"
            and f.stem.startswith("pace-")
            and not f.stem.endswith("_zh")
        ]

        if not en_docs:
            pytest.skip("No EN feature docs found in docs/features/")

        missing_zh = []
        for doc in en_docs:
            zh_path = doc.with_name(f"{doc.stem}_zh.md")
            if not zh_path.exists():
                missing_zh.append(doc.stem)

        assert not missing_zh, (
            f"EN feature docs missing _zh.md translation: {sorted(missing_zh)}"
        )

    def test_tc_syn_11_signal_priority_consumer_skills_exist(self):
        """TC-SYN-11: Skills referenced as consumers in signal-priority.md exist.

        knowledge/_signals/signal-priority.md contains '→ /pace-xxx' action hints.
        Every referenced Skill must exist in skills/ directory.
        """
        sp_file = DEVPACE_ROOT / "knowledge" / "_signals" / "signal-priority.md"
        if not sp_file.exists():
            pytest.skip("signal-priority.md not found")

        content = sp_file.read_text(encoding="utf-8")
        # Extract /pace-xxx references from action column (→ /pace-xxx ...)
        # Require leading / to avoid matching substrings like "devpace-rules"
        refs = set(re.findall(r"/(pace-[a-z]+)", content))

        missing = [r for r in refs if not (SKILLS_DIR / r).is_dir()]
        assert not missing, (
            f"signal-priority.md references non-existent Skills: {sorted(missing)}"
        )

    def test_tc_syn_12_cr_format_procedure_refs_exist(self):
        """TC-SYN-12: Procedure files referenced in cr-format.md exist on disk.

        knowledge/_schema/entity/cr-format.md contains reverse refs like
        'skills/pace-dev/dev-procedures-intent.md' for context.
        """
        cr_file = DEVPACE_ROOT / "knowledge" / "_schema" / "entity" / "cr-format.md"
        if not cr_file.exists():
            pytest.skip("cr-format.md not found")

        content = cr_file.read_text(encoding="utf-8")
        # Match paths like skills/pace-xxx/xxx-procedures-yyy.md
        refs = re.findall(r"(skills/pace-[a-z-]+/[a-z-]+-procedures?[-\w]*\.md)", content)

        missing = [r for r in refs if not (DEVPACE_ROOT / r).exists()]
        assert not missing, (
            f"cr-format.md references non-existent procedure files: {sorted(missing)}"
        )
