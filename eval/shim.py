#!/usr/bin/env python3
"""Eval shim: compatibility wrapper.

This file previously contained the full eval implementation (617 lines).
It now delegates to the modular eval package while maintaining backward
compatibility for existing Makefile targets and scripts.

Usage (unchanged):
  python3 eval/shim.py trigger --skill pace-dev [--runs N] [--timeout T]
  python3 eval/shim.py loop    --skill pace-dev --model MODEL [--iterations N]
  python3 eval/shim.py regress [--threshold 0.1]
  python3 eval/shim.py baseline save --skill pace-dev
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the devpace root (parent of eval/) is on sys.path so that
# `import eval` works when this file is run as `python3 eval/shim.py`.
_DEVPACE_ROOT = str(Path(__file__).resolve().parent.parent)
if _DEVPACE_ROOT not in sys.path:
    sys.path.insert(0, _DEVPACE_ROOT)

# Re-export key functions for any code that imports from shim directly
from eval.skill_io import (  # noqa: F401
    description_hash,
    read_description,
    replace_description as _replace_description_in_file,
)
from eval.results import (  # noqa: F401
    eval_score as _eval_score,
    results_dir_for,
    save_trigger_results,
)
from eval.trigger import (  # noqa: F401
    run_eval_set as _run_eval_set,
    run_single_query as _run_single_query_sdk,
)
from eval.baseline import save_baseline, diff_baseline  # noqa: F401
from eval.regress import run_regress  # noqa: F401
from eval.cli import main


if __name__ == "__main__":
    sys.exit(main())
