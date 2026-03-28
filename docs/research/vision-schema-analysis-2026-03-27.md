# vision-format.md 质量保障与落地执行分析报告

> **日期**：2026-03-27
> **类型**：Schema 质量分析 + 业务需求专家审视
> **分析对象**：`knowledge/_schema/entity/vision-format.md` 及其在价值链中的消费/验证全景

## Context

分析 devpace 如何保证 `vision-format.md` 内容的准确性/有效性，以及在真实项目开发中如何保证 `vision.md` 有效落实执行。经过对全代码库的深度扫描，发现 **vision.md 是 devpace 价值链中保障最薄弱的环节**——Schema 契约定义完整，但实现层面存在多处断裂。

---

## 一、现状：vision.md 的完整生命周期

### 1.1 创建路径

| 路径 | 入口 | 实现状态 |
|------|------|---------|
| `/pace-init` 默认 | init-procedures-core.md | **未实现**——core 中无任何 vision 引用，不创建桩文件 |
| `/pace-init full` | init-procedures-full.md:96 | **已实现**——阶段 2a 引导填充核心四要素 |
| `/pace-biz` 首次 | vision-format.md:10 声明 | **未实现**——pace-biz 全部 10 个 procedures 中无 vision.md 写入逻辑 |

### 1.2 下游消费

| 消费方 | 引用方式 | 实现状态 |
|--------|---------|---------|
| project.md §1.6/§1.7 | 链接引用 `[查看完整愿景](vision.md)` | Schema 定义完整（project-format.md:175-200） |
| pace-biz align | 应检查 Vision→OBJ 对齐 | **未实现**——align 仅检查 OBJ→Epic→BR→PF→CR，不回溯 Vision |
| pace-retro | 应建议更新北极星当前值 + 假设状态 | **未实现**——pace-retro 12 个文件中零 vision 引用 |
| 信号系统 | 应有 vision 缺失/过期信号 | **未实现**——_signals/ 中无 vision 信号 |
| rules | 应有 vision 行为规则 | **未实现**——devpace-rules.md 中无 vision 规则 |

### 1.3 验证机制

| 验证层 | 覆盖状态 |
|--------|---------|
| 静态测试 (tests/static/) | 仅通用覆盖（§0 速查卡片、链接完整性），**无 vision 专用测试** |
| validate-all.sh | **无 vision 特定检查** |
| Hook 守护 | scope check 允许写入 .devpace/，但**无格式验证 Hook** |
| 健康检查 --verify | **vision.md 未纳入校验清单**（init-procedures-verify.md:25-38） |
| eval 评估 | pace-init 12 场景 + pace-biz 16 场景中**零 vision 用例** |
| 迁移框架 | migration.md 三条迁移链**均不涉及 vision** |
| 示例 | examples/ 中**无 vision.md 示例** |

---

## 二、核心问题：Schema 契约与实现的六处断裂

### 断裂 1：pace-init 默认不创建桩

vision-format.md:10-11 声明 `/pace-init` 创建桩，但 init-procedures-core.md 中无任何 vision 引用。只有 `/pace-init full` 才触发。

**影响**：多数用户使用默认初始化后，.devpace/ 中不存在 vision.md，价值链顶端即缺失。

### 断裂 2：pace-biz 不填充 vision.md

vision-format.md:10 声明"首次 /pace-biz 时填充核心四要素"，但 pace-biz 全部 10 个 procedures 文件中**零 vision.md 写入逻辑**。

**影响**：用户按推荐流程（init -> pace-biz）使用，vision.md 始终为空桩或不存在。

### 断裂 3：pace-retro 不更新北极星

vision-format.md:58 声明"北极星当前值 /pace-retro 时填充"，vision-format.md:133 声明"/pace-retro 建议更新北极星当前值、假设状态"。但 pace-retro 全部 12 个文件中零 vision 引用。

**影响**：北极星指标永远停留在初始值，无法形成"目标->度量->回顾->调整"闭环。

### 断裂 4：align 不回溯 Vision

pace-biz align（biz-procedures-align.md）检查 OBJ→Epic→BR→PF→CR 链的 9 项指标，但不检查 OBJ 的"北极星贡献"字段是否与 Vision 北极星指标对齐。

**影响**：OBJ 可能与 Vision 脱节而不被发现。

