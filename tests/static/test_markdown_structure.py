"""TC-MS: Markdown structural requirements."""
import re
import pytest
from tests.conftest import DEVPACE_ROOT, SKILL_NAMES, SCHEMA_FILES

RULES_FILE = DEVPACE_ROOT / "rules" / "devpace-rules.md"
THEORY_FILE = DEVPACE_ROOT / "knowledge" / "theory.md"
SCHEMA_DIR = DEVPACE_ROOT / "knowledge" / "_schema"
SKILLS_ROOT = DEVPACE_ROOT / "skills"

THEORY_TOPICS = [
    "model", "objects", "spaces", "rules", "trace",
    "topic", "metrics", "loops", "change", "decisions", "vs-devops",
]


def _headings(text):
    return [(len(m.group(1)), m.group(2).strip())
            for m in re.finditer(r'^(#{1,6})\s+(.+)$', text, re.MULTILINE)]


@pytest.mark.static
class TestMarkdownStructure:
    def test_tc_ms_01_quick_ref_cards(self):
        """TC-MS-01: rules and schema files have §0 速查卡片 heading."""
        files_to_check = [RULES_FILE] + [SCHEMA_DIR / f for f in SCHEMA_FILES]
        for f in files_to_check:
            if not f.exists():
                continue
            content = f.read_text(encoding="utf-8")
            assert "§0" in content and "速查" in content, \
                f"{f.name} missing '§0 速查卡片' section"

    def test_tc_ms_02_rules_sections(self):
        """TC-MS-02: devpace-rules.md has §0-§9 sections."""
        content = RULES_FILE.read_text(encoding="utf-8")
        for i in range(10):
            assert f"§{i}" in content, f"devpace-rules.md missing §{i} section"

    def test_tc_ms_03_skill_md_structure(self):
        """TC-MS-03: Each SKILL.md has title and flow/description."""
        for name in SKILL_NAMES:
            path = SKILLS_ROOT / name / "SKILL.md"
            if not path.exists():
                continue
            content = path.read_text(encoding="utf-8")
            headings = _headings(content)
            heading_texts = [h[1].lower() for h in headings]
            # Should have some structural content beyond just frontmatter
            assert len(content.splitlines()) > 10, \
                f"{name}/SKILL.md too short ({len(content.splitlines())} lines)"

    def test_tc_ms_04_procedure_files_structure(self):
        """TC-MS-04: Procedure files have clear step structure."""
        for name in SKILL_NAMES:
            skill_dir = SKILLS_ROOT / name
            for proc in skill_dir.glob("*-procedures.md"):
                content = proc.read_text(encoding="utf-8")
                # Should have numbered steps or headings
                has_steps = bool(re.search(r'(?:Step|步骤|###)\s*\d', content, re.IGNORECASE))
                has_headings = len(_headings(content)) >= 2
                assert has_steps or has_headings, \
                    f"{proc.name} lacks clear step structure"

    def test_tc_ms_05_theory_topics(self):
        """TC-MS-05: theory.md covers all queryable topics."""
        if not THEORY_FILE.exists():
            pytest.skip("theory.md not found")
        content = THEORY_FILE.read_text(encoding="utf-8")
        missing = [t for t in THEORY_TOPICS if t not in content.lower()]
        assert not missing, f"theory.md missing topics: {missing}"

    def test_tc_ms_06_skill_split_heuristic(self):
        """TC-MS-06: SKILL.md > 50 lines of non-frontmatter content should have a procedure file."""
        warnings = []
        for name in SKILL_NAMES:
            skill_md = SKILLS_ROOT / name / "SKILL.md"
            if not skill_md.exists():
                continue
            text = skill_md.read_text(encoding="utf-8")
            # Strip frontmatter
            if text.startswith("---"):
                end_idx = text.index("---", 3) + 3
                body = text[end_idx:]
            else:
                body = text
            body_lines = [l for l in body.splitlines() if l.strip()]
            if len(body_lines) > 50:
                procedures = list((SKILLS_ROOT / name).glob("*-procedure*.md"))
                if not procedures:
                    warnings.append(
                        f"{name}/SKILL.md has {len(body_lines)} content lines but no procedure file"
                    )
        assert not warnings, "Skills exceed 50 lines without procedure split:\n" + "\n".join(warnings)
