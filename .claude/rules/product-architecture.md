# 产品层组件架构

> **职责**：产品层组件间的协作关系——依赖方向、通信模式、合规检测。与 `info-architecture.md`（信息组织原则）、`plugin-dev-spec.md`（组件格式规范）、`project-structure.md`（文件放置规则）互补。

## §0 速查卡片

### 组件依赖矩阵（简版）

谁引用谁？`>` = 合法引用方向，`X` = 禁止。

| 引用方 \ 被引用方 | rules | SKILL.md | procedures | _schema | _signals | _guides | knowledge-root | hooks | agents |
|-------------------|-------|----------|-----------|---------|----------|---------|---------------|-------|--------|
| **rules** | — | X | X | > | > | X | > | X | X |
| **SKILL.md** | > | — | > (同 Skill) | > | > | > | > | X | X |
| **procedures** | > | X | — | > | > | > | > | X | X |
| **_schema** | X | X | X | > (同级) | X | X | X | X | X |
| **_signals** | X | X | X | > | — | X | > | X | X |
| **_guides** | X | X | X | > | > | — | > | X | X |
| **knowledge-root** | X | X | X | > | X | X | — | X | X |
| **hooks** | X | X | X | X | X | X | X | — | X |
| **agents** | X | X | X | X | X | X | X | X | — |

**关键约束**：
- **Schema 是纯契约层**——仅引用同级 Schema，不引用 Skill、Rules 或 Hooks 实现
- **Hooks 是独立守护层**——通过 `.devpace/` 运行时文件和 stdin JSON 感知状态，不解析 Markdown 引用
- **Agents 是纯人格定义**——仅包含 persona + 工具权限，不引用任何其他组件

### 组件选择决策树

```
新功能需求
├─ 定义行为约束？ → rules/devpace-rules.md（§N 新增）
├─ 定义工作流程？
│  ├─ 需要专属 Agent？ → skills/pace-xxx/（context: fork）
│  └─ 轻量操作？ → skills/pace-xxx/（inline）
├─ 定义数据格式？ → knowledge/_schema/<subdir>/
├─ 定义信号路由？ → knowledge/_signals/
├─ 定义操作指南？ → knowledge/_guides/
├─ 守护质量门禁？ → hooks/（Gate 3 = Hook 阻断）
└─ 定义角色人格？ → agents/pace-xxx.md
```

### 合规检查清单

| 检查项 | 命令 / 方法 | 频率 |
|--------|------------|------|
| Schema 无反向引用 | `grep -r "skills/\|rules/" knowledge/_schema/` 应为空 | 每次 Schema 变更 |
| Hooks 无 Markdown 引用 | `grep -r "knowledge/\|skills/\|rules/" hooks/` 应为空 | 每次 Hook 变更 |
| Agents 无组件引用 | `grep -r "knowledge/\|skills/\|rules/\|hooks/" agents/` 应为空 | 每次 Agent 变更 |
| 分层完整性（全量） | `bash dev-scripts/validate-all.sh` | 每次提交前 |

## §1 核心架构原则

三大模式定义产品层组件如何协作，与 `info-architecture.md` 的 11 项组织原则互补——IA 原则回答"为什么这样组织信息"，本文件回答"组件之间如何协作"。

### 1. 六层信息栈（IA-1/IA-2 的运行时投影）

```
Layer 6: knowledge/theory      (Why  — 概念知识，被动加载，极少变更)
Layer 5: rules/               (Must — 行为约束，会话启动时自动加载)
Layer 4: knowledge/_schema/*/  (Shape — 数据格式契约，按需加载；分 entity/process/integration/auxiliary)
Layer 3: skills/*/SKILL.md    (What — 路由层，description 触发加载)
Layer 2: skills/*/*-procedures.md (How — 操作步骤，按状态/子命令条件加载)
Layer 1: knowledge/_templates/ (Instance — 具体实例，实例化时加载)
```

**依赖方向严格从下层指向上层**（权威定义见 `info-architecture.md` IA-1）——Layer 2 引用 Layer 4 合法；反向禁止。

**信息类型→资产映射**：

