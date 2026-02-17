---
description: Generate review summary for completed changes. Use when user says "review", "审核", "pace-review", or when a change request reaches in_review state.
allowed-tools: Read, Write, Edit, Glob, Bash
argument-hint: "[<关键词>]"
---

# /pace-review — 生成 Review 摘要

为到达 in_review 状态的变更请求生成人类可读的审核摘要。

## 输入

$ARGUMENTS：
- （空）→ 处理所有 in_review 的 CR
- `<关键词>` → 指定特定变更

## 流程

### Step 1：识别待 review 的变更

扫描 `.devpace/backlog/` 找状态为 in_review 的 CR 文件。如果没有，告知用户。

### Step 2：生成摘要

对每个待 review 的 CR：

**2a. 意图一致性检查**（如果 CR 有范围和验收条件）

1. 读取 CR 的意图 section（范围 + 验收条件）
2. 运行 `git diff main...feature/xxx` 获取实际变更
3. 对比：验收条件是否满足？是否有范围外改动？是否有范围内未完成的？
4. 如果意图 section 只有用户原话（简单 CR），跳过此步

**2b. 输出摘要**

```
## [自然语言标题]

**改了什么**：[变更的文件和内容描述]
**为什么改**：[关联的产品功能 → 业务需求]
**影响范围**：[是否影响其他组件]

**意图匹配**：（仅标准/复杂 CR 显示）
  ✅ 验收条件 1：[描述] — 已满足
  ⚠️ 范围外改动：[描述] — [原因]

**质量检查状态**：
  ✅ [已通过的自动质量检查]
  ⏳ 人类审批

**分支**：feature/xxx
```

如需要，运行 `git diff main...feature/xxx --stat` 提供变更统计。

### Step 3：等待人类决策

| 用户回复 | 动作 |
|---------|------|
| "approved" / "通过" / "lgtm" | 更新 CR → approved，执行 git merge，更新 state.md |
| "打回" + 原因 | 更新 CR → developing，记录打回原因和时间到事件表 |
| 具体修改意见 | Claude 自行修改后重新检查质量检查，再次提交 review |

## 输出

Review 摘要 + 等待用户决策。
