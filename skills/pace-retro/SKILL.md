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
- `focus <维度>` → 聚焦回顾：quality | delivery | dora | defects | value | knowledge | epic
- `compare` → 对比回顾：当前迭代 vs 上一迭代的关键指标 delta
- `history` → 趋势总览：跨 3+ 迭代的趋势线（基于 dashboard.md 历史快照）
- `mid` → 中期检查：轻量版回顾，不更新 dashboard 基准线
- `accept` → 确认回顾建议：执行 MoS 更新等上一次回顾建议的操作

### 执行路由表

#### 固定加载

| 文件 | 说明 |
|------|------|
| `retro-procedures-common.md` | 通用规则：§0 路由索引 · Agent 记忆 · 数据收集详情 · 基准线检测 |

#### 按子命令加载

| 参数 | 额外加载文件 | 执行路径 |
|------|------------|---------|
| （空） | `retro-procedures.md` | Step 1→2→3→4→5→6 完整回顾 |
| `update` | `retro-procedures-update.md` | Step 1→2（带变化反馈） |
| `focus <维度>` | `retro-procedures-focus.md` | 单维度深入分析 |
| `compare` | `retro-procedures-compare.md`（自包含，不加载 common） | 双迭代对比 |
| `history` | `retro-procedures-history.md`（自包含，不加载 common） | 跨迭代趋势 |
| `mid` | `retro-procedures-mid.md`（自包含，不加载 common） | 中期轻量检查 |
| `accept` | `retro-procedures-accept.md`（自包含，不加载 common） | 执行建议操作 |

**路由规则**：只读取路由表映射的 procedures 文件，不加载其他文件。compare/history/mid/accept 自包含，不加载 common。

## 流程

### Step 1：收集数据 + 基准线检测

从 backlog/project.md/iterations/releases 提取度量数据，判断首次/非首次度量。详见 `retro-procedures-common.md`。

### Step 2：更新 dashboard.md

更新度量表格，旧值追加到"度量趋势"表。`update` 模式在此步结束并输出变化反馈（详见 `retro-procedures-update.md`）。

### Step 3：生成回顾报告

两层结构：行动摘要（~10 行）+ 维度详情（按角色排序）。详见 `retro-procedures.md`。

### Step 4：经验沉淀

提炼 pattern 交给 pace-learn 管道，输出「本次学习」透明段。详见 `retro-procedures.md`。

### Step 5：迭代传递清单

结构化传递清单写入 iterations/current.md，供 /pace-plan next 消费。详见 `retro-procedures.md`。

### Step 6：报告质量自评

数据充分度、趋势可信度、建议可执行度三维自评。详见 `retro-procedures.md`。

## 输出

行动摘要 + 维度详情报告 + 更新后的 dashboard.md + insights.md 经验沉淀（如有新 pattern）+ 迭代传递清单（写入 iterations/current.md）。
