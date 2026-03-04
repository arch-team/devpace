"""TC-INIT: pace-init Skill-specific static validation."""
import re

import pytest
import yaml
from tests.conftest import DEVPACE_ROOT, LEGAL_TOOL_NAMES

SKILL_PATH = DEVPACE_ROOT / "skills" / "pace-init" / "SKILL.md"
TEMPLATES_DIR = DEVPACE_ROOT / "skills" / "pace-init" / "templates"


def _parse_frontmatter(path):
    """Extract YAML frontmatter from a markdown file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end])


@pytest.mark.static
class TestPaceInit:
    def test_tc_init_01_edit_in_allowed_tools(self):
        """TC-INIT-01: Edit tool is present in pace-init allowed-tools."""
        fm = _parse_frontmatter(SKILL_PATH)
        assert fm and "allowed-tools" in fm
        tools = [t.strip() for t in fm["allowed-tools"].split(",")]
        assert "Edit" in tools, (
            f"pace-init allowed-tools missing Edit; got: {tools}"
        )

    def test_tc_init_02_hook_matcher_subset_of_allowed_tools(self):
        """TC-INIT-02: Hook matcher tool_name entries are a subset of allowed-tools."""
        fm = _parse_frontmatter(SKILL_PATH)
        assert fm and "hooks" in fm and "allowed-tools" in fm
        allowed = {t.strip() for t in fm["allowed-tools"].split(",")}
        matcher_tools = set()
        for _event, entries in fm["hooks"].items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                matcher = entry.get("matcher", {})
                if not isinstance(matcher, dict):
                    continue
                tool_name = matcher.get("tool_name", "")
                for t in tool_name.split("|"):
                    t = t.strip()
                    if t:
                        matcher_tools.add(t)
        assert matcher_tools, "No tool_name matchers found in hooks"
        missing = matcher_tools - allowed
        assert not missing, (
            f"Hook matcher tools {missing} not in allowed-tools {allowed}"
        )

    def test_tc_init_03_hook_guard_covers_write_targets(self):
        """TC-INIT-03: Hook guard prompt mentions all write target directories."""
        fm = _parse_frontmatter(SKILL_PATH)
        assert fm and "hooks" in fm
        # Collect all prompt texts from hooks
        prompts = []
        for _event, entries in fm["hooks"].items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                for hook in entry.get("hooks", []):
                    if isinstance(hook, dict) and "prompt" in hook:
                        prompts.append(hook["prompt"])
        prompt_text = " ".join(prompts)
        # pace-init writes to: .devpace/, CLAUDE.md, .gitignore
        assert ".devpace/" in prompt_text or ".devpace" in prompt_text, (
            "Hook guard prompt does not mention .devpace/"
        )
        assert "CLAUDE.md" in prompt_text, (
            "Hook guard prompt does not mention CLAUDE.md"
        )
        assert ".gitignore" in prompt_text, (
            "Hook guard prompt does not mention .gitignore"
        )

    def test_tc_init_04_state_template_has_version_marker(self):
        """TC-INIT-04: state.md template contains devpace-version marker."""
        state_tpl = TEMPLATES_DIR / "state.md"
        assert state_tpl.exists(), "state.md template not found"
        content = state_tpl.read_text(encoding="utf-8")
        assert "devpace-version" in content, (
            "state.md template missing devpace-version marker"
        )

    def test_tc_init_05_claude_md_template_markers_paired(self):
        """TC-INIT-05: claude-md-devpace.md template has paired start/end markers."""
        tpl = TEMPLATES_DIR / "claude-md-devpace.md"
        assert tpl.exists(), "claude-md-devpace.md template not found"
        content = tpl.read_text(encoding="utf-8")
        start_count = content.count("<!-- devpace-start -->")
        end_count = content.count("<!-- devpace-end -->")
        assert start_count == 1, (
            f"Expected 1 devpace-start marker, found {start_count}"
        )
        assert end_count == 1, (
            f"Expected 1 devpace-end marker, found {end_count}"
        )
        # start must appear before end
        start_pos = content.index("<!-- devpace-start -->")
        end_pos = content.index("<!-- devpace-end -->")
        assert start_pos < end_pos, (
            "devpace-start marker must appear before devpace-end"
        )
