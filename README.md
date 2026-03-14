🌐 [中文版](README_zh.md) | English

# devpace

Give your Claude Code projects a steady development pace — requirements change, rhythm stays.

> A development harness for Claude Code — rules, schemas, gates, and feedback loops that keep AI-assisted development traceable and measurable.

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

## Full Development Lifecycle

```
Opportunity ──→ Epic ──→ Requirements ──→ Features ──→ Code Changes ──→ Quality ──→ Ship
        │          │           │              │              │              │           │
     pace-biz   pace-biz   pace-biz       pace-plan      pace-dev     pace-review  pace-release
                                          pace-change                              pace-feedback
```

Requirements can change anytime — `/pace-change` auto-analyzes impact, adjusts the plan, and waits for your confirmation.

After each cycle, `/pace-retro` shows quality metrics and improvement trends.

## How It Works

devpace builds a **goal-to-code traceability chain** in your project:

1. **Goal alignment** — Every code change links back to a business goal. No work without purpose.
2. **Auto quality gates** — Claude auto-checks code quality and requirement consistency, self-repairs on failure. Human approval cannot be skipped.
3. **Change is normal** — Requirements changed? Auto impact analysis, orderly adjustment, existing work preserved.
4. **Interrupt-proof** — Session broke? Auto-resume next time. All state in `.devpace/` as plain Markdown.

Under the hood: a Claude Code Plugin using Rules (behavioral guidelines) + Skills (`/pace-*` commands) + Hooks (auto-triggers at critical moments).

## Installation

