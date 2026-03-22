"""With/without baseline comparison for behavioral evaluations.

Runs each eval case twice — once with the devpace plugin loaded and once
without — then grades both and computes comparative statistics.

This measures the plugin's *value*: how much better does Claude perform
on devpace-managed tasks when the plugin is active?
"""
from __future__ import annotations

import asyncio
import json
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from eval.behavior.execute import (
    DEVPACE_ROOT,
    BehavioralResult,
    run_behavioral_eval,
    _resolve_fixture_dir,
)
from eval.behavior.grader import Grader, grade_eval_case
from eval.core.results import results_dir_for

DEFAULT_RUNS_PER_CASE = 3
DEFAULT_BENCHMARK_TIMEOUT = 600  # longer for benchmark pairs


@dataclass
class ConfigResult:
    """Aggregated results for one configuration (with or without plugin)."""
    pass_rates: list[float] = field(default_factory=list)
    durations: list[float] = field(default_factory=list)
    tokens: list[int] = field(default_factory=list)
    g1_passed: int = 0
    g1_total: int = 0
    g2_passed: int = 0
    g2_total: int = 0
    g3_passed: int = 0
    g3_total: int = 0

    def to_dict(self) -> dict:
        def _stats(values: list[float]) -> dict:
            if not values:
                return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}
            m = statistics.mean(values)
            s = statistics.stdev(values) if len(values) > 1 else 0.0
            return {
                "mean": round(m, 3),
                "stddev": round(s, 3),
                "min": round(min(values), 3),
                "max": round(max(values), 3),
            }

        return {
            "pass_rate": _stats(self.pass_rates),
            "duration": _stats(self.durations),
            "tokens": _stats([float(t) for t in self.tokens]),
            "g1_pass_rate": round(self.g1_passed / max(self.g1_total, 1), 3),
            "g2_pass_rate": round(self.g2_passed / max(self.g2_total, 1), 3),
            "g3_pass_rate": round(self.g3_passed / max(self.g3_total, 1), 3),
        }


@dataclass
class BenchmarkResult:
    """Full benchmark comparison result."""
    skill_name: str
    with_plugin: ConfigResult = field(default_factory=ConfigResult)
    without_plugin: ConfigResult = field(default_factory=ConfigResult)
    case_details: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        wp = self.with_plugin.to_dict()
        wo = self.without_plugin.to_dict()

        # Compute delta
        delta_pass = wp["pass_rate"]["mean"] - wo["pass_rate"]["mean"]
        wo_dur = wo["duration"]["mean"]
        token_overhead = (
            (wp["duration"]["mean"] - wo_dur) / wo_dur
            if wo_dur > 0 else 0.0
        )

        return {
            "skill": self.skill_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "configurations": {
                "with_plugin": wp,
                "without_plugin": wo,
                "delta": {
                    "pass_rate": f"+{delta_pass:.3f}" if delta_pass >= 0 else f"{delta_pass:.3f}",
                    "token_overhead": f"{token_overhead:+.1%}",
                },
            },
            "case_details": self.case_details,
        }


def _accumulate_grades(config: ConfigResult, grading_output: dict) -> None:
    """Accumulate grade-level stats from a grading output."""
    by_grade = grading_output.get("summary", {}).get("by_grade", {})
    for level, stats in by_grade.items():
        total = stats.get("total", 0)
        passed = stats.get("passed", 0)
        if level == "G1":
            config.g1_total += total
            config.g1_passed += passed
        elif level == "G2":
            config.g2_total += total
            config.g2_passed += passed
        elif level == "G3":
            config.g3_total += total
            config.g3_passed += passed


async def _run_single_benchmark(
    skill_name: str,
    eval_case: dict,
    fixture_dir: Path,
    grader: Grader,
    with_plugins: bool,
    timeout: int,
    model: str | None,
    max_turns: int,
) -> tuple[BehavioralResult, dict]:
    """Run a single eval and grade it. Reuses run_behavioral_eval."""
    plugins = (
        [{"type": "local", "path": str(DEVPACE_ROOT)}]
        if with_plugins
        else []
    )

    result = await run_behavioral_eval(
        skill_name=skill_name,
        eval_case=eval_case,
        fixture_dir=fixture_dir,
        timeout=timeout,
        model=model,
        max_turns=max_turns,
        plugins=plugins,
    )

    grading_output = grade_eval_case(grader, eval_case, result)
    return result, grading_output


