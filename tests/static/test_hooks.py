"""TC-HK: Hook configuration and script validation."""
import json
import os
import stat

import pytest
import yaml
from tests.conftest import DEVPACE_ROOT, CR_STATES

HOOKS_DIR = DEVPACE_ROOT / "hooks"
HOOKS_JSON = HOOKS_DIR / "hooks.json"

# Valid hook event names (case-sensitive per Claude Code spec)
VALID_HOOK_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "UserPromptSubmit",
    "PreCompact",
    "Stop",
    "SessionStart",
    "SessionEnd",
    "SubagentStart",
    "SubagentStop",
    "TeammateIdle",
    "TaskCompleted",
}

EXPECTED_SCRIPTS_SH = ["session-start.sh", "session-stop.sh", "pre-compact.sh", "session-end.sh"]
EXPECTED_SCRIPTS_MJS = ["pre-tool-use.mjs", "post-cr-update.mjs", "intent-detect.mjs", "subagent-stop.mjs", "pulse-counter.mjs", "post-tool-failure.mjs", "sync-push.mjs", "post-schema-check.mjs"]
SKILL_HOOKS_DIR = HOOKS_DIR / "skill"
EXPECTED_SKILL_SCRIPTS = ["pace-dev-scope-check.mjs", "pace-init-scope-check.mjs", "pace-review-scope-check.mjs"]
EXPECTED_SCRIPTS = EXPECTED_SCRIPTS_SH + EXPECTED_SCRIPTS_MJS


@pytest.mark.static
class TestHooksConfig:
    def test_tc_hk_01_hooks_json_valid(self):
        """TC-HK-01: hooks.json is valid JSON."""
        assert HOOKS_JSON.exists(), "hooks/hooks.json not found"
        content = HOOKS_JSON.read_text(encoding="utf-8")
        data = json.loads(content)  # Raises on invalid JSON
        assert "hooks" in data, "hooks.json missing top-level 'hooks' key"

    def test_tc_hk_02_event_names_case_correct(self):
        """TC-HK-02: Hook event names use correct casing."""
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        for event_name in data["hooks"]:
            assert event_name in VALID_HOOK_EVENTS, (
                f"Invalid hook event name '{event_name}'. "
                f"Valid names (case-sensitive): {sorted(VALID_HOOK_EVENTS)}"
            )


@pytest.mark.static
class TestHooksScripts:
    def test_tc_hk_03_scripts_exist(self):
        """TC-HK-03: All expected hook scripts exist."""
        missing = []
        for script in EXPECTED_SCRIPTS:
            if not (HOOKS_DIR / script).exists():
                missing.append(script)
        assert not missing, f"Missing hook scripts: {missing}"

    def test_tc_hk_04_scripts_executable(self):
        """TC-HK-04: Hook scripts have execute permission."""
        not_executable = []
        for script in EXPECTED_SCRIPTS:
            path = HOOKS_DIR / script
            if path.exists():
                mode = path.stat().st_mode
                if not (mode & stat.S_IXUSR):
                    not_executable.append(script)
        assert not not_executable, (
            f"Scripts lack execute permission: {not_executable}. "
            f"Fix with: chmod +x hooks/<script>"
        )

    def test_tc_hk_05_scripts_have_shebang(self):
        """TC-HK-05: Hook scripts start with shebang line."""
        no_shebang = []
        for script in EXPECTED_SCRIPTS:
            path = HOOKS_DIR / script
            if path.exists():
                first_line = path.read_text(encoding="utf-8").split("\n")[0]
                if not first_line.startswith("#!"):
                    no_shebang.append(script)
        assert not no_shebang, f"Scripts missing shebang: {no_shebang}"

    def test_tc_hk_03b_skill_scripts_exist(self):
        """TC-HK-03b: All expected skill-level hook scripts exist in hooks/skill/."""
        missing = []
        for script in EXPECTED_SKILL_SCRIPTS:
            if not (SKILL_HOOKS_DIR / script).exists():
                missing.append(script)
        assert not missing, f"Missing skill hook scripts: {missing}"

    def test_tc_hk_04b_skill_scripts_executable(self):
        """TC-HK-04b: Skill hook scripts have execute permission."""
        not_executable = []
        for script in EXPECTED_SKILL_SCRIPTS:
            path = SKILL_HOOKS_DIR / script
            if path.exists():
                mode = path.stat().st_mode
                if not (mode & stat.S_IXUSR):
                    not_executable.append(script)
        assert not not_executable, (
            f"Skill scripts lack execute permission: {not_executable}. "
            f"Fix with: chmod +x hooks/skill/<script>"
        )

    def test_tc_hk_05b_skill_scripts_have_shebang(self):
        """TC-HK-05b: Skill hook scripts start with shebang line."""
        no_shebang = []
        for script in EXPECTED_SKILL_SCRIPTS:
            path = SKILL_HOOKS_DIR / script
            if path.exists():
                first_line = path.read_text(encoding="utf-8").split("\n")[0]
                if not first_line.startswith("#!"):
                    no_shebang.append(script)
        assert not no_shebang, f"Skill scripts missing shebang: {no_shebang}"

    def test_tc_hk_08_shared_utils_exist(self):
        """TC-HK-08: Shared utils library exists for Node.js hooks."""
        utils_path = HOOKS_DIR / "lib" / "utils.mjs"
        assert utils_path.exists(), "hooks/lib/utils.mjs not found"


