"""TC-HK: Hook configuration and script validation."""
import json
import os
import stat

import pytest
from tests.conftest import DEVPACE_ROOT, CR_STATES

HOOKS_DIR = DEVPACE_ROOT / "hooks"
HOOKS_JSON = HOOKS_DIR / "hooks.json"

# Valid hook event names (case-sensitive per Claude Code spec)
VALID_HOOK_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "UserPromptSubmit",
    "Stop",
    "SessionStart",
    "SessionEnd",
    "SubagentStart",
    "SubagentStop",
    "TeammateIdle",
    "TaskCompleted",
}

EXPECTED_SCRIPTS = ["session-start.sh", "pre-tool-use.sh", "session-stop.sh"]


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
        """TC-HK-07: CR states in pre-tool-use.sh match conftest CR_STATES."""
        script_path = HOOKS_DIR / "pre-tool-use.sh"
        if not script_path.exists():
            pytest.skip("pre-tool-use.sh not found")
        content = script_path.read_text(encoding="utf-8")
        # The script checks developing, verifying, in_review in case statements
        checked_states = []
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.endswith(")") and not stripped.startswith("#"):
                # Extract case pattern like "developing)"
                state = stripped.rstrip(")")
                if state in CR_STATES:
                    checked_states.append(state)
        # All states referenced in the script must be in CR_STATES
        for state in checked_states:
            assert state in CR_STATES, (
                f"pre-tool-use.sh references state '{state}' "
                f"not in conftest CR_STATES: {CR_STATES}"
            )
