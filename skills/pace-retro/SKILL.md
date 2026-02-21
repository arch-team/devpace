---
description: Run iteration retrospective and update metrics. Use when user says "回顾", "复盘", "度量", "pace-retro", or at iteration end.
allowed-tools: Read, Write, Edit, Glob, Bash
argument-hint: "[update]"
context: fork
agent: pace-analyst
---

# /pace-retro — 迭代回顾与度量

生成迭代回顾报告，更新度量仪表盘。详细执行规则见 `retro-procedures.md`。

## 输入

$ARGUMENTS：
- （空）→ 当前迭代完整回顾
- `update` → 仅更新度量数据，不生成报告

## 流程

### Step 1：收集数据 + 基准线检测

读取 Plugin `knowledge/metrics.md` 获取指标定义和计算公式。
从 `.devpace/backlog/`、`project.md`、`iterations/current.md`（格式参考 Plugin `knowledge/_schema/iteration-format.md`）提取度量数据。
读取 `dashboard.md` 判断是首次度量（建立基准）还是非首次（计算趋势）。

### Step 2：更新 dashboard.md

用收集的数据更新 `.devpace/metrics/dashboard.md` 中的表格。

### Step 3：生成回顾报告（非 `update` 模式时）

输出交付、质量、价值、周期四维度报告 + 改进建议。格式见 `retro-procedures.md`。

### Step 4：经验沉淀（非 `update` 模式时）

从回顾数据中提炼可复用 pattern，追加到 `.devpace/metrics/insights.md`。
已有 pattern 被验证时追加记录，被否定时标注存疑。详见 `retro-procedures.md`。

## 输出

回顾报告 + 更新后的 dashboard.md + insights.md 经验沉淀（如有新 pattern）。
