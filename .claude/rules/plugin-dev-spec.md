# Claude Code 组件开发规范

> **职责**：开发 devpace Plugin 时 Claude 必须遵循的组件规范。基于官方文档（2026-02）。

本项目是一个 Claude Code Plugin。以下是组件开发规范，开发过程中必须遵循。

## Plugin 结构

```
devpace/                        # Plugin 根目录
├── .claude-plugin/             # plugin.json + marketplace.json
├── commands/                   # 命令文件（根目录，不在 .claude-plugin/ 内）
├── agents/                     # Agent 定义（根目录）
├── skills/                     # Skill 目录（根目录，自动发现）
├── hooks/                      # Hook 配置
├── rules/                      # Rules 文件（自动加载）
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

**分拆模式**：SKILL.md 放"做什么"（输入/输出/高层步骤），详细规则超 ~50 行时拆出 `*-procedures.md`（"怎么做"）。参考 `pace-dev/` 和 `pace-change/`。

## Agent 定义

Agent 文件放在 `agents/` 目录，frontmatter 必须包含 `name` 和 `description`。

**合法 frontmatter 字段**：`name`（必填）、`description`（必填）、`tools`、`disallowedTools`、`model`、`permissionMode`、`maxTurns`、`skills`、`mcpServers`、`memory`、`hooks`。

通过 Task 工具调用：`Task(subagent_type="agent-name", prompt="...", description="...")`。子 agent 不能再嵌套调用 Task。

## Hooks

Hook 事件名称区分大小写。可用事件：

| 事件 | 触发时机 | 可阻断? |
|------|---------|---------|
| `PreToolUse` | 工具执行前 | 是（exit 2） |
| `PostToolUse` | 工具执行成功后 | 否 |
| `UserPromptSubmit` | 用户提交 prompt | 是 |
| `Stop` | Claude 完成响应 | 是 |
| `SessionStart` / `SessionEnd` | 会话开始/结束 | 否 |
| `SubagentStart` / `SubagentStop` | 子 agent 启停 | 部分 |
| `TeammateIdle` / `TaskCompleted` | 团队协作事件 | 是（exit 2） |

配置位置（按优先级）：managed settings → `.claude/settings.json`（项目共享）→ `.claude/settings.local.json`（项目本地）→ `~/.claude/settings.json`（全局）→ Plugin `hooks/hooks.json`。

Hook 脚本中使用 `${CLAUDE_PLUGIN_ROOT}` 引用 Plugin 根目录。exit 0 = 成功，exit 2 = 阻断，其他 = 非阻断错误。

## MCP Server 配置

项目级配置放在根目录 `.mcp.json`，格式：

```json
{
  "mcpServers": {
    "server-name": {
      "command": "path/to/server",
      "args": ["--flag"],
      "env": { "KEY": "${ENV_VAR}", "KEY2": "${VAR:-default}" }
    }
  }
}
```

Plugin 内部引用路径时使用 `${CLAUDE_PLUGIN_ROOT}`。也可在 `plugin.json` 的 `mcpServers` 字段内联定义。

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

## 规范查证方法

不确定时，按优先级查证：

1. `Task(subagent_type="claude-code-guide", prompt="查询 [具体问题]")`——内置 agent，可访问官方文档
2. 官方文档：`https://code.claude.com/docs/en/`（plugins、skills、hooks、mcp、sub-agents、agent-teams）
3. `claude --debug` 查看加载日志排查问题
