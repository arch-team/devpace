# DevPace 四大痛点解决方案对照分析

> **来源**：Harness Engineering AI研发实践v1.0.pdf 第4页 "为什么需要 DevPace"
> **日期**：2026-04-07
> **目的**：将 PPT 第4页提出的四个 AI 辅助开发系统性缺陷，与 devpace 当前实现逐一对照分析

---

## 概述

第4页指出 AI 辅助开发存在四个维度的系统性缺陷，DevPace 填补"AI 研发过程管理"空白：

| # | 痛点 | DevPace 解决方向 |
|---|------|-----------------|
| 1 | 跨会话上下文断裂 | state.md 自动保存恢复 |
| 2 | 质量不一致 | 四层门禁不可跳过 |
| 3 | 价值与技术脱节 | 完整追溯链 CR→PF→BR→OBJ |
| 4 | 需求变更导致失序 | 变更是一等公民 |

---

## 1. 跨会话上下文断裂

### 痛点

- 每次新会话重新解释上下文
- 解释时间 > 写代码时间

### devpace 实现

| 机制 | 实现方式 |
|------|---------|
| **state.md 自动保存/恢复** | 15 行以内的快照文件，记录"目标/正在做什么/下一步"三要素 |
| **session-start.sh Hook** | 会话启动自动检测 `.devpace/state.md`，注入恢复指令给 Claude |
| **session-stop.sh Hook** | 每次 `end_turn` 提醒 Claude 保存状态 |
| **L/XL CR 步骤定位** | `→ 步骤 N/M：[描述]` 精确到执行计划的具体步骤 |
| **Checkpoint 机制** | 每个原子步骤后 git commit + 更新 state.md，中断后可从最近点恢复 |

### state.md 字段设计

文件硬限制 **15 行以内**，按项目复杂度自适应：

**必需字段**：

| 字段 | 内容 |
|------|------|
| 头部 blockquote：目标行 | `> 目标：[业务目标] → 成效指标：[MoS]` |
| 头部 blockquote：专题行（可选） | `> 专题：N 进行中 \| M 已完成`（有 Epic 时） |
| 头部 blockquote：迭代行（可选） | `> 迭代：[ID]（[目标]）\| 进度：M/N` |
| 当前工作 | `进行中`、`待 Review`、`阻塞` 三种状态的列表；L/XL CR 含步骤定位 |
| 下一步 | 1-2 行，Claude 下次会话的行动建议 |
| 版本标记 | `<!-- devpace-version: 1.6.1 -->` |
| 教学标记 | `<!-- taught: cr,gate1,review,... -->`（渐进教学去重） |

**可选字段**（按复杂度递增）：
- 关键决策（4-10 CR 时）：最近 3 个决策摘要
- 风险关注（>10 CR 时）：最高优先级 2-3 项
- 发布状态（有活跃 Release 时）：REL-xxx 的当前状态

### 读写 state.md 的组件

**写入方**：

| 写入者 | 时机 |
|--------|------|
| pace-init | 初始化时创建 state.md |
| pace-dev | 每个原子步骤 checkpoint + 会话结束 |
| pace-change | 变更执行后更新当前工作和下一步 |
| pace-plan | 新迭代创建后反映迭代信息 |
| pace-release | 创建/部署/关闭/回滚 Release 时更新发布状态段 |
| pace-feedback | 新增缺陷时 |
| pace-guard | 风险状态变化时 |
| pace-test | 测试状态变化时 |
| pace-review | CR merged 后连锁更新 |
| 渐进教学 (Section 15) | 首次教学后追加 taught 标记 |
| Session Stop Hook | 提醒 Claude 保存 state.md |

**读取方**：

| 读取者 | 用途 |
|--------|------|
| session-start.sh Hook | 会话启动时检测并提示 Claude 恢复上下文 |
| session-end.sh Hook | 检查 L/XL 活跃 CR 需要刷新快照 |
| subagent-stop.mjs Hook | 子 Agent 停止后检查 state 一致性 |
| pre-tool-use.mjs Hook | 探索模式下阻止 state.md 写入 (IR-1) |
| skill-eval.mjs Hook | 检查 state.md 是否存在来判断项目状态 |
| pace-dev | 无参数时从 state.md 读取"下一步"；`--last` 从"进行中"推断 |
| pace-next | 读取当前工作判断优先信号 |
| pace-status | 渲染状态概览 |
| pace-pulse | 周期性信号检测 + 会话开始/结束节奏检测 |
| pace-help | 上下文感知帮助 |
| pace-biz | 读取项目上下文 |
| pace-theory | 读取当前状态和角色偏好 |
| pace-guard | 确定当前 CR 和项目状态 |
| pace-change | 影响分析时读取 |

