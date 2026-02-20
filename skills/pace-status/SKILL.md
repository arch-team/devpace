---
description: Show project development status. Use when user asks "进度怎样", "做到哪了", "pace-status", or wants to see development progress.
allowed-tools: Read, Glob, Grep
argument-hint: "[detail|metrics|tree|<关键词>]"
---

# /pace-status — 查看项目状态

按不同粒度展示项目研发状态。三级输出严格递增：概览 ⊂ detail ⊂ tree。
详细输出格式见 `status-procedures.md`。

## 输入

$ARGUMENTS：
- （空）→ 快速概览（默认）
- `detail` → 产品功能级别展开
- `<关键词>` → 匹配特定功能的变更详情
- `metrics` → 度量仪表盘
- `tree` → 价值功能树

## 流程

### 快速概览（默认）

1. 读取 `.devpace/state.md`
2. 以 **≤ 3 行** 自然语言 + 进度条输出，不暴露 ID（NF6 硬约束）
3. 如果有阻塞项，高亮提醒

### detail

1. 读取 `.devpace/iterations/current.md` 和 `.devpace/project.md`
2. 以功能树缩进可视化展示所有产品功能及状态
3. 标记阻塞项和依赖关系

### <关键词>

1. 在 `.devpace/backlog/` 中按标题关键词搜索匹配的 CR
2. 展示该 CR 的质量检查 checkbox 状态和事件记录

### metrics

1. 读取 `.devpace/metrics/dashboard.md`
2. 展示度量表格 + insights.md 最近 pattern 摘要（如有）

### tree

1. 读取 `.devpace/project.md` 的价值功能树部分
2. 展示完整价值链路，每个节点附带状态 emoji 和进度

## 输出

按请求粒度展示的项目状态。自然语言为主，不主动暴露 ID。