@pytest.mark.static
class TestHooksPaths:
    def test_tc_hk_06_paths_use_plugin_root(self):
        """TC-HK-06: hooks.json command paths use ${CLAUDE_PLUGIN_ROOT}."""
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        for event_name, event_configs in data["hooks"].items():
            for config in event_configs:
                for hook in config.get("hooks", []):
                    cmd = hook.get("command", "")
                    if cmd and "/" in cmd:
                        assert "${CLAUDE_PLUGIN_ROOT}" in cmd, (
                            f"Hook command in '{event_name}' uses path '{cmd}' "
                            f"without ${{CLAUDE_PLUGIN_ROOT}} prefix"
                        )


@pytest.mark.static
class TestHooksStateConsistency:
    def test_tc_hk_07_pre_tool_use_states_match_conftest(self):
        """TC-HK-07: CR states in pre-tool-use hook match conftest CR_STATES."""
        # Check .mjs version first, fall back to .sh for backward compatibility
        script_path = HOOKS_DIR / "pre-tool-use.mjs"
        if not script_path.exists():
            script_path = HOOKS_DIR / "pre-tool-use.sh"
        if not script_path.exists():
            pytest.skip("pre-tool-use hook script not found")
        content = script_path.read_text(encoding="utf-8")
        # Extract state references from either bash case or JS if/switch
        checked_states = []
        for state in CR_STATES:
            if f"'{state}'" in content or f'"{state}"' in content:
                checked_states.append(state)
        # Gate reminder states should be a subset of CR_STATES
        for state in checked_states:
            assert state in CR_STATES, (
                f"pre-tool-use hook references state '{state}' "
                f"not in conftest CR_STATES: {CR_STATES}"
            )
        assert len(checked_states) >= 3, (
            f"pre-tool-use hook only references {len(checked_states)} CR states, expected ≥3"
        )


