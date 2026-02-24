---
description: Use when user says "规划迭代", "下个迭代做什么", "迭代规划", "计划", "排期", "安排", "sprint", "pace-plan", or at iteration boundary when planning next iteration scope.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob
argument-hint: "[next|close]"
context: fork
agent: pace-pm
---

# /pace-plan — 迭代规划

管理迭代的关闭和新迭代的规划，补齐产品闭环中的"规划→执行→回顾"循环。

## 输入

$ARGUMENTS：
- （空）→ 评估当前迭代状态，建议下一步操作（关闭 or 继续）
- `next` → 直接进入新迭代规划流程
- `close` → 关闭当前迭代（不启动新迭代）

## 流程

### Step 1：评估当前迭代状态

读取 `plan-procedures.md` Step 1，评估 `.devpace/iterations/current.md` 和 `project.md`，汇总 PF 完成率和未完成列表。

### Step 2：关闭当前迭代

> 仅在 `$ARGUMENTS` 为 `close` 或用户确认关闭时执行。

读取 `plan-procedures.md` Step 2，填写偏差快照、归档当前迭代、建议运行 `/pace-retro`。

### Step 3：规划新迭代

读取 `plan-procedures.md` Step 3，列出候选 PF、执行范围估算和业务引导、引导用户选择迭代目标和范围、生成 `iterations/current.md`。

### Step 4：确认与输出

展示新迭代规划摘要（目标 + PF 列表 + 周期 + 工作量估算），告知用户"迭代已规划，可以开始推进"。

## 输出

迭代规划摘要（3-5 行）：目标、纳入的 PF 数量、周期。
