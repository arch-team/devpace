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

When `project.md` is in stub state (no active or pending PFs), `/pace-plan next` enters guided planning mode:

- **User goal elicitation**: Asks "What do you want to achieve in this iteration? Describe in 1-2 sentences."
- **PF inference**: Extracts keywords from user's description and infers PFs (similar to `pace-init --from` logic).
- **Auto-populate**: Writes inferred PFs to `project.md` with `<!-- source: claude -->` traceability marker.
- **Confirmation**: Shows inferred PFs for user approval or adjustment before proceeding.

This eliminates the cold start problem -- you can jump into iteration planning without manually writing PFs first.

### Plan Proposal (Smart Suggestion)

Instead of asking users to manually select PFs, Claude generates a complete iteration plan proposal:

**Generation Logic**:
1. **Goal synthesis**: Derives iteration goal from candidate PFs' business requirements (e.g., "Complete user authentication features").
2. **PF selection strategy** (priority-based):
   - a. Deferred PFs from last iteration (highest priority)
   - b. PFs with satisfied dependencies
   - c. Follow the order in `project.md` (implied priority)
   - d. Capacity cap: Don't exceed last iteration's actual completion count (defaults to 3-5 PFs for first iteration)
3. **Estimation**: Attach effort estimation to each PF (historical data if available, heuristics otherwise).
4. **Capacity assessment**: Sum up estimates and compare against iteration timeframe (if set).

**Proposal Format**:
```
Suggested Plan:
  Goal: [Auto-derived 1-line goal]
  PFs to Include (N total):
    [P0] PF-001 xxx — Estimated M (2-4 CRs) [Deferred from last iteration]
    [P1] PF-003 xxx — Estimated S (1-2 CRs)
    [P2] PF-005 xxx — Estimated L (4-7 CRs) ⚠️ High risk
  Total Estimated Effort: ~X work sessions
  Timeframe: [Start-End dates, if previously set]

Confirm this plan? Or need adjustments?
```

**User Response Branches**:
- "OK / Confirm / Yes" → Accept proposal as-is.
- "Adjust: remove X, add Y" → Incremental modification, re-display proposal.
- Full alternative plan → Use user's custom plan.
- Priority adjustment → Update P0/P1/P2 markers.

### Heuristic Estimation (No Historical Data)

For the first iteration or when no historical data exists, estimation falls back to heuristics:

| PF Complexity | Heuristic Rule | Estimated CRs | Effort (sessions) |
|---------------|----------------|---------------|-------------------|
| **S** (Simple) | No acceptance criteria or <1 criteria | 1-2 CRs | ~1-2 sessions |
| **M** (Medium) | 1-2 acceptance criteria | 2-4 CRs | ~2-4 sessions |
| **L** (Large) | ≥3 acceptance criteria | 4-7 CRs | ~4-7 sessions |

- **Trigger condition**: No `dashboard.md` and no `iterations/iter-*.md` files.
- **First iteration cap**: Defaults to 3-5 PFs to avoid over-commitment.
- **Auto-upgrade**: Once the first iteration completes, estimation automatically switches to historical data mode.

Heuristic estimation is clearly marked: "Heuristic estimation (no historical data). Will switch to historical data after first iteration completes."

### Historical Velocity Limiting

When historical data exists:

- **Data source**: `.devpace/metrics/dashboard.md` for average CR cycle time and iteration velocity.
- **Capacity cap**: If velocity < 1.0, suggest including no more than `last iteration actual completion count` PFs.
- **Warning**: "Historical velocity is X%, suggest including at most N PFs."
- **Overrun alert**: If estimated effort exceeds iteration timeframe, add suggestion: "Estimated effort may exceed iteration timeframe. Suggest reducing N PFs or extending iteration."

### Candidate PF Grouping by Business Requirement

When ≥5 PFs are available for selection:

- **Grouping**: Group PFs by their parent Business Requirement (BR) in `project.md`.
- **Summary output**: Display group summary (PF count + overview per BR).
- **Drill-down**: User can specify a BR to expand and see detailed PFs within that group.
- **Flat listing**: When <5 PFs, list all directly without grouping.

This reduces cognitive load when choosing from a large PF pool.

### PF Dependency Validation

If a PF has a `dependencies` field in its specification:

- **Check**: Validate whether dependent PFs are completed or scheduled earlier in the current iteration.
- **Alert**: If dependency unsatisfied → "PF-002 depends on PF-001 ([reason]). Suggest including PF-001 first or confirm parallel work is possible."
- **Skip**: If no `dependencies` field, skip validation.

This prevents planning PFs with unmet prerequisites.

### Risk Integration (pace-guard)

When `.devpace/risks/` exists:

- **Scan**: Match candidate PFs against open risk entries via `affected_pf` field.
- **High risk**: Mark as "⚠️ High risk" + add 30% buffer to estimation (e.g., M 3CR → 4CR).
- **Medium risk**: Mark as "⚡ Medium risk" (no estimation adjustment).
- **Fallback**: If no matching risks or `risks/` absent, silently skip.

Risk information is automatically surfaced during planning without manual lookup.

