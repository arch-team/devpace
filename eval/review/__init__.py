"""eval.review — human review: visualization + feedback + quality analysis.

Modules:
    report    — Static HTML dashboard generator
    viewer    — Interactive eval viewer server
    feedback  — Structured feedback collection (notes.jsonl)
    analyzer  — Assertion quality analysis
"""
from .report import generate_dashboard, write_dashboard
from .viewer import start_viewer
from .feedback import append_note, resolve_note, list_pending, list_stale, list_notes, EvalNote
from .analyzer import analyze_assertion_quality, AnalysisReport, AssertionIssue
