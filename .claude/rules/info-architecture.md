# 信息架构规则（devpace 适配）

> **职责**：将通用 IA 原则（`references/common-ia.md`）映射到 devpace 项目结构（`references/plugin-info-layers.md`）的具体规则。

Plugin 不是程序，是通过组织化 Markdown 塑造 LLM 行为的**信息架构**。传统软件靠编译器确定性执行；Plugin 靠 LLM 概率性解释——信息组织失误直接导致行为偏差。

## §0 速查卡片

### 11 原则一览（devpace 层级映射）

| # | 原则 | 一句话 | 对应层级 |
|---|------|--------|---------|
| IA-1 | 单向依赖 | 信息从抽象流向具体，不可反向 | 全局（层间关系） |
| IA-2 | 抽象分层 | 不同抽象层级放在不同文件 | Layer 6-1 |
| IA-3 | 稳定-易变分离 | 高频变更内容不耦合低频内容 | 全局（变更频率） |
| IA-4 | 信息分类 | 不同信息类型不混放 | 全局（类型维度） |
| IA-5 | 按需加载 | 只加载当前上下文所需的最小信息集 | Layer 3-1 |
| IA-6 | 单一权威 | 每条信息有且仅有一个权威定义点 | 全局（同步维度） |
| IA-7 | 确定性分级 | 约束的执行保障级别匹配其关键程度 | Layer 5 + Hooks |
| IA-8 | 可发现性优先 | 入口信息为发现而设计，不为完整而设计 | Layer 3（description） |
| IA-9 | 认知清晰 | 面向 LLM 的指令精确无歧义，阻止合理化绕过 | 全局（精确性） |
| IA-10 | 契约隔离 | 数据格式由独立契约层约束 | Layer 4 |
| IA-11 | 单一职责 | 每个文件只有一个核心职责 | 全局（职责内聚） |

通用原则定义与约束分级标记：详见 `references/common-ia.md`。
六层架构与信息类型映射：详见 `references/plugin-info-layers.md`。

## §1 单向依赖（IA-1）

> **核心**：信息从抽象流向具体——上层定义，下层实现，不可反向引用。

**规则**：
1. 分发层（`rules/`、`skills/`、`knowledge/`）不得引用开发层（`docs/`、`.claude/`） `iron rule`
2. 六层架构中，下层文件只引用同层或上层文件 `required`
3. 合法的"反向注释"仅限两种：上层的**映射说明**（解释如何对应到下层）和**权威委托**（显式标记"详见 XXX"） `recommended`

**正确**：`rules/devpace-rules.md` 引用 `knowledge/theory.md`（同层/上层引用）
**错误**：`skills/pace-dev/SKILL.md` 引用 `docs/design/design.md`（分发层 → 开发层）

**检测**：`grep -r "docs/\|\.claude/" rules/ skills/ knowledge/` 应返回空

**预防合理化**：`"只是引用一下设计文档的章节编号" → 分发层必须独立可分发，任何开发层引用都破坏这一点`

## §2 抽象分层（IA-2）

> **核心**：不同抽象层级的内容放在不同文件——路由与步骤分离，Manifest 与组件分离。

**规则**：
1. `.claude-plugin/` 仅放 `plugin.json` + `marketplace.json`；所有组件在 Plugin 根目录 `iron rule`
2. SKILL.md 放路由逻辑（"做什么"）；详细步骤超 ~50 行时拆出 `*-procedures.md`（"怎么做"） `recommended`
3. 每个文件包含单一主抽象层级 `recommended`

**正确**：SKILL.md 含 100 行路由表 + 输入/输出定义；procedures 文件含分步指令
**错误**：SKILL.md 内嵌 500 行详细指令与路由逻辑混杂

**检测**：SKILL.md 超过 ~500 行 → 疑似层级混杂，检查是否需要分拆

**预防合理化**：`"内容不多，放一起方便" → 超过 50 行详细规则就该拆；合并不是方便，是让 LLM 混淆路由与执行`

## §3 稳定-易变分离（IA-3）

> **核心**：被广泛依赖的文件应保持高稳定性；高频变更内容应隔离到独立文件。

**规则**：
1. 被多个 Skill 引用的文件（schema、theory）维持低变更频率 `recommended`
2. 始终加载的文件（rules）控制体量；膨胀时将稳定核心与易变索引分拆 `recommended`
3. 加载策略与稳定性对齐：最稳定的被动加载（按引用）；最易变的条件路由加载 `recommended`

**检测**：`git log --oneline <file> | wc -l` — 被多处引用的文件若变更频率高于其依赖者，考虑分拆

## §4 信息分类（IA-4）

> **核心**：不同类型的信息不混放——步骤、约束、概念、结构、路由、实例各归其位。

**规则**：
1. 一个文件包含一种主信息类型 `recommended`
2. 任务内容（执行指令）与参考内容（背景知识）分开存放 `recommended`
3. 背景知识放 `knowledge/`，约束放 `rules/`，执行步骤放 `*-procedures.md` `recommended`

**检测**：审查文件内容，若同一文件包含大段理论 + 分步指令 + 格式定义，则违反 IA-4

## §5 按需加载（IA-5）

> **核心**：只加载当前上下文所需的最小信息集——上下文窗口是硬约束，浪费即降质。

**规则**：
1. `description` 仅提供触发信息；完整内容在激活后才加载 `iron rule`
2. 复杂 Skill 使用两级延迟加载：SKILL.md（路由）→ procedures（操作） `recommended`
3. `knowledge/` 文件被动加载（按引用），不主动注入上下文 `recommended`
4. 上下文预算：description < 300 字符，SKILL.md < 500 行，单次执行加载 < 800 行 `recommended`

