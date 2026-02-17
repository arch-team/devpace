---
description: Run iteration retrospective and update metrics. Use when user says "回顾", "复盘", "度量", "pace-retro", or at iteration end.
allowed-tools: Read, Write, Edit, Glob
argument-hint: "[update]"
---

# /pace-retro — 迭代回顾与度量

生成迭代回顾报告，更新度量仪表盘。

## 输入

$ARGUMENTS：
- （空）→ 当前迭代完整回顾
- `update` → 仅更新度量数据，不生成报告

## 流程

### Step 1：收集数据

从 `.devpace/backlog/` 所有 CR 文件提取：
- 各 CR 状态分布（merged / in-progress / pending）
- 质量检查一次通过率（首次检查即 `[x]` 的比例）
- 人类打回次数（事件表中 in_review → developing 的次数）
- 各 CR 从创建到 merged 的天数

从 `.devpace/project.md` 提取：
- 成效指标（MoS）达成情况（已勾选 / 总数）

从 `.devpace/iterations/current.md` 提取：
- 计划 vs 实际完成的产品功能数

### Step 2：更新 dashboard.md

用收集的数据更新 `.devpace/metrics/dashboard.md` 中的表格。

### Step 3：生成回顾报告（非 `update` 模式时）

```
## 迭代回顾：[迭代名称]

**交付**：计划 N 个产品功能，完成 M 个
**质量**：质量检查一次通过率 X%，打回率 Y%
**价值**：成效指标达成 A/B
**周期**：平均变更周期 Z 天

**做得好的**：[从数据中识别正面趋势]
**需改进的**：[从数据中识别问题]
**下个迭代建议**：[基于数据的改进建议]
```

## 输出

回顾报告 + 更新后的 dashboard.md。
