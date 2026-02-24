---
description: Use when user asks "why did devpace decide X", "追溯", "为什么这样做", "决策记录", "决策原因", wants to see AI decision trail, or says /pace-trace [CR] [gate/decision]
allowed-tools: Read, Glob, Grep
argument-hint: "[CR 名称或编号] [gate1 质量检查|gate2 集成验证|gate3 审批摘要|intent 意图推断|change 变更影响|autonomy 自主决策]"
model: haiku
---

# /pace-trace — 决策轨迹查询

> 三层渐进透明的深入层。提供完整的 AI 决策轨迹，让用户可审计 Claude 的每个系统判断。

## 输入

- `$ARGUMENTS`：可选——CR 名称/编号 + 决策类型
- 无参数时：展示当前/最近 CR 的最新决策轨迹

## 流程

### 决策类型

| 类型 | 查询内容 |
|------|---------|
| `gate1` | Gate 1 质量检查的完整判定过程 |
| `gate2` | Gate 2 集成验证 + 验收比对的完整判定过程 |
| `gate3` | Gate 3 审批前的摘要生成过程 |
| `intent` | 意图检查点的推断过程（含溯源标记） |
| `change` | 变更影响分析的推理过程 |
| `risk` | 风险评估的判断依据 |
| 无指定 | 展示 CR 最近一次重要决策的轨迹 |

详细输出格式、执行步骤和约束规则见 `trace-procedures.md`。

## 输出

格式化的决策轨迹（含上下文、规则匹配、检查结果、溯源信息、综合判定）。
