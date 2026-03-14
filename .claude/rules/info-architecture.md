# Claude Code 组件信息架构规则

> **职责**：Claude Code Plugin 的信息组织原则——内容怎么放、怎么拆、怎么引用、怎么加载。与 `plugin-dev-spec.md`（平台组件规格）互补。

Plugin 不是程序，是通过组织化 Markdown 塑造 LLM 行为的**信息架构**。传统软件靠编译器确定性执行；Plugin 靠 LLM 概率性解释——信息组织失误直接导致行为偏差。

## §0 速查卡片

### 10 原则一览

| # | 原则 | 一句话 | 对应层级 |
|---|------|--------|---------|
| P1 | 单向依赖 | 信息从抽象流向具体，不可反向 | 全局（层间关系） |
| P2 | 抽象分层 | 不同抽象层级放在不同文件 | Layer 6-1 |
| P3 | 稳定-易变分离 | 高频变更内容不耦合低频内容 | 全局（变更频率） |
| P4 | 信息分类 | 不同信息类型不混放 | 全局（类型维度） |
| P5 | 按需加载 | 只加载当前上下文所需的最小信息集 | Layer 3-1 |
| P6 | 单一权威 | 每条信息有且仅有一个权威定义点 | 全局（同步维度） |
| P7 | 确定性分级 | 约束的执行保障级别匹配其关键程度 | Layer 5 + Hooks |
| P8 | 可发现性优先 | 入口信息为发现而设计，不为完整而设计 | Layer 3（description） |
| P9 | 认知清晰 | 面向 LLM 的指令精确无歧义，阻止合理化绕过 | 全局（精确性） |
| P10 | 契约隔离 | 数据格式由独立契约层约束 | Layer 4 |

### 六层架构

```
Layer 6: knowledge/theory     (Why  — 概念知识，被动加载，极少变更)
Layer 5: rules/               (Must — 行为约束，会话启动时自动加载)
Layer 4: knowledge/_schema/   (Shape — 数据格式契约，按需加载)
Layer 3: skills/*/SKILL.md    (What — 路由层，description 触发加载)
Layer 2: skills/*/*-procedures.md (How — 操作步骤，按状态/子命令条件加载)
Layer 1: knowledge/_templates/ (Instance — 具体实例，实例化时加载)
```

依赖方向：**仅允许下层引用上层**。Layer 2 引用 Layer 4 的格式定义；Layer 4 不引用 Layer 2 的实现细节。

### 信息类型 &rarr; 资产映射

| 信息类型 | Plugin 资产 | 特征 |
|---------|------------|------|
| 步骤（Procedure） | `*-procedures.md` | 按步操作指令 |
| 约束（Principle） | `rules/*.md` | 行为规范 |
| 概念（Concept） | `knowledge/*.md` | 背景知识 |
| 结构（Structure） | `knowledge/_schema/*.md` | 数据格式定义 |
| 路由（Process） | `SKILL.md` | 工作流分发 |
| 实例（Fact） | `knowledge/_templates/*.md` | 具体模板 |

## §1 单向依赖（P1）

> **核心**：信息从抽象流向具体——上层定义，下层实现，不可反向引用。

**规则**：
1. 分发层（`rules/`、`skills/`、`knowledge/`）不得引用开发层（`docs/`、`.claude/`） `iron rule`
2. 六层架构中，下层文件只引用同层或上层文件 `required`
3. 合法的"反向注释"仅限两种：上层的**映射说明**（解释如何对应到下层）和**权威委托**（显式标记"详见 XXX"） `recommended`

**正确**：`rules/devpace-rules.md` 引用 `knowledge/theory.md`（同层/上层引用）
**错误**：`skills/pace-dev/SKILL.md` 引用 `docs/design/design.md`（分发层 &rarr; 开发层）

**检测**：`grep -r "docs/\|\.claude/" rules/ skills/ knowledge/` 应返回空

**预防合理化**：`"只是引用一下设计文档的章节编号" → 分发层必须独立可分发，任何开发层引用都破坏这一点`

## §2 抽象分层（P2）

> **核心**：不同抽象层级的内容放在不同文件——路由与步骤分离，Manifest 与组件分离。

**规则**：
1. `.claude-plugin/` 仅放 `plugin.json` + `marketplace.json`；所有组件在 Plugin 根目录（详细结构见 `plugin-dev-spec.md` "Plugin 结构"） `iron rule`
2. SKILL.md 放路由逻辑（"做什么"）；详细步骤超 ~50 行时拆出 `*-procedures.md`（"怎么做"）（详细规格见 `plugin-dev-spec.md` "分拆模式"） `recommended`
3. 每个文件包含单一主抽象层级 `recommended`

