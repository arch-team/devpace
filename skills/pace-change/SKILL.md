---
description: Use when user says "不做了", "先不搞", "加一个", "加需求", "改一下", "改需求", "优先级调", "优先级调整", "延后", "提前", "砍掉", "插入", "新增需求", "先做这个", "恢复之前的", "恢复", "搁置", "放一放", "范围变了", "不要这个功能了", "追加", "补一个", "还需要", "改个需求", "需求变了", "停掉", "捡回来", "排到前面", "pace-change", or wants to add, pause, resume, reprioritize, modify, undo, batch change, or query change history. NOT for code implementation (use /pace-dev) or project initialization (use /pace-init).
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash, Grep
argument-hint: "[add|pause|resume|reprioritize|modify|batch|undo|history|apply] [#N|--last|--dry-run] <描述>"
context: fork
agent: pace-pm
---

# /pace-change — 需求变更管理

有序处理需求的插入、暂停、恢复、优先级调整和范围修改。支持批量变更、撤销和变更历史查询。

## 输入

$ARGUMENTS：

### 核心子命令

- `add <描述>` → 插入新需求
- `pause <功能名>` → 暂停/砍掉某个功能
- `resume <功能名>` → 恢复已暂停的功能
- `reprioritize <描述>` → 优先级调整
- `modify <功能名> <变更描述>` → 修改已有需求

### 扩展子命令

- `batch <描述>` → 批量变更（合并多个变更的影响分析和执行）
- `undo` → 撤销上一次变更操作（限当前会话）
- `history [功能名|--all|--recent N]` → 查询变更历史
- `apply <模板名>` → 应用预定义的变更模板

### 快捷引用

- `#N` → 按编号引用 CR（如 `pause #3` = 暂停 CR-003 所属功能）
- `--last` → 对上次操作的 CR 执行变更（如 `modify --last` = 修改最近操作的 CR）
- `--dry-run` → 仅输出影响预览，不执行任何变更

### 空参数

- （空）→ 智能引导——先扫描项目上下文（paused CR、Snooze 触发条件、迭代容量、频繁变更 PF），给出个性化推荐，再附标准选项列表兜底

## 执行路由表

根据子命令，**只读取路由表中对应的 procedures 文件，不加载其他 procedures 文件。**

| 子命令 | 加载文件 |
|--------|---------|
| add / pause / resume / reprioritize / modify | `change-procedures-common.md` + `change-procedures-types.md` |
| batch | `change-procedures-common.md` + `change-procedures-types.md` + `change-procedures-batch.md` |
| undo | `change-procedures-undo.md`（自包含） |
| history | `change-procedures-history.md`（自包含） |
| apply | `change-procedures-common.md` + `change-procedures-types.md` + `change-procedures-apply.md` |
| （空参数） | `change-procedures-common.md`（仅"上下文感知引导"章节） |
| （降级模式，无 .devpace/） | `change-procedures-degraded.md`（自包含） |

## 流程概要

### Step 0：经验预加载

读取 insights.md 匹配同类 pattern，无匹配则静默跳过。

### Step 1：前置检查 + 确定变更类型

检查 `.devpace/` 是否存在（不存在进入降级模式），解析快捷引用（`#N`/`--last`），空参数进入智能引导。

### Step 1.5：Triage 分流

Accept → 继续影响分析 | Decline → 记录并结束 | Snooze → 持久化并结束 | Hotfix → 跳过直接分析。

### Step 2：影响分析

正常模式：四层追踪（BR→PF→CR→代码），三层分级输出（表面→中间→深入）。`--dry-run` 到此结束。

### Step 3：调整方案 + 等待确认

展示方案和影响预览，**必须等待用户确认后才执行**。

### Step 4：执行变更并记录

更新 CR/功能树/迭代/state.md，git commit，增量更新度量指标。

### Step 5：确认完成 + 下游引导

结果摘要 + 按变更类型引导后续操作（开发/重验/调整迭代）。

## 输出

**正常模式**（分阶段输出，三层分级）：
- Step 2 → 影响分析报告（表面层默认，追问展开中间层/深入层）
- Step 3 → 调整方案（等待确认）
- Step 5 → 执行结果摘要（1-3 行）+ 下游引导

**降级模式**（无 .devpace/）：
- Step 2 → 即时影响评估（基于代码库分析，不创建文件）
- Step 3 → 调整建议（等待确认，执行时仅操作代码，不写 .devpace/）
- Step 5 → 结果摘要 + 初始化引导
