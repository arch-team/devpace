# External Tool Sync (`/pace-sync`)

devpace is a closed system — CR states live exclusively inside `.devpace/`. `/pace-sync` bridges devpace with GitHub Issues through **semantic-level synchronization**: rather than mechanically mapping field A to field B, Claude understands "this change request is being implemented" and generates the corresponding external operation. v1.5.0 ships as a **push-only MVP**; bidirectional sync is planned for Phase 20.

## Prerequisites

| Requirement | Purpose | Required? |
|-------------|---------|:---------:|
| `gh` CLI | GitHub API operations (labels, comments, issue state) | Recommended |
| `git remote` configured | Auto-detect repository owner/name during setup | Yes |
| `.devpace/` initialized | Core devpace project structure | Yes |

> **Graceful degradation**: If `gh` CLI is not installed, `setup` still generates the configuration file (marked as "unverified"). `push` and `status` require `gh` to function.

## Quick Start

```
1. /pace-sync setup      → Detects git remote → generates sync-mapping.md
2. /pace-sync link CR-003 #42   → Associates CR-003 with GitHub Issue #42
3. /pace-sync push        → Pushes state → Issue #42 labels updated
```

After setup, the sync-push advisory hook automatically reminds you to push after CR state changes.

## Command Reference

### `setup`

Guided configuration wizard.

**Syntax**: `/pace-sync setup`

**Behavior**:
1. Check `gh` CLI availability (`gh --version`)
2. Read git remote: `git remote get-url origin` → extract `owner/repo`
3. Confirm with user: repository, sync mode (push recommended for MVP), conflict strategy
4. Verify connection: `gh repo view {owner}/{repo} --json name`
5. Generate `.devpace/integrations/sync-mapping.md` (per [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) schema)
6. Output configuration summary

**Output example**:
```
Sync configured:
- Platform: GitHub (myorg/myrepo)
- Sync mode: push
- Connection: ✅ verified
Next: use /pace-sync link CR-xxx #IssueNumber to associate change requests
```

**Degradation**: When `gh` is unavailable, the config file is still created with "connection unverified" status.

### `link`

Associate a CR with an external entity.

**Syntax**: `/pace-sync link <CR-ID> <#ExternalID>`

**Arguments**:
| Argument | Format | Example |
|----------|--------|---------|
| CR-ID | `CR-xxx` or `xxx` | `CR-003`, `003` |
| External ID | `#number` or `number` | `#42`, `42` |

**Behavior**:
1. Verify CR exists in `.devpace/backlog/CR-{id}.md`
2. Verify external entity exists: `gh issue view {number} --json number,title,state`
3. Write external link field into CR file
4. Append association record to sync-mapping.md
5. Confirm: `CR-{id} ↔ Issue #{number} linked`

**Error handling**:
- CR not found → prompt user
- External entity not found → prompt user to verify ID
- CR already linked → confirm before overwriting

### `push`

Push devpace state to external tools.

**Syntax**: `/pace-sync push [CR-ID]`

**Arguments**:
| Argument | Behavior |
|----------|----------|
| `CR-ID` | Push state for specified CR only |
| *(empty)* | Push all linked CRs |

**Behavior** (per linked CR):
1. Read CR current state
2. Look up state mapping → determine target label
3. Query external current state: `gh issue view {number} --json state,labels`
4. Compare: consistent → skip; inconsistent → update
5. Update external state:
   - Remove old state label, add new label
   - Add comment documenting state change
6. Update sync-mapping.md last-sync timestamp

**Output example**:
```
| CR     | State      | External action            | Result |
|--------|------------|----------------------------|--------|
| CR-003 | developing | Add label: in-progress     | ✅     |
| CR-005 | merged     | Close Issue #18 + add done | ✅     |
```

### `status`

View sync status for all linked CRs.

**Syntax**: `/pace-sync status`

**Behavior**:
1. Read sync-mapping.md association records
2. For each record: read CR state, query external state (optional — shows "unknown" if `gh` unavailable), compare consistency
3. Output sync status table

**Output example**:
```
| CR     | External | devpace    | External      | Consistent | Last sync    |
|--------|----------|------------|---------------|------------|--------------|
| CR-003 | #42      | developing | in-progress   | ✅          | 02-25 10:30  |
| CR-005 | #18      | merged     | open          | ❌ push     | 02-24 15:00  |
```

