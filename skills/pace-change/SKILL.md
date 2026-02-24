---
description: Use when user says "不做了", "先不搞", "加一个", "加需求", "改一下", "改需求", "优先级调", "优先级调整", "延后", "提前", "砍掉", "插入", "新增需求", "先做这个", "恢复之前的", "恢复", "pace-change", or wants to add, pause, resume, reprioritize, or modify requirements. NOT for code implementation (use /pace-dev) or project initialization (use /pace-init).
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash
argument-hint: "[add|pause|resume|reprioritize|modify] <描述>"
context: fork
agent: pace-pm
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

1. 检查 `.devpace/` 是否存在：
   - **存在** → 读取 `.devpace/state.md` 了解当前项目状态，继续 Step 2
   - **不存在（降级模式）** → 不报错、不引导初始化，直接进入 Step 2 的降级分支（仅基于代码库和对话上下文分析）
2. 如果 $ARGUMENTS 明确了类型 → 直接进入对应流程
3. 如果为空 → 询问用户要做什么变更，提供选项（插入 / 暂停 / 恢复 / 调优先级 / 修改范围）

### Step 1.5：Triage 分流

读取 `change-procedures.md` Step 0.5，对变更请求做快速分流：

- **Accept** → 继续 Step 2 影响分析
- **Decline** → 记录拒绝原因，输出结果，结束
- **Snooze** → 记录延后原因和触发条件，输出结果，结束
- **Hotfix/Critical** → 跳过 Triage，直接进入 Step 2

Claude 根据变更与当前迭代目标的相关性自动建议分流决策，用户可覆盖。

### Step 2：影响分析

**正常模式**（.devpace/ 存在）：读取 `change-procedures.md` Step 1，按变更类型执行影响分析：

1. 读取功能树（project.md，无则读 state.md 功能概览）
2. 读取受影响的 CR 文件
3. 读取迭代计划（iterations/current.md，如存在）
4. 用**自然语言**向用户报告影响范围（不使用 ID 和技术术语）

**降级模式**（无 .devpace/）：读取 `change-procedures.md` 降级模式章节，基于代码库即时分析：

1. 用 Glob/Grep/Read 扫描项目代码，识别变更涉及的模块和文件
2. 分析模块间依赖关系，评估变更的波及范围
3. 用**自然语言**向用户报告即时影响评估（不创建任何文件）

### Step 3：调整方案 + 等待确认

读取 `change-procedures.md` Step 2，根据变更类型提出调整方案：

- 插入 → 创建功能 + 变更请求，评估迭代容量
- 暂停 → 保留全部工作成果，标记暂停，解除依赖
- 恢复 → 回到暂停前阶段，评估质量检查有效性
- 重排 → 更新下一步建议，重排计划
- 修改 → 更新范围/验收条件，重置受影响的质量检查

**向用户展示方案，必须等待确认后才执行。**

### Step 4：执行变更并记录

用户确认后，按 `change-procedures.md` Step 3 更新全部关联文件：

1. CR 文件（状态、意图、质量检查、事件表）
2. project.md 功能树（新增 / 暂停 / 恢复 / 状态变更）
3. iterations/current.md 变更记录表（如存在）
4. state.md 当前工作和下一步
5. git commit 记录本次变更

### Step 5：确认完成

向用户确认变更已执行：
- 1-3 行摘要：变更了什么、影响了哪些功能
- 展示调整后的下一步建议
- **降级模式额外输出**："完整初始化后可获得持久化追溯、质量门禁和度量能力。运行 /pace-init 开始。"

## 输出

**正常模式**（分阶段输出）：
- Step 2 → 影响分析报告（自然语言，不使用 ID）
- Step 3 → 调整方案（等待确认）
- Step 5 → 执行结果摘要（1-3 行）

**降级模式**（无 .devpace/）：
- Step 2 → 即时影响评估（基于代码库分析，不创建文件）
- Step 3 → 调整建议（等待确认，执行时仅操作代码，不写 .devpace/）
- Step 5 → 结果摘要 + 初始化引导
