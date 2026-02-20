"""Shared fixtures and constants for devpace test suite."""

from pathlib import Path

import pytest

# ── Paths ──────────────────────────────────────────────────────────────────
DEVPACE_ROOT = Path(__file__).resolve().parent.parent  # devpace/

PRODUCT_DIRS = ["rules", "skills", "knowledge", ".claude-plugin"]
DEV_DIRS = [".claude", "docs"]

# ── Skill / Schema / Template inventories ──────────────────────────────────
SKILL_NAMES = [
    "pace-init",
    "pace-advance",
    "pace-change",
    "pace-guide",
    "pace-retro",
    "pace-review",
    "pace-status",
]

SCHEMA_FILES = ["cr-format.md", "iteration-format.md", "project-format.md", "state-format.md"]

TEMPLATE_FILES = [
    "state.md",
    "project.md",
    "cr.md",
    "workflow.md",
    "checks.md",
    "iteration.md",
    "dashboard.md",
    "claude-md-devpace.md",
    "insights.md",
]

# ── SKILL.md frontmatter constraints ──────────────────────────────────────
LEGAL_SKILL_FIELDS = {
    "name",
    "description",
    "argument-hint",
    "allowed-tools",
    "model",
    "disable-model-invocation",
    "user-invocable",
    "context",
    "agent",
    "hooks",
}

LEGAL_MODEL_VALUES = {"sonnet", "opus", "haiku"}

LEGAL_TOOL_NAMES = {
    "AskUserQuestion",
    "Write",
    "Read",
    "Edit",
    "Glob",
    "Bash",
    "Grep",
    "Task",
    "WebFetch",
    "WebSearch",
}

# ── CR state machine ──────────────────────────────────────────────────────
CR_STATES = [
    "created",
    "developing",
    "verifying",
    "in_review",
    "approved",
    "merged",
    "paused",
]

FORWARD_TRANSITIONS = [
    ("created", "developing"),
    ("developing", "verifying"),
    ("verifying", "in_review"),
    ("in_review", "approved"),
    ("approved", "merged"),
]

REJECT_TRANSITIONS = [
    ("in_review", "developing"),
]

# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def devpace_root():
    """Return the devpace project root as a Path."""
    return DEVPACE_ROOT


@pytest.fixture
def product_md_files():
    """Yield all .md files under product-layer directories."""
    files = []
    for d in PRODUCT_DIRS:
        dirpath = DEVPACE_ROOT / d
        if dirpath.is_dir():
            files.extend(dirpath.rglob("*.md"))
    return files


@pytest.fixture
def skill_dirs():
    """Return list of (name, path) tuples for each skill directory."""
    skills_root = DEVPACE_ROOT / "skills"
    return [
        (name, skills_root / name)
        for name in SKILL_NAMES
        if (skills_root / name).is_dir()
    ]


@pytest.fixture
def template_dir():
    """Return the templates directory path."""
    return DEVPACE_ROOT / "skills" / "pace-init" / "templates"


@pytest.fixture
def schema_dir():
    """Return the schema directory path."""
    return DEVPACE_ROOT / "knowledge" / "_schema"
