# devpace BizDevOps 全生命周期审查与重构方案

## Context

devpace 是一个 Claude Code Plugin，目标是为 AI 辅助开发提供完整的 BizDevOps 研发节奏管理。当前项目非常成熟（127/131 任务完成，42/42 场景覆盖），拥有 19 个 Skills、3 个 Agent、~113 个 procedures 文件、19 个 schema 文件。

本方案从**宏观到微观、整体到局部、粗粒度到细粒度**四个维度审查 devpace，并按 P0-P3 优先级提供分层重构方案，目标是让 devpace 成为世界上最优秀的 BizDevOps 全生命周期 AI 工具。

---

## Part I: 宏观审查 — BizDevOps 生命周期完整性

### 1.1 生命周期覆盖矩阵

| BizDevOps 阶段 | 子活动 | 覆盖 Skill | 覆盖度 | 评估 |
|---------------|--------|-----------|--------|------|
| **业务机会** | 机会捕获、评估、采纳 | pace-biz opportunity | FULL | 完整 |
| **战略对齐** | OBJ 关联、MoS 追踪 | pace-biz align | FULL | 完整 |
| **需求发现** | 交互式探索、文档导入、代码推断 | pace-biz discover/import/infer | FULL | 完整 |
| **需求分解** | Epic->BR->PF 分解 | pace-biz decompose | FULL | 完整 |
| **迭代规划** | 规划/关闭/调整/健康度 | pace-plan | FULL | 完整 |
| **开发执行** | CR 创建/编码/测试/质量门 | pace-dev | FULL | 完整 |
| **代码审查** | Gate 3 审批准备 | pace-review | FULL | 完整 |
| **测试验证** | 策略/覆盖/验收/影响分析 | pace-test | FULL | 完整 |
| **需求变更** | 插入/暂停/恢复/修改/批量 | pace-change | FULL | 完整 |
| **风险管理** | 扫描/监控/趋势/报告 | pace-guard | FULL | 完整 |
| **发布管理** | 创建/部署/验证/关闭/回滚 | pace-release | FULL | 完整 |
| **运维反馈** | 反馈收集/事件追溯/热修 | pace-feedback | FULL | 完整 |
| **度量回顾** | 迭代回顾/DORA/趋势/预测 | pace-retro | FULL | 完整 |
| **外部集成** | GitHub/Linear/Jira 同步 | pace-sync | PARTIAL | Phase 19-20 待完成 |
| **知识沉淀** | 经验提取/知识库管理 | pace-learn | FULL | 完整 |
| **决策审计** | AI 决策轨迹/ADR | pace-trace | FULL | 完整 |
| **--- 以下为缺口 ---** | | | | |
| **架构设计** | 技术方案设计、架构评审 | 无专属 Skill | GAP | 见 1.2-G1 |
| **持续集成** | CI 配置、构建自动化、流水线管理 | 仅 Gate 查询 | GAP | 见 1.2-G2 |
| **环境管理** | dev/staging/prod 环境、特性开关 | 无 | GAP | 见 1.2-G3 |
| **事件管理** | 严重性分级、升级、事后复盘 | pace-feedback 部分覆盖 | PARTIAL | 见 1.2-G4 |
| **项目 Onboarding** | 新成员引导、项目知识传递 | 无 | GAP | 见 1.2-G5 |

### 1.2 生命周期缺口分析

**G1: 架构设计活动缺失**

pace-trace 支持 ADR（架构决策记录），但这是事后记录。在开发前的"技术方案设计"环节没有对应 Skill。当用户面对 L/XL 复杂度的 PF 时，从"需求分解完成"到"开始编码"之间缺少一个结构化的技术设计步骤。

- 影响：L/XL CR 的质量门通过率可能较低（因为缺少前置技术设计）
- 建议：在 pace-dev 的 L/XL 流程中嵌入"技术方案"步骤，或新增 `/pace-design` Skill

**G2: CI/CD 管理能力薄弱**

当前 CI/CD 能力限于 Gate 4 的状态查询（checks-format.md 中的 ci-status-cmd）。无法管理流水线配置、触发构建、查看构建日志。

- 影响：Release 流程依赖用户手动管理 CI/CD
- 建议：中长期通过 MCP Server 或 pace-sync 扩展支持 CI/CD 操作

**G3: 环境管理缺失**

