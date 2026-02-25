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

    def test_tc_cr_06_rules_section_refs_valid(self):
        """TC-CR-06: §N cross-references within rules file point to existing sections."""
        rules = DEVPACE_ROOT / "rules" / "devpace-rules.md"
        content = rules.read_text(encoding="utf-8")

        # Collect all ## §N headings
        section_nums = set()
        for m in re.finditer(r'^## §(\d+)\b', content, re.MULTILINE):
            section_nums.add(m.group(1))

        # Find §N references that are NOT section headings themselves
        broken = []
        for m in re.finditer(r'(?<!^## )§(\d+)', content, re.MULTILINE):
            ref_num = m.group(1)
            if ref_num not in section_nums:
                # Get context line for debugging
                line_start = content.rfind('\n', 0, m.start()) + 1
                line_end = content.find('\n', m.end())
                line = content[line_start:line_end].strip()
                broken.append(f"§{ref_num} referenced but no ## §{ref_num} heading: '{line[:80]}'")

        assert not broken, f"Dangling §N references in rules:\n" + "\n".join(broken)

    def test_tc_cr_07_detail_refs_exist(self):
        """TC-CR-07: '详见' backtick references point to existing files."""
        broken = []
        ref_pattern = re.compile(r'(?:详见|见)\s+`([a-zA-Z0-9_/.-]+\.md)`')
        for f in _product_md_files():
            content = f.read_text(encoding="utf-8")
            for m in ref_pattern.finditer(content):
                ref_path = m.group(1)
                # Try resolving relative to file, then to DEVPACE_ROOT
                resolved_local = (f.parent / ref_path).resolve()
                resolved_root = (DEVPACE_ROOT / ref_path).resolve()
                if not resolved_local.exists() and not resolved_root.exists():
                    broken.append(
                        f"{f.relative_to(DEVPACE_ROOT)}: '详见 `{ref_path}`' file not found"
                    )

        assert not broken, f"Broken '详见' references:\n" + "\n".join(broken)

    def test_tc_cr_08_rules_refs_have_path(self):
        """TC-CR-08: Rules file '详见' refs must include path prefix (no bare filenames)."""
        bare_refs = []
        ref_pattern = re.compile(r'(?:详见|见)\s+`([^`]+\.md)`')
        rules_dir = DEVPACE_ROOT / "rules"
        for f in rules_dir.rglob("*.md"):
            content = f.read_text(encoding="utf-8")
            for m in ref_pattern.finditer(content):
                ref_path = m.group(1)
                if "/" not in ref_path:
                    bare_refs.append(
                        f"{f.relative_to(DEVPACE_ROOT)}: bare ref `{ref_path}` (must include path)"
                    )
        assert not bare_refs, f"Rules bare filename refs (need path prefix):\n" + "\n".join(bare_refs)

    def test_tc_cr_05_claude_md_template_synced_with_rules(self):
        """TC-CR-05: claude-md-devpace.md template contains key content or delegates to rules."""
        template = DEVPACE_ROOT / "skills" / "pace-init" / "templates" / "claude-md-devpace.md"
        rules = DEVPACE_ROOT / "rules" / "devpace-rules.md"
        if not template.exists() or not rules.exists():
            pytest.skip("Template or rules file not found")
        template_content = template.read_text(encoding="utf-8")
        missing = []
        # Template must either contain key concepts directly OR delegate to rules
        delegates_to_rules = "devpace-rules.md" in template_content
        if not delegates_to_rules:
            # §2 dual mode: explore vs advance
            if "探索" not in template_content or "推进" not in template_content:
                missing.append("§2 双模式（探索/推进）关键词缺失")
            # §9 change management trigger words
            change_triggers = ["不做了", "加一个", "改一下"]
            if not any(t in template_content for t in change_triggers):
                missing.append("§9 变更管理触发词缺失（至少需包含一个：不做了/加一个/改一下）")
            # Session end summary
            if "3-5" not in template_content and "3-5" not in template_content.replace("–", "-"):
                missing.append("会话结束 3-5 行摘要规则缺失")
        # state.md reference always required (either inline or in file table)
        if "state.md" not in template_content:
            missing.append("会话开始读 state.md 规则缺失")
        # .devpace/ reference always required
        if ".devpace/" not in template_content:
            missing.append(".devpace/ 文件参考缺失")
        assert not missing, (
            f"claude-md-devpace.md template is out of sync with rules:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )
