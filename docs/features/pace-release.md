# Release Management (`/pace-release`)

devpace treats release as a **proactive orchestration activity**, not passive tracking. `/pace-release` drives the full release lifecycle -- collecting merged changes, deploying across environments, verifying outcomes, and closing with automated changelog, versioning, and tagging -- through standard tools like `git` and `gh`. It orchestrates your release pipeline; it does not replace your CI/CD.

## Prerequisites

| Requirement | Purpose | Required? |
|-------------|---------|:---------:|
| `.devpace/` initialized | Core devpace project structure with merged CRs | Yes |
| `.devpace/releases/` directory | Release file storage (created on first `create`) | Auto |
| `integrations/config.md` | Gate 4 checks, deploy commands, version file config, environment promotion | Optional |
| `gh` CLI | GitHub Release creation via `tag` subcommand | Optional |

> **Graceful degradation**: Every feature works without `integrations/config.md` -- you just provide more information manually. Changelog generation always works because it reads CR metadata directly.

## Quick Start

```
1. /pace-release create   --> Collects merged CRs, suggests version, creates REL-001 (staging)
2. /pace-release deploy   --> Records deployment to target environment (deployed)
3. /pace-release verify   --> Runs verification checklist (verified)
4. /pace-release close    --> Generates changelog + bumps version + creates tag + cascading updates (closed)
```

Or simply call `/pace-release` with no arguments -- the guided wizard detects your current state and walks you through the correct next step.

## Command Reference

### User Layer

These six commands cover the standard release lifecycle. Most teams only need these.

#### `create`

Create a new Release from merged CRs.

**Syntax**: `/pace-release create`

Scans `.devpace/backlog/` for CRs in `merged` state that are not yet associated with a Release. Displays candidates sorted by type (hotfix > defect > feature), asks which to include, suggests a semantic version number, and creates a `REL-xxx.md` file in `staging` state. Optionally runs Gate 4 system-level checks if `integrations/config.md` is present. See [release-procedures-lifecycle.md "Create"](../../skills/pace-release/release-procedures-lifecycle.md) for detailed steps.

#### `deploy`

Record a deployment to an environment.

**Syntax**: `/pace-release deploy`

Supports both single-environment and multi-environment promotion. With multi-environment configuration, follows the defined promotion path (`env1 -> env2 -> ... -> envN`), executing deploy + verify per environment before promoting to the next. Appends a deployment record to the Release file and transitions state from `staging` to `deployed`. See [release-procedures-lifecycle.md "Deploy"](../../skills/pace-release/release-procedures-lifecycle.md) for detailed steps.

#### `verify`

Execute post-deployment verification.

**Syntax**: `/pace-release verify`

Presents the verification checklist (with auto-verification results pre-filled when `integrations/config.md` defines verification commands). Guides you through each item. If issues are found, records them and helps create defect/hotfix CRs linked to the current Release. On full pass, transitions state to `verified`. See [release-procedures-lifecycle.md "Verify"](../../skills/pace-release/release-procedures-lifecycle.md) for detailed steps.

#### `close`

Complete the release with all closing operations.

**Syntax**: `/pace-release close`

Requires `verified` state. Automatically executes the full closing chain: changelog generation, version file bump, Git tag creation (each step shows a brief prompt and can be skipped), then cascading state updates -- CR statuses to `released`, project.md feature tree markers, iteration tracking, state.md cleanup, and dashboard metrics. See [release-procedures-lifecycle.md "Close"](../../skills/pace-release/release-procedures-lifecycle.md) for the 8-step chain.

#### `full`

Recommended alias for `close` with clearer semantics ("complete the release" rather than "close").

**Syntax**: `/pace-release full`

Behavior is identical to `close`. See [release-procedures-lifecycle.md "Full"](../../skills/pace-release/release-procedures-lifecycle.md).

#### `status`

View current Release state and suggested next action.

**Syntax**: `/pace-release status`

