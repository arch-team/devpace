# Project Status Queries (`/pace-status`)

`/pace-status` is a read-only command that surfaces project development progress at multiple levels of detail. It follows a **3-level information hierarchy** with orthogonal dimensions:

- **L1 Overview**: answers "how is the project overall?" (compact 3-line summary)
- **L2 Detail / L2 Trace**: two orthogonal views at the same level -- detail expands breadth (every feature in the current iteration), trace drills depth (full delivery status of a specific requirement, potentially spanning iterations)
- **L3 Tree**: answers "what does the entire value chain look like?" (full objective-to-CR tree)

All output uses natural language and avoids exposing internal IDs unless explicitly requested. Role-based views and a `since` time modifier add further filtering dimensions.

## Quick Start

```
1. /pace-status            --> 3-line overview with progress bar + next-step suggestion
2. /pace-status detail     --> Feature tree with per-feature completion status
3. /pace-status trace Auth --> Reverse traceability from a business requirement or objective
4. /pace-status tree       --> Full value chain from objectives down to change requests
5. /pace-status metrics    --> Core metrics snapshot with trend arrows
6. /pace-status since 3d   --> Changes in the last 3 days
```

The default overview is designed to answer "how is the project going?" in under three seconds of reading time. Use the subcommands when you need progressively deeper insight.

## Command Reference

### (default) -- Quick Overview

**Syntax**: `/pace-status`

Reads `.devpace/state.md` and renders an at-a-glance summary of the current iteration in three lines or fewer. A progress bar visualizes completion, and a next-step suggestion (lightweight subset of `/pace-next` -- top-1 signal only, no reasoning) is appended automatically.

**Output example**:
```
Auth System ████████░░ 80% (4/5 CR), next: access control
Blocked: user management waiting on auth module
Suggestion: continue "OAuth integration" --> /pace-dev
```

**Progress bar rules**: `█` = completed, `░` = remaining, 10 characters total. **Fallback**: when the terminal does not support Unicode block characters, use `[====----] 50%` or a plain percentage. Parenthetical shows merged/total CR count. Only the current iteration's primary feature groups are shown. The suggestion line does not count toward the 3-line limit but is subject to the **appendix cap of 2 lines** (suggestion + sync combined), keeping total output at 5 lines or fewer.

**Push/pull dedup**: When invoked within 5 minutes of session start, the suggestion line is omitted (session-start rhythm check already provided it).

**Sync status line**: When `.devpace/integrations/sync-mapping.md` exists, a one-line sync summary is appended (e.g., `Sync: 3 CRs synced, 1 pending push`). Omitted silently when no sync configuration is present.

### `detail` -- Feature Tree (Breadth View)

**Syntax**: `/pace-status detail`

Reads the current iteration and project files, then renders an indented tree of all product features grouped by functional area. Each node shows its CR completion ratio and current status.

**Output example**:
```
User System
  |-- Done     Login module (3/3 CR) --> [details](features/PF-001.md)
  |-- Active   Access control (1/2 CR) <-- in progress
  +-- Pending  User management (0/2 CR)
Data Management
  |-- Done     Data import (2/2 CR)
  +-- Active   Data export (1/3 CR)

--> Drill into a feature: /pace-status trace [feature name]
```

**Status indicators**: Done, Active, Pending, Paused. Blocked items and dependency relationships are called out explicitly. When sync configuration exists, synced CRs are marked with a link icon and pending-push CRs are annotated.

**Role adaptation**: When a role is set via `/pace-role`, the detail view emphasizes role-relevant information (Dev: quality gate status; PM: completion rates and dependencies; Biz: MoS linkage).

### `trace <name>` -- Reverse Traceability (Depth View)

**Syntax**: `/pace-status trace <name-or-ID>`

Traces downward from a specified business requirement (BR), product feature (PF), or objective (OBJ) to aggregate the status of every downstream entity. This is the primary tool for answering "what is the delivery status of requirement X?" -- potentially spanning multiple iterations.

**Relationship to detail**: Detail and trace are **orthogonal L2 views**, not a containment hierarchy. Trace may show content absent from detail (cross-iteration historical CRs) and may omit content present in detail (unrelated features).

**Matching rules**:

| Input | Match behavior |
|-------|----------------|
| OBJ ID (e.g., `OBJ-1`) | Exact match against the value tree |
| BR ID (e.g., `BR-001`) | Exact match against the value tree |
| PF ID (e.g., `PF-001`) | Exact match against the value tree |
| Name keyword (e.g., `Auth`) | Fuzzy match; if ambiguous, lists candidates for selection |

