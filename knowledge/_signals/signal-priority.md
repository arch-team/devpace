# 信号优先级统一定义

> **职责**：定义 devpace 全局信号优先级的唯一权威源（SSOT）。pace-next / pace-pulse session-start / pace-status 概览均引用本文件，不自行维护独立优先级表。

## §0 速查卡片

**优先级分组**：Blocking → In Progress → Delivery → Strategic → Growth（含 Epic/OPP/discover 信号）→ Idle

**引用方式**：各 Skill 按"可见信号子集"列选择性暴露。修改任何信号的条件或编号时，同步检查三个消费方。

## 信号分组与定义

### Blocking（全局阻塞——所有角色同等优先级）

| ID | 信号 | 条件 | 建议模板 | 命令引导 | status-subset |
|:--:|------|------|---------|---------|:------------:|
| S1 | 审批阻塞 | `backlog/` 中 `in_review` CR > 0 | "有 N 个变更等你审批——审批后才能合并推进" | → /pace-review | ✅ |
| S2 | 高风险阻塞 | `.devpace/risks/` 中 High 严重度且 open 状态风险 > 0 | "有 N 个高级别风险需要处理——高风险不可绕过人类确认" | → /pace-guard report | ❌ |

### In Progress（继续工作——维持工作流连续性）

| ID | 信号 | 条件 | 建议模板 | 命令引导 | status-subset |
|:--:|------|------|---------|---------|:------------:|
| S3 | 继续开发 | `backlog/` 中存在 `developing` CR | "继续 [CR 标题]（[PF 名] 的一部分）——上次停在 [state.md 进行中摘要]" | → /pace-dev 或说"继续" | ✅ |
| S4 | 恢复暂停 | `backlog/` 中 `paused` CR 且阻塞原因已解除 | "[CR 标题] 之前暂停，现在可以继续（属于 [PF 名]）" | → /pace-change resume [CR] | ❌ |

### Delivery（交付推进——推动价值交付管道）

| ID | 信号 | 条件 | 建议模板 | 命令引导 | status-subset |
|:--:|------|------|---------|---------|:------------:|
| S5 | Release 待验证 | `releases/` 中存在 `deployed` 未 `verified` 的 Release | "[Release 名] 已部署待验证" | → /pace-release | ✅ |
| S6 | 风险积压 | `.devpace/risks/` 中 open 风险 > 3（且非 High——High 已被 S2 捕获） | "有 N 个未处理中等风险，建议及时处理" | → /pace-guard report | ❌ |
| S7 | 迭代时间紧迫 | `current.md` 距结束 < 2 天且 PF 完成率 < 50% | "迭代即将结束但完成率不足——考虑调整范围" | → /pace-plan adjust | ❌ |
| S8 | 迭代接近完成 | `current.md` PF 完成率 > 80% | "迭代接近完成——回顾后规划下一迭代" | → /pace-retro 后 /pace-plan | ✅ |

### Strategic（战略关注——回顾与优化）

| ID | 信号 | 条件 | 建议模板 | 命令引导 | status-subset |
|:--:|------|------|---------|---------|:------------:|
| S9 | 回顾提醒 | `dashboard.md` 最近更新距今 > 7 天 + `backlog/` 有 merged CR | "有新完成的工作，建议做一次回顾" | → /pace-retro | ✅ |
| S10 | 缺陷占比高 | `backlog/` 中 defect 类型 CR 占比 > 30% | "缺陷比例较高，建议优先修复" | → /pace-guard report | ❌ |
| S11 | 同步滞后 | `sync-mapping.md` 存在 + 已关联 CR 状态变更未推送 > 24h | "有 N 个 CR 外部同步已滞后" | → /pace-sync push | ❌ |
| S12 | MoS 达成回顾 | `project.md` MoS 达成率 > 80% | "目标接近达成，回顾成效指标" | → /pace-retro | ❌ |

### Growth（增长机会——新价值开拓）