加载策略详见 `references/plugin-info-layers.md`。

**正确**：SKILL.md 加载 80 行路由表，根据当前状态加载一个 200 行 procedures 文件
**错误**：SKILL.md 一次性加载全部 6 个 procedures 文件（1200+ 行），不论当前状态

**检测**：衡量每次 Skill 调用消耗的上下文 token；单次加载超 800 行需警示

**预防合理化**：`"提前加载省得来回切换" → 多加载的内容不只浪费 token，还会污染推理（步骤泄漏）`

## §6 单一权威（IA-6）

> **核心**：每条信息有且仅有一个权威定义点——DRY 从"消除重复"变为"管理重复"。

**规则**：
1. 每个信息项有一个权威文件；派生文件注明来源 `recommended`
2. 多处出现的内容使用"源 → 派生"树模型管理 `recommended`
3. 变更沿 源 → 派生 方向传播；派生文件不得单方面修改权威内容 `recommended`

**合法反 DRY 场景**：
- §0 速查摘要——为快速索引的刻意冗余（IA-5 按需加载优先于 IA-6）
- 权威委托标记——上层用"（权威源）"后缀委托下层详细定义

**正确**：SKILL.md 定义子命令（源）→ rules.md §0 索引子命令（派生，注明"详见 SKILL.md"）
**错误**：SKILL.md 和 rules.md 各自独立定义子命令行为，无权威声明

**检测**：对每个多处出现的内容，确认有一个文件被显式标记为权威；grep 确认派生文件引用它

## §7 确定性分级（IA-7）

> **核心**：约束的执行保障级别必须匹配其关键程度——安全关键规则不能只靠文本。

**规则**：
1. 约束按关键程度选择执行机制（四级保障详见 `references/component-reference.md`） `iron rule`
2. 高级安全规则采用"三重保险"：Hook 阻断 + Rules 声明 + 铁律标记 `recommended`

**检测**：每条铁律都有对应的 Hook 或自动化测试执行保障

## §8 可发现性优先（IA-8）

> **核心**：入口信息为发现（When）而设计，不为完整（What）而设计。

**规则**：
1. SKILL.md `description` 仅写触发条件（When），不写行为描述（What） `iron rule`
2. `description` 使用具体触发关键词（"Use when user says '开始做/实现/修复'"） `recommended`
3. 每个 rules/ 和 _schema/ 文件提供 §0 速查卡片 `recommended`

**正确**：`description: Use when user requests development work or says "implement/fix/build"`
**错误**：`description: Analyzes code quality, runs gate checks, generates diff summary, updates status`

**检测**：审查所有 `description` 字段——不应包含描述内部动作的动词

**预防合理化**：`"写清楚做什么帮助用户理解" → description 的消费者是 Claude 的路由逻辑，不是用户；写了 What 会导致 Claude 跳过读完整 SKILL.md 直接按摘要行动`

## §9 认知清晰（IA-9）

> **核心**：面向 LLM 的指令精确无歧义——阻止合理化绕过。

**规则**：
1. 平台约束（frontmatter 字段、Hook 大小写、路径格式、零摩擦入门）严格遵循官方规格（详见 `plugin-dev-spec.md`） `iron rule`
2. 铁律配反合理化清单——列举可能的绕过借口及反驳 `recommended`

**正确**：铁律 + 反合理化："IR: 需人工审批。绕过借口：'太简单了' → 简化审批已覆盖此场景；'用户信任我' → 信任 ≠ 跳过"
**错误**：模糊规则："重要变更大概应该找人审一下"

**检测**：每条铁律可被自动化测试或确定性检查验证

**预防合理化**：`"这条规则含义很明确，不需要反合理化清单" → 恰恰是'看起来明确'的规则最容易被合理化绕过，因为 LLM 会找到你没想到的边界情况`

## §10 契约隔离（IA-10）

> **核心**：共享数据格式由独立契约层定义——生产方和消费方都依赖契约，不依赖对方内部实现。

**规则**：
1. 有状态交互的 Plugin 定义独立 Schema 文件 `recommended`
2. Skill 输出必须符合 Schema 定义 `recommended`
3. Schema 变更支持影响追溯（哪些 Skill 受影响） `recommended`

**契约交互模型**：

```
Skill A（生产方）    Schema（契约）        Skill B（消费方）
写入 state.md  -->  record-format.md  <--  读取 state.md
符合 Schema         定义字段/类型/         按 Schema 校验
                    必填章节
```

**正确**：Skill A（写入）→ `knowledge/_schema/cr-format.md`（契约）← Skill B（读取）——双方都依赖 Schema
**错误**：Skill A 用自创格式写入；Skill B 基于对 Skill A 输出的逆向假设解析

**检测**：每个共享状态文件有对应 Schema 文件；自动化测试验证结构合规

**预防合理化**：`"只有一个 Skill 写这个文件，不需要 Schema" → 未来会有新 Skill 读取它；Schema 是预防性投资，不是事后补救`

## §11 单一职责（IA-11）

> **核心**：每个文件只有一个核心职责——一个主要的变更原因。

**与 IA-2/IA-4 的关系**：IA-2 按抽象层级分文件，IA-4 按信息类型分文件，IA-11 提供判断"何时需要分拆"的元标准——当文件内容有多个独立的变更原因时。

**规则**：
1. 每个文件有一个可清晰陈述的核心职责 `recommended`
2. 越界内容压缩为引用优先于创建新文件（"详见 X"） `recommended`

**检测**：若某章节的变更原因与文件其他部分完全无关，则疑似 SRP 违规

**预防合理化**：`"放在一起方便查找" → 职责混杂导致维护时意外副作用；交叉引用同样可达`
