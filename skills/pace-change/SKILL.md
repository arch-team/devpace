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

### Step 2：影响分析 + 调整方案

读取 `change-procedure.md`，按变更类型执行三步流程：影响分析 → 提出调整方案 → **等待用户确认**。

### Step 3：执行变更

用户确认后，按 `change-procedure.md` Step 3 执行更新并记录。

### Step 4：确认完成

向用户确认所有文件已更新，展示调整后的状态。

## 输出

影响分析 + 调整方案 + 执行结果。
