<!-- Generated: 2026-02-18 | Files scanned: 68 | Token estimate: ~700 -->

# Architecture — devpace Plugin

## Project Type

Claude Code Plugin (single plugin, BizDevOps workflow manager)

## Layer Separation

```
Product Layer (distributed)          Development Layer (not distributed)
─────────────────────────            ──────────────────────────────────
.claude-plugin/                      .claude/CLAUDE.md (268 lines)
  plugin.json                        .claude/rules/common.md (42 lines)
  marketplace.json                   .claude/rules/dev-workflow.md (266 lines)
rules/devpace-rules.md (215 lines)   docs/design/vision.md (117 lines)
skills/ (7 skills)                   docs/design/design.md (598 lines)
knowledge/ (5 files)                 docs/planning/requirements.md (199 lines)
                                     docs/planning/roadmap.md (129 lines)
                                     docs/planning/progress.md (97 lines)
                                     tests/ (12 .py + 1 .sh)
                                     scripts/validate-all.sh
```

**Hard constraint**: Product → Dev references forbidden.
Check: `grep -r "docs/\|\.claude/" rules/ skills/ knowledge/` must return empty.

## Value Chain (Concept Model)

```
Business Requirement (BR)
  → Product Feature (PF)
    → Change Request (CR)
      → Code Changes (Git)
```

## CR State Machine

```
created → developing → verifying → in_review → approved → merged
                                       ↓
                                   developing  (reject)
           ↕                ↕
         paused           paused  (pause/resume at developing or verifying)
```

## Plugin Loading Flow

```
claude --plugin-dir ./devpace
  → .claude-plugin/plugin.json (entry point)
  → rules/devpace-rules.md (auto-injected into session)
  → skills/**/SKILL.md (registered as /devpace:pace-* commands)
  → knowledge/ (available to skills at runtime)
```

## Key File Relationships

```
User invokes /pace-init
  → skills/pace-init/SKILL.md (orchestration)
  → skills/pace-init/templates/*.md (8 templates → .devpace/)
  → knowledge/_schema/*.md (format contracts for generated files)

User invokes /pace-advance
  → skills/pace-advance/SKILL.md (orchestration)
  → skills/pace-advance/advance-procedures.md (detailed steps)
  → rules/devpace-rules.md §2-§4 (behavioral constraints)

User invokes /pace-change
  → skills/pace-change/SKILL.md (orchestration)
  → skills/pace-change/change-procedure.md (5 subcommands)
  → rules/devpace-rules.md §9 (change management rules)
```
