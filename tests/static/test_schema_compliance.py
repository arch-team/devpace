"""TC-SC: Template files comply with schema contracts."""
import re
import pytest
from tests.conftest import DEVPACE_ROOT

TEMPLATE_DIR = DEVPACE_ROOT / "skills" / "pace-init" / "templates"
SCHEMA_DIR = DEVPACE_ROOT / "knowledge" / "_schema"
METRICS_FILE = DEVPACE_ROOT / "knowledge" / "metrics.md"


def _headings(text):
    """Extract markdown headings as (level, title) tuples."""
    return [(len(m.group(1)), m.group(2).strip())
            for m in re.finditer(r'^(#{1,6})\s+(.+)$', text, re.MULTILINE)]


def _has_heading(text, title_substr):
    """Check if text contains a heading with given substring."""
    return any(title_substr in h[1] for h in _headings(text))


def _table_columns(text, table_heading_substr=None):
    """Extract column names from the first markdown table (or one after a heading)."""
    lines = text.splitlines()
    start = 0
    if table_heading_substr:
        for i, line in enumerate(lines):
            if table_heading_substr in line and line.strip().startswith('#'):
                start = i
                break
    for i in range(start, len(lines)):
        line = lines[i].strip()
        if line.startswith('|') and '---' not in line:
            cols = [c.strip() for c in line.split('|') if c.strip()]
            if cols:
                return cols
    return []


@pytest.mark.static
class TestSchemaCompliance:
    def test_tc_sc_01_cr_template(self):
        """TC-SC-01: cr.md has required sections and defaults."""
        content = (TEMPLATE_DIR / "cr.md").read_text(encoding="utf-8")
        assert _has_heading(content, "意图"), "cr.md missing '意图' section"
        assert _has_heading(content, "质量检查"), "cr.md missing '质量检查' section"
        assert _has_heading(content, "事件"), "cr.md missing '事件' section"
        assert "created" in content, "cr.md should default status to 'created'"
        cols = _table_columns(content, "事件")
        assert "日期" in cols and "事件" in cols and "备注" in cols, \
            f"事件 table should have 日期/事件/备注, got {cols}"

    def test_tc_sc_02_project_template(self):
        """TC-SC-02: project.md has required structure (minimal stub or full)."""
        content = (TEMPLATE_DIR / "project.md").read_text(encoding="utf-8")
        assert _has_heading(content, "业务目标"), "project.md missing '业务目标'"
        assert _has_heading(content, "价值功能树"), "project.md missing '价值功能树'"
        assert ">" in content, "project.md should have blockquote positioning"
        assert "{{PROJECT_NAME}}" in content, "project.md should have PROJECT_NAME placeholder"

    def test_tc_sc_03_state_template(self):
        """TC-SC-03: state.md has required structure and line count (minimal: no iteration line)."""
        content = (TEMPLATE_DIR / "state.md").read_text(encoding="utf-8")
        assert ">" in content, "state.md should have blockquote header"
        assert "目标" in content, "state.md should reference 目标"
        # Iteration line is optional in v0.4.0 minimal init
        assert _has_heading(content, "当前工作"), "state.md missing '当前工作'"
        assert _has_heading(content, "下一步"), "state.md missing '下一步'"
        lines = [l for l in content.splitlines() if l.strip()]
        assert len(lines) <= 20, f"state.md template has {len(lines)} non-empty lines (target ≤15 for output)"
        assert "devpace-version" in content, "state.md should have version marker"

    def test_tc_sc_04_workflow_template(self):
        """TC-SC-04: workflow.md defines all 7 states and transitions."""
        content = (TEMPLATE_DIR / "workflow.md").read_text(encoding="utf-8")
        for state in ["created", "developing", "verifying", "in_review", "approved", "merged", "paused"]:
            assert state in content, f"workflow.md missing state: {state}"
        assert "→" in content or "->" in content, "workflow.md missing transition arrows"

    def test_tc_sc_05_checks_template(self):
        """TC-SC-05: checks.md has two gate sections with built-in checks."""
        content = (TEMPLATE_DIR / "checks.md").read_text(encoding="utf-8")
        assert "developing → verifying" in content or "developing" in content, \
            "checks.md missing 'developing → verifying' gate"
        assert "verifying → in_review" in content or "in_review" in content, \
            "checks.md missing 'verifying → in_review' gate"
        assert "需求完整性" in content, "checks.md missing built-in '需求完整性' check"
        assert "意图一致性" in content, "checks.md missing built-in '意图一致性' check"

    def test_tc_sc_06_iteration_template(self):
        """TC-SC-06: iteration.md has required tables and sections."""
        content = (TEMPLATE_DIR / "iteration.md").read_text(encoding="utf-8")
        assert _has_heading(content, "产品功能"), "iteration.md missing '产品功能'"
        assert _has_heading(content, "变更记录"), "iteration.md missing '变更记录'"
        assert _has_heading(content, "偏差快照"), "iteration.md missing '偏差快照'"
        change_cols = _table_columns(content, "变更记录")
        assert "日期" in change_cols and "类型" in change_cols, \
            f"变更记录 table should have 日期/类型, got {change_cols}"

    def test_tc_sc_07_dashboard_metrics_alignment(self):
        """TC-SC-07: dashboard.md metrics match metrics.md definitions."""
        dashboard = (TEMPLATE_DIR / "dashboard.md").read_text(encoding="utf-8")
        metrics = METRICS_FILE.read_text(encoding="utf-8") if METRICS_FILE.exists() else ""
        for metric in ["质量检查一次通过率", "人类打回率"]:
            assert metric in dashboard, f"dashboard.md missing metric: {metric}"
            if metrics:
                assert metric in metrics, f"metrics.md missing metric: {metric}"
        for metric in ["成效指标达成率"]:
            assert metric in dashboard, f"dashboard.md missing business metric: {metric}"

    def test_tc_sc_08_claude_md_template(self):
        """TC-SC-08: claude-md-devpace.md has required sections."""
        content = (TEMPLATE_DIR / "claude-md-devpace.md").read_text(encoding="utf-8")
        # Template can either contain detailed rules or delegate to devpace-rules.md
        delegates_to_rules = "devpace-rules.md" in content
        if not delegates_to_rules:
            assert _has_heading(content, "会话开始"), "claude-md missing '会话开始'"
            assert "探索" in content or "推进" in content, "claude-md missing work mode references"
            assert "需求变更" in content or "变更" in content, "claude-md missing change management"
            assert "输出" in content, "claude-md missing output control"
        assert ".devpace/" in content, "claude-md missing .devpace file reference"
        assert "state.md" in content, "claude-md missing state.md reference"
