# Project Status Queries (`/pace-status`)

`/pace-status` is a read-only command that surfaces project development progress at multiple levels of detail. It follows a strict **4-level information hierarchy** -- overview, detail, trace, tree -- where each level is a superset of the previous one. By default it returns a compact 3-line summary with a progress bar; deeper views are available on demand. All output uses natural language and avoids exposing internal IDs unless explicitly requested.

## Quick Start

```
1. /pace-status            --> 3-line overview with progress bar + next-step suggestion
2. /pace-status detail     --> Feature tree with per-feature completion status
3. /pace-status trace Auth --> Reverse traceability from a business requirement or objective
4. /pace-status tree       --> Full value chain from objectives down to change requests
```

The default overview is designed to answer "how is the project going?" in under three seconds of reading time. Use the subcommands when you need progressively deeper insight.

## Command Reference

### (default) -- Quick Overview

**Syntax**: `/pace-status`

Reads `.devpace/state.md` and renders an at-a-glance summary of the current iteration in three lines or fewer. A progress bar visualizes completion, and a next-step suggestion is appended automatically.

**Output example**:
```
Auth System ||||||||-- 80% (4/5 CR), next: access control
Blocked: user management waiting on auth module
Suggestion: continue "OAuth integration" --> /pace-dev
```

**Progress bar rules**: `|` = completed, `-` = remaining, 10 characters total. Parenthetical shows merged/total CR count. Only the current iteration's primary feature groups are shown. The suggestion line does not count toward the 3-line limit.

**Sync status line**: When `.devpace/integrations/sync-mapping.md` exists, a one-line sync summary is appended (e.g., `Sync: 3 CRs synced, 1 pending push`). Omitted silently when no sync configuration is present.

### `detail` -- Feature Tree

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
```

**Status indicators**: Done, Active, Pending, Paused. Blocked items and dependency relationships are called out explicitly.

### `trace <name>` -- Reverse Traceability

**Syntax**: `/pace-status trace <name-or-ID>`

Traces downward from a specified business requirement (BR), product feature (PF), or objective (OBJ) to aggregate the status of every downstream entity. This is the primary tool for answering "what is the delivery status of requirement X?"

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
```

When tracing from a PF, the output includes acceptance criteria pass rates and a list of associated CRs with their individual statuses.

### `metrics` -- Measurement Dashboard

**Syntax**: `/pace-status metrics`

Reads `.devpace/metrics/dashboard.md` and displays the measurement table. If `.devpace/metrics/insights.md` exists, the three most recent experience patterns are appended as a summary.

### `tree` -- Full Value Chain

**Syntax**: `/pace-status tree`

Renders the complete value chain from business objectives through requirements and features down to individual change requests. Every node carries a status indicator and progress count. This is the most verbose view and is intended for full-picture orientation.

### `chain` -- Current Work Position

**Syntax**: `/pace-status chain`

Locates the currently active CR and shows where it sits within the value chain, using a user-friendly tree that avoids internal terminology.

**Output example**:
```
Goal: Build user authentication system
  +-- Feature: Login module (Active)
        |-- Task: Form validation (Done)
        +-- Task: OAuth integration (Active) <-- you are here
```

When no CR is active, the most recently completed chain position is shown instead.

### `<keyword>` -- Search by Keyword

**Syntax**: `/pace-status <keyword>`

Searches `.devpace/backlog/` for CRs matching the keyword in their title. Displays the matched CR's quality-check checkbox state and event history.

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

## Output Examples

### 4-Level Hierarchy in Practice

**Level 1 -- Overview** (answers "how is the project overall?"):
```
Auth System ||||||||-- 80% (4/5 CR), next: access control
Suggestion: 1 change awaiting review --> /pace-review
```

**Level 2 -- Detail** (answers "how is each feature doing?"):
```
User System
  |-- Done     Login module (3/3 CR)
  |-- Active   Access control (1/2 CR)
  +-- Pending  User management (0/2 CR)
```

**Level 3 -- Trace** (answers "what is the full delivery status of a specific requirement?"):
```
Requirement: Secure Login (BR-001) --> User Authentication (OBJ-1)
|-- Login Module      --> 3/3 CR Done
|-- Access Control    --> 1/2 CR Active
+-- Session Mgmt      --> 0/1 CR Pending
MoS: 3/5 achieved
```

**Level 4 -- Tree** (answers "what does the entire value chain look like?"):
The full objective-to-CR tree with status on every node.

## Usage Scenarios

### Scenario 1: Morning Stand-Up Check

You open a new session and want a quick pulse on the project:

```
You:    /pace-status
Claude: Auth System ||||||||-- 80% (4/5 CR), next: access control
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
```

## Integration with Other Commands

`/pace-status` is a read-only query layer that complements the action-oriented commands:

| Command | Relationship |
|---------|-------------|
| `/pace-dev` | Status shows active CRs; the overview suggestion may direct you to resume development |
| `/pace-review` | Status flags CRs in `in_review` state; the suggestion links to `/pace-review` |
| `/pace-sync` | When sync configuration exists, the overview appends a sync consistency line |
| `/pace-next` | Status answers "where are we?"; `/pace-next` answers "what should we do?" They are complementary, not overlapping |
| `/pace-plan` | The `detail` and `tree` views help verify that planning decisions are reflected in current state |
| `/pace-retro` | The `metrics` subcommand surfaces data that feeds retrospective discussions |

## Related Resources

- [SKILL.md](../../skills/pace-status/SKILL.md) -- Skill definition and subcommand list
- [status-procedures.md](../../skills/pace-status/status-procedures.md) -- Detailed output formats and rules
- [User Guide](../user-guide.md) -- Quick reference for all commands
- [Design Document](../design/design.md) -- Architecture and workflow context
- [metrics.md](../../knowledge/metrics.md) -- Metric definitions used by the `metrics` subcommand
