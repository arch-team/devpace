---
description: Use when user says "开始做", "帮我改", "实现", "修复", "继续推进", "编码", "写代码", "开发", "重构", "做个", "coding", "implement", "fix", "refactor", "build", /pace-dev, or explicitly requests to start, continue, or resume coding/development work on a feature or bug fix. "帮我改" applies when the target is code, UI, or configuration — not requirements or acceptance criteria. NOT for requirement changes (use /pace-change) or code review (use /pace-review). NOT for running tests (use /pace-test). NOT for user-reported production issues (use /pace-feedback).
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash
argument-hint: "[<功能描述>|#<CR编号>|--last]"
context: fork
agent: pace-engineer
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/pace-dev-scope-check.mjs"
          timeout: 5
---

# /pace-dev — 推进变更请求

进入推进模式，开始或继续推进一个变更。

## 输入

$ARGUMENTS：
- （空）→ 自动选择 state.md 中的"下一步"
- `<功能描述>` → 指定要推进的功能（自然语言匹配）
- `#<N>` → 按 CR 编号直接定位（如 `#3` → CR-003）
- `--last` → 定位上一个操作过的 CR（从 state.md 或最近 git log 推断）

## 执行路由

**重要**：根据 CR 的当前状态和类型，仅读取对应的 procedures 文件，不加载其他 procedures。

### 固定加载

| 文件 | 说明 |
|------|------|
| `dev-procedures-common.md` | 通用规则（始终加载） |

### 按 CR 状态加载

| CR 状态 | 加载文件 | 说明 |
|---------|---------|------|
| `created`（首次进入 developing） | `dev-procedures-intent.md` | 意图检查点 + 复杂度评估 + 执行计划 |
| `developing`（已在推进中） | `dev-procedures-developing.md` | 漂移检测 + 步骤隔离 + checkpoint |
| `verifying` / `in_review` | `dev-procedures-gate.md` | Gate 通过反思 |
| `merged` / CR 新创建 | `dev-procedures-postmerge.md` | 功能发现 + PF 溢出检查 |

### 按 CR 类型追加加载

| CR 类型 | 追加文件 | 说明 |
|---------|---------|------|
| `defect` / `hotfix` | `dev-procedures-defect.md` | 特殊创建 + 修复后处理 |

## 流程

### Step 1：定位变更请求

- `#N` 参数 → 直接读取 `.devpace/backlog/CR-00N.md`（编号补零匹配）
- `--last` 参数 → 从 state.md "进行中"项推断，或 `git log --oneline -5` 中最近操作的 CR
- 有自然语言参数 → 在 `.devpace/backlog/` 中按标题关键词匹配
- 无参数 → 读取 `.devpace/state.md` 的"下一步"
- 未找到对应 CR → 自动创建（格式参考 Plugin `knowledge/_schema/cr-format.md`）并更新 project.md 价值功能树（在匹配的 PF 行追加 `→ CR-xxx ⏳`）
- 找到被阻塞的 CR → 告知用户阻塞原因，建议替代

**CR 类型判断**：
- 用户意图为修复缺陷 → type:defect（触发词："修复""fix""bug""缺陷"）
- 用户意图为紧急修复 → type:hotfix（触发词："紧急""hotfix""线上问题""生产故障"）
- 其他 → type:feature（默认）
- defect/hotfix 必须填写 severity，由 Claude 根据描述自动建议

### Step 2：加载上下文

1. 读取 CR 文件：状态、质量检查、事件记录
2. 读取 `.devpace/rules/workflow.md`：当前阶段的准出条件
3. 读取 `.devpace/rules/checks.md`：质量检查检查项
4. 用 1 句话告知用户："从 [上次进度] 继续。"

### Step 2.5：意图检查点

> 仅在 CR 状态为 created（首次进入 developing）时执行。已在 developing 或更后阶段的 CR 跳过此步。

根据 CR 状态和类型，按上方执行路由表加载对应的 procedures 文件。根据变更复杂度（简单/标准/复杂）自适应执行意图明确。对用户只说"明确了范围，开始做。"

### Step 3：自治推进

进入推进模式，自主工作。遵循推进模式行为约束（`rules/devpace-rules.md` §2）和按执行路由表加载的 procedures 文件（权威源）：

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
3. 更新 project.md 功能树中关联 CR 的状态 emoji（如 ⏳→🔄→✅）；如果 PF 的所有 CR 均 merged → PF 行 emoji 更新为 ✅

## 输出

推进结果摘要（3-5 行）。
