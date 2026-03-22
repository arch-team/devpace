"""Description optimization loop with train/test split (P1.3).

Iteratively improves a skill's description by:
1. Splitting eval queries into train (70%) and test (30%) sets
2. Generating improved descriptions via Anthropic API
3. Evaluating candidates on the train set
4. Validating the best candidate on the test set to detect overfitting
"""
from __future__ import annotations

import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .improve import generate_improved_description
from eval.core.results import DEVPACE_ROOT, EVAL_DATA_DIR, SKILLS_DIR, eval_score, results_dir_for
from eval.core.skill_io import read_description, read_skill_md, replace_description
from .detect import DEFAULT_MAX_TURNS, DEFAULT_RUNS, DEFAULT_TIMEOUT, run_eval_set


def _split_train_test(
    eval_set: list[dict],
    holdout: float = 0.3,
    seed: int | None = None,
) -> tuple[list[dict], list[dict]]:
    """Split eval set into train and test sets.

    Maintains proportion of positive/negative queries in both sets.
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    pos = [e for e in eval_set if e.get("should_trigger")]
    neg = [e for e in eval_set if not e.get("should_trigger")]

    def _split(items: list[dict]) -> tuple[list[dict], list[dict]]:
        shuffled = items[:]
        rng.shuffle(shuffled)
        n_test = max(1, round(len(shuffled) * holdout))
        return shuffled[n_test:], shuffled[:n_test]

    train_pos, test_pos = _split(pos)
    train_neg, test_neg = _split(neg)

    return train_pos + train_neg, test_pos + test_neg


def run_loop(
    skill_name: str,
    model: str,
    iterations: int = 5,
    timeout: int = DEFAULT_TIMEOUT,
    runs: int = DEFAULT_RUNS,
    max_turns: int = DEFAULT_MAX_TURNS,
    holdout: float = 0.3,
    seed: int | None = 42,
) -> int:
    """Run description optimization loop with train/test split.

    Returns exit code (0 = success).
    """
    skill_dir = SKILLS_DIR / skill_name
    skill_md = skill_dir / "SKILL.md"
    eval_file = EVAL_DATA_DIR / skill_name / "trigger-evals.json"

    if not skill_dir.is_dir():
        print(f"Error: skill directory not found: {skill_dir}", file=sys.stderr)
        return 1
    if not eval_file.exists():
        print(f"Error: eval file not found: {eval_file}", file=sys.stderr)
        return 1

    eval_set = json.loads(eval_file.read_text())
    rdir = results_dir_for(skill_name)
    project_root = str(DEVPACE_ROOT)

    # Train/test split
    train_set, test_set = _split_train_test(eval_set, holdout=holdout, seed=seed)
    print(f"  skill: {skill_name}, iterations: {iterations}", file=sys.stderr)
    print(
        f"  split: {len(train_set)} train / {len(test_set)} test "
        f"(holdout={holdout})",
        file=sys.stderr,
    )

    best_desc = read_description(skill_dir)
    skill_md_content = read_skill_md(skill_dir)
    print(
        f"  initial description ({len(best_desc)} chars): "
        f"{best_desc[:80]}...",
        file=sys.stderr,
    )

    # --- Initial eval on train set ---
    print(f"\n  [0/{iterations}] evaluating current description on train set...", file=sys.stderr)
    best_results = run_eval_set(
        eval_set=train_set, skill_name=skill_name, description=best_desc,
        num_workers=min(5, len(train_set)), timeout=timeout,
        project_root=project_root, runs_per_query=runs, model=model,
        max_turns=max_turns, verbose=False,
    )
    best_score = eval_score(best_results)
    print(f"  [0/{iterations}] train_score: {best_score:.0%}", file=sys.stderr)

    history: list[dict] = [
        {"iteration": 0, "description": best_desc, "train_score": best_score}
    ]

    if best_score >= 1.0:
        print("  perfect train score, nothing to optimize", file=sys.stderr)
    else:
        for i in range(1, iterations + 1):
            print(
                f"\n  [{i}/{iterations}] generating improved description...",
                file=sys.stderr,
            )
            candidate = generate_improved_description(
                skill_name=skill_name,
                current_desc=best_desc,
                skill_md_content=skill_md_content,
                eval_results=best_results,
                model=model,
                history=history,
            )

            if candidate is None or candidate == best_desc:
                print(
                    f"  [{i}/{iterations}] no improvement generated, skipping",
                    file=sys.stderr,
                )
                history.append({
                    "iteration": i,
                    "description": best_desc,
                    "train_score": best_score,
                    "skipped": True,
                })
                continue

            print(
                f"  [{i}/{iterations}] candidate ({len(candidate)} chars): "
                f"{candidate[:80]}...",
                file=sys.stderr,
            )

            # Temporarily swap description for eval
            original_content = replace_description(skill_md, candidate)
            try:
                print(
                    f"  [{i}/{iterations}] evaluating candidate on train set...",
                    file=sys.stderr,
                )
                candidate_results = run_eval_set(
                    eval_set=train_set,
                    skill_name=skill_name,
                    description=candidate,
                    num_workers=min(5, len(train_set)),
                    timeout=timeout,
                    project_root=project_root,
                    runs_per_query=runs,
                    model=model,
                    max_turns=max_turns,
                    verbose=False,
                )
            finally:
                # Always restore original SKILL.md
                skill_md.write_text(original_content)

            candidate_score = eval_score(candidate_results)
            print(
                f"  [{i}/{iterations}] train_score: {candidate_score:.0%} "
                f"(best: {best_score:.0%})",
                file=sys.stderr,
            )

            if candidate_score > best_score:
                print(
                    f"  [{i}/{iterations}] improved! "
                    f"{best_score:.0%} -> {candidate_score:.0%}",
                    file=sys.stderr,
                )
                best_desc = candidate
                best_score = candidate_score
                best_results = candidate_results

            history.append({
                "iteration": i,
                "description": candidate,
                "train_score": candidate_score,
            })

            if best_score >= 1.0:
                print(
                    f"  [{i}/{iterations}] perfect train score, stopping early",
                    file=sys.stderr,
                )
                break

    # --- Validate on test set ---
    test_score = None
    if test_set:
        print(f"\n  validating best description on test set...", file=sys.stderr)
        original_content = replace_description(skill_md, best_desc)
        try:
            test_results = run_eval_set(
                eval_set=test_set,
                skill_name=skill_name,
                description=best_desc,
                num_workers=min(5, len(test_set)),
                timeout=timeout,
                project_root=project_root,
                runs_per_query=runs,
                model=model,
                max_turns=max_turns,
                verbose=False,
            )
        finally:
            skill_md.write_text(original_content)

        test_score = eval_score(test_results)
        print(f"  test_score: {test_score:.0%} (train: {best_score:.0%})", file=sys.stderr)

        # Overfitting detection
        gap = best_score - test_score
        if gap > 0.2:
            print(
                f"  WARNING: possible overfitting "
                f"(train-test gap: {gap:.0%})",
                file=sys.stderr,
            )

    # --- Save results ---
    loop_results = {
        "skill": skill_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "best_description": best_desc,
        "best_train_score": best_score,
        "test_score": test_score,
        "holdout": holdout,
        "train_size": len(train_set),
        "test_size": len(test_set),
        "iterations": len(history) - 1,
        "history": history,
    }

    loop_dir = rdir / "loop"
    (loop_dir / "results.json").write_text(
        json.dumps(loop_results, indent=2, ensure_ascii=False)
    )
    (loop_dir / "best-description.txt").write_text(best_desc)

    original_desc = read_description(skill_dir)
    print(f"\n  loop complete: train={best_score:.0%}", file=sys.stderr)
    if test_score is not None:
        print(f"  test={test_score:.0%}", file=sys.stderr)
    if best_desc != original_desc:
        print(
            f"  improved description saved to: "
            f"{loop_dir.relative_to(DEVPACE_ROOT)}/best-description.txt",
            file=sys.stderr,
        )
        print(f"  apply with: make eval-fix-apply S={skill_name}", file=sys.stderr)
    else:
        print("  no improvement found over current description", file=sys.stderr)

    print(json.dumps(loop_results, indent=2, ensure_ascii=False))
    return 0
