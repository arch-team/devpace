# devpace User Guide

Complete reference for using devpace in your Claude Code projects.

For a quick overview, see [README.md](../README.md). For a hands-on walkthrough, see [examples/todo-app-walkthrough.md](../examples/todo-app-walkthrough.md).

## Table of Contents

- [Getting Started](#getting-started)
- [Core Concepts](#core-concepts)
- [Commands Reference](#commands-reference)
- [Working Modes](#working-modes)
- [Change Management](#change-management)
- [Quality Gates](#quality-gates)
- [Cross-Session Continuity](#cross-session-continuity)
- [Project Files](#project-files)
- [Tips and Patterns](#tips-and-patterns)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
# Load devpace as a Claude Code plugin
claude --plugin-dir /path/to/devpace
```

### First Use

In your project directory:

```
/pace-init my-project
```

Claude guides you through an interactive setup:

1. **Project name and description** — What you're building
2. **Business goals** — 1-2 goals for this phase (e.g., "Ship a working MVP")
3. **Success metrics** — How you'll measure each goal (2-4 per goal)
4. **Implementation phases** — How you'll break the work into stages
5. **Initial features** — 3-8 features to build first
6. **Quality checks** — Your project's test/lint/build commands

Result: a `.devpace/` directory with your project's state, feature tree, and workflow rules.

### What If I Already Have a Project?

`/pace-init` works in existing projects. It creates `.devpace/` alongside your code without modifying any existing files. Add `.devpace/` to `.gitignore` if you prefer not to version-track the state files.

---

## Core Concepts

### Value Chain

devpace organizes work as a traceable chain:

```
Business Goal (OBJ)
  └── Business Requirement (BR)
        └── Product Feature (PF)
              └── Change Request (CR)
```

- **You define** goals, requirements, and features (via natural language)
- **Claude creates** change requests automatically as you work
- **Traceability** flows both ways — from goal to code, and from code back to goal

### You Never Need to Know the Terminology

devpace uses these concepts internally, but in conversation everything is natural language:

| Internal concept | What you say |
|------------------|-------------|
| Change Request | "Let's implement user auth" |
| State transition | "Is it ready for review?" |
| Quality gate | Claude handles silently |
| Feature tree | `/pace-status tree` |

---

## Commands Reference

### `/pace-init [name]`

**When**: First time setting up devpace in a project.

**Arguments**:
- `name` — Optional project name. Claude asks if omitted.

**What it does**: Creates `.devpace/` directory with state tracking, feature tree, iteration plan, workflow rules, quality checks, and metrics dashboard.

**Re-initialization**: If `.devpace/` already exists, Claude asks whether to reset.

---

### `/pace-advance [feature]`

**When**: You want to start or continue coding.

**Arguments**:
- *(empty)* — Claude picks up from where you left off (reads `state.md`)
- `feature description` — Start working on a specific feature (natural language match)

**What it does**:

1. Locates or creates a change request
2. Loads context (current state, quality rules, workflow)
3. For new CRs: runs an intent checkpoint (scoping the work)
4. Codes, tests, and validates autonomously
5. Runs quality gates automatically
6. Stops at review state for your approval

**Stops when**:
- All quality checks pass → enters review state
- Needs your decision on a technical question
- Session ending → saves checkpoint

---

### `/pace-status [level]`

**When**: You want to know where things stand.

**Arguments**:

| Argument | Output |
|----------|--------|
| *(empty)* | 1-3 line overview |
| `detail` | Expanded to product feature level |
| `tree` | Full value-feature tree |
| `metrics` | Measurement dashboard |
| `keyword` | Details on a specific feature matching the keyword |

**Output never includes** internal IDs (CR-001) or state machine terms (developing). Everything is natural language.

---

### `/pace-review [keyword]`

**When**: A change is ready for your review.

**Arguments**:
- *(empty)* — Reviews all changes in review state
- `keyword` — Reviews a specific change

**What it generates**:
- What changed (files and content)
- Why it changed (linked product feature → business goal)
- Impact scope
- Intent match (for standard/complex changes): did the code match the planned scope?
- Quality check status
- Branch name

**Your response options**:

| You say | What happens |
|---------|-------------|
| "Approved" / "LGTM" | CR merges, feature tree updates, state advances |
| "Rejected" + reason | CR returns to development, reason recorded |
| Specific feedback | Claude fixes the issues, re-runs checks, re-submits |

---

### `/pace-change [type] [description]`

**When**: Requirements change mid-work.

**Arguments**:
- `add <description>` — Insert a new feature
- `pause <feature>` — Pause a feature (preserves work)
- `resume <feature>` — Resume a paused feature
- `reprioritize <description>` — Change the work order
- `modify <feature> <changes>` — Modify an existing feature's scope
- *(empty)* — Claude asks what kind of change

**Process**: Always follows **Impact Analysis → Plan → Confirm → Execute**. Claude never makes changes without your confirmation.

See [Change Management](#change-management) for details on each change type.

---

### `/pace-retro [update]`

**When**: End of an iteration or when you want to review progress.

**Arguments**:
- *(empty)* — Full retrospective report
- `update` — Only refresh metrics data, skip the report

**Report includes**:
- Delivery: planned vs completed features
- Quality: gate pass rate, rejection rate
- Value: success metrics progress
- Cycle time: average CR duration
- What went well / what needs improvement
- Suggestions for next iteration

---

### `/pace-guide [topic]`

**When**: You want to understand devpace's design methodology.

**Arguments**:

| Topic | Content |
|-------|---------|
| *(empty)* | Quick reference card |
| `model` | Conceptual model (objects, spaces, rules) |
| `objects` | Work objects (BR, PF, CR) explained |
| `rules` | Workflow rules and quality checks |
| `trace` | Value chain traceability |
| `metrics` | Measurement framework |
| `loops` | Three feedback loops (business, product, technical) |
| `change` | Change management theory |
| `mapping` | Theory → devpace implementation mapping |
| `all` | Complete knowledge base |

**Read-only**: Never modifies state files.

---

## Working Modes

### Explore Mode (Default)

When you're reading code, analyzing problems, or discussing ideas, devpace stays out of the way:

- No state files modified
- No change requests created
- No quality gates triggered
- No workflow constraints

**Triggers**: "Look at...", "Analyze...", "Explain...", "What if..."

### Advance Mode

When you start modifying code, devpace activates:

- Creates or attaches to a change request
- Tracks state through the workflow
- Runs quality gates at transitions
- Updates state files and feature tree

**Triggers**: "Implement...", "Fix...", "Build...", "Continue..."

Claude asks when uncertain: *"Start coding, or just exploring?"*

---

## Change Management

devpace treats requirement changes as normal operations, not exceptions.

### Insert New Requirement

```
/pace-change add We need an export-to-CSV feature
```

Claude:
1. Creates a new product feature in the feature tree
2. Creates a change request
3. Evaluates iteration capacity (can this fit?)
4. Proposes scheduling (do it now, or queue it?)
5. Waits for your confirmation

### Pause a Feature

```
/pace-change pause authentication
```

Claude:
1. Marks the feature with ⏸️ in the feature tree
2. Preserves all work (code, branch, quality check progress)
3. Adjusts dependencies (unblocks anything waiting on this)
4. Updates the work plan

### Resume Paused Work

```
/pace-change resume authentication
```

Claude:
1. Restores to pre-pause state
2. Re-validates quality checks if code changed since pause
3. Updates the work plan

### Reprioritize

```
/pace-change reprioritize Move export feature before search
```

Claude:
1. Reorders the work queue
2. Updates state.md and iteration plan
3. Records the reason

### Modify Existing Requirement

```
/pace-change modify authentication Add OAuth2 support
```

Claude:
1. Updates the feature scope
2. Identifies what existing code needs rework
3. Resets affected quality checks
4. Records the change in the CR event log

---

## Quality Gates

### Gate 1: Code Quality (developing → verifying)

Automatic checks defined in `.devpace/rules/checks.md`:
- Lint / format
- Tests pass
- Type checking (if applicable)

Claude runs these automatically, fixes failures, and retries. You're not interrupted.

### Gate 2: Integration (verifying → in_review)

- Integration tests pass
- Intent consistency check (does the code match what was planned?)
- No unintended side effects

Also automatic. Claude fixes issues before advancing.

### Gate 3: Human Review (in_review → approved)

Claude generates a review summary and **stops**. You decide:
- Approve → merge
- Reject → back to development with feedback
- Request changes → Claude fixes and re-submits

---

## Cross-Session Continuity

### How It Works

1. **Session ends**: Claude updates `state.md` with current progress and next steps
2. **New session starts**: devpace hook reads `state.md` and injects context
3. **Claude reports**: One sentence describing where things stand
4. **You say "continue"**: Work resumes from exactly where it stopped

### What Gets Preserved

- Current feature being worked on
- Change request state and quality check progress
- Next recommended action
- Any blockers or dependencies

### What Doesn't Get Preserved

- Conversation history (that's a Claude session, not devpace)
- Exact tool state or file buffers

The key insight: devpace preserves **project state**, not conversation state. This means even if Claude's memory of the conversation is lost, the project state tells it everything needed to continue.

---

## Project Files

### `.devpace/state.md`

The session anchor. 5-15 lines. Auto-maintained.

Contains: current phase, active work, next step, blockers.

### `.devpace/project.md`

The value-feature tree. Shows the full hierarchy from business goals to features.

Updated automatically as features are added, completed, or paused.

### `.devpace/backlog/CR-NNN.md`

One file per change request. Contains: title, status, linked feature, quality check status, event log.

Created automatically when you start working on something.

### `.devpace/iterations/current.md`

Current iteration plan. Tracks planned vs actual, change records.

### `.devpace/rules/workflow.md` and `checks.md`

Project-specific workflow rules and quality checks. Set up during `/pace-init`.

### `.devpace/metrics/dashboard.md`

Measurement dashboard. Updated by `/pace-retro`.

---

## Tips and Patterns

### Let devpace handle the bookkeeping

Don't manually edit `.devpace/` files. Claude maintains them as a byproduct of your normal workflow.

### Use natural language for everything

Instead of `/pace-change modify auth Add OAuth2`, you can just say:

> "Actually, the auth feature also needs OAuth2 support"

Claude detects the change intent and runs the same process.

### Check status when unsure

`/pace-status` gives you a 1-line answer. No context switching, no file reading.

### Review at natural checkpoints

When Claude says "ready for review", use `/pace-review` to see a structured summary before approving.

### Run retro periodically

`/pace-retro` at the end of each iteration builds a data trail that makes future planning more accurate.

---

## Troubleshooting

### "No active devpace project"

Run `/pace-init` to set up `.devpace/` in your project directory.

### Claude doesn't restore context on new session

Check that `.devpace/state.md` exists and has content. The SessionStart hook reads this file automatically.

### Quality checks keep failing

Review `.devpace/rules/checks.md` — the commands there must work in your project (e.g., `npm test`, `pytest`).

### Feature tree looks wrong

Run `/pace-status tree` to see the current state. If it needs correction, tell Claude what's wrong and it will update.

### Changes aren't tracked

Make sure you're in advance mode (actively writing code). Explore mode doesn't track state.