### 用户说"继续"时的恢复流程

**第一步：Hook 触发（自动）**

`hooks/session-start.sh` 在每次会话启动时执行。它检测 `.devpace/state.md` 是否存在，如存在则输出：

```
devpace:session-start Active project detected.
ACTION: Read .devpace/state.md to restore project context and identify active CRs;
then resume in-progress work.
```

**第二步：Claude 执行规则 Section 1（会话开始协议）**

1. 读取 `.devpace/state.md`，校验格式（缺字段补默认值，格式损坏则基于 git log 重建）
2. 用 1 句自然语言报告当前状态和建议
3. 如有 developing/verifying CR，附加 `[推进中]` 标识
4. 无进行中 CR，附加 `[探索]` 标识

**第三步：节奏健康度检测（自动叠加）**

额外执行 pulse-procedures-session-start.md 的分层信号检测，输出最高 1 条完整建议 + 其余触发信号精简列表（总计 3 行以内）。

**第四步：等待用户指令**

Claude 不自作主张开始工作，等用户说"继续"或给出具体指令。

**第五步：恢复到精确工作点**

- **S/M CR**：从"下一步"字段读取恢复建议
- **L/XL CR**：从步骤定位标记 + CR 事件表最后一个 `step_N_done` 事件，精确定位到执行计划的下一步

### 保障机制

1. **被动安全网（Checkpoint）**：每个原子步骤后 git commit + 更新 CR 事件 + 更新 state.md
2. **主动保存（会话结束）**：强制执行 state.md + CR 更新 + 3-5 行摘要
3. **Stop Hook 提醒**：每次 end_turn 提醒 Claude 保存状态
4. **Session End Hook**：会话结束时检查 L/XL 活跃 CR 并刷新恢复建议
5. **子 Agent 一致性检查**：子 Agent 停止后检测 state.md 与 CR 状态的不一致
6. **探索模式保护（IR-1）**：探索模式下硬拦截 state.md 写入，防止误修改
7. **容错自愈**：缺字段补默认值、格式损坏基于 git log 重建、版本不匹配提示但不阻断
8. **O(1) 规模保证**：state.md 是快照设计而非累积设计，始终 15 行以内

### 用户体验

新会话开始 → Hook 自动触发 → Claude 读 state.md → 1 句话报告当前状态 → 用户说"继续"即可。**零手动解释**。

---

## 2. 质量不一致

### 痛点

- Claude 有时跳过测试/检查
- 同项目质量参差不齐

### devpace 实现：三层门禁体系

| 门禁 | 状态转换 | 性质 | 核心检查内容 |
|------|---------|------|-------------|
| **Gate 1** | developing → verifying | **自动**（Claude 执行） | 代码质量：编译、测试、lint、typecheck、需求完整性 |
| **Gate 2** | verifying → in_review | **自动**（Claude 执行） | 需求质量：意图一致性检查 + 对抗审查（Adversarial Review） |
| **Gate 3** | in_review → approved | **人工**（人类审批，铁律不可绕过） | 人类审批：Review 摘要展示后等待人类明确说"批准" |

### Gate 1（代码质量门禁 -- 自动）

- **检查类型**：命令检查（bash exit code 判定）+ 意图检查（Claude 语义判定）
- **内置必检项**（不可删除）：需求完整性——CR 意图 section 与变更复杂度匹配
- **项目自定义检查**：通过 `.devpace/rules/checks.md` 配置（如 `pytest -v`、`npm run lint`、`tsc --noEmit`）
- **推荐安全检查**：`npm audit`、`bandit`、`gosec`、`cargo audit`、密钥泄露检测
- **S-CR 裁剪**：S 复杂度 CR 执行裁剪版 Gate 1，跳过与变更文件无交集的检查项
- **失败自修复**：命令检查失败后 Claude 分析输出并自动修复代码，然后重跑
- **通过后行为**：写入 `gate1_pass` 事件 + 验证证据摘要 + 轻量反思（技术债/测试覆盖）

