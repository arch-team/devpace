"""eval.trigger — trigger accuracy evaluation + description optimization.

Re-exports key symbols for CLI consumption.
"""
from .detect import DEFAULT_MAX_TURNS, DEFAULT_RUNS, DEFAULT_TIMEOUT, run_eval_set
from .loop import run_loop
