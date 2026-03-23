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

from eval.cli import main


if __name__ == "__main__":
    sys.exit(main())