### Gate 2（需求质量门禁 -- 自动）

- **意图一致性检查**：独立验证原则（不信任 Gate 1 快照），从零重新读取验收条件和 git diff，逐条对比
- **范围外改动检测**：对比实际变更与声明范围，标识"合理扩展"或"范围蔓延"
- **范围内遗漏检测**：检查声明要做但未做的内容
- **对抗审查（Adversarial Review）**：强制发现问题机制——Claude **必须**找出至少 1 个问题，零发现不可接受。审查 4 个维度：
  - 边界与错误路径
  - 安全风险
  - 性能隐患
  - 集成风险
- **关键规则**：对抗审查不影响 Gate 2 通过/失败判定（因预期产生假阳性），发现仅供人类参考

### Gate 3（人类审批门禁 -- 人工）

- **铁律**：in_review → approved 必须由人类明确批准，任何自动化尝试都被 Hook **硬阻断**（exit code 2）
- **Review 摘要**：由 `/pace-review` 生成，按复杂度分级：
  - S 微型：3-5 行
  - M 标准：含意图匹配和对抗审查
  - L-XL 完整：含 TL;DR
- **简化审批**：S 复杂度 + Gate 1/2 均一次通过 + 0% 漂移 → 可跳过完整 review 流程，内联确认
- **批量审批**：2+ 个 S-CR 同时 in_review 且均满足简化条件时，可一次性批准

### Hook 质量守护体系

| 事件 | Hook 文件 | 阻断/建议 | 质量作用 |
|------|----------|----------|---------|
| PreToolUse (Write\|Edit) | `pre-tool-use.mjs` | **阻断** (exit 2) | Gate 3 铁律执行 + 探索模式状态保护 |
| PreToolUse (pace-dev 内) | `skill/pace-dev-scope-check.mjs` | 建议 (exit 0) | 范围漂移警告 |
| PreToolUse (pace-review 内) | `skill/pace-review-scope-check.mjs` | 建议 (exit 0) | Review 写入范围验证 |
| PostToolUse (Write\|Edit) | `post-cr-update.mjs` | 建议 (exit 0) | CR 状态转换检测 + Gate 失败学习触发 |
| PostToolUse (Write\|Edit) | `pulse-counter.mjs` | 建议 (exit 0) | 写操作计数 + 卡住检测 |
| PostToolUse (Write\|Edit) | `sync-push.mjs` | 建议 (exit 0) | 状态变更同步提醒 |
| PostToolUse (Write\|Edit) | `post-schema-check.mjs` | 建议 (exit 0) | Schema 格式自动校验 |
| PostToolUseFailure | `post-tool-failure.mjs` | 建议 (exit 0) | 写入失败后状态一致性检查 |
| UserPromptSubmit | `skill-eval.mjs` | 建议 (exit 0) | 强制 Skill 评估，确保正确路由 |
| SubagentStop | `subagent-stop.mjs` | 建议 (exit 0) | 子 agent 结束后状态一致性检查 |

### Hook 硬阻断（exit 2）详情

仅存在于 `pre-tool-use.mjs`：

1. **Gate 3 铁律执行**：CR 处于 `in_review` 状态时，任何试图将状态写为 `approved` 的 Write/Edit 操作被**直接阻断**
2. **探索模式状态保护**：项目不在"推进模式"时，阻断对 `state.md` 的修改和 CR 状态升级

### 质量机制全景

