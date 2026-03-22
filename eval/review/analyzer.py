"""Assertion quality analysis — statistical detection of problematic assertions.

Analyzes multiple eval runs to detect non-discriminating, always-failing,
high-variance, and redundant assertions. Consumes feedback notes when available.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .feedback import EvalNote


@dataclass
class AssertionIssue:
    """A detected quality issue for a specific assertion."""
    skill: str
    eval_id: int
    eval_name: str
    assertion_idx: int
    assertion_text: str
    issue_type: str  # non_discriminating | always_failing | high_variance | redundant | feedback_flagged
    detail: str
    severity: str  # low | medium | high


@dataclass
class AnalysisReport:
    """Complete assertion quality analysis report."""
    total_assertions: int = 0
    total_runs: int = 0
    issues: list[AssertionIssue] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def issues_by_type(self, issue_type: str) -> list[AssertionIssue]:
        return [i for i in self.issues if i.issue_type == issue_type]


def _extract_assertion_pass_matrix(
    behavior_results: list[dict],
) -> dict[tuple[str, int, int], list[bool]]:
    """Build a matrix of (skill, eval_id, assertion_idx) -> [pass/fail per run].

    Each entry in behavior_results is a grading.json-style dict with a
    ``cases`` list. Each case has ``assertions`` with a ``pass`` bool.
    """
    matrix: dict[tuple[str, int, int], list[bool]] = {}
    for run_result in behavior_results:
        skill = run_result.get("skill", "unknown")
        for case in run_result.get("cases", []):
            eval_id = case.get("id", 0)
            for idx, a in enumerate(case.get("assertions", [])):
                key = (skill, eval_id, idx)
                matrix.setdefault(key, [])
                matrix[key].append(bool(a.get("pass", False)))
    return matrix


def _extract_benchmark_pass_rates(
    benchmark_results: dict,
) -> dict[tuple[str, int, int], dict[str, float]]:
    """Extract per-assertion pass rates from benchmark with/without data.

    Returns {(skill, eval_id, assertion_idx): {"with": rate, "without": rate}}.
    """
    rates: dict[tuple[str, int, int], dict[str, float]] = {}
    for config_key in ("with_plugin", "without_plugin"):
        config = benchmark_results.get("configurations", {}).get(config_key, {})
        per_assertion = config.get("per_assertion", {})
        label = "with" if "with" in config_key else "without"
        for key_str, rate in per_assertion.items():
            # key_str format: "skill:eval_id:assertion_idx"
            parts = key_str.split(":")
            if len(parts) == 3:
                try:
                    k = (parts[0], int(parts[1]), int(parts[2]))
                    rates.setdefault(k, {})
                    rates[k][label] = float(rate)
                except (ValueError, TypeError):
                    pass
    return rates


def analyze_assertion_quality(
    behavior_results: list[dict],
    benchmark_results: dict | None = None,
    notes: list[EvalNote] | None = None,
) -> AnalysisReport:
    """Analyze assertion quality across multiple eval runs.

    Detection dimensions:
    1. Non-discriminating: with/without both 100% pass (needs benchmark data)
    2. Always-failing: 0% pass across all runs
    3. High-variance: 30-70% pass rate (flaky)
    4. Redundant: two assertions always pass/fail in sync
    5. Feedback-flagged: notes with note_type=assertion_issue
    """
    report = AnalysisReport()
    report.total_runs = len(behavior_results)

    if not behavior_results:
        return report

    # Build pass matrix
    matrix = _extract_assertion_pass_matrix(behavior_results)
    report.total_assertions = len(matrix)

    # Extract assertion text from first run for reporting
    text_map: dict[tuple[str, int, int], tuple[str, str]] = {}  # key -> (eval_name, text)
    first_run = behavior_results[0]
    skill = first_run.get("skill", "unknown")
    for case in first_run.get("cases", []):
        eval_id = case.get("id", 0)
        eval_name = case.get("name", f"case-{eval_id}")
        for idx, a in enumerate(case.get("assertions", [])):
            text_map[(skill, eval_id, idx)] = (
                eval_name,
                a.get("text", a.get("assertion", f"assertion-{idx}")),
            )

    # --- Detection 1: Non-discriminating (needs benchmark) ---
    if benchmark_results:
        bench_rates = _extract_benchmark_pass_rates(benchmark_results)
        for key, rates in bench_rates.items():
            wp = rates.get("with", 0.0)
            wop = rates.get("without", 0.0)
            if wp >= 1.0 and wop >= 1.0:
                name, text = text_map.get(key, ("?", "?"))
                report.issues.append(AssertionIssue(
                    skill=key[0],
                    eval_id=key[1],
                    eval_name=name,
                    assertion_idx=key[2],
                    assertion_text=text,
                    issue_type="non_discriminating",
                    detail="Both with_plugin (100%) and without_plugin (100%) pass. "
                           "This assertion tests baseline capability, not Skill value.",
                    severity="medium",
                ))

    # --- Detection 2: Always-failing ---
    for key, passes in matrix.items():
        if len(passes) >= 2 and not any(passes):
            name, text = text_map.get(key, ("?", "?"))
            report.issues.append(AssertionIssue(
                skill=key[0],
                eval_id=key[1],
                eval_name=name,
                assertion_idx=key[2],
                assertion_text=text,
                issue_type="always_failing",
                detail=f"0% pass across {len(passes)} runs. "
                       "Assertion may be broken or feature not implemented.",
                severity="high",
            ))

    # --- Detection 3: High-variance ---
    for key, passes in matrix.items():
        if len(passes) < 2:
            continue
        rate = sum(passes) / len(passes)
        if 0.3 <= rate <= 0.7:
            name, text = text_map.get(key, ("?", "?"))
            report.issues.append(AssertionIssue(
                skill=key[0],
                eval_id=key[1],
                eval_name=name,
                assertion_idx=key[2],
                assertion_text=text,
                issue_type="high_variance",
                detail=f"Pass rate {rate:.0%} across {len(passes)} runs. "
                       "Assertion may be flaky or need more precise criteria.",
                severity="medium",
            ))

    # --- Detection 4: Redundant (perfectly correlated pairs) ---
    keys = sorted(matrix.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            # Only check within same eval case
            if keys[i][0] != keys[j][0] or keys[i][1] != keys[j][1]:
                continue
            passes_i = matrix[keys[i]]
            passes_j = matrix[keys[j]]
            min_len = min(len(passes_i), len(passes_j))
            if min_len < 2:
                continue
            if passes_i[:min_len] == passes_j[:min_len]:
                name_j, text_j = text_map.get(keys[j], ("?", "?"))
                _, text_i = text_map.get(keys[i], ("?", "?"))
                report.issues.append(AssertionIssue(
                    skill=keys[j][0],
                    eval_id=keys[j][1],
                    eval_name=name_j,
                    assertion_idx=keys[j][2],
                    assertion_text=text_j,
                    issue_type="redundant",
                    detail=f"Perfectly correlated with assertion #{keys[i][2]} "
                           f"({text_i!r}) across {min_len} runs. Consider merging.",
                    severity="low",
                ))

    # --- Detection 5: Feedback-flagged ---
    if notes:
        for n in notes:
            if n.note_type == "assertion_issue" and not n.resolved:
                key = (n.skill, n.eval_id, n.assertion_idx or 0)
                name, text = text_map.get(key, (n.eval_name, "?"))
                report.issues.append(AssertionIssue(
                    skill=n.skill,
                    eval_id=n.eval_id,
                    eval_name=name,
                    assertion_idx=n.assertion_idx or 0,
                    assertion_text=text,
                    issue_type="feedback_flagged",
                    detail=f"Human feedback: {n.note}",
                    severity="medium",
                ))

    # Build summary
    for issue in report.issues:
        report.summary[issue.issue_type] = report.summary.get(issue.issue_type, 0) + 1

    return report