没有管理开发/测试/生产环境差异的能力，也没有特性开关（feature flag）管理。

- 影响：Release 验证步骤缺少环境上下文
- 建议：作为 pace-release 的子命令扩展（`/pace-release env`），或长期独立 Skill

**G4: 事件管理不完整**

pace-feedback 覆盖了反馈收集和热修复路径，但缺少结构化的事件管理：严重性分级（P0-P4）、升级链、值班轮转、事后复盘（postmortem）。

- 影响：对需要 Ops 成熟度的专业团队吸引力不足
- 建议：扩展 pace-feedback 增加 `incident` 子命令系列

**G5: 项目 Onboarding 缺失**

pace-init 创建项目骨架，pace-theory 解释方法论，但没有"引导新用户完成第一个完整 BizDevOps 循环"的结构化体验。

- 影响：新用户转化率低，学习曲线陡峭
- 建议：P0 优先级，见 Part V 重构方案

### 1.3 四大反馈闭环完整性

| 闭环 | 路径 | 完整度 | 断点 |
|------|------|--------|------|
| 业务闭环 | OBJ -> Epic -> BR -> MoS 达成 -> 回顾 | 95% | MoS 自动评估依赖人工输入 |
| 产品闭环 | BR -> PF -> 迭代 -> 回顾 -> 改进 | 98% | pace-retro accept 到下一迭代的衔接靠信号间接完成 |
| 技术闭环 | CR created -> merged (状态机) | 100% | 完整 |
| 运维闭环 | Release -> 部署 -> 反馈 -> Defect CR | 90% | 缺少结构化事件管理和 postmortem |

---

## Part II: 中观审查 — Skill 架构与互联

### 2.1 Skill 分组与粒度评估

**当前分组**（来自 devpace-rules.md 0）：

| 层级 | Skills | 评估 |
|------|--------|------|
| 核心（5） | init, dev, status, review, next | 合理，覆盖最小闭环 |
| 业务（1） | biz (8 子命令) | 子命令过多，是最大的单一 Skill |
| 进阶（6） | change, plan, retro, guard, sync, role | 合理，各自职责清晰 |
| 专项（4） | release, test, feedback, theory, trace | release 子命令最多(15 procedures) |
| 系统（2） | pulse, learn | 合理，自动调用无需用户关注 |

**粒度问题**：

| 问题 | 涉及 Skill | 分析 |
|------|-----------|------|
| pace-biz 过于庞大 | pace-biz | 8 个子命令跨越 opportunity/epic/decompose/align/view/discover/import/infer，功能跨度大 |
| pace-release 过于庞大 | pace-release | 15 个 procedures 文件，子命令含 create/deploy/verify/close/full/status/changelog/version/tag/notes/branch/rollback |
| pace-status 子命令丰富但分层合理 | pace-status | 9 个 procedures 但层次清晰（L1/L2/L3），可接受 |
| pace-theory 和 pace-trace 有概念重叠 | pace-theory, pace-trace | theory 解释"是什么"，trace 追溯"为什么这样做"，目标不同但用户可能混淆 |

**建议**：
- pace-biz：保持合并但改善 sub-routing，在 §0 速查中更清晰地区分"创建型"和"分析型"子命令
- pace-release：考虑拆分为 `pace-release`（生命周期）+ `pace-changelog`（文档生成），但复杂度增加，暂不推荐
- pace-theory + pace-trace：保持独立，但在帮助文本和 description 中更清晰地区分

### 2.2 Skill 互联拓扑分析

```
                    pace-biz
                   /    |    \
            opportunity  epic  decompose
                   \    |    /
                    pace-plan -------- pace-change
                        |                  |
                    pace-dev ---------- pace-guard
                   /    |    \            |
              Gate1  Gate2  pace-test     |
                        |                |
                    pace-review          |
                        |               |
                    [人类审批]           |
                        |               |
                    merged ---------- pace-learn
                        |               |
                    pace-release --- pace-sync
                        |
                    pace-feedback
                        |
                    pace-retro

横切: pace-status, pace-next, pace-role, pace-trace, pace-theory, pace-pulse
```

### 2.3 互联断层清单

