<!-- Generated: 2026-02-18 | Files scanned: 68 | Token estimate: ~400 -->

# Knowledge — devpace Plugin

## Schema Contracts (knowledge/_schema/)

| Schema | Lines | Defines | Consumed By |
|--------|-------|---------|-------------|
| cr-format.md | 82 | CR file fields, states, transitions | pace-advance, pace-change, pace-review |
| project-format.md | 72 | BR→PF mapping, project metadata | pace-init, pace-status |
| state-format.md | 40 | Session state fields, ≤15 lines target | pace-init, pace-advance, pace-status |

## Runtime Knowledge

| File | Lines | Purpose | Consumed By |
|------|-------|---------|-------------|
| theory.md | 407 | BizDevOps methodology reference | pace-guide (runtime data source) |
| metrics.md | 25 | Metric definitions, calculations | pace-retro, pace-status |

## Schema → Template Alignment

```
state-format.md   → templates/state.md
project-format.md → templates/project.md
cr-format.md      → templates/cr.md
(no schema)       → templates/workflow.md, checks.md, iteration.md, dashboard.md
```

## Rules (Product Layer)

```
rules/devpace-rules.md (215 lines)
  §0 速查卡片 — Quick reference card
  §1 会话开始 — Session start behavior
  §2 推进模式 — Advance mode (CR-bound)
  §3 意图检查点 — Intent checkpoints (adaptive complexity)
  §4 质量检查 — Quality gates (auto-fix, human_review block)
  §5 merged 连锁 — Post-merge cascade
  §6 会话结束 — Session end protocol
  §7 探索模式 — Explore mode (default, no state mutation)
  §8 文件权限 — File permissions
  §9 变更管理 — Change management (4 scenarios)
```