**正确**：SKILL.md 含 100 行路由表 + 输入/输出定义；procedures 文件含分步指令
**错误**：SKILL.md 内嵌 500 行详细指令与路由逻辑混杂

**检测**：SKILL.md 超过 ~500 行 &rarr; 疑似层级混杂，检查是否需要分拆

**预防合理化**：`"内容不多，放一起方便" → 超过 50 行详细规则就该拆；合并不是方便，是让 LLM 混淆路由与执行`

## §3 稳定-易变分离（P3）

> **核心**：被广泛依赖的文件应保持高稳定性；高频变更内容应隔离到独立文件。

**规则**：
1. 被多个 Skill 引用的文件（schema、theory）维持低变更频率 `recommended`
2. 始终加载的文件（rules）控制体量；膨胀时将稳定核心与易变索引分拆 `recommended`
3. 加载策略与稳定性对齐：最稳定的被动加载（按引用）；最易变的条件路由加载 `recommended`

**正确**：theory 文件极少变更，被多个 Skill 引用；procedures 文件频繁迭代但仅按状态加载
**错误**：在被广泛引用的 rules 文件中直接嵌入频繁更新的检查清单

**检测**：`git log --oneline <file> | wc -l` — 被多处引用的文件若变更频率高于其依赖者，考虑分拆

## §4 信息分类（P4）

> **核心**：不同类型的信息不混放——步骤、约束、概念、结构、路由、实例各归其位。

**规则**：
1. 一个文件包含一种主信息类型 `recommended`
2. 任务内容（执行指令）与参考内容（背景知识）分开存放 `recommended`
3. 背景知识放 `knowledge/`，约束放 `rules/`，执行步骤放 `*-procedures.md` `recommended`

**正确**：背景解释在 `knowledge/theory.md`，执行步骤在 `skills/pace-dev/dev-procedures.md`
**错误**：SKILL.md 前 200 行是理论解释，后 50 行是执行步骤——LLM 无法区分"背景上下文"与"执行指令"

**检测**：审查文件内容，若同一文件包含大段理论 + 分步指令 + 格式定义，则违反 P4

**预防合理化**：`"放在一起让 LLM 理解上下文" → LLM 会将背景知识误当执行指令，导致行为漂移`

## §5 按需加载（P5）

> **核心**：只加载当前上下文所需的最小信息集——上下文窗口是硬约束，浪费即降质。

**规则**：
1. `description` 仅提供触发信息；完整内容在激活后才加载 `iron rule`
2. 复杂 Skill 使用两级延迟加载：SKILL.md（路由）&rarr; procedures（操作） `recommended`
3. `knowledge/` 文件被动加载（按引用），不主动注入上下文 `recommended`
4. 上下文预算：description < 300 字符，SKILL.md < 500 行，单次执行加载 < 800 行 `recommended`

**加载策略参考**：

| 内容类型 | 加载策略 | 触发条件 |
|---------|---------|---------|
| Rules | 始终加载（会话启动） | 自动 |
| SKILL.md | 触发时加载 | description 匹配 |
| Procedures | 按状态/子命令加载 | SKILL.md 路由表 |
| Knowledge | 按引用加载 | procedures 中的 "读取 knowledge/X" 指令 |
| Schema | 产出/校验时加载 | Skill 需写入/读取状态文件 |
| Templates | 实例化时加载 | Skill 创建新状态文件 |

**正确**：SKILL.md 加载 80 行路由表，根据当前状态加载一个 200 行 procedures 文件
**错误**：SKILL.md 一次性加载全部 6 个 procedures 文件（1200+ 行），不论当前状态

**检测**：衡量每次 Skill 调用消耗的上下文 token；单次加载超 800 行需警示

**预防合理化**：`"提前加载省得来回切换" → 多加载的内容不只浪费 token，还会污染推理（步骤泄漏）`

## §6 单一权威（P6）

> **核心**：每条信息有且仅有一个权威定义点——DRY 从"消除重复"变为"管理重复"。

**规则**：
1. 每个信息项有一个权威文件；派生文件注明来源 `recommended`
2. 多处出现的内容使用"源 &rarr; 派生"树模型管理 `recommended`
3. 变更沿 源 &rarr; 派生 方向传播；派生文件不得单方面修改权威内容 `recommended`