**断层 D1: pace-biz decompose -> pace-plan 引导不一致**
- SKILL.md 推荐流程：`discover -> decompose -> /pace-plan next`
- decompose 实际输出引导：`-> /pace-change add 或 /pace-dev`
- 修复：统一 decompose 的输出引导，增加到 `/pace-plan next` 的引导
- 涉及文件：`skills/pace-biz/biz-procedures-decompose.md`

**断层 D2: pace-plan -> pace-dev 迭代绑定弱**
- pace-plan 规划了迭代并选择 PF，但 pace-dev 按单个功能描述或 CR 编号工作
- 迭代中 PF 的优先顺序仅通过 pace-next 信号间接传递（S13）
- 缺少"按迭代计划优先级自动推进下一 PF"的直接路径
- 修复：在 pace-dev merged 后的引导中，如果迭代内有未开始 PF，直接推荐迭代中最高优先级的 PF
- 涉及文件：`skills/pace-dev/dev-procedures-postmerge.md`、`knowledge/_signals/signal-priority.md`

**断层 D3: pace-retro -> pace-plan 回顾到规划的衔接**
- pace-retro 生成回顾报告和改进建议，但到下一迭代规划(pace-plan next)时需要用户手动关联
- 修复：pace-plan next 的规划流程中显式引用上一迭代 retro 的关键建议
- 涉及文件：`skills/pace-plan/plan-procedures.md`

**断层 D4: pace-guard scan 与 pace-dev 的触发门槛**
- S/M CR 仅在 insights.md 有匹配 pattern 时触发风险扫描
- 新项目 insights.md 为空，S/M CR 的风险扫描永远不会被自动触发
- 修复：新项目首 N 个 CR 默认触发基础扫描，或首次 Guard 扫描由 init 完成后的引导触发
- 涉及文件：`skills/pace-guard/guard-procedures-common.md`、`skills/pace-dev/dev-procedures-gate.md`

**断层 D5: pace-feedback -> pace-change 的反馈转需求路径**
- pace-feedback 创建 Defect/Hotfix CR 后，如果反馈表明需要新功能而非修缺陷，转到 pace-change add 的路径不够显式
- 修复：pace-feedback intake 步骤增加"功能请求"类型判断，自动路由到 pace-change add
- 涉及文件：`skills/pace-feedback/feedback-procedures-intake.md`

### 2.4 信号系统缺口

当前 S1-S20 信号覆盖全面，但缺少以下场景：

| 编号 | 缺失信号 | 场景 | 建议优先级 |
|------|---------|------|-----------|
| S21 | 跨 CR 依赖阻塞 | CR-A 被 CR-B 阻塞且 CR-B 长期未推进 | P1 |
| S22 | 技术债积压 | tech-debt CR 数量或占比超阈值 | P2 |
| S23 | 知识库健康度 | insights.md 引用命中率 < 50% | P2 |
| S24 | 首次完整循环 | 用户从未完成过 init->dev->review->merged 完整循环 | P0 |
| S25 | 长期休眠项目 | .devpace/ 存在但 30+ 天无活动 | P2 |

---

## Part III: 微观审查 — 用户操作流畅性

### 3.1 新用户首次体验（First-Time UX）

**当前流程**：
```
用户安装 Plugin -> /pace-init -> 生成 .devpace/ ->
"说'帮我做 [功能名]'开始第一个功能..." -> ???
```

**问题**：
1. 初始化后的"空白页"——用户不确定下一步做什么
2. 从 README 的 19 个命令列表到"只需说自然语言"的认知跳跃过大
3. 没有引导式的 onboarding tour
4. 第一次使用 pace-dev 时用户不理解为什么会创建 BR/PF/CR 三层结构

**改进方案**（P0 优先级）：
- 新增 `S24 首次完整循环` 信号，在 session-start 检测到用户从未完成过完整循环时，触发引导式 onboarding
- Onboarding 不是新 Skill，而是 pace-pulse session-start 的增强：检测到"新项目 + 0 个 merged CR"时，输出简化版的下一步引导
- README 精简：首页只保留核心 5 命令 + 30 秒体验，完整列表链接到 user-guide

### 3.2 日常开发流程（Daily UX）

**当前流程**：
```
会话开始 -> 1 句话状态 -> "帮我做 X" -> pace-dev 推进 ->
Gate 1/2 -> pace-review -> Gate 3 人类审批 -> merged ->
下一步引导
```

