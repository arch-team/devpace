# Feedback Collection & Incident Management (`/pace-feedback`)

In most AI-assisted workflows, production feedback arrives as fragmented signals — a Slack message here, a vague bug report there, and no clear way to trace feedback back to business goals or forward into actionable improvements. devpace treats feedback as **structured value chain events**. `/pace-feedback` provides intelligent classification, multi-layer traceability, incident severity assessment, and seamless routing back into development, closing the loops from "delivery → feedback → improvement" and "deployment → incident → fix."

Every piece of feedback receives a unique **FB-ID** for full lifecycle tracking — from initial report through resolution and retrospective analysis.

## Quick Start

```
1. /pace-feedback report "API 500 errors in /checkout"  → Emergency channel → Create hotfix CR
2. /pace-feedback "search is too slow"                  → Classify → Improvement pool
3. /pace-feedback                                       → Guided collection → Two-round dialog
```

Or use the emergency hotline:

```
You:    /pace-feedback report "payment gateway timeout"
Claude: [Production incident detected — accelerated triage]
        Severity: critical | Affects: Payment Feature (PF-003)
        Hotfix CR-042 created. Start emergency fix? → /pace-dev
```

## Workflow

### Step 0: Draft Recovery Check

Before starting new feedback collection, `/pace-feedback` checks for an unfinished draft from a previous interrupted session:

- **Draft exists** → "Resume interrupted feedback? (Y/N)"
  - Yes → Restore context and continue from the last step
  - No → Delete draft, start fresh
- **No draft** → Proceed to Step 1

This prevents duplicate work and preserves partial progress across sessions.

### Step 1: Classification

Not all feedback is created equal. `/pace-feedback` routes each input through intelligent classification into 5 types (production incident, defect, improvement, new requirement, inbox) before triggering type-specific downstream actions. See [Classification Types](#classification-types) below for detailed descriptions and examples.

**Emergency channel**: Using `report <description>` bypasses normal triage and fast-tracks to production incident handling with automatic hotfix eligibility assessment.

### Step 2: Severity Assessment + Value Chain Tracing

For production incidents and defects, `/pace-feedback` performs:

1. **Severity scoring** (critical / major / minor / trivial) based on:
   - User impact scope (all users / subset / single user)
   - Data integrity risk
   - Business operation blockage
   - Workaround availability

2. **Three-layer value chain tracing**:
   - **BR layer** — Which business goals are affected? Are success metrics (MoS) at risk?
   - **PF layer** — Which product features are impacted?
   - **CR layer** — Which CRs introduced or can fix the issue?

3. **Historical feedback matching**: Searches `.devpace/backlog/feedback/` for similar past incidents:
   - Same feature + similar description → "Similar incident FB-012 (3 weeks ago) root cause: X"
   - Recurring pattern → "This feature has 3 previous incidents — consider root cause analysis"
   - Historical fix data informs resolution effort estimates

**Three-tier progressive output** (aligned with design.md §2):
- **Surface** (trivial/minor): 1-line summary — "Defect affecting search, minor severity, CR created."
- **Middle** (major): 5-8 lines with feature impact, suggested fix scope, historical context
- **Deep** (critical): Full trace report with BR impact, affected MoS, historical pattern analysis, recommended hotfix path, optional Mermaid visualization

### Step 3: MoS Update

When feedback affects business-critical metrics tracked in `project.md`:

- **Degradation detected** → Update MoS current value, add annotation: "Degraded due to FB-015"
- **Risk flagged** → Mark MoS as "at risk" with feedback reference
- **Improvement potential** → Note optimization opportunity in MoS comments

This closes the loop: business goals → features → code → deployment → **feedback → business metrics**.

### Step 4: Execute Action

Based on classification, `/pace-feedback` performs type-specific routing:

| Type | Execution |
|------|-----------|
| Production incident | Create defect or hotfix CR → Update feature status → Record in incident log |
| Defect | Create fix CR → Link to source PF → Schedule into backlog |
| Improvement | Append to improvement suggestion pool in `project.md` → Tag with originating feature |
| New requirement | Generate `/pace-change add` template → Guide user through insertion workflow |
| Inbox | Save to `.devpace/backlog/feedback-inbox.md` with triage reminder |

**Hotfix acceleration**: For critical incidents, `/pace-feedback` can directly invoke `/pace-dev` with a fast-track flag that relaxes gate requirements (with explicit user consent).

### Step 5: Status & Metrics Update

After executing actions, update feedback status and metrics per the authoritative status flow defined in `feedback-procedures-status.md` (7 transitions with classification-specific paths: Created → Processing → Fixed, Created → Pending → Adopted, etc.).

Metrics updated include feature tree markers, feedback log entries, and defect escape rate in `dashboard.md`.

### Step 6: Draft Cleanup

After successful completion, delete `.devpace/backlog/FEEDBACK-DRAFT.md` to prepare for the next feedback session.

## Classification Types

> Complete type + characteristic definition is the authoritative source in `SKILL.md`. The table below extends it with examples and typical sources for documentation purposes.

| Type | Typical Source | Example |
|------|---------------|---------|
| **Production Incident** | Monitoring alerts, user reports of outages | "Payment gateway timeout", "API 500 errors", "Database connection failure" |
| **Defect** | QA testing, user bug reports | "Export CSV generates incorrect totals", "Profile image upload fails for PNG" |
| **Improvement** | User surveys, UX feedback, support tickets | "Search takes 5 seconds", "Login form has too many fields", "Button placement confusing" |
| **New Requirement** | Feature requests, stakeholder input | "Need bulk import", "Support SSO", "Add export to PDF" |
| **Inbox** | Ambiguous signals, deferred items | "Something feels off", "Users complaining (details unclear)", "Monitor this behavior" |

## Key Features

### Unique Feedback ID (FB-ID) Tracking

Every piece of feedback receives a unique FB-ID that persists through the entire lifecycle. All related artifacts (CRs, commits, test cases) reference the FB-ID, enabling full traceability. See `feedback-procedures-common.md` for ID allocation rules.

### Progressive Two-Round Collection

When called without arguments, `/pace-feedback` uses a **guided two-round dialog** (aligned with design.md §2 progressive disclosure):

- **Round 1**: Minimal questions — "What happened?" + "How urgent?" (2 questions, <30 sec)
- **Round 2**: Context-specific deep dive based on Round 1 classification (5-8 questions, only if needed)

This respects user time: simple reports stay simple; complex incidents get the detail they need.

### Interruption Recovery

Feedback collection persists partial progress to a draft file. Next session automatically detects and offers to resume from the last step. See `feedback-procedures-common.md` for full draft mechanism and recovery flow.

### Three-Tier Traceability Output

Feedback impact reports follow a **surface → middle → deep** progression based on severity:

- **trivial/minor severity**: 1-line summary (reading time: 5 sec)
- **major severity**: 5-8 lines with feature impact and historical context (reading time: 15 sec)
- **critical severity**: Full trace with BR impact, MoS risk, recurring pattern analysis, visualization (reading time: 45 sec)

This matches cognitive load to actual decision-making needs.

### Feedback Inbox ("Record Pending")

Not all feedback can be immediately classified or acted upon. The **Inbox** category provides a holding area for:

- Ambiguous descriptions requiring follow-up
- Uncertain classification needing more context
- Explicitly deferred items ("monitor this for a week")

Inbox items are reviewed during `/pace-retro` and pulse checks to prevent forgotten feedback.

### Improvement Suggestion Pool

Improvement-classified feedback flows into a **structured suggestion pool** in `project.md`:

```
## Improvement Suggestions
- [FB-023] Search performance (from User Survey): Currently 5s, target 2s
- [FB-031] Login UX (from Support Tickets): Reduce form fields from 8 to 4
```

These suggestions are:
- **Tagged by source** (user reports, analytics, internal observation)
- **Linked to originating features** (enables feature quality scoring)
- **Prioritized during planning** (`/pace-plan` references this pool)
- **Tracked for adoption** (metrics show improvement implementation rate)

### Historical Feedback Matching

When processing new feedback, `/pace-feedback` searches `.devpace/backlog/feedback/` for similar past incidents:

- **Same feature + keyword overlap** → "Similar incident FB-012 (3 weeks ago, root cause: X)"
- **Recurring pattern** → "This is the 3rd incident for Feature Y in 2 months — consider root cause analysis"
- **Resolution time data** → "Similar issues historically resolved in 2-4 hours"

This institutional memory prevents repeated diagnosis work and highlights systemic issues.

### Intelligent Root Cause Assistance

For production incidents, `/pace-feedback` provides root cause investigation support:

1. **Historical pattern analysis**: "Previous incidents in this feature traced to API timeout (2 cases) and cache invalidation (1 case)"
2. **Git blame integration**: Identify recent changes to affected modules
3. **Dependency impact scan**: Check if related features reported similar issues
4. **Suggested investigation paths**: "Check: API gateway logs, database connection pool, recent config changes"

This accelerates diagnosis, especially for teams with high context switching.

### Git Fallback Tracing

When `.devpace/` history is unavailable (new project, partial adoption), `/pace-feedback` falls back to **git-native tracing**:

- **Co-change analysis**: Files frequently modified together suggest coupling
- **Hotspot identification**: Recent high-activity areas
- **Commit message mining**: Search for keywords ("fix", "bug", "hotfix") in history
- **Author expertise inference**: Suggest contacting recent committers

This enables partial functionality even in degraded mode.

### Hotfix Emergency Channel

Using `report <description>` triggers a **fast-track path** for production incidents:

1. **Skip normal triage**: Automatically classified as "Production Incident"
2. **Accelerated eligibility check**: Evaluate if hotfix procedure applies (severity + impact threshold)
3. **Direct CR creation**: Create hotfix CR with special state (`hotfix`) that bypasses some quality gates
4. **One-click dev handoff**: "Critical incident detected. Start emergency fix? → /pace-dev (hotfix mode)"

This reduces time-to-action from 3-5 minutes to under 60 seconds for genuine emergencies.

### Degraded Mode

When `.devpace/` exists but `releases/` does not, `/pace-feedback` runs in degraded mode. Core capabilities (classification, severity assessment, CR creation, improvement pool, inbox, FB-ID tracking) remain fully functional; only release tracing and deployment time correlation are skipped.

For authoritative degraded mode behavior, see `feedback-procedures-common.md`.

## Usage Scenarios

### Scenario 1: Report a Production Incident

A payment gateway timeout is causing checkout failures in production.

```
You:    /pace-feedback report "payment gateway timeout at /checkout endpoint"
Claude: [Production incident detected — emergency channel activated]

        Severity assessment:
        - User impact: All checkout attempts (critical)
        - Workaround: None available
        - Overall: critical

        Value chain trace:
        - BR-002 (E-commerce Core): At risk
        - MoS "Checkout success rate": Degraded from 98% to 0%
        - PF-008 (Payment Processing): Affected

        Historical match: FB-009 (45 days ago) — same feature, timeout issue
        Previous root cause: API gateway connection pool exhaustion

        Hotfix eligibility: Qualified (critical severity + user-facing + no workaround)

        Actions:
        ✓ Created CR-067 (hotfix, priority: urgent)
        ✓ Updated MoS-002 status → Degraded
        ✓ Recorded incident FB-024 in log
        ✓ Assigned FB-024 → CR-067

        Start emergency fix? → /pace-dev (hotfix mode) [Y/N]

You:    Yes
Claude: [Entering hotfix development mode…]
```

### Scenario 2: Submit an Improvement Suggestion

A user survey reveals that search performance is suboptimal.

```
You:    /pace-feedback "users complain search is slow, taking 5+ seconds"
Claude: Classification: Improvement (functional but suboptimal performance)

        Related feature: PF-004 (Search & Discovery)
        Severity: minor (non-blocking but impacts UX)

        Historical context: PF-004 has 1 previous improvement (FB-018, response time)

        Actions:
        ✓ Added to improvement suggestion pool:
          [FB-025] Search performance: Currently 5s, UX target 2s
          Tagged: User Survey, PF-004
        ✓ Feature quality score updated: PF-004 (88% → 85%)

        Next steps:
        - Consider during next planning cycle (/pace-plan)
        - Review improvement pool priorities in retrospective

        Priority this improvement now? → /pace-change add [Y/N]

You:    No — note it for next sprint.
Claude: Acknowledged. FB-025 recorded in improvement pool for future planning.
```

### Scenario 3: Resume Interrupted Feedback

You started reporting an issue but got interrupted by an urgent meeting.

```
You:    /pace-feedback
Claude: Detected unfinished feedback draft from 2 hours ago:
        - Type: Production incident
        - Description: "database connection pool exhausted"
        - Progress: Classification complete, severity assessment pending

        Resume this feedback? [Y/N]

You:    Yes
Claude: [Restoring context…]

        Continuing severity assessment:
        Questions (Round 2):
        1. How many users are affected? (all / some / one)
        2. Is there a workaround?
        3. Is data integrity at risk?

You:    All users, no workaround, no data risk
Claude: Severity: critical (user-facing, no workaround)

        [Continuing with value chain tracing…]
        [Actions: Create CR-068, update MoS-003…]

        Feedback FB-026 processed. Draft cleaned up.
```

### Scenario 4: Classify Ambiguous Feedback

Not all feedback is immediately clear.

```
You:    /pace-feedback "something feels off with the export feature"
Claude: Classification uncertain — additional context needed.

        Follow-up questions:
        1. Does export complete or fail?
        2. Is the data incorrect or incomplete?
        3. Is this urgent or can it wait?

You:    It completes, but I'm not sure if all data is there. Can wait.
Claude: Classification: Inbox (ambiguous, non-urgent)

        Actions:
        ✓ Recorded FB-027 in feedback inbox
        ✓ Triage reminder set for next retrospective

        To investigate further, provide:
        - Expected vs actual export row count
        - Example CSV file
        - Steps to reproduce

        Update this feedback when more info available: /pace-feedback #27
```

## Integration with Other Commands

| Command | Relationship |
|---------|-------------|
| `/pace-dev` | Feedback-created CRs (defect/hotfix) are picked up by `/pace-dev` for implementation. Emergency channel offers one-click transition with hotfix mode enabled. |
| `/pace-change` | New requirement feedback is guided into `/pace-change add` workflow with pre-filled description. Recurring improvement suggestions may trigger "add as feature?" prompts. |
| `/pace-plan` | Improvement suggestion pool is referenced during iteration planning. Feedback frequency per feature informs prioritization. |
| `/pace-test` | Feedback that originates from test failures is enriched with test context. Resolved feedback CRs require verification via `/pace-test accept`. |
| `/pace-status` | Reflects all feedback-created CRs and their current state. Open feedback items count displayed in status overview. |
| `/pace-pulse` | Pulse checks highlight: unresolved high-severity feedback, stale inbox items (>7 days), recurring feedback patterns (same feature 3+ times). |
| `/pace-retro` | Feedback metrics (frequency by type, resolution time, recurring incidents, improvement adoption rate) are aggregated in retrospective reports. Inbox items are reviewed for triage decisions. |
| `/pace-learn` | Feedback patterns become training data: "Feature X has recurring performance feedback — consider proactive optimization." Root cause patterns feed into decision support. |

## Related Resources

- [User Guide — /pace-feedback section](../user-guide.md) — Quick reference and command syntax
- [Design Document — Feedback Loop Integration](../design/design.md) — Architecture and closed-loop design principles
- [skills/pace-feedback/](../../skills/pace-feedback/) — Operational procedures (5 split files: common, intake, trace, hotfix, analysis)
- [fb-format.md](../../knowledge/_schema/fb-format.md) — Feedback record schema with FB-ID structure
- [feedback-status.md](../../knowledge/_schema/feedback-status.md) — Feedback lifecycle state definitions
- [metrics.md](../../knowledge/metrics.md) — Feedback management metrics definitions (resolution time, recurring rate, improvement adoption)
- [devpace-rules.md](../../rules/devpace-rules.md) — Runtime behavior rules for feedback processing