### 断裂 5：信号系统盲区

knowledge/_signals/ 中无 vision 相关信号。pace-next / pace-pulse 不会推荐"vision 信息缺失"或"北极星未更新"。

**影响**：用户得不到主动提醒去完善 vision.md。

### 断裂 6：验证全面缺失

健康检查、静态测试、eval、迁移框架均未覆盖 vision.md。

**影响**：即使 vision.md 格式错误、内容缺失或被意外删除，也不会被任何自动化机制发现。

---

## 三、根因分析

1. **Fan-in = 1**：vision-format.md 是所有 entity Schema 中消费者最少的，导致在开发优先级排序中被忽视
2. **渐进丰富设计的副作用**：vision.md 被设计为"可以为空"，这降低了实现的紧迫性，但也导致了"永远为空"
3. **顶层抽象难以自动化**：vision 是人类战略意图，不像 CR 状态那样可以通过 Hook/Gate 自动守护
4. **Schema 先行开发模式**：vision-format.md 作为契约被完整定义，但消费方的 procedures 尚未跟进实现

---

## 四、实现层改进建议（按优先级）

### P0：补齐 Schema->实现断裂（3 项）

| # | 断裂 | 修复方案 | 涉及文件 |
|---|------|---------|---------|
| 1 | pace-init 默认不创建桩 | init-procedures-core.md 增加 vision.md 桩创建步骤 | `skills/pace-init/init-procedures-core.md` |
| 2 | pace-biz 不填充 vision | 新增 biz-procedures-vision.md 或在 discover 流程中集成迁移+填充逻辑 | `skills/pace-biz/` |
| 3 | pace-retro 不更新北极星 | 在 retro dimensions procedures 中增加 vision.md 北极星当前值建议更新步骤 | `skills/pace-retro/retro-procedures-dimensions.md` |

### P1：补齐闭环机制（2 项）

| # | 缺口 | 修复方案 | 涉及文件 |
|---|------|---------|---------|
| 4 | align 不回溯 Vision | biz-procedures-align.md 增加第 10 项检查：Vision->OBJ 北极星贡献对齐 | `skills/pace-biz/biz-procedures-align.md` |
| 5 | 信号系统盲区 | signal-priority.md 增加 S-Vision 类信号（vision 缺失/北极星未更新） | `knowledge/_signals/signal-priority.md` |

### P2：补齐验证覆盖（3 项）

| # | 缺口 | 修复方案 | 涉及文件 |
|---|------|---------|---------|
| 6 | 健康检查不含 vision | init-procedures-verify.md 校验清单增加 vision.md 行 | `skills/pace-init/init-procedures-verify.md` |
| 7 | 无专用测试 | test_schema_compliance.py 增加 vision schema 测试 | `tests/static/test_schema_compliance.py` |
| 8 | 无 eval 用例 | pace-init evals.json 增加 full 模式 vision 创建场景 | `tests/evaluation/pace-init/evals.json` |

---

## 五、业务需求分析专家视角：Schema 设计层面的结构性问题

### 5.1 Vision 在 BizDevOps 价值链中的真实定位

根据 theory.md §3.0c 和 §6 的定义，Vision 在 devpace 中承担三重角色：

| 角色 | 理论定义 | 当前 Schema 覆盖 |
|------|---------|-----------------|
| **战略锚点** | "所有 OBJ 和 Epic 应当回溯到愿景"（theory.md:92） | 仅声明，无 OBJ 反向索引字段 |
| **度量起点** | "MoS 最终体现在 Vision 的北极星指标上"（theory.md:286） | 有北极星指标字段，但无聚合机制 |
| **方向守护者** | "愿景的价值在于提供一个稳定的方向参照"（theory.md:95） | 有"Claude 不推断愿景"规则，但无对齐检查触发 |

**核心矛盾**：theory.md 将 Vision 定位为价值链的**最顶层战略起点**（design.md:145 的链路图第一个节点），但 vision-format.md 将其设计为**可选的渐进填充文件**（渐进阶段：桩->初始->成长->成熟）。这导致一个悖论——

> **价值链最重要的锚点，却是整个系统中约束最弱、消费最少、验证最缺的组件。**

### 5.2 五个结构性问题与优化方案

