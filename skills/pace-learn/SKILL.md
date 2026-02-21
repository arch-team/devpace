---
description: Immediate knowledge extraction after CR merge, gate failure recovery, or human rejection. Auto-invoked to accumulate patterns in insights.md.
user-invocable: false
allowed-tools: Read, Write, Edit, Glob
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

1. 读取触发 CR 的完整事件表和质量检查记录
2. 分析关键决策点和转折事件
3. 提炼 1 个可复用的经验规律

### Step 3：对比与积累

1. 读取 `.devpace/metrics/insights.md`
2. 检查是否已存在相似 pattern：
   - **已存在且吻合** → 在该 pattern 下追加验证记录：`再次验证：[日期] [数据]`
   - **已存在但矛盾** → 标注存疑：`存疑：[日期] [反例数据]`
   - **不存在** → 追加新 pattern

### Pattern 格式

```
### [日期] [pattern 标题]

**类型**：成功 | 防御 | 改进
**观察**：[从事件中观察到的现象]
**规律**：[提炼的可复用经验]
**证据**：[支持该规律的具体数据]
**建议**：[基于该规律的行动建议]
```

### Step 4：静默完成

- 不输出任何内容给用户（静默执行）
- 仅在 insights.md 写入变更时 git commit（消息：`chore(knowledge): extract pattern from CR-xxx`）

## 输出

无用户可见输出。insights.md 文件更新。

## 约束

- 每次触发最多提取 1 个 pattern（质量优先于数量）
- 不修改 CR 文件或其他状态文件
- 不中断当前工作流
