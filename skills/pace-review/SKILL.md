---
description: Use when user says "review", "审核", "帮我看看", "代码审查", "提交审核", "Gate 2", "提交审批", "pace-review", or when a change request reaches in_review state. NOT for running tests or acceptance verification (use /pace-test).
allowed-tools: Read, Write, Edit, Glob, Bash, AskUserQuestion
argument-hint: "[<关键词>]"
model: opus
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: prompt
          prompt: "You are a devpace review gate. During /pace-review, only the following writes are allowed: 1) Updating CR status from in_review to approved (ONLY after explicit human approval in the conversation) 2) Updating CR event table with review notes 3) Recording review rejection and returning to developing. BLOCK any write that changes CR status to approved without clear human approval text in the conversation. Input context: $ARGUMENTS"
          timeout: 15
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

对每个待 review 的 CR，读取 `review-procedures.md` 执行：

1. **意图一致性检查**：对比 CR 意图 section 与 `git diff` 实际变更（简单 CR 跳过）
2. **输出摘要**：包含改了什么、为什么改、影响范围、意图匹配、质量检查状态

详细操作步骤和摘要格式见 `review-procedures.md`。

### Step 3：等待人类决策

处理人类回复（approved / 打回 / 具体修改意见），详细动作见 `review-procedures.md`。

## 输出

Review 摘要 + 等待用户决策。
