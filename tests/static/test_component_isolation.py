"""TC-CI: Component isolation rules from product-architecture.md S0.

Encodes the 5 inter-component dependency rules from the compliance checklist
that were previously manual-only grep commands:
- TC-CI-01 (G4): Schema -> no skills/ or rules/ references
- TC-CI-02 (G5): Hooks -> no knowledge/ or skills/ or rules/ references
- TC-CI-03 (G6): Agents -> no knowledge/ or skills/ or rules/ or hooks/ references
- TC-CI-04 (G7): Procedures -> no cross-Skill path references
- TC-CI-05 (G8): knowledge subdirs -> no skills/ or rules/ references
- TC-CI-06 (G16): Procedures with Schema-like tables must reference _schema/

Stripping strategy (to separate functional dependency from documentation annotation):
- Markdown: strip fenced code blocks + inline code (backtick-wrapped paths are annotations)
- JS/Shell: strip line comments (// and #)
- Lookbehind: exclude .devpace/rules/ and .devpace/skills/ (runtime paths, not Plugin layer)
"""
import re

import pytest

from tests.conftest import DEVPACE_ROOT, SKILL_NAMES, SCHEMA_DIR, _is_workspace_path

HOOKS_DIR = DEVPACE_ROOT / "hooks"
AGENTS_DIR = DEVPACE_ROOT / "agents"
KNOWLEDGE_DIR = DEVPACE_ROOT / "knowledge"
SKILLS_DIR = DEVPACE_ROOT / "skills"

# ---- Content stripping helpers (preserve line numbers) ----

FENCE_RE = re.compile(r"```[^\n]*\n.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]+`")
JS_LINE_COMMENT_RE = re.compile(r"//.*$", re.MULTILINE)
SH_LINE_COMMENT_RE = re.compile(r"#.*$", re.MULTILINE)


def _clean_md(content: str) -> str:
    """Strip fenced code blocks and inline code from Markdown."""
    content = FENCE_RE.sub(lambda m: "\n" * m.group().count("\n"), content)
    return INLINE_CODE_RE.sub("", content)


def _clean_js(content: str) -> str:
    """Strip JS single-line comments."""
    return JS_LINE_COMMENT_RE.sub("", content)


def _clean_sh(content: str) -> str:
    """Strip shell comments (keep shebang)."""
    lines = content.splitlines(keepends=True)
    return "".join(
        line if i == 0 and line.startswith("#!") else SH_LINE_COMMENT_RE.sub("", line)
        for i, line in enumerate(lines)
    )


def _clean_auto(filepath, content: str) -> str:
    """Auto-select cleaning strategy by file extension."""
    if filepath.suffix == ".md":
        return _clean_md(content)
    if filepath.suffix == ".mjs":
        return _clean_js(content)
    if filepath.suffix == ".sh":
        return _clean_sh(content)
    return content


def _scan(files, pattern, clean=True, exclude=None):
    """Scan files for pattern matches, return violation strings with original lines.

    Args:
        exclude: optional regex — lines matching this are exempt (e.g. ACTION: repair instructions).
    """
    violations = []
    for f in files:
        raw = f.read_text(encoding="utf-8")
        text = _clean_auto(f, raw) if clean else raw
        raw_lines = raw.splitlines()
        for i, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                if exclude and exclude.search(raw_lines[i - 1] if i <= len(raw_lines) else line):
                    continue
                display = raw_lines[i - 1].strip()[:120] if i <= len(raw_lines) else line.strip()[:120]
                violations.append(f"{f.relative_to(DEVPACE_ROOT)}:{i}: {display}")
    return violations


# ---- Patterns ----
# Lookbehind excludes .devpace/ runtime paths (e.g. .devpace/rules/checks.md)
PLUGIN_SKILLS_OR_RULES = re.compile(r"(?<!devpace/)(?:skills/|rules/)")
PLUGIN_ALL_COMPONENTS = re.compile(r"(?<!devpace/)(?:knowledge/|skills/|rules/)")
AGENT_ALL_COMPONENTS = re.compile(r"(?:knowledge/|skills/|rules/|hooks/)")
CROSS_SKILL_PATH = re.compile(r"skills/pace-")
# Schema-like table headers that indicate inline format definitions
SCHEMA_TABLE_HEADER = re.compile(
    r"^\|.*(?:字段|field).*\|.*(?:类型|说明|type|必填|required|描述|description).*\|",
    re.IGNORECASE,
)


