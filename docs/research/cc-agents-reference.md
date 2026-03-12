# Claude Code Agents 参考手册

> **研究日期**: 2026-03-11
> **信息来源**: 官方文档 `https://code.claude.com/docs/en/sub-agents.md`、`agent-teams.md` 等，经 claude-code-guide agent 查证
> **适用版本**: Claude Code 2026-02+

---

## 目录

- [1. 概述](#1-概述)
- [2. Frontmatter 字段速查](#2-frontmatter-字段速查)
- [3. 字段详解](#3-字段详解)
- [4. 创建与管理](#4-创建与管理)
- [5. 调用方式](#5-调用方式)
- [6. 内置 Agent 类型](#6-内置-agent-类型)
- [7. Agent 记忆系统](#7-agent-记忆系统)
- [8. Agent 隔离模式](#8-agent-隔离模式)
- [9. Agent Hooks](#9-agent-hooks)
- [10. Skills 预加载](#10-skills-预加载)
- [11. Agent Teams（实验性）](#11-agent-teams实验性)
- [12. Agent vs Skill with context:fork](#12-agent-vs-skill-with-contextfork)
- [13. 限制与约束](#13-限制与约束)
- [14. 环境变量](#14-环境变量)
- [15. 实战组合模式](#15-实战组合模式)

---

## 1. 概述

### 什么是 Agent

Agent（Subagent/子 agent）是 Claude Code 中的**专业化 AI 助手**，每个 Agent 运行在独立的上下文窗口中，拥有自定义的 system prompt、工具访问权限和模型配置。当 Claude 遇到匹配 Agent description 的任务时，会自动委派给该 Agent 执行。

### 核心优势

| 优势 | 说明 |
|------|------|
| 保护上下文 | 探索/实现的中间输出不污染主对话 |
| 强制约束 | 限制 Agent 可使用的工具 |
| 复用配置 | 用户级 Agent 跨所有项目生效 |
| 专业化行为 | 聚焦特定领域的 system prompt |
| 控制成本 | 将任务路由到更快更便宜的模型 |

### Agent vs Skill

| 维度 | Agent | Skill |
|------|-------|-------|
| 上下文 | 独立上下文窗口 | 在主对话中运行（除非 `context: fork`） |
| System Prompt | 自定义（markdown body） | 指令注入主对话 |
| 工具访问 | 可独立限制 | 可指定 `allowed-tools` |
| 对话历史 | **不继承**主对话历史 | **可访问**主对话上下文 |
| 记忆持久化 | 支持 `memory` 字段 | 不支持 |
| 典型用途 | 自包含任务、需要隔离的输出 | 可复用指令、领域知识 |

---

## 2. Frontmatter 字段速查

### 完整字段表

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | **是** | — | 唯一标识符。小写字母和连字符 |
| `description` | **是** | — | 何时委派给此 Agent。Claude 据此决定自动委派 |
| `tools` | 否 | 继承全部 | 可用工具，逗号分隔或数组。支持 `Agent(type)` 语法 |
| `disallowedTools` | 否 | — | 禁用工具，从继承或指定列表中移除 |
| `model` | 否 | `inherit` | 模型：`sonnet` / `opus` / `haiku` / `inherit` |
| `permissionMode` | 否 | `default` | 权限模式：`default` / `acceptEdits` / `dontAsk` / `bypassPermissions` / `plan` |
| `maxTurns` | 否 | — | 最大执行轮数 |
| `skills` | 否 | — | 预加载到 Agent 上下文的 Skill 名称列表 |
| `mcpServers` | 否 | — | 可用的 MCP Server（名称引用或内联定义） |
| `memory` | 否 | — | 记忆持久化范围：`user` / `project` / `local` |
| `hooks` | 否 | — | Agent 级 Hook 配置 |
| `isolation` | 否 | — | `worktree` = 在独立 git worktree 中运行 |
| `background` | 否 | `false` | `true` = 始终作为后台任务运行 |
| `color` | 否 | — | UI 背景色：`blue` / `cyan` / `green` / `yellow` / `red` / `magenta` |

### 按功能分类

| 类别 | 字段 | 解决什么问题 |
|------|------|-------------|
| 身份标识 | `name`, `description`, `color` | Agent 是谁、何时委派、UI 识别 |
| 工具与权限 | `tools`, `disallowedTools`, `permissionMode` | 能用什么工具、权限如何控制 |
| 运行环境 | `model`, `maxTurns`, `isolation`, `background` | 用什么模型、运行多久、是否隔离 |
| 知识注入 | `skills`, `mcpServers` | 预加载什么知识和能力 |
| 持久化 | `memory` | 跨会话学习和记忆 |
| 生命周期 | `hooks` | 运行期间的拦截与验证 |

---

## 3. 字段详解

### 3.1 `name` — 唯一标识符（必填）

```yaml
name: code-reviewer
```

**作用**：Agent 的唯一名称，用于调用和识别。

**约束**：小写字母和连字符。当多个同名 Agent 存在时，高优先级位置的定义胜出（见 [4.1 目录优先级](#41-目录与优先级)）。

---

### 3.2 `description` — 委派条件描述（必填）

```yaml
description: Reviews code for quality and best practices. Use proactively after code changes.
```

**作用**：Claude 据此判断何时自动委派任务给此 Agent。

**编写技巧**：
- 加入 **"use proactively"** 鼓励 Claude 主动委派
- 描述 Agent 的专长领域和适用场景
- 避免过于宽泛（会抢夺其他 Agent 的任务）

---

### 3.3 `tools` — 可用工具

```yaml
tools: Read, Glob, Grep, Bash
```

**作用**：限制 Agent 可使用的工具。省略时继承全部工具。

**特殊语法 `Agent(type)`**：限制 Agent 可生成的子 Agent 类型（仅在通过 `--agent` 作为主线程运行时有效）：

```yaml
tools: Agent(worker, researcher), Read, Bash
```

此为白名单模式：只能生成 `worker` 和 `researcher`。如果 `tools` 中不含 `Agent`，则该 Agent 无法生成任何子 Agent。

---

### 3.4 `disallowedTools` — 禁用工具

```yaml
disallowedTools: Write, Edit
```

**作用**：从继承或指定的工具列表中移除特定工具。适合"允许大多数工具，排除少数几个"的场景。

**与 `tools` 的区别**：
- `tools`：白名单（只允许列出的工具）
- `disallowedTools`：黑名单（排除列出的工具，其余全部允许）
- 同时使用时，`disallowedTools` 从 `tools` 列表中移除

---

### 3.5 `model` — 指定模型

```yaml
model: haiku
```

**作用**：指定 Agent 使用的模型。默认 `inherit`（继承主对话模型）。

**可选值与场景**：

| 值 | 场景 |
|---|---|
| `haiku` | 快速探索、简单任务 — 低延迟低成本 |
| `sonnet` | 日常开发 — 平衡性能和成本 |
| `opus` | 复杂分析、架构设计 — 最强推理 |
| `inherit` | 跟随主对话（默认） |

---

### 3.6 `permissionMode` — 权限模式

```yaml
permissionMode: acceptEdits
```

**作用**：控制 Agent 如何处理权限提示。

| 模式 | 行为 |
|------|------|
| `default` | 标准权限检查（弹出确认） |
| `acceptEdits` | 自动接受文件编辑 |
| `dontAsk` | 自动拒绝权限提示（已显式允许的工具仍可用） |
| `bypassPermissions` | 跳过所有权限检查（谨慎使用） |
| `plan` | 计划模式 — 只读探索 |

**注意**：如果父级使用 `bypassPermissions`，子 Agent 无法覆盖此设置。

---

### 3.7 `maxTurns` — 最大执行轮数

```yaml
maxTurns: 30
```

**作用**：Agent 的最大执行轮数，超过后自动停止。用于防止 Agent 无限循环。

---

### 3.8 `skills` — 预加载 Skill

```yaml
skills:
  - api-conventions
  - error-handling-patterns
```

**作用**：在 Agent 启动时将列出的 Skill **完整内容**注入 Agent 上下文。

**关键点**：
- 注入的是**完整 Skill 内容**，不只是使其可调用
- Agent **不会**自动继承父对话的 Skill，必须显式列出
- 详见 [第 10 章](#10-skills-预加载)

---

### 3.9 `mcpServers` — MCP Server 配置

```yaml
mcpServers:
  - serena
  - context7
```

或内联定义：

```yaml
mcpServers:
  my-server:
    command: "node"
    args: ["./server.js"]
```

**作用**：指定 Agent 可用的 MCP Server。可引用已配置的 Server 名称，或内联定义新 Server。

---

### 3.10 `memory` — 记忆持久化

```yaml
memory: user
```

**作用**：启用跨会话持久记忆。详见 [第 7 章](#7-agent-记忆系统)。

| 值 | 存储位置 | 适用场景 |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name>/` | 跨项目通用知识（推荐默认） |
| `project` | `.claude/agent-memory/<name>/` | 项目特定，可提交到版本控制 |
| `local` | `.claude/agent-memory-local/<name>/` | 项目特定，不提交到版本控制 |

---

### 3.11 `hooks` — Agent 级 Hook

```yaml
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
```

**作用**：定义仅在该 Agent 运行期间生效的 Hook。详见 [第 9 章](#9-agent-hooks)。

---

### 3.12 `isolation` — 隔离模式

```yaml
isolation: worktree
```

**作用**：在独立的 git worktree 中运行 Agent。详见 [第 8 章](#8-agent-隔离模式)。

---

### 3.13 `background` — 后台运行

```yaml
background: true
```

**作用**：始终作为后台任务运行。后台 Agent 会自动拒绝未预批准的权限请求，且无法调用 `AskUserQuestion`。

---

### 3.14 `color` — UI 标识色

```yaml
color: cyan
```

**作用**：Agent 在 UI 中的背景色标识。

**可选值**：`blue` / `cyan` / `green` / `yellow` / `red` / `magenta`

---

## 4. 创建与管理

### 4.1 目录与优先级

| 位置 | 作用域 | 优先级 | 说明 |
|------|--------|--------|------|
| `--agents` CLI 参数 | 当前会话 | 1（最高） | 启动时传入 JSON |
| `.claude/agents/` | 当前项目 | 2 | 项目级 Agent |
| `~/.claude/agents/` | 所有项目 | 3 | 用户级 Agent |
| Plugin `agents/` | Plugin 启用处 | 4（最低） | 随 Plugin 安装 |

同名 Agent 高优先级位置胜出。

### 4.2 创建方式

#### 方式一：交互式 `/agents` 命令

在 Claude Code 中运行 `/agents`，通过引导式界面创建、查看、编辑或删除 Agent。可选择 "Generate with Claude" 由 Claude 生成 system prompt。

#### 方式二：手动创建文件

```bash
mkdir -p .claude/agents
```

创建 `.claude/agents/code-reviewer.md`：

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a senior code reviewer. Analyze code and provide specific,
actionable feedback on quality, security, and best practices.
```

#### 方式三：CLI JSON 参数（仅当前会话）

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

**注意**：JSON 格式中使用 `prompt` 字段（等同于文件方式的 markdown body）。

### 4.3 列出 Agent

- `/agents` — 交互式 TUI 管理界面
- `claude agents` — CLI 命令，按来源分组列出所有 Agent

### 4.4 加载时机

Agent 在**会话启动时**加载。手动添加文件后需要重启会话或使用 `/agents` 立即加载。

---

## 5. 调用方式

### 5.1 自动委派

Claude 根据以下信息自动决定是否委派：
- 用户请求的任务描述
- Agent 的 `description` 字段
- 当前上下文

在 `description` 中加入 **"use proactively"** 可鼓励 Claude 主动委派。

### 5.2 显式请求

用户可在对话中指名调用：

```
用 code-reviewer agent 审查我最近的改动
让 test-runner agent 跑一下测试
```

### 5.3 编程调用（Agent Tool）

在代码或 Skill 中通过 Agent Tool（原 Task Tool，仍兼容）调用：

```
Agent(
  subagent_type="code-reviewer",
  prompt="审查 src/auth/ 目录下的所有文件",
  description="审查认证模块代码"
)
```

### 5.4 `--agent` 主线程模式

将 Agent 作为**主会话 agent**（而非子 agent）运行：

```bash
claude --agent my-custom-agent
```

在此模式下，Agent **可以**生成子 Agent（通过 `tools` 字段中的 `Agent(type)` 控制可生成的类型）。这是唯一允许 Agent 生成子 Agent 的方式。

---

## 6. 内置 Agent 类型

| Agent | 模型 | 工具范围 | 用途 |
|-------|------|---------|------|
| `general-purpose` | 继承 | 全部工具 | 复杂研究、多步操作、代码修改 |
| `Explore` | Haiku | 只读（禁用 Write/Edit） | 文件发现、代码搜索、代码库探索 |
| `Plan` | 继承 | 只读（禁用 Write/Edit） | 计划模式下的代码库研究 |
| `Bash` | 继承 | 终端命令 | 在独立上下文中运行终端命令 |
| `statusline-setup` | Sonnet | Read, Edit | `/statusline` 配置状态栏 |
| `claude-code-guide` | Haiku | Read, Glob, Grep, WebFetch, WebSearch | Claude Code 功能问答 |

### Explore 详解

- 使用 Haiku 模型（快速、低延迟）
- Claude 委派探索任务时会指定彻底程度：**quick**（基本搜索）、**medium**（适度探索）、**very thorough**（全面分析）
- 不可修改文件，适合安全的代码库探索

---

## 7. Agent 记忆系统

### 工作原理

启用 `memory` 后：

1. Agent 的 system prompt 中自动包含读写记忆目录的指令
2. 记忆目录中 `MEMORY.md` 的前 **200 行**被注入 system prompt
3. `Read`、`Write`、`Edit` 工具**自动启用**（即使 `tools` 中未列出）
4. Agent 可自主管理记忆文件

### 记忆范围

| 范围 | 存储位置 | 适用场景 |
|------|---------|---------|
| `user` | `~/.claude/agent-memory/<name>/` | 跨项目通用知识（**推荐默认**） |
| `project` | `.claude/agent-memory/<name>/` | 项目特定，可入版本控制共享 |
| `local` | `.claude/agent-memory-local/<name>/` | 项目特定，不入版本控制 |

### 最佳实践

在 Agent 的 markdown body 中加入记忆指令：

```markdown
---
name: code-reviewer
description: Reviews code quality
memory: user
---

You are a senior code reviewer.

**Memory instructions:**
- Before starting, consult your memory for patterns and decisions.
- After completing a review, update your memory with new patterns discovered.
- Track recurring issues to provide progressively better feedback.
```

---

## 8. Agent 隔离模式

### Worktree 隔离

```yaml
isolation: worktree
```

**行为**：
- Agent 在独立的 git worktree（仓库的隔离副本）中运行
- 修改完全隔离于主工作目录
- **无变更时**自动清理 worktree
- **有变更时**保留 worktree 供审查，返回 worktree 路径和分支名

**适用场景**：
- 高风险重构 — 在隔离环境中安全试验
- 并行实验 — 同时探索多种方案
- 代码生成 — 避免半成品污染主目录

---

## 9. Agent Hooks

### 9.1 Agent 内部 Hook

在 Agent frontmatter 中定义，**仅在该 Agent 运行期间生效**：

```yaml
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

所有 Hook 事件均支持。Agent 的 `Stop` hook 会自动转换为 `SubagentStop` 事件。

### 9.2 项目级 Agent 生命周期 Hook

在 `settings.json` 中配置，响应 Agent 生命周期事件：

| 事件 | 触发时机 | 可阻断 | Matcher 输入 |
|------|---------|--------|-------------|
| `SubagentStart` | Agent 开始执行 | 否（但可注入上下文） | Agent 类型名 |
| `SubagentStop` | Agent 完成执行 | 是（exit 2 阻止停止） | Agent 类型名 |

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db-connection.sh" }
        ]
      }
    ]
  }
}
```

`SubagentStart` hook 可返回 `systemPromptSuffix` 向 Agent 注入额外上下文。

---

## 10. Skills 预加载

### 机制

```yaml
skills:
  - api-conventions
  - error-handling-patterns
```

`skills` 字段将 Skill 的**完整内容**注入 Agent 上下文：

- 注入的是完整 SKILL.md 内容，不只是使其可调用
- Agent **不会**自动继承父对话的 Skill，必须显式列出
- Skill 内容在 Agent 启动时一次性加载

### 与 Skill `context: fork` 的关系

| 方式 | System Prompt 来源 | Task 来源 | 附加加载 |
|------|-------------------|-----------|---------|
| Skill + `context: fork` | Agent 类型定义 | SKILL.md 内容 | CLAUDE.md |
| Agent + `skills` 字段 | Agent 的 markdown body | Claude 的委派消息 | 预加载 Skills + CLAUDE.md |

**选择建议**：
- **Skill + fork**：你写好具体任务，选一个 Agent 类型执行
- **Agent + skills**：你定义 Agent 能力，将 Skill 作为知识注入，由 Claude 决定委派什么任务

---

## 11. Agent Teams（实验性）

### 启用

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 与 Subagent 的区别

| 维度 | Subagent | Agent Team |
|------|----------|------------|
| 上下文 | 独立窗口，结果返回调用者 | 完全独立窗口 |
| 通信 | 仅向主 Agent 报告结果 | 成员间直接消息 |
| 协调 | 主 Agent 管理所有工作 | 共享任务列表，自协调 |
| 适用 | 聚焦任务，只需结果 | 复杂工作，需要讨论和协作 |
| Token 成本 | 较低（结果摘要返回） | 较高（每个成员独立实例） |

### 架构

| 组件 | 角色 |
|------|------|
| Team Lead | 主 Claude Code 会话，创建团队并协调 |
| Teammate | 独立 Claude Code 实例，执行分配的任务 |
| Task List | 共享工作项，成员认领并完成 |
| Mailbox | 成员间消息系统 |

### 显示模式

| 模式 | 说明 |
|------|------|
| `in-process` | 所有成员在主终端中，Shift+Down 切换 |
| `tmux` | 每个成员独立窗格（需要 tmux 或 iTerm2） |
| `auto`（默认） | 在 tmux 中则分窗格，否则 in-process |

### Team Hook

| 事件 | 触发时机 | 可阻断 |
|------|---------|--------|
| `TeammateIdle` | 成员即将空闲 | 是（exit 2 发送反馈，成员继续工作） |
| `TaskCompleted` | 任务标记完成 | 是（exit 2 阻止完成，发送反馈） |

---

## 12. Agent vs Skill with context:fork

| 维度 | Agent | Skill + `context: fork` |
|------|-------|------------------------|
| System Prompt | 自定义（markdown body） | Agent 类型的默认 prompt |
| Task | Claude 的委派消息 | SKILL.md 内容 |
| 复用性 | 通用专业化，处理多种任务 | 特定工作流/任务封装 |
| 触发方式 | Claude 自动委派或用户指名 | 用户 `/name` 或 Claude 自动触发 |
| 记忆 | 支持 `memory` 持久化 | 不支持 |
| 配置粒度 | 全面：model、tools、permissions、hooks、isolation、memory | 有限：`agent` 类型、`allowed-tools` |
| 生命周期 | 持久存在的专家角色 | 一次性任务执行 |

**决策规则**：
- 需要**持久专家**（有自己的身份和记忆）→ Agent
- 需要**可复用任务配方**（在隔离中运行）→ Skill + `context: fork`

---

## 13. 限制与约束

| 约束 | 说明 |
|------|------|
| **不可嵌套** | Subagent 不能生成其他 Subagent。需要嵌套委派时用 Skill 或从主对话链式调用 |
| **不继承 System Prompt** | Subagent 只接收自己的 markdown body + 基本环境信息，不接收主对话的完整 system prompt |
| **不继承 Skills** | 必须在 `skills` 字段中显式列出 |
| **后台 Agent 权限受限** | 未预批准的权限请求自动拒绝，无法调用 `AskUserQuestion` |
| **`Agent(type)` 限制仅限主线程** | `tools` 中的 `Agent(type)` 语法仅在 `--agent` 主线程模式下生效 |
| **Agent Teams 实验性** | 不支持会话恢复、任务状态可能滞后、每会话一个团队、不可嵌套团队 |

---

## 14. 环境变量

| 变量 | 用途 |
|------|------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | 设为 `1` 启用 Agent Teams |
| `CLAUDE_CODE_TEAMMATE_MODE` | 成员显示模式：`auto` / `in-process` / `tmux` |
| `CLAUDE_CODE_SUBAGENT_MODEL` | 覆盖 Subagent 使用的模型 |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | 设为 `1` 禁用所有后台任务 |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 覆盖 Subagent 自动压缩阈值（默认 ~95%） |
| `CLAUDE_CODE_PLAN_MODE_REQUIRED` | 标记成员需要计划审批（自动设置，只读） |
| `CLAUDE_CODE_TEAM_NAME` | 成员所属团队名（自动设置） |

---

## 15. 实战组合模式

### 模式 1：只读探索 Agent

安全的代码库探索，不可修改文件。

```markdown
---
name: codebase-explorer
description: Explore and understand codebase structure. Use proactively when searching.
tools: Read, Glob, Grep
model: haiku
---

You are a codebase exploration specialist. Find files, understand structure,
and report findings concisely. Never suggest modifications.
```

**适用**：代码搜索、架构理解、依赖分析

### 模式 2：带记忆的代码审查 Agent

跨会话积累审查经验。

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices. Use proactively after code changes.
tools: Read, Glob, Grep
model: sonnet
memory: project
---

You are a senior code reviewer. Before starting:
1. Consult your memory for project patterns and past findings
2. Review the code for quality, security, and best practices
3. After review, update your memory with new patterns discovered
```

**适用**：持续代码质量改进、模式积累

### 模式 3：隔离重构 Agent

在 worktree 中安全重构。

```markdown
---
name: refactorer
description: Performs complex refactoring in isolation
tools: Read, Write, Edit, Glob, Grep, Bash
model: opus
isolation: worktree
permissionMode: acceptEdits
---

You are a refactoring specialist. Work in your isolated worktree.
Make bold changes — your work is isolated and can be reviewed before merging.
```

**适用**：高风险重构、大规模代码迁移

### 模式 4：带 Skill 知识的专业 Agent

预加载 Skill 作为领域知识。

```markdown
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
Always check existing patterns before creating new ones.
```

**适用**：需要遵循特定规范的实现任务

### 模式 5：后台分析 Agent

异步运行，不阻塞主对话。

```markdown
---
name: security-scanner
description: Scan codebase for security vulnerabilities
tools: Read, Glob, Grep, Bash
model: sonnet
background: true
---

Scan the codebase for security vulnerabilities. Check for:
- SQL injection, XSS, CSRF
- Hardcoded secrets
- Outdated dependencies with known CVEs
Report findings in a structured format.
```

**适用**：安全扫描、性能分析、长时间运行的检查任务

### 模式 6：带 Hook 保护的写入 Agent

执行期间自动验证写入操作。

```markdown
---
name: schema-generator
description: Generate database schema files
tools: Read, Write, Glob, Grep
model: sonnet
hooks:
  PreToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "./scripts/validate-schema.sh"
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "./scripts/run-migration-check.sh"
---

Generate database schema files following project conventions.
All writes are automatically validated by hooks.
```

**适用**：Schema 生成、配置管理、需要自动验证的文件写入

---

## 附录：官方文档索引

| 主题 | URL |
|------|-----|
| Subagents | `https://code.claude.com/docs/en/sub-agents.md` |
| Agent Teams | `https://code.claude.com/docs/en/agent-teams.md` |
| Skills（context:fork） | `https://code.claude.com/docs/en/skills.md` |
| Hooks（SubagentStart/Stop） | `https://code.claude.com/docs/en/hooks.md` |
| Permissions | `https://code.claude.com/docs/en/permissions.md` |
| CLI Reference（--agents/--agent） | `https://code.claude.com/docs/en/cli-reference.md` |
| Plugins（plugin agents） | `https://code.claude.com/docs/en/plugins-reference.md` |
| Settings | `https://code.claude.com/docs/en/settings.md` |