Displays the active Release with CR breakdown by type, deployment issue count, verification progress, and a recommended next step. When no active Release exists, shows the count of merged CRs available for release. See [release-procedures-lifecycle.md "Status"](../../skills/pace-release/release-procedures-lifecycle.md) for output format.

### Expert Layer

These commands are available individually for teams that need fine-grained control over specific release steps. During normal `close`, steps 1-3 run automatically.

#### `changelog`

Auto-generate CHANGELOG.md from CR metadata.

**Syntax**: `/pace-release changelog`

Reads CRs included in the active Release, groups them by type (Features / Bug Fixes / Hotfixes) with PF associations, and writes entries to both the Release file and the project-root `CHANGELOG.md`. See [release-procedures-expert.md "Changelog"](../../skills/pace-release/release-procedures-expert.md).

#### `version`

Bump the semantic version number.

**Syntax**: `/pace-release version`

Reads version file configuration from `integrations/config.md` (supports JSON, TOML, YAML, plain text). Infers the bump level from CR types: feature present = minor, defect/hotfix only = patch. User can override. Updates the version file in place. See [release-procedures-expert.md "Version Bump"](../../skills/pace-release/release-procedures-expert.md).

#### `tag`

Create a Git tag and optionally a GitHub Release.

**Syntax**: `/pace-release tag`

Creates an annotated Git tag using the Release version number and configured prefix (default `v`). When `gh` CLI is available, offers to create a GitHub Release with the changelog content as release notes. See [release-procedures-expert.md "Git Tag"](../../skills/pace-release/release-procedures-expert.md).

#### `notes`

Generate user-facing Release Notes organized by business impact.

**Syntax**: `/pace-release notes`

Unlike the developer-oriented changelog (grouped by CR type), Release Notes are organized by BR (Business Requirement) and PF (Product Feature), written in product language without technical identifiers. Includes a Business Impact section that traces the Release's contribution back to OBJ-level objectives and MoS progress. See [release-procedures-expert.md "Release Notes"](../../skills/pace-release/release-procedures-expert.md).

#### `branch`

Manage release branches.

**Syntax**: `/pace-release branch [create|pr|merge]`

Supports three branching modes configured in `integrations/config.md`: direct release (default, tag on main), release branch (`release/v{version}` for final fixes), and Release PR (PR-driven release inspired by Release Please). When no branching mode is configured, all operations happen on the main branch. See [release-procedures-expert.md "Branch Management"](../../skills/pace-release/release-procedures-expert.md).

#### `rollback`

Record a rollback when a deployed Release has critical issues.

**Syntax**: `/pace-release rollback`

Only available when Release is in `deployed` state. Records the rollback reason, appends a rollback entry to the deployment log, transitions state to `rolled_back` (terminal state), and guides creation of defect/hotfix CRs for the root cause. A new Release must be created after rollback. See [release-procedures-expert.md "Rollback"](../../skills/pace-release/release-procedures-expert.md).

## Release State Machine

```
                create          deploy          verify          close
  (merged CRs) -----> staging -----> deployed -----> verified -----> closed
                                        |
                                        | rollback
                                        v
                                   rolled_back
```

| State | Meaning | Allowed transitions |
|-------|---------|---------------------|
| `staging` | Release created, CRs collected, ready for deployment | `deployed` |
| `deployed` | Deployed to target environment | `verified`, `rolled_back` |
| `verified` | Post-deployment verification passed | `closed` |
| `closed` | Release complete, all closing operations done (terminal) | -- |
| `rolled_back` | Deployment reverted due to critical issues (terminal) | -- |

Human confirmation is required for `deployed` and `verified` transitions. The `verified` to `closed` transition is automated by Claude (including the closing chain).

## Key Features

### Gate 4: System-Level Release Checks

An optional pre-deployment gate that runs after `create`:

1. **Build verification** -- executes the build command from `integrations/config.md`
2. **CI status check** -- queries CI pipeline status (auto-detects CI config if no explicit configuration)
3. **Candidate integrity** -- confirms all included CRs have passed Gates 1/2/3 (merged state)
4. **Test report** -- auto-generates a Release-level quality report via `/pace-test report`

