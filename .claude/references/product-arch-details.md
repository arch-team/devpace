# 产品层组件架构——详细映射表

> 按需加载。从 `product-architecture.md` §3 引用。

## §0 速查

| 章节 | 内容 | 何时查阅 |
|------|------|---------|
| §A | Skill-Agent 路由矩阵 | 创建/修改 Skill 的 fork/inline/model/Hook 配置 |
| §B | Hook 架构模式 | 创建/修改 Hook、理解事件映射 |
| §C | Agent 协作架构 | 创建/修改 Agent、理解决策边界 |
| §D | Skill→Schema 依赖矩阵 | 修改 Schema 前评估影响范围 |
| §E | 信号系统三方同步 | 修改信号定义时 |

## §A Skill-Agent 路由矩阵

| Skill | Agent (fork) | model | Skill 级 Hooks |
|-------|-------------|-------|----------------|
| pace-dev | pace-engineer | sonnet | PreToolUse: scope-check |
| pace-review | pace-engineer | opus | PreToolUse: scope-check |
| pace-test | pace-engineer | sonnet | — |
| pace-feedback | pace-engineer | — | — |
| pace-release | pace-engineer | — | — |
| pace-change | pace-pm | sonnet | — |
| pace-plan | pace-pm | sonnet | — |
| pace-biz | pace-pm | sonnet | PreToolUse: scope-check |
| pace-retro | pace-analyst | sonnet | — |
| pace-guard | pace-analyst | — | — |
| pace-init | _(inline)_ | — | PreToolUse: scope-check |
| pace-next | pace-analyst | haiku | — |
| pace-status | pace-analyst | haiku | — |
| pace-pulse | pace-analyst | haiku | — |
| pace-learn | _(inline)_ | — | — |
| pace-theory | _(inline)_ | — | — |
| pace-role | _(inline)_ | — | — |
| pace-trace | _(inline)_ | — | — |
| pace-sync | _(inline)_ | — | — |

**路由原则**：
- **fork**：需要写入 `.devpace/` 或执行复杂多步操作的 Skill——提供上下文隔离
- **inline**：查询型或轻量操作的 Skill——避免子 agent 开销
- **Agent 鲁棒性**：fork 不可用时静默回退到 inline（rules §13.5）

## §B Hook 架构模式

**全局 vs Skill 级 Hook**：

| 范围 | 配置位置 | 生效条件 |
|------|---------|---------|
| 全局 | `hooks/hooks.json` | 始终生效（匹配 matcher） |
| Skill 级 | SKILL.md `hooks` frontmatter | 仅该 Skill 激活时生效 |

Skill 级 Hook 位于 `hooks/skill/` 目录，命名规范：`pace-xxx-scope-check.mjs`。

**事件-Hook-行为映射表**：

| 事件 | Hook 脚本 | 行为 | 阻断? | 异步? |
|------|----------|------|-------|-------|
| SessionStart | session-start.sh | 加载 devpace 上下文，检测 `.devpace/` | 否 | 否 |
| PreToolUse (Write\|Edit) | pre-tool-use.mjs | 质量检查：路径合规、状态一致性 | 是 (exit 2) | 否 |
| PostToolUse (Write\|Edit) | post-cr-update.mjs | CR 更新后的连锁检查 | 否 | 是 |
| PostToolUse (Write\|Edit) | pulse-counter.mjs | 脉搏计数器（节奏检测） | 否 | 是 |
| PostToolUse (Write\|Edit) | sync-push.mjs | 外部同步推送检查 | 否 | 是 |
| PostToolUse (Write\|Edit) | post-schema-check.mjs | Schema 合规验证 | 否 | 是 |
| PostToolUseFailure (Write\|Edit) | post-tool-failure.mjs | 失败恢复检查 | 否 | 否 |
| UserPromptSubmit | intent-detect.mjs | 意图检测（探索/推进模式判断） | 否 | 是 |
| PreCompact | pre-compact.sh | 压缩前保存 devpace 状态 | 否 | 否 |
| Stop | session-stop.sh | 会话检查 | 否 | 否 |
| SessionEnd | session-end.sh | 最终状态保存 | 否 | 否 |
| SubagentStop | subagent-stop.mjs | 子 agent 状态检查 | 否 | 否 |

**Skill 级 Hook 映射**：

