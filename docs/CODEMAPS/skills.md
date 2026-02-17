<!-- Generated: 2026-02-18 | Files scanned: 68 | Token estimate: ~600 -->

# Skills — devpace Plugin

## Skill Inventory (7 skills)

| Skill | Lines | Procedure | Templates | Trigger Keywords |
|-------|-------|-----------|-----------|-----------------|
| pace-init | 66 | — | 8 files (261 lines) | 初始化研发管理, pace-init |
| pace-advance | 60 | advance-procedures.md (33) | — | 开始做, 继续, 推进 |
| pace-change | 72 | change-procedure.md (104) | — | 加需求, 不做了, 恢复, 优先级调整, 改需求 |
| pace-status | 51 | — | — | 进度怎样, 做到哪了 |
| pace-review | 66 | — | — | review, 审核 |
| pace-retro | 54 | — | — | 回顾, 复盘, 度量 |
| pace-guide | 54 | — | — | 理论, 概念, 为什么这样设计 |

## Skill → Tools Mapping

| Skill | Allowed Tools |
|-------|--------------|
| pace-init | AskUserQuestion, Write, Read, Glob, Bash |
| pace-advance | AskUserQuestion, Write, Read, Edit, Glob, Bash |
| pace-change | AskUserQuestion, Write, Read, Edit, Glob, Bash |
| pace-status | Read, Glob |
| pace-review | Read, Write, Edit, Glob, Bash |
| pace-retro | Read, Write, Edit, Glob |
| pace-guide | Read, Glob |

## Templates (pace-init/templates/)

| Template | Lines | Target | Purpose |
|----------|-------|--------|---------|
| state.md | 14 | .devpace/state.md | Session anchor, current status |
| project.md | 28 | .devpace/project.md | BR→PF mapping |
| cr.md | 21 | .devpace/cr/CR-NNN.md | Change request instance |
| workflow.md | 69 | .devpace/workflow.md | CR transitions + paused handling |
| checks.md | 23 | .devpace/checks.md | Quality gate checklist |
| iteration.md | 32 | .devpace/iteration.md | Iteration tracking + change log |
| dashboard.md | 19 | .devpace/dashboard.md | Metrics dashboard |
| claude-md-devpace.md | 55 | CLAUDE.md append | devpace section for project CLAUDE.md |

## Skill Split Pattern

SKILL.md = "what" (input/output/high-level steps)
*-procedures.md = "how" (detailed rules, >50 lines threshold)

Applied in: pace-advance, pace-change
Not needed: pace-init (templates serve this role), pace-status/review/retro/guide (under threshold)