> 以下五个问题经过 Agent Team 四阶段工作流处理（设计→评审→执行→验证），最终决策和实施结果标注在每个问题的"优化方案"中。

#### 问题 E："渐进丰富"与"战略锚点"的设计张力 ✅ 已实施

渐进丰富是 devpace 的核心设计原则（P2），但应用到 Vision 时产生了一个独特的张力：

- **渐进丰富的假设**：信息在使用过程中逐步完善，系统在任何阶段都能工作
- **Vision 的特殊性**：Vision 是价值链的**起点**——如果起点为空，下游所有"回溯到愿景"的机制都失效

当前设计的"桩状态"（占位文字）在技术上不阻塞任何功能，但在**语义上**阻断了价值链：

```
Vision(空桩) -> OBJ(北极星贡献指向空值) -> Epic(主OBJ有意义，但上游锚点为空)
-> BR -> PF -> CR -> Release ... 整条链路的"为什么做"没有答案
```

**优化方案（已实施）**：在 vision-format.md 渐进阶段 section 新增"最小有效状态"子 section（vision-format.md:77-90），区分"文件可以渐进"和"核心字段必须有意义"：

- **三个必填字段**：一句话愿景摘要 + 目标用户 + 核心问题——构成最小价值主张
- **占位判定**：使用 exact match 列表（`[一句话愿景摘要]`、`[谁会用这个产品]`、`[他们的什么痛点]`），匹配任一即为无效
- **渐进兼容**：有效性是质量维度，不是门禁——无效 Vision 不阻断任何 Skill 执行
- **为何只要求三个字段**：差异化和成功图景对下游 OBJ 分解不构成硬依赖，允许渐进补充

**评审修订**：原方案包含 state.md 中增加 `<!-- vision-ready: true -->` 标记，评审后推迟——state.md 是会话启动必读文件（≤15 行硬限），无消费者时不应增加标记。待 align / 信号系统实现后再添加。

#### 问题 C：战略上下文过于简化 ✅ 已实施

当前战略上下文仅有"核心假设"和"外部约束"两个字段。作为**战略决策辅助信息**，这缺少了几个对 AI Agent 决策有重要影响的维度：

| 缺失维度 | 对 Claude 决策的影响 |
|---------|-------------------|
| **竞争格局** | 差异化字段告诉"凭什么"，但不告诉"对手是谁、他们在做什么" |
| **用户画像深度** | "目标用户"是一个标签，缺少行为特征、使用场景、决策链 |
| **技术约束** | context.md 记录技术栈，但 Vision 层面的技术选型约束（如"必须离线可用"）无处安放 |

**优化方案（已实施）**：将核心假设扩展为结构化格式（vision-format.md:43-45），保持向后兼容：

```markdown
**核心假设**：
- [假设内容]（[待验证 | 已验证 | 已推翻]）
  - 验证方式：[如何验证这个假设]（可选）
  - 验证结果：[验证后的发现]（可选，状态为已验证/已推翻时填充）
```

- **向后兼容**：简单格式（`- 假设内容（状态）`）仍合法——无验证子行的条目视为简单格式
- **格式选择规则**（vision-format.md:119）：Claude 新建假设时使用简单格式；用户主动提供验证方式时切换到结构化格式
- **为断裂修复铺路**：断裂 3（pace-retro 不更新假设状态）的修复前提是假设有可操作的结构化格式

**未纳入本次实施**：竞争格局和用户画像深度——不建议在 vision-format.md 中膨胀字段（违反 IA-11 单一职责），这些信息可作为 vision.md 的可选附录 section 在未来渐进出现。

#### 问题 D：Vision->OBJ 缺少反向索引 ❌ 评审否决

OBJ 有"北极星贡献"字段指向 Vision，但 Vision 没有"OBJ 索引"指向下游 OBJ 列表。这导致：

- 从 Vision 视角看不到"有哪些 OBJ 在贡献北极星"
- align 检查无法从 Vision 向下扫描覆盖率
- 度量链（theory.md:286 声称"MoS -> 北极星指标"）缺少物理聚合路径

**原始建议**：在 vision-format.md 的"北极星指标" section 增加 OBJ 贡献索引表。

**评审否决理由**：

