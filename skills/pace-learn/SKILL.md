---
description: Use when user says "/pace-learn", "经验", "知识库", "pattern", "lessons learned", "学到了什么", or auto-invoked after CR merge, gate failure recovery, or human rejection. NOT for iteration retrospectives or metrics (use /pace-retro). NOT for concept explanations (use /pace-theory).
allowed-tools: Read, Write, Edit, Glob, Grep
model: sonnet
argument-hint: "[note|list|stats|export] [参数]"
---

# /pace-learn — 经验积累与知识管理

devpace 的学习引擎。双模式运行：

- **自动模式**（主体）：在关键事件后静默提取经验 pattern 到 `.devpace/metrics/insights.md`
- **手动模式**：用户通过子命令管理知识库

## 子命令路由

**重要**：根据触发方式（自动/手动）和子命令，仅读取路由表中对应的 procedures 文件，不加载其他 procedures。

| 子命令 | 说明 | 详见 |
|--------|------|------|
| （无参数/自动触发） | 事件驱动的自动学习 | 本文件"自动模式流程" + `learn-procedures.md` |
| `note <描述>` | 手动沉淀探索中的有价值经验 | `learn-procedures-query.md` §1 |
| `list [--type TYPE] [--tag TAG] [--confidence MIN]` | 按条件筛选 pattern | `learn-procedures-query.md` §2 |
| `stats` | 知识库统计概览 | `learn-procedures-query.md` §3 |
| `export [--path FILE]` | 导出可复用经验 | `learn-procedures-query.md` §4 |

## 自动触发场景

| 触发事件 | 事件类型 | 学习重点 | 提取目标 |
|---------|---------|---------|---------|
| CR merged | `merged` | 成功模式 | 可复用的检查项、高效的工作路径 |
| Gate fail | `gate1_fail` / `gate2_fail` | 失败教训 | 检查项阈值调整、Claude 盲区识别 |
| 人类打回 | `rejected` | 理解差距 | 意图理解偏差模式、审查标准校准 |
| 挣扎信号 | `struggle` | 环境缺陷识别 | Skill/procedures/Schema 改进建议 |

触发源由 `hooks/post-cr-update.mjs` 检测并输出 `devpace:learn-trigger` 提醒。

## 自动模式流程

**重要**：自动模式按以下步骤执行，仅读取 `learn-procedures.md` 中对应 Step，不加载 `learn-procedures-query.md`。

### Step 1：前置检查

检查 `.devpace/` 是否存在——不存在则静默退出。存在则按触发源确定提取方向（merged→成功 pattern | Gate fail→防御 pattern | rejected→改进 pattern）。

### Step 2：提取 Pattern

读取 `learn-procedures.md` Step 2 执行。

### Step 3：对比与积累

读取 `learn-procedures.md` Step 3 执行。

### Step 4：嵌入式反馈

读取 `learn-procedures.md` Step 4 执行。

## 输出

- **自动模式**：嵌入式 1 行通知（有新 pattern 时），或静默（无有价值发现时）
- **手动模式**：按子命令输出，详见 `learn-procedures-query.md`

## 约束

- 不修改 CR 文件或其他状态文件（仅写入 insights.md）
- 不中断当前工作流