**No associations**:
```
No linked external entities.
Use /pace-sync link CR-xxx #IssueNumber to create an association.
```

## State Mapping

devpace CR states map to GitHub Issue labels:

| devpace state | GitHub label | Direction | Notes |
|---------------|-------------|:---------:|-------|
| `created` | `backlog` | ↔ | New CR corresponds to backlog label |
| `developing` | `in-progress` | ↔ | Active development |
| `verifying` | `needs-review` | → | Push-only in MVP |
| `in_review` | `awaiting-approval` | → | Push-only in MVP |
| `approved` | `approved` | → | Push-only in MVP |
| `merged` | close Issue + `done` | ↔ | Closes the issue |
| `released` | `released` | → | Push-only |
| `paused` | `on-hold` | ↔ | Paused work |

**Direction and sync mode interaction**: The effective sync direction is the intersection of the platform sync mode (configured in setup) and the per-state direction. When sync mode is `push`, even ↔ states only execute the → direction.

## Usage Scenarios

### Scenario 1: First-time Configuration

You have an existing devpace project and want to start syncing with GitHub Issues.

```
You:    /pace-sync setup
Claude: Detected repository: myorg/my-project
        Sync mode: push (recommended for MVP)
        Conflict strategy: ask-user
        Verify connection? [Y/n]

You:    Y
Claude: ✅ Connection verified
        Config written to .devpace/integrations/sync-mapping.md

        Next: /pace-sync link CR-xxx #IssueNumber
```

### Scenario 2: Daily Development Push

After a `/pace-dev` session transitions CR-003 from `created` to `developing`, the sync-push hook reminds you:

```
Hook:   devpace:sync-push CR state=developing, linked to github#42.
        Consider running /pace-sync push to sync status.

You:    /pace-sync push CR-003
Claude: | CR     | State      | Action               | Result |
        |--------|------------|----------------------|--------|
        | CR-003 | developing | Add label in-progress| ✅     |
```

### Scenario 3: Consistency Check

Before a release, verify all CRs are in sync:

```
You:    /pace-sync status
Claude: | CR     | External | devpace    | External      | Match | Last sync   |
        |--------|----------|------------|---------------|-------|-------------|
        | CR-003 | #42      | merged     | done (closed) | ✅    | 02-25 14:00 |
        | CR-005 | #18      | developing | backlog       | ❌    | 02-24 15:00 |

        1 CR out of sync. Run /pace-sync push to update.
```

## Configuration Reference

The sync configuration lives in `.devpace/integrations/sync-mapping.md`, following the [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) schema.

### Platform

```markdown
## Platform

- **Type**: github
- **Connection**: myorg/myrepo
- **Sync mode**: push
- **Conflict strategy**: ask-user
```

| Field | Values | Description |
|-------|--------|-------------|
| Type | `github` / `linear` / `jira` / `gitlab` | External platform identifier |
| Connection | Platform-specific identifier (e.g., `owner/repo` for GitHub) | Target endpoint |
| Sync mode | `readonly` / `push` / `pull` / `bidirectional` | Data flow direction |
| Conflict strategy | `devpace-authoritative` / `external-authoritative` / `ask-user` | Bidirectional conflict resolution |

### State Mapping Table