@pytest.mark.static
class TestComponentIsolation:
    """Inter-component dependency direction enforcement."""

    def test_tc_ci_01_schema_no_reverse_refs(self):
        """TC-CI-01: _schema/ files have no references to skills/ or rules/.

        Schema is a pure contract layer (L4) -- only references sibling schemas.
        Ref: product-architecture.md S0 -- grep -r "skills/|rules/" knowledge/_schema/
        """
        files = [f for f in SCHEMA_DIR.rglob("*.md") if f.name != "README.md"]
        violations = _scan(files, PLUGIN_SKILLS_OR_RULES)
        assert not violations, (
            f"Schema files reference skills/ or rules/ ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nACTION: Remove path refs; use _schema/README.md consumer table for documentation."
        )

    def test_tc_ci_02_hooks_no_markdown_refs(self):
        """TC-CI-02: hooks/ files have no references to knowledge/, skills/, or rules/.

        Hooks communicate via stdin JSON + .devpace/ files, not Markdown parsing.
        Ref: product-architecture.md S0 -- grep -r "knowledge/|skills/|rules/" hooks/
        """
        files = [
            f for f in HOOKS_DIR.rglob("*")
            if f.is_file()
            and f.suffix in (".mjs", ".sh", ".json")
            and "node_modules" not in f.parts
        ]
        # ACTION: repair instructions legitimately reference component paths to guide the Agent
        action_exempt = re.compile(r"ACTION:")
        violations = _scan(files, PLUGIN_ALL_COMPONENTS, exclude=action_exempt)
        assert not violations, (
            f"Hook files reference knowledge/, skills/, or rules/ ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nACTION: Hooks must only read .devpace/ files and stdin JSON. "
            "See product-architecture.md S1.2."
        )

    def test_tc_ci_03_agents_no_component_refs(self):
        """TC-CI-03: agents/ files have no references to knowledge/, skills/, rules/, or hooks/.

        Agents are pure persona definitions (persona + tool permissions).
        Ref: product-architecture.md S0 -- grep -r "knowledge/|skills/|rules/|hooks/" agents/
        """
        files = [f for f in AGENTS_DIR.glob("*.md") if f.is_file()]
        if not files:
            pytest.skip("No agent files found")
        violations = _scan(files, AGENT_ALL_COMPONENTS)
        assert not violations, (
            f"Agent files reference component paths ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nACTION: Agents only define persona + tool permissions. "
            "Business logic belongs in SKILL.md + procedures."
        )

    def test_tc_ci_04_no_cross_skill_procedure_refs(self):
        """TC-CI-04: Procedure files don't contain 'skills/pace-' path references.

        Shared steps should be extracted to knowledge/_guides/.
        Ref: product-architecture.md S0 -- grep -rn "skills/pace-" skills/ --include="*-procedures*.md"
        """
        files = [
            proc
            for name in SKILL_NAMES
            for proc in (SKILLS_DIR / name).glob("*-procedures*.md")
            if not _is_workspace_path(proc)
        ]
        violations = _scan(files, CROSS_SKILL_PATH)
        assert not violations, (
            f"Procedure files reference other Skills via paths ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nACTION: Extract shared steps to knowledge/_guides/ and reference from both Skills; "
            "or use command form /pace-xxx instead of path form skills/pace-xxx/."
        )

    def test_tc_ci_05_knowledge_subdirs_isolated(self):
        """TC-CI-05: _signals/, _guides/, _extraction/ don't reference skills/ or rules/.

        These subdirs can reference _schema/ and root knowledge/ only.
        Ref: product-architecture.md S0 -- grep -rn "skills/|rules/" knowledge/_signals/ _guides/ _extraction/
        """
        files = [
            f
            for subdir in ("_signals", "_guides", "_extraction")
            if (KNOWLEDGE_DIR / subdir).is_dir()
            for f in (KNOWLEDGE_DIR / subdir).rglob("*.md")
            if not _is_workspace_path(f)
        ]
        if not files:
            pytest.skip("No knowledge subdirectory files found")
        violations = _scan(files, PLUGIN_SKILLS_OR_RULES)
        assert not violations, (
            f"knowledge subdirs reference skills/ or rules/ ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nACTION: knowledge subdirs can only reference _schema/ and root knowledge/. "
            "See product-architecture.md S1.4."
        )

    def test_tc_ci_06_procedures_inline_schema_has_ref(self):
        """TC-CI-06: Procedures with Schema-like field tables must reference _schema/.

        Ref: product-architecture.md S2 — procedures must not inline Schema-defined formats.
        Schema is the single authority for data format (IA-6). When a procedure defines a
        field table, it must reference the corresponding _schema/ file.
        """
        violations = []
        for name in SKILL_NAMES:
            for proc in (SKILLS_DIR / name).glob("*-procedures*.md"):
                if _is_workspace_path(proc):
                    continue
                content = proc.read_text(encoding="utf-8")
                clean = _clean_md(content)
                has_schema_table = bool(SCHEMA_TABLE_HEADER.search(clean))
                has_schema_ref = "_schema/" in content
                if has_schema_table and not has_schema_ref:
                    violations.append(
                        f"{proc.relative_to(DEVPACE_ROOT)}: has field definition table but no _schema/ reference"
                    )
        assert not violations, (
            f"Procedures inline Schema format without _schema/ reference ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nACTION: Add '_schema/<subdir>/<name>-format.md' reference near the table, "
            "or delegate the format definition to Schema and remove the inline table."
        )
