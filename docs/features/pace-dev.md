# Development Workflow (`/pace-dev`)

`/pace-dev` is devpace's core development skill. It drives a Change Request (CR) through its entire lifecycle -- from intent clarification to code implementation to quality gates -- in a single, autonomous workflow. Claude enters "advance mode," writes code, runs tests, self-corrects on failures, and commits at each meaningful step. The skill adapts its rigor to the complexity of the change: a one-file typo fix gets minimal ceremony, while a multi-module feature gets a full execution plan with user confirmation.

## Quick Start

```
1. /pace-dev "add user login"   --> Locates or creates a CR, clarifies intent, starts coding
2. (Claude works autonomously)  --> Implements, tests, commits, runs Gate 1 & Gate 2
3. "LGTM"                       --> Human approval (Gate 3) --> CR merged
```

After the initial command, Claude drives the workflow with no further prompts required until it needs a decision from you or reaches the human approval gate.

## CR Lifecycle Overview

Every change flows through a six-state lifecycle. `/pace-dev` manages transitions automatically; you only intervene at Gate 3 (human approval).

```
created --> developing --> verifying --> in_review --> approved --> merged
   |            |              |             |            |          |
   |  Intent    |  Code &      |  Gate 1     |  Gate 2    | Gate 3   | Post-merge
   |  checkpoint|  test        |  (code      |  (req      | (human)  | updates
   |            |              |   quality)  |   quality) |          |
```

| State | What happens | Who acts |
|-------|-------------|----------|
| `created` | CR exists with title and intent; complexity assessed | Claude |
| `developing` | Code implementation, tests, git commits at each step | Claude |
| `verifying` | Gate 1 -- automated code quality checks; self-fix on failure | Claude |
| `in_review` | Gate 2 -- acceptance criteria comparison; review summary generated | Claude |
| `approved` | Gate 3 -- human reviews the diff summary and approves | You |
| `merged` | Branch merged, state.md updated, linked PFs refreshed | Claude |

## Key Features

### Intent Checkpoint

When a CR first enters `developing`, Claude performs a self-preparation step to lock down scope and acceptance criteria. This is not a form you fill out -- Claude does it internally and tells you "Scope confirmed, starting work."

- **Simple (S)**: Records your original request plus a free-text acceptance condition.
- **Standard (M)**: Adds a numbered acceptance criteria list and marks ambiguities with `[TBD]` tags.
- **Complex (L/XL)**: Produces full Given/When/Then acceptance criteria, an execution plan, and asks you up to 2 clarifying questions (each with a recommended answer).

If you ask "What's the plan?", Claude surfaces the full intent section including the execution plan.

### Complexity Assessment

Claude evaluates every CR across four dimensions and assigns a size: S, M, L, or XL.

| Dimension | S | M | L | XL |
|-----------|---|---|---|-----|
| Files involved | 1-3 | 4-7 | 8-15 | >15 |
| Directories | 1 | 2-3 | 4-5 | >5 |
| Acceptance criteria | 1 | 2-3 | 4+ | Multiple groups |
| Cross-module deps | None | One-way | Bidirectional | Architectural |

The highest dimension determines the final rating. L/XL CRs automatically enter the split evaluation flow, where Claude suggests breaking the work into smaller CRs.

### Adaptive Paths

Complexity drives how much ceremony the workflow applies:

| Path | Complexity | Behavior |
|------|-----------|----------|
| **Quick** | S, single file | Minimal intent record, no execution plan, straight to coding |
| **Standard** | S multi-file, M | Standard intent with numbered criteria; optional execution plan |
| **Full** | L, XL | Complete intent, mandatory execution plan, plan reflection, user confirmation gate before coding begins |

An **upgrade guard** watches for scope creep during the intent checkpoint. If an S-rated CR turns out to involve multiple modules, Claude suggests upgrading to M or L. The suggestion never blocks -- you can choose to continue at the original level.

### Execution Plan (L/XL)

For complex changes, Claude generates a step-by-step plan before writing any code:

- Each step is an atomic action corresponding to one meaningful commit.
- Steps include exact file paths, the action to take, and a verifiable expected result.
- Dependencies between steps are explicitly annotated.
- When a test strategy exists, test skeleton steps are scheduled before implementation steps.

After generating the plan, Claude performs a **plan reflection** across four dimensions (requirement coverage, over-engineering risk, split necessity, technical assumptions) and records 1-3 lines of observations. The plan is then presented to you for confirmation before coding begins.

### Gate Reflections

After each quality gate passes, Claude appends a brief self-assessment to the CR event log:

- **Gate 1 reflection**: Technical debt observations, test coverage assessment, and test-first adherence review.
- **Gate 2 reflection**: Boundary scenario coverage and acceptance completeness observations.

These reflections do not block the workflow. They accumulate quality signals that feed into experience extraction when the CR is merged.

### Drift Detection

Two complementary monitors run at every checkpoint (git commit + CR update):

- **Intent drift**: Compares changed files against the declared scope. If more than 30% of files fall outside the intent boundary, Claude flags it: "These files are outside the declared scope -- intentional expansion or scope creep?"
- **Complexity drift**: Compares actual file/directory counts against the initial complexity thresholds. If an S-rated CR has touched 4+ files, Claude suggests upgrading. Each CR is flagged at most once.

Both detections are advisory only -- they never block your workflow.

### PF Overflow Check

When a CR is created or merged, Claude checks whether the associated Product Feature (PF) has grown beyond its inline capacity in `project.md`:

