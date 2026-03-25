# 教学内容目录

> **职责**：存放渐进教学系统（devpace-rules.md §15）的教学文案。首次触发对应行为时，从本文件读取教学内容。

## 教学触发表

| 行为 | 触发时机 | 教学内容（≤1 句话） | 标记值 |
|------|---------|-------------------|--------|
| 自动创建 CR | 首次在推进模式创建 CR 时 | "（devpace 自动跟踪每个变更，方便后续追溯和恢复。）" | `cr` |
| Gate 1 质量检查 | 首次执行 Gate 1 时 | "（自动检查代码质量，不通过会自行修复，不需要你操心。）" | `gate1` |
| 等待 review | 首次进入 in_review 时 | "（这是唯一需要你确认的环节——确保变更符合预期。）" | `review` |
| 变更意图检测 | 首次检测到变更意图时 | "（devpace 会先分析影响再调整，避免连锁混乱。）" | `change` |
| 功能树更新 | 首次更新 project.md 功能树时 | "（功能树自动记录目标到代码的关系，随工作自然生长。）" | `tree` |
| merged 连锁更新 | 首次执行 merged 后连锁更新时 | "（合并后自动更新所有关联状态，保持一致。）" | `merge` |
| AI 验收验证 | 首次执行 /pace-test accept 时 | "（accept 为人类审批提供逐条验收证据和改进建议，让 Gate 3 更高效。详见 /pace-test。）" | `accept` |
| 同步配置 | 首次运行 /pace-sync setup 时 | "（同步配置让 devpace 状态自动映射到 GitHub Issue 标签。）" | `sync_setup` |
| 状态推送 | 首次运行 /pace-sync push 时 | "（push 将 CR 状态变化同步到外部工具，保持项目管理工具和实际进度一致。）" | `sync_push` |
| Issue 自动创建 | 首次在 CR 创建后提议创建外部 Issue 时 | "（检测到同步配置，可以自动在 GitHub 创建对应 Issue 并关联。）" | `sync_create` |
| 关联外部实体 | 首次运行 /pace-sync link 时 | "（link 将 CR 与外部 Issue 一一对应，后续 push 会自动同步状态变化。）" | `sync_link` |
| 预览同步操作 | 首次使用 --dry-run 参数时 | "（dry-run 预览将要执行的操作但不实际执行，可安全确认后再推送。）" | `sync_dryrun` |
| 同步状态不一致 | 首次检测到 devpace 与外部状态不一致时 | "（外部状态可能被其他人修改，push 会将 devpace 状态同步过去。）" | `sync_conflict` |
| 自动关联 | 首次 CR 创建时触发 auto-link/create 建议时 | "（检测到同步配置，自动匹配外部 Issue。修改偏好：编辑 sync-mapping.md '自动同步'字段。）" | `sync_auto` |
| Gate 结果同步 | 首次 Gate 通过/失败后推送到外部时 | "（Gate 结果会自动同步到关联的外部 Issue，团队成员可在 GitHub 看到质量门状态。）" | `gate_sync` |
| 层级映射 | 首次建立 sub-issue 层级关系时 | "（devpace 将 PF→CR 层级映射为 GitHub sub-issue 关系，团队可在 Issue 层级中看到完整追踪链。）" | `sync_hierarchy` |
| 推进模式 opt-in | 首次向用户确认推进模式后用户同意时 | "（下次你说'开始做'，我会直接进入管理模式，不再确认。）" | `opt-in-explained` |
| context.md 自动生成 | 首次在推进时自动创建 context.md 时 | "（根据项目配置自动生成了技术约定，推进时会参考这些规则。）" | `context_generated` |
| 反馈追踪 | 首次通过 /pace-feedback 创建 defect/hotfix CR 时 | "（每条反馈有唯一 FB-ID，从报告到修复全程可追踪。）" | `feedback_report` |
| 风险文件创建 | 首次通过 scan 创建 .devpace/risks/RISK-xxx.md 时 | "（首次创建风险文件，后续趋势分析将自动基于此数据。）" | `risk_file_created` |
| 首次知识积累 | 首个 CR merged + insights.md 创建或首次写入时 | "（devpace 会从每次成功交付中提炼经验，并在后续开发中自动引用。）" | `first_merged` |
| 经验导出 | 知识库积累超过 5 条高置信度 pattern 时首次 merged 后 | "（知识库已积累 N 条高质量经验，可用 /pace-learn export 导出到其他项目复用。）" | `learn_export` |
| 角色适配输出 | 首次 pace-status 按角色适配输出时 | "（当前按 [角色] 视角输出，可切换：/pace-role [biz\|pm\|dev\|tester\|ops]。）" | `role_adapt` |
| 角色自动推断 | 首次自动推断非 Dev 角色时 | "（devpace 检测到你在讨论 [线索]，自动调整到 [角色] 视角。切换：/pace-role。）" | `role_infer` |
| 初始化完成引导 | /pace-init 正常初始化或 --full 完成时 | "（项目已就绪。说'帮我做 [功能名]'开始第一个功能，或 `/pace-plan` 规划迭代。）" | `init_complete` |