async def run_benchmark(
    skill_name: str,
    eval_cases: list[dict],
    runs_per_case: int = DEFAULT_RUNS_PER_CASE,
    timeout: int = DEFAULT_BENCHMARK_TIMEOUT,
    model: str | None = None,
    max_turns: int = 20,
    case_ids: list[int] | None = None,
    concurrency: int = 2,
) -> BenchmarkResult:
    """Run with/without benchmark comparison.

    For each eval case, runs `runs_per_case` times with and without the plugin,
    grades each run, and aggregates statistics.
    """
    grader = Grader()
    benchmark = BenchmarkResult(skill_name=skill_name)

    # Filter cases
    cases = eval_cases
    if case_ids:
        cases = [c for c in eval_cases if c["id"] in case_ids]

    # Pre-resolve fixtures
    env_names = {c.get("env", "ENV-DEV-A") for c in cases}
    fixture_dirs = {env: _resolve_fixture_dir(env) for env in env_names}

    sem = asyncio.Semaphore(concurrency)

    async def _bounded_run(case, fixture_dir, with_plugins, run_idx):
        async with sem:
            return await asyncio.wait_for(
                _run_single_benchmark(
                    skill_name, case, fixture_dir, grader,
                    with_plugins=with_plugins, timeout=timeout,
                    model=model, max_turns=max_turns,
                ),
                timeout=timeout + 30,
            )

    for case in cases:
        env = case.get("env", "ENV-DEV-A")
        fixture_dir = fixture_dirs[env]
        case_detail: dict = {
            "eval_id": case["id"],
            "eval_name": case["name"],
            "with_runs": [],
            "without_runs": [],
        }

        # Launch all runs for this case concurrently
        with_tasks = [
            _bounded_run(case, fixture_dir, True, i)
            for i in range(runs_per_case)
        ]
        without_tasks = [
            _bounded_run(case, fixture_dir, False, i)
            for i in range(runs_per_case)
        ]
        all_results = await asyncio.gather(
            *with_tasks, *without_tasks, return_exceptions=True
        )

        with_results = all_results[:runs_per_case]
        without_results = all_results[runs_per_case:]

        for run_idx, r in enumerate(with_results):
            if isinstance(r, Exception):
                case_detail["with_runs"].append({"run": run_idx, "error": str(r)})
                continue
            w_result, w_grading = r
            w_summary = w_grading["summary"]
            w_pass_rate = w_summary["passed"] / max(w_summary["total"], 1)
            benchmark.with_plugin.pass_rates.append(w_pass_rate)
            benchmark.with_plugin.durations.append(w_result.duration_seconds)
            benchmark.with_plugin.tokens.append(w_result.total_tokens)
            _accumulate_grades(benchmark.with_plugin, w_grading)
            case_detail["with_runs"].append({
                "run": run_idx,
                "pass_rate": w_pass_rate,
                "duration": w_result.duration_seconds,
            })

        for run_idx, r in enumerate(without_results):
            if isinstance(r, Exception):
                case_detail["without_runs"].append({"run": run_idx, "error": str(r)})
                continue
            wo_result, wo_grading = r
            wo_summary = wo_grading["summary"]
            wo_pass_rate = wo_summary["passed"] / max(wo_summary["total"], 1)
            benchmark.without_plugin.pass_rates.append(wo_pass_rate)
            benchmark.without_plugin.durations.append(wo_result.duration_seconds)
            benchmark.without_plugin.tokens.append(wo_result.total_tokens)
            _accumulate_grades(benchmark.without_plugin, wo_grading)
            case_detail["without_runs"].append({
                "run": run_idx,
                "pass_rate": wo_pass_rate,
                "duration": wo_result.duration_seconds,
            })

        benchmark.case_details.append(case_detail)

    return benchmark


def save_benchmark_results(skill_name: str, benchmark: BenchmarkResult) -> Path:
    """Save benchmark results to benchmark/ directory."""
    rdir = results_dir_for(skill_name)
    bench_dir = rdir / "benchmark"
    bench_dir.mkdir(exist_ok=True)

    out_path = bench_dir / "benchmark.json"
    out_path.write_text(
        json.dumps(benchmark.to_dict(), indent=2, ensure_ascii=False)
    )
    return out_path
