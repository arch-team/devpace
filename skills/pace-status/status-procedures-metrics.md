# metrics：度量仪表盘

> 由 SKILL.md 路由表加载。仅在 `metrics` 子命令时读取。

## 数据源

读取 `.devpace/metrics/dashboard.md`。如有 `.devpace/metrics/insights.md`，附加最近 3 条经验 pattern 摘要。

## 默认输出（核心指标摘要）

```
📊 核心指标
一次通过率：78% →    CR 平均周期：3.2 天 ↓
MoS 达成率：60% ↑    迭代速度：5 CR/迭代 →
```

- 从 dashboard.md 提取 4 项核心指标
- 与上次记录值对比标注趋势箭头：↑ 上升、↓ 下降、→ 持平

## 按类别聚焦（可选参数）

- `metrics quality`：一次通过率 + 人类打回率 + 缺陷逃逸率 + Gate 通过分布
- `metrics delivery`：CR 平均周期 + 迭代速度 + 完成率 + 范围变更次数
- `metrics risk`：open 风险数 + MTTR + 高严重度占比 + 风险解决率

每项均标注趋势箭头。数据不足时显示"（数据不足）"而非空值。

## 与 pace-retro 的关系

概念边界见 SKILL.md 路由表（metrics = 实时快照）。本文件仅定义快照的输出格式。

## 导航

输出末尾追加 1 行：`→ 完整回顾：/pace-retro`