**合法反 DRY 场景**：
- §0 速查摘要——为快速索引的刻意冗余（P5 按需加载优先于 P6）
- 权威委托标记——上层用"（权威源）"后缀委托下层详细定义

**正确**：SKILL.md 定义子命令（源）&rarr; rules.md §0 索引子命令（派生，注明"详见 SKILL.md"）
**错误**：SKILL.md 和 rules.md 各自独立定义子命令行为，无权威声明

**检测**：对每个多处出现的内容，确认有一个文件被显式标记为权威；grep 确认派生文件引用它

## §7 确定性分级（P7）

> **核心**：约束的执行保障级别必须匹配其关键程度——安全关键规则不能只靠文本。

**四级保障**：

| 可靠性 | 机制 | 适用场景 |
|--------|------|---------|
| 最高 | Hook command + exit 2 | 不可逆操作阻断、模式保护 |
| 高 | Hook prompt/agent | 需语义理解的检查 |
| 中 | Skill 指令 + 铁律标记 | 工作流约束 |
| 基线 | Rules 文本建议 | 行为规范、风格指引 |

**规则**：
1. 安全关键约束使用 Hook 确定性执行（exit 2） `iron rule`
2. 不可逆操作（如人工审批门禁）匹配最高保障级别 `iron rule`
3. 高级安全规则采用"三重保险"：Hook 阻断 + Rules 声明 + 铁律标记 `recommended`

**正确**：人工审批门禁 &rarr; Hook exit 2 阻断自动状态变更 + Rules 声明规则 + 铁律标记在 §0
**错误**：人工审批门禁 &rarr; 仅 rules 文件中写"请等待用户审批"

**检测**：每条铁律都有对应的 Hook 或自动化测试执行保障

**预防合理化**：`"文本规则够了，Claude 会遵守" → LLM 在复杂推理链中会构造绕过理由；文本是意图文档，不是唯一执行保障`

## §8 可发现性优先（P8）

> **核心**：入口信息为发现（When）而设计，不为完整（What）而设计。

**规则**：
1. SKILL.md `description` 仅写触发条件（When），不写行为描述（What）（详细编写规则见 `plugin-dev-spec.md` "description 编写规则 CSO"） `iron rule`
2. `description` 使用具体触发关键词（"Use when user says '开始做/实现/修复'"） `recommended`
3. 每个 rules/ 和 _schema/ 文件提供 §0 速查卡片 `recommended`

**正确**：`description: Use when user requests development work or says "implement/fix/build"`
**错误**：`description: Analyzes code quality, runs gate checks, generates diff summary, updates status`

**检测**：审查所有 `description` 字段——不应包含描述内部动作的动词

**预防合理化**：`"写清楚做什么帮助用户理解" → description 的消费者是 Claude 的路由逻辑，不是用户；写了 What 会导致 Claude 跳过读完整 SKILL.md 直接按摘要行动`

## §9 认知清晰（P9）

> **核心**：面向 LLM 的指令精确无歧义——阻止合理化绕过。

**规则**：
1. 仅使用官方文档记录的 frontmatter 字段——不猜测、不发明 `iron rule`
2. Hook 事件名严格区分大小写（`PreToolUse` 而非 `pretooluse`） `iron rule`
3. 零摩擦入门——自然语言开箱即用，无需强制配置 `iron rule`
4. 所有路径相对引用，以 `./` 开头 `iron rule`
5. 铁律配反合理化清单——列举可能的绕过借口及反驳 `recommended`

**正确**：铁律 + 反合理化："IR: 需人工审批。绕过借口：'太简单了' &rarr; 简化审批已覆盖此场景；'用户信任我' &rarr; 信任 &ne; 跳过"
**错误**：模糊规则："重要变更大概应该找人审一下"

**检测**：每条铁律可被自动化测试或确定性检查验证

**预防合理化**：`"这条规则含义很明确，不需要反合理化清单" → 恰恰是'看起来明确'的规则最容易被合理化绕过，因为 LLM 会找到你没想到的边界情况`

## §10 契约隔离（P10）

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

**正确**：Skill A（写入）&rarr; `knowledge/_schema/cr-format.md`（契约）&larr; Skill B（读取）——双方都依赖 Schema
**错误**：Skill A 用自创格式写入；Skill B 基于对 Skill A 输出的逆向假设解析

**检测**：每个共享状态文件有对应 Schema 文件；自动化测试验证结构合规

**预防合理化**：`"只有一个 Skill 写这个文件，不需要 Schema" → 未来会有新 Skill 读取它；Schema 是预防性投资，不是事后补救`
