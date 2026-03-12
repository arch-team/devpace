# Claude Code Skills 参考手册

> **研究日期**: 2026-03-11
> **信息来源**: 官方文档 `https://code.claude.com/docs/en/skills.md`，经 claude-code-guide agent 查证
> **适用版本**: Claude Code 2026-02+

---

## 目录

- [1. 概述](#1-概述)
- [2. Frontmatter 字段速查](#2-frontmatter-字段速查)
- [3. 字段详解](#3-字段详解)
  - [3.1 name — 显示名称](#31-name--显示名称)
  - [3.2 description — 触发条件描述](#32-description--触发条件描述)
  - [3.3 argument-hint — 参数提示](#33-argument-hint--参数提示)
  - [3.4 disable-model-invocation — 禁止自动调用](#34-disable-model-invocation--禁止自动调用)
  - [3.5 user-invocable — 用户可见性](#35-user-invocable--用户可见性)
  - [3.6 allowed-tools — 免确认工具](#36-allowed-tools--免确认工具)
  - [3.7 model — 指定模型](#37-model--指定模型)
  - [3.8 context — 子 agent 隔离运行](#38-context--子-agent-隔离运行)
  - [3.9 agent — 指定子 agent 类型](#39-agent--指定子-agent-类型)
  - [3.10 hooks — Skill 级 Hook](#310-hooks--skill-级-hook)
- [4. 字符串替换变量](#4-字符串替换变量)
- [5. Subagent Fork 深入解析](#5-subagent-fork-深入解析)
- [6. 实战组合模式](#6-实战组合模式)

---

## 1. 概述

### 什么是 Skill

Skill 是 Claude Code 的可复用指令模块，以 `skills/<name>/SKILL.md` 文件形式存在。用户通过 `/name` 手动调用，或由 Claude 根据对话上下文自动触发。

### 什么是 Frontmatter

Frontmatter 是 SKILL.md 文件顶部 `---` 包裹的 YAML 块，定义 Skill 的**元数据和行为控制**。Claude 通过这些字段决定：

- **何时触发** — `description`, `disable-model-invocation`, `user-invocable`
- **如何运行** — `context`, `agent`, `model`
- **有什么权限** — `allowed-tools`
- **生命周期拦截** — `hooks`

### 基本结构

```markdown
---
name: my-skill
description: Use when user says "xxx" or /my-skill
allowed-tools: Read, Write, Edit
---

# Skill 正文内容

这里是 Claude 加载此 Skill 后执行的指令...
```

---

## 2. Frontmatter 字段速查

### 完整字段表

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | 否 | 目录名 | 显示名称。仅限小写字母、数字、连字符（最长 64 字符） |
| `description` | 推荐 | markdown 首段 | 触发条件描述。Claude 据此判断是否自动调用 |
| `argument-hint` | 否 | — | 自动补全参数提示，如 `[issue-number]` |
| `disable-model-invocation` | 否 | `false` | `true` = 禁止 Claude 自动触发，仅用户手动 `/name` 调用 |
| `user-invocable` | 否 | `true` | `false` = 从 `/` 菜单隐藏，仅 Claude 内部可调用 |
| `allowed-tools` | 否 | — | Skill 激活期间免确认的工具，逗号分隔 |
| `model` | 否 | 会话当前模型 | 指定模型：`sonnet` / `opus` / `haiku` |
| `context` | 否 | — | `fork` = 在隔离子 agent 上下文中运行 |
| `agent` | 否 | `general-purpose` | `context: fork` 时使用的 agent 类型 |
| `hooks` | 否 | — | 作用域为此 Skill 的 Hook 配置 |

### 按功能分类

| 类别 | 字段 | 解决什么问题 |
|------|------|-------------|
| 身份标识 | `name`, `description`, `argument-hint` | Skill 是谁、何时触发、怎么传参 |
| 触发控制 | `disable-model-invocation`, `user-invocable` | 谁能调用、是否自动触发 |
| 运行环境 | `model`, `context`, `agent`, `allowed-tools` | 用什么模型、在哪运行、有什么权限 |
| 生命周期 | `hooks` | Skill 运行期间的拦截与验证 |

### 触发控制组合矩阵

| 组合 | 用户可调用 | Claude 可自动调用 | 典型用途 |
|------|-----------|------------------|---------|
| 两者都默认 | 是 | 是 | 常规 Skill |
| `disable-model-invocation: true` | 是 | 否 | 危险操作、手动触发 |
| `user-invocable: false` | 否 | 是 | 背景知识、内部子流程 |
| 两者都设置 | 否 | 否 | 无意义（不会被使用） |

---

## 3. 字段详解

### 3.1 `name` — 显示名称

```yaml
name: deep-research
```

**作用**：Skill 在 `/` 菜单中的显示名称。省略时取目录名。

**约束**：仅限小写字母、数字、连字符，最长 64 字符。

**应用场景**：
- 目录名用于文件系统组织（如 `pace-dev/`），但想在 UI 中显示不同名称时设置
- 大多数情况下省略即可，让目录名 = 显示名，减少维护成本

---

### 3.2 `description` — 触发条件描述

```yaml
description: Use when user says "开始做/帮我改/实现/修复" or /pace-dev
```

**作用**：Claude 判断是否自动触发该 Skill 的**唯一依据**。省略时取 markdown 内容的第一段。

**应用场景**：

| 场景 | description 写法 |
|------|-----------------|
| 用户驱动的命令 | `Use when user says "关键词1/关键词2" or /skill-name` |
| 上下文自动触发 | `Use when CR reaches in_review state` |
| 背景知识（不触发） | 配合 `user-invocable: false` 使用，description 供 Claude 内部匹配 |

**编写原则**：

| 规则 | 正确 | 错误 |
|------|------|------|
| 只写"何时触发"，不写"做什么" | `Use when user wants to track changes` | `Analyzes impact and updates status` |
| 开头用 "Use when" | `Use when entering dev mode` | `Development mode skill` |
| 包含具体触发关键词 | `Use when user says "开始做/修复"` | `Handles implementation tasks` |
| 避免描述内部步骤 | `Use when CR needs review` | `Runs Gate 2 checks, generates diff` |

**为什么重要**：description 写不好会导致两个问题：
1. Claude 跳过阅读完整 SKILL.md，按 description 摘要直接行动
2. 误触发（过于模糊）或漏触发（过于具体）

---

### 3.3 `argument-hint` — 参数提示

```yaml
argument-hint: "[CR编号] [子命令]"
```

**作用**：用户输入 `/skill-name` 时，自动补全下拉框中显示的参数提示。

**应用场景**：
- `/pace-dev CR-003` → `argument-hint: "[CR编号]"`
- `/pace-change add "新功能描述"` → `argument-hint: "[子命令] [描述]"`
- 无参数的 Skill 不需要设置

---

### 3.4 `disable-model-invocation` — 禁止自动调用

```yaml
disable-model-invocation: true
```

**作用**：设为 `true` 后，Claude **不会**根据对话上下文自动触发此 Skill，只能由用户手动输入 `/name` 调用。默认 `false`。

**应用场景**：

| 场景 | 设置 |
|------|------|
| 危险操作（如数据库迁移、发布） | `true` — 必须人工显式触发 |
| 日常开发辅助 | `false` — 让 Claude 根据上下文自动激活 |
| 调试/诊断工具 | `true` — 避免误触发干扰正常工作流 |

---

### 3.5 `user-invocable` — 用户可见性

```yaml
user-invocable: false
```

**作用**：设为 `false` 后，从 `/` 菜单中隐藏，用户看不到也无法手动调用。仅 Claude 内部可通过 description 匹配调用。默认 `true`。

**应用场景**：
- **背景知识注入**：如编码规范、API 约定 — Claude 在相关上下文自动加载，但用户不需要直接调用
- **内部子流程**：被其他 Skill 间接依赖的辅助 Skill

---

### 3.6 `allowed-tools` — 免确认工具

```yaml
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
```

**作用**：Skill 激活期间，列出的工具无需用户逐次确认即可执行。

**应用场景**：
- **高频读写 Skill**：`Read, Write, Edit, Glob, Grep` — 避免反复弹确认框
- **需要执行脚本**：加入 `Bash`
- **需要 MCP 工具**：`mcp__serena__find_symbol, mcp__context7__query-docs`
- **安全敏感 Skill**：故意**不**列入危险工具，保留人工确认

---

### 3.7 `model` — 指定模型

```yaml
model: sonnet
```

**作用**：覆盖当前会话的默认模型，在此 Skill 激活期间使用指定模型。

**可选值**：`sonnet` / `opus` / `haiku`

**应用场景**：

| 模型 | 场景 |
|------|------|
| `haiku` | 简单模板生成、格式转换 — 追求速度和成本 |
| `sonnet` | 日常开发、代码生成 — 平衡性能和成本 |
| `opus` | 复杂架构分析、多文件重构 — 需要最强推理能力 |
| 不设置 | 跟随会话当前模型 — 大多数情况的推荐做法 |

---

### 3.8 `context` — 子 agent 隔离运行

```yaml
context: fork
```

**作用**：Skill 在**独立的子 agent 上下文**中运行，不携带主对话历史。SKILL.md 内容作为子 agent 的任务 prompt。

**应用场景**：
- **重量级分析**：避免大量中间输出污染主对话上下文
- **独立任务**：研究、探索、代码审查 — 结果摘要返回即可
- **上下文敏感**：需要干净上下文（不受之前对话影响）的任务

**不适用**：Skill 内容是指导原则而非具体任务时（子 agent 没有可执行的操作，会返回空结果）

> 深入机制详见 [第 5 章 Subagent Fork 深入解析](#5-subagent-fork-深入解析)

---

### 3.9 `agent` — 指定子 agent 类型

```yaml
agent: Explore
```

**作用**：当 `context: fork` 时，指定用哪个 agent 类型执行。决定了子 agent 的 system prompt、可用工具、权限。省略时默认 `general-purpose`。

**可用值**：

| 值 | 来源 | 可用工具 |
|---|---|---|
| `general-purpose` | 内置（默认） | 全部工具 |
| `Explore` | 内置 | 只读工具（Glob, Grep, Read 等） |
| `Plan` | 内置 | 只读工具 |
| 自定义名称 | `agents/<name>.md` | 由 agent 定义的 `tools` 字段决定 |

---

### 3.10 `hooks` — Skill 级 Hook

```yaml
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: prompt
          prompt: "验证此写入是否符合 Schema 规范"
          timeout: 15
```

**作用**：定义仅在该 Skill 激活时生效的 Hook。与全局 `hooks.json` 互补。

**应用场景**：
- **写入验证**：Skill 产出文件时，自动检查是否符合 Schema
- **安全拦截**：特定 Skill 中禁止某些危险操作
- **审计日志**：记录 Skill 执行过程中的关键操作

---

## 4. 字符串替换变量

Skill 内容（非 frontmatter 部分）中可使用以下动态变量：

### 参数变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `$ARGUMENTS` | 调用时传入的全部参数 | `分析 $ARGUMENTS 的代码结构` |
| `$ARGUMENTS[N]` | 按 0-based 索引访问特定参数 | `$ARGUMENTS[0]` 取第一个参数 |
| `$N` | `$ARGUMENTS[N]` 的简写 | `在 $0 目录中查找 $1 模式` |

**隐式行为**：如果 SKILL.md 内容中未出现 `$ARGUMENTS`，参数会自动追加为 `ARGUMENTS: <value>`。

### 环境变量

| 变量 | 说明 | 典型用法 |
|------|------|---------|
| `${CLAUDE_SESSION_ID}` | 当前会话 ID | 日志关联、会话特定文件命名 |
| `${CLAUDE_SKILL_DIR}` | SKILL.md 所在目录路径 | 引用同目录下的脚本或文件 |

**`${CLAUDE_SKILL_DIR}` 的关键用途**：Plugin 的 Skill 可能被安装到不同位置，用此变量确保路径正确：

```markdown
执行分析脚本：
!`bash ${CLAUDE_SKILL_DIR}/analyze.sh $ARGUMENTS`
```

### 预处理器

`` !`command` `` 语法可在 Skill 加载时执行 shell 命令，并将 stdout 替换到 Skill 内容中：

```markdown
当前项目状态：
!`cat ${CLAUDE_SKILL_DIR}/../../state/project.md`
```

---

## 5. Subagent Fork 深入解析

### 5.1 核心机制

通过 `context: fork` + `agent` 两个字段，Skill 可以在隔离的子 agent 中运行：

```yaml
---
name: deep-research
description: Use when user needs thorough research on a topic
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

### 5.2 运行流程

```
用户触发 /deep-research "认证模块"
         |
         v
[1] 创建隔离子 agent 上下文（不携带主对话历史）
         |
         v
[2] SKILL.md 内容作为子 agent 的 task prompt
    "Research 认证模块 thoroughly: ..."
         |
         v
[3] agent 字段（Explore）决定执行环境
    - System prompt: Explore agent 的内置定义
    - 可用工具: Glob, Grep, Read（只读）
    - 权限: 不可编辑文件
         |
         v
[4] CLAUDE.md 加载到子 agent 上下文（项目规则生效）
         |
         v
[5] 子 agent 自主执行任务
         |
         v
[6] 结果摘要返回主对话
```

### 5.3 agent 可用值详解

#### 内置 agent

| 名称 | 用途 | 工具范围 |
|------|------|---------|
| `general-purpose` | 通用（**默认值**） | 全部工具 |
| `Explore` | 快速代码探索 | 只读（Glob, Grep, Read 等） |
| `Plan` | 架构规划 | 只读 |

#### 自定义 agent

`agents/` 目录下的 `.md` 文件，文件名（不含扩展名）即为 agent 名称：

```
agents/
  my-analyst.md    -> agent: my-analyst
  code-reviewer.md -> agent: code-reviewer
```

自定义 agent 的 frontmatter 支持字段：

| 字段 | 说明 |
|------|------|
| `name` | 必填，agent 名称 |
| `description` | 必填，用途描述 |
| `tools` | 可用工具列表 |
| `disallowedTools` | 禁用工具列表 |
| `model` | 使用的模型 |
| `color` | UI 背景色（blue/cyan/green/yellow/red/magenta） |
| `permissionMode` | 权限模式 |
| `maxTurns` | 最大执行轮数 |
| `skills` | 预加载的 Skill |
| `mcpServers` | 可用的 MCP Server |
| `memory` | 记忆持久化（user/project/local） |
| `hooks` | agent 级 Hook |
| `isolation` | `worktree` = 在独立 git worktree 中运行 |

### 5.4 Skill Fork vs Subagent 委派

两种让 Skill 在子 agent 中运行的方式：

| 维度 | Skill + `context: fork` | Subagent + `skills` 字段 |
|------|------------------------|-------------------------|
| System Prompt | 来自 agent 类型定义 | Subagent 的 markdown body |
| Task | SKILL.md 内容 | Claude 的委派消息 |
| 附加加载 | CLAUDE.md | 预加载 skills + CLAUDE.md |
| 控制权 | **Skill 作者**写好任务 | **Claude** 动态决定任务 |

**选择建议**：

- **Skill + fork**：你明确知道任务内容，写在 SKILL.md 里，选一个合适的 agent 类型来执行
- **Subagent + skills**：你定义 agent 的能力和行为，由 Claude 在主对话中决定何时委派什么任务

### 5.5 注意事项

**必须包含明确任务指令**：`context: fork` 仅适用于包含**具体可执行任务**的 Skill。如果 Skill 内容只是指导原则（如"使用这些 API 规范"）而没有具体任务，子 agent 收到后无可执行操作，会返回空结果。

**上下文隔离**：
- 子 agent **不会**继承主对话的历史消息
- 子 agent **会**加载 CLAUDE.md（项目规则仍然生效）
- 子 agent 的输出以摘要形式返回主对话

---

## 6. 实战组合模式

### 模式 1：常规自动触发

最常见的 Skill 形式。Claude 根据对话上下文自动触发，在主对话上下文中运行。

```yaml
---
description: Use when user says "开始做" or /pace-dev
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---
```

**适用**：日常开发辅助、代码生成、文件操作

### 模式 2：手动触发的危险操作

禁止 Claude 自动触发，必须用户显式调用。

```yaml
---
description: Use when user wants to release
disable-model-invocation: true
allowed-tools: Read, Bash
---
```

**适用**：发布、数据库迁移、破坏性操作

### 模式 3：隔离运行的重量级分析

在独立子 agent 中运行，避免污染主对话上下文。

```yaml
---
description: Use when deep code analysis is needed
context: fork
agent: Explore
---
```

**适用**：代码库探索、架构分析、深度研究

### 模式 4：Claude 内部背景知识

用户不可见，仅 Claude 在需要时自动加载。

```yaml
---
description: API conventions for the project
user-invocable: false
---
```

**适用**：编码规范、API 约定、项目特定知识

### 模式 5：带安全 Hook 的写入

Skill 执行期间自动验证写入操作。

```yaml
---
description: Use when generating schema files
allowed-tools: Read, Write
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write"
      hooks:
        - type: prompt
          prompt: "Check if output matches schema format"
---
```

**适用**：Schema 生成、配置文件写入、需要格式验证的产出

### 模式 6：自定义 agent + fork 的完全控制

使用自定义 agent 精确控制工具、模型和权限。

```yaml
---
description: Use when security audit is needed
context: fork
agent: security-auditor
model: opus
---
```

配套 `agents/security-auditor.md`：

```yaml
---
name: security-auditor
description: Security audit specialist
tools: Read, Glob, Grep, Bash
model: opus
maxTurns: 50
---

You are a security auditor. Analyze code for vulnerabilities...
```

**适用**：安全审计、性能分析、需要专业化 agent 的独立任务
