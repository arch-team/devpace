---
description: Plan iteration scope. Use when user says "规划迭代", "下个迭代做什么", "迭代规划", "pace-plan", or at iteration boundary.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob
argument-hint: "[next|close]"
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

1. 读取 `.devpace/iterations/current.md`（不存在则跳到 Step 3）
2. 读取 `.devpace/project.md` 的价值功能树
3. 汇总当前迭代状态：
   - PF 完成率（✅ 数 / 总数）
   - 未完成 PF 列表及其 CR 状态
   - 变更记录条数
4. 用 1-2 句话告知用户当前迭代进展

### Step 2：关闭当前迭代

> 仅在 `$ARGUMENTS` 为 `close` 或用户确认关闭时执行。

1. 更新 `iterations/current.md`：
   - 填写偏差快照（计划 PF 数 vs 实际完成数）
   - 标记未完成 PF 的状态（⏸️ 延后 / 🔄 续入下个迭代）
2. 归档：将 `current.md` 重命名为 `iter-N.md`（N = 已有归档文件数 +1）
3. 建议用户运行 `/pace-retro` 做迭代回顾（不自动触发）

### Step 3：规划新迭代

> `$ARGUMENTS` 为 `next` 时直接进入；否则在 Step 2 完成后或无当前迭代时进入。

1. 读取 `.devpace/project.md` 功能树，列出所有待开始（⏳）和进行中（🔄）的 PF
2. 如有上一迭代延后的 PF，优先列出并标注"上迭代延后"
3. 使用 `AskUserQuestion` 引导用户选择：
   - 本次迭代目标（1 句话）
   - 纳入的 PF（从待选列表中选择）
   - 迭代周期（起止日期，可选）
4. 生成 `iterations/current.md`（格式遵循 `knowledge/_schema/iteration-format.md`）
5. 更新 `.devpace/state.md`：反映新迭代信息

### Step 4：确认与输出

1. 展示新迭代规划摘要（目标 + PF 列表 + 周期）
2. 告知用户"迭代已规划，可以开始推进"

## 输出

迭代规划摘要（3-5 行）：目标、纳入的 PF 数量、周期。
