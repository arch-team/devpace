# Example Walkthrough: Todo App with devpace

This walkthrough shows devpace managing a complete development cycle — from project initialization to a merged change request, including a mid-stream requirement change.

## Setup

```bash
# In your project directory with devpace plugin loaded
cd ~/projects/my-todo-app
claude --plugin-dir /path/to/devpace
```

## Phase 1: Initialize

**You**: `/pace-init my-todo-app`

**Claude** asks a series of questions:

1. *What's this project about?*
   → "A CLI todo app with local storage"

2. *What are your business goals for this phase?*
   → "Ship a working MVP that manages tasks with priorities"

3. *How do you measure success?*
   → "Users can add, list, complete, and delete tasks"

4. *What features to build first?*
   → "Task CRUD, priority levels, local file storage"

Claude generates `.devpace/`:

```
.devpace/
├── state.md          # "Phase: MVP | Next: implement task CRUD"
├── project.md        # Value tree: OBJ → BR → 3 PFs
├── backlog/          # Empty (CRs created as you work)
├── iterations/
│   └── current.md    # First iteration with 3 features planned
├── rules/
│   ├── workflow.md   # Standard CR state machine
│   └── checks.md     # "npm test" + "npm run lint"
└── metrics/
    └── dashboard.md  # Empty template
```

## Phase 2: Daily Work

### Session 1 — Start coding

**You**: "Let's implement the task add command"

Claude enters **advance mode** automatically:
- Creates `CR-001` (you never see this ID)
- Writes the code, runs tests
- Gate 1 passes (lint + test)
- Gate 2 passes (integration check)
- Advances to review state

**Claude**: "Task add command is ready for review. It supports `todo add 'Buy milk' --priority high`. Want to review?"

**You**: `/pace-review`

Claude shows a summary:
> **Changed**: `src/commands/add.ts`, `src/storage.ts`
> **Why**: Implements task creation with priority support
> **Tests**: 5 new tests, all passing

**You**: "Looks good, approve"

Claude merges the CR. Feature tree updates:

```
MVP
├── [✅] Task CRUD
│   ├── [✅] Add command
│   ├── [ ] List command
│   └── [ ] Delete command
├── [ ] Priority levels
└── [ ] Local file storage
```

### Session 2 — Resume seamlessly

*Next day, new Claude session.*

**Claude** (automatic): "Yesterday we merged the add command. List and delete commands are next. Continue with list?"

No re-explanation needed. Claude read `state.md` and knows exactly where things stand.

**You**: "Yes, continue"

Claude creates CR-002 for the list command, implements it, runs gates, requests review. Same flow.

## Phase 3: Requirement Change

Mid-sprint, priorities shift.

**You**: "Actually, we need to add due dates before finishing delete. And let's pause the priority levels feature for now."

Claude detects two changes and runs impact analysis:

> **Change 1: Insert "Due dates"**
> - New PF under Task CRUD
> - Affects: storage format (needs migration field)
> - Capacity: fits in current iteration
>
> **Change 2: Pause "Priority levels"**
> - PF marked ⏸️
> - No in-progress CRs affected
> - Work preserved, can resume later
>
> Proceed with both changes?

**You**: "Yes"

Claude updates everything in one shot:
- `project.md` — feature tree with ⏸️ marker and new PF
- `state.md` — updated next steps
- `iterations/current.md` — reordered plan

Updated feature tree:

```
MVP
├── [✅] Task CRUD
│   ├── [✅] Add command
│   ├── [✅] List command
│   ├── [ ] Delete command
│   └── [ ] Due dates         ← inserted
├── [⏸️] Priority levels      ← paused
└── [ ] Local file storage
```

## Phase 4: Review and Retro

After completing all features:

**You**: `/pace-retro`

Claude generates a retrospective:

> **Delivery**: 5/6 planned features shipped (1 paused by design)
> **Quality**: Gate 1 pass rate 100%, 1 Gate 2 failure caught and fixed
> **Changes**: 1 insert + 1 pause, all handled within same session
> **Cycle time**: Average CR from created to merged: < 1 session

## Key Takeaways

| What happened | devpace behavior |
|---------------|-----------------|
| Project started | `/pace-init` guided setup, no forms to fill |
| Code written | Automatic CR creation, quality gates, state tracking |
| Session interrupted | Zero re-explanation on resume |
| Requirement changed | Impact analysis → confirmation → all files updated atomically |
| Feature paused | Work preserved with ⏸️, resumable anytime |
| Sprint ended | Data-driven retrospective from actual CR history |

The user never typed a CR ID, never edited a state file, never learned BizDevOps terminology. devpace handled the rhythm; the developer just wrote code.
