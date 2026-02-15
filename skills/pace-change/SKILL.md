---
description: Manage requirement changes (add, pause, resume, reprioritize, modify). Use when user says "加需求", "不做了", "恢复", "优先级调整", "改需求", "pace-change", or when requirements change mid-iteration.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash
---

# /pace-change — 需求变更管理

有序处理需求的插入、暂停、恢复、优先级调整和范围修改。

## 输入

$ARGUMENTS：
- `add <描述>` → 插入新需求
- `pause <功能名>` → 暂停/砍掉某个功能
- `resume <功能名>` → 恢复已暂停的功能
- `reprioritize <描述>` → 优先级调整
- `modify <功能名> <变更描述>` → 修改已有需求
- （空）→ 通过对话确定变更类型

## 流程

### Step 1：前置检查 + 确定变更类型

1. 检查 `.devpace/` 是否存在 → 不存在则提示用户先运行 `/pace-init`
2. 读取 `.devpace/state.md` 了解当前项目状态
3. 如果 $ARGUMENTS 明确了类型 → 直接进入对应流程
4. 如果为空 → 询问用户要做什么变更，提供选项（插入 / 暂停 / 恢复 / 调优先级 / 修改范围）

### Step 2：影响分析

读取 `change-procedure.md` Step 1，按变更类型执行影响分析：

1. 读取功能树（project.md，无则读 state.md 功能概览）
2. 读取受影响的 CR 文件
3. 读取迭代计划（iterations/current.md，如存在）
4. 用**自然语言**向用户报告影响范围（不使用 ID 和技术术语）

### Step 3：调整方案 + 等待确认

读取 `change-procedure.md` Step 2，根据变更类型提出调整方案：

- 插入 → 创建功能 + 变更请求，评估迭代容量
- 暂停 → 保留全部工作成果，标记暂停，解除依赖
- 恢复 → 回到暂停前阶段，评估质量检查有效性
- 重排 → 更新下一步建议，重排计划
- 修改 → 更新范围/验收条件，重置受影响的质量检查

**向用户展示方案，必须等待确认后才执行。**

### Step 4：执行变更并记录

用户确认后，按 `change-procedure.md` Step 3 更新全部关联文件：

1. CR 文件（状态、意图、质量检查、事件表）
2. project.md 功能树（新增 / 暂停 / 恢复 / 状态变更）
3. iterations/current.md 变更记录表（如存在）
4. state.md 当前工作和下一步
5. git commit 记录本次变更

### Step 5：确认完成

向用户确认变更已执行：
- 1-3 行摘要：变更了什么、影响了哪些功能
- 展示调整后的下一步建议

## 输出

分阶段输出：
- Step 2 → 影响分析报告（自然语言，不使用 ID）
- Step 3 → 调整方案（等待确认）
- Step 5 → 执行结果摘要（1-3 行）
