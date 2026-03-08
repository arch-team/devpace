# pace-pulse 会话开始节奏检测

> **职责**：定义会话开始（§1）时的信号检测逻辑。由 `SKILL.md` 路由表指定加载。

## 与核心脉搏检查的关系

本文件的信号集独立于 `pulse-procedures-core.md` 的周期性检查信号。在以下重叠领域，阈值策略不同：

| 领域 | 本文件阈值 | Core 阈值 | 修改时需同步？ |
|------|-----------|-----------|--------------|
| Review 积压 | >0 | >2 | 否（场景差异，独立调整） |
| 风险积压 | >3 或 High>0 | 相同 | 是 |
| 迭代完成率 | >80% | >80% | 是 |
| 目标回顾逾期 | >14 天 | >14 天 | 是 |

新增 core 信号时，评估是否需要对应的会话开始版本。

## 数据源

- `.devpace/metrics/dashboard.md` 的"最近更新"日期（**目录不存在时跳过**）
- `.devpace/backlog/` 中状态为 `in_review` 的 CR 数量
- `.devpace/backlog/` 中状态为 `merged` 的 CR 数量（**目录不存在或无任何 merged CR 时视为 0，用于 onboarding 信号判定**）
- `.devpace/iterations/current.md`（**文件不存在时跳过迭代相关检测**）

## 信号优先级（分层摘要，≤3 行）

**分层输出规则**：最高优先级信号以完整建议呈现（1 行），其余触发的信号合并为精简列表（1 行，格式：`另外注意：[信号A]、[信号B]`），总输出不超过 3 行。

**与 /pace-status 推/拉去重**：session-start 是"推送式"快照，/pace-status 是"拉取式"详情。去重规则见 `skills/pace-status/status-procedures-overview.md` "推/拉去重"节（pace-status 侧执行抑制）。两者互补不重复。

| 优先级 | 条件 | 提醒 |
|--------|------|------|
| 0 | `.devpace/` 存在 + backlog/ 中 merged CR = 0（目录不存在或为空也视为 0） | "首次使用——试试说"帮我实现 [功能名]"开始第一个功能，或用 `/pace-biz discover` 从业务目标出发" |
| 1 | in_review CR > 0 | "有 N 个变更等待 review——`/pace-review`" |
| 2 | deployed 未 verified Release | "有未验证的 Release——`/pace-release verify`" |
| 3 | 迭代完成率 > 80% | "迭代接近完成——`/pace-plan next`" |
| 4 | 距 retro > 7 天 + merged CR | "已有交付成果可回顾——`/pace-retro`" |
| 5 | defect 占比 > 30% | "缺陷占比偏高，关注质量改进——`/pace-guard report`" |
| 6 | MoS 达成率 > 80% | "业务指标接近达成，建议回顾目标——`/pace-retro`" |
| 7 | 风险积压（`.devpace/risks/` 存在且 open 风险 > 3 或 High > 0） | "有 [N] 个未处理风险——`/pace-guard report`" |
| 8 | sync-mapping.md 存在 + 关联 CR 最后同步 > 24h | "有 N 个 CR 外部同步已滞后——`/pace-sync push`" |
| 9 | dashboard.md 最近更新 > 14 天 + MoS 有未勾选项 | "距上次回顾已超 2 周——`/pace-retro`" |
| 10 | Snooze 条目触发条件满足（CR 事件表/迭代变更记录） | "之前延后的变更触发条件已满足（详情见 `pulse-procedures-snooze.md`）" |
| 11 | 用户对话含运维关键词 + pace-feedback 未在本会话使用 | "检测到生产问题描述——`/pace-feedback report`" |