**问题**：
1. Gate 3 高频审批摩擦——连续做 5-6 个 S 复杂度 PF 时，每个都要审批
2. 批量审批虽有设计（§2），但触发条件苛刻（2+ CR 同时 in_review）
3. 推进模式中"探索中继续"的模式切换对用户不透明

**改进方案**（P1 优先级）：
- "连续推进模式"：用户说"连续做"或"批量推进"时，pace-dev 在 S 复杂度 CR 满足简化审批条件时不立即审批，而是推进到下一个 PF，最后统一展示批量审批列表
- 涉及文件：`skills/pace-dev/SKILL.md`（新增 `--batch` 参数）、`rules/devpace-rules.md §2`（放宽批量审批触发条件）

### 3.3 认知负荷分析

| 维度 | 当前状态 | 问题 | 改进 |
|------|---------|------|------|
| 命令数量 | 19 Skill + ~83 子命令 | 信息过载 | 分层暴露：核心 5 -> 进阶 -> 专项 |
| 价值链层级 | OPP->Epic->BR->PF->CR->Release | 对小项目过重 | "轻量模式"：小项目隐藏 OPP/Epic 层 |
| 模式切换 | 探索/推进隐式切换 | 用户不知当前模式 | status 行显示当前模式标识 |
| 术语体系 | BR/PF/CR/Gate/MoS 等 | 对非产品经理背景的开发者陌生 | 自然语言优先，术语仅在 tree/detail 视图暴露 |

### 3.4 错误恢复与容错

**当前容错设计**：
- Gate 失败自修复（最多 2 次）
- 文件损坏降级处理（pace-change degraded mode）
- 中断恢复（state.md 锚点）
- 验收失败回退到 developing

**缺口**：
- 用户误操作的"撤销"能力有限——pace-change undo 只针对需求变更，pace-dev 没有"撤销上一次合并"的能力
- 会话中途 Claude 出错（幻觉）时的恢复机制依赖用户主动发现

---

## Part IV: 竞争力差异化分析

### 4.1 devpace 独特定位

| 维度 | 传统工具 (Jira/Linear/GitHub Projects) | 通用 AI 编码 (Cursor/Copilot Workspace) | devpace |
|------|--------------------------------------|---------------------------------------|---------|
| 业务到代码追溯 | 手动关联 | 无 | **自动**（OBJ->BR->PF->CR） |
| 变更管理 | 手动调整看板 | 无 | **一等公民**，影响分析+有序调整 |
| 质量门 | CI/CD 外挂 | 无 | **内嵌**，4 级 Gate 自动执行 |
| 跨会话连续性 | N/A | 有限 | **完整**（state.md 锚点） |
| 度量与回顾 | 需额外配置 | 无 | **内建** DORA + 迭代回顾 |
| 自然语言交互 | 有限（AI 辅助搜索） | 代码层面 | **全流程**自然语言驱动 |
| AI 决策透明度 | N/A | 无 | **完整审计**（pace-trace） |

### 4.2 护城河强化方向

**当前三层护城河**：入口层（跨会话） -> 差异化层（变更管理） -> 护城河层（完整价值链+度量+合规）

**强化建议**：

| 方向 | 措施 | 目的 |
|------|------|------|
| **智能编排** | 引入"旅程模板"，自动编排多 Skill 流程 | 从"工具集"升级为"智能工作流平台" |
| **预测能力** | 强化 pace-retro forecast + pace-guard trends | 从"被动管理"升级为"主动预测" |
| **生态集成** | 完成 Phase 19-20 外部同步 + CI/CD 深度集成 | 从"独立工具"升级为"研发中枢" |
| **团队适配** | 多用户状态隔离 + 角色权限 + 共享仪表盘 | 从"个人工具"升级为"团队平台" |
| **可视化** | Phase 24 devpace-cadence Next.js 仪表盘 | 从"CLI 工具"升级为"可视化平台" |

### 4.3 与"世界最优秀"的差距

对标 BizDevOps 领域最佳实践，devpace 的主要差距：

1. **编排智能不足**：19 个 Skill 是独立的，缺少跨 Skill 的智能编排能力。用户需要自己知道"下一步该用哪个命令"，虽然 pace-next 提供建议，但缺少"一键执行推荐"
2. **小项目体验过重**：概念模型（6 层价值链）对个人小项目来说认知成本过高
3. **大项目性能未验证**：50+ CR 场景下的 backlog 遍历、信号采集性能未经实战验证
4. **多人协作空白**：完全面向"1 人 + Claude"，无法支持 2+ 人共享 .devpace/
5. **可视化缺失**：纯 CLI 交互，无法提供全局鸟瞰视图

