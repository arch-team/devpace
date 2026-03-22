"""eval.behavior — behavioral evaluation: execute, grade, benchmark, compare.

Submodules:
    execute     — Agent SDK execution in fixture environments
    grader      — Mixed G1/G2/G3 grading engine
    benchmark   — With/without baseline comparison (Phase 2)
    comparator  — Blind A/B comparison (Phase 3)
"""
from .execute import (
    DEFAULT_CONCURRENCY,
    DEFAULT_MAX_TURNS,
    DEFAULT_TIMEOUT,
    BehavioralResult,
    ToolCall,
    run_behavioral_eval,
    run_behavioral_eval_set,
    save_behavioral_results,
)
from .grader import (
    Grader,
    GradingResult,
    grade_eval_case,
    save_grading_results,
)
from .benchmark import (
    BenchmarkResult,
    run_benchmark,
    save_benchmark_results,
)
from .comparator import (
    ComparisonResult,
    blind_compare,
    save_comparison_results,
)