**Output example (tracing from an objective)**:
```
Objective: User Authentication System (OBJ-1)
|-- Requirement: Secure Login (BR-001)
|   |-- Login Module (PF-001)    --> 3/3 CR Done
|   |-- Access Control (PF-002)  --> 1/2 CR Active
|   +-- Session Mgmt (PF-003)   --> 0/1 CR Pending
+-- Requirement: OAuth Support (BR-002)
    +-- OAuth Module (PF-004)    --> 2/2 CR Done
MoS: 3/5 achieved (login latency < 200ms Done | MFA coverage Pending)

--> Full value chain: /pace-status tree
```

When tracing from a PF, the output includes acceptance criteria pass rates and a list of associated CRs with their individual statuses.

### `metrics [category]` -- Measurement Dashboard

**Syntax**: `/pace-status metrics [quality|delivery|risk]`

Reads `.devpace/metrics/dashboard.md` and displays a core metrics snapshot with trend arrows (up/down/steady compared to the previous record). If `.devpace/metrics/insights.md` exists, the three most recent experience patterns are appended.

**Default output** (no category): first-pass rate, MoS achievement rate, average CR cycle time, iteration velocity -- each with a trend arrow.

**Category focus**: `quality` (pass rates, rejection rate, defect escape rate), `delivery` (CR cycle, velocity, completion rate, scope changes), `risk` (open risks, MTTR, severity distribution).

**Distinction from /pace-retro**: `metrics` is a real-time snapshot (current values + trends); `/pace-retro` produces a time-period retrospective report.

### `tree` -- Full Value Chain

**Syntax**: `/pace-status tree`

Renders the complete value chain from business objectives through requirements and features down to individual change requests. Every node carries a status indicator and progress count. This is the most verbose view and is intended for full-picture orientation.

### `chain` -- Current Work Position

**Syntax**: `/pace-status chain`

A specialized version of `trace` focused on the currently active CR's parent feature. Locates the active CR and shows where it sits within the value chain, using a user-friendly tree that avoids internal terminology.

**Output example**:
```
Goal: Build user authentication system
  +-- Feature: Login module (Active)
        |-- Task: Form validation (Done)
        +-- Task: OAuth integration (Active) <-- you are here

--> Trace another feature: /pace-status trace [name]
```

When no CR is active, the most recently completed chain position is shown instead.

### `<keyword>` -- Search by Keyword

**Syntax**: `/pace-status <keyword>`

Searches `.devpace/backlog/` for CRs matching the keyword in their title. Displays the matched CR's quality-check checkbox state and event history.

**Fallback when no match**: Automatically searches the feature tree in `project.md`. If a PF/BR/OBJ name matches, suggests using `trace` instead. If nothing matches at all, offers `detail` and `trace` as alternatives.

### `since <time>` -- Temporal View

**Syntax**: `/pace-status since <time-marker>` or combined with other subcommands

Shows changes within a specified time window. Time markers: `Nd` (last N days), `Nw` (last N weeks), `last-session` (since last session ended). Can combine with other subcommands (e.g., `/pace-status detail since 3d` highlights recently changed features).

### Role-Based Views

Five role-specific lenses are available, each pulling from different data sources and emphasizing different concerns:

| Subcommand | Perspective | Key metrics |
|------------|------------|-------------|
| `biz` | Business Owner | MoS achievement rate, value delivery count, risk items |
| `pm` | Product Manager | Iteration progress bar, scope changes, average CR cycle time |
| `dev` | Developer | Active CRs and their stages, quality gate pass counts |
| `tester` | Tester | Defect distribution (open/fixed/escaped), check pass rate, rejection rate |
| `ops` | Operations | Latest release status, post-deploy defects, MTTR, unreleased merged CRs |

Each view reads only the data sources relevant to that role and omits information outside the role's concern.

**Priority rule**: Explicit role subcommand > `/pace-role` automatic adaptation. If a user sets `/pace-role pm` then runs `/pace-status dev`, the Dev view takes precedence.

**Automatic adaptation**: When a role is set via `/pace-role` (without explicit role subcommand), the overview and detail/trace/tree views automatically adjust their emphasis to match the role's focus areas.

## Output Examples

### 3-Level Hierarchy in Practice

**L1 -- Overview** (answers "how is the project overall?"):
```
Auth System ████████░░ 80% (4/5 CR), next: access control
Suggestion: 1 change awaiting review --> /pace-review
```

**L2 -- Detail** (breadth: "how is each feature doing?"):
```
User System
  |-- Done     Login module (3/3 CR)
  |-- Active   Access control (1/2 CR)
  +-- Pending  User management (0/2 CR)
```

**L2 -- Trace** (depth: "what is the full delivery status of a specific requirement?"):
```
Requirement: Secure Login (BR-001) --> User Authentication (OBJ-1)
|-- Login Module      --> 3/3 CR Done
|-- Access Control    --> 1/2 CR Active
+-- Session Mgmt      --> 0/1 CR Pending
MoS: 3/5 achieved
```

**L3 -- Tree** (answers "what does the entire value chain look like?"):
The full objective-to-CR tree with status on every node.

## Usage Scenarios

### Scenario 1: Morning Stand-Up Check

You open a new session and want a quick pulse on the project:

```
You:    /pace-status
Claude: Auth System ████████░░ 80% (4/5 CR), next: access control
        Blocked: user management waiting on auth module
        Suggestion: continue "OAuth integration" --> /pace-dev
```

### Scenario 2: Stakeholder Asks About a Feature

A business stakeholder wants to know whether the authentication objective is on track:

```
You:    /pace-status trace Auth
Claude: Objective: User Authentication System (OBJ-1)
        |-- Requirement: Secure Login (BR-001)
        |   |-- Login Module       --> 3/3 CR Done
        |   +-- Access Control     --> 1/2 CR Active
        +-- Requirement: OAuth Support (BR-002)
            +-- OAuth Module       --> 2/2 CR Done
        MoS: 3/5 achieved (login latency Done | MFA coverage Pending)
        --> Full value chain: /pace-status tree
```

### Scenario 3: Role-Specific Briefing Before Release

Before cutting a release, the ops engineer checks deployment readiness:

```
You:    /pace-status ops
Claude: ## Operations Status
        Latest Release: REL-002 (deployed, 2026-02-24)
        Post-deploy defects: 1 (fixed)
        MTTR: 0.5 days
        Unreleased: 2 merged CRs awaiting release
        --> Switch perspective: /pace-role [biz|pm|dev|tester|ops]
```

### Scenario 4: What Changed This Week?

```
You:    /pace-status since 1w
Claude: Changes in the last 7 days:
        Completed: "OAuth integration" (merged)
        In progress: "Session management" (created --> developing)
        New: "MFA support" (created)
        --> See current full picture: /pace-status detail
```

### Scenario 5: Metrics Quick Check

```
You:    /pace-status metrics
Claude: Core Metrics
        First-pass rate: 78% -->    Avg CR cycle: 3.2 days (down)
        MoS achievement: 60% (up)  Iteration velocity: 5 CR/iter -->
        --> Full retrospective: /pace-retro
```

## Integration with Other Commands

`/pace-status` is a read-only query layer that complements the action-oriented commands:

| Command | Relationship |
|---------|-------------|
| `/pace-dev` | Status shows active CRs; the overview suggestion may direct you to resume development |
| `/pace-review` | Status flags CRs in `in_review` state; the suggestion links to `/pace-review` |
| `/pace-sync` | When sync configuration exists, the overview appends a sync consistency line |
| `/pace-next` | Status answers "where are we?" with a lightweight top-1 suggestion; `/pace-next` provides full prioritized recommendation with reasoning. They are complementary layers |
| `/pace-plan` | The `detail` and `tree` views help verify that planning decisions are reflected in current state |
| `/pace-retro` | The `metrics` subcommand is a real-time snapshot; `/pace-retro` produces period retrospectives |
| `/pace-role` | Role set via `/pace-role` automatically adapts status output emphasis; explicit role subcommands override |
| `/pace-pulse` | Session-start check is "push"; `/pace-status` is "pull". Dedup: suggestion line suppressed within 5 minutes of session start |

## Related Resources

- [SKILL.md](../../skills/pace-status/SKILL.md) -- Skill definition and subcommand list
- [status-procedures-*.md](../../skills/pace-status/) -- Detailed output formats (split by subcommand for on-demand loading)
- [User Guide](../user-guide.md) -- Quick reference for all commands
- [Design Document](../design/design.md) -- Architecture and workflow context
- [metrics.md](../../knowledge/metrics.md) -- Metric definitions used by the `metrics` subcommand
