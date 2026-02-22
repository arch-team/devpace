---
description: Use when user asks "why did devpace decide X", wants to see AI decision trail, or says /pace-trace [CR] [gate/decision]
allowed-tools: Read, Glob, Grep
argument-hint: "[CR 名称或编号] [gate1|gate2|gate3|intent|change|autonomy]"
---

# /pace-trace — 决策轨迹查询

> 三层渐进透明的深入层。提供完整的 AI 决策轨迹，让用户可审计 Claude 的每个系统判断。

## 输入

- `$ARGUMENTS`：可选——CR 名称/编号 + 决策类型
- 无参数时：展示当前/最近 CR 的最新决策轨迹

## 决策类型

| 类型 | 查询内容 |
|------|---------|
| `gate1` | Gate 1 质量检查的完整判定过程 |
| `gate2` | Gate 2 集成验证 + 验收比对的完整判定过程 |
| `gate3` | Gate 3 审批前的摘要生成过程 |
| `intent` | 意图检查点的推断过程（含溯源标记） |
| `change` | 变更影响分析的推理过程 |
| `risk` | 风险评估的判断依据 |
| 无指定 | 展示 CR 最近一次重要决策的轨迹 |

## 输出格式

```markdown
## 决策轨迹 — [CR 名称] [决策类型]

### 读取的上下文
- [文件路径]: [读取了什么信息]
- [文件路径]: [读取了什么信息]

### 规则匹配
- [匹配的规则/检查项]: [如何应用到当前场景]

### 逐项检查结果（Gate 类型）
1. [检查项] — [通过/失败] ([具体数据])
2. [检查项] — [通过/失败] ([具体数据])

### 溯源信息
- 用户明确表达: [source: user 的内容摘要]
- Claude 推断: [source: claude 的内容摘要及推断原因]

### 综合判定
[最终判定] 原因: [完整推理链]
```

## 步骤

1. **解析参数**：识别 CR（名称匹配或 ID）和决策类型
2. **定位数据源**：
   - CR 文件（`backlog/CR-*.md`）：事件表、意图 section、质量检查 checkbox
   - project.md：溯源标记、功能树上下文
   - checks.md：项目质量规则
   - insights.md：经验引用记录
3. **重建决策上下文**：根据事件表时间线，还原决策时 Claude 读取了哪些信息
4. **展示溯源标记**：提取并展示 CR 意图 section 和 project.md 中的 `<!-- source: ... -->` 标记
5. **输出格式化轨迹**：按上述格式输出，层次清晰

## 规则

- **只读操作**：不修改任何文件（纯查询）
- **基于已有数据**：从 CR 事件表、checkpoint 标记、溯源标记重建轨迹，不重新执行判断
- **溯源标记展示**：深入层是溯源标记唯一可见的位置（日常输出不展示）
- **无数据降级**：CR 无事件记录或无溯源标记时，输出"此 CR 创建时未启用决策追踪"
- **不暴露内部术语**：输出中使用自然语言描述，不直接展示 schema 字段名