| 信息类型 | Plugin 资产 | 特征 |
|---------|------------|------|
| 步骤（Procedure） | `*-procedures.md` | 按步操作指令 |
| 约束（Principle） | `rules/*.md` | 行为规范 |
| 概念（Concept） | `knowledge/*.md` | 背景知识 |
| 结构（Structure） | `knowledge/_schema/*/*.md` | 数据格式定义（四子目录分组） |
| 路由（Process） | `SKILL.md` | 工作流分发 |
| 实例（Fact） | `knowledge/_templates/*.md` | 具体模板 |

### 2. 事件驱动守护（Hook 层独立性）

Hooks 通过 **stdin JSON + exit code + stdout** 与 Skill 层通信，**不解析 Markdown 文件引用**。Guard 通过 `.devpace/` 运行时文件感知状态。这保证 Hook 逻辑的可测试性和独立演进。

### 3. 契约协作（Schema 中介模式）

Skills 通过 **Schema + `.devpace/` 状态文件**间接协作，不直接引用对方 procedures。生产方和消费方都依赖契约，不依赖对方内部实现。

## §2 组件类型与依赖规则

### 六类组件职责边界

| 组件类型 | 职责 | 引用规则 |
|---------|------|---------|
| **rules/** | 行为约束，始终加载 | 可引用 knowledge/（Schema + root），不引用 Skill 实现 |
| **skills/SKILL.md** | 工作流路由（做什么） | 可引用 rules、knowledge 全域、同 Skill 的 procedures |
| **skills/procedures** | 操作步骤（怎么做） | 可引用 rules、knowledge 全域，不引用其他 Skill 的 procedures |
| **knowledge/_schema/** | 数据格式契约 | 仅引用同级 Schema（如 cr-format 引用 checks-format），不引用 Skill/Rules |
| **knowledge/ (root + _signals + _guides + _extraction)** | 领域知识 | 可引用同层 knowledge，不引用 Skill/Rules |
| **hooks/** | 质量守护（事件驱动） | 零 Markdown 引用——通过 stdin JSON + `.devpace/` 文件感知状态 |
| **agents/** | 角色人格定义 | 零外部引用——仅定义 persona + tools + model |

### 禁止模式（附预防合理化）

| 禁止模式 | 常见借口 | 反驳 |
|---------|---------|------|
| Schema 引用 Skill procedures | "方便说明填充规则" | Schema 只定义格式和验证约束，填充规则属于 procedures |
| procedures 引用其他 Skill 的 procedures | "复用步骤" | 提取共享步骤到 `knowledge/_guides/`，让两个 Skill 各自引用 |
| Hooks 解析 Markdown 文件 | "需要读 CR 状态" | Hook 通过 `.devpace/state.md` 的 JSON/文本解析获取状态 |
| Agents 包含业务逻辑 | "Agent 需要知道流程" | 业务逻辑在 SKILL.md + procedures 中；Agent 只定义 persona |

## §3 数据流与通信模式

### Skill-Agent 路由矩阵

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

### Hook 架构模式

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

### Agent 协作架构

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

### Skill → Schema 依赖矩阵

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

### 信号系统三方同步

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

## §4 合规检测

### 自动化检测（完整检查表，整合自 CLAUDE.md 和 info-architecture.md）

```bash
# Schema 纯净性（零反向引用）
grep -r "skills/\|rules/" knowledge/_schema/

# Hook 独立性（零 Markdown 引用）
grep -r "knowledge/\|skills/\|rules/" hooks/ --include="*.mjs" --include="*.sh"

# Agent 纯净性（零外部引用）
grep -r "knowledge/\|skills/\|rules/\|hooks/" agents/

# 跨 Skill procedures 引用（应为空）
grep -rn "skills/pace-" skills/ --include="*-procedures*.md" | grep -v "自身目录"

# 全量检测
bash dev-scripts/validate-all.sh
```

### 手动检查

- [ ] 新增 Schema 字段后，检查 fan-in 消费者（查 `_schema/README.md`）是否需要适配
- [ ] 新增 Skill 时，确认 Agent 路由（fork vs inline）与职责域匹配
- [ ] Hook 逻辑变更后，确认仅通过 stdin JSON / `.devpace/` 文件获取状态
