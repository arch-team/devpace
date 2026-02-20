# Contributing to devpace

Thank you for your interest in contributing to devpace! This guide covers everything you need to get started.

## Prerequisites

- [Claude Code CLI](https://claude.ai/code) installed
- Python 3.9+ (for running tests)
- Git

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd devpace

# Install test dependencies
pip install pytest pyyaml

# Verify your setup
bash scripts/validate-all.sh
```

## Project Structure

devpace has a strict **two-layer architecture**. Understanding this is critical before making changes:

| Layer | Directories | Purpose | Distributed? |
|-------|-------------|---------|:------------:|
| **Product** | `rules/`, `skills/`, `knowledge/`, `.claude-plugin/` | Plugin runtime assets delivered to users | Yes |
| **Development** | `.claude/`, `docs/`, `tests/`, `scripts/` | Internal dev standards and docs | No |

**Hard constraint**: Product layer files must never reference development layer files (`docs/` or `.claude/`). Verify with:

```bash
grep -r "docs/\|\.claude/" rules/ skills/ knowledge/
# Expected: no output
```

## Running Tests

```bash
# Full validation suite (recommended before any PR)
bash scripts/validate-all.sh

# Static tests only (faster)
pytest tests/static/ -v

# Individual test module
pytest tests/static/test_frontmatter.py -v

# Plugin loading test (requires Claude CLI)
bash tests/integration/test_plugin_loading.sh
```

### What the Static Tests Cover

| Test | What it checks |
|------|----------------|
| `test_layer_separation` | Product layer doesn't reference dev layer |
| `test_plugin_json_sync` | `plugin.json` matches actual files on disk |
| `test_frontmatter` | Skill/agent frontmatter uses only valid fields |
| `test_schema_compliance` | Schema files follow required structure |
| `test_template_placeholders` | Templates use `{{PLACEHOLDER}}` format |
| `test_markdown_structure` | Section 0 quick-reference cards present where required |
| `test_cross_references` | Internal file references resolve correctly |
| `test_naming_conventions` | Files follow kebab-case naming |
| `test_state_machine` | CR state transitions are consistent across docs |

## Making Changes

### Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with valid frontmatter:

```yaml
---
description: When to trigger this skill (be specific — Claude uses this to decide)
allowed-tools: Read, Write, Glob, Grep
---
```

2. If the skill body exceeds ~50 lines of procedural rules, split into:
   - `SKILL.md` — what it does (input/output/high-level steps)
   - `<name>-procedures.md` — how it does it (detailed rules)

3. Update `.claude-plugin/plugin.json` — run `pytest tests/static/test_plugin_json_sync.py -v` to verify sync.

4. Reference existing skills (`pace-advance/`, `pace-change/`) as patterns.

### Modifying Schema

Schema files in `knowledge/_schema/` are contracts. Changes affect all Skills that produce output conforming to that schema. Before modifying:

1. Read the schema file and understand all consumers
2. Update all affected templates in `skills/pace-init/templates/`
3. Run `pytest tests/static/test_schema_compliance.py -v`

### Modifying Rules

`rules/devpace-rules.md` is the runtime behavior protocol loaded by Claude when the plugin is active. Changes here directly affect how Claude behaves in user projects. Test by loading the plugin:

```bash
claude --plugin-dir ./
```

### Modifying Hooks

Hook scripts are in `hooks/`. Key requirements:

- Must have `#!/bin/bash` shebang and executable permission (`chmod +x`)
- Use `${CLAUDE_PLUGIN_ROOT}` for plugin-relative paths
- Exit codes: `0` = success, `2` = block operation, other = non-blocking error
- Event names are case-sensitive (`PreToolUse`, not `preToolUse`)
- Avoid bashisms that don't work on Linux/WSL (test with `bash --posix`)

## Commit Convention

Format: `<type>(<scope>): <short description>`

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Scopes**: `skills`, `rules`, `knowledge`, `hooks`, `scripts`, `agents`, `docs`, `*` (cross-scope)

Examples:
```
feat(skills): add pace-deploy skill
fix(hooks): correct state matching pattern in pre-tool-use
docs(docs): update design.md state machine diagram
test(scripts): add hook cross-platform test
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following the guidelines above
3. Run the full validation suite: `bash scripts/validate-all.sh`
4. Verify plugin loads: `claude --plugin-dir ./`
5. Write a clear PR description covering what changed and why

### PR Checklist

- [ ] `bash scripts/validate-all.sh` passes
- [ ] Layer separation check passes (no product→dev references)
- [ ] `plugin.json` is in sync with actual files
- [ ] New Skills have valid frontmatter fields only
- [ ] Templates use `{{PLACEHOLDER}}` format
- [ ] Hook scripts have executable permission and shebang
- [ ] Commit messages follow the convention

## Key Design Principles

When contributing, keep these in mind:

- **Conceptual model is always complete**: BR→PF→CR chain exists from day one. Content can be empty but structure must be whole.
- **Markdown is the only format**: State files are consumed by LLM + human, not traditional parsers.
- **Schema is contract**: `knowledge/_schema/` definitions are hard constraints.
- **UX first**: Zero friction, progressive disclosure, byproducts not prerequisites, fault-tolerant recovery.
- **Theory alignment**: New features should align with `knowledge/theory.md`.

## Questions?

Open an issue for questions about architecture decisions, contribution scope, or anything unclear in this guide.
