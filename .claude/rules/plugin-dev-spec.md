# devpace Plugin 开发约定

> **职责**：devpace 特有的 Plugin 编写约定。Claude Code 平台 API 参考见 `references/component-reference.md`（按需加载）。

## §0 速查卡片

### Plugin 目录规则

目录结构与文件放置 → `project-structure.md` §0。核心提醒：组件不放 `.claude-plugin/`（仅 plugin.json + marketplace.json）。

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

Plugin 结构 / Frontmatter 字段 / Agent / Hook / MCP / 常见陷阱 → `references/component-reference.md`（按需加载）

## description 编写规则（CSO）

`description` 是 Claude 判断是否自动触发 Skill 的**唯一依据**——写错会导致跳过读 SKILL.md 或误触发/漏触发。

| 规则 | 正确 | 错误 |
|------|------|------|
| 用 "Use when" 开头，只写触发条件，不写行为 | `Use when user wants to track requirement changes or says "不做了/加一个/先不搞"` | `Analyzes impact, creates triage report, and updates CR status` |
| 包含具体触发关键词 | `Use when user says "开始做/帮我改/实现/修复" or /pace-dev` | `Handles code implementation tasks` |
| 避免描述内部步骤 | `Use when CR needs quality review before human approval` | `Runs Gate 2 checks, generates diff summary, compares acceptance criteria` |

## SKILL.md 章节顺序规范

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

## skill-creator 集成约定

详见 `.claude/references/skill-creator-integration.md`（按需参考，仅在创建/评估 Skill 时使用）。
