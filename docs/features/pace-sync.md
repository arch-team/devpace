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
1. /pace-sync setup           → Detects git remote → generates sync-mapping.md
   /pace-sync setup --auto    → Same but skips interactive prompts (CI/CD friendly)
2. /pace-sync                 → Smart sync: detects changes, shows summary, syncs all entity types
   /pace-sync --dry-run       → Preview changes without executing
3. /pace-sync link CR-003 #42 → Associates CR-003 with GitHub Issue #42
   /pace-sync link EPIC-001   → Smart match: searches Issues by title similarity
```

After setup, the sync-push advisory hook automatically reminds you to run `/pace-sync` after state changes. The smart sync detects which entities changed (via content hash) and only pushes the differences.

## Command Reference

### `setup`

Guided configuration wizard.

**Syntax**: `/pace-sync setup [--auto]`

Detects `git remote`, auto-selects platform adapter based on remote URL domain, verifies `gh` CLI connectivity, and generates `.devpace/integrations/sync-mapping.md` per the [sync-mapping-format.md](../../knowledge/_schema/integration/sync-mapping-format.md) schema. With `--auto`, skips all interactive prompts and uses defaults (push mode, ask-user conflict strategy). See [sync-procedures-setup.md](../../skills/pace-sync/sync-procedures-setup.md) for detailed steps.

**Auto-setup via `/pace-init`**: When init detects a supported git remote (e.g., github.com) and `gh auth status` passes, sync configuration is generated automatically as a natural extension of init — no separate setup step needed.

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

**Syntax**: `/pace-sync link <CR-ID> [#ExternalID]` (e.g., `link CR-003 #42` or `link CR-003`)

Verifies both the CR and external entity exist, writes the association into the CR file and sync-mapping.md. When external ID is omitted, performs **smart match**: searches external platform for Issues with similar titles and presents a candidate list. Supports `--all` to batch-link all unlinked CRs. See [sync-procedures-link.md](../../skills/pace-sync/sync-procedures-link.md) for detailed steps.

**Error handling**: CR not found, external entity not found → prompts user. CR already linked → confirms before overwriting. No title match found → suggests running `/pace-sync` to auto-create.

### `sync` (Smart Sync — Default Command)

Intelligent sync: auto-detect changes, present summary, execute after confirmation. Absorbs previous `push` and `create` functionality.

**Syntax**: `/pace-sync` or `/pace-sync sync [--dry-run]`

Runs `skills/pace-sync/scripts/compute-sync-diff.mjs` to detect all entity changes (Epic/BR/PF/CR), presents a summary showing changed/new/unchanged entities, and after user confirmation: creates Issues for unlinked entities (in hierarchy order: Epic→BR→PF→CR) and pushes state updates for changed entities. With `--dry-run`, only shows what would happen without executing.

**Output example**:
```
Sync detection:
- 3 entities changed (CR-003 status→developing, EPIC-001 progress↑, PF-002 acceptance updated)
- 2 new entities unlinked (BR-003, CR-008)
- 7 entities in sync

| Entity   | Type | External   | Action              | Result |
|----------|------|------------|---------------------|--------|
| EPIC-001 | Epic | [#10](URL) | Update label        | ✅     |
| BR-003   | BR   | [#15](URL) | Create Issue        | ✅     |
| CR-003   | CR   | [#42](URL) | Update label + Comment | ✅  |

Summary: 3 synced / 2 created / 7 unchanged
Hierarchy: 2 sub-issue relationships established
```

### `unlink`

Remove the association between an entity and its external Issue.

**Syntax**: `/pace-sync unlink <EntityID>` (e.g., `unlink CR-003`, `unlink EPIC-001`)

Clears the external association field from the entity file and removes the record from sync-mapping.md. See [sync-procedures-status.md §4](../../skills/pace-sync/sync-procedures-status.md) for detailed steps.

**Error handling**: Entity has no association or doesn't exist → prompts user.

### `pull` (Lightweight MVP)

Check external state and prompt to update devpace state.

**Syntax**: `/pace-sync pull <CR-ID>`

Queries the external platform for the current state of a linked CR's Issue, compares with devpace state, and prompts the user to update if inconsistent. Does **not** auto-modify devpace state — requires user confirmation and validates against the CR state machine rules. See [sync-procedures-pull.md](../../skills/pace-sync/sync-procedures-pull.md) for detailed steps.

**Output example** (inconsistent):
```
CR-003 state mismatch:
- devpace: developing
- External (#42): closed + done → maps to: merged

Update devpace state to merged?
Note: this transition must comply with devpace state machine rules.
[Update / Skip]
```

**Error handling**: CR has no association → prompts to link first. `gh` unavailable → prompts installation. State transition invalid → explains why and suggests normal workflow.

### `status`

View sync status for all linked CRs.

**Syntax**: `/pace-sync status`

Reads all association records, compares devpace vs external state, and outputs a consistency table. See [sync-procedures-status.md](../../skills/pace-sync/sync-procedures-status.md) for detailed steps.

**Output example**:
```
| CR     | External | devpace    | External      | Consistent | Last sync    |
|--------|----------|------------|---------------|------------|--------------|
| CR-003 | #42      | developing | in-progress   | ✅          | 02-25 10:30  |
| CR-005 | #18      | merged     | open          | ❌ push     | 02-24 15:00  |
```

## State Mapping

devpace CR states map to GitHub labels (e.g., `developing` → `in-progress`, `merged` → close Issue + `done`). The full mapping table is defined in [sync-mapping-format.md](../../knowledge/_schema/integration/sync-mapping-format.md) (schema authority) and [sync-adapter-github.md](../../skills/pace-sync/sync-adapter-github.md) (GitHub-specific operations).

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
        Consider running /pace-sync to sync status.

You:    /pace-sync CR-003
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

        1 CR out of sync. Run /pace-sync to update.
```

## Configuration Reference

The sync configuration lives in `.devpace/integrations/sync-mapping.md`, following the [sync-mapping-format.md](../../knowledge/_schema/integration/sync-mapping-format.md) schema.

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

The [sync-mapping-format.md](../../knowledge/_schema/integration/sync-mapping-format.md) schema defines all configuration sections: platform fields, state mapping, entity mapping, gate result sync, and association records.

## Integration with Other Commands

`/pace-dev` and `/pace-change` trigger the sync-push advisory hook after CR state changes. `/pace-status` displays sync status alongside CR info. Future integrations include `/pace-release` and `/pace-review` (Phase 19). See [sync-procedures-common.md §5](../../skills/pace-sync/sync-procedures-common.md) for the full integration matrix.

## Architecture (for Developers)

### Semantic Bridge Concept

Traditional integrations map "field A → field B" mechanically. devpace takes a fundamentally different approach:

- **Semantic understanding**: CR `developing` is not simply mapped to a GitHub `in-progress` label. Claude understands "this change request is being implemented" and generates the corresponding operation.
- **Contextual actions**: An external PR merge doesn't just trigger a state change — Claude understands "code has been merged, quality gate check is needed."
- **Intelligent conflict resolution**: Conflicts are not resolved by "who wins" rules, but by Claude analyzing context from both sides and providing recommendations.

### Layered Architecture

```
┌──────────────────────────────────────┐
│          pace-sync Skill Layer       │
│  setup/link/push/pull/unlink/create/ │
│  ci status/ci trigger/ci logs/       │
├──────────────────────────────────────┤
│  Operation Orchestration             │
│  sync-procedures-*.md                │
│  (on-demand loaded per subcommand)   │
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
- Platform adapters are split into per-platform files (e.g., `sync-adapter-github.md`). `sync-procedures-*.md` files use operation semantics (e.g., "verify connection", "update status marker") that reference the adapter's operation table. Adding a new platform requires zero changes to procedures (OCP).

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
3. Add routing entry to `sync-procedures-common.md §1` adapter route table
4. No changes needed to sync-procedures-*.md subcommand steps or SKILL.md (OCP verified)

## Degradation & Troubleshooting

### Degradation Behavior

All subcommands gracefully degrade: missing sync-mapping.md guides to `setup`, unavailable `gh` CLI allows config creation but blocks push/status, and missing associations are skipped silently. The full degradation matrix is defined in [sync-mapping-format.md](../../knowledge/_schema/integration/sync-mapping-format.md).

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
  Consider running /pace-sync to sync status.
  ```
- **Merged transition** — directive language (§11 step 7 safety net):
  ```
  devpace:sync-push CR-003 state transition: in_review→merged, linked to github#42.
  Auto-execute: /pace-sync CR-003 (§11 step 7 — close Issue + done label + completion summary)
  ```

**post-cr-update.mjs** — Detects merged state and outputs the full 7-step post-merge pipeline (§11 aligned). Step 7 (external sync push) is conditionally included only when `sync-mapping.md` exists and the CR has an external link.

Both hooks never block workflow (always exit 0, async execution).

## Roadmap

| Phase | Features | Status |
|-------|----------|--------|
| Phase 18 (v1.5.0) | Semantic MVP + GitHub (`setup`/`link`/`push`/`unlink`/`create`/`status` + `--dry-run` + merged auto-push) | ✅ |
| Phase 18.5 | UX optimizations: `setup --auto`, smart link by title, `link --all`, lightweight `pull` MVP, enhanced dry-run (diff + selective push), graded push output, semantic Comment enrichment (transition context + change summary + PR link), Hook noise reduction, teaching catalog expansion | ✅ Current |
| Phase 19 | Smart push + Issue lifecycle + Gate→PR Review + Multi-platform preview (Linear) | Planned |
| Phase 20 | Polling inbound + AI conflict resolution + Multi-platform full support | Planned |

## Related Resources

- [User Guide — /pace-sync section](../user-guide.md) — Quick reference
- [Design Document §19](../design/design.md) — Architecture decisions
- [sync-mapping-format.md](../../knowledge/_schema/integration/sync-mapping-format.md) — Configuration schema
- [sync-procedures-common.md](../../skills/pace-sync/sync-procedures-common.md) — Platform-agnostic operation orchestration (route index)
- [sync-adapter-github.md](../../skills/pace-sync/sync-adapter-github.md) — GitHub adapter (gh CLI commands)
- [devpace-rules.md §16](../../rules/devpace-rules.md) — Runtime behavior rules
