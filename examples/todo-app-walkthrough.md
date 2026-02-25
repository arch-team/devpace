🌐 [中文版](todo-app-walkthrough_zh.md) | English

# End-to-End Walkthrough: Todo App

This walkthrough shows devpace managing a full development cycle — from project initialization to task merge, including a mid-stream requirements change.

## Prerequisites

- [Claude Code CLI](https://claude.ai/code) installed
- devpace obtained: `git clone https://github.com/arch-team/devpace.git`

## Setup

```bash
# Load devpace plugin in your project directory
cd ~/projects/my-todo-app
claude --plugin-dir ~/devpace    # replace with the actual path where you cloned devpace
```

## Phase 1: Initialization

**You**: `/pace-init my-todo-app`

**Claude** asks one question:

1. *Describe what this project does in one sentence?*
   → "A CLI todo app with local storage"

Claude generates a minimal `.devpace/`:

```
.devpace/
├── state.md          # "Goal: A CLI todo app, no work in progress"
├── project.md        # Project name + description (feature tree grows automatically as you work)
├── backlog/          # Empty (tasks are created as you work)
└── rules/
    ├── workflow.md   # Standard task state machine
    └── checks.md     # "npm test" + "npm run lint" (auto-detected)
```

No business goals, no feature list, no iteration plan. Just a skeleton — everything else grows automatically as you work.

> **Want the full setup?** Use `/pace-init my-todo-app full` for a guided 6-step configuration (goals, features, iterations, quality checks).

## Phase 2: Daily Development

### Session 1 — Start Coding

**You**: "Help me implement the task add command"

Claude automatically enters **Advance mode**:
- Creates `CR-001` (you won't see this ID)
- Writes code, runs tests
- Gate 1 passes (lint + tests)
- Gate 2 passes (integration checks)
- Advances to pending review

**Claude**: "The task add command is ready for review. Supports `todo add 'Buy milk' --priority high`. Want to review?"

**You**: `/pace-review`

Claude shows a summary:
> **Changed files**: `src/commands/add.ts`, `src/storage.ts`
> **Reason**: Implement task creation with priority support
> **Tests**: 5 new tests, all passing

**You**: "Looks good, approve"

Claude merges the task. The feature tree updates:

```
MVP
├── [✅] Task CRUD
│   ├── [✅] Add command
│   ├── [ ] List command
│   └── [ ] Delete command
├── [ ] Priority levels
└── [ ] Local file storage
```

This is your first merged task, so devpace shows a brief recap:

> What devpace did during this change: auto-tracked task lineage → quality checks → waited for your approval → updated all related state after merge.
> Next time requirements change, devpace will analyze impact before adjusting — no cascading chaos.
> If a session gets interrupted, devpace auto-restores context on restart — zero re-explanation needed.

## Phase 3: Requirements Change

After the first task is merged, priorities shift.

**You**: "We need to add due dates first, before list and delete. Put priority levels on hold."

Claude detects two changes and runs impact analysis:

> **Change 1: Insert "Due dates"**
> - New feature under Task CRUD
> - Impact: storage format (needs a migration field)
> - Capacity: fits within the current iteration
>
> **Change 2: Pause "Priority levels"**
> - Feature marked ⏸️
> - No in-progress tasks affected
> - Work is preserved, can resume anytime
>
> Proceed with both changes?

**You**: "Yes"

Claude updates everything in one shot:
- `project.md` — feature tree gets ⏸️ marker and new feature
- `state.md` — next steps updated
- `iterations/current.md` — plan reordered

Updated feature tree:

```
MVP
├── [✅] Task CRUD
│   ├── [✅] Add command
│   ├── [ ] List command
│   ├── [ ] Delete command
│   └── [ ] Due dates         ← new
├── [⏸️] Priority levels      ← paused
└── [ ] Local file storage
```

After processing the changes, Claude automatically assesses test impact:

> Due dates involve a storage format change → affects Task CRUD module (direct) + Local Storage (indirect)
> Recommended re-runs: add command tests (required) + storage module tests (recommended)

During subsequent development, Claude uses this impact analysis to determine regression test scope, ensuring the changes don't break existing functionality.

## Phase 4: Continue & Resume

### Session 2 — Seamless Resume

*Next day, new Claude session.*

**Claude** (automatic): "Yesterday we merged the add command and adjusted the plan (added due dates, paused priority levels). Due dates is next. Continue?"

No re-explanation needed. Claude read `state.md` and knows exactly where things stand.

**You**: "Yes, continue"

Claude creates CR-002 and starts implementing due dates. Writes code, runs tests, Gate 1/2 pass. Before requesting review, Claude runs acceptance verification:

> **Acceptance verification results**:
> ✅ User can set a due date on a task — `src/commands/add.ts:45` new `--due` parameter
> ✅ Overdue tasks are highlighted in the list — `src/display.ts:23` rendering logic implemented
> ⚠️ Due dates support relative dates (e.g. "tomorrow") — only absolute dates supported, needs follow-up

**Claude**: "Due dates feature is ready for review. Acceptance verification found 1 item to address — relative dates currently only support absolute format. Want to complete that first or review as-is?"

**You**: "Review as-is, we'll do relative dates next round"

After approval, work continues on list and delete commands.

## Phase 5: Retrospective

After all features are done:

**You**: `/pace-retro`

Claude generates a retrospective report:

> **Delivery**: 5 of 6 planned features completed (1 paused as planned)
> **Quality**: Gate 1 pass rate 100%, 1 Gate 2 failure caught and fixed
> **Changes**: 1 insert + 1 pause, both handled in the same session
> **Cycle time**: Average task from creation to merge: under 1 session

## Key Takeaways

| What happened | How devpace handled it |
|--------------|----------------------|
| Project start | `/pace-init` guides setup, no forms to fill |
| Writing code | Auto-creates tasks, quality gates, status tracking |
| Session interrupted | Zero re-explanation on resume |
| Requirements changed | Impact analysis → confirmation → atomic update of all files |
| Feature paused | Work preserved with ⏸️, resume anytime |
| Iteration ends | Data-driven retrospective based on actual task history |

The user never typed a task ID, never edited a state file, never learned any BizDevOps jargon. devpace manages the rhythm; developers just write code.
