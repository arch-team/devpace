"""Evaluation results persistence and data model.

Handles saving, loading, and structuring trigger evaluation results
with enhanced metadata (P1.4: model, sdk_options, environment, duration).
"""
from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from eval import __version__
from .skill_io import description_hash

# Default paths — eval/core/ is two levels below devpace root
DEVPACE_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_DATA_DIR = DEVPACE_ROOT / "tests" / "evaluation"
SKILLS_DIR = DEVPACE_ROOT / "skills"


def results_dir_for(skill_name: str) -> Path:
    """Get or create the results directory for a skill."""
    d = EVAL_DATA_DIR / skill_name / "results"
    d.mkdir(parents=True, exist_ok=True)
    (d / "history").mkdir(exist_ok=True)
    (d / "loop").mkdir(exist_ok=True)
    return d


def _get_sdk_version() -> str:
    """Get claude_agent_sdk version if available."""
    try:
        from importlib.metadata import version
        return version("claude-agent-sdk")
    except Exception:
        return "unknown"


def build_metadata(
    *,
    model: str | None = None,
    max_turns: int = 5,
    timeout: int = 90,
    runs_per_query: int = 1,
    duration_seconds: float | None = None,
) -> dict:
    """Build enhanced metadata dict (P1.4)."""
    meta: dict = {}
    if model:
        meta["model"] = model
    meta["sdk_options"] = {
        "max_turns": max_turns,
        "timeout": timeout,
        "runs_per_query": runs_per_query,
    }
    meta["environment"] = {
        "python": platform.python_version(),
        "sdk": _get_sdk_version(),
        "eval_version": __version__,
        "platform": sys.platform,
    }
    if duration_seconds is not None:
        meta["duration_seconds"] = round(duration_seconds, 1)
    return meta


def save_trigger_results(
    skill_name: str,
    raw: dict,
    *,
    metadata: dict | None = None,
) -> Path:
    """Save trigger evaluation results to disk.

    Writes both latest.json and a timestamped history file.
    Returns path to latest.json.
    """
    rdir = results_dir_for(skill_name)
    res = raw.get("results", [])
    pos = [r for r in res if r.get("should_trigger")]
    neg = [r for r in res if not r.get("should_trigger")]

    structured = {
        "skill": skill_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description_hash": description_hash(SKILLS_DIR / skill_name),
        "summary": raw.get("summary", {}),
        "positive": {
            "total": len(pos),
            "passed": sum(1 for r in pos if r["pass"]),
            "failed": sum(1 for r in pos if not r["pass"]),
        },
        "negative": {
            "total": len(neg),
            "passed": sum(1 for r in neg if r["pass"]),
            "failed": sum(1 for r in neg if not r["pass"]),
        },
        "false_negatives": [
            {"id": i, "query": r["query"]}
            for i, r in enumerate(pos) if not r["pass"]
        ],
        "false_positives": [
            {"id": i, "query": r["query"]}
            for i, r in enumerate(neg) if not r["pass"]
        ],
        "runs_per_query": res[0].get("runs", 1) if res else 1,
        "raw_results": res,
    }

    if metadata:
        structured["metadata"] = metadata

    latest = rdir / "latest.json"
    latest.write_text(json.dumps(structured, indent=2, ensure_ascii=False))
    ts = datetime.now().strftime("%Y-%m-%dT%H-%M")
    (rdir / "history" / f"{ts}.json").write_text(
        json.dumps(structured, indent=2, ensure_ascii=False)
    )
    return latest


def load_results(skill_name: str, which: str = "latest") -> dict | None:
    """Load results for a skill. which='latest' or 'baseline'."""
    rdir = EVAL_DATA_DIR / skill_name / "results"
    path = rdir / f"{which}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def eval_score(results: dict) -> float:
    """Compute a single score from eval results (0.0 - 1.0)."""
    s = results.get("summary", {})
    total = s.get("total", 0)
    return s.get("passed", 0) / max(total, 1)
