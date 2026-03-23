# IR-2 Hook 执行机制架构说明

> **职责**：说明 Gate 3 人类审批的 Hook 强制执行架构。被 `rules/devpace-rules.md` IR-2 引用。

## 架构特性

Gate 3 由全局 `pre-tool-use.mjs` command Hook 强制执行——当检测到 CR 当前状态为 `in_review` 且写入内容包含 `approved` 时无条件阻断（exit 2）。

- 全局 Hook 和 Skill 级 Hook **并行执行、互不覆盖**——Skill 级 Hook 无法 override 全局阻断
- 全局 Hook 是确定性检查（正则匹配），无法感知对话上下文中用户是否已批准
- 因此 Claude 首次尝试写入 `approved` 时必然被阻断，阻断消息反馈给 Claude 后由 Claude 告知用户
- 用户确认后 Claude 重试写入时仍会触发 Hook——此时 Claude 应先通过 Bash 工具执行状态变更（Bash 不受 Write|Edit 的 PreToolUse Hook 约束），或采用两步写入（先写中间内容再补状态字段）
- 简化审批和批量审批的"用户说'好/合并'"本质是触发上述人机交互循环