### Last Retrospective Recommendations Direct Link

When planning a new iteration:

- **Source**: Read last archived iteration `iter-N.md` (N = latest) for retrospective section.
- **Display**: If "Recommendations for Next Iteration" section exists, show to user: "Last retrospective recommended: [content]."
- **Skip**: If no retrospective section or no recommendations, silently skip.

This closes the feedback loop from retrospective to planning.

### Auto Lightweight Retrospective on Close

When closing an iteration (`/pace-plan close`):

1. **Archive**: Rename `current.md` to `iter-N.md` with completion snapshot.
2. **Extract metrics** (auto, no user input):
   - PF completion rate (planned vs actual)
   - Average CR cycle time (created → merged in days)
   - Iteration velocity (actual completed PFs / planned PFs)
3. **Update dashboard**: Append or update these 3 metrics in `.devpace/metrics/dashboard.md`.
4. **Output**: "This iteration: X% completion, N days avg CR cycle, Y velocity."
5. **Suggest full retrospective**: Recommend running `/pace-retro` for comprehensive analysis (not auto-invoked).

This ensures `dashboard.md` baseline data is never missing, while full retrospective remains optional.

### Mid-Iteration Scope Adjustment (adjust)

For changes to iteration scope after planning:

**Boundary with /pace-change**:
- `/pace-change`: PF-level requirement changes (add/pause/resume/modify features).
- `/pace-plan adjust`: Iteration scope-level adjustments (which PFs to include in current iteration).

**Operations**:
1. **Display current state**: Goal, PF list (with completion status), remaining capacity.
2. **Adjustment actions** (via `AskUserQuestion`):
   - **Add PF**: Select from `project.md` pending PFs, with effort estimation.
   - **Remove PF**: Move unstarted PFs back to pending pool (started PFs should use `/pace-change pause`).
   - **Reprioritize**: Re-rank P0/P1/P2 priorities within current iteration.
3. **Recalculate capacity** after each operation:
   - Sum up estimated effort for all current iteration PFs.
   - Compare against iteration timeframe (if set).
   - **Overrun warning**: "Adjusted effort is X sessions, exceeds remaining capacity Y. Suggest removing lower-priority PFs."
4. **Update `current.md`**: PF list + priorities + append adjustment reason to change log.
5. **No closure**: Iteration remains open, no archival.

### Iteration Health Metrics (health)

Show health indicators for current iteration:

**Metrics Displayed**:
1. **Completion vs Time Progress**: PF completion rate / iteration time elapsed ratio (if timeframe set); otherwise just PF completion %.
2. **Scope Change Count**: Number of entries in `current.md` change log (reflects scope stability).
3. **PF Status Distribution**: Count of ✅ completed / 🔄 in progress / ⏳ pending / ⏸️ paused.
4. **Velocity Trend**: Compare with last iteration velocity (if `dashboard.md` exists).

**Health Assessment**:
- **Healthy**: "Iteration on track: X% completion, progressing as planned."
- **At risk**: "May delay: X% completion but Y% time elapsed. Suggest `/pace-plan adjust` to reduce scope."
- **Scope instability**: "Scope changed N times. Consider requirements stability."

**pace-pulse Integration**: When health below threshold (completion rate / time progress < 0.5), mark as pulse-detectable signal.

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

## Plan Proposal vs Manual Selection

**Traditional Iteration Planning** (manual):
1. List all candidate PFs
2. User manually picks which PFs to include
3. User sets priorities
4. User estimates effort (or skips)
5. Tool generates `current.md`

**Plan Proposal** (devpace):
1. Tool analyzes candidate PFs + historical data + constraints
2. Tool generates complete suggested plan with reasoning
3. User confirms or adjusts in natural language
4. Tool applies adjustments and regenerates proposal
5. Tool generates `current.md` once approved

**Benefits**:
- **Faster**: One confirmation vs multiple choices.
- **Guided**: Users see a concrete plan, easier to adjust than build from scratch.
- **Informed**: Proposal reflects velocity limits, dependencies, risks automatically.
- **Flexible**: Still supports full custom plans if user prefers.

## Related Resources

- [plan-procedures.md](../../skills/pace-plan/plan-procedures.md) -- Step 3+4: New iteration planning (candidate PFs, estimation, Plan Proposal, file generation)
- [close-procedures.md](../../skills/pace-plan/close-procedures.md) -- Step 2: Iteration closure (archival, auto lightweight retrospective, dashboard update)
- [adjust-procedures.md](../../skills/pace-plan/adjust-procedures.md) -- Step 2.5: Mid-iteration scope adjustment (add/remove PFs, reprioritize, capacity recalculation)
- [health-procedures.md](../../skills/pace-plan/health-procedures.md) -- Step 5: Iteration health metrics (completion vs time, scope stability, velocity trend)
- [iteration-format.md](../../knowledge/_schema/iteration-format.md) -- Iteration file schema (fields, PF list format, change log)
- [devpace-rules.md](../../rules/devpace-rules.md) -- Runtime behavior rules (iteration lifecycle integration)
- [User Guide](../user-guide.md) -- Quick reference for all commands
