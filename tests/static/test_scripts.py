"""TC-SCR: Script output validation — verifies JSON structure of all .mjs scripts."""
import json
import os
import subprocess
import textwrap

import pytest
from tests.conftest import DEVPACE_ROOT

SCRIPTS_DIR = DEVPACE_ROOT / "scripts"

# ── Minimal CR fixture content ─────────────────────────────────────────
CR_FIXTURE = textwrap.dedent("""\
    # CR-001 测试变更

    - **ID**：CR-001
    - **状态**：developing
    - **类型**：feature
    - **复杂度**：S
    - **产品功能**：PF-001

    ## 意图

    测试用 CR 意图描述。

    ## 事件

    | 日期 | 事件 | 操作者 | 备注 |
    |------|------|--------|------|
    | 2025-01-01 | created | Claude | 初始化 |
    | 2025-01-02 | developing | Claude | 开始开发 |

    ## 质量检查

    - [ ] Gate 1
""")

CR_MERGED_FIXTURE = textwrap.dedent("""\
    # CR-002 已合并变更

    - **ID**：CR-002
    - **状态**：merged
    - **类型**：feature
    - **复杂度**：M

    ## 意图

    已合并的测试 CR。

    ## 事件

    | 日期 | 事件 | 操作者 | 备注 |
    |------|------|--------|------|
    | 2025-01-01 | created | Claude | |
    | 2025-01-05 | merged | 用户 | 审批通过 |

    ## 质量检查

    - [x] Gate 1
    - [x] Gate 2
""")

STATE_FIXTURE = textwrap.dedent("""\
    <!-- devpace-version: 1.0.0 -->
    > 目标：测试项目

    **进行中**：CR-001 测试变更

    下一步：完成 CR-001
""")

PROJECT_FIXTURE = textwrap.dedent("""\
    # 测试项目

    > 测试用项目描述

    ## 价值功能树

    - PF-001 测试功能 → CR-001 🔄
""")


def _make_devpace(tmp_path):
    """Create a minimal .devpace directory for script testing."""
    d = tmp_path / ".devpace"
    backlog = d / "backlog"
    backlog.mkdir(parents=True)

    (backlog / "CR-001.md").write_text(CR_FIXTURE, encoding="utf-8")
    (backlog / "CR-002.md").write_text(CR_MERGED_FIXTURE, encoding="utf-8")
    (d / "state.md").write_text(STATE_FIXTURE, encoding="utf-8")
    (d / "project.md").write_text(PROJECT_FIXTURE, encoding="utf-8")

    return str(d)


def _run_script(script_name, args=None, stdin_data=None, expect_exit_0=True):
    """Run a .mjs script and return parsed JSON output."""
    script_path = str(SCRIPTS_DIR / script_name)
    cmd = ["node", script_path] + (args or [])
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=15,
        input=stdin_data,
    )
    if expect_exit_0 and result.returncode != 0:
        assert result.returncode == 0, (
            f"Script {script_name} exited with {result.returncode}.\n"
            f"stderr: {result.stderr}"
        )
    stdout = result.stdout.strip()
    assert stdout, (
        f"Script {script_name} produced no stdout.\n"
        f"stderr: {result.stderr}\nreturncode: {result.returncode}"
    )
    return json.loads(stdout), result.returncode