1. **YAGNI——无消费者**：align 本身未实现 Vision 回溯（断裂 4），索引无人读取
2. **IA-6 同步风险**：OBJ 状态变更需同步三处（OBJ 文件 + project.md 索引 + vision.md 索引），同步链变长 = 失同步风险增加
3. **维护时机未定义**：方案未明确哪个 Skill 的 procedures 在什么时机维护索引（HE-3 违规）
4. **更优替代方案存在**：align 的 procedures 可在运行时动态扫描 objectives/ 目录获取 OBJ 覆盖率，无需在 vision.md 中维护静态索引——**动态查询优于静态索引**

**替代建议（待断裂 4 修复时实施）**：在 biz-procedures-align.md 中增加动态扫描逻辑——遍历 objectives/ 下所有 OBJ 文件的"北极星贡献"字段，生成临时视图供对齐检查使用。

#### 问题 A：核心四要素的抽象框架缺少"做什么" ⏸️ 推迟

当前核心愿景四要素：目标用户 + 核心问题 + 差异化 + 成功图景。

这本质上是 Value Proposition Canvas 的简化版（Who + Pain + Why Us + What Success Looks Like），但缺少了一个关键维度——**"解决方案方向"（What We Do）**。

| 要素 | 回答的问题 | 对下游的引导作用 |
|------|-----------|---------------|
| 目标用户 | 为谁？ | OBJ 的客户价值维度 |
| 核心问题 | 解决什么？ | BR 的需求来源 |
| 差异化 | 凭什么？ | 竞争策略选择 |
| 成功图景 | 做成什么样？ | OBJ 的成效指标方向 |
| **缺失：解决方案方向** | **怎么解决？** | **Epic 的技术/产品路线选择** |

**推迟理由**：

1. **YAGNI**：6 处实现断裂未修复前，新增字段只会扩大"Schema 声明 vs 实际实现"的鸿沟
2. **理论稳定性**：theory.md §3.0c 将核心要素定义为四项，这是经过理论推导的对称结构。无用户反馈证明"缺少解决方案方向导致 OBJ 分解质量差"
3. **功能已部分覆盖**：project-format.md §1.1 的 blockquote 已承载"项目定位"信息，部分覆盖了"解决方案方向"

**列入 backlog**：当实现断裂修复完成 + 至少 2 个真实项目验证后，若 Claude 在 OBJ 分解时频繁缺乏方向性约束，再重新评估。

#### 问题 B：北极星指标"唯一性"规则过于刚性 ⏸️ 推迟

vision-format.md:115 规定"每个产品只有一个北极星指标"。这在理论上是正确的（单一聚焦），但在实践中有两个问题：

1. **早期项目难以确定北极星**：产品愿景清晰不等于已确定量化指标。强制"唯一"可能导致用户选择一个不成熟的指标，或干脆留空
2. **北极星指标可能随产品阶段变化**：初创期关注 DAU，增长期关注留存率，成熟期关注 ARPU——但 Schema 没有版本化或演进机制

**方案评估**：

| 维度 | 候选北极星方案 | 阶段标注方案（推荐） |
|------|-------------|-------------------|
| "聚焦一个"纪律 | 弱化风险高——多候选让"不选择"合法化 | 保持——始终一个指标，阶段是附加上下文 |
| Agent Legibility | Claude 需判断"当前选定"是哪个 | 只需读一个指标 + 一个标签 |
| OBJ 影响 | obj-format 北极星贡献需区分指向哪个候选——连锁修改 | 无需修改 |
| 体量 | +15~20 行 | +5~8 行 |

**推迟理由**：

1. **无消费者**：pace-retro 完全不读 vision.md（断裂 3），北极星字段整体缺乏消费方
2. **现有设计已容错**：北极星为"渐进"字段，空值不阻塞功能——早期不确定时可暂不填
3. **候选方案弊大于利**：即使未来实施，也应选阶段标注而非候选机制

**列入 backlog 附带预案**：当断裂 3 修复 + pace-retro 消费北极星后，若用户反馈需要记录指标演进，实施**阶段标注方案**：

```markdown
## 北极星指标

**指标**：[单一核心量化指标]
**阶段**：[验证期 | 增长期 | 成熟期]（可选，默认不显示）
**当前值**：...
**目标值**：...
```

### 5.3 落地执行的根本挑战

