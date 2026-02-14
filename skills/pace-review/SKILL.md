---
description: Generate review summary for completed changes. Use when user says "review", "审核", "pace-review", or when a change request reaches review_ready state.
allowed-tools: Read, Write, Edit, Glob, Bash
---

# /pace-review — 生成 Review 摘要

为到达 review_ready 状态的变更请求生成人类可读的审核摘要。

## 输入

$ARGUMENTS：
- （空）→ 处理所有 review_ready 的 CR
- `<关键词>` → 指定特定变更

## 流程

### Step 1：识别待 review 的变更

扫描 `bizdevops/backlog/` 找状态为 review_ready 的 CR 文件。如果没有，告知用户。

### Step 2：生成摘要

对每个待 review 的 CR，输出：

```
## [自然语言标题]

**改了什么**：[变更的文件和内容描述]
**为什么改**：[关联的产品功能 → 业务需求]
**影响范围**：[是否影响其他组件]
**门禁状态**：
  ✅ [已通过的自动门禁]
  ⏳ 人类审批

**分支**：feature/xxx
```

如需要，运行 `git diff main...feature/xxx --stat` 提供变更统计。

### Step 3：等待人类决策

| 用户回复 | 动作 |
|---------|------|
| "approved" / "通过" / "lgtm" | 更新 CR → approved，执行 git merge，更新 state.md |
| "打回" + 原因 | 更新 CR → developing，记录打回原因和时间到事件表 |
| 具体修改意见 | Claude 自行修改后重新检查门禁，再次提交 review |

## 输出

Review 摘要 + 等待用户决策。
