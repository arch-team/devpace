"""eval.core — shared infrastructure (no domain logic).

Re-exports commonly used symbols from results and skill_io modules.
"""
from .results import (
    DEVPACE_ROOT,
    EVAL_DATA_DIR,
    SKILLS_DIR,
    build_metadata,
    eval_score,
    load_results,
    results_dir_for,
    save_trigger_results,
)
from .skill_io import (
    description_hash,
    read_description,
    read_skill_md,
    replace_description,
)
from .llm_client import (
    get_anthropic_client,
    resolve_model_id,
)
