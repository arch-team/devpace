---
description: Use when user asks "why did devpace decide X", "追溯", "为什么这样做", "决策记录", "决策原因", wants to see AI decision trail, or says /pace-trace [CR] [gate/decision]
allowed-tools: Read, Glob, Grep
argument-hint: "[CR 名称或编号] [gate1 质量检查|gate2 集成验证|gate3 审批摘要|intent 意图推断|change 变更影响|risk 风险评估|autonomy 自主决策|timeline 决策时间线]"
model: haiku
---

# /pace-trace — 决策轨迹查询

> 三层渐进透明的深入层。提供完整的 AI 决策轨迹，让用户可审计 Claude 的每个系统判断。

## 与相关功能的区别

| 功能 | 回答的问题 | 数据维度 |
|------|-----------|---------|
| `/pace-trace [CR] [type]` | "Claude 为什么这样判断？" | 单个决策的审计轨迹 |
| `/pace-trace [CR] timeline` | "这个 CR 经历了什么？" | CR 全生命周期决策时间线 |
| `/pace-status trace <name>` | "这个目标完成到哪了？" | 价值链完成度（OBJ→Epic→BR→PF→CR→OPP） |
| `/pace-theory why` | "devpace 为什么这样设计？" | 系统方法论解释 |

## 输入

- `$ARGUMENTS`：可选——CR 名称/编号 + 决策类型
- 无参数时：展示当前/最近 CR 的最新决策轨迹

## 流程

### 执行路由表

#### 固定加载

| 文件 | 说明 |
|------|------|
| `trace-procedures-common.md` | 通用规则：§0 路由索引 · 输出格式框架 · confidence 表 · 降级处理 · 执行步骤 · 规则 |

#### 按子命令加载

| 决策类型 | 额外加载文件 | 说明 |
|---------|------------|------|
| `gate1` / `gate2` / `gate3` | `trace-procedures-gates.md` | Gate 类型输出要点 + 导航建议 |
| `intent` / `change` / `risk` / `autonomy` | `trace-procedures-analysis.md` | 分析类输出调整 + 导航建议 |
| `timeline` | `trace-procedures-timeline.md`（自包含，不加载 common） | CR 全生命周期决策时间线 |
| 无指定 | 查 CR 事件表最新 checkpoint 类型，匹配上述路由 | 先确定类型再加载对应文件 |

**路由规则**：只读取路由表映射的 procedures 文件，不加载其他文件。timeline 自包含，不加载 common。

## 输出

格式化的决策轨迹（含判定结论、confidence 评估、评估过程、决策上下文、溯源信息、上下文导航）。
