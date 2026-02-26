# Requirements Change Management (`/pace-change`)

In most AI-assisted workflows, requirement changes are disruptive events handled ad hoc — a comment here, a manual file edit there, and scattered notes that no one can trace back. devpace treats changes as **first-class citizens**. `/pace-change` provides structured triage, multi-layer impact analysis, risk quantification, and traceable execution, so that shifting requirements never derail the development rhythm.

## Quick Start

```
1. /pace-change add "support OAuth login"   → Triage → Impact analysis → Proposal
2. User confirms proposal                   → Execute changes across all project files
3. Changes recorded in iteration log        → Full traceability maintained
```

Or let Claude guide you interactively:

```
You:    /pace-change
Claude: What kind of change? (add / pause / resume / reprioritize / modify)
```

## Workflow

### Step 1: Triage

Not every change request warrants a full analysis. Before diving into impact assessment, `/pace-change` routes each request through a triage gate:

| Decision | Meaning | What happens next |
|----------|---------|-------------------|
| **Accept** | Proceed with full analysis | Continue to impact analysis |
| **Decline** | Reject with recorded rationale | Log reason, end |
| **Snooze** | Defer until a trigger condition is met | Log reason + trigger condition, end |

Claude auto-suggests a triage decision based on alignment with the current iteration goal, urgency, and project direction. Hotfix/critical changes bypass triage entirely. The user can always override the suggestion.

### Step 2: Impact Analysis (4-Layer)

Accepted changes go through a **BR-to-code impact trace** — the same value chain that devpace maintains from business requirements down to code changes:

1. **Business Requirement (BR) layer** — Does this affect an entire business goal? Are success metrics (MoS) at risk?
2. **Product Feature (PF) layer** — Which features are impacted? How many need scope or acceptance-criteria changes?
3. **Change Request (CR) layer** — Which in-progress or planned CRs are affected? What dependencies exist?
4. **Code layer** — Which modules, files, and interfaces will need modification?

The analysis result is reported in **plain language** — feature names instead of IDs, status descriptions instead of state-machine jargon.

When a change affects 50% or more of a BR's features (or the user explicitly targets a BR), the report elevates to a BR-level view showing the full downstream cascade.

### Step 3: Risk Quantification

After impact analysis, `/pace-change` produces a semi-quantitative risk summary across three dimensions:

| Dimension | Low | Medium | High |
|-----------|:---:|:------:|:----:|
| Modules affected | <=2 | 3-5 | >5 |
| In-progress CRs impacted | 0 | 1-2 | >=3 |
| Quality checks to reset | 0 | 1-3 | >3 |

Overall risk: **Low** (all dimensions low), **Medium** (any medium, no high), or **High** (any high). High-risk changes additionally receive suggested testing focus areas and a phased execution strategy.

If a CR already contains an impact analysis section (written by `/pace-test impact`), that data is reused rather than re-evaluated.

### Step 4: Proposal and Confirmation

Claude presents a concrete adjustment plan — new CRs to create, states to transition, quality checks to reset, iteration capacity implications — and **waits for explicit user confirmation** before making any changes. Nothing is modified until you say "go."

### Step 5: Execute and Record

Upon confirmation, all affected project files are updated atomically:

1. **CR files** — state, intent, quality checks, event log
2. **project.md** — feature tree (new entries, pause/resume markers, status changes)
3. **PF files** — acceptance criteria updates + history annotations (for `modify` on spilled-out features)
4. **iterations/current.md** — change log entry (when iteration tracking is active)
5. **state.md** — current work snapshot and next-step suggestions
6. **git commit** — all changes recorded in a single traceable commit

### Step 6: External Sync Check

After execution, `/pace-change` checks whether any affected CRs are linked to external issues (e.g., GitHub Issues). If so, it reminds you to run `/pace-sync push` to keep external tools in sync. It never pushes automatically — you stay in control.

## Change Types

| Type | Syntax | Description |
|------|--------|-------------|
| **add** | `/pace-change add <description>` | Insert a new requirement. Creates PF + CR entries, evaluates iteration capacity. |
| **pause** | `/pace-change pause <feature>` | Suspend a feature. All associated CRs move to `paused`, prior state is preserved, dependencies are unblocked. Feature tree shows a pause marker. |
| **resume** | `/pace-change resume <feature>` | Restore a paused feature. CRs return to their pre-pause state. Quality checks are re-validated against any code changes made during the pause window. |
| **reprioritize** | `/pace-change reprioritize <description>` | Adjust priority order. Updates next-step recommendations and reshuffles the iteration plan. |
| **modify** | `/pace-change modify <feature> <change>` | Change scope or acceptance criteria of an existing feature. Affected quality checks are reset. PF files are updated with history annotations. |

Omitting the type argument starts an interactive dialog where Claude helps you identify the right change type.

## Key Features

### Structured Triage Routing

Every change request passes through Accept/Decline/Snooze before consuming analysis effort. This prevents low-value or premature requests from disrupting active work while ensuring nothing is silently dropped.

### BR-Level Impact View

When a change is large enough to affect an entire business requirement, the impact report automatically elevates from feature-level to BR-level, showing the full cascade: business goal impact, success metric risk, all affected features, and all affected CRs.

