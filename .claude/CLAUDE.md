# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# devpace — 开发节奏管理器

> **devpace** 是一个 Claude Code 插件，为 AI 辅助开发带来完整的 BizDevOps 研发节奏管理。它将"业务目标→产品功能→代码变更"串成一条可追溯的价值链，让 Claude 不只是写代码的工具，而是理解业务意图的研发协作者。会话中断？自动恢复上下文，无需重复解释。需求变更？即时评估影响范围，有序调整而非推倒重来。质量跑偏？内置门禁自动拦截，未就绪的变更无法流入下游。**需求永远在变，但从规划到交付的研发节奏，不应该因此失控。**

详见 [vision.md](../docs/design/vision.md)。

## 分层架构（硬性要求）

devpace 分为两个独立层次，**产品层不得依赖开发层**：

| 层次 | 目录 | 职责 | 分发 |
|------|------|------|------|
| **开发层** | `.claude/`、`docs/` | 开发 devpace 本身的规范和设计文档 | 不分发 |
| **产品层** | `rules/`、`skills/`、`knowledge/`、`.claude-plugin/` | Plugin 运行时资产，分发给用户 | 随 Plugin 分发 |

**硬性约束**：

1. **产品层独立可分发**：`rules/`、`skills/`、`knowledge/`、`.claude-plugin/` 必须作为独立整体分发，不依赖 `.claude/` 和 `docs/` 中的任何文件
2. **禁止产品→开发引用**：产品层文件（rules/、skills/、knowledge/）中不得出现指向 `docs/` 或 `.claude/` 的路径引用
3. **开发→产品引用允许**：开发层文件（.claude/CLAUDE.md、docs/design.md 等）可以引用产品层文件
4. **共享知识归产品层**：如果一份内容同时被开发和产品使用（如 theory.md），它必须放在产品层（knowledge/），开发层引用它

**检查方法**：`grep -r "docs/\|\.claude/" rules/ skills/ knowledge/` 应返回空结果。

## 开发守则

1. **概念模型始终完整**：BR→PF→CR 价值链从第一天就存在，不可省略任何环节。内容可为空但结构必须完整
2. **Markdown 是唯一格式**：消费者是 LLM + 人类，不使用 YAML/JSON 作为状态文件格式
3. **Schema 是契约**：`knowledge/_schema/` 中的格式定义是强约束，Skill 输出必须符合 Schema
4. **plugin.json 必须与文件系统同步**：新增/删除 Skill 后立即更新 `.claude-plugin/plugin.json`
5. **Rules 是分发规范，不是开发规范**：`rules/devpace-rules.md` 面向 Plugin 用户，开发规范在 `.claude/rules/`
6. **UX 优先**：零摩擦、渐进暴露、副产物非前置、容错恢复（设计原则见 `design.md §2`）
7. **理论对齐**：新增功能或调整概念模型时，对照 `knowledge/theory.md` 确保一致性
8. **规范优先，不猜测**：开发 Claude Code 组件（plugin、skill、agent、hook、MCP 等）时，必须遵循下方"Claude Code 组件开发规范"章节的最佳实践。对不确定的 API、frontmatter 字段或机制行为，通过 `claude-code-guide` agent（`Task(subagent_type="claude-code-guide")`) 或官方文档（`https://code.claude.com/docs/en/`）查证，禁止凭记忆猜测

## Claude Code 组件开发规范

本项目是一个 Claude Code Plugin。以下是基于官方文档（2026-02）的组件开发规范，开发过程中必须遵循。

### Plugin 结构

```
devpace/                        # Plugin 根目录
├── .claude-plugin/plugin.json  # 唯一放在 .claude-plugin/ 内的文件
├── commands/                   # 命令文件（根目录，不在 .claude-plugin/ 内）
├── agents/                     # Agent 定义（根目录）
├── skills/                     # Skill 目录（根目录，自动发现）
├── hooks/                      # Hook 配置
├── rules/                      # Rules 文件（自动加载）
└── .mcp.json                   # MCP Server 配置
```

**关键规则**：只有 `plugin.json` 放在 `.claude-plugin/` 内，其余组件（commands/、agents/、skills/、hooks/）必须在 Plugin 根目录。

### plugin.json

当前采用最小格式，仅含 `name`、`description`、`author`。`name` 是唯一必填字段（当 manifest 存在时），同时作为 Skill 的命名空间前缀（`devpace:pace-init`）。