Gate 4 does not block Release creation -- it surfaces issues before deployment.

### Changelog Auto-Generation

Changelog entries are generated entirely from CR metadata (title, type, PF association). No manual writing required. Output goes to both the Release file and a project-root `CHANGELOG.md` (appended at the top, preserving history).

### Release Notes with Business Impact

A distinct output from the changelog: organized by BR/PF in product language, with a Business Impact section that traces upward to OBJ-level objectives and MoS milestones. Provides stakeholders a clear view of what was delivered and why it matters.

### Environment Promotion

When `integrations/config.md` defines multiple environments, `deploy` follows a sequential promotion path with per-environment verification before advancing.

### Rollback Path

When a deployed Release encounters critical issues, `rollback` provides a structured response: record the incident, revert to a known state, and create CRs to track the fix. `rolled_back` is a terminal state -- recovery requires a new Release.

## Usage Scenarios

### Scenario 1: Standard Release

```
You:    /pace-release
Claude: Found 3 merged CRs ready for release.
        CR-001 (feature), CR-003 (defect), CR-005 (hotfix).
        Create a new release? [Y/n]

You:    Y
Claude: Suggested version: 1.3.0 (contains features).
        Confirm version? [1.3.0]

You:    1.3.0
Claude: REL-002 created (v1.3.0, staging).
        Gate 4: Build OK, CI green, all CRs passed.
        Next: /pace-release deploy

You:    /pace-release deploy
Claude: Deploy REL-002 (v1.3.0) to production? [Y/n]

You:    Y
Claude: Deployment recorded. Status: deployed.
        Next: /pace-release verify

You:    /pace-release verify
Claude: Verification checklist (3/3 passed).
        All items confirmed. Status: verified.
        Next: /pace-release close

You:    /pace-release close
Claude: Generating changelog... done.
        Version bump 1.2.0 -> 1.3.0? [Y] ... done.
        Create tag v1.3.0? [Y] ... done.

        Release REL-002 complete (v1.3.0).
        - Changelog written to CHANGELOG.md
        - Version updated in package.json
        - Tag v1.3.0 created
        - 3 CRs marked as released
        - Metrics updated (deploy frequency, lead time)
```

### Scenario 2: Rollback After Deployment

```
You:    /pace-release
Claude: REL-002 (v1.3.0) is deployed. Start verification? [Y/n/problem]

You:    problem
Claude: What happened?

You:    Payment processing is failing for international orders
Claude: Recording rollback for REL-002.
        Reason: Payment processing failure (international orders).
        Status: rolled_back.

        Create a hotfix CR for this issue? [Y/n]

You:    Y
Claude: CR-006 created (hotfix, linked to REL-002).
        After fixing, create a new release with /pace-release create.
```

## Integration with Other Commands

| Command | Integration point |
|---------|-------------------|
| `/pace-dev` | CRs reach `merged` state through the dev pipeline, becoming release candidates |
| `/pace-test` | `create` auto-generates a Release-level test report via `/pace-test report` |
| `/pace-feedback` | `verify` issues trigger defect CR creation through feedback flow |
| `/pace-retro` | `close` updates dashboard.md DORA metrics (deploy frequency, lead time, change failure rate) |
| `/pace-sync` | Future integration (Phase 19) for external platform release status sync |

## Related Resources

- [SKILL.md](../../skills/pace-release/SKILL.md) -- Skill entry point and subcommand overview
- [release-procedures-lifecycle.md](../../skills/pace-release/release-procedures-lifecycle.md) -- Lifecycle operations (create/deploy/verify/close/full/status)
- [release-procedures-expert.md](../../skills/pace-release/release-procedures-expert.md) -- Expert operations (changelog/version/tag/notes/branch/rollback)
- [integrations-format.md](../../knowledge/_schema/integrations-format.md) -- Integration configuration schema
- [devpace-rules.md](../../rules/devpace-rules.md) -- Runtime behavior rules
