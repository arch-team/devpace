---
description: Show project development status. Use when user asks "进度怎样", "做到哪了", "pace-status", or wants to see development progress.
allowed-tools: Read, Glob
---

# /pace-status — 查看项目状态

按不同粒度展示项目研发状态。

## 输入

$ARGUMENTS：
- （空）→ 快速概览（默认）
- `detail` → 产品功能级别展开
- `<关键词>` → 匹配特定功能的变更详情
- `metrics` → 度量仪表盘
- `tree` → 价值追溯树

## 流程

### 快速概览（默认）

1. 读取 `bizdevops/state.md`
2. 以 1-3 行自然语言输出，不暴露 ID
3. 如果有阻塞项，高亮提醒

### detail

1. 读取 `bizdevops/iterations/current.md`
2. 列出所有产品功能及状态
3. 标记阻塞项和进度百分比

### <关键词>

1. 在 `bizdevops/backlog/` 中按标题关键词搜索匹配的 CR
2. 展示该 CR 的门禁 checkbox 状态和事件记录

### metrics

1. 读取 `bizdevops/metrics/dashboard.md`
2. 展示度量表格

### tree

1. 读取 `bizdevops/product-line.md` 的价值追溯树部分
2. 展示从业务目标到变更请求的完整链路

## 输出

按请求粒度展示的项目状态。自然语言为主，不主动暴露 ID。
