# Claude Code 组件开发规范

> **职责**：开发 devpace Plugin 时 Claude 必须遵循的组件规范。基于官方文档。

本项目是一个 Claude Code Plugin。以下是组件开发规范，开发过程中必须遵循。

## §0 速查卡片

### Plugin 目录规则

| 位置 | 内容 | 注意 |
|------|------|------|
| `.claude-plugin/` | 仅 `plugin.json` + `marketplace.json` | 组件不放这里 |
| Plugin 根目录 | `commands/`、`agents/`、`skills/`、`hooks/`、`rules/` | 所有组件在此 |

### SKILL.md 关键字段

| 字段 | 用途 | 常见错误 |
|------|------|---------|
| `description` | 触发条件（When），不写行为（What） | 写成行为摘要导致跳过读 SKILL.md |
| `allowed-tools` | 免确认工具，逗号分隔 | — |
| `disable-model-invocation` | `true` = 仅用户可调用 | — |
| `context` | `fork` = 子 agent 运行 | — |

### 分拆模式

SKILL.md 放"做什么"（输入/输出/路由），详细规则超 ~50 行拆出 `*-procedures.md`（"怎么做"）。参考 `pace-dev/` 和 `pace-change/`。

### 查证优先级

1. `claude-code-guide` agent → 2. 官方文档 `code.claude.com/docs/en/` → 3. `claude --debug`

### 组件参考

Agent / Hook / MCP 详细规格 → `.claude/references/component-reference.md`（按需加载）

## Plugin 结构

```
devpace/                        # Plugin 根目录
├── .claude-plugin/             # plugin.json + marketplace.json
├── commands/                   # 命令文件（根目录，不在 .claude-plugin/ 内）
├── agents/                     # Agent 定义（根目录）
├── skills/                     # Skill 目录（根目录，自动发现）
├── hooks/                      # Hook 配置
├── rules/                      # Rules 文件（自动加载）
├── output-styles/              # 输出风格定义（plugin.json outputStyles 声明）
├── settings.json               # Plugin 默认配置（Agent 设置等）
└── .mcp.json                   # MCP Server 配置
```

**关键规则**：只有 `plugin.json` 和 `marketplace.json` 放在 `.claude-plugin/` 内，其余组件（commands/、agents/、skills/、hooks/）必须在 Plugin 根目录。

## plugin.json

当前采用最小格式，仅含 `name`、`description`、`author`。`name` 是唯一必填字段（当 manifest 存在时），同时作为 Skill 的命名空间前缀（`devpace:pace-init`）。

可选字段（均为合法）：`version`、`homepage`、`repository`（字符串）、`license`、`keywords`、`commands`、`agents`、`skills`、`hooks`、`mcpServers`、`outputStyles`、`lspServers`。其中 `commands/skills/agents/hooks/mcpServers` 用于声明**额外**路径（补充默认目录的自动发现，不替代）。所有路径必须相对且以 `./` 开头。

## SKILL.md Frontmatter

每个 Skill 是 `skills/<name>/SKILL.md`。目录名即 Skill 名称。

**合法 frontmatter 字段**：

| 字段 | 说明 |
|------|------|
| `name` | 显示名称（可选，省略则用目录名） |
| `description` | 触发条件描述——Claude 据此判断是否自动调用 |
| `argument-hint` | 自动补全时的参数提示（如 `[CR编号]`） |
| `allowed-tools` | 激活时免确认的工具，逗号分隔 |
| `model` | `sonnet` / `opus` / `haiku` |
| `disable-model-invocation` | `true` = 仅用户可调用，Claude 不会自动调用 |
| `user-invocable` | `false` = 从 `/` 菜单隐藏，仅 Claude 可调用 |
| `context` | `fork` = 在子 agent 上下文中运行 |
| `agent` | 当 `context: fork` 时使用的 agent 类型 |
| `hooks` | 作用域为此 Skill 的 Hook 配置 |

### description 编写规则（CSO）

`description` 是 Claude 判断是否自动触发 Skill 的唯一依据。编写不当会导致两类问题：

**问题 1：Claude 跳过阅读完整 SKILL.md**——如果 description 中总结了工作流步骤，Claude 可能根据摘要直接行动而不加载完整 Skill 内容。

**问题 2：误触发或漏触发**——description 过于模糊（"管理变更"）或过于具体（"当用户说'不做了'时"）都会影响准确性。

**编写规则**：

| 规则 | 正确 | 错误 |
|------|------|------|
| 只写"何时触发"，不写"做什么" | `Use when user wants to track requirement changes or says "不做了/加一个/先不搞"` | `Analyzes impact, creates triage report, and updates CR status` |
| 开头用 "Use when" 或触发条件列表 | `Use when entering development mode for a CR` | `Development mode skill for CR lifecycle management` |
| 包含具体触发关键词 | `Use when user says "开始做/帮我改/实现/修复" or /pace-dev` | `Handles code implementation tasks` |
| 避免描述内部步骤 | `Use when CR needs quality review before human approval` | `Runs Gate 2 checks, generates diff summary, compares acceptance criteria` |

**字符串替换**：Skill 内容中可使用 `$ARGUMENTS`（全部参数）、`$0`/`$1`（按位参数）、`` !`command` ``（预处理器，执行 shell 命令并替换输出）。

### SKILL.md 章节顺序规范

标准章节顺序如下（可选章节仅在需要时出现）：

```
# /pace-xxx — 标题
[1-2 行用途说明]

## 与现有机制的关系    ← 可选，仅当需要区分相似 Skill 时
## 推荐使用流程        ← 可选，仅当子命令有推荐组合路径时
## 输入
## 流程
## 输出
```

## 常见陷阱

| 问题 | 原因 | 解决 |
|------|------|------|
| 组件放在 `.claude-plugin/` 内 | 只有 plugin.json 和 marketplace.json 在此目录 | 移到 Plugin 根目录 |
| Command frontmatter 含 `name` | Command 名由文件名决定 | 删除 `name`（SKILL.md 中合法） |
| Skill 不触发 | `description` 过于模糊 | 写明具体触发关键词 |
| Hook 不执行 | 脚本无执行权限或缺 shebang | `chmod +x` + `#!/bin/bash` |
| Hook 事件名大小写错误 | 事件名区分大小写 | `PostToolUse` 而非 `postToolUse` |
| Plugin 路径用绝对路径 | 必须相对且以 `./` 开头 | 改为相对路径 |
| MCP 环境变量不展开 | 语法错误 | 使用 `${VAR}` 或 `${VAR:-default}` |

## skill-creator 集成约定

详见 `.claude/references/skill-creator-integration.md`（按需参考，仅在创建/评估 Skill 时使用）。
