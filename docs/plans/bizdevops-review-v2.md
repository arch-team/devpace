# devpace BizDevOps 全生命周期审查与改进方案（v2 — 基于最新项目状态）

## Context

devpace 是一个 Claude Code Plugin，经过 21 个 Phase 迭代（18 完成，Phase 21 进行中，Phase 19/20 待开始），构建了 19 个 Skills、3 个 Agents、18+ 个 Schemas、14 个 Hooks。Phase 21 正在补齐 Biz 域的上游建模（Opportunity→Epic→BR），新增了 pace-biz Skill（8 个子命令 + 8 个 procedures）和 3 个 Schema（opportunity-format、epic-format、br-format）。同时，独立的可视化平台 `devpace-cadence`（Next.js Web 应用）已完成设计方案。

用户要求从 BizDevOps 专家视角进行系统审查，并参照华为 CodeArts ALM 等企业级 ALM 工具的价值流设计，识别覆盖缺口和体验短板，提出改进方案。

---

## 第一部分：最新 BizDevOps 覆盖矩阵

### 1.1 实体关系现状（价值链六层）

```
Opportunity(OPP) ──采纳──→ Epic(EPIC) ──分解──→ BR ──细化──→ PF ──实现──→ CR ──发布──→ Release
  [Schema ✅]          [Schema ✅]         [Schema ✅]    [Schema ✅]   [Schema ✅]   [Schema ✅]
  [Skill ✅]          [Skill ✅]         [Skill ✅]    [Skill ✅]   [Skill ✅]    [Skill ✅]
   pace-biz             pace-biz            pace-biz      pace-dev     pace-dev     pace-release
   opportunity          epic                decompose     (自动创建PF) (状态机)     (14子命令)

横向支撑：OBJ(业务目标) ✅ | MoS(成效指标) ✅ | 迭代 ✅ | 风险 ✅ | 度量 ✅ | 经验 ✅
```

### 1.2 三域评分（基于最新实现）

| 域 | 评分 | 说明 |
|----|:----:|------|
| **Biz 域** | **6/10** | Schema 完整且设计优秀（OPP/EPIC/BR），pace-biz Skill 已定义 8 子命令 + 8 procedures，但 S35-S42 验收标准全部未打勾（验证待完成）。与上次审查（3/10）大幅提升 |
| **Dev 域** | **9/10** | 完整：pace-init/dev/test/guard/review 全部实现并验证 |
| **Ops 域** | **7.5/10** | pace-release 完整，pace-sync GitHub MVP 已完成（Phase 19/20 待扩展） |
| **Observe 域** | **9/10** | pace-status/next/pulse/retro/trace 全部完整 |
| **Knowledge 域** | **8.5/10** | pace-learn/theory 完整，devpace-cadence 可视化平台已设计 |

### 1.3 对标 CodeArts ALM 实体覆盖（用户 promt.md 分析的更新）

| CodeArts 概念 | devpace 覆盖 | 最新状态 | 差距评估 |
|--------------|:------------:|---------|---------|
| 业务机会 | **已建模** | OPP Schema + pace-biz opportunity | 待验证 |
| 专题（Epic） | **已建模** | EPIC Schema + pace-biz epic（含 MoS） | 待验证 |
| 业务需求（BR） | **已建模** | BR Schema + 溢出模式 + 优先级 + 成功标准 | 待验证（不再是"空壳"） |
| 产品特性（PF） | 较好 | 完整字段体系 + 溢出模式 | 已验证 |
| 业务目标 | 较好 | OBJ + MoS checkbox | 已验证 |
| 愿景 | **已增强** | project-format.md 结构化（目标用户+核心问题+差异化+成功图景） | 不再是一行 blockquote |
| 战略上下文 | **已新增** | project-format.md 战略上下文 section（核心假设+外部约束） | 渐进填充 |
| 成功标准 | **已扩展** | MoS 覆盖 OBJ + **新增 Epic 级 MoS** + BR 级成功标准 | 三层 MoS |
| 需求工作流 | **已改善** | BR→PF 有 pace-biz decompose；PF→CR 有状态机 | 但 BR 自身无独立状态机（状态由下游 PF 聚合计算） |
| 版本规划 | 较好 | Release 完整 | 已验证 |
| 日常需求 | **有路径** | `/pace-change add`（快速路径，跳过 OPP/EPIC） | 已设计但需验证 |
| 业务线/产品线 | 无 | 刻意不建模（单项目 Claude Code 场景不需要） | **合理省略** |
| 投资组合 | 无 | 不建模 | **合理省略**（单人场景） |
| 产品目标 | 间接 | 通过 OBJ→Epic→BR→PF 间接关联 | 可接受 |
| 战略/策略 | 间接 | 被 OBJ + 战略上下文隐含 | 可接受 |

