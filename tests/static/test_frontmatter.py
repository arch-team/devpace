"""TC-FM: SKILL.md frontmatter validation."""
import pytest
import yaml
from tests.conftest import DEVPACE_ROOT, SKILL_NAMES, LEGAL_SKILL_FIELDS, LEGAL_MODEL_VALUES, LEGAL_TOOL_NAMES, parse_frontmatter

def _skill_md_files():
    skills_root = DEVPACE_ROOT / "skills"
    return [
        (name, skills_root / name / "SKILL.md")
        for name in SKILL_NAMES
    ]

@pytest.mark.static
class TestFrontmatter:
    @pytest.mark.parametrize("name,path", _skill_md_files(), ids=[n for n, _ in _skill_md_files()])
    def test_tc_fm_01_has_frontmatter(self, name, path):
        """TC-FM-01: Each SKILL.md has --- delimited frontmatter."""
        assert path.exists(), f"SKILL.md missing for {name}"
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---"), f"{name}/SKILL.md missing opening ---"
        assert text.index("---", 3) > 3, f"{name}/SKILL.md missing closing ---"

    @pytest.mark.parametrize("name,path", _skill_md_files(), ids=[n for n, _ in _skill_md_files()])
    def test_tc_fm_02_legal_fields_only(self, name, path):
        """TC-FM-02: Frontmatter uses only legal fields."""
        fm = parse_frontmatter(path)
        if fm is None:
            pytest.skip(f"{name} has no frontmatter")
        illegal = set(fm.keys()) - LEGAL_SKILL_FIELDS
        assert not illegal, f"{name} has illegal frontmatter fields: {illegal}"

    @pytest.mark.parametrize("name,path", _skill_md_files(), ids=[n for n, _ in _skill_md_files()])
    def test_tc_fm_03_description_required(self, name, path):
        """TC-FM-03: description field must exist."""
        fm = parse_frontmatter(path)
        assert fm and "description" in fm, f"{name} SKILL.md missing 'description' in frontmatter"

    @pytest.mark.parametrize("name,path", _skill_md_files(), ids=[n for n, _ in _skill_md_files()])
    def test_tc_fm_04_allowed_tools_valid(self, name, path):
        """TC-FM-04: allowed-tools values are recognized tool names."""
        fm = parse_frontmatter(path)
        if fm is None or "allowed-tools" not in fm:
            pytest.skip(f"{name} has no allowed-tools")
        tools = [t.strip() for t in fm["allowed-tools"].split(",")]
        unknown = [t for t in tools if t not in LEGAL_TOOL_NAMES]
        assert not unknown, f"{name} has unknown tools: {unknown}"

    @pytest.mark.parametrize("name,path", _skill_md_files(), ids=[n for n, _ in _skill_md_files()])
    def test_tc_fm_05_model_valid(self, name, path):
        """TC-FM-05: model field (if present) is sonnet/opus/haiku."""
        fm = parse_frontmatter(path)
        if fm is None or "model" not in fm:
            pytest.skip(f"{name} has no model field")
        assert fm["model"] in LEGAL_MODEL_VALUES, f"{name} has invalid model: {fm['model']}"

    @pytest.mark.parametrize("name,path", _skill_md_files(), ids=[n for n, _ in _skill_md_files()])
    def test_tc_fm_06_yaml_parseable(self, name, path):
        """TC-FM-06: Frontmatter YAML can be parsed without error."""
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            pytest.skip(f"{name} has no frontmatter")
        end = text.index("---", 3)
        try:
            yaml.safe_load(text[3:end])
        except yaml.YAMLError as e:
            pytest.fail(f"{name} frontmatter YAML parse error: {e}")

    # ── File-reading skills must declare Read or Glob ────────────────────

    # Keywords that indicate the skill reads files at runtime
    _FILE_READ_INDICATORS = ["读取", "Read(", "knowledge/", ".devpace/", "加载知识库"]

    @pytest.mark.parametrize("name,path", _skill_md_files(), ids=[n for n, _ in _skill_md_files()])
    def test_tc_fm_07_file_reading_skills_have_allowed_tools(self, name, path):
        """TC-FM-07: Skills that read files must declare Read or Glob in allowed-tools."""
        text = path.read_text(encoding="utf-8")
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        reads_files = any(kw in body for kw in self._FILE_READ_INDICATORS)
        if not reads_files:
            pytest.skip(f"{name} does not appear to read files")
        fm = parse_frontmatter(path)
        assert fm and "allowed-tools" in fm, (
            f"{name} reads files but has no allowed-tools declared"
        )
        tools = fm["allowed-tools"]
        assert "Read" in tools or "Glob" in tools, (
            f"{name} reads files but allowed-tools lacks Read or Glob"
        )

    # ── Skills with structured arguments should have argument-hint ────────

    @pytest.mark.parametrize("name,path", _skill_md_files(), ids=[n for n, _ in _skill_md_files()])
    def test_tc_fm_08_argument_hint_present(self, name, path):
        """TC-FM-08 (warning): Skills accepting arguments should have argument-hint."""
        text = path.read_text(encoding="utf-8")
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        has_arguments = "$ARGUMENTS" in body or "$0" in body or "$1" in body
        if not has_arguments:
            pytest.skip(f"{name} does not use $ARGUMENTS")
        fm = parse_frontmatter(path)
        if not fm or "argument-hint" not in fm:
            import warnings
            warnings.warn(
                f"{name} accepts arguments but has no argument-hint in frontmatter",
                UserWarning,
            )

    # ── Hook matcher tools must be in allowed-tools ──────────────────────

    @pytest.mark.parametrize("name,path", _skill_md_files(), ids=[n for n, _ in _skill_md_files()])
    def test_tc_fm_09_hook_matcher_tools_in_allowed_tools(self, name, path):
        """TC-FM-09: Hook matcher tool_name entries must be a subset of allowed-tools."""
        fm = parse_frontmatter(path)
        if fm is None or "hooks" not in fm or "allowed-tools" not in fm:
            pytest.skip(f"{name} has no hooks or no allowed-tools")
        allowed = {t.strip() for t in fm["allowed-tools"].split(",")}
        hooks_cfg = fm["hooks"]
        matcher_tools = set()
        # Walk hook config to extract tool_name from matchers
        for _event, entries in hooks_cfg.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                matcher = entry.get("matcher", {})
                if not isinstance(matcher, dict):
                    continue
                tool_name = matcher.get("tool_name", "")
                if tool_name:
                    # tool_name may be a regex-like "Write|Edit" pattern
                    for t in tool_name.split("|"):
                        t = t.strip()
                        if t:
                            matcher_tools.add(t)
        if not matcher_tools:
            pytest.skip(f"{name} hooks have no tool_name matchers")
        missing = matcher_tools - allowed
        assert not missing, (
            f"{name}: hook matcher references tools {missing} not in allowed-tools {allowed}"
        )
