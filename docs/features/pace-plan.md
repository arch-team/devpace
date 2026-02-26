# Iteration Planning (`/pace-plan`)

`/pace-plan` is devpace's iteration planning skill. It manages the complete lifecycle of iterations -- from closing the current iteration to planning the next one -- bridging the "plan → execute → review" loop in the product cycle. Unlike `/pace-change` which handles Product Feature (PF) level requirement changes, `/pace-plan` operates at the iteration scope level, deciding which PFs to include in each iteration and managing capacity constraints.

## Quick Start

```
1. /pace-plan              --> Assess current iteration status, suggest next action
2. /pace-plan next         --> Plan a new iteration (with Plan Proposal)
3. /pace-plan close        --> Close current iteration (auto retrospective)
4. /pace-plan adjust       --> Mid-iteration scope adjustment
5. /pace-plan health       --> Show iteration health metrics
```

## Subcommands

| Subcommand | When to Use | What It Does |
|------------|-------------|--------------|
| `(empty)` | Check iteration status | Assess completion rate and suggest next steps (close or continue) |
| `next` | Start a new iteration | Plan next iteration with guided flow and Plan Proposal |
| `close` | End current iteration | Close iteration with auto lightweight retrospective and archival |
| `adjust` | Mid-iteration | Add/remove PFs or reprioritize within current iteration |
| `health` | Monitor progress | Show health metrics (completion vs time, scope stability) |

## Core Features

### Empty Feature Tree Guided Planning

When `project.md` has no active or pending PFs, `/pace-plan next` enters guided planning mode -- asking the user to describe their iteration goal in 1-2 sentences, inferring PFs from the description, and populating `project.md` with traceability markers. This eliminates the cold start problem.

### Plan Proposal (Smart Suggestion)

Instead of manual PF selection, Claude generates a complete iteration plan proposal with auto-derived goals, priority-based PF selection (deferred PFs first → dependency-satisfied → project.md order), effort estimation, and capacity assessment. Users confirm or adjust in natural language. Detailed generation logic and format in [plan-procedures.md](../../skills/pace-plan/plan-procedures.md) Step 3.7.

### Estimation (Heuristic and Historical)

Estimation adapts to available data: with historical data from `dashboard.md`, it uses actual velocity and CR cycle times (definitions in `knowledge/metrics.md`); without historical data, it falls back to heuristic S/M/L sizing based on acceptance criteria count. First iteration defaults to 3-5 PF capacity cap. Detailed rules in [plan-procedures.md](../../skills/pace-plan/plan-procedures.md) Step 3.3.

### Planning Enhancements

- **BR grouping**: When ≥5 candidate PFs, groups them by parent Business Requirement to reduce cognitive load.
- **Dependency validation**: Checks PF dependency fields, alerts on unmet prerequisites.
- **Risk integration**: When `.devpace/risks/` exists, surfaces high/medium risk markers and adds 30% estimation buffer for high-risk PFs.
- **Retrospective link**: Displays last iteration's "Recommendations for Next Iteration" to close the feedback loop.

### Auto Lightweight Retrospective on Close

`/pace-plan close` archives `current.md` as `iter-N.md`, auto-extracts 3 baseline metrics (PF completion rate, average CR cycle, iteration velocity -- definitions in `knowledge/metrics.md`), and updates `dashboard.md`. Full retrospective via `/pace-retro` remains optional. Detailed flow in [close-procedures.md](../../skills/pace-plan/close-procedures.md).

### Mid-Iteration Scope Adjustment (adjust)

Adds/removes PFs or reprioritizes within the current iteration, with capacity recalculation after each operation. Boundary with `/pace-change`: change manages PF-level requirement changes, adjust manages iteration scope. Detailed flow in [adjust-procedures.md](../../skills/pace-plan/adjust-procedures.md).

### Iteration Health Metrics (health)

Displays completion vs time progress, scope change count, PF status distribution, and velocity trend. Assesses health as on-track / at-risk / scope-unstable, with pulse signal integration for low health detection. Detailed flow in [health-procedures.md](../../skills/pace-plan/health-procedures.md).

## Usage Scenarios

### Scenario 1: First Iteration Planning (Empty Feature Tree)

```
You:    /pace-plan next
Claude: No active or pending PFs found. Let's start from your goals.
        What do you want to achieve in this iteration? Describe in 1-2 sentences.

You:    Build user authentication with login and registration
Claude: Based on your description, I inferred these features:
        - PF-001: User login with email/password
        - PF-002: User registration with email verification
        - PF-003: Password reset flow
        Confirm or adjust?

You:    Looks good
Claude: PFs added to project.md.

        Suggested Plan:
          Goal: Complete user authentication features
          PFs to Include (3 total):
            [P0] PF-001 User login — Estimated M (2-4 CRs)
            [P0] PF-002 User registration — Estimated M (2-4 CRs)
            [P1] PF-003 Password reset — Estimated S (1-2 CRs)
          Total Estimated Effort: ~7-10 sessions
          Timeframe: [Next 2 weeks if specified]

        Confirm this plan?

You:    Yes
Claude: Iteration planned and saved to .devpace/iterations/current.md.
        Highest priority: PF-001 User login. Start now?

You:    Let's go
Claude: Suggest running: /pace-dev "implement PF-001"
```

### Scenario 2: Planning with Historical Data

