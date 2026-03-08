---
description: Use when user says "规划迭代", "下个迭代做什么", "迭代规划", "计划", "排期", "安排", "sprint", "pace-plan", "调整迭代范围", "迭代调整", "迭代健康", or at iteration boundary when planning next iteration scope. NOT for PF-level requirement changes (use /pace-change).
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob
argument-hint: "[next|close|adjust|health]"
context: fork
agent: pace-pm
---

# /pace-plan — 迭代规划

管理迭代的关闭和新迭代的规划，补齐产品闭环中的"规划→执行→回顾"循环。

## 与相关命令的关系

- `/pace-change`：PF/BR/Epic 级需求变更（add/pause/resume/modify）
- `/pace-biz`：业务规划域（Opportunity→Epic→BR 的创建和分解）
- `/pace-plan adjust`：迭代范围级调整（本迭代纳入/移出哪些 PF）
- 典型协同：`/pace-biz decompose` 分解出 BR/PF → `/pace-plan next` 纳入迭代 → `/pace-dev` 开始开发

## 输入

$ARGUMENTS：
- （空）→ 评估当前迭代状态，建议下一步操作（关闭 or 继续）
- `next` → 直接进入新迭代规划流程
- `close` → 关闭当前迭代（自动轻量回顾 + 归档，不启动新迭代）
- `adjust` → 迭代中途范围调整（增加/移除 PF、调整优先级）
- `health` → 展示当前迭代健康度指标

## 执行路由

**重要**：根据 $ARGUMENTS 值，仅读取对应的 procedures 文件，不加载其他 procedures。

| 参数 | 加载文件 | 执行路径 |
|------|---------|---------|
| (空) | 无外部文件 | Step 1 评估 → 建议下一步 |
| `next` | `plan-procedures.md` | Step 1 → Step 3 → Step 4 |
| `close` | `close-procedures.md` | Step 1 → Step 2 |
| `adjust` | `adjust-procedures.md` | Step 2.5 |
| `health` | `health-procedures.md` | Step 5 |

## 流程

### Step 1：评估当前迭代状态

1. 读取 `.devpace/iterations/current.md`（不存在则跳到 Step 3）
2. 读取 `.devpace/project.md` 的价值功能树（有 Epic 时按 Epic 分组展示）
3. 汇总：PF 完成率（✅ 数 / 总数）、未完成 PF 列表及 CR 状态、变更记录条数、Epic 完成度（如有）
4. 用 1-2 句话告知用户当前迭代进展

### Step 3：规划新迭代

> `$ARGUMENTS` 为 `next` 时执行。读取 `plan-procedures.md` 完成候选 PF 列出、范围估算、Plan Proposal 生成、迭代文件创建。

### Step 4：确认与输出

展示新迭代规划摘要（目标 + PF 列表 + 周期 + 工作量估算），引导衔接 `/pace-dev`。

## 输出

迭代规划摘要（3-5 行）：目标、纳入的 PF 数量、周期。
