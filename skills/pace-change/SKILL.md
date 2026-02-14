---
description: Manage requirement changes (add, pause, reprioritize, modify). Use when user says "加需求", "不做了", "优先级调整", "改需求", "pace-change", or when requirements change mid-iteration.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob
---

# /pace-change — 需求变更管理

有序处理需求的插入、暂停、优先级调整和范围修改。

## 输入

$ARGUMENTS：
- `add <描述>` → 插入新需求
- `pause <功能名>` → 暂停/砍掉某个功能
- `resume <功能名>` → 恢复已暂停的功能
- `reprioritize <描述>` → 优先级调整
- `modify <功能名> <变更描述>` → 修改已有需求
- （空）→ 通过对话确定变更类型

## 流程

### Step 1：确定变更类型

如果 $ARGUMENTS 明确了类型 → 直接进入对应流程。
如果为空 → 询问用户要做什么变更。

### Step 2：影响分析

1. 读取 `.devpace/project.md` 价值功能树
2. 读取 `.devpace/iterations/current.md` 当前迭代
3. 读取相关 `.devpace/backlog/` CR 文件

根据变更类型分析影响：

**add（插入新需求）**：
- 新需求属于哪个 BR？需要新建 BR 吗？
- 需要几个 CR？
- 当前迭代容量够吗？需要延后哪些现有 PF？

**pause（暂停）**：
- 目标 PF 下有哪些 CR？各自什么状态？
- 有哪些其他 CR 依赖它们？
- 暂停后对成效指标（MoS）有影响吗？

**resume（恢复）**：
- 暂停时是什么状态？
- 恢复后质量检查是否仍然有效？
- 对当前迭代容量的影响？

**reprioritize（优先级调整）**：
- 哪个 PF/CR 需要提前？
- 当前正在进行的工作要不要暂停让路？

**modify（修改需求）**：
- 已有 CR 的哪些工作需要返工？
- 哪些质量检查需要重置为未检查？

### Step 3：展示影响并提出方案

用自然语言向用户报告：
- 影响了哪些功能
- 具体调整动作
- 对迭代进度的影响
- 对成效指标的影响（如有）

**等待用户确认。**

### Step 4：执行变更

用户确认后：

1. 更新 CR 文件（状态、质量检查、事件记录）
2. 更新 `project.md` 功能树（标记 ⏸️/新增/提前）
3. 更新 `iterations/current.md`（计划 + 变更记录表）
4. 更新 `state.md`（当前工作 + 下一步）

### Step 5：确认完成

向用户确认所有文件已更新，展示调整后的状态。

## 输出

影响分析 + 调整方案 + 执行结果。
