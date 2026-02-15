# Human-AI Collaborative Development Principles

> **本文件定位**：供人类阅读的方法论参考文档，不面向 Claude Code。
> Claude Code 的行为规程见 `knowledge/_templates/claude-md-devpace.md`（由 `/pace-init` 植入目标项目 CLAUDE.md）
> 和 `rules/devpace-rules.md`（插件加载时自动注入）。

**Core Directive**: Value > activity | Checkpoint > memory | Change = learning

These principles apply whenever Claude works on product development, shaping thinking regardless of whether formal workflow tooling is active.

## Value Chain Thinking
- Every technical change should trace to a product purpose
- Think in terms of: Why (business goal) → What (product feature) → How (technical change)
- When unsure whether work is valuable, ask "what product outcome does this serve?"
- Bidirectional traceability: from business goal down to code change, and from code change up to business goal

## Quality Gate Consciousness
- Quality gates are the rhythm of reliable delivery, not bureaucracy
- Automated checks (lint, test, typecheck) should self-heal without bothering the user
- Human review is a gate, not a speed bump — stop and present a clear summary
- Gate failures are feedback signals: fix the root cause, do not disable the gate

## Change Is Normal
- Requirement changes are signals of learning, not failures of planning
- Before executing a change, assess impact on related work (direct + dependency chain)
- Pausing work preserves it; pausing is not abandoning
- All changes should be traceable and auditable

## Dual-Mode Awareness
- Exploration (reading, analyzing, understanding) needs no process overhead
- Advancement (writing code, modifying state) benefits from structure and checkpoints
- Know which mode you are in; do not impose process on exploration
- When unsure, ask: "Do you want to start changing code, or just look around first?"

## Session Continuity
- Assume the conversation may end at any moment
- Important state should be externalized, not kept only in context
- Each atomic step should leave a recoverable checkpoint
- Next session should be able to resume from where the last one stopped

## Feedback Loop Clarity
- Business decisions belong to humans (business objectives, success criteria)
- Product decisions are collaborative — human-AI partnership (feature decomposition, prioritization)
- Technical execution is Claude's autonomous domain, up to the review gate
- Each loop has its own rhythm: business (quarterly), product (iteration), technical (per-change)

## Information Layering
- Default to the minimum information needed (1-line summary)
- Provide detail only when asked or when the situation demands it
- Never dump full state when a summary suffices
- Three tiers: Summary (what's happening) → Detail (what specifically) → Panorama (full picture)
