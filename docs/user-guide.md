🌐 [中文版](user-guide_zh.md) | English

# devpace User Guide

Complete reference for managing Claude Code projects with devpace.

For a quick overview, see [README.md](../README.md). For a hands-on walkthrough, see the [end-to-end demo](../examples/todo-app-walkthrough.md).

## Table of Contents

- [Getting Started](#getting-started)
- [Core Concepts](#core-concepts)
- [Command Reference](#command-reference)
- [Work Modes](#work-modes)
- [Requirement Changes](#requirement-changes)
- [Quality Gates](#quality-gates)
- [Cross-Session Continuity](#cross-session-continuity)
- [Project Files](#project-files)
- [Tips](#tips)
- [FAQ](#faq)

---

## Getting Started

### Installation

```bash
# Load devpace as a Claude Code plugin
claude --plugin-dir /path/to/devpace
```

### First Use (2 Steps)

```
/pace-init my-project
```

Claude asks one question: **"Describe what this project does in one sentence."**

Then it auto-generates a minimal `.devpace/` (state.md + project.md + backlog/ + rules/).

From there, say "help me implement X" and you're working — feature trees, iteration plans, etc. appear automatically as you go.

### The Project Grows With Your Work

devpace doesn't require upfront planning. Initialization creates only a minimal skeleton; other files appear on demand:

| What you do | What devpace auto-creates |
|-------------|--------------------------|
| Say "help me implement X" | Feature tree (appears in project.md) |
| `/pace-plan` | Iteration plan (iterations/current.md) |
| `/pace-retro` | Metrics dashboard (metrics/dashboard.md) |
| `/pace-release create` | Release record (releases/) |

You can also use `/pace-init full` to complete the full setup at once (business goals, feature list, iteration plan, etc.).

### What About Existing Projects?

`/pace-init` works in existing projects. It creates `.devpace/` alongside your code without modifying any existing files. If you don't want state files in version control, add `.devpace/` to `.gitignore`.

---

## Core Concepts

### Traceability Chain

devpace organizes work into a traceable chain:

```
Goal → Feature → Task → Code
You define goals    You plan features    Claude auto-creates    Claude writes code
```

- **You define** goals and features (in natural language)
- **Claude auto-creates** tasks and maintains traceability throughout
- **Bidirectional traceability**: from goals to code, and from code back to goals

> **Internal terminology reference** (you don't need to memorize these — Claude won't use them in conversation either):
> Goal = OBJ/BR (Business Goal/Requirement), Feature = PF (Product Feature), Task = CR (Change Request)

### You Don't Need to Learn Any Terminology

devpace uses a precise internal concept model, but everything in conversation is natural language:

| You say | What devpace does |
|---------|-------------------|
| "帮我实现用户认证" (= "Help me implement user auth") | Auto-creates a task and starts working |
| "做到哪了" (= "Where are we") | Shows current progress |
| "准备好了吗" (= "Is it ready") | Checks quality gate status |
| "加一个导出功能" (= "Add an export feature") | Recognizes a requirement change, runs impact analysis |

---

## Command Reference

> **Core commands** (daily use): `/pace-init`, `/pace-dev`, `/pace-status`, `/pace-review`, `/pace-next`
> **Advanced commands** (when needed): `/pace-change`, `/pace-plan`, `/pace-retro`
> **Specialized commands** (optional): `/pace-test`, `/pace-release`, `/pace-guard`, `/pace-feedback`, `/pace-role`, `/pace-theory`, `/pace-trace`

### `/pace-init [name] [full]`

**When to use**: First-time devpace setup in a project.

**Arguments**:
- `name` — Optional, project name. Claude asks if omitted.
- `full` — Optional. Runs full setup (business goals, feature list, iteration plan, quality checks).

**Behavior**:
- **Default**: Creates minimal `.devpace/` (state + project stub + backlog + rules). Only asks for project name and description. After init, previews "what happens next" to orient you.
- **`full`**: Creates complete `.devpace/` with feature tree, iteration plan, metrics dashboard. Guided 6-step setup.

**Re-initialization**: If `.devpace/` already exists, Claude asks whether to reset.

---

### `/pace-dev [feature]`

**When to use**: You want to start or continue coding.

**Arguments**:
- *(empty)* — Claude continues from where it left off (reads `state.md`)
- `feature description` — Start working on the specified feature (natural language matching)

**Behavior**:

1. Locates or creates a task
2. Loads context (current state, quality rules, workflow)
3. New task: runs intent checkpoint (determines work scope)
4. Autonomous coding, testing, and verification
5. Auto-runs quality gates
6. Stops at pending-review status, waiting for your approval

**When it stops**:
- All quality checks pass → enters pending-review
- Needs your technical decision
- Session ending → saves checkpoint

---

### `/pace-status [level]`

**When to use**: You want to know the current progress.

**Arguments**:

| Argument | Output |
|----------|--------|
| *(empty)* | 1-3 line overview |
| `detail` | Expanded to feature level |
| `tree` | Full value-feature tree |
| `metrics` | Metrics dashboard |
| `chain` | Value chain view: where current work sits in the goal → feature → task tree |
| `biz` | Biz Owner perspective (MoS attainment + value delivery) |
| `pm` | PM perspective (iteration progress + feature completion) |
| `dev` | Dev perspective (CR status + quality gates) |
| `tester` | Tester perspective (defect distribution + quality metrics) |
| `ops` | Ops perspective (release status + deployment health) |
| `keyword` | Details for a specific feature matching the keyword |

**Output excludes** internal IDs (CR-001) or state machine terminology (developing). Everything is in natural language.

---

### `/pace-review [keyword]`

**When to use**: Changes are ready and waiting for your approval.

**Arguments**:
- *(empty)* — Review all changes in pending-review status
- `keyword` — Review the specified change

**Generated content**:
- What changed (files and content)
- Why it changed (linked feature → business goal)
- Blast radius
- Intent consistency (standard/complex changes): does the code match the planned scope?
- Quality check status
- Branch name

**Simplified approval**: When all conditions are met (single task, ≤3 files, quality gates passed first try, 0% drift), skips waiting and uses inline confirmation to reduce process overhead.

**Your response options**:

| You say | What happens |
|---------|-------------|
| "批准" / "approve" / "LGTM" | Task merged, feature tree updated, status advances |
| "打回" / "reject" + reason | Task returns to development, reason recorded |
| Specific feedback | Claude fixes the issue, re-checks, re-submits |

---

### `/pace-next [detail]`

**When to use**: Not sure what to do next.

**Arguments**:
- *(empty)* — 1 recommendation (≤3 lines)
- `detail` — Expanded candidate list (≤8 lines)

**Behavior**: Synthesizes multi-dimensional signals (in_review CRs, developing CRs, unverified deployments, iteration completion, retro cycles, backlog status, etc.) and recommends next actions via a 12-level priority matrix.

**Read-only**: Does not modify any state files.

---

### `/pace-plan [next|close]`

**When to use**: At iteration boundaries — closing the current iteration or planning the next one.

**Arguments**:
- *(empty)* — Evaluates current iteration status, suggests next steps
- `next` — Starts planning a new iteration directly
- `close` — Closes the current iteration (archived as iter-N.md)

**Behavior**:

1. Evaluates feature completion rate for the current iteration
2. Closes and archives the current iteration (if requested)
3. Shows available features in the feature tree
4. Guides you in selecting scope, goals, and timeline for the new iteration
5. Generates `iterations/current.md`

---

### `/pace-change [type] [description]`

**When to use**: Requirements change mid-work.

**Arguments**:
- `add <description>` — Insert a new feature
- `pause <feature>` — Pause a feature (work preserved)
- `resume <feature>` — Resume a paused feature
- `reprioritize <description>` — Adjust work order
- `modify <feature> <change>` — Modify an existing feature's scope
- *(empty)* — Claude asks for the change type

**Process**: Always follows **impact analysis → proposal → confirmation → execution**. Claude never makes changes without your confirmation.

See the [Requirement Changes](#requirement-changes) section for details.

---

### `/pace-retro [update]`

**When to use**: At the end of an iteration, or when you want to review progress.

**Arguments**:
- *(empty)* — Full retrospective report
- `update` — Refresh metrics data only, skip the report

**Report contents**:
- Delivery: planned vs. actually completed features
- Quality: gate pass rate, rejection rate
- Value: success metric progress
- Cycle time: average task duration
- What went well / what needs improvement
- Next iteration recommendations

---

### `/pace-theory [topic]`

**When to use**: You want to understand the design methodology behind devpace.

**Arguments**:

| Topic | Content |
|-------|---------|
| *(empty)* | Quick reference card |
| `model` | Concept model (objects, spaces, rules) |
| `objects` | Work objects (BR, PF, CR) explained |
| `rules` | Workflow rules and quality checks |
| `trace` | Value chain traceability |
| `metrics` | Metrics framework |
| `loops` | Three feedback loops (business, product, technical) |
| `change` | Change management theory |
| `mapping` | Theory → devpace implementation mapping |
| `why` | Explains the design rationale behind recent devpace behavior |
| `all` | Full knowledge base |

**Read-only**: Does not modify any state files.

---

### `/pace-test [subcommand]` *(optional)*

> Test verification expert — not just "run tests", but evaluates test coverage against requirement acceptance criteria, with AI-driven item-by-item acceptance verification.

**When to use**: You want to know if tests are sufficient, where gaps exist, and how to fill them.

**By scenario**:

**During daily development**:

| Usage | Effect |
|-------|--------|
| `/pace-test` | Runs all configured tests, outputs a structured report |
| `/pace-test accept` | AI compares each acceptance criterion — with code line-number evidence, three-level verdict (✅ Pass / ⚠️ Needs additional verification / ❌ Fail), reviews test assertion substantiveness |

**Understanding the testing landscape**:

| Usage | Effect |
|-------|--------|
| `/pace-test strategy` | Generates test strategy from feature acceptance criteria — recommends test type (including security/performance auxiliary types) and priority for each criterion |
| `/pace-test coverage` | Analyzes test coverage of acceptance criteria (requirement coverage primary, code coverage secondary) |
| `/pace-test report` | Aggregates three layers into a review report: test results + requirement coverage + AI acceptance |

**After requirement changes**:

| Usage | Effect |
|-------|--------|
| `/pace-test impact` | Analyzes which features are affected by code changes, recommends tests to re-run by priority |
| `/pace-test impact --run` | Analyzes then auto-executes the "must-run" test list |

**Going deeper** (use as needed):

| Usage | Effect |
|-------|--------|
| `generate [--full]` | Generates test cases from acceptance criteria (skeleton by default, `--full` for complete implementation) |
| `flaky` | Test health analysis: flaky tests, empty assertions, duration inflation, long-unchanged tests |
| `dryrun [1\|2\|4]` | Simulates Gate checks (no state transitions, for pre-flight verification) |
| `baseline` | Establishes a test baseline (for retrospective metric comparison) |
| `report REL-xxx` | Release-level quality report (aggregates all CR test data + release recommendation) |

**accept enhances approval quality**:

Gate 2 checks "does the code match the plan." accept builds on this with finer-grained evidence, helping humans approve more efficiently:

- Per-criterion acceptance with code evidence (referencing specific files and line numbers)
- Three-level verdict: ✅ Pass / ⚠️ Needs additional verification / ❌ Fail (Gate 2 only has pass/fail)
- Test oracle review: do existing tests actually verify the acceptance conditions they claim to cover?
- Auto-downgrade: when weak or false coverage is found, automatically downgrades test strategy status

You can pass Gate 2 without running accept — but changes with accept have stronger evidence for human review.

**Recommended workflow**:

- First time: `strategy` → `generate` → write implementation → `coverage` → develop → run tests → `accept` → `report`
- Daily: run tests + `accept` is enough. After changes, use `impact --run` for quick regression
- Pre-release: `report REL-xxx` generates a release-level quality report

---

### `/pace-release [action]` *(optional)*

> This is an optional feature. If you don't have a formal release process, you can skip it. Task merged is your completion point.

**When to use**: Managing production releases — from creating a Release to generating Changelog, version bump, Git Tag, and GitHub Release.

**Arguments**:

**Daily use** (most scenarios only need these):

| Argument | Action |
|----------|--------|
| `create` | Collects merged tasks to create a new release + Gate 4 system-level checks |
| `deploy` | Records that deployment was executed (supports multi-environment promotion) |
| `verify` | Executes verification checklist (supports automated verification commands) |
| `close` | Completes the release (auto changelog + version bump + tag + cascading updates) |
| `full` | Recommended alias for close (clearer semantics) |
| `status` | Views current release status and suggested next step |
| *(empty)* | Guided release wizard — auto-guides based on current state (recommended for new users) |

**Standalone use** (when you only need a specific step):

| Argument | Action |
|----------|--------|
| `changelog` | Generates CHANGELOG.md only (close auto-executes this step) |
| `version` | Updates version files only (close auto-executes this step) |
| `tag` | Creates Git Tag / GitHub Release only (close auto-executes this step) |
| `notes` | Generates end-user-facing Release Notes (grouped by business requirements) |
| `branch` | Manages release branches (creates release branch or Release PR) |
| `rollback` | Records rollback operation (when critical issues arise in deployed state) |

**Changelog vs Release Notes**:

| | Changelog | Release Notes |
|---|-----------|---------------|
| Audience | Developers | Product users |
| Organization | By type (Features / Bug Fixes) | By business requirement → feature |
| Language | Technical | Product-facing |

**Release branches** (optional, configured in integrations/config.md):

- `branch create` — Creates a `release/v{version}` branch
- `branch pr` — Creates a Release PR (with changelog + version bump); merging the PR = confirming the release
- `branch merge` — Merges the release branch back to main

**Rollback**: When critical issues are found in deployed state, `/pace-release rollback` records the rollback reason and guides creation of a fix task. rolled_back is a terminal state; a new Release is needed after the fix.

**Configuration enhancements**: In `.devpace/integrations/config.md` you can configure version file paths/formats, verification commands, release branch patterns, and CI check commands. Without configuration, all features degrade to manual mode. For multi-environment setups, environments are promoted sequentially by row order in the environment table (e.g., staging → canary → production), with independent deploy + verify per environment.

---

### `/pace-guard [action]` *(optional)*

> This is an optional feature. Requires the `.devpace/risks/` directory (`/pace-init` doesn't auto-create it; it's created on first use). L/XL complexity CRs auto-trigger `scan` at the intent checkpoint.

**When to use**: Assessing risks before coding, tracking risk status during development, analyzing risk trends across iterations.

**Arguments**:

| Argument | Action |
|----------|--------|
| `scan [CR-ID]` | Pre-flight risk scan — 5-dimension assessment (historical lessons / dependency impact / architecture compatibility / scope complexity / security sensitivity) |
| `monitor [CR-ID]` | Summarizes real-time risk status for a CR (mitigated / pending / new) |
| `trends [iteration-ID]` | Cross-CR trend analysis (by category, recurring risk identification, improvement suggestions) |
| `report` | Project-level risk dashboard (grouped by PF, sorted by severity, overall risk score) |
| `resolve <RISK-ID> <status>` | Updates risk status (mitigated / accepted / closed) |
| *(empty)* | Same as `scan`, runs risk scan on the current CR |

**Risk levels and responses**:

| Level | Behavior |
|-------|----------|
| Low | Silent logging, no interruption |
| Medium | Logged + reminder + mitigation suggestions |
| High | Development paused, awaits human confirmation (non-negotiable) |

**Auto-triggers** (no manual invocation needed):
- L/XL CRs auto-trigger `scan` on entering development
- Advance mode runs lightweight risk detection at each checkpoint
- Pulse checks trigger `monitor` when risk backlog is detected

**Degraded mode**: Without `.devpace/`, `scan` still works (instant assessment based on codebase), but `trends`/`report`/`resolve` require historical data and are unavailable.

---

### `/pace-feedback [report <description>] or [feedback description]` *(optional)*

> This is an optional feature. Used for systematically collecting post-launch feedback and handling production incidents.

**When to use**: Receiving user feedback, finding bugs, or reporting production issues.

**Arguments**:
- `report <description>` — Report a production issue directly (skips triage)
- `<feedback description>` — Classified and routed (defect / improvement / new requirement / production incident)
- *(empty)* — Guided collection (asks about issue type, impact, and urgency)

**Behavior**:
1. Classifies feedback (production incident / defect / improvement / new requirement)
2. Production incident: assesses severity → traces origin → creates defect/hotfix task
3. Defect: auto-creates a fix task linked to the feature
4. Improvement / new requirement: recorded or routed through change management

---

### `/pace-trace [keyword]` *(optional)*

**When to use**: You want to understand the full reasoning behind a Claude decision.

**Arguments**:
- `keyword` — Query the reasoning trace for a specific decision (e.g., "why rejected", "Gate 2")
- *(empty)* — Shows the most recent decision trace

**Behavior**: Reads task event tables, checkpoint markers, and traceability tags to reconstruct the complete reasoning process behind Gate/intent/change decisions.

**Read-only**: Does not modify any state files.

---

### `/pace-role [role]` *(optional)*

> Switches Claude's output perspective. Default is Dev perspective when not switched.

**When to use**: You want to view project information from a different perspective.

**Arguments**:

| Role | Focus |
|------|-------|
| `biz` | Business value, goal attainment |
| `pm` | Delivery cadence, priorities, iteration progress |
| `dev` | Code quality, technical details (default) |
| `tester` | Defect distribution, test coverage |
| `ops` | Release status, deployment health |
| *(empty)* | Shows current role and options |

---

## Work Modes

### Explore Mode (Default)

When you're reading code, analyzing problems, or discussing approaches, devpace stays out of your way:

- No state file modifications
- No task creation
- No quality gate triggers
- No workflow constraints

**Trigger phrases**: "look at...", "analyze...", "explain...", "what if..."

### Advance Mode

When you start modifying code, devpace activates:

- Creates or links a task
- Tracks status through the workflow
- Runs quality gates at state transitions
- Updates state files and feature tree

**Trigger phrases**: `/pace-dev` (direct entry), or "implement...", "fix...", "develop...", "continue..."

**First-entry confirmation**: The first time you express coding intent in a session (without using `/pace-dev`), Claude naturally asks: *"Want me to track this change, or is this just a quick fix?"* Choosing to track automatically enters Advance mode for the rest of the session. Choosing "just a quick fix" skips tracking.

Using `/pace-dev` always enters Advance mode directly, no confirmation needed.

### State Machine Details

> You don't need to know this for daily use. This is the complete reference for task state transitions in Advance mode.

```
created -> developing -> verifying -> in_review -> approved -> merged -> released (optional)
              |               |            ^
              |               |            |
              +-- Gate 1 -----+-- Gate 2 --+-- Gate 3 (human)
              (code quality)  (integration)  (code review)

Any state <-> paused  (preserves all work, change management)
Hotfix fast path: created -> developing -> verifying -> merged (critical only)
```

| State | User perception | Description |
|-------|----------------|-------------|
| created | "Created" | Task just created, not started yet |
| developing | "In progress" | Claude is writing code and tests |
| verifying | "Verifying" | Integration tests and intent consistency checks |
| in_review | "Awaiting your approval" | Claude stops, waiting for your decision |
| approved | "Approved" | You approved, merging in progress |
| merged | "Done" | Code merged (default terminal state) |
| released | "Released" | Auto-marked after Release closes (optional terminal state) |
| paused | "Paused" | Paused due to requirement change, all work preserved |

- **Gate 1/2**: Claude runs automatically, auto-fixes failures, doesn't bother you
- **Gate 3**: Human code review — Claude generates a summary and waits for you
- **released**: Optional — if you don't use a release process, `merged` is the endpoint

### Task Types

| Type | Purpose | Description |
|------|---------|-------------|
| feature | New feature or enhancement (default) | Product feature development in normal iterations |
| defect | Defect fix | Issues found in released features |
| hotfix | Emergency fix | Critical production issues, eligible for fast path |

---

## Requirement Changes

devpace treats requirement changes as normal operations, not exceptions.

### Inserting a New Requirement

```
/pace-change add 我们需要一个导出 CSV 的功能
```
(= "We need a CSV export feature")

Claude:
1. Creates a new feature in the feature tree
2. Creates a task
3. Evaluates iteration capacity (can it fit?)
4. Proposes scheduling (do it now, or queue it?)
5. Waits for your confirmation

### Pausing a Feature

```
/pace-change pause authentication
```

Claude:
1. Marks ⏸️ in the feature tree
2. Preserves all work (code, branches, quality check progress)
3. Adjusts dependencies (unblocks tasks waiting on this feature)
4. Updates the work plan

### Resuming Paused Work

```
/pace-change resume authentication
```

Claude:
1. Restores to pre-pause state
2. If code changed during the pause, re-validates quality checks
3. Updates the work plan

### Reprioritizing

```
/pace-change reprioritize 把导出功能排到搜索前面
```
(= "Move export ahead of search")

Claude:
1. Reorders the work queue
2. Updates state.md and iteration plan
3. Records the reason

### Modifying an Existing Requirement

```
/pace-change modify authentication 增加 OAuth2 支持
```
(= "Add OAuth2 support to authentication")

Claude:
1. Updates feature scope
2. Identifies which existing code needs rework
3. Resets affected quality checks
4. Records the change in the task event log

---

## Quality Gates

### Gate 1: Code Quality (developing → verifying)

Automated checks defined in `.devpace/rules/checks.md`:
- Lint / formatting
- Tests pass
- Type checks (if applicable)

Claude runs automatically, fixes failures and retries. Doesn't bother you.

### Gate 2: Integration Check (verifying → in_review)

- Integration tests pass
- Intent consistency check (does the code match the plan?)
- No unexpected side effects

Also automatic. Claude fixes issues before advancing.

### Gate 3: Human Approval (in_review → approved)

Claude generates a review summary and **stops**. You decide:
- Approve → merge
- Reject → returns to development with feedback
- Request changes → Claude fixes and resubmits

### Gate 4: System-Level Release Gate (Release create → deploy) *(optional)*

Release-level checks (depends on `integrations/config.md` configuration):
- Runs build/test commands to verify the code builds
- Checks CI pipeline status
- Confirms all included tasks passed Gate 1/2/3

Without configuration, Gate 4 silently skips and doesn't affect the release flow.

---

## Cross-Session Continuity

### How It Works

1. **Session ends**: Claude updates `state.md`, recording current progress and next steps
2. **New session starts**: devpace Hook reads `state.md` and injects context
3. **Claude reports**: one sentence describing the current situation
4. **You say "continue"**: work resumes precisely from where it left off

**Adaptive session end**: No `.devpace/` changes means no end protocol; simple scenarios get 1 line, standard scenarios 3 lines, complex scenarios 5 lines — avoiding unnecessary overhead.

### What's Preserved

- Feature currently being worked on
- Task status and quality check progress
- Next step recommendations
- Blockers and dependencies

### What's NOT Preserved

- Conversation history (that's the Claude session, not devpace)
- Tool state or file buffers

Key insight: devpace preserves **project state**, not conversation state. This means even if Claude loses conversation memory, the project state tells it everything needed to continue.

---

## Project Files

### `.devpace/state.md`

Session anchor. 5-15 lines. Auto-maintained.

Contains: current phase, work in progress, next steps, blockers.

### `.devpace/project.md`

Value-feature tree. Shows the complete hierarchy from business goals to features.

Auto-updated when features are added, completed, or paused.

### `.devpace/backlog/CR-NNN.md`

One file per task. Contains: title, status, linked feature, quality check status, event log.

Auto-created when work begins.

### `.devpace/iterations/current.md`

Current iteration plan. Tracks planned vs. actual, change log.

### `.devpace/rules/workflow.md` and `checks.md`

Project-specific workflow rules and quality checks. Set up during `/pace-init`.

### `.devpace/metrics/dashboard.md`

Metrics dashboard. Updated by `/pace-retro`.

---

## Tips

### Let devpace Handle the Bookkeeping

Don't manually edit `.devpace/` files. Claude maintains them automatically as you work.

### Use Natural Language for Everything

Instead of `/pace-change modify auth Add OAuth2`, you can simply say:

> "认证功能还需要支持 OAuth2" (= "Auth also needs OAuth2 support")

Claude detects the change intent and executes the same flow.

### Check Status When Unsure

`/pace-status` gives you a one-line answer. No context switching, no digging through files.

### Approve at Natural Checkpoints

When Claude says "ready for review," use `/pace-review` to see a structured summary before approving.

### Run Retrospectives Regularly

Run `/pace-retro` at the end of each iteration. Accumulated data makes future planning more accurate.

---

## FAQ

### "No active devpace project"

Run `/pace-init` to set up `.devpace/` in your project directory.

### Claude Doesn't Restore Context in a New Session

Check that `.devpace/state.md` exists and has content. The SessionStart Hook auto-reads this file.

### Quality Checks Keep Failing

Check `.devpace/rules/checks.md` — the commands inside must work in your project (e.g., `npm test`, `pytest`).

### Feature Tree Looks Wrong

Run `/pace-status tree` to see the current state. If it needs correction, tell Claude what's wrong and it will update.

### Changes Aren't Being Tracked

Make sure you're in Advance mode (actively writing code). Explore mode doesn't track state.
