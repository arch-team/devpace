# Decision Trail (`/pace-trace`)

devpace decision trail is the "deep layer" of the three-tier progressive transparency system — the only entry point that exposes the complete AI decision trace and source attribution markers. While the surface layer (reasoning suffixes) and middle layer (follow-up expansion) provide quick explanations, `/pace-trace` delivers full audit-grade decision reconstruction.

## Prerequisites

| Requirement | Purpose | Required? |
|-------------|---------|:---------:|
| `.devpace/` initialized | Project structure, CR tracking | Yes |
| Active or recent CR | Decision data source | Yes |

> **Graceful degradation**: Without `.devpace/`, outputs initialization guidance. Without matching CR, suggests `/pace-status detail` to browse all CRs. Partial data triggers reduced-confidence output rather than failure.

## Quick Start

```
1. /pace-trace CR-001 gate1     --> Full Gate 1 quality check trail
2. /pace-trace CR-001 intent    --> Intent inference process with source attribution
3. /pace-trace CR-001 timeline  --> Full lifecycle decision timeline
4. /pace-trace                   --> Latest decision trail for current CR
```

Typical workflow: After seeing a reasoning suffix ("Gate 1 passed — tests 92%, lint 0 error"), ask "why?" to get middle-layer expansion, then use `/pace-trace` for the complete audit trail.

## Decision Types

| Type | What it reconstructs | Key data sources |
|------|---------------------|------------------|
| `gate1` | Gate 1 quality check judgment | CR checks, command output, checkpoint evidence |
| `gate2` | Gate 2 integration verification + acceptance comparison | CR acceptance criteria vs actual changes |
| `gate3` | Gate 3 pre-approval summary generation | CR status, review summary |
| `intent` | Intent checkpoint inference process | CR intent section, source attribution markers |
| `change` | Change impact analysis reasoning | CR relations, PF/iteration impact chain |
| `risk` | Risk assessment judgment basis | 5-dimension scan results, risk files |
| `autonomy` | How autonomy level affects Gate behavior | project.md autonomy-level, interaction mode differences |
| `timeline` | Full CR lifecycle decision timeline | All events and checkpoints chronologically |

## Output Structure

pace-trace uses a **conclusion-first** three-part narrative optimized for audit mindset:

1. **Verdict** — Final judgment + key factor + reconstruction confidence (High/Medium/Low)
2. **Assessment Process** — Item-by-item checks, rule matching, experience influence
3. **Decision Context** — Information read, source attribution markers

### Reconstruction Confidence

Confidence reflects data completeness for trail reconstruction, not decision correctness:

| Completeness | Confidence | Condition |
|-------------|-----------|-----------|
| Full | High | Event table + source markers + checkpoint evidence + insights references all present |
| Mostly complete | Medium | Event table + checkpoint evidence present, source markers partially missing |
| Partial | Low | Only event table present, checkpoint evidence and source markers missing |

### Timeline View

The `timeline` type aggregates all checkpoints and state transitions into a chronological overview:

```
| Time  | Decision Point | Result        | Key Factor              |
|-------|---------------|---------------|-------------------------|
| 02-21 | Intent check  | Complexity M  | 3 files, standard pattern |
| 02-21 | Gate 1        | Passed        | tsc 0 error, 8/8 tests  |
| 02-21 | Gate 2        | Passed        | 3/3 acceptance met      |
| 02-22 | Gate 3        | Rejected      | User: unclear error msg  |
| 02-23 | Gate 2 (retry)| Passed        | 1/1 fix confirmed       |
```

## Error Handling

| Scenario | Output | Guidance |
|----------|--------|----------|
| Project not initialized | "No .devpace/ directory found" | Suggests `/pace-init` |
| CR not found | "No CR matching '[input]'" | Suggests `/pace-status detail` |
| Decision type has no data | "No [type] decision record for this CR" | Lists available types for this CR |
| Source markers missing | "Event records exist but source markers are incomplete" | Notes reconstruction is based on event table |
| Unknown type | "Unknown decision type '[input]'" | Lists supported types |

## Context Navigation

Each output ends with context-aware navigation suggestions based on decision type:

| Decision Type | Navigation |
|--------------|------------|
| gate1/gate2 | Experience patterns, quality trends |
| intent | Design theory, change history |
| change | Test impact, risk scan |
| risk | Risk overview, related experience |
| autonomy | Role perspective, theory basis |
| timeline | Drill into specific decision, current status |

## Distinguishing Similar Features

- **`/pace-trace [CR] [type]`**: "Why did Claude judge this way?" — single decision audit trail
- **`/pace-status trace <name>`**: "How far along is this goal?" — value chain completion tracking (OBJ to BR to PF to CR)
- **`/pace-theory why`**: "Why is devpace designed this way?" — system methodology explanation

## Three-Tier Transparency System

```
Surface layer:  Reasoning suffix (<=15 chars after system action)
                "Gate 1 passed — tests 92%, lint 0 error."

Middle layer:   Follow-up expansion (ask "why?" -> 2-5 lines)
                Judgment basis with data points
                -> Full decision trail: /pace-trace [CR] [type]

Deep layer:     /pace-trace (complete audit trail)
                Verdict + assessment + context + source attribution
```

## Related Resources

- [Output guide](../../knowledge/output-guide.md)
- [CR format schema](../../knowledge/_schema/cr-format.md)
- [Transparency rules](../../rules/devpace-rules.md)
