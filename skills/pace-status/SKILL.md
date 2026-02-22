---
description: Use when user asks "进度怎样", "做到哪了", "pace-status", or wants to see project development progress.
allowed-tools: Read, Glob, Grep
argument-hint: "[detail|metrics|tree|chain|<关键词>]"
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
- `chain` → 当前工作在价值链中的位置
- `biz` → Biz Owner 视角（MoS 达成率 + 价值交付）
- `pm` → PM 视角（迭代进度 + 功能完成度）
- `dev` → Dev 视角（CR 状态 + 质量门）
- `tester` → Tester 视角（缺陷分布 + 质量指标）
- `ops` → Ops 视角（Release 状态 + 部署健康）

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

### chain

1. 读取 `.devpace/state.md` 当前工作 + `.devpace/project.md` 价值功能树
2. 定位当前活跃 CR 在价值链中的位置
3. 以用户友好的树形视图输出，**不使用 BR/PF/CR 术语**

输出示例：
```
目标: 实现用户认证系统
  └── 功能: 登录模块 (🔄)
        ├── 任务: 表单验证 (✅)
        └── 任务: OAuth 集成 (🔄) ← 你在这里
```

无活跃 CR 时显示最近完成的链路位置。

### tree

1. 读取 `.devpace/project.md` 的价值功能树部分
2. 展示完整价值链路，每个节点附带状态 emoji 和进度

## 输出

按请求粒度展示的项目状态。自然语言为主，不主动暴露 ID。