---

## Part V: 分层重构方案

### P0: 即刻改进（1-2 周，不改架构）

| 编号 | 改进项 | 涉及文件 | 预期效果 |
|------|--------|---------|---------|
| P0-1 | **新用户 Onboarding 引导** | `skills/pace-pulse/pulse-procedures-session-start.md` | 新项目首次会话自动引导用户完成"init -> 第一个功能 -> review -> merged"完整闭环 |
| P0-2 | **修复 D1: biz decompose 输出引导** | `skills/pace-biz/biz-procedures-decompose.md` | 统一 decompose 输出引导到 `/pace-plan next`，消除路径歧义 |
| P0-3 | **修复 D2: merged 后迭代优先级推荐** | `skills/pace-dev/dev-procedures-postmerge.md` | merged 后如果迭代内有未开始 PF，直接推荐最高优先级 PF |
| P0-4 | **README 精简** | `README.md`、`README_zh.md` | 首页只保留核心 5 命令 + 30 秒体验，降低新用户信息过载 |
| P0-5 | **修复 D4: 新项目风险扫描兜底** | `skills/pace-guard/guard-procedures-common.md` | 新项目（insights.md 为空）的首 3 个 CR 默认触发基础风险扫描 |
| P0-6 | **修复 D5: feedback 功能请求路由** | `skills/pace-feedback/feedback-procedures-intake.md` | 增加"功能请求"类型判断，自动路由到 pace-change add |

### P1: 体验升级（3-4 周，小幅架构调整）

| 编号 | 改进项 | 涉及文件 | 预期效果 |
|------|--------|---------|---------|
| P1-1 | **连续推进模式（batch dev）** | `skills/pace-dev/SKILL.md`、`dev-procedures-common.md`、`rules/devpace-rules.md §2` | 用户说"连续做"时批量推进 S 复杂度 PF，最后统一审批 |
| P1-2 | **修复 D3: retro -> plan 衔接** | `skills/pace-plan/plan-procedures.md` | 规划新迭代时自动引用上一迭代回顾的关键建议 |
| P1-3 | **轻量模式（lite mode）** | `skills/pace-init/SKILL.md`、`init-procedures-core.md`、`knowledge/_schema/entity/project-format.md` | 小项目初始化时隐藏 OPP/Epic 层，project.md 只含 OBJ->PF->CR 三层 |
| P1-4 | **信号系统补全** | `knowledge/_signals/signal-priority.md`、`knowledge/_signals/signal-collection.md` | 新增 S21(依赖阻塞)、S22(技术债积压)、S24(首次循环引导) |
| P1-5 | **模式状态可见** | `rules/devpace-rules.md §1/§2` | session-start 和推进模式切换时，在输出中明确标识当前模式 |
| P1-6 | **pace-biz 子命令分组优化** | `skills/pace-biz/SKILL.md` | 将 8 个子命令分为"创建型"(opportunity/epic/decompose)和"分析型"(align/view/discover/import/infer) |

### P2: 结构增强（1-2 月，中度架构调整）

| 编号 | 改进项 | 涉及范围 | 预期效果 |
|------|--------|---------|---------|
| P2-1 | **智能旅程编排器（Journey Orchestrator）** | 新增 `skills/pace-journey/` 或整合到 `pace-next` | 提供"旅程模板"：`/pace-next journey new-feature` 自动编排 biz->plan->dev->review->release 完整流程，每步完成后自动推进到下一步 |
| P2-2 | **事件管理增强** | 扩展 `skills/pace-feedback/` | 增加 `incident` 子命令系列：severity 分级、escalation、postmortem 模板 |
| P2-3 | **架构设计步骤** | 扩展 `skills/pace-dev/` 或新增 `skills/pace-design/` | L/XL CR 开发前增加"技术方案"步骤，含方案选择、ADR 记录、依赖分析 |
| P2-4 | **信号快照缓存** | `knowledge/_signals/signal-collection.md`、相关 Skill procedures | 实现信号采集结果的会话级缓存，避免同一会话重复扫描 |
| P2-5 | **大型项目性能优化** | `knowledge/_schema/process/state-format.md`、各 Skill 的 backlog 扫描逻辑 | backlog 索引机制：state.md 维护 CR 摘要索引，避免逐文件遍历 |

