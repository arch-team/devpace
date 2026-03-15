"""Multi-dimensional regression detection (P3.1).

Compares baseline vs latest results across multiple metrics:
- Positive trigger rate drop
- False positive increase
- False negative increase
- Overall pass rate drop

Also includes change detection (P3.2) for selective eval.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .results import DEVPACE_ROOT, EVAL_DATA_DIR

# Regression thresholds
THRESHOLDS = {
    "positive_trigger_rate_drop": {"warning": 0.10, "failure": 0.20},
    "false_positive_increase": {"warning": 1, "failure": 1},  # any new false positive is warning+failure
    "false_negative_increase": {"warning": 2, "failure": 4},
    "overall_pass_rate_drop": {"warning": 0.05, "failure": 0.15},
}


def _compute_metrics(baseline: dict, latest: dict) -> dict:
    """Compute regression metrics between baseline and latest."""
    bl_s, lt_s = baseline["summary"], latest["summary"]

    bl_total = max(bl_s.get("total", 0), 1)
    lt_total = max(lt_s.get("total", 0), 1)

    bl_rate = bl_s.get("passed", 0) / bl_total
    lt_rate = lt_s.get("passed", 0) / lt_total

    # Positive trigger rate
    bl_pos = baseline.get("positive", {})
    lt_pos = latest.get("positive", {})
    bl_pos_total = max(bl_pos.get("total", 0), 1)
    lt_pos_total = max(lt_pos.get("total", 0), 1)
    bl_pos_rate = bl_pos.get("passed", 0) / bl_pos_total
    lt_pos_rate = lt_pos.get("passed", 0) / lt_pos_total

    # False negatives and false positives
    bl_fn = len(baseline.get("false_negatives", []))
    lt_fn = len(latest.get("false_negatives", []))
    bl_fp = len(baseline.get("false_positives", []))
    lt_fp = len(latest.get("false_positives", []))

    return {
        "positive_trigger_rate_drop": round(bl_pos_rate - lt_pos_rate, 4),
        "false_positive_increase": lt_fp - bl_fp,
        "false_negative_increase": lt_fn - bl_fn,
        "overall_pass_rate_drop": round(bl_rate - lt_rate, 4),
        "baseline_rate": bl_rate,
        "latest_rate": lt_rate,
        "baseline_pos_rate": bl_pos_rate,
        "latest_pos_rate": lt_pos_rate,
    }


def _classify(metric_name: str, value: float | int) -> str:
    """Classify a metric value as OK/WARNING/FAILURE."""
    t = THRESHOLDS.get(metric_name, {})
    failure = t.get("failure", float("inf"))
    warning = t.get("warning", float("inf"))

    if value >= failure:
        return "FAILURE"
    if value >= warning:
        return "WARNING"
    return "OK"


def run_regress(threshold: float = 0.1) -> int:
    """Check for regressions across all skills with baselines.

    Returns exit code: 0 if no failures, 1 if any FAILURE-level regression.
    """
    any_fail = False
    report: dict = {"skills": {}, "overall": "OK"}

    for d in sorted(EVAL_DATA_DIR.iterdir()):
        if d.name.startswith("_") or not d.is_dir():
            continue

        bl_path = d / "results" / "baseline.json"
        lt_path = d / "results" / "latest.json"
        if not bl_path.exists() or not lt_path.exists():
            continue

        bl = json.loads(bl_path.read_text())
        lt = json.loads(lt_path.read_text())
        metrics = _compute_metrics(bl, lt)

        # Classify each metric
        classifications = {}
        skill_fail = False
        skill_warn = False

        for metric_name in THRESHOLDS:
            val = metrics.get(metric_name, 0)
            cls = _classify(metric_name, val)
            classifications[metric_name] = {"value": val, "level": cls}
            if cls == "FAILURE":
                skill_fail = True
            elif cls == "WARNING":
                skill_warn = True

        # Determine per-query regressions
        bl_results = {r["query"]: r for r in bl.get("raw_results", [])}
        lt_results = {r["query"]: r for r in lt.get("raw_results", [])}
        new_failures = []
        for q, lt_r in lt_results.items():
            bl_r = bl_results.get(q)
            if bl_r and bl_r.get("pass") and not lt_r.get("pass"):
                new_failures.append(q)

        skill_status = "FAILURE" if skill_fail else ("WARNING" if skill_warn else "OK")
        report["skills"][d.name] = {
            "status": skill_status,
            "metrics": classifications,
            "baseline_rate": f"{metrics['baseline_rate']:.0%}",
            "latest_rate": f"{metrics['latest_rate']:.0%}",
            "new_failures": new_failures,
        }

        if skill_fail:
            any_fail = True
            print(f"  FAILURE {d.name}: {metrics['baseline_rate']:.0%} -> {metrics['latest_rate']:.0%}")
            for mn, mc in classifications.items():
                if mc["level"] != "OK":
                    print(f"    {mc['level']} {mn}: {mc['value']}")
        elif skill_warn:
            print(f"  WARNING {d.name}: {metrics['baseline_rate']:.0%} -> {metrics['latest_rate']:.0%}")
        else:
            print(f"  OK {d.name}: {metrics['baseline_rate']:.0%} -> {metrics['latest_rate']:.0%}")

    report["overall"] = "FAILURE" if any_fail else "OK"

    # Write report
    report_dir = EVAL_DATA_DIR / "regress"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "latest-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n  report: {report_path.relative_to(DEVPACE_ROOT)}")

    return 1 if any_fail else 0


def detect_changed_skills(base_ref: str = "origin/main") -> list[str]:
    """Detect skills changed relative to base_ref using git diff (P3.2).

    Returns list of skill names that have changes.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref, "--", "skills/"],
            capture_output=True, text=True, timeout=10,
            cwd=str(DEVPACE_ROOT),
        )
        if result.returncode != 0:
            return []

        changed = set()
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("/")
            if len(parts) >= 2 and parts[0] == "skills":
                changed.add(parts[1])
        return sorted(changed)
    except Exception:
        return []


def get_sibling_skills(skill_name: str) -> list[str]:
    """Get 'sibling' skills that might be affected by a skill's changes.

    For example, pace-dev changes should also check pace-change (similar triggers).
    """
    siblings_map = {
        "pace-dev": ["pace-change", "pace-test"],
        "pace-change": ["pace-dev", "pace-biz"],
        "pace-review": ["pace-test", "pace-guard"],
        "pace-test": ["pace-review", "pace-dev"],
        "pace-status": ["pace-next", "pace-pulse"],
        "pace-next": ["pace-status"],
        "pace-init": ["pace-biz"],
        "pace-biz": ["pace-init", "pace-change"],
    }
    return siblings_map.get(skill_name, [])