- **Triggers**: >15 lines of feature spec, 3+ associated CRs, or a prior `/pace-change modify` on the PF.
- **Action**: Automatically extracts the PF into a standalone file under `.devpace/features/PF-xxx.md` and updates `project.md` with a link.
- **Zero friction**: No confirmation needed. The extraction is reported in the execution summary.

### Quick CR Switch

Multiple CRs in progress? Switch between them efficiently:

- `/pace-dev #3` -- Jump directly to CR-003 by number.
- `/pace-dev --last` -- Resume the most recently worked-on CR.
- `/pace-dev "login"` -- Match by keyword (existing behavior).

### Simplified Approval Improvements

The simplified approval path (skip `in_review` waiting) now distinguishes between cosmetic and structural self-fixes:

- **Cosmetic fixes** (lint, format, import sorting) do not count as "non-first-pass." This means more S CRs qualify for simplified approval.
- **Structural fixes** (logic errors, type errors, missing returns) still disqualify simplified approval.
- **Batch approval**: When 2+ CRs are simultaneously in `in_review` and all qualify for simplified approval, Claude offers a batch confirmation prompt.

### L/XL Step-Level Progress

For L/XL CRs with execution plans, each step completion produces:

1. A step checkpoint marker in the CR event log (`[checkpoint: step-3-done]`).
2. A step-level locator in state.md (`→ Step 3/5: middleware implementation`).
3. A one-line progress notification to the user: `[Step 3/5] middleware implementation complete ✅`.

This enables precise cross-session recovery -- the next session resumes at exactly the right step.

### Execution Plan Editing

During the confirmation gate for L/XL CRs, you can adjust the plan using natural language:

- "Delete step 3" / "Merge steps 4 and 5" / "Add a step after step 2: ..." / "Swap steps 3 and 4"
- Claude applies the changes and re-presents the updated plan for confirmation.
- You can also set **pause points**: "Pause after step 3" -- Claude will stop there with a progress summary and wait for confirmation before continuing.

### Explore-to-Advance Context Inheritance

When switching from explore mode to advance mode within the same session, Claude automatically extracts relevant context from the preceding discussion:

- Solution choices and their rationale
- Discovered constraints and dependencies
- Conclusions reached during exploration

This context is pre-filled into the CR intent section with source attribution, eliminating the need to re-explain decisions already made.

### Mid-Development Compact Suggestion

For L/XL CRs past 60% of the execution plan, Claude may suggest `/compact` when the current step is independent from previous ones -- freeing context space for the remaining work.

### Inline Exploration During Advance

If you need to think or discuss alternatives mid-implementation ("let me think..." / "is there a better approach?"), Claude pauses the advance workflow for free discussion, then resumes seamlessly when you say "continue." Discussion outcomes automatically update the CR intent.

## Usage Scenarios

### Scenario 1: Quick Bug Fix

```
You:    /pace-dev "fix null check in auth middleware"
Claude: Found no existing CR. Creating CR-012 (type: defect, severity: medium).
        Scope confirmed, starting work.

        ... (implements fix, adds test, commits) ...

        Change summary
        - Files: modified 1 / added 1
        - CR status: created --> developing --> verifying --> in_review
        - Gate 1: passed. Gate 2: passed.
        Ready for your review. Approve to merge?
```

### Scenario 2: Multi-Module Feature (L)

```
You:    /pace-dev "add role-based access control"
Claude: CR-013 created. Complexity: L (8 files, 4 directories, bidirectional deps).
        Suggesting split into 2 CRs:
        - CR-013a: Role model + permission middleware
        - CR-013b: Admin UI for role assignment
        Dependencies: CR-013a before CR-013b.
        Split or continue as one CR?

You:    Split.
Claude: Created CR-013a and CR-013b. Starting CR-013a.
        Here is the execution plan (5 steps):
        1. Define Role schema in models/role.ts ...
        ...
        Confirm to start, or adjust?

You:    Go ahead.
Claude: ... (autonomous implementation with checkpoints) ...
```

### Scenario 3: Resuming Interrupted Work

```
You:    /pace-dev
Claude: Resuming CR-010 (state: developing, step 3/5 of execution plan).
        Last checkpoint: "completed API route, next: write integration tests."
        Continuing from step 4.
```

## Integration with Other Commands

| Command | Relationship to `/pace-dev` |
|---------|-----------------------------|
| `/pace-init` | Initializes the `.devpace/` project structure that `/pace-dev` operates within |
| `/pace-review` | Auto-invoked when CR reaches `in_review`; generates the diff summary for Gate 2 |
| `/pace-test` | Can be called during development to generate test skeletons aligned with acceptance criteria |
| `/pace-change` | Handles requirement changes (add/remove/modify PFs); `/pace-dev` is for implementation |
| `/pace-sync` | After CR state transitions, the sync-push hook reminds you to push status to GitHub |
| `/pace-status` | Shows current CR state and project progress at any time |
| `/pace-guard` | Risk pre-scan is invoked during the intent checkpoint for L/XL CRs |
| `/pace-next` | Suggests the next action after a CR is merged or when no work is in progress |

## Related Resources

- [dev-procedures.md](../../skills/pace-dev/dev-procedures.md) -- Detailed execution procedures (intent checkpoint, adaptive paths, drift detection, gate reflections)
- [cr-format.md](../../knowledge/_schema/cr-format.md) -- CR file schema (fields, states, event log format)
- [devpace-rules.md](../../rules/devpace-rules.md) -- Runtime behavior rules (advance mode constraints, dual-mode system)
- [User Guide](../user-guide.md) -- Quick reference for all commands
