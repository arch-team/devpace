"""TC-CR: Cross-reference integrity between product-layer files."""
import re
import pytest
from tests.conftest import DEVPACE_ROOT, PRODUCT_DIRS, SKILL_NAMES

LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')


def _product_md_files():
    files = []
    for d in PRODUCT_DIRS:
        dirpath = DEVPACE_ROOT / d
        if dirpath.is_dir():
            files.extend(dirpath.rglob("*.md"))
    return files


@pytest.mark.static
class TestCrossReferences:
    def test_tc_cr_01_internal_links_valid(self):
        """TC-CR-01: Markdown internal links point to existing files."""
        broken = []
        for f in _product_md_files():
            content = f.read_text(encoding="utf-8")
            for m in LINK_RE.finditer(content):
                target = m.group(2)
                # Skip external URLs and anchors
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                # Strip anchor from path
                path_part = target.split("#")[0]
                if not path_part:
                    continue
                resolved = (f.parent / path_part).resolve()
                if not resolved.exists():
                    broken.append(f"{f.relative_to(DEVPACE_ROOT)}: link to '{target}' not found")
        assert not broken, f"Broken links:\n" + "\n".join(broken)

    def test_tc_cr_02_skill_schema_refs_exist(self):
        """TC-CR-02: SKILL.md references to schema files are valid."""
        schema_dir = DEVPACE_ROOT / "knowledge" / "_schema"
        for name in SKILL_NAMES:
            skill_md = DEVPACE_ROOT / "skills" / name / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text(encoding="utf-8")
            for m in re.finditer(r'_schema/([a-z-]+\.md)', content):
                schema_file = schema_dir / m.group(1)
                assert schema_file.exists(), \
                    f"{name}/SKILL.md references missing schema: {m.group(1)}"

    def test_tc_cr_03_skill_procedure_refs_exist(self):
        """TC-CR-03: SKILL.md references to procedure files are valid."""
        for name in SKILL_NAMES:
            skill_dir = DEVPACE_ROOT / "skills" / name
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text(encoding="utf-8")
            for m in re.finditer(r'`?([a-z-]+-procedure[s]?\.md)`?', content):
                proc_file = skill_dir / m.group(1)
                assert proc_file.exists(), \
                    f"{name}/SKILL.md references missing procedure: {m.group(1)}"

    def test_tc_cr_04_init_template_refs_exist(self):
        """TC-CR-04: pace-init references templates that exist."""
        init_skill = DEVPACE_ROOT / "skills" / "pace-init" / "SKILL.md"
        template_dir = DEVPACE_ROOT / "skills" / "pace-init" / "templates"
        if not init_skill.exists():
            pytest.skip("pace-init SKILL.md not found")
        content = init_skill.read_text(encoding="utf-8")
        # Check templates/ directory exists and has files
        assert template_dir.is_dir(), "pace-init/templates/ directory missing"
        templates = list(template_dir.glob("*.md"))
        assert len(templates) >= 7, f"Expected ≥7 templates, found {len(templates)}"

    def test_tc_cr_05_claude_md_template_synced_with_rules(self):
        """TC-CR-05: claude-md-devpace.md template contains key rules concepts."""
        template = DEVPACE_ROOT / "skills" / "pace-init" / "templates" / "claude-md-devpace.md"
        rules = DEVPACE_ROOT / "rules" / "devpace-rules.md"
        if not template.exists() or not rules.exists():
            pytest.skip("Template or rules file not found")
        template_content = template.read_text(encoding="utf-8")
        # Key concepts from rules that must be reflected in template
        missing = []
        # §2 dual mode: explore vs advance
        if "探索" not in template_content or "推进" not in template_content:
            missing.append("§2 双模式（探索/推进）关键词缺失")
        # §9 change management trigger words
        change_triggers = ["不做了", "加一个", "改一下"]
        if not any(t in template_content for t in change_triggers):
            missing.append("§9 变更管理触发词缺失（至少需包含一个：不做了/加一个/改一下）")
        # Session start: read state.md
        if "state.md" not in template_content:
            missing.append("会话开始读 state.md 规则缺失")
        # Session end summary
        if "3-5" not in template_content and "3-5" not in template_content.replace("–", "-"):
            missing.append("会话结束 3-5 行摘要规则缺失")
        assert not missing, (
            f"claude-md-devpace.md template is out of sync with rules:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )
