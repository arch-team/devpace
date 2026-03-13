"""TC-INIT: pace-init Skill comprehensive static validation.

Covers:
- Frontmatter & hook guards (TC-INIT-01~05, original)
- Template completeness & quality (TC-INIT-10~19)
- Procedure file routing & integrity (TC-INIT-20~29)
- Migration chain consistency (TC-INIT-30~39)
- Lifecycle detection rules (TC-INIT-40~49)
- Schema references (TC-INIT-50~59)
- Subcommand completeness (TC-INIT-60~69)
- Content quality & layer separation (TC-INIT-70~79)
"""
import re

import pytest
import yaml
from tests.conftest import DEVPACE_ROOT, LEGAL_TOOL_NAMES, TEMPLATE_FILES, parse_frontmatter

SKILL_PATH = DEVPACE_ROOT / "skills" / "pace-init" / "SKILL.md"
SKILL_DIR = DEVPACE_ROOT / "skills" / "pace-init"
TEMPLATES_DIR = DEVPACE_ROOT / "skills" / "pace-init" / "templates"
SCHEMA_DIR = DEVPACE_ROOT / "knowledge" / "_schema"


def _skill_body():
    """Return SKILL.md body text (after frontmatter)."""
    text = SKILL_PATH.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    return parts[2] if len(parts) >= 3 else text


def _procedure_files():
    """Return list of all init-procedures-*.md files."""
    return sorted(SKILL_DIR.glob("init-procedures-*.md"))


# ── Expected inventory ──────────────────────────────────────────────────────

EXPECTED_TEMPLATES = TEMPLATE_FILES

EXPECTED_PROCEDURES = [
    "init-procedures-core.md",
    "init-procedures-full.md",
    "init-procedures-from.md",
    "init-procedures-verify.md",
    "init-procedures-reset.md",
    "init-procedures-dryrun.md",
    "init-procedures-template.md",
    "init-procedures-migration.md",
    "init-procedures-monorepo.md",
    "init-procedures-checks.md",
    "init-procedures-lite.md",
]

# Routing table from SKILL.md: parameter -> procedure file(s)
ROUTING_TABLE = {
    "（默认）": ["init-procedures-core.md"],
    "full": ["init-procedures-core.md", "init-procedures-full.md"],
    "--from": ["init-procedures-core.md", "init-procedures-from.md"],
    "--import-insights": ["init-procedures-from.md"],
    "--verify": ["init-procedures-verify.md"],
    "--dry-run": ["init-procedures-dryrun.md", "init-procedures-core.md"],
    "--reset": ["init-procedures-reset.md"],
    "--export-template": ["init-procedures-template.md"],
    "--from-template": ["init-procedures-template.md"],
    "（迁移触发时）": ["init-procedures-migration.md"],
    "（检测到 monorepo 信号时）": ["init-procedures-monorepo.md"],
}

# Documented subcommands from argument-hint
DOCUMENTED_SUBCOMMANDS = [
    "full",
    "--from",
    "--verify",
    "--fix",
    "--dry-run",
    "--reset",
    "--keep-insights",
    "--export-template",
    "--from-template",
    "--import-insights",
    "--interactive",
]

# Monorepo signal files from init-procedures-monorepo.md
MONOREPO_SIGNALS = [
    "pnpm-workspace.yaml",
    "nx.json",
    "turbo.json",
    "lerna.json",
    "rush.json",
]

# ════════════════════════════════════════════════════════════════════════════
# ORIGINAL TESTS (TC-INIT-01 ~ TC-INIT-05)
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.static
class TestPaceInitFrontmatter:
    """Original frontmatter and hook guard tests."""

    def test_tc_init_01_edit_in_allowed_tools(self):
        """TC-INIT-01: Edit tool is present in pace-init allowed-tools."""
        fm = parse_frontmatter(SKILL_PATH)
        assert fm and "allowed-tools" in fm
        tools = [t.strip() for t in fm["allowed-tools"].split(",")]
        assert "Edit" in tools, (
            f"pace-init allowed-tools missing Edit; got: {tools}"
        )

    def test_tc_init_02_hook_matcher_subset_of_allowed_tools(self):
        """TC-INIT-02: Hook matcher tool_name entries are a subset of allowed-tools."""
        fm = parse_frontmatter(SKILL_PATH)
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
        """TC-INIT-03: Hook guard is a command Hook with scope check script."""
        fm = parse_frontmatter(SKILL_PATH)
        assert fm and "hooks" in fm
        hooks_found = []
        for _event, entries in fm["hooks"].items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                for hook in entry.get("hooks", []):
                    if isinstance(hook, dict):
                        hooks_found.append(hook)
        assert hooks_found, "No hooks found in pace-init SKILL.md"
        # Verify at least one command hook with scope check script
        command_hooks = [h for h in hooks_found if h.get("type") == "command"]
        assert command_hooks, "pace-init should have a command-type hook (not prompt)"
        scope_check = command_hooks[0]
        assert "pace-init-scope-check" in scope_check.get("command", ""), (
            "Hook command should reference pace-init-scope-check script"
        )
        # Verify the script file exists
        script_path = DEVPACE_ROOT / "hooks" / "pace-init-scope-check.mjs"
        assert script_path.exists(), (
            f"Hook script not found: {script_path}"
        )
        # Verify the script covers all 3 write targets
        script_content = script_path.read_text(encoding="utf-8")
        assert ".devpace/" in script_content, "Script does not check .devpace/ scope"
        assert "CLAUDE.md" in script_content, "Script does not check CLAUDE.md scope"
        assert ".gitignore" in script_content, "Script does not check .gitignore scope"

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
        start_pos = content.index("<!-- devpace-start -->")
        end_pos = content.index("<!-- devpace-end -->")
        assert start_pos < end_pos, (
            "devpace-start marker must appear before devpace-end"
        )


# ════════════════════════════════════════════════════════════════════════════
# TEMPLATE COMPLETENESS (TC-INIT-10 ~ TC-INIT-19)
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.static
class TestTemplateCompleteness:
    """Verify all expected template files exist and have proper structure."""

    @pytest.mark.parametrize("tpl_name", EXPECTED_TEMPLATES)
    def test_tc_init_10_template_exists(self, tpl_name):
        """TC-INIT-10: Each expected template file exists."""
        path = TEMPLATES_DIR / tpl_name
        assert path.exists(), f"Template missing: {tpl_name}"

    @pytest.mark.parametrize("tpl_name", EXPECTED_TEMPLATES)
    def test_tc_init_11_template_non_empty(self, tpl_name):
        """TC-INIT-11: Each template file is non-empty."""
        path = TEMPLATES_DIR / tpl_name
        if not path.exists():
            pytest.skip(f"Template not found: {tpl_name}")
        content = path.read_text(encoding="utf-8").strip()
        assert len(content) > 10, f"Template {tpl_name} is nearly empty"

    def test_tc_init_12_no_orphan_templates(self):
        """TC-INIT-12: No unexpected template files exist."""
        actual = {f.name for f in TEMPLATES_DIR.glob("*.md")}
        expected = set(EXPECTED_TEMPLATES)
        orphans = actual - expected
        assert not orphans, (
            f"Unexpected template files: {orphans}. "
            "Add them to EXPECTED_TEMPLATES if intentional."
        )

    def test_tc_init_13_state_template_required_sections(self):
        """TC-INIT-13: state.md template has required sections."""
        content = (TEMPLATES_DIR / "state.md").read_text(encoding="utf-8")
        required = ["当前工作", "下一步"]
        for section in required:
            assert section in content, (
                f"state.md template missing required section: {section}"
            )

    def test_tc_init_14_project_template_required_sections(self):
        """TC-INIT-14: project.md template has required sections."""
        content = (TEMPLATES_DIR / "project.md").read_text(encoding="utf-8")
        required = ["业务目标", "价值功能树", "范围", "项目原则"]
        for section in required:
            assert section in content, (
                f"project.md template missing required section: {section}"
            )

    def test_tc_init_15_checks_template_gate_sections(self):
        """TC-INIT-15: checks.md template has Gate sections for state transitions."""
        content = (TEMPLATES_DIR / "checks.md").read_text(encoding="utf-8")
        required = ["developing → verifying", "verifying → in_review"]
        for gate in required:
            assert gate in content, (
                f"checks.md template missing gate section: {gate}"
            )

    def test_tc_init_16_checks_template_has_builtin_checks(self):
        """TC-INIT-16: checks.md template includes devpace builtin checks."""
        content = (TEMPLATES_DIR / "checks.md").read_text(encoding="utf-8")
        assert "需求完整性" in content, (
            "checks.md missing builtin '需求完整性' check"
        )
        assert "意图一致性" in content, (
            "checks.md missing builtin '意图一致性' check"
        )

    def test_tc_init_17_context_template_placeholders(self):
        """TC-INIT-17: context.md template uses proper placeholder format."""
        content = (TEMPLATES_DIR / "context.md").read_text(encoding="utf-8")
        placeholders = re.findall(r"\{\{([A-Z_]+)\}\}", content)
        assert len(placeholders) >= 3, (
            f"context.md has too few placeholders ({len(placeholders)}); "
            "expected at least 3 (PROJECT_NAME, TECH_STACK, etc.)"
        )

    def test_tc_init_18_claude_md_template_has_placeholders(self):
        """TC-INIT-18: claude-md-devpace.md template has required placeholders."""
        content = (TEMPLATES_DIR / "claude-md-devpace.md").read_text(encoding="utf-8")
        required_placeholders = ["PROJECT_NAME", "PROJECT_POSITIONING"]
        for ph in required_placeholders:
            assert f"{{{{{ph}}}}}" in content, (
                f"claude-md-devpace.md missing placeholder: {{{{{ph}}}}}"
            )

    def test_tc_init_19_workflow_template_has_state_machine(self):
        """TC-INIT-19: workflow.md template defines the CR state machine."""
        content = (TEMPLATES_DIR / "workflow.md").read_text(encoding="utf-8")
        required_states = ["created", "developing", "verifying", "in_review", "approved", "merged"]
        for state in required_states:
            assert state in content, (
                f"workflow.md template missing state: {state}"
            )


# ════════════════════════════════════════════════════════════════════════════
# PROCEDURE FILE ROUTING & INTEGRITY (TC-INIT-20 ~ TC-INIT-29)
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.static
class TestProcedureIntegrity:
    """Verify procedure files exist, are referenced correctly, and are well-formed."""

    @pytest.mark.parametrize("proc_name", EXPECTED_PROCEDURES)
    def test_tc_init_20_procedure_file_exists(self, proc_name):
        """TC-INIT-20: Each expected procedure file exists."""
        path = SKILL_DIR / proc_name
        assert path.exists(), f"Procedure file missing: {proc_name}"

    @pytest.mark.parametrize("proc_name", EXPECTED_PROCEDURES)
    def test_tc_init_21_procedure_non_empty(self, proc_name):
        """TC-INIT-21: Each procedure file is non-empty."""
        path = SKILL_DIR / proc_name
        if not path.exists():
            pytest.skip(f"Procedure file not found: {proc_name}")
        content = path.read_text(encoding="utf-8").strip()
        assert len(content) > 50, f"Procedure {proc_name} is nearly empty"

    def test_tc_init_22_routing_table_files_exist(self):
        """TC-INIT-22: Every file in the SKILL.md routing table exists on disk."""
        missing = []
        for param, files in ROUTING_TABLE.items():
            for f in files:
                if not (SKILL_DIR / f).exists():
                    missing.append(f"{param} -> {f}")
        assert not missing, f"Routing table references missing files: {missing}"

    def test_tc_init_23_no_orphan_procedures(self):
        """TC-INIT-23: No procedure files exist that aren't in the expected list."""
        actual = {f.name for f in _procedure_files()}
        expected = set(EXPECTED_PROCEDURES)
        orphans = actual - expected
        assert not orphans, (
            f"Unexpected procedure files: {orphans}. "
            "Add them to EXPECTED_PROCEDURES if intentional."
        )

    def test_tc_init_24_all_procedures_reachable(self):
        """TC-INIT-24: All procedure files are reachable (referenced by SKILL.md or another procedure)."""
        body = _skill_body()
        # Collect all refs from all procedure files + SKILL.md body
        all_refs = set(re.findall(r"init-procedures-[\w-]+\.md", body))
        for proc_path in _procedure_files():
            content = proc_path.read_text(encoding="utf-8")
            all_refs.update(re.findall(r"init-procedures-[\w-]+\.md", content))
        for proc in EXPECTED_PROCEDURES:
            assert proc in all_refs, (
                f"{proc} is not referenced by SKILL.md or any other procedure file. "
                "It may be an orphan."
            )

    def test_tc_init_25_core_procedure_has_speed_card(self):
        """TC-INIT-25: init-procedures-core.md has §0 速查卡片."""
        path = SKILL_DIR / "init-procedures-core.md"
        content = path.read_text(encoding="utf-8")
        assert "§0" in content and "速查" in content, (
            "init-procedures-core.md missing §0 速查卡片"
        )

    def test_tc_init_26_procedure_cross_references_valid(self):
        """TC-INIT-26: Procedure files that reference other procedures point to existing files."""
        pattern = re.compile(r"init-procedures-[\w-]+\.md")
        for proc_path in _procedure_files():
            content = proc_path.read_text(encoding="utf-8")
            refs = pattern.findall(content)
            for ref in refs:
                assert (SKILL_DIR / ref).exists(), (
                    f"{proc_path.name} references non-existent {ref}"
                )

    def test_tc_init_27_core_lifecycle_stages_defined(self):
        """TC-INIT-27: Core procedure defines strategies for all 3 lifecycle stages."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        for stage in ["阶段 A", "阶段 B", "阶段 C"]:
            assert stage in content, (
                f"Core procedure missing lifecycle stage: {stage}"
            )

    def test_tc_init_28_verify_procedure_references_schemas(self):
        """TC-INIT-28: Verify procedure references schema files that exist."""
        content = (SKILL_DIR / "init-procedures-verify.md").read_text(encoding="utf-8")
        schema_refs = re.findall(r"([\w-]+-format\.md)", content)
        for ref in schema_refs:
            assert (SCHEMA_DIR / ref).exists(), (
                f"init-procedures-verify.md references non-existent schema: {ref}"
            )

    def test_tc_init_29_checks_procedure_ecosystems_covered(self):
        """TC-INIT-29: Checks procedure covers all major ecosystems."""
        content = (SKILL_DIR / "init-procedures-checks.md").read_text(encoding="utf-8")
        ecosystems = ["Node.js", "Python", "Go", "Rust"]
        for eco in ecosystems:
            assert eco in content, (
                f"Checks procedure missing ecosystem: {eco}"
            )


# ════════════════════════════════════════════════════════════════════════════
# MIGRATION CHAIN CONSISTENCY (TC-INIT-30 ~ TC-INIT-39)
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.static
class TestMigrationChain:
    """Verify version migration chain is consistent and connected."""

    def _parse_migration_versions(self):
        """Extract version transitions from migration section headers (§N vX → vY)."""
        path = SKILL_DIR / "init-procedures-migration.md"
        content = path.read_text(encoding="utf-8")
        # Match section headers like "## §3 v1.2.0 → v1.5.0 迁移"
        header_pattern = re.compile(
            r"^##\s+§\d+\s+v?(\d+\.\d+\.\d+)\s*→\s*v?(\d+\.\d+\.\d+)",
            re.MULTILINE,
        )
        return header_pattern.findall(content)

    def _template_version(self):
        """Extract version from state.md template."""
        content = (TEMPLATES_DIR / "state.md").read_text(encoding="utf-8")
        match = re.search(r"devpace-version:\s*(\d+\.\d+\.\d+)", content)
        return match.group(1) if match else None

    def test_tc_init_30_migration_chain_connected(self):
        """TC-INIT-30: Migration chain forms a connected path (each target is next source)."""
        transitions = self._parse_migration_versions()
        if len(transitions) < 2:
            pytest.skip("Only one migration step, no chain to verify")
        for i in range(len(transitions) - 1):
            _, target = transitions[i]
            source, _ = transitions[i + 1]
            # Allow the source to match target or a patch variant (e.g., 1.5.0 matches 1.5.x)
            target_major_minor = ".".join(target.split(".")[:2])
            source_major_minor = ".".join(source.split(".")[:2])
            assert target_major_minor == source_major_minor, (
                f"Migration chain broken: step {i} ends at {target}, "
                f"but step {i+1} starts from {source}"
            )

    def test_tc_init_31_template_version_matches_latest_target(self):
        """TC-INIT-31: state.md template version matches the latest migration target."""
        transitions = self._parse_migration_versions()
        if not transitions:
            pytest.skip("No migration transitions found")
        _, latest_target = transitions[-1]
        template_ver = self._template_version()
        assert template_ver is not None, "state.md template missing version marker"
        assert template_ver == latest_target, (
            f"Template version {template_ver} != latest migration target {latest_target}"
        )

    def test_tc_init_32_migration_has_safety_rules(self):
        """TC-INIT-32: Migration procedure documents safety rules."""
        content = (SKILL_DIR / "init-procedures-migration.md").read_text(encoding="utf-8")
        safety_keywords = ["只添加不删除", "默认值兼容", "回滚", "幂等"]
        found = [kw for kw in safety_keywords if kw in content]
        assert len(found) >= 3, (
            f"Migration procedure missing safety rules. Found only: {found}"
        )

    def test_tc_init_33_migration_speed_card(self):
        """TC-INIT-33: Migration procedure has §0 速查卡片."""
        content = (SKILL_DIR / "init-procedures-migration.md").read_text(encoding="utf-8")
        assert "§0" in content and "速查" in content, (
            "Migration procedure missing §0 速查卡片"
        )

    def test_tc_init_34_migration_version_detection_documented(self):
        """TC-INIT-34: Migration procedure documents how version is detected."""
        content = (SKILL_DIR / "init-procedures-migration.md").read_text(encoding="utf-8")
        assert "devpace-version" in content, (
            "Migration procedure does not document version marker detection"
        )
        assert "无标记" in content or "无 tag" in content, (
            "Migration procedure does not document behavior for missing version marker"
        )


# ════════════════════════════════════════════════════════════════════════════
# LIFECYCLE DETECTION RULES (TC-INIT-40 ~ TC-INIT-49)
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.static
class TestLifecycleDetection:
    """Verify lifecycle detection rules are complete and consistent."""

    def test_tc_init_40_stage_a_line_count_target(self):
        """TC-INIT-40: Stage A defines state.md line count target ~6."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        # Look for line count specification near Stage A
        assert "~6" in content or "约 6" in content or "6 行" in content, (
            "Stage A state.md line count target (~6) not documented"
        )

    def test_tc_init_41_stage_b_line_count_target(self):
        """TC-INIT-41: Stage B defines state.md line count target ~10."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        assert "~10" in content or "约 10" in content or "10 行" in content, (
            "Stage B state.md line count target (~10) not documented"
        )

    def test_tc_init_42_stage_c_line_count_target(self):
        """TC-INIT-42: Stage C defines state.md line count target ~13."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        assert "~13" in content or "约 13" in content or "13 行" in content, (
            "Stage C state.md line count target (~13) not documented"
        )

    def test_tc_init_43_project_name_detection_sources(self):
        """TC-INIT-43: Stage A documents project name detection priority."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        sources = ["package.json", "pyproject.toml", "go.mod", "Cargo.toml", "git remote"]
        found = [s for s in sources if s in content]
        assert len(found) >= 4, (
            f"Project name detection sources incomplete. Found: {found}"
        )

    def test_tc_init_44_stage_b_includes_git_strategy(self):
        """TC-INIT-44: Stage B strategy includes Git strategy detection."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        # Find Stage B section and check it references Git strategy
        stage_b_start = content.find("阶段 B")
        assert stage_b_start >= 0
        stage_b_section = content[stage_b_start:stage_b_start + 2000]
        assert "Git 策略" in stage_b_section or "git branch" in stage_b_section, (
            "Stage B strategy does not reference Git strategy detection"
        )

    def test_tc_init_45_stage_c_includes_version_management(self):
        """TC-INIT-45: Stage C strategy includes version management auto-config."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        stage_c_start = content.find("阶段 C")
        assert stage_c_start >= 0
        stage_c_section = content[stage_c_start:stage_c_start + 3000]
        assert "版本管理" in stage_c_section, (
            "Stage C strategy missing version management auto-config"
        )

    def test_tc_init_46_each_stage_has_guidance(self):
        """TC-INIT-46: Each lifecycle stage has a contextual guidance message."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        # Check §5 引导规则 has entries for all stages
        assert "阶段 A" in content and "阶段 B" in content and "阶段 C" in content
        guidance_section_start = content.find("情境化引导")
        assert guidance_section_start >= 0, "Missing §5 情境化引导规则 section"
        guidance = content[guidance_section_start:]
        for stage_label in ["阶段 A", "阶段 B", "阶段 C"]:
            assert stage_label in guidance, (
                f"Guidance section missing entry for {stage_label}"
            )

    def test_tc_init_47_git_strategy_patterns_documented(self):
        """TC-INIT-47: Git strategy detection has at least 3 known patterns."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        patterns = ["trunk-based", "gitflow", "环境分支"]
        found = [p for p in patterns if p in content]
        assert len(found) >= 3, (
            f"Git strategy detection patterns incomplete. Found: {found}"
        )

    def test_tc_init_48_non_git_fallback_documented(self):
        """TC-INIT-48: Non-git repository fallback behavior is documented."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        assert ("非 git" in content or "无 `.git/`" in content
                or "非 Git" in content or ".git/" in content), (
            "Non-git repository fallback behavior not documented"
        )

    def test_tc_init_49_interactive_flag_documented(self):
        """TC-INIT-49: --interactive flag behavior is documented."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        assert "--interactive" in content, (
            "--interactive flag not documented in core procedure"
        )


# ════════════════════════════════════════════════════════════════════════════
# SCHEMA REFERENCES (TC-INIT-50 ~ TC-INIT-59)
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.static
class TestSchemaReferences:
    """Verify schema file references in procedure files resolve correctly."""

    def test_tc_init_50_verify_all_schema_refs_exist(self):
        """TC-INIT-50: All schema files referenced in verify procedure exist on disk."""
        content = (SKILL_DIR / "init-procedures-verify.md").read_text(encoding="utf-8")
        refs = re.findall(r"([\w-]+-format\.md)", content)
        assert len(refs) >= 3, "Verify procedure references too few schemas"
        missing = [r for r in refs if not (SCHEMA_DIR / r).exists()]
        assert not missing, (
            f"Verify procedure references non-existent schemas: {missing}"
        )

    def test_tc_init_51_checks_procedure_refs_checks_format(self):
        """TC-INIT-51: Checks procedure references checks-format.md."""
        content = (SKILL_DIR / "init-procedures-checks.md").read_text(encoding="utf-8")
        assert "checks-format.md" in content, (
            "Checks procedure does not reference checks-format.md schema"
        )
        assert (SCHEMA_DIR / "checks-format.md").exists(), (
            "checks-format.md schema file does not exist"
        )

    def test_tc_init_52_core_procedure_refs_context_format(self):
        """TC-INIT-52: Core procedure references context-format.md for context.md generation."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        assert "context-format.md" in content, (
            "Core procedure does not reference context-format.md"
        )

    def test_tc_init_53_from_procedure_refs_insights_format(self):
        """TC-INIT-53: --from procedure references insights-format.md for import validation."""
        content = (SKILL_DIR / "init-procedures-from.md").read_text(encoding="utf-8")
        assert "insights-format.md" in content, (
            "--from procedure does not reference insights-format.md for import validation"
        )

    def test_tc_init_54_core_refs_integrations_format(self):
        """TC-INIT-54: Core procedure references integrations-format.md for CI detection."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        assert "integrations-format.md" in content, (
            "Core procedure does not reference integrations-format.md"
        )


# ════════════════════════════════════════════════════════════════════════════
# SUBCOMMAND COMPLETENESS (TC-INIT-60 ~ TC-INIT-69)
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.static
class TestSubcommandCompleteness:
    """Verify all documented subcommands are properly routed and described."""

    def test_tc_init_60_argument_hint_covers_subcommands(self):
        """TC-INIT-60: argument-hint in frontmatter lists all documented subcommands."""
        fm = parse_frontmatter(SKILL_PATH)
        assert fm and "argument-hint" in fm
        hint = fm["argument-hint"]
        for subcmd in DOCUMENTED_SUBCOMMANDS:
            assert subcmd in hint, (
                f"argument-hint missing subcommand: {subcmd}"
            )

    def test_tc_init_61_routing_table_in_skill_body(self):
        """TC-INIT-61: SKILL.md body contains a routing table with procedure mappings."""
        body = _skill_body()
        assert "执行规程" in body or "规程" in body, (
            "SKILL.md body missing routing/procedure table"
        )

    def test_tc_init_62_reset_has_confirmation(self):
        """TC-INIT-62: Reset procedure requires user confirmation before deletion."""
        content = (SKILL_DIR / "init-procedures-reset.md").read_text(encoding="utf-8")
        assert "确认" in content or "AskUserQuestion" in content, (
            "Reset procedure missing user confirmation step"
        )

    def test_tc_init_63_reset_handles_keep_insights(self):
        """TC-INIT-63: Reset procedure handles --keep-insights flag."""
        content = (SKILL_DIR / "init-procedures-reset.md").read_text(encoding="utf-8")
        assert "keep-insights" in content, (
            "Reset procedure does not handle --keep-insights flag"
        )

    def test_tc_init_64_reset_cleans_claude_md(self):
        """TC-INIT-64: Reset procedure cleans CLAUDE.md devpace section."""
        content = (SKILL_DIR / "init-procedures-reset.md").read_text(encoding="utf-8")
        assert "CLAUDE.md" in content and "devpace-start" in content, (
            "Reset procedure does not clean CLAUDE.md devpace section"
        )

    def test_tc_init_65_dryrun_zero_writes(self):
        """TC-INIT-65: Dry-run procedure explicitly states no file writes."""
        content = (SKILL_DIR / "init-procedures-dryrun.md").read_text(encoding="utf-8")
        assert "不写入" in content or "不创建" in content, (
            "Dry-run procedure does not explicitly guarantee no file writes"
        )

    def test_tc_init_66_template_export_and_import(self):
        """TC-INIT-66: Template procedure handles both export and import."""
        content = (SKILL_DIR / "init-procedures-template.md").read_text(encoding="utf-8")
        assert "--export-template" in content or "导出" in content, (
            "Template procedure missing export handling"
        )
        assert "--from-template" in content or "应用" in content, (
            "Template procedure missing import/apply handling"
        )

    def test_tc_init_67_from_handles_directory_and_multi_file(self):
        """TC-INIT-67: --from procedure handles directory paths and multiple files."""
        content = (SKILL_DIR / "init-procedures-from.md").read_text(encoding="utf-8")
        assert "目录" in content or "directory" in content, (
            "--from procedure does not document directory path handling"
        )
        assert "多文件" in content or "多个" in content, (
            "--from procedure does not document multi-file handling"
        )

    def test_tc_init_68_from_handles_openapi(self):
        """TC-INIT-68: --from procedure handles OpenAPI/Swagger specs."""
        content = (SKILL_DIR / "init-procedures-from.md").read_text(encoding="utf-8")
        assert "OpenAPI" in content or "Swagger" in content, (
            "--from procedure does not document OpenAPI/Swagger handling"
        )

    def test_tc_init_69_import_insights_confidence_degradation(self):
        """TC-INIT-69: --import-insights documents confidence degradation rule."""
        content = (SKILL_DIR / "init-procedures-from.md").read_text(encoding="utf-8")
        assert "0.8" in content or "置信度" in content, (
            "--import-insights does not document confidence degradation (×0.8)"
        )


# ════════════════════════════════════════════════════════════════════════════
# CONTENT QUALITY & LAYER SEPARATION (TC-INIT-70 ~ TC-INIT-79)
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.static
class TestContentQuality:
    """Verify content quality, description CSO compliance, and layer separation."""

    def test_tc_init_70_description_starts_with_trigger(self):
        """TC-INIT-70: Description follows CSO rules — starts with trigger conditions."""
        fm = parse_frontmatter(SKILL_PATH)
        desc = fm["description"]
        assert desc.startswith("Use when"), (
            f"Description should start with 'Use when' per CSO rules. Got: {desc[:60]}..."
        )

    def test_tc_init_71_description_has_not_for_exclusions(self):
        """TC-INIT-71: Description includes NOT-for exclusions to prevent mis-triggering."""
        fm = parse_frontmatter(SKILL_PATH)
        desc = fm["description"]
        assert "NOT" in desc, (
            "Description missing NOT-for exclusions for disambiguation"
        )

    def test_tc_init_72_description_has_trigger_keywords(self):
        """TC-INIT-72: Description includes Chinese trigger keywords."""
        fm = parse_frontmatter(SKILL_PATH)
        desc = fm["description"]
        keywords = ["初始化", "pace-init"]
        for kw in keywords:
            assert kw in desc, (
                f"Description missing trigger keyword: {kw}"
            )

    def test_tc_init_73_templates_no_dev_layer_refs(self):
        """TC-INIT-73: Templates don't reference dev-layer files (docs/ or .claude/)."""
        for tpl_path in TEMPLATES_DIR.glob("*.md"):
            content = tpl_path.read_text(encoding="utf-8")
            # Check for dev-layer path references (but allow .claude-plugin which is product layer)
            dev_refs = re.findall(r"(?:docs/|\.claude/)", content)
            assert not dev_refs, (
                f"Template {tpl_path.name} references dev-layer paths: {dev_refs}"
            )

    def test_tc_init_74_skill_body_has_input_output_sections(self):
        """TC-INIT-74: SKILL.md body follows standard structure with 输入/流程/输出."""
        body = _skill_body()
        assert "## 输入" in body, "SKILL.md body missing ## 输入 section"
        assert "## 流程" in body, "SKILL.md body missing ## 流程 section"
        assert "## 输出" in body, "SKILL.md body missing ## 输出 section"

    def test_tc_init_75_monorepo_signals_documented(self):
        """TC-INIT-75: Monorepo procedure documents all known monorepo signals."""
        content = (SKILL_DIR / "init-procedures-monorepo.md").read_text(encoding="utf-8")
        for signal in MONOREPO_SIGNALS:
            assert signal in content, (
                f"Monorepo procedure missing signal file: {signal}"
            )

    def test_tc_init_76_monorepo_signals_also_in_core(self):
        """TC-INIT-76: Core procedure references at least one monorepo signal.

        Monorepo routing is managed by SKILL.md routing table, not core.md.
        Core only needs to mention monorepo in context detection (e.g. pnpm-workspace.yaml).
        """
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        found = [s for s in MONOREPO_SIGNALS if s in content]
        assert len(found) >= 1, (
            f"Core procedure mentions no monorepo signals: {found}"
        )

    def test_tc_init_77_gitignore_handling_documented(self):
        """TC-INIT-77: .gitignore handling covers all 3 cases."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        assert ".gitignore" in content, "Core procedure missing .gitignore handling"
        # Three cases: no file, file without .devpace, file with .devpace
        cases_found = 0
        if "无 .gitignore" in content or "不存在" in content:
            cases_found += 1
        if "未包含" in content or "未含" in content:
            cases_found += 1
        if "已包含" in content or "已含" in content:
            cases_found += 1
        assert cases_found >= 2, (
            f".gitignore handling documents only {cases_found} of 3 expected cases"
        )

    def test_tc_init_78_sync_proposal_documented(self):
        """TC-INIT-78: Sync configuration proposal is documented with lifecycle-aware messaging."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        assert "pace-sync" in content, (
            "Core procedure does not reference pace-sync proposal"
        )
        assert "推荐" in content or "可选" in content, (
            "Core procedure does not differentiate sync proposal strength by stage"
        )

    def test_tc_init_79_on_demand_directory_documented(self):
        """TC-INIT-79: On-demand directory creation is documented (§6)."""
        content = (SKILL_DIR / "init-procedures-core.md").read_text(encoding="utf-8")
        assert "按需" in content or "首次使用" in content, (
            "Core procedure missing on-demand directory creation documentation (§6)"
        )
        # Verify key directories mentioned
        on_demand_dirs = ["iterations/", "metrics/", "releases/", "integrations/"]
        found = [d for d in on_demand_dirs if d in content]
        assert len(found) >= 3, (
            f"On-demand directory documentation incomplete. Found: {found}"
        )