| 机制 | 自动/人工 | 阻断级别 | 说明 |
|------|----------|---------|------|
| Gate 1 质量检查 | 自动 | 流程阻断 | 命令检查 + 意图检查 |
| Gate 2 需求检查 | 自动 | 流程阻断 | 意图一致性 + 对抗审查 |
| Gate 3 人类审批 | **人工** | Hook **硬阻断** | 铁律，不可被 AI 绕过 |
| 探索模式保护 | 自动 | Hook **硬阻断** | 防止非推进模式下修改状态 |
| 范围漂移检测 | 自动 | 建议 | 开发过程中每次 checkpoint 检查 |
| 复杂度漂移检测 | 自动 | 建议 | S→M 或 M→L 升级警告 |
| 语义漂移检测 | 自动 | 建议 | 代码是否偏离验收标准 |
| Schema 格式校验 | 自动 | 建议 | CR/state/project 文件格式检查 |
| 对抗审查 | 自动（Claude） | 不阻断 Gate 2 | 强制找问题，结果供人类参考 |
| 卡住检测 | 自动 | 建议 | 同一 CR 反复写入 5+ 次警告 |
| Pre-flight 风险扫描 | 自动 | 取决于风险等级 | L/XL CR 自动触发 |
| High 风险人类确认 | **人工** | 暂停等确认 | 与 Gate 3 同级铁律 |

### 核心设计哲学

1. **机制级执行而非文字级约束**：Gate 3 通过 `pre-tool-use.mjs` 以 exit code 2 **物理阻断**——即使 Claude 无视规则也无法绕过
2. **三层检查类型互补**：命令检查（确定性工具）+ 意图检查（语义理解）+ 对抗审查（对抗确认偏差）
3. **证据驱动**：每次 Gate 通过必须附带当次验证运行的证据摘要
4. **渐进精细化**：S-CR 裁剪版（低成本），L/XL 全量版（高保障），按变更规模自适应

---

## 3. 价值与技术脱节

### 痛点

- 功能增多后偏离业务目标
- 不知代码为谁而写

### devpace 实现：完整价值链 Schema

#### 价值功能树

```
Vision（北极星指标）
  └─ OBJ（业务目标）── 北极星贡献字段向上连接
      └─ Epic（专题）── OBJ 字段（支持主/副双目标）
          └─ BR（业务需求）── Epic + OBJ + 来源(OPP) 字段
              └─ PF（产品功能）── BR→Epic→OBJ 完整上溯
                  └─ CR（变更请求）── PF→BR→Epic 一行写完整链路
```

在 `project.md` 中以树形结构呈现：

```
Vision（北极星指标）
└── OBJ-001（业务目标）
    ├── EPIC-001（专题）
    │   ├── BR-001（业务需求）
    │   │   ├── PF-001（产品功能）→ CR-001（变更请求）
    │   │   └── PF-002 → CR-002, CR-003
    │   └── BR-002 → PF-003 → CR-004
    └── EPIC-002
        └── BR-003 → PF-004 → CR-005
```

OPP（Opportunity）作为侧面输入，经评估后可转化为 Epic。

#### 8 层实体 Schema

| 文件 | 实体 | 层级角色 |
|------|------|---------|
| `vision-format.md` | Vision（产品愿景） | 最高层：北极星指标 + 核心愿景 |
| `obj-format.md` | OBJ（业务目标） | 战略层：业务/产品/技术目标 |
| `opportunity-format.md` | OPP（业务机会） | 输入层：机会捕获与评估 |
| `epic-format.md` | EPIC（专题） | 组织层：跨需求的专题分组 |
| `br-format.md` | BR（业务需求） | 需求层：业务上下文 + 成效指标 |
| `pf-format.md` | PF（产品功能） | 功能层：验收标准 + 用户故事 |
| `cr-format.md` | CR（变更请求） | 执行层：代码变更的完整生命周期 |
| `project-format.md` | Project（项目全景） | 容器：价值功能树的载体 |

#### 每个实体的追溯字段

**CR（变更请求）**：
- `产品功能`：`[PF 标题]（[PF-ID]）→ [BR 标题]（[BR-ID]）→ [Epic 标题]（[EPIC-ID]）` —— 一行写完整上溯链路

**PF（产品功能）**：
- `BR`：`[BR 名称]（[BR-ID]）→ [Epic 名称]（[EPIC-ID]）→ [OBJ-xxx：目标描述]` —— 完整上溯到 OBJ

**BR（业务需求）**：
- `Epic`：`EPIC-xxx（专题名称）`
- `OBJ`：链接到 OBJ 文件
- `来源`：`OPP-xxx | 日常需求`
- `成效指标（MoS）`：双维度（客户价值 + 企业价值）

