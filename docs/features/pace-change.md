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
Claude: [Smart recommendation based on project context]
        Or choose: add / pause / resume / reprioritize / modify / batch
```

## Workflow

### Step 0: Experience Preload

Before analysis begins, `/pace-change` reads `insights.md` for historical patterns matching the current change type. Historical data is referenced in impact reports, and rollback patterns elevate risk levels. No history? Silently skipped.

### Step 1: Triage

Not every change request warrants a full analysis. Before diving into impact assessment, `/pace-change` routes each request through a triage gate:

| Decision | Meaning | What happens next |
|----------|---------|-------------------|
| **Accept** | Proceed with full analysis | Continue to impact analysis |
| **Decline** | Reject with recorded rationale | Log reason, end |
| **Snooze** | Defer until a trigger condition is met | Persist record + trigger condition, end. Pulse auto-checks trigger conditions at session start, new iteration, and CR merge |

Claude auto-suggests a triage decision based on alignment with the current iteration goal, urgency, and project direction. Hotfix/critical changes bypass triage entirely. The user can always override the suggestion.

### Step 2: Impact Analysis (4-Layer, 3-Tier Output)

Accepted changes go through a **BR-to-code impact trace** — the same value chain that devpace maintains from business requirements down to code changes:

1. **Business Requirement (BR) layer** — Does this affect an entire business goal? Are success metrics (MoS) at risk?
2. **Product Feature (PF) layer** — Which features are impacted? How many need scope or acceptance-criteria changes?
3. **Change Request (CR) layer** — Which in-progress or planned CRs are affected? What dependencies exist?
4. **Code layer** — Which modules, files, and interfaces will need modification?

**Three-tier progressive output** (aligned with design.md §2):
- **Surface** (default): 1-line conclusion — "This change affects 2 features, risk is low."
- **Middle** (on follow-up or medium risk): 3-5 lines with affected features and risk summary
- **Deep** (on further follow-up or high risk): Full 4-layer trace, risk matrix, dependency chains, optional Mermaid visualization

For medium/high risk changes, transitive dependencies are traced up to 3 layers deep (CR-A → CR-B → CR-C).

When a change affects 50% or more of a BR's features (or the user explicitly targets a BR), the report elevates to a BR-level view showing the full downstream cascade.

### Step 3: Risk Quantification + Cost Estimation

After impact analysis, `/pace-change` produces a semi-quantitative risk summary across three dimensions:

| Dimension | Low | Medium | High |
|-----------|:---:|:------:|:----:|
| Modules affected | <=2 | 3-5 | >5 |
| In-progress CRs impacted | 0 | 1-2 | >=3 |
| Quality checks to reset | 0 | 1-3 | >3 |

Overall risk: **Low** (all dimensions low), **Medium** (any medium, no high), or **High** (any high). High-risk changes additionally receive suggested testing focus areas and a phased execution strategy.

**Cost estimation**: Based on historical data from `insights.md` (when available) or heuristic rules, an estimated additional effort is appended to help decision-making.

If a CR already contains an impact analysis section (written by `/pace-test impact`), that data is reused rather than re-evaluated.

### Step 4: Proposal, Preview, and Confirmation

Claude presents a concrete adjustment plan — new CRs to create, states to transition, quality checks to reset, iteration capacity implications — along with a **preview of affected files**. The user can request `--dry-run` to see only the preview without execution.

**Nothing is modified until you say "go."**

### Step 5: Execute and Record

Upon confirmation, all affected project files are updated atomically:

1. **CR files** — state, intent, quality checks, event log
2. **project.md** — feature tree (new entries, pause/resume markers, status changes)
3. **PF files** — acceptance criteria updates + history annotations (for `modify` on spilled-out features)
4. **iterations/current.md** — change log entry (when iteration tracking is active)
5. **state.md** — current work snapshot and next-step suggestions
6. **dashboard.md** — change management metrics (incremental update)
7. **git commit** — all changes recorded in a single traceable commit

### Step 6: Downstream Guidance + External Sync

After execution, `/pace-change` provides **type-specific next-step guidance**:

| Change type | Guidance |
|-------------|----------|
| add | "Start developing?" → confirms into `/pace-dev` |
| modify | "N checks need re-verification, continue?" → resumes `/pace-dev` |
| pause | "Adjust iteration scope?" → confirms into `/pace-plan adjust` |
| resume | "Continue development?" → confirms into `/pace-dev` |
| reprioritize | "Switch to start working?" → confirms into `/pace-dev` |

It also checks for external issue associations and generates sync summaries when needed — keeping your GitHub Issues (or other tools) consistent without automatic side effects.

**Capacity coordination**: After `add` overflows iteration capacity, Claude directly asks whether to adjust scope (inline `/pace-plan adjust`). After `pause` frees capacity, it suggests pulling in waiting features.

## Change Types

| Type | Syntax | Description |
|------|--------|-------------|
| **add** | `/pace-change add <description>` | Insert a new requirement. Creates PF + CR entries, evaluates iteration capacity. |
| **pause** | `/pace-change pause <feature>` | Suspend a feature. All associated CRs move to `paused`, prior state is preserved, dependencies are unblocked. Feature tree shows a pause marker. |
| **resume** | `/pace-change resume <feature>` | Restore a paused feature. CRs return to their pre-pause state. Quality checks are re-validated against any code changes made during the pause window. |
| **reprioritize** | `/pace-change reprioritize <description>` | Adjust priority order. Updates next-step recommendations and reshuffles the iteration plan. |
| **modify** | `/pace-change modify <feature> <change>` | Change scope or acceptance criteria of an existing feature. Affected quality checks are precisely reset based on sensitivity scope matching. PF files are updated with history annotations. |
| **batch** | `/pace-change batch <description>` | Execute multiple changes in one pass. Merged impact analysis, cross-impact detection, single confirmation, single git commit. |
| **undo** | `/pace-change undo` | Revert the last `/pace-change` operation (current session only). Uses `git revert` for precise rollback. |
| **history** | `/pace-change history [feature\|--all\|--recent N]` | Query change history aggregated from iteration logs, CR events, PF annotations, and git log. |
| **apply** | `/pace-change apply <template>` | Apply a predefined change template from `.devpace/rules/change-templates.md`. |

### Quick References

- `#N` — Reference CR by number (e.g., `pause #3` = pause CR-003's feature)
- `--last` — Apply to the most recently worked-on CR (e.g., `modify --last`)
- `--dry-run` — Preview only, no execution

