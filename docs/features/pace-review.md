# Code Review & Quality Gates (`/pace-review`)

`/pace-review` generates a structured review summary for change requests in the `in_review` state. It combines automated quality gate checks (Gate 2) with an adversarial review layer and a cumulative diff report, then hands off to the human for final approval (Gate 3). The goal is to give the reviewer everything needed for an informed approve/reject decision with minimal cognitive overhead.

## Quick Start

```
1. CR reaches in_review state (via /pace-dev)
2. /pace-review           → Gate 2 + adversarial review + summary generated
3. Human reviews summary  → "approved" / reject / specific feedback
4. approved → git merge → CR transitions to merged
```

Gate 3 (human approval) cannot be bypassed under any circumstances (Iron Law IR-2).

## Review Process

### Step 1: Identify CRs Pending Review

Scans `.devpace/backlog/` for CRs in `in_review` state. An optional keyword argument narrows the selection to a specific CR. If none qualify, the user is informed and the process stops.

### Step 2: Gate 2 -- Automated Quality Checks

Gate 2 is the last automated gate before human review. It follows the **independent verification principle**: nothing from Gate 1 is trusted -- all evidence is gathered fresh (acceptance criteria re-read, git diff re-obtained).

**Execution order (mandatory)**:

1. Re-read acceptance criteria from the CR file
2. Obtain a fresh `git diff main...<branch>`
3. Intent consistency first -- if intent does not match, Gate 2 fails immediately (no further checks)

**Intent consistency check** marks each acceptance criterion as satisfied (pass), not satisfied (fail + what is missing), or partially satisfied (details of done vs. remaining). It also detects **out-of-scope changes** and **in-scope omissions**.

**On failure**: CR returns to `developing`. Claude addresses the gap, re-runs checks, and resubmits -- no manual restart needed.

### Step 3: Adversarial Review

After Gate 2 passes, the mindset switches from "verify correctness" to "find defects" -- a countermeasure against confirmation bias.

**Core rule**: Zero findings is not acceptable. If all dimensions produce nothing, at least one optional optimization is output as a floor.

**Four forced dimensions** (each considered at least once):

| Dimension | Examples |
|-----------|---------|
| Boundary & error paths | Empty input, extreme values, concurrency, timeouts |
| Security risks | Injection, privilege escalation, sensitive data exposure |
| Performance concerns | N+1 queries, large allocations, blocking operations |
| Integration risks | API contract changes, backward compatibility |

Severity tags: `🔴 Recommend fix` / `🟡 Recommend improvement` / `🟢 Optional optimization`. Every finding carries a false-positive disclaimer.

**Key rules**: Adversarial findings do not block Gate 2 -- they are informational for the human reviewer. Simple CRs (complexity S) skip adversarial review entirely.

### Step 4: Cumulative Diff Report

For medium-and-above CRs, a module-grouped diff maps each changed file to its acceptance criterion:

```
Cumulative diff report:
  Module A (+N/-M lines):
    - file1.ts (new)      → Acceptance criterion 1
    - file2.ts (modified)  → Acceptance criterion 2
  ⚠️ Uncovered criteria: [list]
  ⚠️ Out-of-scope changes: [files + rationale]
```

This complements Gate 2: Gate 2 checks "was it done?", the diff shows "how was it done?" Simple CRs skip this report.

### Step 5: Review Summary

All findings are assembled into a structured summary presented to the human:

- **What changed / Why / Impact scope** -- plain-language overview with business traceability
- **Intent match** -- per-criterion pass/fail table (standard/complex CRs)
- **AI acceptance verification** -- `/pace-test accept` evidence when available
- **Adversarial review** -- findings with severity tags (M/L/XL CRs)
- **Cumulative diff report** -- module grouping with criteria mapping (M/L/XL CRs)
- **Quality check status** -- automated checks passed + human approval pending
- **Branch and change stats**

See [review-procedures.md](../../skills/pace-review/review-procedures.md) for the full summary template.

### Step 6: Human Decision (Gate 3)

| Human response | Action |
|----------------|--------|
| "approved" / "lgtm" | CR → `approved` → `git merge` → CR → `merged` → cascade updates |
| Reject + reason | CR → `developing`; reason recorded in event table (scope / quality / design) |
| Specific feedback | Claude modifies code → re-runs affected checks → updates summary |

## Key Features

### Anti-Performative Opinion Handling

When receiving review feedback, Claude follows: **understand** real intent (clarify ambiguity) → **evaluate** alignment with CR scope → **execute + verify**. Prohibited: "You're absolutely right!" responses, accepting YAGNI-violating suggestions, modifying code before understanding intent.

### Independent Verification Principle

Gate 2 gathers all evidence from scratch. It does not trust Gate 1 snapshots -- context windows shift and code may have changed during the `verifying` phase. This is a hard requirement.

### Structured Rejection Records

When the human rejects a CR, Claude prompts for a categorized reason (one follow-up maximum). Categories: **scope** (acceptance gaps or creep), **quality** (code or test coverage), **design** (architecture or API). Records are stored in the CR event table for `/pace-learn` pattern extraction.

## Usage Scenarios

### Scenario 1: Standard Review Flow

```
You:    /pace-review
Claude: Found CR-007 (in_review)

        ## Add retry logic to payment gateway
        **What changed**: 3 files in src/payment/, new RetryPolicy class
        **Intent match**:
          ✅ AC-1: Exponential backoff — satisfied
          ✅ AC-2: Max 3 retries — satisfied
        **Adversarial review** (2 findings):
          🟡 maxDelay has no upper bound validation
          🟢 Consider retry metrics logging
        **Quality**: ✅ lint, types, tests | ⏳ Human approval

You:    approved
Claude: ✅ CR-007 → approved → merged into main
```

### Scenario 2: Review with Pushback

```
You:    /pace-review CR-012
Claude: [summary generated]

You:    Error handling in parser.ts is too broad -- use specific catch blocks.

Claude: Understood: granular catch blocks per error type. Aligns with AC-2.
        Modifying parser.ts ... re-running checks ... ✅ all pass.
        Updated summary: ✅ all criteria satisfied | ⏳ Human approval

You:    lgtm
Claude: ✅ CR-012 → approved → merged into main
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `/pace-dev` | Transitions CR to `in_review` when Gate 1 passes, handing off to `/pace-review` |
| `/pace-test` | Provides `accept` verification evidence displayed in the review summary |
| `/pace-change` | CR state transitions (reject → `developing`) follow the state machine |
| `/pace-learn` | Structured rejection records feed pattern extraction for future improvements |

## Related Resources

- [SKILL.md](../../skills/pace-review/SKILL.md) -- Skill entry point and trigger description
- [review-procedures.md](../../skills/pace-review/review-procedures.md) -- Detailed review procedures
- [Design Document](../design/design.md) -- Quality gate definitions and CR state machine
- [devpace-rules.md](../../rules/devpace-rules.md) -- Runtime behavior rules
