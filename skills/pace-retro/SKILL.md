---
description: Use when user says "回顾", "复盘", "度量", "retro", "总结", "数据分析", "DORA", "质量报告", "交付效率", "度量报告", "趋势", "中期检查", "对比", "pace-retro", or at iteration end when reviewing progress and metrics.
allowed-tools: Read, Write, Edit, Glob, Bash
argument-hint: "[update|focus <维度>|compare|history|mid|accept]"
context: fork
agent: pace-analyst
---

# /pace-retro — 迭代回顾与度量

生成迭代回顾报告，更新度量仪表盘，提供多粒度分析视角。详细执行规则见对应 procedures 文件。

## 与现有机制的关系

| 机制 | 职责 | 区别 |
|------|------|------|
| /pace-status metrics | 查看当前度量快照 | 只读展示，不做分析 |
| /pace-plan close | 迭代关闭时轻量回顾 | 3 个基准指标，不含改进建议 |
| /pace-retro | 完整回顾分析 + 经验沉淀 | 多维度分析 + 趋势对比 + 知识闭环 |

## 推荐使用流程

```
1. /pace-retro mid          → 迭代中期快速检查（轻量，不影响基准线）
2. /pace-retro focus quality → 聚焦某个维度深入分析
3. /pace-retro               → 迭代末尾完整回顾
4. /pace-retro accept        → 确认回顾建议的操作（MoS 更新等）
5. /pace-retro compare       → 对比本迭代与上一迭代的变化
6. /pace-retro history       → 查看 3+ 迭代的趋势总览
7. /pace-retro update        → 仅刷新度量数据（不生成报告）
```

## 输入

$ARGUMENTS：
- （空）→ 当前迭代完整回顾
- `update` → 仅刷新度量数据，不生成报告（带变化反馈）
- `focus <维度>` → 聚焦回顾：quality | delivery | dora | defects | value | knowledge
- `compare` → 对比回顾：当前迭代 vs 上一迭代的关键指标 delta
- `history` → 趋势总览：跨 3+ 迭代的趋势线（基于 dashboard.md 历史快照）
- `mid` → 中期检查：轻量版回顾，不更新 dashboard 基准线
- `accept` → 确认回顾建议：执行 MoS 更新等上一次回顾建议的操作

### 执行路由表

| 参数 | 加载的 procedures 文件 | 执行路径 |
|------|----------------------|---------|
| （空） | `retro-procedures.md` | Step 1→2→3→4 完整回顾 |
| `update` | `retro-procedures.md` | Step 1→2（带变化反馈） |
| `focus <维度>` | `retro-procedures.md` + `retro-procedures-focus.md` | 单维度深入分析 |
| `compare` | `retro-procedures-compare.md` | 双迭代对比 |
| `history` | `retro-procedures-history.md` | 跨迭代趋势 |
| `mid` | `retro-procedures-mid.md` | 中期轻量检查 |
| `accept` | `retro-procedures-accept.md` | 执行建议操作 |

**路由规则**：只读取路由表映射的 procedures 文件，不加载其他 procedures 文件。

## 流程

### Step 1：收集数据 + 基准线检测

读取 Plugin `knowledge/metrics.md` 获取指标定义和计算公式。
从 `.devpace/backlog/`、`project.md`、`iterations/current.md`（格式参考 Plugin `knowledge/_schema/iteration-format.md`）提取度量数据。
从 `.devpace/releases/` 提取 Release 数据（如有）。
读取 `dashboard.md` 判断是首次度量（建立基准）还是非首次（计算趋势）。
额外采集缺陷数据：backlog/ 中 type:defect 和 type:hotfix 的 CR 数量、严重度分布、修复周期。

### Step 2：更新 dashboard.md

用收集的数据更新 `.devpace/metrics/dashboard.md` 中的表格。
**历史快照追加**：更新时将旧值追加到"度量趋势"表（而非覆盖），保留跨迭代历史数据供 `compare` 和 `history` 子命令消费。

`update` 模式在此步完成后输出变化反馈摘要（格式见 `retro-procedures.md`），然后结束。

### Step 3：生成回顾报告（非 `update` 模式时）

**输出结构为两层**：

**第一层：行动摘要（~10 行，默认必输出）**——关键指标 + 趋势箭头 + 关注项 + 亮点 + 核心建议 + 待确认操作。
**第二层：维度详情（紧跟摘要，按角色排序）**——交付、质量、缺陷、价值、周期 + 条件段（DORA/风险趋势/知识驱动改进/知识库健康度/学习效能）。

格式和段落详情见 `retro-procedures.md`。

### Step 4：经验沉淀（非 `update`/`mid` 模式时）

从回顾数据中提炼可复用 pattern，通过 pace-learn 统一写入管道处理。
沉淀完成后输出「本次学习」透明段——列出提交的 pattern、验证结果和处理状态。
详见 `retro-procedures.md`。

### Step 5：迭代传递清单（完整回顾模式时）

生成结构化的"迭代传递清单"写入 `iterations/current.md` 的回顾 section，供 `/pace-plan next` 消费。
包含：继承到下个迭代的改进项、度量基线、未完成 PF、下个迭代建议关注维度。
详见 `retro-procedures.md`。

### Step 6：报告质量自评（完整回顾模式时）

在报告末尾输出数据充分度、趋势可信度、建议可执行度三维自评。
详见 `retro-procedures.md`。

## 输出

行动摘要 + 维度详情报告 + 更新后的 dashboard.md + insights.md 经验沉淀（如有新 pattern）+ 迭代传递清单（写入 iterations/current.md）。