> **Prerequisite**: [Claude Code CLI](https://claude.ai/code) must be installed.

### Marketplace Install (Recommended)

```bash
# Step 1: Register marketplace (one-time)
/plugin marketplace add arch-team/devpace-marketplace

# Step 2: Install
/plugin install devpace@devpace
```

### From Source

```bash
git clone https://github.com/arch-team/devpace.git
claude --plugin-dir /path/to/devpace
```

### Verify Installation

After installing, type `/pace-` in Claude Code. If devpace is loaded, you'll see auto-complete suggestions for `/pace-init`, `/pace-dev`, `/pace-status`, etc.

## Commands

Most of the time you don't need commands — saying "help me implement X" equals `/pace-dev`, "where are we" equals `/pace-status`.

### Start Here (5 commands cover 90% of daily work)

| Command | Purpose |
|---------|---------|
| `/pace-init` | First-time setup (once) |
| `/pace-dev` | Start coding — or just say "help me implement X" |
| `/pace-status` | Check progress — or say "where are we" |
| `/pace-review` | Approve changes |
| `/pace-next` | Not sure what's next? Get AI recommendations |

### More Commands

As your project grows, devpace offers change management, iteration planning, business alignment, release orchestration, and more. See [User Guide](docs/user-guide.md) for all 19 commands.

Quick reference: `/pace-change` (requirements changed) · `/pace-plan` (plan iterations) · `/pace-retro` (review metrics) · `/pace-biz` (business planning) · `/pace-release` (ship it)

## Core Capabilities

### Change Management (Core Differentiator)

| Capability | Description |
|-----------|-------------|
| Requirement changes | Add features, pause, change scope — auto impact analysis, orderly adjustment, Claude won't change the plan unilaterally |
| Complexity awareness | Auto-assesses task complexity, small changes fast-track, large changes full process, complexity drift auto-detected |
| Technical debt management | `tech-debt` CR type + iteration capacity reservation + trend tracking |
| Architecture decisions | `/pace-trace arch` manages cross-CR Architecture Decision Records (ADR) |

### Quality & Traceability

| Capability | Description |
|-----------|-------------|
| Quality gates | Code quality + requirement consistency auto-check + adversarial review, human approval cannot be skipped |
| Goal traceability | From business goals to code changes, always traceable |
| Test verification | Requirements-driven — strategy generation, coverage analysis, AI acceptance verification, change impact regression |
| Semantic drift detection | Continuous monitoring of code-requirement alignment during development, Review includes semantic consistency score |

### Development Rhythm

| Capability | Description |
|-----------|-------------|
| Cross-session restore | Session interrupted? Auto-resume, zero re-explanation, experience persists across sessions |
| Iteration management | Plan → Execute → Review full cycle, auto-recommends next step |
| Progressive autonomy | Assisted / Standard / Autonomous — more guidance for new users, less for experienced ones |
| DORA proxy metrics | Deploy frequency / Lead time / Failure rate / MTTR proxy values, Elite~Low benchmarks + trend comparison |
| CI/CD awareness | Auto-detects CI tool type, Gate 4 auto-queries CI status, zero config |
| Risk fabric | OWASP-aware security scanning + Pre-flight 5-dimension risk scan + Runtime monitoring + Graduated autonomous response (High requires human confirmation) |
| Delivery prediction | AI-powered iteration delivery probability forecasting, bottleneck identification, and risk early warning |
| Cross-project insights | High-confidence insights exportable/importable to other projects, reducing redundant learning |

## Workflow

### Two Modes

- **Explore mode** (default): Freely read code, analyze problems, discuss approaches. No process triggered.
- **Advance mode** (when changing code): Auto-creates tasks, tracks progress, checks quality. Small changes fast-track, large changes full process.

When unsure, Claude asks: "Ready to start coding, or just exploring?"

### Workflow

```
Normal flow:
Start ──→ In Progress ──→ Pending Review ──→ Done
              │                │
        Auto quality check  You approve      Auto merge + status update
        (Claude handles)   (you decide)

Anytime:
  Requirements changed ──→ Impact analysis ──→ Adjust plan ──→ Continue
  Session interrupted  ──→ Next session auto-resumes from where you left off

Full cycle (optional):
  Plan (pace-plan) → Build (pace-dev) → Review (pace-retro) → Next cycle
```

## Design Principles

| Principle | Meaning |
|-----------|---------|
| Zero friction | Natural language works, no jargon to learn |
| Progressive disclosure | Default 1-line output, details on demand |
| Byproducts not prerequisites | Structured data is auto-produced from work, not a required input |
| Interruption tolerance | Interrupt at any point, seamless resume next time |

## vs Alternatives

| Dimension | GitHub Issues / Manual | devpace |
|-----------|----------------------|---------|
| Core model | Task list | Goal → Feature → Code Change traceability |
| Requirement changes | Manual impact assessment | Auto impact analysis + orderly adjustment |
| Claude's role | Executor (you direct each step) | Autonomous collaborator (auto-advances, self-checks, waits for your decisions) |
| Traceability | Task → Code | Business Goal → Feature → Change → Code |
| Metrics | Completion count | Quality pass rate + value alignment + DORA proxies |

## What devpace is NOT

- **Not a CI/CD pipeline** — it works alongside your existing tools (GitHub Actions, Jenkins, etc.)
- **Not a project management platform** — no web dashboard, no team features, pure CLI
- **Not a replacement for git** — it creates Markdown state files in `.devpace/`, your code stays in git

## Feedback

Tried devpace? [Tell us what you think](https://github.com/arch-team/devpace/issues/3) — one word or a full report, everything helps.

## Learn More

- [User Guide](docs/user-guide.md) — Full command reference, modes, state machine details ([中文](docs/user-guide_zh.md))
- [Walkthrough](examples/todo-app-walkthrough.md) — Complete example from init to finish ([中文](examples/todo-app-walkthrough_zh.md))
- [Contributing](CONTRIBUTING.md) — Dev environment, testing, PR process
- [Changelog](CHANGELOG.md) — Version history ([English summaries on GitHub Releases](https://github.com/arch-team/devpace/releases))
- [Troubleshooting](https://github.com/arch-team/devpace/issues?q=label%3Abug) — Search known issues or open a new one

---
MIT