可选字段（均为合法）：`version`、`homepage`、`repository`（字符串）、`license`、`keywords`、`commands`、`agents`、`skills`、`hooks`、`mcpServers`、`outputStyles`、`lspServers`。其中 `commands/skills/agents/hooks/mcpServers` 用于声明**额外**路径（补充默认目录的自动发现，不替代）。所有路径必须相对且以 `./` 开头。

### SKILL.md Frontmatter

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

**分拆模式**：SKILL.md 放"做什么"（输入/输出/高层步骤），详细规则超 ~50 行时拆出 `*-procedures.md`（"怎么做"）。参考 `pace-advance/` 和 `pace-change/`。

### Agent 定义

Agent 文件放在 `agents/` 目录，frontmatter 必须包含 `name` 和 `description`。

**合法 frontmatter 字段**：`name`（必填）、`description`（必填）、`tools`、`disallowedTools`、`model`、`permissionMode`、`maxTurns`、`skills`、`mcpServers`、`memory`、`hooks`。

通过 Task 工具调用：`Task(subagent_type="agent-name", prompt="...", description="...")`。子 agent 不能再嵌套调用 Task。

### Hooks

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

### MCP Server 配置

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

### 常见陷阱

| 问题 | 原因 | 解决 |
|------|------|------|
| 组件放在 `.claude-plugin/` 内 | 只有 plugin.json 在此目录 | 移到 Plugin 根目录 |
| Command frontmatter 含 `name` | Command 名由文件名决定 | 删除 `name`（SKILL.md 中合法） |
| Skill 不触发 | `description` 过于模糊 | 写明具体触发关键词 |
| Hook 不执行 | 脚本无执行权限或缺 shebang | `chmod +x` + `#!/bin/bash` |
| Hook 事件名大小写错误 | 事件名区分大小写 | `PostToolUse` 而非 `postToolUse` |
| Plugin 路径用绝对路径 | 必须相对且以 `./` 开头 | 改为相对路径 |
| MCP 环境变量不展开 | 语法错误 | 使用 `${VAR}` 或 `${VAR:-default}` |

### 规范查证方法

不确定时，按优先级查证：

1. `Task(subagent_type="claude-code-guide", prompt="查询 [具体问题]")`——内置 agent，可访问官方文档
2. 官方文档：`https://code.claude.com/docs/en/`（plugins、skills、hooks、mcp、sub-agents、agent-teams）
3. `claude --debug` 查看加载日志排查问题

## 目录结构

```
devpace/
├── .claude/                    # 开发层：开发 devpace 本身的规范
│   ├── CLAUDE.md               # 本文件
│   ├── settings.local.json     # 本地 Claude 设置（git 预提交权限等）
│   └── rules/
│       ├── common.md           # 语言、Git、命名规范
│       └── dev-workflow.md     # 开发会话协议、任务流程、文档级联
├── .claude-plugin/plugin.json  # Plugin 入口声明
├── docs/                       # 开发层：项目文档（不随 Plugin 分发）
│   ├── design/
│   │   ├── vision.md           # 北极星、OBJ、MoS
│   │   └── design.md           # 完整设计方案
│   └── planning/
│       ├── requirements.md     # 需求场景 S1-S9、功能需求 F1-F3
│       ├── roadmap.md          # 战略规划：阶段、里程碑
│       └── progress.md         # 操作跟踪：当前任务、会话历史、变更记录
├── knowledge/                  # 产品层：运行时知识
│   ├── _schema/                #   格式契约（cr-format/project-format/state-format）
│   ├── metrics.md              #   度量指标定义
│   └── theory.md               #   BizDevOps 理论（/pace-guide 运行时数据源）
├── rules/devpace-rules.md      # 产品层：运行时行为协议
├── skills/                     # 产品层：7 个 Slash Commands
│   ├── pace-init/              #   含 templates/（8 个模板文件）
│   ├── pace-advance/           #   含 advance-procedures.md
│   ├── pace-change/            #   含 change-procedure.md
│   ├── pace-guide/
│   ├── pace-retro/
│   ├── pace-review/
│   └── pace-status/
├── tests/                      # 开发层：测试体系（不随 Plugin 分发）
│   ├── conftest.py             #   共享 fixtures 和常量
│   ├── static/                 #   Tier 1: 9 个 pytest 静态检查模块
│   ├── integration/            #   Tier 2: Plugin 加载验证脚本
│   ├── scenarios/              #   Tier 3: Claude-in-the-loop 行为场景
│   └── evaluation/             #   Tier 4: 验收矩阵和评分表
├── scripts/                    # 开发层：验证工具
│   └── validate-all.sh         #   编排器：运行全部静态检查
└── pytest.ini                  # pytest 配置
```

