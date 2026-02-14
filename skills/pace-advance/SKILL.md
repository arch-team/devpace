---
description: Advance a development task through the workflow. Use when user says "开始做", "继续", "推进", "pace-advance", or wants to progress on a specific feature.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash
---

# /pace-advance — 推进变更请求

进入推进模式，开始或继续推进一个变更。

## 输入

$ARGUMENTS：
- （空）→ 自动选择 state.md 中的"下一步"
- `<功能描述>` → 指定要推进的功能（自然语言匹配）

## 流程

### Step 1：定位变更请求

- 有参数 → 在 `.devpace/backlog/` 中按标题关键词匹配
- 无参数 → 读取 `.devpace/state.md` 的"下一步"
- 未找到对应 CR → 自动创建（格式参考 Plugin `knowledge/_schema/cr-format.md`）
- 找到被阻塞的 CR → 告知用户阻塞原因，建议替代

### Step 2：加载上下文

1. 读取 CR 文件：状态、质量检查、事件记录
2. 读取 `.devpace/rules/workflow.md`：当前阶段的准出条件
3. 读取 `.devpace/rules/checks.md`：质量检查检查项
4. 用 1 句话告知用户："从 [上次进度] 继续。"

### Step 3：自治推进

进入推进模式，自主工作。遵循 `rules/devpace-rules.md` 的推进模式规则：

- 编码、测试、验证——不需要用户确认每一步
- 质量检查不通过 → 自行修复重试
- 每个原子步骤后：git commit + 更新 CR 事件 + 更新 state.md

停止条件（满足任一）：
a. 所有自动质量检查通过 → 到达 in_review → 自动运行 `/pace-review` 逻辑
b. 遇到需要用户决策的技术问题 → 询问用户
c. 会话即将结束 → 保存 checkpoint

### Step 4：更新状态

1. 更新 CR 文件（质量检查 checkbox、事件记录）
2. 更新 `.devpace/state.md`（当前进度、下一步）
3. 检查关联 PF：如果所有 CR 完成 → 更新 project.md 功能树

## 输出

推进结果摘要（3-5 行）。