### P3: 长期演进（3+ 月，重大架构变革）

| 编号 | 改进项 | 涉及范围 | 预期效果 |
|------|--------|---------|---------|
| P3-1 | **多用户协作支持** | state.md 分离为 per-user + shared、合并策略 | 支持 2+ 人共享 .devpace/，通过 Git 自然协作 |
| P3-2 | **可视化仪表盘** | Phase 24 devpace-cadence Next.js | 从 CLI 到 Web UI，提供全局鸟瞰 |
| P3-3 | **CI/CD 深度集成** | MCP Server 或 pace-sync 扩展 | 触发构建、查看日志、管理部署环境 |
| P3-4 | **智能自主性升级** | 新的 autonomy-level 框架 | Claude 根据项目成熟度和用户信任度自动调整自主级别 |
| P3-5 | **插件生态** | Plugin 扩展机制 | 允许第三方为 devpace 编写领域扩展（安全审计、合规检查等） |

---

## Part VI: 核心架构重构 — 智能旅程编排器（P2-1 详设）

这是本次重构的**核心架构级提案**，将 devpace 从"工具集"升级为"智能工作流平台"。

### 6.1 问题本质

19 个 Skill 各自优秀，但用户需要**自己知道**下一步该用哪个。虽然 pace-next 提供建议，但：
- pace-next 只推荐"1 件事"，不提供完整的工作流视图
- 用户需要手动执行推荐的命令
- 没有"一键走完整个流程"的能力

### 6.2 方案设计

**不新增 Skill**，而是增强 `/pace-next` 增加 `journey` 子命令：

```
/pace-next journey <模板名> [--auto]
```

**内置旅程模板**：

| 模板 | 编排流程 | 适用场景 |
|------|---------|---------|
| `new-feature` | biz discover -> decompose -> plan next -> dev -> review -> merged | 从零开始交付一个功能 |
| `iteration` | plan next -> [dev -> review -> merged]* -> plan close -> retro | 完整迭代循环 |
| `hotfix` | feedback report -> dev(hotfix) -> review -> release deploy | 紧急修复 |
| `release` | release create -> deploy -> verify -> close | 标准发布 |
| `onboarding` | init -> dev(第一个功能) -> review -> merged | 新用户首次体验 |

**`--auto` 模式**：每步完成后自动推进到下一步（S 复杂度），L/XL 在每步前暂停确认。

### 6.3 为什么是 pace-next 而非新 Skill

1. pace-next 已有全局信号采集能力，是最佳的编排锚点
2. 不增加 Skill 数量，降低用户认知负荷
3. `journey` 是 pace-next 的自然扩展——从"推荐下一步"到"编排完整旅程"
4. 复用 signal-priority.md 的优先级逻辑

---

## Part VII: 验证方案

### 7.1 P0 验证

1. 新建测试项目，使用 `/pace-init` 初始化
2. 验证 session-start 是否触发 onboarding 引导
3. 使用 `/pace-biz decompose` 验证输出引导是否指向 `/pace-plan next`
4. 完成一个 CR merged，验证 postmerge 引导是否推荐迭代内下一 PF
5. 在新项目上创建 S 复杂度 CR，验证是否触发基础风险扫描

### 7.2 P1 验证

1. 连续推进 3 个 S 复杂度 PF，验证批量审批流程
2. 使用 lite mode 初始化小项目，验证 project.md 只含 OBJ->PF->CR
3. 创建互相依赖的 2 个 CR，验证 S21 信号是否触发

### 7.3 P2 验证

1. `/pace-next journey new-feature` 端到端测试：从 biz discover 到 merged
2. `/pace-next journey onboarding` 新用户体验测试
3. 50+ CR 项目的信号采集性能基准测试

### 7.4 自动化验证

扩展 `tests/static/` 测试套件：
- `test_journey_templates.py`：验证旅程模板定义完整性
- `test_signal_coverage.py`：验证新增信号的采集和消费正确性
- `test_skill_interconnections.py`：验证 D1-D5 断层修复后的引导路径一致性