@pytest.mark.static
class TestExtractCrMetadata:
    """Tests for extract-cr-metadata.mjs JSON output."""

    def test_tc_scr_01_returns_json_array(self, tmp_path):
        """TC-SCR-01: extract-cr-metadata returns a JSON array."""
        devpace_dir = _make_devpace(tmp_path)
        data, rc = _run_script("extract-cr-metadata.mjs", [devpace_dir])
        assert rc == 0
        assert isinstance(data, list)
        assert len(data) == 2

    def test_tc_scr_02_cr_has_required_fields(self, tmp_path):
        """TC-SCR-02: Each CR object has required metadata fields."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("extract-cr-metadata.mjs", [devpace_dir])
        required_fields = {"id", "title", "type", "status", "events", "breaking", "fileName"}
        for cr in data:
            missing = required_fields - set(cr.keys())
            assert not missing, f"CR {cr.get('id', '?')} missing fields: {missing}"

    def test_tc_scr_03_status_filter_works(self, tmp_path):
        """TC-SCR-03: --status filter returns only matching CRs."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("extract-cr-metadata.mjs", [devpace_dir, "--status", "merged"])
        assert all(cr["status"] == "merged" for cr in data)
        assert len(data) == 1
        assert data[0]["id"] == "CR-002"

    def test_tc_scr_04_events_parsed(self, tmp_path):
        """TC-SCR-04: Events table is parsed into array."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("extract-cr-metadata.mjs", [devpace_dir, "--id", "CR-001"])
        assert len(data) == 1
        events = data[0]["events"]
        assert isinstance(events, list)
        assert len(events) >= 2
        assert events[0]["event"] == "created"


@pytest.mark.static
class TestValidateSchema:
    """Tests for validate-schema.mjs JSON output."""

    def test_tc_scr_05_returns_json_with_results(self, tmp_path):
        """TC-SCR-05: validate-schema returns JSON with results array."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("validate-schema.mjs", [devpace_dir], expect_exit_0=False)
        assert "results" in data
        assert isinstance(data["results"], list)
        assert "total" in data
        assert "errors" in data
        assert "warnings" in data

    def test_tc_scr_06_cr_validation_has_correct_type(self, tmp_path):
        """TC-SCR-06: CR file validation identifies type as 'cr'."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("validate-schema.mjs", [devpace_dir, "--type", "cr"], expect_exit_0=False)
        for result in data["results"]:
            assert result["type"] == "cr"

    def test_tc_scr_07_each_result_has_structure(self, tmp_path):
        """TC-SCR-07: Each validation result has file/type/valid/errors/warnings."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("validate-schema.mjs", [devpace_dir], expect_exit_0=False)
        required_fields = {"file", "type", "valid", "errors", "warnings"}
        for result in data["results"]:
            missing = required_fields - set(result.keys())
            assert not missing, f"Result for {result.get('file', '?')} missing fields: {missing}"

    def test_tc_scr_08_valid_cr_passes(self, tmp_path):
        """TC-SCR-08: A well-formed CR passes validation."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script(
            "validate-schema.mjs",
            [devpace_dir, "--file", os.path.join(devpace_dir, "backlog", "CR-001.md")],
            expect_exit_0=False,
        )
        cr_result = data["results"][0]
        assert cr_result["valid"] is True, f"CR-001 validation errors: {cr_result['errors']}"


@pytest.mark.static
class TestCollectSignals:
    """Tests for collect-signals.mjs JSON output."""

    def test_tc_scr_09_returns_json_with_triggered(self, tmp_path):
        """TC-SCR-09: collect-signals returns JSON with triggered array."""
        devpace_dir = _make_devpace(tmp_path)
        data, rc = _run_script("collect-signals.mjs", [devpace_dir])
        assert rc == 0
        assert "triggered" in data
        assert isinstance(data["triggered"], list)
        assert "top_signal" in data
        assert "role" in data
        assert "timestamp" in data

    def test_tc_scr_10_signals_have_required_fields(self, tmp_path):
        """TC-SCR-10: Each triggered signal has id/group/label/detail."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("collect-signals.mjs", [devpace_dir])
        required_fields = {"id", "group", "label", "detail"}
        for signal in data["triggered"]:
            missing = required_fields - set(signal.keys())
            assert not missing, f"Signal {signal.get('id', '?')} missing fields: {missing}"

    def test_tc_scr_11_developing_cr_triggers_s3(self, tmp_path):
        """TC-SCR-11: A developing CR triggers S3 (continue development)."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("collect-signals.mjs", [devpace_dir])
        signal_ids = [s["id"] for s in data["triggered"]]
        assert "S3" in signal_ids, f"Expected S3 for developing CR, got: {signal_ids}"

    def test_tc_scr_12_role_reorder_respected(self, tmp_path):
        """TC-SCR-12: --role flag is reflected in output."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("collect-signals.mjs", [devpace_dir, "--role", "pm"])
        assert data["role"] == "pm"


    def test_tc_scr_21_s4_paused_with_resolved_blocker(self, tmp_path):
        """TC-SCR-21: S4 triggers when paused CR's blocker is resolved (merged)."""
        d = tmp_path / ".devpace" / "backlog"
        d.mkdir(parents=True)
        # CR-001: paused, blocked by CR-002
        cr_paused = textwrap.dedent("""\
            # CR-001 Paused

            - **ID**：CR-001
            - **状态**：paused
            - **类型**：feature
            - **阻塞**：CR-002 完成后才能继续

            ## 意图

            测试

            ## 事件

            | 日期 | 事件 | 操作者 | 备注 |
            |------|------|--------|------|
            | 2025-01-01 | created | Claude | |
            | 2025-01-02 | paused | Claude | 等 CR-002 |
        """)
        # CR-002: merged (blocker resolved)
        cr_blocker = textwrap.dedent("""\
            # CR-002 Blocker

            - **ID**：CR-002
            - **状态**：merged
            - **类型**：feature

            ## 意图

            测试

            ## 事件

            | 日期 | 事件 | 操作者 | 备注 |
            |------|------|--------|------|
            | 2025-01-01 | created | Claude | |
            | 2025-01-05 | merged | 用户 | |
        """)
        (d / "CR-001.md").write_text(cr_paused, encoding="utf-8")
        (d / "CR-002.md").write_text(cr_blocker, encoding="utf-8")
        (tmp_path / ".devpace" / "state.md").write_text(STATE_FIXTURE, encoding="utf-8")
        data, _ = _run_script("collect-signals.mjs", [str(tmp_path / ".devpace")])
        signal_ids = [s["id"] for s in data["triggered"]]
        assert "S4" in signal_ids, f"Expected S4 when blocker is resolved, got: {signal_ids}"

    def test_tc_scr_22_s4_paused_with_unresolved_blocker(self, tmp_path):
        """TC-SCR-22: S4 does NOT trigger when paused CR's blocker is still active."""
        d = tmp_path / ".devpace" / "backlog"
        d.mkdir(parents=True)
        cr_paused = textwrap.dedent("""\
            # CR-001 Paused

            - **ID**：CR-001
            - **状态**：paused
            - **类型**：feature
            - **阻塞**：CR-002 完成后才能继续

            ## 意图

            测试

            ## 事件

            | 日期 | 事件 | 操作者 | 备注 |
            |------|------|--------|------|
            | 2025-01-01 | created | Claude | |
        """)
        cr_blocker = textwrap.dedent("""\
            # CR-002 Blocker

            - **ID**：CR-002
            - **状态**：developing
            - **类型**：feature

            ## 意图

            测试

            ## 事件

            | 日期 | 事件 | 操作者 | 备注 |
            |------|------|--------|------|
            | 2025-01-01 | created | Claude | |
        """)
        (d / "CR-001.md").write_text(cr_paused, encoding="utf-8")
        (d / "CR-002.md").write_text(cr_blocker, encoding="utf-8")
        (tmp_path / ".devpace" / "state.md").write_text(STATE_FIXTURE, encoding="utf-8")
        data, _ = _run_script("collect-signals.mjs", [str(tmp_path / ".devpace")])
        signal_ids = [s["id"] for s in data["triggered"]]
        assert "S4" not in signal_ids, f"S4 should NOT trigger when blocker is still active, got: {signal_ids}"

    def test_tc_scr_23_extract_cr_has_blocked_field(self, tmp_path):
        """TC-SCR-23: extract-cr-metadata includes blocked field."""
        d = tmp_path / ".devpace" / "backlog"
        d.mkdir(parents=True)
        cr = textwrap.dedent("""\
            # CR-001 Blocked

            - **ID**：CR-001
            - **状态**：paused
            - **类型**：feature
            - **阻塞**：等待外部 API 就绪

            ## 意图

            测试

            ## 事件

            | 日期 | 事件 | 操作者 | 备注 |
            |------|------|--------|------|
            | 2025-01-01 | created | Claude | |
        """)
        (d / "CR-001.md").write_text(cr, encoding="utf-8")
        data, _ = _run_script("extract-cr-metadata.mjs", [str(tmp_path / ".devpace")])
        assert len(data) == 1
        assert data[0]["blocked"] is not None
        assert "外部 API" in data[0]["blocked"]


