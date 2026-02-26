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

Detects `git remote`, verifies `gh` CLI connectivity, and generates `.devpace/integrations/sync-mapping.md` per the [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) schema. See [sync-procedures.md §2](../../skills/pace-sync/sync-procedures.md) for detailed steps.

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

**Syntax**: `/pace-sync link <CR-ID> <#ExternalID>` (e.g., `link CR-003 #42`)

Verifies both the CR and external entity exist, writes the association into the CR file and sync-mapping.md. See [sync-procedures.md §3](../../skills/pace-sync/sync-procedures.md) for detailed steps.

**Error handling**: CR not found, external entity not found → prompts user. CR already linked → confirms before overwriting.

### `push`

Push devpace state to external tools.

**Syntax**: `/pace-sync push [CR-ID] [--dry-run]`

Pushes CR state to external platform for one or all linked CRs. With `--dry-run`, previews actions without executing. Compares local vs external state and only updates when inconsistent. See [sync-procedures.md §4](../../skills/pace-sync/sync-procedures.md) for detailed steps.

**Output example**:
```
| CR     | State      | External action            | Result |
|--------|------------|----------------------------|--------|
| CR-003 | developing | Add label: in-progress     | ✅     |
| CR-005 | merged     | Close Issue #18 + add done | ✅     |
```

### `unlink`

Remove the association between a CR and its external entity.

**Syntax**: `/pace-sync unlink <CR-ID>`

Clears the external association field from the CR file and removes the record from sync-mapping.md. See [sync-procedures.md §5.5](../../skills/pace-sync/sync-procedures.md) for detailed steps.

**Error handling**: CR has no association or doesn't exist → prompts user.

### `create`

Create an external Issue from CR metadata and automatically link it.

**Syntax**: `/pace-sync create <CR-ID>`

Reads CR metadata (title, intent, acceptance criteria), creates an Issue with the appropriate state label, and auto-links via the `link` flow. See [sync-procedures.md §5.6](../../skills/pace-sync/sync-procedures.md) for detailed steps.

**Error handling**: CR already linked → confirms before overriding. `gh` unavailable → prompts installation. CR doesn't exist → prompts user.

### `status`

View sync status for all linked CRs.

**Syntax**: `/pace-sync status`

Reads all association records, compares devpace vs external state, and outputs a consistency table. See [sync-procedures.md §5](../../skills/pace-sync/sync-procedures.md) for detailed steps.

**Output example**:
```
| CR     | External | devpace    | External      | Consistent | Last sync    |
|--------|----------|------------|---------------|------------|--------------|
| CR-003 | #42      | developing | in-progress   | ✅          | 02-25 10:30  |
| CR-005 | #18      | merged     | open          | ❌ push     | 02-24 15:00  |
```

## State Mapping

devpace CR states map to GitHub labels (e.g., `developing` → `in-progress`, `merged` → close Issue + `done`). The full mapping table is defined in [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) (schema authority) and [sync-adapter-github.md](../../skills/pace-sync/sync-adapter-github.md) (GitHub-specific operations).

The effective sync direction is the intersection of the platform sync mode and the per-state direction. In push mode, even bidirectional states only execute the push direction.

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

After a `/pace-dev` session transitions CR-003 from `created` to `developing`, the sync-push hook detects the actual state transition and reminds you:

```
Hook:   devpace:sync-push CR-003 state transition: created→developing, linked to github#42.
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

### State Mapping Table

Customizable per-project. The default mapping can be modified to use your own label names:

```markdown
| devpace state | External state         | Direction | Notes              |
|---------------|------------------------|-----------|--------------------|
| created       | open + my-custom-label | ↔         | Custom label name  |
```

The [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) schema defines all configuration sections: platform fields, state mapping, entity mapping, gate result sync, and association records.

## Integration with Other Commands

`/pace-dev` and `/pace-change` trigger the sync-push advisory hook after CR state changes. `/pace-status` displays sync status alongside CR info. Future integrations include `/pace-release` and `/pace-review` (Phase 19). See [sync-procedures.md §7](../../skills/pace-sync/sync-procedures.md) for the full integration matrix.

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
│  setup/link/push/unlink/create/  │
├──────────────────────────────────┤
│  Operation Orchestration         │
│  sync-procedures.md              │
│  (platform-agnostic steps)       │
├──────────────────────────────────┤
│  Platform Adapters               │
│  sync-adapter-github.md          │
│  sync-adapter-linear.md (P19)    │
├──────────────────────────────────┤
│  Existing MCP/CLI (no custom)    │
│  gh CLI / Linear MCP / Jira MCP  │
├──────────────────────────────────┤
│        Configuration Layer       │
│  sync-mapping.md + config.md     │
└──────────────────────────────────┘
```