Omitting the type argument starts an **intelligent guided dialog** where Claude scans project context (paused CRs, Snooze triggers, iteration capacity, frequently-changed features) and makes personalized recommendations before falling back to the standard option list.

## Key Features

### Context-Aware Smart Guidance

When called without arguments, `/pace-change` scans the project state and recommends the most likely action — "Resume paused feature X?" or "Evaluate previously snoozed change Y?" — before showing the standard option list.

### Three-Tier Progressive Output

Impact reports follow a surface → middle → deep progression. Daily low-risk changes show just 1 line; complex changes expand on follow-up. Reading effort drops from 15-20 lines to 3-5 lines for typical changes.

### Precise Quality Check Reset

When modifying requirements, `/pace-change` compares the change scope against each quality check's `sensitivity` field (glob patterns in `checks.md`). Only checks with overlapping scope are reset — no more over-resetting or under-resetting.

### Batch Changes

Multiple changes in one pass: merged impact analysis, cross-impact detection (e.g., pausing A while B depends on A), single confirmation, single git commit. Supports both explicit `/pace-change batch` and natural language ("pause A and B").

### Change Undo

Precise rollback based on git commit history. Appends an "undo" entry to the iteration change log. Limited to current session to prevent cross-session state inconsistency.

### Change History Query

Aggregates change history from four scattered sources (iteration logs, CR events, PF annotations, git log) into a unified timeline. Proactively warns when a feature has been changed more than 3 times.

### Snooze with Active Reminders

Snoozed changes are persisted with trigger conditions. The pulse system automatically checks conditions at session start, new iteration creation, and CR merge — ensuring deferred changes are never forgotten. Each Snooze item is reminded exactly once.

### Experience-Driven Analysis

Historical patterns from `insights.md` inform impact analysis ("similar changes historically affected N modules") and elevate risk for patterns that previously required rollback.

### Transitive Dependency Tracing

Impact analysis traces up to 3 layers of transitive dependencies, with display depth scaled to risk level. Direct, indirect, and deep impacts are shown with indentation.

### Downstream Flow Automation

After execution, type-specific guidance helps users seamlessly transition to the next step — start developing, re-verify checks, or adjust iteration scope — with one-click confirmation into the relevant Skill.

### Structured Triage Routing

Every change request passes through Accept/Decline/Snooze before consuming analysis effort. This prevents low-value or premature requests from disrupting active work while ensuring nothing is silently dropped.

### BR-Level Impact View

When a change is large enough to affect an entire business requirement, the impact report automatically elevates from feature-level to BR-level, showing the full cascade: business goal impact, success metric risk, all affected features, and all affected CRs.

### Impact Visualization (Mermaid)

For medium/high risk changes (or on request), a Mermaid diagram visualizes the impact chain — from the change through affected features to individual CRs. Low-risk changes skip visualization to avoid noise.

### Change Cost Estimation

Risk quantification includes an estimated effort dimension — based on historical checkpoint counts from `insights.md` or heuristic rules when no history exists.

### External Sync Check

After any state-changing operation, `/pace-change` generates sync summaries for externally-linked CRs and prompts sync when needed — keeping your GitHub Issues (or other tools) consistent without automatic side effects.

