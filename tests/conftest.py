"""Shared fixtures and constants for devpace test suite."""

import re
from pathlib import Path

import yaml

# ── Paths ──────────────────────────────────────────────────────────────────
DEVPACE_ROOT = Path(__file__).resolve().parent.parent  # devpace/

PRODUCT_DIRS = ["rules", "skills", "knowledge", ".claude-plugin"]
DEV_DIRS = [".claude", "docs"]

SKILLS_ROOT = DEVPACE_ROOT / "skills"
SCHEMA_DIR = DEVPACE_ROOT / "knowledge" / "_schema"
TEMPLATE_DIR = DEVPACE_ROOT / "skills" / "pace-init" / "templates"
RULES_FILE = DEVPACE_ROOT / "rules" / "devpace-rules.md"

# ── Skill / Schema / Template inventories ──────────────────────────────────
SKILL_NAMES = [
    "pace-biz",
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
    "pace-role",
    "pace-status",
    "pace-sync",
    "pace-test",
    "pace-theory",
    "pace-trace",
]

SCHEMA_FILES = [
    "entity/br-format.md",
    "entity/cr-format.md",
    "entity/epic-format.md",
    "auxiliary/insights-format.md",
    "entity/obj-format.md",
    "entity/opportunity-format.md",
    "entity/pf-format.md",
    "entity/project-format.md",
    "entity/vision-format.md",
    "process/checks-format.md",
    "process/iteration-format.md",
    "process/release-format.md",
    "process/state-format.md",
    "process/test-baseline-format.md",
    "process/test-strategy-format.md",
    "integration/integrations-format.md",
    "integration/sync-mapping-format.md",
    "auxiliary/accept-report-contract.md",
    "auxiliary/adr-format.md",
    "auxiliary/context-format.md",
    "auxiliary/incident-format.md",
    "auxiliary/merge-strategy.md",
    "auxiliary/readiness-score.md",
    "auxiliary/risk-format.md",
]

# ── Eval directories (per-Skill under tests/evaluation/) ────────────────
EVAL_DIR = DEVPACE_ROOT / "tests" / "evaluation"
EVAL_CROSS_CUTTING_DIR = EVAL_DIR / "_cross-cutting"

# Expected eval files per Skill subdirectory
EVAL_FILES_PER_SKILL = ["evals.json", "trigger-evals.json"]

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

# ── Shared utilities ─────────────────────────────────────────────────────

def parse_frontmatter(path):
    """Extract YAML frontmatter; returns None if missing or malformed."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    return yaml.safe_load(text[3:end])


def headings(text):
    """Extract markdown headings as (level, title) tuples."""
    return [(len(m.group(1)), m.group(2).strip())
            for m in re.finditer(r'^(#{1,6})\s+(.+)$', text, re.MULTILINE)]


# ── Workspace exclusion ──────────────────────────────────────────────────
# skill-creator evaluation workspaces (*-workspace/) are gitignored but may
# exist on disk.  Tests scanning product-layer directories must skip them.

def _is_workspace_path(p: Path) -> bool:
    """Return True if any ancestor directory name ends with '-workspace'."""
    return any(part.endswith("-workspace") for part in p.parts)


def product_md_files(exclude_workspace=True):
    """Collect all .md files under product-layer directories."""
    files = []
    for d in PRODUCT_DIRS:
        dirpath = DEVPACE_ROOT / d
        if dirpath.is_dir():
            for f in dirpath.rglob("*.md"):
                if exclude_workspace and _is_workspace_path(f):
                    continue
                files.append(f)
    return files

