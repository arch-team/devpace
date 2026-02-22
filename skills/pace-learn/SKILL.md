---
description: Auto-invoked after CR merge, gate failure recovery, or human rejection.
user-invocable: false
allowed-tools: Read, Write, Edit, Glob
model: sonnet
---

# pace-learn — 即时知识积累

Claude 自动调用的知识提取 Skill，不暴露给用户。在关键事件后即时提取经验 pattern，追加到 `.devpace/metrics/insights.md`。

## 触发条件

由 `rules/devpace-rules.md` §11 定义触发时机：
- CR 状态变为 merged 后
- 质量门首次失败后成功修复
- 人类打回 CR（in_review → developing）后

## 流程

### Step 1：识别学习事件

根据触发源确定提取方向：

| 触发源 | 提取方向 |
|--------|---------|
| CR merged | 成功 pattern：什么做法效果好 |
| 质量门修复 | 防御 pattern：什么容易出错、如何避免 |
| 人类打回 | 改进 pattern：人类关注点、设计质量提升 |

### Step 2：提取 Pattern

读取 `learn-procedures.md` Step 2，从触发 CR 的事件表和质量检查记录中提炼 1 个可复用经验规律。

### Step 3：对比与积累

读取 `learn-procedures.md` Step 3，与 `.devpace/metrics/insights.md` 已有 pattern 对比，追加新 pattern 或标注验证/存疑。

### Step 4：静默完成

- 不输出任何内容给用户（静默执行）
- 仅在 insights.md 写入变更时 git commit（消息：`chore(knowledge): extract pattern from CR-xxx`）

## 输出

无用户可见输出。insights.md 文件更新。

## 约束

- 每次触发最多提取 1 个 pattern（质量优先于数量）
- 不修改 CR 文件或其他状态文件
- 不中断当前工作流
