---
description: Use when user says "不做了", "先不搞", "加一个", "加需求", "改一下", "改需求", "优先级调", "优先级调整", "延后", "提前", "砍掉", "插入", "新增需求", "先做这个", "恢复之前的", "恢复", "搁置", "放一放", "范围变了", "不要这个功能了", "追加", "补一个", "还需要", "改个需求", "需求变了", "停掉", "捡回来", "排到前面", "pace-change", or wants to add, pause, resume, reprioritize, modify, undo, batch change, or query change history. NOT for code implementation (use /pace-dev) or project initialization (use /pace-init).
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash, Grep
argument-hint: "[add|pause|resume|reprioritize|modify|batch|undo|history|apply] [#N|--last|--dry-run] <描述>"
context: fork
agent: pace-pm
---

# /pace-change — 需求变更管理

有序处理需求的插入、暂停、恢复、优先级调整和范围修改。支持批量变更、撤销和变更历史查询。

## 与现有机制的关系

- `/pace-change`：PF/BR/Epic 级需求变更（add/pause/resume/modify/reprioritize）
- `/pace-biz`：业务规划域（Opportunity→Epic→BR 的**创建和分解**）
- `/pace-plan adjust`：迭代范围调整（哪些 PF 纳入/移出当前迭代）
- 协同场景：`/pace-change add` 插入新 BR 或 PF → 容量溢出 → 建议 `/pace-plan adjust`
- `devpace-rules.md §9`：自动检测变更意图，共享同一套 procedures 文件

## 推荐使用流程

```
新需求到达：  (空参) → add → /pace-dev
范围调整：    modify → （验证影响）→ /pace-dev
暂停与恢复：  pause → ... → resume → /pace-dev
撤销误操作：  undo（限当前会话）
审计追踪：    history [功能名|--all]
批量操作：    batch（合并多个变更，单次确认）
```

## 输入

$ARGUMENTS：

### 核心子命令

- `add <描述>` → 插入新需求（支持 BR 级和 PF 级——自动检测粒度，或用 `add br <描述>` / `add pf <描述>` 显式指定）
- `pause <名称>` → 暂停/砍掉（支持 Epic/BR/PF/CR 级——根据名称或 ID 自动匹配层级）
- `resume <名称>` → 恢复已暂停的项目（支持 Epic/BR/PF/CR 级）
- `reprioritize <描述>` → 优先级调整
- `modify <名称> <变更描述>` → 修改已有需求（支持 Epic/BR/PF 级）

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
| add / pause / resume / reprioritize / modify | `change-procedures-common.md` + `change-procedures-triage.md` + `change-procedures-impact.md` + `change-procedures-risk.md` + `change-procedures-execution.md` + `change-procedures-types.md` |
| batch | `change-procedures-common.md` + `change-procedures-triage.md` + `change-procedures-impact.md` + `change-procedures-risk.md` + `change-procedures-execution.md` + `change-procedures-types.md` + `change-procedures-batch.md` |
| undo | `change-procedures-undo.md`（自包含） |
| history | `change-procedures-history.md`（自包含） |
| apply | `change-procedures-common.md` + `change-procedures-triage.md` + `change-procedures-impact.md` + `change-procedures-risk.md` + `change-procedures-execution.md` + `change-procedures-types.md` + `change-procedures-apply.md` |
| （空参数） | `change-procedures-common.md`（仅"上下文感知引导"章节） |
| （降级模式，无 .devpace/） | `change-procedures-degraded.md`（自包含） |

## 流程概要

### Step 0：经验预加载

读取 insights.md 匹配同类 pattern，无匹配则静默跳过。

### Step 1：Triage 分流

Accept → 继续影响分析 | Decline → 记录并结束 | Snooze → 持久化并结束。Hotfix/critical 级别触发 auto-Accept，跳过 Triage 直接进入影响分析。

### Step 2：影响分析

评估变更对项目的影响范围，三层分级输出（表面→中间→深入）。`--dry-run` 到此结束。

### Step 3：风险量化

3 维评分（波及模块/受影响 CR/检查重置）+ 变更成本估算。

### Step 4：调整方案 + 等待确认

展示方案和影响预览，**必须等待用户确认后才执行**。

### Step 5：执行变更并记录

更新所有受影响的项目文件，git commit，增量更新度量指标。

### Step 6：下游引导 + 外部同步

结果摘要 + 按变更类型引导后续操作 + 外部关联同步提醒。

## 输出

分阶段输出：影响分析报告（三层分级）→ 调整方案（等待确认）→ 执行结果摘要 + 下游引导。降级模式基于代码库即时分析，不创建 .devpace/ 文件。
