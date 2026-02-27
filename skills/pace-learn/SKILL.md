---
description: Use when user says "/pace-learn" for knowledge base management, or auto-invoked after CR merge, gate failure recovery, or human rejection.
allowed-tools: Read, Write, Edit, Glob, Grep
model: sonnet
argument-hint: "[note|list|stats|export] [参数]"
---

# pace-learn — 经验积累与知识管理

devpace 的学习引擎。双模式运行：

- **自动模式**（主体）：在关键事件后静默提取经验 pattern 到 `.devpace/metrics/insights.md`
- **手动模式**：用户通过子命令管理知识库

## 与现有机制的关系

| 机制 | 职责边界 |
|------|---------|
| pace-learn（自动） | CR 级微观学习：merged/Gate 修复/打回后提取 pattern |
| pace-learn（手动） | 知识库查询、手动知识沉淀、导出导入 |
| pace-retro | 迭代级宏观回顾：生成回顾报告，产出学习请求交 pace-learn 处理 |
| §12 经验引用 | 只读消费 insights.md，辅助决策 |
| §12.5 纠正即学习 | 产出偏好学习请求，交 pace-learn 处理写入 |

**统一写入原则**：pace-learn 是 `insights.md` 的唯一写入入口。其他 Skill 产出结构化"学习请求"，由 pace-learn 的 Step 3 管道统一处理（去重、置信度、格式合规）。

## 子命令路由

| 子命令 | 说明 | 详见 |
|--------|------|------|
| （无参数/自动触发） | 事件驱动的自动学习 | 本文件"自动模式流程" |
| `note <描述>` | 手动沉淀探索中的有价值经验 | `learn-procedures-query.md` §1 |
| `list [--type TYPE] [--tag TAG] [--confidence MIN]` | 按条件筛选 pattern | `learn-procedures-query.md` §2 |
| `stats` | 知识库统计概览 | `learn-procedures-query.md` §3 |
| `export [--path FILE]` | 导出可复用经验 | `learn-procedures-query.md` §4 |

## 触发条件（自动模式）

由 `rules/devpace-rules.md` §11 定义触发时机：
- CR 状态变为 merged 后
- 质量门首次失败后成功修复
- 人类打回 CR（in_review → developing）后

## 自动模式流程

### Step 1：前置检查

1. 检查 `.devpace/` 是否存在——不存在则静默退出，不报错
2. 根据触发源确定提取方向：

| 触发源 | 提取方向 |
|--------|---------|
| CR merged | 成功 pattern：什么做法效果好 |
| 质量门修复 | 防御 pattern：什么容易出错、如何避免 |
| 人类打回 | 改进 pattern：人类关注点、设计质量提升 |

### Step 2：提取 Pattern

读取 `learn-procedures.md` Step 2，从触发 CR 的多维数据源中提炼经验规律。

**自适应提取数量**（按 CR 复杂度调整）：
- S 复杂度（≤3 checkpoint）→ 最多 1 个 pattern
- M 复杂度（4-7 checkpoint）→ 最多 2 个 pattern
- L/XL 复杂度（>7 checkpoint）→ 最多 3 个 pattern

### Step 3：对比与积累

读取 `learn-procedures.md` Step 3，与 `.devpace/metrics/insights.md` 已有 pattern 对比，追加新 pattern 或标注验证/存疑。

此步骤同时处理来自其他 Skill 的学习请求（pace-retro 回顾沉淀、§12.5 纠正即学习）。

### Step 4：嵌入式反馈

- 有新 pattern 时：在 §11 管道输出末尾追加 1 行通知——`（经验 +N：[pattern 标题简写]）`
- 仅验证已有 pattern 时：`（经验验证：[pattern 标题] 置信度 → X.X）`
- 无有价值 pattern 时：静默，不输出
- 仅在 insights.md 写入变更时 git commit（消息：`chore(knowledge): extract pattern from CR-xxx`）

## 输出

- **自动模式**：嵌入式 1 行通知（有新 pattern 时），或静默（无有价值发现时）
- **手动模式**：按子命令输出，详见 `learn-procedures-query.md`

## 约束

- 自适应提取数量（见 Step 2），质量优先于数量
- 不修改 CR 文件或其他状态文件（仅写入 insights.md）
- 不中断当前工作流
- insights.md 唯一写入者——其他 Skill 通过学习请求协议贡献知识
