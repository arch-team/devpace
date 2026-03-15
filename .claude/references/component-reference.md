# Claude Code 组件参考

> **职责**：Agent、Hook、MCP Server 的完整规格参考。按需加载，仅在开发/修改对应组件时使用。
>
> 核心开发规范见 `.claude/rules/plugin-dev-spec.md`（始终加载）。

**章节索引**：[Agent 定义](#agent-定义) | [Hooks](#hooks) | [MCP Server 配置](#mcp-server-配置) | [规范查证方法](#规范查证方法)

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

Skill 级 Hook 与全局 hooks.json 互补——全局做通用检查，Skill 级做精细控制。

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

## 规范查证方法

不确定时，按优先级查证：

1. `Task(subagent_type="claude-code-guide", prompt="查询 [具体问题]")`——内置 agent，可访问官方文档
2. 官方文档：`https://code.claude.com/docs/en/`（plugins、skills、hooks、mcp、sub-agents、agent-teams）
3. `claude --debug` 查看加载日志排查问题

### 官方 plugin-dev 工具（推荐）

Anthropic 官方 plugin-dev Plugin 提供综合开发工具。安装后可用于 devpace 开发验证：

| 组件 | 用途 | 使用场景 |
|------|------|---------|
| **plugin-validator** Agent | 10 步综合验证（Manifest/目录/Skills/Hooks/安全） | 任何 Plugin 结构变更后 |
| **skill-reviewer** Agent | Skill 质量审查（description/内容/渐进披露） | Skill 新增或修改后 |
| **agent-creator** Agent | AI 辅助 Agent 创建 | 新增 Agent 定义时 |
| `/plugin validate` | 内置命令，验证 plugin.json 基本结构 | 快速检查 |

安装：`/plugin install plugin-dev@claude-plugins-official`
