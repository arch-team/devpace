# Gate 决策轨迹查询执行规程

> **职责**：pace-trace `gate1`/`gate2`/`gate3` 子命令的类型特定规则。通用规则（输出格式框架、confidence 表、降级处理、执行步骤、规则）见 `trace-procedures-common.md`。

## §0 速查卡片

- **本文件覆盖**：Gate 类型输出要点 · Gate 导航建议表
- **通用规则**（输出格式、confidence、降级、步骤、规则）→ `trace-procedures-common.md`

## Gate 类型输出要点

- **gate1/gate2/gate3**：完整三段结构，"评估过程"以"逐项检查"为标题
- 检查项以编号列表呈现：`1. [检查项] — [通过/失败] ([具体数据])`
- "规则匹配"section 展示 checks.md 中匹配的质量规则及其应用

## 上下文导航（输出末尾）

| 决策类型 | 导航建议 |
|---------|---------|
| gate1 | → 经验模式：/pace-learn list · 质量趋势：/pace-retro quality |
| gate2 | → 经验模式：/pace-learn list · 质量趋势：/pace-retro quality |
| gate3 | → 审批历史：/pace-status detail · 经验模式：/pace-learn list |

导航建议用 `→` 前缀，跟在输出最后一行之后。
