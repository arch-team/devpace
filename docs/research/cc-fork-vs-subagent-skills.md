# Skill Fork vs Subagent Skills：两种子 agent 运行模式对比

> 分析 `context: fork + agent` 与 `Subagent + skills 字段` 两种模式下，Skill 内容的加载方式、角色定位和适用场景差异。
>
> **勘误**（2026-03-12）：初版错误地将 Agent `skills` 字段描述为"仅注入 description，按需通过 Skill tool 加载"。经与 `cc-agents-reference.md` 第 557-561 行交叉验证，`skills` 字段实际是**启动时全量注入** SKILL.md 内容。已修正。

---

## 1. 信息加载时序

### 模式 A：Skill + `context: fork` + `agent`

```
主对话                                子 agent 上下文
────────────────────                  ────────────────────
1. 看到 description (~100 词)
2. 用户触发 -> Skill tool
3. 派发 Task ──────────────────────>  4. SKILL.md 全文作为 task prompt（一次性全量加载）
                                      5. CLAUDE.md 也加载
                                      6. 自主执行，遇到引用文件时 Read 加载
7. 收到结果摘要  <────────────────────  8. 返回摘要
```

**加载方式**：SKILL.md 全文 = 子 agent 的**任务指令**，一次性交付。引用的 procedure 文件需子 agent 主动 Read。

### 模式 B：Subagent + `skills` 字段

```
主对话                                子 agent 上下文
────────────────────                  ────────────────────
1. Claude 决定委派任务
2. Task(subagent_type="pace-pm")
3. 派发 Task ──────────────────────>  4. Agent markdown body 作为 system prompt
                                      5. skills 列表中的 SKILL.md 全文注入（全量，非按需）
                                      6. CLAUDE.md 也加载
                                      7. Claude 的委派消息作为 task
                                      8. 自主执行，遇到引用文件时 Read 加载
9. 收到结果摘要  <────────────────────  10. 返回摘要
```

**加载方式**：所有 `skills` 列出的 SKILL.md **完整内容在 Agent 启动时一次性注入**上下文，作为**背景知识**而非任务指令。引用的 procedure 文件仍需主动 Read。

> **来源**：`cc-agents-reference.md` 第 557-561 行：
> "skills 字段将 Skill 的完整内容注入 Agent 上下文。注入的是完整 SKILL.md 内容，不只是使其可调用。Skill 内容在 Agent 启动时一次性加载。"

---

## 2. 核心差异总结

两种模式都是 SKILL.md **全量加载**，差异在于 SKILL.md 的角色和控制权：

| 维度 | Skill + fork | Subagent + skills |
|------|-------------|-------------------|
| **SKILL.md 的角色** | 任务指令（工单） | 背景知识（参考手册） |
| **何时加载** | fork 时立即加载 | Agent 启动时全量注入 |
| **谁写任务** | Skill 作者（写死在 SKILL.md） | Claude（动态生成委派消息） |
| **子 agent 的角色** | 单任务执行者 | 多知识持有者 |
| **谁决定用哪个 skill** | 主对话的 Claude（触发哪个就 fork 哪个） | Claude（委派时选择哪个 agent） |
| **多 skill 支持** | 一次只 fork 一个 skill | 多个 skill 内容同时注入 |
| **上下文开销** | 仅消耗被触发的那一个 SKILL.md | 消耗所有列出的 SKILL.md（启动即全部注入） |
| **控制权** | Skill 作者 | Claude + Agent 定义者 |

---

## 3. devpace 实例说明

### 当前 pace-dev（fork 模式）

```
用户说 "开始做 CR-003"
  -> 触发 pace-dev skill
  -> fork 出 pace-engineer 子 agent
  -> pace-engineer 收到 pace-dev SKILL.md 全文作为任务
  -> 按 SKILL.md 步骤执行（读 procedure 文件、写代码...）
```

子 agent **只能做 pace-dev 这一件事**，SKILL.md 就是它的全部指令。

### 假设改为 subagent + skills 模式

```yaml
# agents/pace-engineer.md
---
name: pace-engineer
tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
skills: devpace:pace-dev, devpace:pace-test, devpace:pace-review
---
```

```
用户说 "帮我实现并测试 CR-003"
  -> Claude 委派给 pace-engineer
  -> pace-engineer 启动，pace-dev + pace-test + pace-review 三个 SKILL.md 全文注入上下文
  -> Claude 的委派消息："实现并测试 CR-003"
  -> pace-engineer 根据注入的知识自主决定工作流
```

