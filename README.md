🌐 [中文版](README_zh.md) | English

# devpace

Give your Claude Code projects a steady development pace — requirements change, rhythm stays.

![version](https://img.shields.io/github/v/release/arch-team/devpace?label=version) ![license](https://img.shields.io/badge/license-MIT-green) ![type](https://img.shields.io/badge/Claude%20Code-Plugin-purple)

## Why devpace

When using Claude Code for product development:

| Problem | Without devpace | With devpace |
|---------|----------------|-------------|
| Requirements change = chaos | "Add a feature" triggers cascading confusion, nobody knows the blast radius | Impact analysis + orderly adjustment, Claude won't change the plan on its own |
| Inconsistent quality | Claude sometimes skips tests, forgets checks | Auto-checks + human approval, quality gates cannot be bypassed |
| Work drifts from goals | Technical work disconnects from business goals, lots done but unclear value | Goal-to-code traceability at all times |
| Re-explain everything each session | Manual approach needs **8** user corrections (3 interruption test) | Auto-restores context, **0** corrections |

> [See full walkthrough: from init to done](examples/todo-app-walkthrough.md)

## 30-Second Experience

```
/pace-init                 ← Initialize (once)
"Help me implement user auth" ← Claude auto-tracks tasks, writes code, runs tests, checks quality
"approve" or "reject"      ← You decide whether to merge
"add an export feature"    ← Claude analyzes impact, adjusts plan, waits for your confirmation
"pause auth for now"       ← Impact analysis → pause (preserving work) → adjust plan
```

Next session, Claude reports: "Last time we stopped at auth module, continue?" — zero manual re-explanation.

## How It Works

devpace is a Claude Code Plugin that extends Claude's capabilities through three mechanisms:

- **Rules**: Define Claude's behavioral guidelines — when to auto-check quality, how to trace goals
- **Skills**: `/pace-*` command series, triggering specific workflows
- **Hooks**: Auto-trigger at critical moments — check quality before writing code, restore context on session start

All state is stored in `.devpace/` folder at project root, pure Markdown, human-readable.

## Installation

> **Prerequisite**: [Claude Code CLI](https://claude.ai/code) must be installed.

### From Source (Recommended)

```bash
git clone https://github.com/arch-team/devpace.git
claude --plugin-dir /path/to/devpace
```

### Plugin Registry

```bash
/plugin install devpace
```

> If `/plugin install` is not available yet, use the "From Source" method above.

### Verify Installation

After installing, type `/pace-` in Claude Code. If devpace is loaded, you'll see auto-complete suggestions for `/pace-init`, `/pace-dev`, `/pace-status`, etc.

## Commands

### Daily Use

| Command | Purpose |
|---------|---------|
| `/pace-init` | First-time setup (once, supports `--from PRD` for auto feature tree) |
| `/pace-dev` | Start coding |
| `/pace-status` | Check progress |
| `/pace-review` | Approve changes |
| `/pace-next` | Not sure what's next? Get AI recommendations |

### When Requirements Change or a Cycle Completes

| Command | When to use |
|---------|------------|
| `/pace-change` | Add requirements, pause, change scope, reprioritize |
| `/pace-plan` | Cycle done, plan the next one |
| `/pace-retro` | Review how things went |

### Specialized Features (Optional)

| Command | Scenario |
|---------|----------|
| `/pace-test` | Requirements-traceable test management |
| `/pace-guard` | Risk fabric: Pre-flight scan + Runtime monitoring + Trend analysis + Graduated response |
| `/pace-release` | Release orchestration: Changelog + Version bump + Git Tag + GitHub Release |
| `/pace-role` | Switch perspective (PM / Tester / Ops / etc.) |
| `/pace-theory` | Learn the methodology behind devpace |
| `/pace-feedback` | Collect post-launch feedback |
| `/pace-trace` | View full reasoning trace of AI decisions |

Most of the time you don't need commands — saying "help me implement X" equals `/pace-dev`, "where are we" equals `/pace-status`.

## Core Capabilities

### Change Management (Core Differentiator)

| Capability | Description |
|-----------|-------------|
| Requirement changes | Add features, pause, change scope — auto impact analysis, orderly adjustment, Claude won't change the plan unilaterally |
| Complexity awareness | Auto-assesses task complexity, small changes fast-track, large changes full process, complexity drift auto-detected |

### Quality & Traceability

| Capability | Description |
|-----------|-------------|
| Quality gates | Code quality + requirement consistency auto-check + adversarial review, human approval cannot be skipped |
| Goal traceability | From business goals to code changes, always traceable |
| Test verification | Requirements-driven — strategy generation, coverage analysis, AI acceptance verification, change impact regression |

### Development Rhythm

| Capability | Description |
|-----------|-------------|
| Cross-session restore | Session interrupted? Auto-resume, zero re-explanation, experience persists across sessions |
| Iteration management | Plan → Execute → Review full cycle, auto-recommends next step |
| Progressive autonomy | Assisted / Standard / Autonomous — more guidance for new users, less for experienced ones |
| DORA proxy metrics | Deploy frequency / Lead time / Failure rate / MTTR proxy values, Elite~Low benchmarks + trend comparison |
| CI/CD awareness | Auto-detects CI tool type, Gate 4 auto-queries CI status, zero config |
| Risk fabric | Pre-flight 5-dimension risk scan + Runtime monitoring + Graduated autonomous response (High requires human confirmation) |
| Cross-project insights | High-confidence insights exportable/importable to other projects, reducing redundant learning |

## Workflow

### Two Modes

- **Explore mode** (default): Freely read code, analyze problems, discuss approaches. No process triggered.
- **Advance mode** (when changing code): Auto-creates tasks, tracks progress, checks quality. Small changes fast-track, large changes full process.

When unsure, Claude asks: "Ready to start coding, or just exploring?"

### Workflow

```
Start ──→ In Progress ──→ Pending Review ──→ Done
              │                │
        Auto quality check  You approve      Auto merge
        (Claude handles)   (you decide)    + status update

Pause anytime, resume from where you left off
```

## Design Principles

| Principle | Meaning |
|-----------|---------|
| Zero friction | Natural language works, no jargon to learn |
| Progressive disclosure | Default 1-line output, details on demand |
| Byproducts not prerequisites | Structured data is auto-produced from work, not a required input |
| Interruption tolerance | Interrupt at any point, seamless resume next time |

## What devpace is NOT

- **Not a CI/CD pipeline** — it works alongside your existing tools (GitHub Actions, Jenkins, etc.)
- **Not a project management platform** — no web dashboard, no team features, pure CLI
- **Not a replacement for git** — it creates Markdown state files in `.devpace/`, your code stays in git

## Learn More

- [User Guide](docs/user-guide.md) — Full command reference, modes, state machine details ([中文](docs/user-guide_zh.md))
- [Walkthrough](examples/todo-app-walkthrough.md) — Complete example from init to finish ([中文](examples/todo-app-walkthrough_zh.md))
- [Contributing](CONTRIBUTING.md) — Dev environment, testing, PR process
- [Changelog](CHANGELOG.md) — Version history ([English summaries on GitHub Releases](https://github.com/arch-team/devpace/releases))
- [Troubleshooting](https://github.com/arch-team/devpace/issues?q=label%3Abug) — Search known issues or open a new one

---
MIT
