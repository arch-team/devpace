"""Shared fixtures and constants for devpace test suite."""

from pathlib import Path

import pytest

# ── Paths ──────────────────────────────────────────────────────────────────
DEVPACE_ROOT = Path(__file__).resolve().parent.parent  # devpace/

PRODUCT_DIRS = ["rules", "skills", "knowledge", ".claude-plugin"]
DEV_DIRS = [".claude", "docs"]

# ── Skill / Schema / Template inventories ──────────────────────────────────
SKILL_NAMES = [
    "pace-change",
    "pace-dev",
    "pace-feedback",
    "pace-guard",
    "pace-init",
    "pace-learn",
    "pace-next",
    "pace-plan",
    "pace-pulse",
    "pace-release",
    "pace-retro",
    "pace-review",
    "pace-sync",
    "pace-role",
    "pace-status",
    "pace-test",
    "pace-theory",
    "pace-trace",
]

SCHEMA_FILES = ["checks-format.md", "context-format.md", "cr-format.md", "insights-format.md", "integrations-format.md", "iteration-format.md", "pf-format.md", "project-format.md", "release-format.md", "risk-format.md", "state-format.md", "sync-mapping-format.md", "test-baseline-format.md", "test-strategy-format.md"]

TEMPLATE_FILES = [
    "state.md",
    "project.md",
    "cr.md",
    "workflow.md",
    "checks.md",
    "context.md",
    "iteration.md",
    "dashboard.md",
    "claude-md-devpace.md",
    "insights.md",
    "integrations.md",
    "release.md",
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
    "released",
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

# ── Release state machine ────────────────────────────────────────────────
RELEASE_STATES = [
    "staging",
    "deployed",
    "verified",
    "closed",
    "rolled_back",
]

RELEASE_FORWARD_TRANSITIONS = [
    ("staging", "deployed"),
    ("deployed", "verified"),
    ("verified", "closed"),
]

RELEASE_ROLLBACK_TRANSITIONS = [
    ("deployed", "rolled_back"),
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
