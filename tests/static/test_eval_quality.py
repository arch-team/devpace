"""TC-EQ: Eval trigger-evals.json quality gates.

Ensures eval test sets have sufficient coverage to produce meaningful
trigger accuracy measurements:
- TC-EQ-01: minimum total cases
- TC-EQ-02: minimum positive cases (should_trigger=true)
- TC-EQ-03: minimum negative cases (should_trigger=false)
- TC-EQ-04: positive ratio balance (prevent skewed sets)
"""
import json

import pytest

from tests.conftest import DEVPACE_ROOT, SKILL_NAMES

EVAL_DIR = DEVPACE_ROOT / "tests" / "evaluation"

MIN_TOTAL = 15
MIN_POSITIVE = 8
MIN_NEGATIVE = 5
POSITIVE_RATIO_MIN = 0.4
POSITIVE_RATIO_MAX = 0.7


def _load_trigger_evals(skill_name):
    """Load trigger-evals.json for a skill, return (positive_count, negative_count) or None."""
    path = EVAL_DIR / skill_name / "trigger-evals.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    pos = sum(1 for e in data if e.get("should_trigger", False))
    neg = sum(1 for e in data if not e.get("should_trigger", False))
    return pos, neg


def _skills_with_evals():
    """Return list of (skill_name, pos, neg) for skills that have trigger-evals.json."""
    results = []
    for name in SKILL_NAMES:
        counts = _load_trigger_evals(name)
        if counts:
            results.append((name, counts[0], counts[1]))
    return results


_EVAL_DATA = _skills_with_evals()
_EVAL_IDS = [name for name, _, _ in _EVAL_DATA]


@pytest.mark.static
class TestEvalQuality:
    """Eval test set quality gates."""

    @pytest.mark.parametrize("name,pos,neg", _EVAL_DATA, ids=_EVAL_IDS)
    def test_tc_eq_01_min_total(self, name, pos, neg):
        """TC-EQ-01: trigger-evals.json has >= 15 total cases."""
        total = pos + neg
        assert total >= MIN_TOTAL, (
            f"{name}: {total} eval cases (min {MIN_TOTAL}). "
            f"ACTION: Add {MIN_TOTAL - total} more cases to tests/evaluation/{name}/trigger-evals.json."
        )

    @pytest.mark.parametrize("name,pos,neg", _EVAL_DATA, ids=_EVAL_IDS)
    def test_tc_eq_02_min_positive(self, name, pos, neg):
        """TC-EQ-02: trigger-evals.json has >= 8 positive (should_trigger=true) cases."""
        assert pos >= MIN_POSITIVE, (
            f"{name}: {pos} positive cases (min {MIN_POSITIVE}). "
            f"ACTION: Add {MIN_POSITIVE - pos} more should_trigger:true cases."
        )

    @pytest.mark.parametrize("name,pos,neg", _EVAL_DATA, ids=_EVAL_IDS)
    def test_tc_eq_03_min_negative(self, name, pos, neg):
        """TC-EQ-03: trigger-evals.json has >= 5 negative (should_trigger=false) cases."""
        assert neg >= MIN_NEGATIVE, (
            f"{name}: {neg} negative cases (min {MIN_NEGATIVE}). "
            f"ACTION: Add {MIN_NEGATIVE - neg} more should_trigger:false cases."
        )

    @pytest.mark.parametrize("name,pos,neg", _EVAL_DATA, ids=_EVAL_IDS)
    def test_tc_eq_04_ratio_balanced(self, name, pos, neg):
        """TC-EQ-04: positive ratio between 40%-70% (prevent skewed eval sets)."""
        total = pos + neg
        if total == 0:
            pytest.skip(f"{name} has no eval cases")
        ratio = pos / total
        assert POSITIVE_RATIO_MIN <= ratio <= POSITIVE_RATIO_MAX, (
            f"{name}: positive ratio {ratio:.0%} (expected {POSITIVE_RATIO_MIN:.0%}-{POSITIVE_RATIO_MAX:.0%}). "
            f"ACTION: Rebalance by adding {'negative' if ratio > POSITIVE_RATIO_MAX else 'positive'} cases."
        )