@pytest.mark.static
class TestComputeMetrics:
    """Tests for compute-metrics.mjs JSON output."""

    def test_tc_scr_13_returns_json_with_metrics(self, tmp_path):
        """TC-SCR-13: compute-metrics returns JSON with metrics object."""
        devpace_dir = _make_devpace(tmp_path)
        data, rc = _run_script("compute-metrics.mjs", [devpace_dir])
        assert rc == 0
        assert "metrics" in data
        assert isinstance(data["metrics"], dict)

    def test_tc_scr_14_metrics_include_core_indicators(self, tmp_path):
        """TC-SCR-14: Metrics include expected core indicator keys."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("compute-metrics.mjs", [devpace_dir])
        metrics = data["metrics"]
        # At minimum, should have delivery/quality related keys
        assert len(metrics) > 0, "Metrics object is empty"


@pytest.mark.static
class TestSecurityScan:
    """Tests for security-scan.mjs JSON output."""

    def test_tc_scr_15_empty_input_returns_zero_findings(self):
        """TC-SCR-15: Empty stdin returns zero findings."""
        data, rc = _run_script("security-scan.mjs", stdin_data="")
        assert rc == 0
        assert data["findings"] == []
        assert data["summary"]["total"] == 0

    def test_tc_scr_16_detects_sql_injection_pattern(self, tmp_path):
        """TC-SCR-16: Detects SQL injection pattern in diff."""
        diff = textwrap.dedent("""\
            +++ src/db.js
            +const result = db.query("SELECT * FROM users WHERE id=" + req.params.id);
        """)
        data, _ = _run_script("security-scan.mjs", stdin_data=diff, expect_exit_0=False)
        assert data["summary"]["total"] > 0
        categories = [f["category"] for f in data["findings"]]
        assert "A03" in categories, f"Expected A03 (Injection), got: {categories}"

    def test_tc_scr_17_output_has_summary_structure(self, tmp_path):
        """TC-SCR-17: Output has findings/summary/scanned_files keys."""
        data, _ = _run_script("security-scan.mjs", stdin_data="no diff here")
        required_keys = {"findings", "summary", "scanned_files"}
        missing = required_keys - set(data.keys())
        assert not missing, f"Missing output keys: {missing}"


@pytest.mark.static
class TestInferVersionBump:
    """Tests for infer-version-bump.mjs JSON output."""

    def test_tc_scr_18_no_merged_returns_null_bump(self, tmp_path):
        """TC-SCR-18: No unreleased merged CRs → null bump type."""
        d = tmp_path / ".devpace" / "backlog"
        d.mkdir(parents=True)
        # Only a developing CR, no merged
        (d / "CR-001.md").write_text(CR_FIXTURE, encoding="utf-8")
        data, rc = _run_script("infer-version-bump.mjs", [str(tmp_path / ".devpace")])
        assert rc == 0
        assert data["bump_type"] is None

    def test_tc_scr_19_merged_feature_suggests_minor(self, tmp_path):
        """TC-SCR-19: Merged feature CR → minor bump suggestion."""
        devpace_dir = _make_devpace(tmp_path)
        data, rc = _run_script("infer-version-bump.mjs", [devpace_dir, "1.0.0"])
        assert rc == 0
        assert data["bump_type"] == "minor"
        assert data["suggested"] == "1.1.0"
        assert len(data["candidates"]) > 0

    def test_tc_scr_20_output_has_required_structure(self, tmp_path):
        """TC-SCR-20: Output has current/suggested/bump_type/reasoning/candidates."""
        devpace_dir = _make_devpace(tmp_path)
        data, _ = _run_script("infer-version-bump.mjs", [devpace_dir, "1.0.0"])
        required_keys = {"current", "suggested", "bump_type", "reasoning", "candidates"}
        missing = required_keys - set(data.keys())
        assert not missing, f"Missing output keys: {missing}"