@pytest.mark.static
class TestHooksV2Features:
    """Tests for Claude Code v2.1 feature alignment (H1-H10)."""

    def test_tc_hk_09_async_hooks_configured(self):
        """TC-HK-09: Advisory hooks have async:true for non-blocking execution."""
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        # intent-detect (UserPromptSubmit) should be async
        for config in data["hooks"].get("UserPromptSubmit", []):
            for hook in config.get("hooks", []):
                if "intent-detect" in hook.get("command", ""):
                    assert hook.get("async") is True, (
                        "intent-detect.mjs should have async:true for non-blocking execution"
                    )
        # post-cr-update (PostToolUse) should be async
        for config in data["hooks"].get("PostToolUse", []):
            for hook in config.get("hooks", []):
                if "post-cr-update" in hook.get("command", ""):
                    assert hook.get("async") is True, (
                        "post-cr-update.mjs should have async:true for non-blocking execution"
                    )

    def test_tc_hk_10_precompact_hook_exists(self):
        """TC-HK-10: PreCompact hook is configured in hooks.json."""
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        assert "PreCompact" in data["hooks"], (
            "PreCompact hook event not found in hooks.json"
        )

    def test_tc_hk_11_post_tool_use_failure_configured(self):
        """TC-HK-11: PostToolUseFailure hook is configured for Write/Edit."""
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        assert "PostToolUseFailure" in data["hooks"], (
            "PostToolUseFailure hook event not found in hooks.json"
        )
        for config in data["hooks"]["PostToolUseFailure"]:
            matcher = config.get("matcher", {})
            # matcher can be a string (shorthand) or dict with tool_name
            if isinstance(matcher, str):
                tool_pattern = matcher
            else:
                tool_pattern = matcher.get("tool_name", "")
            assert "Write" in tool_pattern, (
                "PostToolUseFailure should match Write tool"
            )

    def test_tc_hk_12_agent_memory_configured(self):
        """TC-HK-12: All agents have memory:project for cross-session persistence."""
        agents_dir = DEVPACE_ROOT / "agents"
        for agent_file in agents_dir.glob("*.md"):
            content = agent_file.read_text(encoding="utf-8")
            # Extract frontmatter
            if content.startswith("---"):
                fm_end = content.index("---", 3)
                fm = yaml.safe_load(content[3:fm_end])
                assert fm.get("memory") == "project", (
                    f"Agent {agent_file.name} should have memory:project, "
                    f"got: {fm.get('memory')}"
                )

    def test_tc_hk_13_skill_level_hooks_configured(self):
        """TC-HK-13: pace-dev and pace-review have skill-level hooks."""
        for skill_name in ["pace-dev", "pace-review", "pace-init"]:
            skill_path = DEVPACE_ROOT / "skills" / skill_name / "SKILL.md"
            assert skill_path.exists(), f"SKILL.md not found for {skill_name}"
            content = skill_path.read_text(encoding="utf-8")
            if content.startswith("---"):
                fm_end = content.index("---", 3)
                fm = yaml.safe_load(content[3:fm_end])
                assert "hooks" in fm, (
                    f"Skill {skill_name} should have hooks in frontmatter"
                )
                assert "PreToolUse" in fm["hooks"], (
                    f"Skill {skill_name} hooks should include PreToolUse"
                )

    def test_tc_hk_14_output_styles_exist(self):
        """TC-HK-14: Output style file exists and is declared in plugin.json."""
        style_path = DEVPACE_ROOT / "output-styles" / "devpace-bizdevops.md"
        assert style_path.exists(), "output-styles/devpace-bizdevops.md not found"
        # Check plugin.json declares it
        plugin_json = DEVPACE_ROOT / ".claude-plugin" / "plugin.json"
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
        assert "outputStyles" in data, "plugin.json should declare outputStyles"
        assert any("devpace-bizdevops" in s for s in data["outputStyles"]), (
            "plugin.json outputStyles should reference devpace-bizdevops"
        )

    def test_tc_hk_15_plugin_settings_exist(self):
        """TC-HK-15: Plugin settings.json exists at root."""
        settings_path = DEVPACE_ROOT / "settings.json"
        assert settings_path.exists(), "settings.json not found at Plugin root"
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        assert "agents" in data, "settings.json should have agents section"

    def test_tc_hk_17_hooks_json_scripts_exist_on_disk(self):
        """TC-HK-17: All scripts referenced in hooks.json exist on disk."""
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        missing = []
        for event_name, event_configs in data["hooks"].items():
            for config in event_configs:
                for hook in config.get("hooks", []):
                    cmd = hook.get("command", "")
                    if not cmd:
                        continue
                    # Extract script filename from ${CLAUDE_PLUGIN_ROOT}/hooks/...
                    prefix = "${CLAUDE_PLUGIN_ROOT}/hooks/"
                    if prefix in cmd:
                        rel_path = cmd.split(prefix, 1)[1]
                        script_path = HOOKS_DIR / rel_path
                        if not script_path.exists():
                            missing.append(f"{event_name}: {rel_path}")
        assert not missing, (
            f"hooks.json references scripts not found on disk: {missing}"
        )

    def test_tc_hk_16_sync_push_async_configured(self):
        """TC-HK-16: sync-push.mjs is configured as async in PostToolUse hooks."""
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        found = False
        for config in data["hooks"].get("PostToolUse", []):
            for hook in config.get("hooks", []):
                if "sync-push" in hook.get("command", ""):
                    found = True
                    assert hook.get("async") is True, (
                        "sync-push.mjs should have async:true for non-blocking execution"
                    )
        assert found, "sync-push.mjs not found in PostToolUse hooks"
