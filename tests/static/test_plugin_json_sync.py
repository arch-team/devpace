"""TC-PJ: plugin.json validity and sync with filesystem."""
import json
import pytest
from tests.conftest import DEVPACE_ROOT, SKILL_NAMES

PLUGIN_JSON = DEVPACE_ROOT / ".claude-plugin" / "plugin.json"

@pytest.mark.static
class TestPluginJsonSync:
    def test_tc_pj_01_valid_json(self):
        """TC-PJ-01: plugin.json is valid JSON."""
        assert PLUGIN_JSON.exists(), f"{PLUGIN_JSON} not found"
        data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_tc_pj_02_name_field(self):
        """TC-PJ-02: name field exists and is non-empty."""
        data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        assert "name" in data and data["name"], "plugin.json must have a non-empty 'name' field"

    def test_tc_pj_03_skills_discoverable(self):
        """TC-PJ-03: Every skill directory with SKILL.md is discoverable."""
        skills_root = DEVPACE_ROOT / "skills"
        for name in SKILL_NAMES:
            skill_md = skills_root / name / "SKILL.md"
            assert skill_md.exists(), f"Missing SKILL.md for skill '{name}'"

    def test_tc_pj_04_declared_paths_exist(self):
        """TC-PJ-04: If plugin.json declares explicit paths, they must exist."""
        data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        for key in ("skills", "agents", "hooks", "rules", "commands"):
            if key in data:
                paths = data[key] if isinstance(data[key], list) else [data[key]]
                for p in paths:
                    if isinstance(p, str):
                        resolved = DEVPACE_ROOT / p.lstrip("./")
                        assert resolved.exists(), f"Declared {key} path does not exist: {p}"

    def test_tc_pj_05_marketplace_version_sync(self):
        """TC-PJ-05: marketplace.json version matches plugin.json version."""
        marketplace_json = DEVPACE_ROOT / ".claude-plugin" / "marketplace.json"
        if not marketplace_json.exists():
            pytest.skip("marketplace.json not found")
        plugin_data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        marketplace_data = json.loads(marketplace_json.read_text(encoding="utf-8"))
        plugin_version = plugin_data.get("version")
        if not plugin_version:
            pytest.skip("plugin.json has no version field")
        for plugin_entry in marketplace_data.get("plugins", []):
            mp_version = plugin_entry.get("version")
            if mp_version:
                assert mp_version == plugin_version, (
                    f"marketplace.json plugin '{plugin_entry.get('name')}' version "
                    f"'{mp_version}' != plugin.json version '{plugin_version}'"
                )