### PF File Writes on Modify

When modifying acceptance criteria for a feature that has been spilled out to its own file (`features/PF-xxx.md`), `/pace-change` updates the file directly and appends a history annotation. For features still inline in `project.md`, it updates there and checks whether the modification triggers a spill-out.

### 5-Dimension Risk Quantification

Beyond simple "this looks risky" assessments, `/pace-change` scores three measurable dimensions and derives an overall L/M/H risk level, with actionable guidance for high-risk changes (testing focus areas, phased execution).

### External Sync Check

After any state-changing operation, `/pace-change` checks for external issue associations and prompts sync when needed — keeping your GitHub Issues (or other tools) consistent without automatic side effects.

## Degraded Mode

When `.devpace/` has not been initialized, `/pace-change` still works — it degrades gracefully instead of failing:

- **Triage** simplifies to a verbal confirmation: "Handle this now or note it for later?"
- **Impact analysis** scans the codebase directly using `Glob`/`Grep`/`Read`, analyzes `import`/`require` dependency graphs, and identifies affected modules and risk areas
- **Risk quantification** evaluates module spread from the dependency graph; CR and quality-check dimensions are marked "not available"
- **Execution** operates on code only — no `.devpace/` files are created or modified
- **Completion** naturally mentions: "Full initialization enables persistent traceability, quality gates, and metrics. Run `/pace-init` to get started."

This means you can use `/pace-change` on any project at any time, even before deciding to adopt devpace fully.

## Usage Scenarios

### Scenario 1: Insert a New Requirement Mid-Sprint

A stakeholder requests OAuth login support while the team is focused on core API development.

```
You:    /pace-change add "support OAuth login via Google and GitHub"
Claude: Triage: This is a new feature unrelated to the current API sprint.
        Recommendation: Snooze until API milestone completes.
        Accept / Decline / Snooze?

You:    Accept — the client needs it for the demo.
Claude: Impact analysis:
        - This adds a new feature under "User Authentication"
        - 2 new change requests needed (Google OAuth, GitHub OAuth)
        - Current iteration has capacity for 1 more CR; the second
          would push "rate limiting" to next iteration.
        - Risk: Low (2 modules, 0 in-progress CRs affected)

        Proposal: Create 2 CRs, defer "rate limiting" to next iteration.
        Proceed?

You:    Yes
Claude: Done. 2 CRs created, iteration plan updated, rate limiting deferred.
        Next suggested step: /pace-dev CR-007
```

### Scenario 2: Pause a Feature

The team decides to shelve the notification system to focus on higher-priority work.

```
You:    /pace-change pause notification system
Claude: Impact analysis:
        - "Notification System" has 3 CRs: 1 in progress, 2 planned
        - The in-progress CR (email notifications) has passed Gate 1
        - No other features depend on notifications
        - Risk: Low

        Proposal: Pause all 3 CRs, preserve current progress,
        mark feature tree with pause indicator.
        Proceed?

You:    Go ahead
Claude: Done. 3 CRs paused, feature tree updated.
        CR-004 progress preserved (Gate 1 passed, branch intact).
        Resume anytime with: /pace-change resume notification system
```

### Scenario 3: Modify Acceptance Criteria

After user testing, the team wants to tighten the search feature's response time requirement.

```
You:    /pace-change modify search "response time must be under 200ms, not 500ms"
Claude: Impact analysis:
        - "Search" feature acceptance criteria changing: 500ms → 200ms
        - CR-005 (search implementation) is in progress, Gate 1 passed
        - Performance-related quality checks need reset
        - Risk: Medium (1 in-progress CR, 2 checks to reset)

        Proposal: Update acceptance criteria in PF file, reset
        performance checks on CR-005, add history annotation.
        Proceed?

You:    Yes
Claude: Done. Acceptance criteria updated, 2 quality checks reset on CR-005.
        History annotation added to PF file.
        Suggested: re-run /pace-dev CR-005 to address the tighter requirement.
```

## Integration with Other Commands

| Command | Relationship |
|---------|-------------|
| `/pace-dev` | After a change is executed, `/pace-dev` picks up new or modified CRs for implementation. Paused CRs are excluded from the dev queue. |
| `/pace-plan` | `/pace-change add` creates PF and CR entries that become part of the plan. Reprioritize adjustments are reflected in `/pace-plan`'s iteration view. |
| `/pace-sync` | After state-changing operations, `/pace-change` checks for external associations and prompts a sync push. |
| `/pace-test` | Quality checks reset by `modify` are re-evaluated during the next `/pace-test` gate review. Impact data from `/pace-test impact` is reused in `/pace-change` risk quantification. |
| `/pace-status` | Reflects all changes made by `/pace-change` — paused features, new CRs, updated priorities. |

## Related Resources

- [User Guide — /pace-change section](../user-guide.md) — Quick reference
- [Design Document — Change Management](../design/design.md) — Architecture and design principles
- [change-procedures.md](../../skills/pace-change/change-procedures.md) — Detailed operational procedures
- [cr-format.md](../../knowledge/_schema/cr-format.md) — CR file schema (includes `paused` state definition)
- [devpace-rules.md](../../rules/devpace-rules.md) — Runtime behavior rules