**Key decisions**:
- devpace does **not** build custom MCP Servers — GitHub, Linear, Jira, and GitLab all have mature existing tools. devpace focuses exclusively on the semantic orchestration layer.
- Platform adapters are split into per-platform files (e.g., `sync-adapter-github.md`). `sync-procedures.md` uses operation semantics (e.g., "verify connection", "update status marker") that reference the adapter's operation table. Adding a new platform requires zero changes to procedures (OCP).

### Adapter Routing

| Platform | Adapter file | Tool | Status |
|----------|-------------|------|--------|
| GitHub | sync-adapter-github.md | gh CLI | Available |
| Linear | sync-adapter-linear.md | MCP | Phase 19 |
| Jira | sync-adapter-jira.md | MCP/CLI | Phase 19+ |

MVP defaults to GitHub via `gh` CLI (zero additional dependencies). Subcommand steps use operation semantics; Claude loads the corresponding adapter file based on the platform field in sync-mapping.md.

### Extension Points

To add a new platform adapter:

1. Create `sync-adapter-{platform}.md` with operation table, state update strategy, and platform-specific rules
2. Add platform type to sync-mapping-format.md (`Type` field values)
3. Add routing entry to `sync-procedures.md §1` adapter route table
4. No changes needed to sync-procedures.md subcommand steps or SKILL.md (OCP verified)

## Degradation & Troubleshooting

### Degradation Behavior

All subcommands gracefully degrade: missing sync-mapping.md guides to `setup`, unavailable `gh` CLI allows config creation but blocks push/status, and missing associations are skipped silently. The full degradation matrix is defined in [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md).

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `gh auth` error | Not logged in | Run `gh auth login` |
| Label not found | Custom labels not created | Labels are auto-created on first push |
| Wrong repository | Multiple remotes | Re-run `setup` to select correct remote |
| Stale sync state | Manual external changes | Run `status` to detect drift, then `push` |

### Advisory Hooks (Dual-Layer)

Two PostToolUse hooks work together to ensure external sync on CR state transitions:

**sync-push.mjs** — State change detection via file-based cache (`.devpace/.sync-state-cache`). Only fires on **actual state transitions**, not on every CR write (eliminates noise). Output varies by transition type:

- **Non-merged transitions** — advisory suggestion:
  ```
  devpace:sync-push CR-003 state transition: created→developing, linked to github#42.
  Consider running /pace-sync push to sync status.
  ```
- **Merged transition** — directive language (§11 step 7 safety net):
  ```
  devpace:sync-push CR-003 state transition: in_review→merged, linked to github#42.
  Auto-execute: /pace-sync push CR-003 (§11 step 7 — close Issue + done label + completion summary)
  ```

**post-cr-update.mjs** — Detects merged state and outputs the full 7-step post-merge pipeline (§11 aligned). Step 7 (external sync push) is conditionally included only when `sync-mapping.md` exists and the CR has an external link.

Both hooks never block workflow (always exit 0, async execution).

## Roadmap

| Phase | Features | Status |
|-------|----------|--------|
| Phase 18 (v1.5.0) | Semantic MVP + GitHub (`setup`/`link`/`push`/`unlink`/`create`/`status` + `--dry-run` + merged auto-push) | ✅ Current |
| Phase 19 | Smart push + Issue lifecycle + Gate sync + Multi-platform preview (Linear) | Planned |
| Phase 20 | Polling inbound + AI conflict resolution + Multi-platform full support | Planned |

## Related Resources

- [User Guide — /pace-sync section](../user-guide.md) — Quick reference
- [Design Document §19](../design/design.md) — Architecture decisions
- [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) — Configuration schema
- [sync-procedures.md](../../skills/pace-sync/sync-procedures.md) — Platform-agnostic operation orchestration
- [sync-adapter-github.md](../../skills/pace-sync/sync-adapter-github.md) — GitHub adapter (gh CLI commands)
- [devpace-rules.md §16](../../rules/devpace-rules.md) — Runtime behavior rules
