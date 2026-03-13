---
description: Use when user says "review", "审核", "帮我看看", "代码审查", "提交审核", "Gate 2", "提交审批", "pace-review", or when a change request reaches in_review state. NOT for running tests or acceptance verification (use /pace-test).
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Bash
argument-hint: "[<关键词>]"
model: opus
context: fork
agent: pace-engineer
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/pace-review-scope-check.mjs"
          timeout: 5
---

# /pace-review — 生成 Review 摘要

为到达 in_review 状态的变更请求生成人类可读的审核摘要。追溯链展示至 Epic 层（CR→PF→BR→Epic→OBJ）。

## 输入

$ARGUMENTS：
- （空）→ 处理所有 in_review 的 CR
- `<关键词>` → 指定特定变更

## 流程

### Step 1：识别待 review 的变更

扫描 `.devpace/backlog/` 找状态为 in_review 的 CR 文件。

如果没有 in_review 的 CR，按以下顺序做状态感知引导（用户不需要理解状态机）：
1. 有 `verifying` 状态的 CR → 提示"CR-xxx 正在验证中（Gate 2 自动检查），检查完成后会自动进入 Review。要先看看当前质量检查进度吗？"
2. 只有 `developing` 状态的 CR → 提示"CR-xxx 还在开发中。需要先推进到 review 阶段吗？"
3. 无活跃 CR → 告知用户当前没有待审查的变更

### Step 2：确定 Review 模式并按需加载

重要：根据 Review 模式和 CR 复杂度，仅读取对应的 procedures 文件，不加载全部规程。

**固定加载**：

| 文件 | 说明 |
|------|------|
| `review-procedures-common.md` | 通用规则（始终加载） |

**按 Review 模式和复杂度加载**：

| 模式 | 条件 | 额外加载文件 |
|------|------|-------------|
| 中断恢复 | CR 验证证据有已生成摘要 + 代码无变更 | 无（仅用 common） |
| 增量 Review（S 级） | 打回历史 + S 级 | `review-procedures-delta.md`（自包含） |
| 增量 Review（M+ 级） | 打回历史 + M+ 级 | `review-procedures-delta.md` + `review-procedures-gate.md` |
| 全量 Review（S 级） | 首次 review，S 级 | 无（common 含 S 级格式） |
| 全量 Review（M+ 级） | 首次 review，M+ 级 | `review-procedures-gate.md` |

**后续按需加载**：

| 触发条件 | 加载文件 |
|---------|---------|
| 用户打回或给出修改意见 | `review-procedures-feedback.md`（自包含） |

### Step 3：生成摘要

对每个待 review 的 CR 执行：

1. **交叉影响扫描**：检测多活跃 CR 间的文件/模块重叠
2. **意图一致性检查**：对比 CR 意图与 `git diff` 实际变更（简单 CR 跳过），含推理后缀
3. **业务追溯**：CR → PF → BR 完整价值链追溯
4. **对抗审查**：强制发现问题（M/L/XL），联动 accept 报告弱覆盖区域
5. **输出摘要**：按复杂度分级——S 微型 / M 标准 / L-XL 完整+TL;DR
6. **持久化**：将摘要写入 CR 验证证据 section

详细操作步骤和摘要格式见已加载的 procedures 文件。

### Step 4：等待人类决策

处理人类回复（approved / 打回 / 修改意见 / 探索性问题），详细动作见已加载的 procedures 文件。

## 输出

Review 摘要 + 等待用户决策。