Vision 的落地执行面临一个根本挑战：**它是最抽象的层级，也是最依赖人类输入、最难自动化验证的层级。**

| 层级 | 自动化程度 | 验证难度 |
|------|-----------|---------|
| CR | 高（Hook 守护、Gate 检查、代码 diff） | 低（明确的通过/失败） |
| PF/BR | 中（Schema 格式校验、就绪度计算） | 中（验收标准可核对） |
| Epic/OBJ | 低（MoS 达成度人工确认） | 高（成效指标需人类判断） |
| **Vision** | **极低**（Claude 不推断愿景） | **极高**（战略方向对错无客观标准） |

Vision 的落地不能靠自动化守护（不像 CR），而是要靠**触发+引导+回顾+对齐的人机协同四环闭环**：

```
触发：什么时候提醒用户关注 Vision？
      -> pace-init（创建）+ 信号系统（缺失/过期）+ pace-retro（回顾）

引导：Claude 如何帮助用户产出有效 Vision？
      -> 引导提问（不是推断）+ 框架化结构 + 最小有效状态检测

回顾：Vision 如何随项目演进而更新？
      -> pace-retro 北极星当前值 + 假设状态 + 度量链贡献分析

对齐：下游决策如何回溯 Vision？
      -> align 的 Vision->OBJ 检查 + OBJ 贡献索引 + trace 链路
```

**当前四环中三环断裂**（触发仅有 pace-init full、引导仅有 init-procedures-full 的 4 个问题、回顾完全缺失、对齐完全缺失），这才是"vision.md 无法有效落地"的系统性原因。

---

## 六、全部优化建议汇总与执行结果

| # | 维度 | 建议 | 决策 | 结果 |
|---|------|------|:----:|------|
| E | Schema 语义 | 定义"最小有效状态"（三字段有效性判定） | ✅ 已实施 | vision-format.md:77-90 新增定义，+15 行 |
| C | Schema 字段 | 核心假设扩展为结构化格式（验证方式+验证结果） | ✅ 已实施 | vision-format.md:43-45, 63-65, 119, 173 修改，+7 行 |
| D | Schema 结构 | 北极星指标 section 增加 OBJ 贡献索引 | ❌ 评审否决 | 动态查询替代静态索引（待 align 实现时在 procedures 中实现） |
| A | Schema 字段 | 核心愿景增加"解决方案方向"字段 | ⏸️ 推迟 | YAGNI + 理论稳定性 + 功能已部分覆盖。列入 backlog |
| B | Schema 字段 | 北极星指标增加"候选"或"阶段"字段 | ⏸️ 推迟 | 无消费者 + 现有容错已足够。阶段标注预案备用 |
| F | 实现补齐 | P0/P1/P2 的 8 项实现断裂修复（第四章） | 待实施 | Schema 层优化已完成，实现层修复可独立推进 |

**实际变更**：vision-format.md 151→173 行（+22 行，+14.6%），validate-all.sh 全部通过。

**核心结论**：

> **Schema 是契约，不是实现。** vision-format.md 声明了"谁在什么时候做什么"，但消费方的 procedures 尚未履行契约。Schema 层面已补齐"最小有效状态"定义和"结构化假设"格式——修复的下一步是让 procedures 履行 Schema 已定义好的契约（第四章 P0/P1/P2 实现断裂修复）。

### Agent Team 工作流记录

本次优化通过 `vision-schema-optimize` Agent Team 的四阶段工作流完成：

| Phase | Agent | 角色 | 产出 |
|-------|-------|------|------|
| 1A | designer-high | Schema 设计专家 | E+D 方案（含完整 Schema 变更、影响评估、向后兼容分析） |
| 1B | designer-low | 业务需求分析专家 | A+C+B 方案（含利弊分析、PROPOSE/DEFER/REJECT 判定） |
| 2 | reviewer | 架构评审专家 | IA/HE/YAGNI 多维评审（E:REVISE, D:REJECT, C:REVISE, A:DEFER, B:DEFER） |
| 3 | executor | Schema 工程师 | 执行 E+C 修改 + validate-all.sh 验证通过 |
| 4 | final-reviewer | 质量工程师 | 12 项检查清单逐项评审（11 PASS + 1 次要修复 README.md 行数）|