子 agent **拥有三份 SKILL.md 的完整知识**，但任务由 Claude 的委派消息决定。

### 上下文开销对比

假设三个 SKILL.md 各 300 行：

| 模式 | 启动时上下文消耗 |
|------|----------------|
| fork pace-dev | 300 行（仅 pace-dev） |
| subagent + 3 skills | 900 行（三个 SKILL.md 全部注入） |

**代价**：subagent + skills 模式启动成本更高（全量注入），但子 agent 拥有更完整的知识。

---

## 4. 选型指南

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| 任务流程固定、单一职责 | **fork** | SKILL.md 写好了所有步骤，不需要动态判断 |
| 需要严格控制执行步骤 | **fork** | 作者写死流程，子 agent 不会自行决定跳过步骤 |
| 子 agent 需要综合多领域知识 | **subagent + skills** | 多份知识同时可用，灵活应对复杂任务 |
| SKILL.md 较短且彼此相关 | **subagent + skills** | 全量注入开销可接受，知识整合价值高 |
| 每个 SKILL.md 很长（200+ 行） | **fork** | 避免 subagent 模式下多份大文件同时注入撑爆上下文 |
| 省上下文 token | **fork** | 只加载一个 SKILL.md，而非全部 |

---

## 5. devpace 当前 Skill 配置一览

### 已使用 fork 的（9 个）

| Skill | Agent | 适合 fork 的原因 |
|-------|-------|-----------------|
| pace-dev | pace-engineer | 核心开发流程，多步实现+写代码+跑测试，maxTurns=50 |
| pace-test | pace-engineer | 执行测试策略+跑测试+生成覆盖报告，自主完成后返回结果 |
| pace-plan | pace-pm | 迭代规划需读取大量状态文件+生成迭代计划文件 |
| pace-change | pace-pm | 变更影响分析+triage report+状态更新，多文件写入 |
| pace-biz | pace-pm | 业务需求发现/分解/导入，需自主分析+创建多个需求文件 |
| pace-retro | pace-analyst | 度量数据采集+分析+生成回顾报告，计算密集型 |
| pace-review | pace-engineer | 代码审查：diff 分析+验收对照+生成审查报告+更新 CR 状态 |
| pace-guard | pace-analyst | 风险预检：扫描+评估+生成风险报告 |
| pace-release | pace-engineer | 发布流程：版本号+changelog+tag+状态更新 |

### 未使用 fork 的（10 个）

| Skill | 不 fork 的原因 |
|-------|---------------|
| pace-status | 纯读取+格式化输出，1-2 步完成，用户看完可能立即追问 |
| pace-next | 信号采集+推荐排序+输出，用户需要基于推荐继续对话 |
| pace-theory | 概念解释/教学，高度依赖用户追问的上下文 |
| pace-role | 视角切换修改后续输出风格，必须留在主上下文 |
| pace-pulse | 节奏健康检测，轻量诊断+提醒 |
| pace-trace | 追溯决策记录，查询+展示，用户常连续追问 |
| pace-learn | 知识库管理，简短的记录/更新操作 |
| pace-init | 项目初始化，通常只执行一次且用户想看到过程 |
| pace-sync | 外部工具同步，取决于子命令复杂度 |
| pace-feedback | 用户反馈处理，可能需要与用户多轮确认 |

### fork 判断口诀

```
写多文件 + 步骤长 + 不需回聊 -> fork
只读展示 + 步骤短 + 要追问   -> 不 fork
```

---

## 6. 官方文档验证状态

| 结论 | 验证状态 | 来源 |
|------|---------|------|
| `context: fork` 全量加载 SKILL.md 作为 task prompt | 项目研究文档一致支持 | cc-skills-reference.md 第 237 行 |
| Agent `skills` 字段全量注入 SKILL.md | 项目研究文档明确记载 | cc-agents-reference.md 第 557-561 行 |
| `agent` 字段支持自定义 agent | 项目研究文档+实际使用验证 | cc-skills-reference.md 第 260-266 行 |
| fork = 单 skill，subagent = 多 skill | 架构逻辑自洽 | cc-skills-reference.md 第 417-431 行 |

> **注意**：以上结论基于项目研究文档（cc-agents-reference.md、cc-skills-reference.md），这些文档声称来源于 `code.claude.com` 官方文档。VSCode Claude Code 扩展的缓存 schema 尚未覆盖 `context`、`agent`、`hooks` 等运行时字段，但 CLI 实际支持这些字段。
