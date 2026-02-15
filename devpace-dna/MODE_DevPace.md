# DevPace Mode

> **本文件定位**：供人类阅读的完整行为参考文档，不面向 Claude Code。
> Claude Code 的行为规程见 `knowledge/_templates/claude-md-devpace.md`（由 `/pace-init` 植入目标项目 CLAUDE.md）
> 和 `rules/devpace-rules.md`（插件加载时自动注入）。

**Purpose**: Structured human-AI collaborative development workflow with value tracing, quality gates, and orderly change management.

## Activation Triggers
- `.devpace/state.md` detected in project root (auto-activate on session start)
- `--devpace` or `--pace` flag
- User invokes any `/pace-*` skill
- Sustained product development context detected (business goals, iteration planning, feature backlogs)

## Progressive Loading

| Level | Condition | What's Loaded | Token Cost |
|-------|-----------|---------------|------------|
| 0 — Mindset | No `.devpace/` | PRINCIPLES_COLLAB only | ~700 |
| 1 — Awareness | `state.md` exists | + state.md snapshot (≤15 lines) | +200 |
| 2 — Advancing | `/pace-advance` or code changes | + active CR file + workflow rules + checks | +500 on demand |
| 3 — Panorama | `/pace-status tree` or `/pace-change` | + project.md full value tracing tree | +800 on demand |

**Rule**: Never load more than the current operation needs. Follow devpace's own information layering principle.

## Behavioral Changes

### Session Start Protocol
1. Check project root for `.devpace/state.md`
2. If exists → read it, report current status in **1 natural language sentence**, then wait for instructions
3. If not exists → work normally with PRINCIPLES_COLLAB guiding thinking, no process enforcement
4. Never start work unprompted — wait for user

### Dual-Mode Operation

**Explore Mode (default)**:
- Freely read, analyze, explain any file
- Do NOT modify `.devpace/` state files
- Not bound by state machine or quality gates
- Trigger words: "看看", "分析", "评估", "了解", "look at", "analyze", "evaluate"

**Advance Mode (when modifying code)**:
- Enters when user says "开始做", "帮我改", "实现", "修复" or invokes `/pace-advance`
- Binds to a Change Request (existing or auto-created)
- Follows workflow state machine: created → developing → verifying → in_review → approved → merged
- After each atomic step: git commit + update CR + update state.md
- Quality check failure → self-fix, do NOT ask user
- Human review gate → generate summary, STOP and wait

**Ambiguity**: Ask "要正式开始改代码，还是先看看？"

### Quality Gates
- **Auto-gates** (developing → verifying, verifying → in_review): Claude self-executes, self-heals on failure
- **Human review gate** (in_review → approved): Claude generates summary and **stops**, waits for human decision
- Gates are idempotent — re-running is safe with no side effects

### Change Management
When requirement change intent is detected ("不做了", "加一个", "改一下", "先做这个"):
1. **Impact analysis**: Read value tracing tree, identify affected features and changes
2. **Propose plan**: Present adjustment options with natural language impact description
3. **Wait for confirmation**: Never execute changes unilaterally
4. **Execute and record**: Update all state files, record change event

### Output Discipline

| Context | Volume | Example |
|---------|--------|---------|
| Step completion | 1 sentence | "标注完成，框架覆盖 75%。" |
| Session end | 3-5 lines | What was done + quality status + next step |
| User asks details | Expand as needed | Quality check list, progress percentage |
| `/pace-status` | Tiered by argument | default: 1 line, detail: full, tree: panorama |

### Checkpoint & Recovery
- Every atomic step is checkpointed: git commit + CR update + state.md update
- Atomic step granularity: one meaningful work result (e.g., file created, one gate passed)
- Next session resumes from state.md "next step" field
- Quality checks are idempotent — just re-run

## Integration with SuperClaude

| SuperClaude Mode | How DevPace Integrates |
|-----------------|----------------------|
| **Task Management** | devpace CRs map to task hierarchy; state.md informs TodoWrite |
| **Orchestration** | devpace context informs tool selection priority |
| **Introspection** | devpace metrics (gate pass rate, review rejections) feed self-reflection |
| **Token Efficiency** | devpace info layering aligns with --uc compression strategy |
| **Brainstorming** | Pre-devpace phase — requirements discovery feeds into /pace-init |

## Three Feedback Loops (Conceptual Foundation)

```
Business Loop (👤 Human-led, quarterly/topic level)
  │  Define business objectives + MoS
  │  Claude assists analysis, does NOT make business decisions
  ▼
Product Loop (👤🤖 Human-AI collaboration, iteration level)
  │  Decompose BR into PF, schedule, track progress
  │  Claude assists decomposition and suggests scheduling
  ▼
Technical Loop (🤖 Claude autonomous, per-change level)
  │  CR state machine: created → developing → verifying → in_review
  │  Claude self-codes, self-tests, self-fixes gate failures
  │  Stops at human review gate
  ▼
Feedback flows upward: delivery metrics → product adjustments → business learning
```
