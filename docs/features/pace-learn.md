# Experience Learning (`/pace-learn`)

devpace's learning engine — dual-mode knowledge management that automatically extracts experience patterns from CR lifecycle events, and provides manual knowledge base exploration and curation.

## Prerequisites

| Requirement | Purpose | Required? |
|-------------|---------|:---------:|
| `.devpace/` initialized | Project structure, insights storage | Yes (auto-mode) |
| `.devpace/metrics/insights.md` | Pattern storage (auto-created on first extraction) | Auto |

> **Graceful degradation**: Without `.devpace/`, auto-mode exits silently — no errors, no prompts. Manual commands (`list`/`stats`) report "no knowledge base found" and suggest `/pace-init`.

## Quick Start

```
Auto mode (event-driven, no user action needed):
  CR merged              --> success pattern extraction
  Gate failure recovered --> defense pattern extraction
  Human rejection        --> improvement pattern extraction

Manual mode:
  /pace-learn note "large refactors need test baselines"  --> manual capture
  /pace-learn list --type defense                         --> filter by type
  /pace-learn stats                                       --> knowledge base overview
  /pace-learn export                                      --> export for reuse
```

## Dual-Mode Architecture

| Mode | Trigger | Purpose | Output |
|------|---------|---------|--------|
| **Auto** (primary) | CR merge, Gate recovery, human rejection | Extract patterns from CR lifecycle events | 1-line embedded notification or silent |
| **Manual** | User invokes `/pace-learn <subcommand>` | Knowledge base query, manual capture, export | Per-subcommand output |

### Auto Mode Flow

1. **Pre-check**: `.devpace/` exists? No → silent exit. Yes → continue
2. **Extract**: Read multi-source data matrix from triggering CR → distill patterns
3. **Accumulate**: Deduplicate, update confidence, detect conflicts → write to `insights.md`
4. **Notify**: New pattern → `(experience +N: [title])` | Validation only → `(validated: [title] → X.X)` | Nothing → silent

### Adaptive Extraction

Pattern extraction depth scales with CR complexity:

| CR Complexity | Checkpoint count | Max patterns |
|:---:|:---:|:---:|
| S | ≤ 3 | 1 |
| M | 4–7 | 2 |
| L / XL | > 7 | 3 |

## Command Reference

### `note <description>`

Manually capture valuable experience from exploration or non-CR contexts.

```
/pace-learn note "large refactors need test baselines first"
→ Recorded: test baselines before refactoring (confidence 0.5, tags: refactoring, testing, quality)
```

Pattern goes through the same unified write pipeline (dedup, conflict detection).

### `list [--type TYPE] [--tag TAG] [--confidence MIN]`

Filter and browse knowledge base entries.

```
/pace-learn list --type defense --confidence 0.6
→ Knowledge base (12 total, 3 filtered):

| # | Title | Type | Confidence | Verified | Last referenced | Status |
|---|-------|------|------------|----------|----------------|--------|
| 1 | Auth changes need integration tests | Defense | 0.8 | 5x | 2026-02-20 | Active |
| 2 | Large refactors risk regressions | Defense | 0.6 | 2x | 2026-02-15 | Active |
| ...
```

### `stats`

Knowledge base health overview.

```
/pace-learn stats
→ Knowledge base statistics:

  Total: 15 (Active: 12 | Dormant: 2 | Archived: 1)
  Types: pattern 6 · defense 4 · improvement 3 · preference 2
  Confidence: high(>0.7) 5 · mid(0.4-0.7) 7 · low(<0.4) 3
  Top-5 referenced: [list]
  Unreferenced: 3 (review recommended)
  Conflict pairs: 1 unresolved
  Decay warning: 2 entries will become Dormant in 30 days
```

### `export [--path FILE]`

Export reusable patterns for cross-project sharing.

- **Filter**: confidence ≥ 0.7, excludes preference type (project-specific)
- **Default output**: `./insights-export.md`
- **Progressive teaching**: First time knowledge base reaches 5+ high-confidence patterns, a one-time prompt suggests export capability

## Knowledge Lifecycle

Patterns in `insights.md` follow a three-stage lifecycle:

```
Active ──(confidence < 0.4 or 180 days unreferenced)──> Dormant
Dormant ──(re-referenced or verified)──> Active
Dormant ──(360 days + 0 verifications)──> Archived
```

| Stage | Condition | Behavior |
|-------|-----------|----------|
| **Active** | confidence ≥ 0.4 and referenced within 180 days | Participates in §12 experience-driven decisions |
| **Dormant** | confidence < 0.4 or 180+ days unreferenced | Not proactively referenced; visible in `stats` and `list` |
| **Archived** | Dormant 360+ days with 0 verifications | Moved to file end; manual reactivation only |

### Confidence Decay

Unreferenced patterns automatically lose confidence over time:

- **Trigger**: 180 days without §12 reference
- **Rate**: −0.1 per month from day 181
- **Floor**: 0.2 (preserved but not proactively used)
- **Reset**: Any §12 reference stops decay and updates "last referenced" date

## Unified Writer Principle

`pace-learn` is the **single writer** for `insights.md` (Single Writer Principle):

| Source | Mechanism |
|--------|-----------|
| Auto extraction | Merged / Gate recovery / rejection events |
| `/pace-retro` retrospective | Generates "learning request" → pace-learn pipeline |
| §12.5 correction-as-learning | User confirms preference → pace-learn pipeline |
| `/pace-learn note` | Manual capture → pace-learn pipeline |

This ensures: consistent format, unified dedup logic, unified confidence rules, complete conflict detection.

## Conflict Detection

When a new pattern contradicts an existing one:

1. Both patterns get a **conflict pair** marker pointing to each other
2. Contradicted pattern's confidence −0.2
3. §12 references include conflict warning: "conflicting experience exists, consider resolving in /pace-retro"
4. `/pace-retro` outputs unresolved conflict list for user arbitration

## Cross-Skill Integration

| Integration point | Behavior |
|-------------------|----------|
| §11 merged pipeline | Auto-triggers pace-learn after CR merge (step 2) |
| §12 experience reference | 5 timing points consume insights.md for decision support |
| §12.5 correction-as-learning | Graded interaction: minor → batch at session end; major → immediate |
| `/pace-retro` | Bidirectional: retro validates patterns + defense summary feeds improvement |
| `/pace-retro` meta-analysis | Knowledge base health report embedded in retrospective |
| Session start (§1) | Top-1 defense reminder + expandable "N more, say 'more' to view" |
| Global insights | Confidence ≥ 0.8 + verified ≥ 3 → auto-sync to `~/.devpace/global-insights.md` |

## Related Resources

- [Insights format schema](../../knowledge/_schema/insights-format.md)
- [Experience reference rules](../../knowledge/experience-reference.md)
- [Learning effectiveness metrics](../../knowledge/metrics.md#学习效能指标)
- [Retrospective integration](../../skills/pace-retro/retro-procedures.md#retro↔learn-双向整合)