## 开发验证

```bash
# 自动化静态检查（首选——覆盖分层、plugin.json、frontmatter、schema、模板、命名、状态机等）
pytest tests/static/ -v

# 编排脚本（静态 + 分层 grep + 集成测试）
bash scripts/validate-all.sh

# 加载 Plugin 测试
claude --plugin-dir ./

# 在目标项目中集成测试
cd /Users/jinhuasu/Project_Workspace/Anker-Projects/diagnostic-agent-framework
claude --plugin-dir ../ml-platform-research/llm-platform-solution/claude-code-forge/devpace

# 分层完整性检查（产品层不得引用开发层——已被 test_layer_separation.py 自动化）
grep -r "docs/\|\.claude/" rules/ skills/ knowledge/
# 期望：无输出

# 集成测试（需 Claude CLI）
bash tests/integration/test_plugin_loading.sh

# 调试 Plugin 加载问题
claude --plugin-dir ./ --debug
```

## 会话协议

详见 `.claude/rules/dev-workflow.md`（自动加载）。速查版：

1. **开始**：读 `progress.md` 快照 + 当前任务 → 检测上游文档变更 → 1 句话报告 → 等指令
2. **执行**：追溯关联链加载参考 → 实现 → 质量检查 → 更新 progress
3. **变更**：发现上游变更 → §8 级联处理 → 影响分析 → 级联更新 → 记录
4. **结束**：更新 `progress.md`（快照 + 任务状态 + 会话记录 + 变更记录）→ 3 行摘要
5. **恢复**：progress.md = 唯一恢复点（快照 → 当前任务 → 近期会话）

## 权威文件索引

| 概念 | 权威文件 | 权威范围 |
|------|---------|---------|
| 北极星、OBJ、MoS | `docs/design/vision.md` | 为什么做、做什么 |
| UX 原则（P1-P7） | `docs/design/design.md §2` | 设计约束 |
| 概念模型映射 | `docs/design/design.md §3` | 价值交付链路、闭环、渐进丰富 |
| 端到端工作流（Phase 0-5） | `docs/design/design.md §4` | 完整流程、Skill 映射 |
| CR 状态机 | `docs/design/design.md §5` | 状态、转换、门禁完整定义 |
| 质量门系统 | `docs/design/design.md §6` | Gate 1/2/3 定义 |
| 变更管理 | `docs/design/design.md §7` | 设计原则、四种场景、操作流程 |
| BizDevOps 理论 | `knowledge/theory.md` | 方法论参考（/pace-guide 运行时数据源） |
| 需求场景 S1-S9 | `docs/planning/requirements.md` | 验收标准 |
| 功能需求 F1-F3 | `docs/planning/requirements.md` | 特性规格 |
| 战略规划 | `docs/planning/roadmap.md` | 阶段、里程碑、任务定义 |
| 操作跟踪 | `docs/planning/progress.md` | 当前任务状态、会话历史、变更记录 |
| 运行时行为规则 | `rules/devpace-rules.md` | 插件加载后 Claude 的行为 |
| 文件格式契约 | `knowledge/_schema/*.md` | state/project/CR 的字段定义 |
| 度量指标定义 | `knowledge/metrics.md` | 指标名称、计算方式、用途 |

### 开发规范索引（.claude/rules/，自动加载）

| 规范文件 | 职责 |
|---------|------|
| `common.md` | 响应语言、Git 提交规范、文档命名 |
| `dev-workflow.md` | 开发会话协议、任务执行、质量检查、跨会话连续性、文档级联 |

## 质量检查

- plugin.json 与文件系统同步（新增/删除 Skill 后立即更新）
- 每个 rules/ 和 _schema/ 文件有 §0 速查卡片
- 模板文件用 `{{PLACEHOLDER}}` 标记需填充的内容
- Skill 的 SKILL.md 遵循本文件"Claude Code 组件开发规范"章节的 frontmatter 字段定义
- Skill 分拆模式：SKILL.md 放输入/输出/高层步骤（"做什么"），当详细规则超过 ~50 行时拆出 `*-procedures.md`（"怎么做"）。参考 pace-advance 和 pace-change
- **分层完整性**：产品层文件不得引用 `docs/` 或 `.claude/`（见分层架构章节）
