🌐 [中文版](pace-theory_zh.md) | English

# pace-theory — Design Theory Guide

Reference Skill for understanding devpace's BizDevOps methodology and design rationale. Read-only.

## Core Features

- **15 Subcommands in 3 Tiers**: Beginner (overview, model, why) → Concept (objects, spaces, rules, trace, loops, change, metrics, topic) → Reference (mapping, decisions, vs-devops, sdd, all)
- **Precise Chapter Routing**: Each subcommand loads only its corresponding theory.md section, not the full 550-line file
- **`why` Deep Explanation**: Three-layer output — recent behaviors → design decisions (§11, 16 entries) → theory excerpts; supports keyword-targeted queries (`why gate`, `why paused`)
- **Context-Aware Output**: When `.devpace/` exists, uses actual project data (CRs, metrics, iterations) as live examples
- **Role-Adapted Framing**: Output perspective adjusts based on current role (biz/pm/dev/tester/ops)

## Key Enhancements (v1.6)

### Three-Tier Command Structure
Subcommands organized into Beginner / Concept / Reference tiers. Empty invocation shows only the beginner tier, progressively exposing advanced options to reduce cognitive load.

### Explicit Routing Table
Each subcommand maps to a specific theory.md section (§0–§14). No more full-file loading for targeted queries — haiku model receives only the relevant chapter.

### `why` as Differentiation Feature
Implements devpace's four-level explainability chain: reasoning suffix (15 chars) → mid-layer expansion (2-5 lines) → `/pace-theory why` (methodology) → `/pace-trace` (full decision trail). Each level naturally guides to the next.

### Enhanced `why` with Design Decisions
`why` now cross-references §11 (16 design decisions) for every behavior explanation. Supports focused queries like `why gate`, `why cr`, `why paused` for targeted explanations.

### Progressive Disclosure
Default output is summary-first (1-2 sentences + core table of 5-8 lines), with expand hints pointing to related subcommands. Full chapter content available on demand.

### Keyword Search with Context
Free-text keyword search returns matching paragraphs with positional context ("This concept belongs to [chapter], related: [subcommands]") and intelligent fallback for zero-match cases.

### Project Context Integration
For objects/trace/metrics subcommands, actual project BR/PF/CR data replaces generic theory examples. Uninitialized projects get a gentle nudge toward `/pace-init`.

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| `/pace-trace` | pace-theory explains "why devpace is designed this way" (general theory); pace-trace reconstructs "the full decision trail for a specific CR" (instance-level) |
| `/pace-status` | Status shows current state; theory explains the concepts behind those states |
| `/pace-retro` | Retro generates metrics; theory explains the DIKW model behind them |
| `/pace-learn` | Learn captures experience; theory provides the framework for connecting experience to methodology |

## Related Resources

- **Authoritative source**: `skills/pace-theory/SKILL.md` (routing table, flow)
- **Default output rules**: `skills/pace-theory/theory-procedures-default.md` (summary layering, navigation, role adaptation)
- **Why output rules**: `skills/pace-theory/theory-procedures-why.md` (three-layer template, keyword mapping)
- **Search output rules**: `skills/pace-theory/theory-procedures-search.md` (search flow, context positioning)
- **Data source**: `knowledge/theory.md` (550-line BizDevOps knowledge base, 14 chapters)
- **Design decisions**: `knowledge/theory.md` §11 (16 key design decisions)