---

## 第二部分：系统性缺口分析（按严重程度排序）

### G1 [严重: 高] pace-biz 实现验证缺口

**现状**：pace-biz 的 8 个子命令 + 8 个 procedures + 3 个 Schema 已全部定义，但 S35-S42 的验收标准（requirements.md）全部未打勾。这意味着 Biz 域的实际运行时行为尚未被端到端验证。

**风险**：
- Schema 定义优秀但实际执行时可能有边界条件问题
- pace-biz 与下游 Skill（pace-change、pace-plan、pace-dev）的衔接未验证
- 价值功能树中 Epic→BR→PF 的渐进溢出模式未验证

**建议**：这是当前最高优先级——完成 Phase 21 M21.4（文档+eval）和 M21.5（discover/import/infer 验证），然后逐条打勾 S35-S42。

### G2 [严重: 高] Skill 间紧耦合风险

**新发现**：`docs/design/skill-dependencies.md` 揭示了多处高风险耦合：

| 耦合关系 | 风险等级 | 问题 |
|---------|:--------:|------|
| pace-review → pace-test accept | **很高** | review 摘要模板内嵌 accept 输出字段，格式变更直接破坏 |
| pace-dev → pace-guard scan | **高** | dev 直接引用 guard 的 procedures 文件路径 |
| pace-dev → pace-test strategy-gen | **高** | dev 直接引用 test 的 procedures 文件路径 |
| pace-change → pace-plan adjust | **高** | change 内联执行 plan 的逻辑 |

**影响**：任何单个 Skill 的重构都可能级联破坏其他 Skill。这在 19 个 Skill 规模下是严重的维护性风险。

**建议**：
- **短期**：将高风险耦合点的格式定义抽取为共享 Schema（类似 cr-format.md 的契约模式）
- **中期**：考虑引入"接口契约"层——Skill 间通过 Schema 定义的数据格式通信，而非直接引用 procedures 文件路径
- **立即**：在 skill-dependencies.md 中标注的 "§5 变更影响矩阵" 作为每次修改前的必查清单

### G3 [严重: 中] 架构决策记录（ADR）缺失

**现状**：context.md 记录技术约定（"怎么写代码"），CR 事件表记录单 CR 决策。但跨 CR 的架构级决策（"为什么选 PostgreSQL"、"为什么微服务架构"）没有独立管理。

**影响**：跨会话时 Claude 可能做出矛盾的架构选择。技术债务根源不可追溯。

**建议**：扩展 pace-trace 增加 `arch` 子命令 + 新增 `decisions/ADR-NNN.md` Schema。不需要新 Skill，在 pace-trace 内扩展即可（符合"深度优于广度"原则）。

### G4 [严重: 中] 技术债务非一等公民

**现状**：pace-biz infer 可推断技术债务，pace-guard 可扫描风险，但技术债务没有独立状态机和偿还计划。

**建议**：
- CR type 增加 `tech-debt`（cr-format.md 已有 type 枚举，扩展即可）
- pace-plan 增加迭代容量预留配置（project.md 配置 section 添加 `tech-debt-budget: 20%`）
- pace-retro 增加技术债务趋势指标

### G5 [严重: 中] 安全维度（DevSecOps）薄弱

**现状**：checks-format.md 有"安全检查推荐表"，但安全不是系统化管理维度。

**建议**：pace-guard scan 增加"安全"维度（第 6 维）。不需要新 Skill。

### G6 [严重: 低] BR 缺少独立状态机

**现状**：BR 状态由下游 PF 聚合计算（"所有 PF 完成→BR 完成"），但没有独立的状态转换（如"BR 评审中→BR 已确认→BR 开发中"）。这意味着 BR→PF 的转化过程无显式工作流。

**对标**：CodeArts ALM 的需求工作流有独立的 "需求→评审→开发→验证→关闭" 工作流。

**评估**：在 Claude Code 单人场景下，BR 的独立工作流可能过重。当前的聚合计算模式是合理的极简设计。但如果 devpace 要面向团队场景（devpace-cadence 可视化平台暗示这一方向），BR 独立工作流将变得必要。