```
You:    /pace-plan next
Claude: Last iteration completed 4/5 PFs (80% velocity).
        2 PFs deferred from last iteration.
        Last retrospective recommended: "Focus on smaller PFs to improve completion rate."

        Suggested Plan:
          Goal: Complete deferred features + checkout flow
          PFs to Include (4 total):
            [P0] PF-005 User profile (deferred) — Est: 2.5 sessions (historical avg)
            [P0] PF-008 Email notifications (deferred) — Est: 1.8 sessions
            [P1] PF-012 Shopping cart — Est: 3.2 sessions
            [P2] PF-014 Payment integration — Est: 4.5 sessions ⚠️ High risk (+30%)
          Total: ~12 sessions vs capacity of 15 sessions

        Confirm or adjust?

You:    Remove PF-014, too risky
Claude: Adjusted. Removing PF-014.

        Updated Plan:
          PFs to Include (3 total):
            [P0] PF-005 User profile — 2.5 sessions
            [P0] PF-008 Email notifications — 1.8 sessions
            [P1] PF-012 Shopping cart — 3.2 sessions
          Total: ~7.5 sessions (well under capacity)

        Confirm?

You:    Good
Claude: Iteration saved. Start with PF-005?
```

### Scenario 3: Mid-Iteration Adjustment

```
You:    /pace-plan adjust
Claude: Current iteration status:
          Goal: Complete user authentication
          Progress: 2/4 PFs completed (50%)
          Remaining: PF-003 (in progress), PF-004 (pending)
          Capacity: ~5 sessions used, ~3 remaining

        What adjustment do you need?

You:    Remove PF-004, add PF-007 instead
Claude: Checking capacity...
        - Removing PF-004 frees ~2 sessions
        - Adding PF-007 requires ~3 sessions
        - New total: ~6 sessions remaining

        Adjustment possible. Confirm?

You:    Yes
Claude: Updated current.md.
        Change logged: "Mid-iteration adjustment: swap PF-004 → PF-007 due to priority shift."
```

### Scenario 4: Iteration Health Check

```
You:    /pace-plan health
Claude: Iteration Health Report:
          Time elapsed: 60% (6 days of 10-day iteration)
          PF completion: 40% (2/5 completed)
          Status distribution: ✅2 🔄1 ⏳2
          Scope changes: 0 (stable)

        ⚠️ At Risk: Completion rate (40%) behind time progress (60%).
        Velocity needed: 1.5x current pace to complete on time.

        Suggestions:
        1. Run /pace-plan adjust to reduce scope
        2. Check if in-progress CR is blocked
        3. Consider extending iteration timeframe
```

### Scenario 5: Iteration Closure

```
You:    /pace-plan close
Claude: Closing current iteration...

        Final Status:
          Planned: 5 PFs
          Completed: 4 PFs (80%)
          Deferred: 1 PF (PF-015)

        Auto retrospective metrics:
          - PF completion rate: 80%
          - Avg CR cycle: 2.3 days
          - Iteration velocity: 0.8

        Metrics updated in dashboard.md.
        Iteration archived to iter-03.md.

        Suggest running /pace-retro for full retrospective analysis.

        Ready to plan next iteration?
```

## Integration with Other Commands

| Command | Relationship to `/pace-plan` |
|---------|------------------------------|
| `/pace-init` | Initializes `.devpace/` structure that iterations operate within |
| `/pace-change` | Handles PF-level requirement changes; may trigger `/pace-plan adjust` suggestion if capacity exceeded |
| `/pace-dev` | Execution phase; `/pace-plan` guides handoff to `/pace-dev` after planning |
| `/pace-retro` | Full retrospective; `/pace-plan close` performs lightweight auto retrospective, suggests `/pace-retro` for deep analysis |
| `/pace-status` | Shows current iteration progress alongside overall project status |
| `/pace-guard` | Risk scanning integrated into planning; high-risk PFs get estimation buffer |
| `/pace-pulse` | Health metrics feed pulse signals; low health triggers pulse detection |
| `/pace-next` | May suggest `/pace-plan next` when iteration ends or no active work |

## Degradation Behavior

When certain data is missing, `/pace-plan` degrades gracefully:

| Missing Data | Degradation |
|--------------|-------------|
| `project.md` empty | Guided planning mode: elicit user goal → infer PFs → populate tree |
| No historical data | Heuristic estimation (S/M/L based on acceptance criteria count) |
| No iteration timeframe | Capacity checks skip time-based warnings, show only PF count limits |
| No `dashboard.md` | Skip velocity-based limits, use heuristic cap (3-5 PFs for first iteration) |
| No last retrospective | Skip recommendation display, continue normal planning |
| No `.devpace/risks/` | Skip risk integration, no high-risk markers |
| Empty `current.md` | `/pace-plan adjust` / `health` prompt "No active iteration, run `/pace-plan next` first" |

## Related Resources

- [plan-procedures.md](../../skills/pace-plan/plan-procedures.md) -- Step 3+4: New iteration planning (candidate PFs, estimation, Plan Proposal, file generation)
- [close-procedures.md](../../skills/pace-plan/close-procedures.md) -- Step 2: Iteration closure (archival, auto lightweight retrospective, dashboard update)
- [adjust-procedures.md](../../skills/pace-plan/adjust-procedures.md) -- Step 2.5: Mid-iteration scope adjustment (add/remove PFs, reprioritize, capacity recalculation)
- [health-procedures.md](../../skills/pace-plan/health-procedures.md) -- Step 5: Iteration health metrics (completion vs time, scope stability, velocity trend)
- [iteration-format.md](../../knowledge/_schema/iteration-format.md) -- Iteration file schema (fields, PF list format, change log)
- [devpace-rules.md](../../rules/devpace-rules.md) -- Runtime behavior rules (iteration lifecycle integration)
- [User Guide](../user-guide.md) -- Quick reference for all commands