| Skill | 事件 | Hook 脚本 | 用途 |
|-------|------|----------|------|
| pace-dev | PreToolUse (Write\|Edit) | skill/pace-dev-scope-check.mjs | 开发范围守护 |
| pace-review | PreToolUse (Write\|Edit) | skill/pace-review-scope-check.mjs | 审核范围守护 |
| pace-init | PreToolUse (Write\|Edit) | skill/pace-init-scope-check.mjs | 初始化范围守护 |
| pace-biz | PreToolUse (Write\|Edit) | skill/pace-biz-scope-check.mjs | 业务分析范围守护 |

**Hook 通信协议**：

```
事件触发 → stdin JSON（含 tool_name, file_path 等上下文）
         → Hook 脚本解析 JSON + 读取 .devpace/ 状态文件
         → exit 0（放行）| exit 2（阻断 + stderr 提示）| 其他（非阻断错误）
         → stdout 反馈信息注入会话上下文
```

**关键约束**：Hook 脚本不解析 `rules/`、`skills/`、`knowledge/` 中的 Markdown 文件——所有状态感知通过 `.devpace/` 运行时文件和 stdin JSON 完成。

## §C Agent 协作架构

**三角色模型**：

| Agent | 职责域 | 核心能力 | 工具权限 |
|-------|--------|---------|---------|
| pace-engineer | 工程执行 | CR 实现、质量门、代码变更 | Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion |
| pace-pm | 产品规划 | 迭代规划、变更管理、业务对齐 | Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion |
| pace-analyst | 度量分析 | 指标收集、回顾分析、趋势报告 | Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion |

**决策边界矩阵**：

| 决策类型 | 决策者 | Agent 角色 |
|---------|--------|-----------|
| 代码实现方案 | pace-engineer | 执行 + 建议 |
| CR 状态转换 | pace-engineer | 执行（受 Gate 约束） |
| 迭代范围调整 | pace-pm | 建议（需用户确认） |
| 需求变更评估 | pace-pm | 分析 + 建议 |
| 度量报告生成 | pace-analyst | 执行 |
| 风险预警 | pace-analyst | 分析 + 提示 |
| Gate 3 审批 | **人类** | 不可代替（IR-2） |

**Memory 策略**：Agent 使用 `memory: project`（`.claude/agent-memory/<name>/`）持久化跨会话上下文。下次 fork 到同一 Agent 时自动加载。适用于：迭代上下文延续（pace-pm）、技术决策记忆（pace-engineer）、度量基线记忆（pace-analyst）。

## §D Skill→Schema 依赖矩阵

基于产品层文件的直接路径引用统计。`>` = 直接引用。权威 fan-in 数据见 `knowledge/_schema/README.md`。

| Skill | cr-format | project-format | checks-format | iteration-format | test-strategy | insights-format | 其他 Schema |
|-------|-----------|---------------|---------------|-----------------|--------------|----------------|-------------|
| pace-init | | > | > | | | | context-format, integrations-format |
| pace-dev | > | | | | > | | br-format, pf-format, risk-format, context-format |
| pace-review | > | | | | | | accept-report-contract |
| pace-test | > | | | | > | | test-baseline-format |
| pace-change | > | | | > | | | |
| pace-plan | | | | > | | | |
| pace-biz | | > | | | | | epic-format, opportunity-format, readiness-score, merge-strategy |
| pace-retro | | | | | | > | test-baseline-format |
| pace-guard | | | | | | | risk-format |
| pace-feedback | > | | | | | | |
| pace-release | | | | | | | release-format, integrations-format |
| pace-learn | | | | | | > | |
| pace-sync | | | | | | | sync-mapping-format |
| pace-trace | | | | | | | adr-format |
| pace-pulse | > | | | | | | |
| rules | > | | > | > | | | state-format |

### Schema Fan-in 摘要

| Schema 文件 | Fan-in | 稳定性要求 |
|------------|--------|-----------|
| cr-format.md | 10 | 极高——变更需评估 5+ Skill 影响 |
| checks-format.md | 4 | 高 |
| iteration-format.md | 4 | 高 |
| insights-format.md | 4 | 高 |
| sync-mapping-format.md | 4 | 高 |
| integrations-format.md | 3 | 中 |
| test-baseline-format.md | 3 | 中 |

## §E 信号系统三方同步

信号（Signal）驱动 Skill 间的衔接推荐：

```
signal-priority.md (SSOT)     ← 定义信号优先级
signal-collection.md           ← 定义信号采集规则
                                    ↓
pace-next / pace-pulse / pace-status  ← 消费信号，生成推荐
                                    ↓
session-start.sh (推送) → pace-next (拉取，去重)  ← 会话级信号流
```

三方同步要求：变更信号定义时，`signal-priority.md`、`signal-collection.md`、消费 Skill（next/pulse/status）三者需同步更新。详见 `references/sync-checklists.md`。
