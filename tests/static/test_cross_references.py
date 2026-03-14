"""TC-CR: Cross-reference integrity between product-layer files."""
import re
import pytest
from tests.conftest import DEVPACE_ROOT, PRODUCT_DIRS, SKILL_NAMES, product_md_files

LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
FENCE_RE = re.compile(r'```[^\n]*\n.*?```', re.DOTALL)
INLINE_CODE_RE = re.compile(r'`[^`]+`')


def _strip_code(content: str) -> str:
    """Remove fenced and inline code blocks so example links are not checked."""
    content = FENCE_RE.sub('', content)
    content = INLINE_CODE_RE.sub('', content)
    return content


@pytest.mark.static
class TestCrossReferences:
    def test_tc_cr_01_internal_links_valid(self):
        """TC-CR-01: Markdown internal links point to existing files."""
        broken = []
        for f in product_md_files():
            content = f.read_text(encoding="utf-8")
            # Strip code blocks — example links should not be validated
            content = _strip_code(content)
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
        for f in product_md_files():
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

    def test_tc_cr_09_value_tree_5_layer_entities(self):
        """TC-CR-09: project-format.md value tree covers 5-layer entities (OBJ→Epic→BR→PF→CR)."""
        pf = DEVPACE_ROOT / "knowledge" / "_schema" / "project-format.md"
        content = pf.read_text(encoding="utf-8")
        for entity in ["OBJ", "EPIC", "BR-", "PF-", "CR-"]:
            assert entity in content, \
                f"project-format.md value tree missing entity layer: {entity}"
        # Check that Epic link format is documented
        assert "epics/EPIC" in content, \
            "project-format.md missing Epic link format documentation"
        # Check that BR overflow format is documented
        assert "requirements/BR" in content, \
            "project-format.md missing BR overflow format documentation"

    def test_tc_cr_10_epic_schema_refs_valid(self):
        """TC-CR-10: epic-format.md references to project.md and BR are consistent."""
        epic = DEVPACE_ROOT / "knowledge" / "_schema" / "epic-format.md"
        content = epic.read_text(encoding="utf-8")
        assert "OBJ" in content, "epic-format.md missing OBJ reference"
        assert "BR-" in content or "BR" in content, "epic-format.md missing BR reference"
        assert "project.md" in content, "epic-format.md missing project.md reference"

    def test_tc_cr_11_br_schema_refs_valid(self):
        """TC-CR-11: br-format.md references to Epic and PF are consistent."""
        br = DEVPACE_ROOT / "knowledge" / "_schema" / "br-format.md"
        content = br.read_text(encoding="utf-8")
        assert "EPIC" in content or "Epic" in content, "br-format.md missing Epic reference"
        assert "PF-" in content or "PF" in content, "br-format.md missing PF reference"
        assert "project.md" in content, "br-format.md missing project.md reference"

    def test_tc_cr_12_no_orphan_procedures(self):
        """TC-CR-12: Every procedures file is reachable from SKILL.md or sibling procedures.

        TC-CR-03 checks forward (SKILL.md refs → file exists).
        This checks reverse (file exists → is referenced somewhere).
        Handles abbreviated references (e.g. "status.md" for "release-procedures-status.md")
        when SKILL.md declares a prefix convention.
        """
        proc_pattern = re.compile(r"[a-z]+-procedures?[-\w]*\.md")
        orphans = []
        for name in SKILL_NAMES:
            skill_dir = DEVPACE_ROOT / "skills" / name
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            # Collect all text from SKILL.md + all procedures
            all_text = ""
            for md_file in [skill_md] + list(skill_dir.glob("*-procedures*.md")):
                all_text += md_file.read_text(encoding="utf-8") + "\n"
            full_refs = set(proc_pattern.findall(all_text))
            # Also collect short .md refs for prefix-abbreviated routing tables
            short_refs = set(re.findall(r"(?<!\w)([\w-]+\.md)", all_text))
            # Check each procedure file on disk is referenced (full or short name)
            for proc_file in skill_dir.glob("*-procedures*.md"):
                # Match by full name or by suffix after the common prefix
                # e.g. "release-procedures-status.md" → also check "status.md"
                short_name = re.sub(r"^[a-z]+-procedures-", "", proc_file.name)
                if proc_file.name not in full_refs and short_name not in short_refs:
                    orphans.append(f"{name}/{proc_file.name}")
        assert not orphans, (
            f"Orphan procedure files (not referenced by SKILL.md or siblings):\n"
            + "\n".join(f"  - {o}" for o in orphans)
        )

    def test_tc_cr_13_pace_dev_cr_state_coverage(self):
        """TC-CR-13: pace-dev routing table covers all core CR states."""
        skill_md = DEVPACE_ROOT / "skills" / "pace-dev" / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        # Extract the routing section (between ## 执行路由 and ## 流程)
        route_match = re.search(
            r"## 执行路由\s*\n(.*?)(?=\n## )",
            content, re.DOTALL,
        )
        assert route_match, "pace-dev SKILL.md missing '## 执行路由' section"
        route_text = route_match.group(1)
        required_states = ["created", "developing", "in_review", "merged"]
        missing = [s for s in required_states if s not in route_text]
        assert not missing, (
            f"pace-dev routing table missing CR states: {missing}"
        )

    def test_tc_cr_14_pace_change_subcmd_procedures(self):
        """TC-CR-14: pace-change routing table subcmds have matching procedure files."""
        skill_md = DEVPACE_ROOT / "skills" / "pace-change" / "SKILL.md"
        skill_dir = DEVPACE_ROOT / "skills" / "pace-change"
        content = skill_md.read_text(encoding="utf-8")
        # Extract routing table rows: | subcmd | files |
        route_match = re.search(
            r"## 执行路由表\s*\n(.*?)(?=\n## )",
            content, re.DOTALL,
        )
        assert route_match, "pace-change SKILL.md missing '## 执行路由表' section"
        route_text = route_match.group(1)
        # Extract all procedure filenames referenced in the table
        proc_refs = set(re.findall(r"(change-procedures-[\w-]+\.md)", route_text))
        assert len(proc_refs) >= 5, (
            f"pace-change routing table references too few procedures: {proc_refs}"
        )
        missing = [p for p in proc_refs if not (skill_dir / p).exists()]
        assert not missing, (
            f"pace-change routing table references missing files: {missing}"
        )
