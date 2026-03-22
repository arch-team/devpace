# Harness Engineering 开发原则

> **职责**：devpace 作为 Claude Code Harness 的工程原则——指导如何设计、调试和维护 Agent 工作环境。与 `ia-principles-details.md`（信息组织）和 `product-architecture.md`（组件协作）互补——本文件回答"为什么这样设计 Harness 组件，以及 Agent 视角下的质量标准"。

## §0 速查卡片

**核心公式**：`Agent 产出质量 = 模型能力 × 环境质量`——模型能力是商品，环境（Harness）才是差异化资产。

| # | 原则 | 一句话 |
|---|------|--------|
| HE-1 | 环境优先调试 | Agent 表现不佳 → 修环境，不怪模型 |
| HE-2 | 规则是乘数 | 编码一条规则 = 在所有未来执行中同时应用 |
| HE-3 | Agent Legibility | 所有组件以"Agent 能否高效理解并正确执行"为标准 |
| HE-4 | Hook 输出即修复指令 | 错误消息 = Agent 可直接执行的修复步骤 |
| HE-5 | 仓库知识是记录系统 | `.devpace/` + 仓库 Markdown = 唯一真相源 |
| HE-6 | 对抗熵增 | Agent 会复制次优模式，需主动维护节奏 |

## §1 核心思维模型

### HE-1 环境优先调试

当 Claude 在某个 Skill 中表现不佳时，按以下顺序排查：

1. **description** 是否导致误触发/漏触发
2. **procedures** 是否有歧义条件分支或缺失步骤
3. **Schema** 是否遗漏字段或约束不足
4. **rules** 是否有冲突或覆盖不足
5. **Hook 输出** 是否对 Agent 不透明

**预防合理化**：`"模型能力不够" → 99% 的情况是上下文或约束缺失。先穷尽环境排查，再考虑模型局限。`

### HE-2 规则是乘数

- 反复出现的质量问题 → 优先编码为 Hook/Rules/Schema 约束，而非每次手动检查
- 品味级别的偏好也值得编码（命名风格、输出格式、章节顺序）

| 场景 | 正确（编码为规则） | 错误（手动重复） |
|------|-------------------|-----------------|
| 命名风格偏差反复出现 | Schema 字段命名规范 + validate-all 检测 | 每次 review 口头提醒 |
| Hook 消息缺修复指令 | HE-4 格式标准 + grep 检测命令 | 发现一次修一次 |

**预防合理化**：`"这个问题太特殊不值得编码" → 出现 2 次就不特殊。编码成本 < 手动检查的 N 次累积`

### HE-3 Agent Legibility

| 组件 | 正确（Agent-legible） | 错误（仅人类可读） |
|------|---------------------|-------------------|
| description | `Use when user says "开始做/实现" or /pace-dev` | `Handles development workflow tasks` |
| procedures | `1. 读 .devpace/…CR-NNN.md → 2. 若 status=created → gate 检查 → 3. 否则→报错` | `在适当时机执行必要的质量检查` |
| Schema 字段 | `blocked_reason: string, required when status=paused` | `reason: string` |
| Hook 输出 | `devpace:tag 状态描述。ACTION: 步骤 1；步骤 2` | `Error: Invalid state` |
| Rules | `禁止 X。预防合理化："因为 Y" → Z` | `尽量避免 X` |

**预防合理化**：`"人类也要看，Agent 优先太极端" → Agent 可读性是人类可读性的超集——无歧义步骤、完整条件分支对人类同样有益`

## §2 组件设计标准

### HE-4 Hook 输出即修复指令

Hook 错误消息必须设计为 Claude 可直接理解并执行修复的指令。

**格式模板**：`devpace:<标签> <当前状态描述>。ACTION: <步骤 1>；<步骤 2>；<替代路径>。`

| 正确 | 错误 |
|------|------|
| `devpace:gate CR-007 状态为 created，尚未通过 Gate 1。ACTION: 运行 /pace-dev gate 完成 Gate 1 检查；或确认 CR 已有足够测试覆盖。` | `Error: Invalid state transition` |

**编写规则**：

1. 说明**当前状态**（什么不满足）
2. 给出**修复动作**（运行什么命令或修改什么文件）
3. 提供**替代路径**（如有多种修复方式）

**预防合理化**：`"Hook 只是内部工具不需要精细消息" → Hook 输出是 Agent 的唯一反馈源。消息模糊 = Agent 下一步随机`

### Procedures 可执行性

| 规则 | 正确 | 错误 |
|------|------|------|
| 步骤可直接执行 | `1. 读 .devpace/backlog/CR-NNN.md 提取 status 字段` | `检查 CR 状态` |
| 条件分支完整 | `若 status=developing → A；若 paused → B；其他 → 报错` | `在必要时检查状态` |
| 引用 Schema 不内联 | `格式见 _schema/entity/cr-format.md §验收条件` | 内联格式定义（双源头） |

### Schema 字段设计

| 规则 | 正确 | 错误 |
|------|------|------|
| 字段名自解释 | `acceptance_criteria`、`blocked_reason` | `ac`、`reason` |
| 必填/可选标注 | `required when status=paused`、`optional, defaults to []` | 无标注 |
| 示例值有代表性 | 典型值 + 边界值（空数组 `[]`、空串 `""`） | `"示例"` |

## §3 仓库知识治理

### HE-5 仓库知识是记录系统

- 信息只存在于人脑或对话中 → 必须持久化到 `.devpace/` 或仓库 Markdown
- 决策、状态、上下文全部记录在仓库中（ADR、变更记录、state.md）

**预防合理化**：`"决策太小不需要记录" → ADR 不是审批文档，是给下一个 Agent 会话的上下文恢复点。2 行 ADR 胜过下次 50 行重新推理`

### HE-6 对抗熵增

**维护节奏**（补充 `dev-workflow.md` §4 的被动触发机制）：

| 时机 | 检查内容 | 命令 |
|------|---------|------|
| 里程碑完成时 | Schema 一致性、procedures 与实际行为对齐、rules 指针引用有效性 | `bash dev-scripts/validate-all.sh` |
| 发现重复模式时 | 提取到 `_guides/` 共享，而非在多个 procedures 中各自维护 | — |
| 会话开始时 | 若距上次维护超过 5 个里程碑，执行全量验证 | `bash dev-scripts/validate-all.sh` |

**预防合理化**：`"刚改完不需要检查" → 熵增在每次变更后发生。刚改完正是最需要验证的时刻`

## §4 Harness 质量检测

可执行检测命令汇总——新建或修改 Harness 组件后运行：

| 检查项 | 命令 | 期望 |
|--------|------|------|
| Hook 输出含修复指令 | `grep -rn 'console\.\(log\|error\)' hooks/ --include="*.mjs" \| grep -v "ACTION:\|lib/"` | 空 |
| Procedures 无歧义措辞 | `grep -rn "自行判断\|酌情\|适当时" skills/ --include="*-procedures*.md"` | 空 |
| Schema 字段名非缩写 | `grep -rn "^| [a-z]\{1,3\} |" knowledge/_schema/ --include="*.md"` | 空 |
| 全量 Harness 验证 | `bash dev-scripts/validate-all.sh` | 0 failures |