### Change Management Metrics

Execution data feeds into `metrics.md` change management indicators (frequency, type distribution, rework rate, triage distribution, execution time), updated incrementally in `dashboard.md`.

## Degraded Mode

When `.devpace/` has not been initialized, `/pace-change` still works — it degrades gracefully instead of failing:

- **Triage** simplifies to a verbal confirmation: "Handle this now or note it for later?"
- **Impact analysis** scans the codebase directly using `Glob`/`Grep`/`Read`, analyzes `import`/`require` dependency graphs, and identifies affected modules and risk areas
- **Git history enhancement**: co-change analysis (frequently co-modified file groups) and hotspot identification (recent change hotspots)
- **Risk quantification** evaluates module spread from the dependency graph; CR and quality-check dimensions are marked "not available"
- **Execution** operates on code only — no `.devpace/` files are created or modified
- **Incremental enrichment**: Analysis results can optionally persist to `.devpace-cache/changes.md`. After 3+ degraded uses, the upgrade prompt becomes more specific
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
Claude: This change adds 1 new feature, risk is low.
        [Follow-up: "What specifically?"]
        Proposal: Create 2 CRs, defer "rate limiting" to next iteration.
        Iteration capacity exceeded — adjust scope now? (Y/N)

You:    Yes
Claude: Done. 2 CRs created, iteration plan updated, rate limiting deferred.
        Start developing? → /pace-dev
```

### Scenario 2: Batch Pause and Reprioritize

```
You:    /pace-change batch "pause notifications and move export ahead of search"
Claude: Detected 2 change intents:
        ① pause: Notification System
        ② reprioritize: Export ahead of Search
        Correct?

You:    Yes
Claude: Combined impact: 3 CRs paused (notifications), 1 CR reordered.
        No cross-impact detected. Risk: Low.
        Proceed?

You:    Go
Claude: Done. Notifications paused (3 CRs preserved), export prioritized.
        Start working on export? → /pace-dev
```

### Scenario 3: Modify with Precise Check Reset

```
You:    /pace-change modify search "response time must be under 200ms, not 500ms"
Claude: This change affects 1 feature, risk is medium.
        CR-005 (search implementation): Gate 1 passed, 1 of 3 checks needs reset.
        [Precise match: "performance test" check has sensitivity scope "src/search/",
         overlapping with change. "lint" and "type check" preserved.]
        Proceed?

You:    Yes
Claude: Done. 1 check reset on CR-005. History annotation added.
        1 check needs re-verification — continue development?
```

### Scenario 4: Undo Last Change

```
You:    /pace-change undo
Claude: Last change (2 minutes ago): paused "Notification System" (3 CRs).
        Revert this change?

You:    Yes
Claude: Reverted. Notification System restored, 3 CRs back to previous states.
```

## Integration with Other Commands

| Command | Relationship |
|---------|-------------|
| `/pace-dev` | After a change is executed, `/pace-dev` picks up new or modified CRs for implementation. Paused CRs are excluded from the dev queue. Downstream guidance offers one-click transition. |
| `/pace-plan` | `/pace-change add` creates PF and CR entries that become part of the plan. Capacity overflow triggers inline `adjust` coordination. Reprioritize adjustments are reflected in `/pace-plan`'s iteration view. |
| `/pace-sync` | After state-changing operations, `/pace-change` generates sync summaries and prompts a sync push. |
| `/pace-test` | Quality checks reset by `modify` (precision-matched via sensitivity scope) are re-evaluated during the next `/pace-test` gate review. Impact data from `/pace-test impact` is reused in `/pace-change` risk quantification. |
| `/pace-status` | Reflects all changes made by `/pace-change` — paused features, new CRs, updated priorities. |
| `/pace-pulse` | Snooze wake-up checks are performed by pulse at session start, new iteration, and CR merge. Change warning signals (acceptance drift, repeated failures, requirement conflicts) are pulse signals. |
| `/pace-retro` | Change management metrics (frequency, type distribution, rework rate) are aggregated in retrospective reports. |

## Related Resources

- [User Guide — /pace-change section](../user-guide.md) — Quick reference
- [Design Document — Change Management](../design/design.md) — Architecture and design principles
- [skills/pace-change/](../../skills/pace-change/) — Operational procedures (split by step: common, triage, impact, risk, execution, types; by subcommand: batch, undo, history, apply, degraded)
- [cr-format.md](../../knowledge/_schema/entity/cr-format.md) — CR file schema (includes `paused` state definition)
- [checks-format.md](../../knowledge/_schema/process/checks-format.md) — Quality check schema (includes sensitivity scope)
- [metrics.md](../../knowledge/metrics.md) — Change management metrics definitions
- [devpace-rules.md](../../rules/devpace-rules.md) — Runtime behavior rules