Customizable per-project. The default mapping (shown in [State Mapping](#state-mapping) above) can be modified to use your own label names:

```markdown
| devpace state | External state         | Direction | Notes              |
|---------------|------------------------|-----------|--------------------|
| created       | open + my-custom-label | ↔         | Custom label name  |
```

### Entity Mapping

Maps devpace concepts to external platform concepts:

| devpace concept | External concept | Description |
|-----------------|-----------------|-------------|
| BR (Business Requirement) | Milestone | Business goals map to milestones |
| PF (Product Feature) | Epic / large Issue | Features map to epics |
| CR (Change Request) | Issue | Change requests map to issues |
| Release | Release | Releases map to platform releases |

### Gate Result Sync

Quality gate results can be synchronized to external tools:

| Gate | Pass action | Fail action |
|------|------------|-------------|
| Gate 1 (Dev Complete) | Comment + `gate-1-passed` label | Comment with failure summary |
| Gate 2 (Approval) | PR Review (approve) | Comment with review items |
| Gate 3 (Release) | Comment + `gate-3-passed` label | PR Review (request changes) |

## Integration with Other Commands

| Command | Integration |
|---------|------------|
| `/pace-dev` | CR state transitions trigger sync-push hook reminder |
| `/pace-change` | Change operations sync state to external |
| `/pace-release` | Release state sync (Phase 19) |
| `/pace-review` | Gate 2 results sync as PR Review (Phase 19) |
| `/pace-status` | Displays sync status and external links |

## Architecture (for Developers)

### Semantic Bridge Concept

Traditional integrations map "field A → field B" mechanically. devpace takes a fundamentally different approach:

- **Semantic understanding**: CR `developing` is not simply mapped to a GitHub `in-progress` label. Claude understands "this change request is being implemented" and generates the corresponding operation.
- **Contextual actions**: An external PR merge doesn't just trigger a state change — Claude understands "code has been merged, quality gate check is needed."
- **Intelligent conflict resolution**: Conflicts are not resolved by "who wins" rules, but by Claude analyzing context from both sides and providing recommendations.

### Layered Architecture

```
┌──────────────────────────────────┐
│        pace-sync Skill Layer     │
│  setup / link / push / status    │
├──────────────────────────────────┤
│   Semantic Bridge (Core Value)   │
│  Intent mapping + Conflict       │
│  detection + Adapter routing     │
├──────────────────────────────────┤
│   Existing MCP/CLI (no custom)   │
│  gh CLI / Linear MCP / Jira MCP  │
├──────────────────────────────────┤
│        Configuration Layer       │
│  sync-mapping.md + config.md     │
└──────────────────────────────────┘
```

**Key decision**: devpace does **not** build custom MCP Servers — GitHub, Linear, Jira, and GitLab all have mature existing tools. devpace focuses exclusively on the semantic orchestration layer.

### Adapter Routing

| Operation | GitHub (gh CLI) | Linear (MCP) | Jira (MCP/CLI) |
|-----------|----------------|--------------|----------------|
| Create work item | `gh issue create` | `mcp__linear__create_issue` | Phase 19+ |
| Update status | `gh issue edit --add-label` | `mcp__linear__update_issue` | Phase 19+ |
| Add comment | `gh issue comment` | `mcp__linear__create_comment` | Phase 19+ |
| Get status | `gh issue view --json` | `mcp__linear__get_issue` | Phase 19+ |

MVP defaults to GitHub via `gh` CLI (zero additional dependencies).

### Extension Points

To add a new platform adapter:

1. Add platform type to sync-mapping-format.md (`Type` field values)
2. Add tool routing section in `sync-procedures.md §1`
3. Add state mapping defaults for the platform
4. No Skill changes needed — the adapter routing is procedure-level

## Degradation & Troubleshooting

### Degradation Behavior

| Condition | Behavior |
|-----------|----------|
| No sync-mapping.md | All subcommands → guide user to `setup` |
| `gh` CLI unavailable | `setup` generates config (unverified); `push`/`status` unavailable |
| External entity deleted | `push` reports error, suggests `unlink` |
| CR has no external link | `push` skips, `status` shows "not linked" |
| config.md missing sync section | Falls back to sync-mapping.md only, no error |

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `gh auth` error | Not logged in | Run `gh auth login` |
| Label not found | Custom labels not created | Labels are auto-created on first push |
| Wrong repository | Multiple remotes | Re-run `setup` to select correct remote |
| Stale sync state | Manual external changes | Run `status` to detect drift, then `push` |

### Advisory Hook

The `sync-push.mjs` hook (PostToolUse) monitors CR file writes. When a linked CR's state changes, it outputs a non-blocking reminder:

```
devpace:sync-push CR state=developing, linked to github#42.
Consider running /pace-sync push to sync status.
```

This hook never blocks workflow (always exit 0).

## Roadmap

| Phase | Features | Status |
|-------|----------|--------|
| Phase 18 (v1.5.0) | Manual push + GitHub MVP (`setup`/`link`/`push`/`status`) | ✅ Current |
| Phase 19 | Auto-push on state change + Multi-platform (Linear, Jira) + `pull` subcommand | Planned |
| Phase 20 | Bidirectional sync + AI conflict resolution + `sync`/`resolve` subcommands | Planned |

## Related Resources

- [User Guide — /pace-sync section](../user-guide.md) — Quick reference
- [Design Document §19](../design/design.md) — Architecture decisions
- [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) — Configuration schema
- [sync-procedures.md](../../skills/pace-sync/sync-procedures.md) — Detailed operation procedures
- [devpace-rules.md §16](../../rules/devpace-rules.md) — Runtime behavior rules