| ID | 信号 | 条件 | 建议模板 | 命令引导 | status-subset |
|:--:|------|------|---------|---------|:------------:|
| S13 | 功能未开始 | `project.md` 有 PF 无对应 CR | "功能 [PF 名] 还没开始——是 [BR 名] 的关键组成" | → 说"帮我实现 [PF 名]" | ✅ |
| S14 | 规划新迭代 | 上一迭代已关闭 + `current.md` 不存在 | "上一迭代已结束——规划新迭代" | → /pace-plan | ❌ |
| S15 | 全部完成 | `backlog/` 全部 CR 为 merged 或 released | "所有任务完成——开始新功能或回顾" | 自然语言 | ✅ |
| S16 | Epic 需分解 | `epics/` 中有 `规划中` 状态 Epic 且 BR 列表为空 | "专题 [Epic 名] 已创建但还没分解为需求" | → /pace-biz decompose [EPIC] | ❌ |
| S17 | 未评估机会 | `opportunities.md` 中有 `评估中` 状态 Opportunity > 0 | "有 N 个业务机会待评估" | → /pace-biz epic [OPP] | ❌ |
| S18 | 功能树稀疏 | `project.md` PF 数量 < 3 且项目创建 > 7 天 | "功能树还很稀疏，建议探索需求或从文档导入" | → /pace-biz discover 或 /pace-biz import | ❌ |
| S19 | 范围未定义 | `project.md` "范围" section 为桩或不存在 | "项目范围尚未定义，建议通过需求发现明确边界" | → /pace-biz discover | ❌ |
| S21 | 跨 CR 依赖阻塞 | `backlog/` 中 CR-A `blocked_by` 字段指向 CR-B 且 CR-B 状态非 merged/developing 超 3 天（`blocked_by` 字段存在时才检测） | "[CR-A] 被 [CR-B] 阻塞且 [CR-B] 已 N 天未推进" | → /pace-dev #B 或 /pace-change reprioritize | ❌ |
| S22 | 技术债积压 | `backlog/` 中 `tech-debt` 类型 CR 占比 > 30% 或数量 > 5 | "技术债务 CR 占比偏高（N%），建议安排偿还" | → /pace-plan adjust | ❌ |
| S24 | 首次循环引导 | `backlog/` 中无 merged 状态 CR 且存在 ≥1 个 developing CR | "第一个功能正在进行中——完成后 /pace-review 审批即可体验完整循环" | 自然语言 | ❌ |

### Idle（无信号）

| ID | 信号 | 条件 | 建议模板 | 命令引导 | status-subset |
|:--:|------|------|---------|---------|:------------:|
| S20 | 无信号 | 无任何信号命中 | "当前无紧急事项，可以自由探索或规划新目标" | 自然语言 | ❌ |

## 角色重排序规则

S1-S2（Blocking 组）**不受角色影响**，全角色同等最高优先级。

S3-S15 范围内，以下角色可在组内重排序（提升最多 1 个组级别）：

| 角色 | 提升信号 | 降低信号 | 理由 |
|------|---------|---------|------|
| PM | S8（迭代完成）、S13（功能未开始） | S10（缺陷占比）—— 不降级但不主动提升 | PM 关注功能交付和迭代目标 |
| Biz | S12（MoS 达成）、S13（功能未开始） | S3（继续开发）—— 不降级但不主动提升 | Biz 关注业务目标达成 |
| Ops | S5（Release 待验证）、S11（同步滞后） | S13（功能未开始）—— 不降级但不主动提升 | Ops 关注部署和运维 |
| Tester | S10（缺陷占比高）、S6（风险积压） | S14（规划新迭代）—— 不降级但不主动提升 | Tester 关注质量和风险 |
| Dev（默认） | 无调整 | 无调整 | 默认排序 |

**重排序约束**：提升操作将目标信号移到组内第一位或提升一个组级别（不跨越两个组）。detail 模式下标注 `（[角色]关注）`。

## 消费方引用规则

| 消费方 | 可见子集 | 引用方式 |
|--------|---------|---------|
| pace-next | 全部 S1-S24 | 从高到低遍历，取首个命中；detail 模式取 top-3 |
| pace-status 概览 | `status-subset = ✅` 的信号（S1/S3/S5/S8/S9/S13/S15） | 取 top-1，追加"（详情 → /pace-next）" |
| pace-pulse session-start | 全部（独立阈值版本，见 pulse-procedures-session-start.md） | 分层摘要 ≤3 行 |

**去重规则**：pace-status 概览在距会话开始 < 5 分钟时省略建议行（session-start 刚给过）。pace-next 在距 session-start < 5 分钟时跳过已通知的最高信号，直接给出第二条。

## 修改协议

修改本文件时必须同步检查：

1. `skills/pace-next/SKILL.md` — Step 2 数据源表 + Step 3 信号分组摘要（内联副本）
2. `skills/pace-next/next-procedures-output-default.md` — 命令引导与行为预览表
3. `skills/pace-next/next-procedures.md` — 信号条件详述
4. `skills/pace-status/status-procedures-overview.md` — 概览子集引用
5. `skills/pace-pulse/pulse-procedures-session-start.md` — 如有同名信号
6. `rules/devpace-rules.md` — 如有规则引用

## Consumers

rules, pace-next, pace-status, pace-pulse