**建议**：P3 优先级。当前设计已够用，未来面向团队场景时再评估。

---

## 第三部分：用户体验流畅性分析

### UX1 [影响: 高] 命令认知过载

**数据**：19 Skills × 平均 6 子命令 ≈ 60+ 入口。pace-release 14 子命令、pace-test 10 子命令、pace-change 9 子命令。

**已有缓解**：pace-next 推荐下一步、rules §15 渐进教学、空参数智能引导、渐进暴露设计。

**改进方向**：
- 强化"无命令体验"——扩展自然语言触发覆盖面
- pace-biz 空参引导已设计良好（扫描项目上下文→个性化推荐），建议作为模式推广到其他 Skill
- 评估是否需要 "pace-help" 或在 pace-status 中集成命令推荐

### UX2 [影响: 高] 探索→推进模式切换摩擦

**问题**：`context: fork` 创建新 Agent 上下文，探索阶段发现需要重建。

**已有缓解**：T118 上下文继承、Agent memory 持久化。

**改进方向**：
- S/M 复杂度 CR 提供"快速模式"（不 fork）
- 探索模式关键发现写入 CR "探索笔记" section
- fork 时自动注入探索摘要

### UX3 [影响: 中] 新用户上手断点

**问题**：pace-init 完成后"然后呢？"不明确。

**改进方向**：
- pace-init 完成后自动触发 pace-biz infer（已有代码的项目）
- state.md 初始生成时包含推荐下一步
- 第一次 /pace-dev 增加新手引导

### UX4 [影响: 中] 长会话上下文压力

**问题**：550 行 rules + 126 个 procedures 在 compact 后可能退化。

**改进方向**：
- PreCompact Hook 增强：保存关键状态快照
- compact 后注入最小恢复上下文（IR-1~5 + 当前 CR + 下一步）

### UX5 [影响: 中→低] 度量可视化受限

**问题**：dashboard.md 纯文本表格表现力有限。

**已有方案**：devpace-cadence Web 应用（ReactFlow 价值链图 + Recharts 仪表盘）将系统性解决此问题。

**短期改进**：pace-retro 输出增加 Mermaid 趋势图。

---

## 第四部分：差异化创新建议

### D1 [杀手级] AI 驱动的预测性项目管理

**概念**：基于历史 CR 周期、Gate 通过率、变更频率、风险趋势、insights.md 经验，AI 预测迭代交付概率和瓶颈。

**为何杀手级**：传统工具用统计学（燃尽图），devpace 可做"因果推断"——Claude 理解代码复杂度和需求耦合度。

**实施**：扩展 pace-retro 增加 `forecast` 子命令（不新增 Skill），输出：
- 迭代交付概率（基于当前进度 + 历史模式）
- 预测瓶颈（基于 CR 滞留时间 + 依赖关系）
- 风险预警（基于 pace-guard 趋势 + insights 模式）

### D2 [杀手级] 语义级代码-需求持续一致性检测

**概念**：不只 Gate 2 的一次性比对，而是持续监控代码变更是否偏离需求语义。

**实施**：增强 pace-dev 漂移检测 + pace-review 增加"语义一致性评分"。不需要新 Skill。

### D3 [强差异化] devpace-cadence 可视化平台

**已规划**：独立 Next.js 应用，从 Git 仓库拉取 `.devpace/` 数据，提供价值链追溯图 + 看板 + 仪表盘。

**战略价值**：
- 让非开发角色（PM/QA/管理层）无需 Claude Code 即可查看研发状态
- 多项目支持为 pace-portfolio 奠定基础
- 角色视图复用 pace-role 的 5 角色维度

### D4 [强差异化] 多项目组合管理

**概念**：跨项目的全局 insights 库、依赖声明、统一 DORA 仪表盘。

**基础**：devpace-cadence 的多项目支持 + pace-learn export/import。

**实施**：待 devpace-cadence 成熟后，在 Plugin 侧新增 pace-portfolio Skill 或扩展 pace-sync。

### D5 [中等差异化] 自然语言工作流编排

**概念**：用户自然语言定义自动化工作流，devpace 自动编排执行。

**实施**：长期目标，扩展 project.md 配置 section 增加自动化流程定义。

---

## 第五部分：优先级路线图

### 立即（Phase 21 剩余）

