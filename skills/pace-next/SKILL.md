---
description: Use when user asks "下一步做什么", "接下来做什么", "该做什么", "什么最重要", "pace-next", or wants a recommendation for the most important next action.
allowed-tools: Read, Glob, Grep
argument-hint: "[detail]"
---

# /pace-next — 下一步导航

跨域全局导航：综合 CR、迭代、Release、度量等多维信号，推荐当前最该做的 1 件事。

详细决策规则见 `next-procedures.md`。

## 输入

$ARGUMENTS：
- （空）→ 最高优先级 1 条建议（默认，≤ 3 行）
- `detail` → 展开候选列表（≤ 8 行，含 top-3 建议）

## 流程

### Step 1：检测项目状态

1. 检查项目根目录是否存在 `.devpace/state.md`
2. 不存在 → 输出未初始化引导（见 next-procedures.md），结束
3. 存在 → 继续

### Step 2：采集信号

读取 `.devpace/` 目录下的多个数据源，采集优先级决策所需信号。详细数据源和读取规则见 `next-procedures.md` Step 2。

### Step 3：优先级决策

按 12 级优先级矩阵（见 `next-procedures.md` Step 3）从高到低遍历，取命中的最高优先级信号。

### Step 4：经验增强（可选）

如果 `.devpace/metrics/insights.md` 存在，读取匹配当前建议类型的 pattern，增强建议内容。

### Step 5：角色适配

根据 §13 角色意识调整建议视角。详见 `next-procedures.md` Step 5。

### Step 6：输出

- 默认：≤ 3 行（建议 + 原因 + 操作）
- detail：≤ 8 行（top-1 + 候选 2-3）

## 输出

≤ 3 行（默认）或 ≤ 8 行（detail）的行动建议，自然语言为主，不暴露 ID。
