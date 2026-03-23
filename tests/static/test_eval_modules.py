"""TC-EVAL: Unit tests for eval package modules.

Tests skill_io, results, regress, baseline, and loop utilities
without requiring Agent SDK or API calls.
"""
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from tests.conftest import DEVPACE_ROOT


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_skill(tmp_path):
    """Create a temporary skill directory with a SKILL.md."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "description: Use when user says \"test\" or \"check\"\n"
        "allowed-tools: Read, Write\n"
        "---\n"
        "\n"
        "# /test-skill\n"
        "Test skill body.\n"
    )
    return skill_dir


@pytest.fixture
def tmp_skill_multiline(tmp_path):
    """Create a skill with multi-line folded description."""
    skill_dir = tmp_path / "multi-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "description: >\n"
        "  Use when user says \"build\" or \"create\"\n"
        "  or wants to start a new project.\n"
        "  NOT for existing project changes.\n"
        "allowed-tools: Read\n"
        "---\n"
        "\n"
        "# /multi-skill\n"
    )
    return skill_dir


@pytest.fixture
def tmp_results_dir(tmp_path):
    """Create a temporary results directory structure."""
    rdir = tmp_path / "results"
    rdir.mkdir()
    (rdir / "history").mkdir()
    (rdir / "loop").mkdir()
    return rdir


# ---------------------------------------------------------------------------
# TC-EVAL-IO: skill_io module
# ---------------------------------------------------------------------------

@pytest.mark.static
class TestSkillIO:
    def test_read_description_inline(self, tmp_skill):
        """TC-EVAL-IO-01: Read inline description."""
        from eval.core.skill_io import read_description
        desc = read_description(tmp_skill)
        assert desc == 'Use when user says "test" or "check"'

    def test_read_description_multiline(self, tmp_skill_multiline):
        """TC-EVAL-IO-02: Read multi-line folded description."""
        from eval.core.skill_io import read_description
        desc = read_description(tmp_skill_multiline)
        assert "build" in desc
        assert "create" in desc
        assert "NOT for existing" in desc

    def test_description_hash_deterministic(self, tmp_skill):
        """TC-EVAL-IO-03: Hash is deterministic for same description."""
        from eval.core.skill_io import description_hash
        h1 = description_hash(tmp_skill)
        h2 = description_hash(tmp_skill)
        assert h1 == h2
        assert len(h1) == 16

    def test_replace_description_inline(self, tmp_skill):
        """TC-EVAL-IO-04: Replace inline description."""
        from eval.core.skill_io import read_description, replace_description
        skill_md = tmp_skill / "SKILL.md"
        original = replace_description(skill_md, "New description here")
        assert "test" in original  # original content returned
        new_desc = read_description(tmp_skill)
        assert new_desc == "New description here"

    def test_replace_description_long(self, tmp_skill):
        """TC-EVAL-IO-05: Long description uses folded block scalar."""
        from eval.core.skill_io import replace_description
        skill_md = tmp_skill / "SKILL.md"
        long_desc = "Use when " + " ".join(f"word{i}" for i in range(50))
        replace_description(skill_md, long_desc)
        content = skill_md.read_text()
        assert "description: >" in content

    def test_replace_preserves_other_fields(self, tmp_skill):
        """TC-EVAL-IO-06: Replacement preserves other frontmatter fields."""
        from eval.core.skill_io import replace_description
        skill_md = tmp_skill / "SKILL.md"
        replace_description(skill_md, "New desc")
        content = skill_md.read_text()
        assert "allowed-tools: Read, Write" in content

    def test_read_skill_md(self, tmp_skill):
        """TC-EVAL-IO-07: Read full SKILL.md content."""
        from eval.core.skill_io import read_skill_md
        content = read_skill_md(tmp_skill)
        assert "# /test-skill" in content

    def test_read_description_no_description(self, tmp_path):
        """TC-EVAL-IO-08: Returns empty string if no description field."""
        skill_dir = tmp_path / "no-desc"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nallowed-tools: Read\n---\n")
        from eval.core.skill_io import read_description
        assert read_description(skill_dir) == ""


# ---------------------------------------------------------------------------
# TC-EVAL-RES: results module
# ---------------------------------------------------------------------------

@pytest.mark.static
class TestResults:
    def test_build_metadata_basic(self):
        """TC-EVAL-RES-01: Build metadata with defaults."""
        from eval.core.results import build_metadata
        meta = build_metadata(model="test-model", duration_seconds=12.345)
        assert meta["model"] == "test-model"
        assert meta["sdk_options"]["max_turns"] == 5
        assert meta["environment"]["eval_version"] == "0.3.0"
        assert meta["duration_seconds"] == 12.3

    def test_build_metadata_no_model(self):
        """TC-EVAL-RES-02: Build metadata without model."""
        from eval.core.results import build_metadata
        meta = build_metadata()
        assert "model" not in meta
        assert "sdk_options" in meta

    def test_eval_score(self):
        """TC-EVAL-RES-03: Score computation."""
        from eval.core.results import eval_score
        assert eval_score({"summary": {"total": 10, "passed": 8}}) == 0.8
        assert eval_score({"summary": {"total": 0, "passed": 0}}) == 0.0
        assert eval_score({"summary": {"total": 5, "passed": 5}}) == 1.0
        assert eval_score({}) == 0.0

    def test_save_and_load(self, tmp_path):
        """TC-EVAL-RES-04: Save and load results round-trip."""
        from eval.core.results import save_trigger_results, load_results, EVAL_DATA_DIR
        # Patch EVAL_DATA_DIR temporarily
        with patch("eval.core.results.EVAL_DATA_DIR", tmp_path):
            with patch("eval.core.results.SKILLS_DIR", tmp_path):
                # Create fake skill for hash
                fake_skill = tmp_path / "fake"
                fake_skill.mkdir()
                (fake_skill / "SKILL.md").write_text("---\ndescription: test\n---\n")
                with patch("eval.core.results.description_hash", return_value="abc123"):
                    raw = {
                        "summary": {"total": 3, "passed": 2, "failed": 1},
                        "results": [
                            {"query": "q1", "should_trigger": True, "pass": True, "runs": 1},
                            {"query": "q2", "should_trigger": True, "pass": False, "runs": 1},
                            {"query": "q3", "should_trigger": False, "pass": True, "runs": 1},
                        ],
                    }
                    path = save_trigger_results("fake", raw)
                    assert path.exists()
                    data = json.loads(path.read_text())
                    assert data["skill"] == "fake"
                    assert data["summary"]["passed"] == 2
                    assert len(data["false_negatives"]) == 1
                    assert len(data["false_positives"]) == 0


# ---------------------------------------------------------------------------
# TC-EVAL-REG: regress module
# ---------------------------------------------------------------------------

@pytest.mark.static
class TestRegress:
    def test_compute_metrics_no_regression(self):
        """TC-EVAL-REG-01: No regression when latest >= baseline."""
        from eval.regression.detect import _compute_metrics
        baseline = {
            "summary": {"total": 10, "passed": 8},
            "positive": {"total": 7, "passed": 5},
            "false_negatives": [{"id": 0, "query": "q1"}, {"id": 1, "query": "q2"}],
            "false_positives": [],
        }
        latest = {
            "summary": {"total": 10, "passed": 9},
            "positive": {"total": 7, "passed": 6},
            "false_negatives": [{"id": 0, "query": "q1"}],
            "false_positives": [],
        }
        metrics = _compute_metrics(baseline, latest)
        assert metrics["overall_pass_rate_drop"] < 0  # improved
        assert metrics["false_negative_increase"] == -1  # fewer FN

    def test_compute_metrics_regression(self):
        """TC-EVAL-REG-02: Detect regression when latest < baseline."""
        from eval.regression.detect import _compute_metrics
        baseline = {
            "summary": {"total": 10, "passed": 9},
            "positive": {"total": 7, "passed": 7},
            "false_negatives": [],
            "false_positives": [],
        }
        latest = {
            "summary": {"total": 10, "passed": 6},
            "positive": {"total": 7, "passed": 4},
            "false_negatives": [{"id": i, "query": f"q{i}"} for i in range(3)],
            "false_positives": [{"id": 0, "query": "fp1"}],
        }
        metrics = _compute_metrics(baseline, latest)
        assert metrics["overall_pass_rate_drop"] > 0.15  # FAILURE level
        assert metrics["false_negative_increase"] == 3
        assert metrics["false_positive_increase"] == 1

    def test_classify_thresholds(self):
        """TC-EVAL-REG-03: Classification matches expected thresholds."""
        from eval.regression.detect import _classify
        assert _classify("overall_pass_rate_drop", 0.03) == "OK"
        assert _classify("overall_pass_rate_drop", 0.07) == "WARNING"
        assert _classify("overall_pass_rate_drop", 0.20) == "FAILURE"
        assert _classify("false_positive_increase", 0) == "OK"
        assert _classify("false_positive_increase", 1) == "FAILURE"

    def test_sibling_skills(self):
        """TC-EVAL-REG-04: Sibling skill lookup works."""
        from eval.regression.detect import get_sibling_skills
        siblings = get_sibling_skills("pace-dev")
        assert "pace-change" in siblings
        assert get_sibling_skills("nonexistent") == []


# ---------------------------------------------------------------------------
# TC-EVAL-BASE: baseline module
# ---------------------------------------------------------------------------

@pytest.mark.static
class TestBaseline:
    def test_save_baseline(self, tmp_path):
        """TC-EVAL-BASE-01: Save copies latest to baseline."""
        from eval.regression.baseline import save_baseline
        rdir = tmp_path / "test-skill" / "results"
        rdir.mkdir(parents=True)
        (rdir / "latest.json").write_text('{"summary":{"total":5,"passed":4}}')
        with patch("eval.regression.baseline.EVAL_DATA_DIR", tmp_path):
            with patch("eval.regression.baseline.DEVPACE_ROOT", tmp_path.parent):
                rc = save_baseline("test-skill")
        assert rc == 0
        assert (rdir / "baseline.json").exists()
        assert json.loads((rdir / "baseline.json").read_text())["summary"]["passed"] == 4

    def test_save_baseline_no_latest(self, tmp_path):
        """TC-EVAL-BASE-02: Save fails without latest.json."""
        from eval.regression.baseline import save_baseline
        rdir = tmp_path / "test-skill" / "results"
        rdir.mkdir(parents=True)
        with patch("eval.regression.baseline.EVAL_DATA_DIR", tmp_path):
            rc = save_baseline("test-skill")
        assert rc == 1


# ---------------------------------------------------------------------------
# TC-EVAL-SPLIT: train/test split
# ---------------------------------------------------------------------------

@pytest.mark.static
class TestTrainTestSplit:
    def test_split_proportions(self):
        """TC-EVAL-SPLIT-01: Split maintains approximate holdout ratio."""
        from eval.trigger.loop import _split_train_test
        eval_set = [
            {"query": f"pos{i}", "should_trigger": True} for i in range(20)
        ] + [
            {"query": f"neg{i}", "should_trigger": False} for i in range(10)
        ]
        train, test = _split_train_test(eval_set, holdout=0.3, seed=42)
        assert len(train) + len(test) == 30
        assert 8 <= len(test) <= 10  # ~30% of 30

    def test_split_preserves_all_queries(self):
        """TC-EVAL-SPLIT-02: All queries appear in exactly one set."""
        from eval.trigger.loop import _split_train_test
        eval_set = [{"query": f"q{i}", "should_trigger": i < 5} for i in range(10)]
        train, test = _split_train_test(eval_set, holdout=0.3, seed=42)
        all_queries = {e["query"] for e in train} | {e["query"] for e in test}
        assert all_queries == {f"q{i}" for i in range(10)}

    def test_split_deterministic_with_seed(self):
        """TC-EVAL-SPLIT-03: Same seed produces same split."""
        from eval.trigger.loop import _split_train_test
        eval_set = [{"query": f"q{i}", "should_trigger": True} for i in range(20)]
        t1, s1 = _split_train_test(eval_set, holdout=0.3, seed=123)
        t2, s2 = _split_train_test(eval_set, holdout=0.3, seed=123)
        assert [e["query"] for e in t1] == [e["query"] for e in t2]
        assert [e["query"] for e in s1] == [e["query"] for e in s2]

    def test_split_both_sets_have_pos_and_neg(self):
        """TC-EVAL-SPLIT-04: Both sets have positive and negative queries."""
        from eval.trigger.loop import _split_train_test
        eval_set = [
            {"query": f"pos{i}", "should_trigger": True} for i in range(10)
        ] + [
            {"query": f"neg{i}", "should_trigger": False} for i in range(10)
        ]
        train, test = _split_train_test(eval_set, holdout=0.3, seed=42)
        train_pos = sum(1 for e in train if e["should_trigger"])
        train_neg = sum(1 for e in train if not e["should_trigger"])
        test_pos = sum(1 for e in test if e["should_trigger"])
        test_neg = sum(1 for e in test if not e["should_trigger"])
        assert train_pos > 0 and train_neg > 0
        assert test_pos > 0 and test_neg > 0


# ---------------------------------------------------------------------------
# TC-EVAL-TRIGGER: trigger module (unit-level, no SDK calls)
# ---------------------------------------------------------------------------

@pytest.mark.static
class TestTriggerUtils:
    def test_wilson_interval_basic(self):
        """TC-EVAL-TRIG-01: Wilson interval for known proportions."""
        from eval.trigger.detect import _wilson_interval
        lo, hi = _wilson_interval(5, 10)
        assert 0.2 < lo < 0.5
        assert 0.5 < hi < 0.8

    def test_wilson_interval_zero(self):
        """TC-EVAL-TRIG-02: Wilson interval for zero total."""
        from eval.trigger.detect import _wilson_interval
        assert _wilson_interval(0, 0) == (0.0, 0.0)

    def test_wilson_interval_perfect(self):
        """TC-EVAL-TRIG-03: Wilson interval for perfect rate."""
        from eval.trigger.detect import _wilson_interval
        lo, hi = _wilson_interval(10, 10)
        assert lo > 0.6
        assert hi == 1.0 or hi > 0.95


# ---------------------------------------------------------------------------
# TC-EVAL-CLI: CLI module
# ---------------------------------------------------------------------------

@pytest.mark.static
class TestCLI:
    def test_parser_has_all_commands(self):
        """TC-EVAL-CLI-01: Parser has all expected subcommands."""
        from eval.cli import build_parser
        parser = build_parser()
        # Check by parsing known subcommands
        args = parser.parse_args(["trigger", "--skill", "test"])
        assert args.command == "trigger"
        assert args.skill == "test"
        assert args.max_turns == 5  # default

    def test_parser_loop_requires_model(self):
        """TC-EVAL-CLI-02: Loop subcommand requires --model."""
        from eval.cli import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["loop", "--skill", "test"])

    def test_parser_changed_default_base(self):
        """TC-EVAL-CLI-03: Changed subcommand has default base ref."""
        from eval.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["changed"])
        assert args.base == "origin/main"

    def test_parser_loop_holdout(self):
        """TC-EVAL-CLI-04: Loop subcommand accepts --holdout."""
        from eval.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["loop", "--skill", "t", "--model", "m", "--holdout", "0.2"])
        assert args.holdout == 0.2
