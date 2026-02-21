# Changelog

All notable changes to devpace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-02-20

First public release. Full BizDevOps development pace management for Claude Code.

### Added

- **8 Slash Commands**: `/pace-init`, `/pace-dev`, `/pace-plan`, `/pace-status`, `/pace-review`, `/pace-change`, `/pace-retro`, `/pace-theory`
- **Value chain model**: Business Goal (OBJ) → Business Requirement (BR) → Product Feature (PF) → Change Request (CR)
- **CR state machine**: `created → developing → verifying → in_review → approved → merged` with `paused` transitions
- **Quality gates**: Gate 1 (code quality), Gate 2 (integration), Gate 3 (human review)
- **Change management**: 5 change types — insert, pause, resume, reprioritize, modify — with impact analysis and confirmation workflow
- **Cross-session continuity**: Auto-restore via `state.md` with zero user re-explanation
- **Two operating modes**: Explore (default, read-only) and Advance (code changes, CR-bound)
- **PreToolUse Hook**: Advisory quality gate reminders for CR state transitions
- **Session lifecycle hooks**: Auto-load state at session start, save reminder at session stop
- **3 schema contracts**: CR format, project format, state format (`knowledge/_schema/`)
- **8 project templates**: Bootstrapped by `/pace-init` into `.devpace/` directory
- **Runtime rules**: 225-line behavior protocol (`rules/devpace-rules.md`)
- **Metrics definitions**: Quality, delivery, and value alignment metrics (`knowledge/metrics.md`)
- **BizDevOps theory reference**: Methodology guide accessible via `/pace-theory`

### Verified

- 2 real projects validated (Python/diagnostic-agent-framework + TypeScript/NestJS simulation)
- 16 verification items passed across existing and new project scenarios
- 87 static test cases passing (9 test modules)
- Cross-session recovery: 0 user corrections needed across 3 interruptions (vs 8 with manual approach)
- Progressive enrichment: 0 manual edits to state files across 8 commits
- State scalability: 15 lines at 12 CRs (O(1) growth confirmed)
