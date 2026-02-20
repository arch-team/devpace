# devpace

**Development pace manager for Claude Code** — bring structured BizDevOps rhythm to AI-assisted development.

devpace connects business goals to code changes through a traceable value chain (Business Goal -> Product Feature -> Change Request). Session interrupted? Context auto-restores. Requirements changed? Impact analysis runs instantly. Quality slipping? Built-in gates catch it before it flows downstream.

> Requirements always change. The development rhythm shouldn't break because of it.

## The Problem

When using Claude Code for product development across multiple sessions:

| Pain Point | What Happens |
|------------|-------------|
| **Context lost between sessions** | Every new session starts with "let me re-explain what we're building..." |
| **Quality inconsistency** | Claude sometimes skips tests, forgets checks, rushes through validation |
| **Code disconnected from goals** | Technical work drifts from business objectives over time |
| **Requirement changes cause chaos** | A simple "let's add X" creates cascade confusion across files |

## How devpace Solves It

| With devpace | How |
|-------------|-----|
| **Zero re-explanation** | `state.md` auto-restored at session start |
| **Quality gates enforced** | Gate 1/2 auto-check before state transitions; Gate 3 = human review |
| **Always traceable** | Business Goal -> Feature -> Change Request -> Code |
| **Ordered change management** | Impact analysis + adjustment plan + confirmation before execution |

**Measured improvement**: In a real project comparison across 3 session interruptions, devpace required **0 user corrections** to resume context vs **8 corrections** with a manually maintained CLAUDE.md approach (7 recovery dimensions analyzed).

## Install

```bash
# Load as Claude Code plugin (local development)
claude --plugin-dir /path/to/devpace
```

## Quickstart

### 1. Initialize your project

In your project directory with the devpace plugin loaded:

```
/pace-init my-project
```

Claude asks about your business goals, success metrics, and initial features, then generates:

```
.devpace/
├── state.md          # Session state (5-8 lines, auto-maintained)
├── project.md        # Value-feature tree + business goals
├── backlog/          # Change requests (auto-created as you work)
├── iterations/       # Iteration tracking (populated when needed)
├── rules/            # Project-specific quality rules
└── metrics/          # Measurement dashboard
```

### 2. Start working

```
Help me implement user authentication
```

Claude automatically enters **advance mode**: creates a Change Request, codes, tests, and runs quality gates. Every meaningful step is checkpointed via git commit + state update.

### 3. Review and approve

When code reaches review state, Claude generates a summary and **stops**:

```
/pace-review
```

You approve or reject with feedback. Approved changes auto-merge and the feature tree updates.

### 4. Handle changes

```
Actually, let's pause auth and add an export feature first
```

Claude detects the change intent, runs impact analysis, shows what's affected, proposes a plan, and **waits for your confirmation** before executing.

### 5. Resume next session

Start a new Claude session. devpace reads `state.md` and reports:

> "Last time we paused authentication. Export feature is in development. Continue?"

No re-explanation needed.

## Commands

| Command | When to Use | Detail Levels |
|---------|-------------|---------------|
| `/pace-init [name]` | First time project setup | Interactive guided setup |
| `/pace-advance [feature]` | Start or continue coding | Auto-selects next task if no argument |
| `/pace-status [level]` | Check progress | `(default)` 1-3 lines, `detail` PF-level, `tree` full feature tree |
| `/pace-review [keyword]` | Code ready for human review | Generates change summary for approval |
| `/pace-change [type] [desc]` | Requirements changed | `add`, `pause`, `resume`, `reprioritize`, `modify` |
| `/pace-retro [update]` | End of iteration | Generates retrospective report + metrics |
| `/pace-guide [topic]` | Understand the methodology | `model`, `objects`, `rules`, `trace`, `metrics`, `all` |

## How It Works

### Two Modes

- **Explore mode** (default): Freely read, analyze, and discuss. No state files touched.
- **Advance mode** (when coding): Bound to a Change Request. State machine enforced. Quality gates active.

Claude asks when uncertain: *"Start coding, or just exploring?"*

### CR State Machine

```
created -> developing -> verifying -> in_review -> approved -> merged
              |               |            ^
              |               |            |
              +-- Gate 1 -----+-- Gate 2 --+-- Gate 3 (human)
              (code quality)  (integration)  (code review)

Any state <-> paused  (preserves all work, change management)
```

- **Gate 1/2**: Claude auto-executes, auto-fixes failures, no user interruption
- **Gate 3**: Human code review — Claude stops and waits

### Value Chain

```
Business Goal (OBJ) -> Business Requirement (BR) -> Product Feature (PF) -> Change Request (CR)
     human-defined         human-defined             human+AI collaborate      Claude creates
```

The conceptual model exists from day one. Content starts minimal and enriches naturally as iterations progress — you never need to fill out forms upfront.

### Change Management (Core Differentiator)

devpace treats requirement changes as **first-class citizens**, not exceptions:

| Change Type | What Happens |
|-------------|-------------|
| **Insert** new requirement | Creates PF + CR, evaluates capacity, suggests scheduling |
| **Pause** a feature | CR -> paused (preserves all work), feature tree marked ⏸️ |
| **Resume** paused work | Restores to pre-pause state, re-validates quality checks if code changed |
| **Reprioritize** | Reorders work queue, updates state.md and iteration plan |
| **Modify** existing requirement | Updates CR scope, resets affected quality checks |

All changes follow: **Impact Analysis -> Adjustment Plan -> User Confirmation -> Execute + Record**.

## Design Principles

| # | Principle | What It Means |
|---|-----------|---------------|
| P1 | Zero friction | Natural language only — no BizDevOps jargon required |
| P2 | Progressive disclosure | Default output is 1 line; drill down on demand |
| P3 | Byproducts, not prerequisites | Structured data is automatic output of working, not upfront input |
| P4 | Fault tolerance | Interrupt at any point, resume seamlessly next session |
| P5 | Free exploration | Default is free mode; process kicks in only when advancing |
| P6 | Tiered output | Concise by default, expandable by request |
| P7 | Git as source | CR records branch name only; commit details via `git log` |

## Project Status

**v0.1.0 — Community Release** (Phase 4 complete)

- 7 Skills fully implemented
- 3 Schema contracts (CR, Project, State)
- 225-line runtime rules
- 87 static test cases passing (9 test modules)
- 16 verification items passed across 2 projects (Python + TypeScript/NestJS)
- Validated: initialization, full CR lifecycle (incl. reject/fix loop), cross-session recovery (0 corrections in 3 interruptions), change management (insert/pause/reprioritize), quality gate enforcement (Gate 1/2 blocking + Hook advisory), progressive enrichment (0 manual edits across 8 commits)

## Documentation

- [User Guide](docs/user-guide.md) — Complete reference for all commands and concepts
- [Example Walkthrough](examples/todo-app-walkthrough.md) — End-to-end demo from init to merged
- [Contributing](CONTRIBUTING.md) — Development setup, testing, and PR guidelines
- [Changelog](CHANGELOG.md) — Version history

## License

MIT