| 项目 | 内容 | 对应缺口 |
|------|------|---------|
| M21.4 完成 | 文档 + eval 验证 | G1 |
| M21.5 完成 | discover/import/infer 端到端验证 | G1 |
| S35-S42 打勾 | pace-biz 全部验收标准验证 | G1 |

### Phase 22: 体验增强 + 紧耦合治理

| 里程碑 | 内容 | 优先级 | 对应缺口 |
|--------|------|:------:|---------|
| M22.1 | Skill 间接口契约层设计（解耦 pace-review↔pace-test、pace-dev↔pace-guard 等） | P0 | G2 |
| M22.2 | 首次推进引导 + 无命令体验增强 | P1 | UX1, UX3 |
| M22.3 | ADR 管理（pace-trace arch 子命令 + decisions/ Schema） | P1 | G3 |
| M22.4 | 技术债务一等公民化（CR type 扩展 + pace-plan 容量预留） | P1 | G4 |

### Phase 23: 预测与安全

| 里程碑 | 内容 | 优先级 | 对应缺口 |
|--------|------|:------:|---------|
| M23.1 | pace-retro forecast 子命令（预测性项目管理） | P1 | D1 |
| M23.2 | 安全维度增强（pace-guard 第 6 维） | P1 | G5 |
| M23.3 | Compact 恢复优化 | P1 | UX4 |
| M23.4 | 语义级漂移检测增强 | P1 | D2 |

### Phase 24+: 可视化与企业级

| 里程碑 | 内容 | 优先级 | 对应缺口 |
|--------|------|:------:|---------|
| devpace-cadence MVP | 独立仓库实现 | P1 | D3, UX5 |
| 多项目组合管理 | pace-portfolio 或 pace-sync 扩展 | P2 | D4 |
| BR 独立工作流 | 面向团队场景评估 | P3 | G6 |

---

## 第六部分：三条核心战略建议

### 1. 深度优于广度

19 Skills 已到认知极限。本方案中**没有新增任何 Skill**——所有改进都通过扩展现有 Skill 子命令实现（ADR→pace-trace arch；forecast→pace-retro forecast；安全→pace-guard 第 6 维）。这是刻意的设计选择。

### 2. 契约优于内联

skill-dependencies.md 揭示的紧耦合是最大的维护性风险。Skill 间应通过 Schema 定义的数据契约通信，而非直接引用内部 procedures 文件路径。这是 Phase 22 的最高优先级。

### 3. 验证优于新增

Phase 21 的 pace-biz + 3 个 Schema 设计质量很高，但验收标准全部未打勾。当前最有价值的工作不是新增功能，而是**完成验证并在真实项目中跑通 OPP→EPIC→BR→PF→CR 全链路**。

---

## 第七部分：风险

| 风险 | 严重度 | 缓解 |
|------|:------:|------|
| Skill 间紧耦合导致级联故障 | 高 | Phase 22 接口契约层（G2） |
| 规则过载 compact 后退化 | 高 | Phase 23 规则分层加载 |
| pace-biz 设计未经真实项目验证 | 高 | 立即完成 S35-S42 验证 |
| 复杂度膨胀（60+ 子命令） | 中 | 不新增 Skill，强化无命令体验 |
| Claude Code 原生 session persistence | 中 | 加速向预测+智能层迁移 |

## 验证方法

1. **Biz 域验证**：在 1 个真实项目中跑通 `pace-biz opportunity → epic → decompose → /pace-dev → /pace-review → /pace-release` 全链路
2. **紧耦合验证**：修改 pace-test accept 输出格式，验证 pace-review 是否破坏
3. **回归验证**：`bash scripts/validate-all.sh` + `pytest tests/static/ -v`
4. **竞争力对比**：与 Linear AI、CodeArts ALM 做特性矩阵对比

## 关键文件

- `docs/design/skill-dependencies.md` — **新增**：Skill 间耦合关系（变更影响矩阵必查）
- `docs/plans/devpace-cadence-design.md` — **新增**：可视化平台设计方案
- `skills/pace-biz/SKILL.md` — **新增**：Biz 域统一入口
- `knowledge/_schema/opportunity-format.md` — **新增**：OPP Schema
- `knowledge/_schema/epic-format.md` — **新增**：EPIC Schema
- `knowledge/_schema/br-format.md` — **新增**：BR Schema
- `knowledge/_schema/project-format.md` — **更新**：价值功能树增加 Epic→BR 链接格式
- `docs/planning/requirements.md` — S35-S42 验收标准（待打勾）
- `rules/devpace-rules.md` — 运行时行为规则
