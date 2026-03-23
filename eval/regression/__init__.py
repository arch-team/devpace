"""eval.regression — regression detection + baseline management.

Re-exports key symbols for CLI consumption.
"""
from .detect import detect_changed_skills, run_regress
from .baseline import diff_baseline, save_baseline