**Epic（专题）**：
- `OBJ`：支持主/副双目标关联
- `来源`：从 OPP 转化时记录

**OBJ（业务目标）**：
- `北极星贡献`：描述 OBJ 如何贡献到 Vision 的北极星指标
- `成效指标（MoS）`：双维度（客户价值 + 企业价值）

**OPP（业务机会）**：
- `来源`：用户反馈 | 竞品观察 | 技术发现 | 市场趋势 | 内部洞察
- `状态`：评估中 → `已采纳 → EPIC-xxx`

#### 追溯关系全景

```
Vision.北极星指标
    ↑ OBJ.北极星贡献
OBJ (objectives/OBJ-xxx.md)
    ↑ Epic.OBJ字段（主/副）  |  BR.OBJ字段（无Epic时）
Epic (epics/EPIC-xxx.md)          ← OPP.状态="已采纳→EPIC-xxx"
    ↑ BR.Epic字段
BR (requirements/BR-xxx.md)       ← BR.来源=OPP-xxx
    ↑ PF.BR字段
PF (features/PF-xxx.md)
    ↑ CR.产品功能字段
CR (backlog/CR-xxx.md)
```

#### 追溯查询 Skill 矩阵

| Skill | 回答的问题 |
|-------|-----------|
| `/pace-status trace <name>` | "这个目标完成到哪了？"——从 OBJ/BR/PF 向下追溯完成度 + MoS 达成率 |
| `/pace-status chain` | "我当前在价值链的什么位置？"——定位活跃 CR 在价值树中的位置 |
| `/pace-status tree` | 展示完整的价值功能树全景 |
| `/pace-trace` | "Claude 为什么这样判断？"——Gate/意图/风险/变更决策的审计轨迹 |
| `/pace-feedback trace` | "这个问题关联到哪个需求？"——从问题反向追溯到 PF/BR |
| `/pace-retro` | 计算"价值链完整率"——有完整 BR→PF→CR 链路的占比 |

**核心保障**：CR 的 `产品功能` 字段**强制要求**写出 PF→BR→Epic 完整链路。每个代码变更都必须回答"为谁而写"。追溯随迭代自然加深——渐进丰富而非一次性负担。

---

## 4. 需求变更导致失序

### 痛点

- 影响范围未知，进度混乱
- 不知哪些工作需返工

### devpace 实现：变更是一等公民

设计文档明确宣言：

> **变更不是异常，是常态。** devpace 把变更当作一等公民——这是与纯任务管理工具的核心差异。

#### 双入口设计

- **自动检测**：`devpace-rules.md §9` 自动检测变更意图触发词（零摩擦）
- **显式调用**：`/pace-change` 结构化调用
- 两者共享同一套 procedures 文件

#### 七步流水线

```
Step 0: 经验预加载（insights.md 历史 pattern 匹配）
Step 1: Triage 分流（Accept / Decline / Snooze）
Step 2: 影响分析（四层追踪 BR → PF → CR → 代码）
Step 3: 风险量化（波及模块 × 受影响 CR × 需重置检查）
Step 4: 调整方案展示 + 等待人类确认
Step 5: 原子性执行（单次 git commit 更新所有受影响文件）
Step 6: 下游引导 + 外部同步提醒
```

#### Step 1：Triage 分流

三个决策路径：

| 决策 | 行为 |
|------|------|
| **Accept** | 进入影响分析 |
| **Decline** | 记录原因并归档 |
| **Snooze** | 持久化记录（含触发条件），由 pulse 系统在会话开始/新迭代/CR merge 时自动检测唤醒 |

- Hotfix/Critical 级别自动 Accept，跳过 Triage
- 每条 Snooze 仅唤醒提醒 1 次

#### Step 2：影响分析（四层追踪 + 三层分级输出）

**四层追踪**：BR（业务需求）→ PF（产品功能）→ CR（变更请求）→ 代码（模块/文件/接口）

**三层分级输出**（降低日常阅读量从 15-20 行到 3-5 行）：

| 层级 | 触发条件 | 内容 |
|------|---------|------|
| **表面层**（默认） | 低风险 | 1 行结论，如"这个变更影响 2 个功能，综合风险低" |
| **中间层** | 追问或中风险自动展开 | 3-5 行，列出受影响功能和风险概要 |
| **深入层** | 再追问或高风险自动展开 | 完整四层追踪 + 风险三维表 + 传递性依赖链 + Mermaid 可视化 |

