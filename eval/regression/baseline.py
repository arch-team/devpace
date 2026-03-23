"""Baseline management for eval results.

Save current results as baselines and compare against them.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from eval.core.results import DEVPACE_ROOT, EVAL_DATA_DIR


def save_baseline(skill_name: str) -> int:
    """Copy latest.json to baseline.json for a skill. Returns exit code."""
    rdir = EVAL_DATA_DIR / skill_name / "results"
    latest = rdir / "latest.json"
    baseline = rdir / "baseline.json"

    if not latest.exists():
        print(f"Error: no latest.json for {skill_name}", file=sys.stderr)
        return 1

    shutil.copy2(latest, baseline)
    print(f"  baseline saved: {baseline.relative_to(DEVPACE_ROOT)}")
    return 0


def diff_baseline(skill_name: str) -> int:
    """Show diff between baseline and latest for a skill. Returns exit code."""
    rdir = EVAL_DATA_DIR / skill_name / "results"
    baseline = rdir / "baseline.json"
    latest = rdir / "latest.json"

    if not baseline.exists() or not latest.exists():
        print(f"Missing baseline or latest for {skill_name}", file=sys.stderr)
        return 1

    bl = json.loads(baseline.read_text())
    lt = json.loads(latest.read_text())
    bl_s, lt_s = bl["summary"], lt["summary"]
    print(
        f"  {skill_name}: baseline {bl_s['passed']}/{bl_s['total']}"
        f" -> latest {lt_s['passed']}/{lt_s['total']}"
    )
    return 0
