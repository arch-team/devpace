# Claude Code 组件参考

> **职责**：Claude Code 平台级组件 API 参考（Plugin / Skill / Agent / Hook / MCP）。按需加载。
>
> devpace 编写约定见 `plugin-dev-spec.md`（始终加载）。devpace 项目级映射见 `references/product-arch-details.md`。

**章节索引**：[Plugin 结构](#plugin-结构) | [plugin.json](#pluginjson) | [SKILL.md Frontmatter](#skillmd-frontmatter) | [Agent 定义](#agent-定义) | [Hooks](#hooks) | [MCP Server 配置](#mcp-server-配置) | [常见陷阱](#常见陷阱) | [官方 plugin-dev 工具](#官方-plugin-dev-工具推荐)

## Plugin 结构

```
<plugin-name>/
├── .claude-plugin/
├── commands/
├── agents/
├── skills/
├── hooks/
├── rules/
├── output-styles/
├── settings.json
└── .mcp.json
```

## plugin.json

`name` 是唯一必填字段（当 manifest 存在时），同时作为 Skill 的命名空间前缀（如 `devpace:pace-init`）。

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

**字符串替换**：Skill 内容中可使用 `$ARGUMENTS`（全部参数）、`$0`/`$1`（按位参数）、`` !`command` ``（预处理器，执行 shell 命令并替换输出）。

## Agent 定义

Agent 文件放在 `agents/` 目录，frontmatter 必须包含 `name` 和 `description`。

**合法 frontmatter 字段**：

| 字段 | 说明 |
|------|------|
| `name` | **必填**，Agent 名称 |
| `description` | **必填**，Agent 描述 |
| `tools` | 允许的工具列表 |
| `disallowedTools` | 禁止的工具列表 |
| `model` | `sonnet` / `opus` / `haiku` |
| `color` | UI 背景色（`blue`/`cyan`/`green`/`yellow`/`red`/`magenta`） |
| `permissionMode` | 权限模式 |
| `maxTurns` | 最大轮次 |
| `skills` | 可用 Skill 列表 |
| `mcpServers` | 可用 MCP Server |
| `memory` | 记忆持久化级别（见下方备注） |
| `hooks` | Agent 级 Hook 配置 |
| `isolation` | `worktree` = 独立 git worktree 运行 |

`memory` 持久化路径：`user` → `~/.claude/agent-memory/<name>/`，`project` → `.claude/agent-memory/<name>/`，`local` → 仅当前会话。下次 fork 时自动加载。`isolation: worktree` 时无变更自动清理。

通过 Task 工具调用：`Task(subagent_type="agent-name", prompt="...", description="...")`。子 agent 不能再嵌套调用 Task。

## Hooks

Hook 事件名称区分大小写。可用事件：

| 事件 | 触发时机 | 可阻断? |
|------|---------|---------|
| `PreToolUse` | 工具执行前 | 是（exit 2） |
| `PostToolUse` | 工具执行成功后 | 否 |
| `PostToolUseFailure` | 工具执行失败后 | 否 |
| `UserPromptSubmit` | 用户提交 prompt | 是 |
| `PreCompact` | 上下文压缩前（manual/auto） | 否 |
| `Stop` | Claude 完成响应 | 是 |
| `SessionStart` / `SessionEnd` | 会话开始/结束 | 否 |
| `SubagentStart` / `SubagentStop` | 子 agent 启停 | 部分 |
| `TeammateIdle` / `TaskCompleted` | 团队协作事件 | 是（exit 2） |

配置位置（优先级从高到低）：

1. managed settings
2. `.claude/settings.json`（项目共享）
3. `.claude/settings.local.json`（项目本地）
4. `~/.claude/settings.json`（全局）
5. Plugin `hooks/hooks.json`

Hook 脚本中使用 `${CLAUDE_PLUGIN_ROOT}` 引用 Plugin 根目录。exit 0 = 成功，exit 2 = 阻断，其他 = 非阻断错误。

### Hook 类型

| 类型 | 说明 | 超时默认 |
|------|------|---------|
| `command` | 执行 shell 命令，通过 stdin 接收 JSON 输入 | 无默认 |
| `prompt` | LLM 评估 prompt 内容，决定是否放行 | 30s |
| `agent` | LLM agent 执行（有工具访问权限），决定是否放行 | 60s |

`command` 类型额外支持 `"async": true`（后台执行，不阻塞主流程）。`prompt`/`agent` 类型具有语义理解能力，适合替代简单的正则匹配做复杂判断。

### Skill 级 Hooks

SKILL.md 的 `hooks` frontmatter 字段支持定义仅在该 Skill 激活时生效的 Hook：

```yaml
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: prompt
          prompt: "验证此写入是否合法..."
          timeout: 15
```

Skill 级 Hook 与全局 hooks.json 互补——全局做通用检查，Skill 级做精细控制。devpace 当前 Skill 级 Hook 配置见 `references/product-arch-details.md` §B。

### 约束执行分级

选择约束的执行保障级别时参考：

| 可靠性 | 机制 | 适用场景 |
|--------|------|---------|
| 最高 | Hook command + exit 2 | 不可逆操作阻断、模式保护 |
| 高 | Hook prompt/agent | 需语义理解的检查 |
| 中 | Skill 指令 + 铁律标记 | 工作流约束 |
| 基线 | Rules 文本建议 | 行为规范、风格指引 |

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

## 官方 plugin-dev 工具（推荐）

查证优先级见 `plugin-dev-spec.md` §0。Anthropic 官方 plugin-dev Plugin 提供综合开发工具：

| 组件 | 用途 | 使用场景 |
|------|------|---------|
| **plugin-validator** Agent | 10 步综合验证（Manifest/目录/Skills/Hooks/安全） | 任何 Plugin 结构变更后 |
| **skill-reviewer** Agent | Skill 质量审查（description/内容/渐进披露） | Skill 新增或修改后 |
| **agent-creator** Agent | AI 辅助 Agent 创建 | 新增 Agent 定义时 |
| `/plugin validate` | 内置命令，验证 plugin.json 基本结构 | 快速检查 |

安装：`/plugin install plugin-dev@claude-plugins-official`