- **传递性依赖链**：最多追踪 3 层（直接 → 间接 → 深度）
- **角色适配**：表面层措辞按 Biz Owner / PM / Dev / Tester / Ops 角色调整
- **BR 级升报**：变更涉及 BR 下 >=50% PF 时自动升级到 BR 视角
- **Release 影响评估**：涉及已发布 CR 时额外评估对 Release 稳定性的影响

#### Step 3：风险量化（三维评分）

| 维度 | 低 | 中 | 高 |
|------|:--:|:--:|:--:|
| 波及模块数 | <=2 | 3-5 | >5 |
| 进行中 CR 受影响数 | 0 | 1-2 | >=3 |
| 质量检查需重置数 | 0 | 1-3 | >3 |

- 成本估算基于 insights.md 历史数据或启发式规则
- 高风险额外输出：测试重点区域 + 分步执行策略

#### Step 4-6：方案确认 + 执行 + 下游引导

- **确认门禁**：Claude 分析但不自作主张——变更涉及业务决策，**必须人类确认后才执行**
- **原子性执行**：CR 文件 → project.md → PF 文件 → iterations/current.md → state.md → dashboard.md，单次 git commit
- **双写记录**：变更事件同时写入迭代文件（宏观）和 CR 事件表（微观）
- **下游引导**：按变更类型精确引导后续操作 + 外部关联同步提醒

#### 五种核心变更场景

| 场景 | 用户意图 | 初始（信息轻量） | 丰富后（多功能+业务目标） |
|------|---------|----------------|--------------------------|
| **add** | "还要加一个 X" | 创建 CR，标注所属功能 | 创建 CR + 功能影响分析 + MoS 评估 |
| **pause** | "X 先不做了" | CR→paused，通知关联功能 | 功能级联暂停 + 功能树更新 + MoS 重评估 |
| **resume** | "把 X 恢复" | CR 恢复到暂停前状态 | 恢复 + 迭代容量评估 + 质量检查有效性验证 |
| **reprioritize** | "X 优先做" | 重排 CR，更新 state.md | 基于业务优先级重排功能和 CR |
| **modify** | "X 还要支持 Y" | 更新 CR 描述，重置质量检查 | 评估功能级返工 + 追溯业务目标影响 |

#### 四种扩展子命令

| 子命令 | 用途 |
|--------|------|
| **batch** | 合并多个变更的影响分析和执行，交叉影响检测 |
| **undo** | 基于 git revert 精确回滚上次 /pace-change 操作（仅限当前会话） |
| **history** | 从四个数据源聚合变更历史，同一 PF 变更 > 3 次时主动告警 |
| **apply** | 应用预定义变更模板，填入参数后走标准流程 |

#### 降级模式

无 `.devpace/` 时仍可工作：
- Triage 简化为口头确认
- 影响分析基于 Glob/Grep/Read 扫描代码结构 + import/require 依赖图 + git co-change/hotspot 分析
- 风险量化仅能评估模块波及，CR 和质量检查维度标注"无法评估"
- 累计 3+ 次使用后，引导语从标准版升级为强化版

---

## 总结：PPT 简述 vs 实际实现深度

| PPT 简述 | 实际深度 |
|---------|---------|
| "state.md 自动保存恢复" | 15 行快照 + 6 个 Hook 协同 + L/XL 步骤级精确定位 + 容错自愈 |
| "四层门禁不可跳过" | Gate 1/2 自动 + Gate 3 Hook 物理阻断 + 对抗审查对抗确认偏差 + 复杂度自适应 |
| "完整追溯链 CR→PF→BR→OBJ" | 8 层 entity schema + 6 个追溯 Skill + project.md 价值功能树 + 双维度 MoS |
| "影响分析→方案→确认→执行" | 七步流水线 + 五种变更场景 + 三层渐进输出 + 降级模式 + 经验驱动校准 |

**底部注释**：DevPace 不替代 GitHub Issues / Jira / Linear，而是补充——管的是"Claude Code 项目级研发节奏"，通过 /pace-sync 协同。
