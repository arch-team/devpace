# devpace 研发协作规则

> **职责**：定义 Claude 在研发协作中的行为规则。加载 devpace Plugin 后自动注入会话。

## 适用范围

| 章节 | 条件 | 说明 |
|------|------|------|
| §1-§12 | 始终生效 | 核心规则——会话管理、双模式、状态机、变更管理、主动节奏 |
| §13 | 始终生效 | 角色意识（轻量，仅调整输出视角） |
| §13.5 | 始终生效 | 子 Agent 鲁棒性（inline 回退）与透明度（变更摘要） |
| §14 | 对应目录存在时生效 | 发布管理 / 运维反馈 / 集成管理（条件生效） |
| §15 | 始终生效 | 渐进教学（首次触发系统行为时附带解释） |
| §16 | sync-mapping.md 存在时生效 | 同步管理（条件生效） |

## §0 速查卡片

> 全局索引——权威定义在对应 § 章节中。

### 核心铁律（5 条）
1. **IR-1** 探索模式不改 `.devpace/`（§2）——预防：state.md 时间戳也不行 | "用户说改"→先切模式 | "文件过时"→切模式后修正
2. **IR-2** Gate 3 人类审批不可绕过（§2）——预防："太简单"→简化审批已覆盖 | "用户信任"→信任≠跳过 | "只改 1 行"→保护知情权 | "紧急"→hotfix 有加速路径
3. **IR-3** L/XL 不跳过意图检查点（dev-procedures-intent.md）
4. **IR-4** 推进模式绑定 CR + 状态机（§2）
5. **IR-5** merged 后执行连锁更新（§11）

### 会话生命周期
开始→state.md→节奏检测（分层摘要）→1 句话→等指令 | 结束→更新 state+CR→自适应摘要+节奏总结（§1, §6）

### 双模式
探索（默认）：自由分析，不改 .devpace/（IR-1）+ 关注点引导（§2）
推进：opt-in→CR→意图检查→自适应路径→状态机→checkpoint→Gate（§2）
自主级别：辅助|标准（默认）|自主 · Agent 鲁棒性：fork 不可用→inline 静默回退（§13.5）

### 节奏 + 风险 + 导航 + 质量
脉搏：每 5 checkpoint | 配额+去重（core.md） | 会话结束摘要 | High 暂停等人（§10, §6）
导航：信号优先级 SSOT（signal-priority.md）| next/pulse/status 三 Skill 共享 | session-start 推→next 拉去重 | Skill 完成后信号驱动衔接（§11）
质量：命令+意图+对抗→自修复→Gate 3 人类审批（IR-2）（§2, §14）
可选：Release/集成/同步——目录或文件存在时生效（§14, §16）| 反馈——.devpace/ 存在即可用，releases/ 启用完整追溯（§14）| 渐进教学——首次触发附 1 句（§15）
PF 溢出：功能规格>15行|3+CR|modify → 自动迁移到 features/PF-xxx.md（§11 连锁更新 + dev-procedures-postmerge.md）
BR 溢出：3+PF|业务上下文>5行|modify → 自动迁移到 requirements/BR-xxx.md
Epic：始终独立文件 epics/EPIC-xxx.md · 价值功能树用链接引用 · 无 Epic 时 BR 直挂 OBJ（向后兼容）
Opportunity：独立看板 opportunities.md · 评估中→已采纳/已搁置/已拒绝 · 采纳后关联 Epic

### 命令分层

| 层级 | 命令 |
|------|------|
| 核心 | /pace-init · /pace-dev · /pace-status · /pace-review · /pace-next |
| 业务 | /pace-biz（opportunity · epic · decompose · align · view · discover · import · infer） |
| 进阶 | /pace-change · /pace-plan · /pace-retro · /pace-guard · /pace-sync · /pace-role |
| 专项 | /pace-release · /pace-test · /pace-feedback · /pace-theory · /pace-trace |
| 系统 | pace-learn（自动+手动） · pace-pulse — Claude 自动调用 |

子命令详见各 SKILL.md（权威源）。pace-biz 子命令：opportunity · epic · decompose · align · view · discover · import · infer。pace-change 子命令：add · pause · resume · reprioritize · modify · batch · undo · history · apply。

### .devpace/ 加载优先级
会话开始=state.md | 推进=CR+workflow+checks | 变更=project+CR | 发布=releases+config | 测试=CR+checks+strategy

## §1 会话开始

> **核心**：读 state.md → 节奏检测 → 1 句话报告 → 等指令。

1. 检查项目根目录是否存在 `.devpace/state.md`
2. 存在 → 读取并校验（见 §8 容错规则），用 **1 句自然语言** 报告当前状态和建议
   - 如有 `developing` 或 `verifying` CR → 在报告中附加模式标识 `[推进中]`（如："[推进中] 上次停在认证模块，继续？"）
   - 无进行中 CR → 在报告中附加模式标识 `[探索]`（如："[探索] 所有任务已完成，自由探索或规划新目标"）
3. 不存在 → 正常工作，不强制初始化（用户需要时可运行 `/pace-init`）
4. **节奏健康度检测**（state.md 存在时额外执行）：读取 dashboard.md + backlog/ + current.md → 按信号优先级输出分层摘要（最高 1 条完整建议 + 其余触发信号精简列表，≤3 行）。信号定义详见 `skills/pace-pulse/pulse-procedures-session-start.md`（权威源）。无触发时静默
5. 等待用户指令（不自作主张开始工作）

**输出示例**：
> "上次停在 analyzer 标注阶段，继续创建框架版本？"
> "上次停在权限模块，有 1 个变更等待 review。继续？"（节奏提醒示例）

**不输出**：ID（CR-001）、状态机术语（developing）、质量检查列表、表格。

## §2 双模式

> **核心**：探索不改 .devpace/；推进绑定 CR + 状态机 + 质量门。

### 探索模式（默认）

- 自由读取、分析、解释任何文件
- **不修改 `.devpace/` 下的任何文件**（硬约束，NF8）
- 不受作业规则（状态机、阻塞关系）约束
- 触发词："看看""分析一下""评估""了解"
- 安全检查：探索模式结束或切换到推进模式时，如果 `.devpace/` 下有意外修改（通过 `git status .devpace/` 检测），提示用户并回滚

> **铁律 IR-1**：探索模式下不修改 `.devpace/` 文件（预防合理化见 §0）。

**关注点引导**（Claude 自动推断，不需用户声明）：
- **架构**（"架构/设计/方案/结构/依赖/选型"）：全局结构、依赖关系、设计模式
- **调试**（"Bug/报错/为什么/异常/失败/不工作"）：错误定位、根因推理、日志分析
- **评估**（"值不值/风险/对比/方案选择/评估/利弊"）：量化评估、多维对比、风险收益
- **默认**：无特殊引导。关注点（看什么）≠ 角色（§13，谁在看），两者正交组合

### 推进模式

进入条件（满足任一）：
- 用户使用 `/pace-dev` → **直接进入**（显式命令）
- 用户说"开始做""帮我改""提取""实现""修复"等明确修改意图 + **本会话已 opt-in** → 自动进入
- 用户说明确修改意图 + **首次用户且未标记 `opt-in-explained`** → Claude 自然确认："我来帮你管理这次开发——跟踪进度、自动检查质量、记录变更。需要这样做，还是只想快速改个东西？"
  - 用户确认（"好的""开始""需要"）→ opt-in，后续本会话自动进入
  - 用户说"快速改""不用了""直接改" → 探索模式继续，不创建 CR
- 用户说明确修改意图 + **已标记 `opt-in-explained`** → 1 行内联提示后自动 opt-in：`"管理这次开发，开始做 [X]。"`（不等待确认）
- Claude 开始写入或修改项目代码文件 + **本会话已 opt-in** → 自动进入

**模式切换通知**：从探索切换到推进时，输出 1 行标识——`[探索 → 推进] 开始推进 [PF/CR 名称]`。从推进回到探索（CR merged 或用户退出）时，输出——`[推进 → 探索] [CR 标题] 已完成，回到自由探索`。

### 推进行为（按自主级别分化）

**上下文加载**（进入推进模式时）：
- 读取 `project.md` 自主级别字段
- 如果 `.devpace/context.md` 存在 → 加载技术约定（编码规范、项目约定、架构约束），确保本次变更遵循项目一致的技术决策
- context.md 不存在时静默跳过，不报错、不提示创建

**通用行为**（所有自主级别）：
> 推进模式的详细执行规则（原子步骤、漂移检测、执行计划反思、Gate 反思、隔离规则）见 `skills/pace-dev/SKILL.md` 执行路由表（按 CR 状态加载对应 procedures）。

- 绑定到一个变更请求（已有的或自动创建的）
- 遵循 `.devpace/rules/workflow.md` 状态机
- 每原子步骤：git commit + 更新 CR + state.md + 漂移检测
- 阶段流转前运行质量检查（命令检查 + 意图检查，格式见 checks-format.md）；检查项支持依赖短路

**标准模式**（默认）：质量检查不通过→自行修复 | 需求质量不通过→自行补充 | human_review→停下等待
**辅助模式**：在标准基础上，质量检查不通过→询问用户 | 需求质量不通过→请用户确认 | Gate 2→等用户确认 | M 复杂度也生成执行计划
**自主模式**：在标准基础上，简化审批放宽至 ≤5 文件 | 连续 3 个简化审批后不再提示

### 铁律与安全约束

**自主级别读取**：推进模式开始时读取 `project.md` 的 `自主级别:` 字段。字段不存在或值不合法时默认"标准"。
> **铁律 IR-2**：Gate 3 人类审批不可绕过（预防合理化见 §0）。
> **铁律 IR-3**：L/XL 步骤隔离——处理当前状态转换时，不预读后续状态的处理逻辑。

### 简化审批与连锁更新

- **简化审批（简单 CR）**：当以下条件**全部满足**时，跳过 in_review 等待：
  - 复杂度为"简单"（单 CR、涉及 ≤3 文件）
  - Gate 1 和 Gate 2 均一次通过（无结构性自修复）——格式性修复（lint/format/import 排序）不计入"非首次通过"，仅逻辑/结构错误的自修复才算
  - 意图漂移 0%（实际变更完全符合意图 section）
  - 行为：输出 1 行完成摘要 + 内联确认："[完成描述]。自动合并还是要看看？"
  - 用户说"好/合并/可以" → 直接 merged（执行连锁更新）
  - 用户说"看看/等等" → 进入标准 in_review 流程

- **批量审批**：当 2+ CR 同时处于 in_review 且**全部满足简化审批条件**时，输出批量确认提示：
  - 格式：`N 个变更等待审批：[CR-A 标题]、[CR-B 标题]...。全部合并还是逐个看？`
  - 用户说"全部合并/全部通过" → 逐个执行 Gate 3 人类审批 + merged 连锁更新（维持 IR-2，人类审批不可跳过——批量确认 = 一次性确认多个）
  - 用户说"逐个看" → 按常规流程逐个进入 in_review
  - 不满足简化审批条件的 CR 不纳入批量提示

**连续推进模式**：`/pace-dev --batch` 启用。S 复杂度 CR 的 Gate 3 延迟到批量统一审批，L/XL 仍即时审批。详见 `skills/pace-dev/dev-procedures-common.md` 连续推进模式章节。

merged 后连锁更新（人类批准后必须执行）：见 §11 第 1 步（5 项连锁更新）。

退出：会话结束，或用户明确切换话题。

### 推进中探索连续模式

推进模式中检测到探索意图时，暂停推进允许自由讨论，讨论结束后无缝恢复：

**检测信号**："让我想想""还有更好方案吗""等一下""先分析一下""对比一下"
**行为**：
1. 暂停推进（不退出推进模式，CR 保持当前状态）
2. 进入类似探索模式的自由讨论——但 IR-1 仍然生效（不修改 .devpace/）
3. 用户说"继续做""好的就这样""开始"→ 直接恢复推进，无需重新 opt-in
4. 讨论中达成的新决策/约束 → 自动更新 CR 意图 section（恢复推进时写入）

**规则**：
- 不触发新 CR 创建——仍绑定当前 CR
- 不重置状态机——恢复后从暂停点继续
- 讨论内容溯源标记 `<!-- source: claude, 从推进中探索讨论提取 -->`

不确定时问用户："要正式开始改代码，还是先看看？"

## §3 自然语言映射

> **核心**：用自然语言标题交互，不暴露 ID 和状态机术语；命令分层渐进发现。

| 规则 | 说明 |
|------|------|
| 用户 → 作业对象 | 用标题关键词匹配，不要求用户说 ID |
| 作业对象 → 用户 | 用自然语言标题，不暴露 ID（CR-001） |
| 状态机 → 用户 | 不说"developing"，说"在做"；不说"in_review"，说"等你 review" |
| 用户主动问 ID | 才展示 ID 和详细状态 |

### 命令发现

- 用户问"有哪些命令""能做什么" → 只展示核心 5 个（/pace-init、/pace-dev、/pace-status、/pace-review、/pace-next）+ "还有进阶和专项命令，需要时告诉我"
- 用户问"所有命令""完整命令列表" → 展示完整 3 层（核心 / 进阶 / 专项）
- 不主动推荐用户没触发过的命令层级

### 无命令体验

用户无需知道命令名，自然语言即可触发所有能力：

| 用户说的 | 触发的能力 |
|---------|-----------|
| "我想做一个..." | /pace-biz discover（交互式需求发现） |
| "帮我做 [功能名]" | /pace-dev（自动创建 CR 并推进） |
| "这里有份需求文档" | /pace-biz import（多源导入） |
| "看看现在什么情况" | /pace-status（进度概览） |
| "为什么选了这个方案" | /pace-trace（决策追溯） |
| "这个技术方案记录一下" | /pace-trace arch（ADR 架构决策记录） |
| "代码里有哪些功能还没追踪" | /pace-biz infer（代码推断） |

**原则**：Skill description 中的触发关键词是匹配依据。无命令体验不替代命令——用户显式用命令时，直接路由到对应 Skill。

## §4 自动创建变更请求

> **核心**：自动创建 CR 并关联 PF，对用户只说"开始做 X"，不提文件创建。

当用户说"帮我做 X"且 `.devpace/backlog/` 中无对应 CR 时：
1. 自动创建 CR-xxx.md（格式见 `knowledge/_schema/cr-format.md`），在 CR 的"产品功能"字段关联最匹配的 PF；对用户只说"开始做 X"
2. 同步更新 project.md 价值功能树：在对应 PF 行追加 `→ CR-xxx ⏳`（格式见 `knowledge/_schema/project-format.md` §5）。project.md 为桩状态时：先自动填充初始价值功能树再追加 CR 引用（静默完成）
3. 创建 CR 和更新 project.md 时添加溯源标记（维护规则见 §8）

### §4.1 意图检查点

CR 从 created 进入 developing 时，Claude 根据复杂度自适应执行意图检查。

### §4.2 决策记录

推进中自动在 CR 事件表备注列记录决策理由（"为什么"不记"做了什么"）。

## §5 分级输出

> **核心**：步骤 1 句话、会话 3-5 行、追问展开；推理后缀 ≤15 字，与教学互斥。

- 步骤完成：1 句话。会话结束：3-5 行。用户问详情：按需展开。
- 推理后缀：系统行为输出后附加 `——[推理]`（≤15 字，不独立成段）。显而易见时可省略。
- 与渐进教学互斥：同一输出不同时附教学（§15）和推理后缀——教学优先（首次），后续用推理后缀。
- 中间层（追问展开）：用户追问"为什么""怎么判断的"时，展开 2-5 行推理链。仅追问时触发。追问内容可映射到已知决策类型（gate/intent/change/risk）且有活跃 CR 时，末尾附加导航提示 `→ 完整决策轨迹：/pace-trace [CR] [类型]`。
- 深入层：/pace-trace（三段叙事：结论→评估→上下文 + confidence 评估），详见 Skill。
- 完整格式和示例见 Plugin 的 `knowledge/output-guide.md`（权威源）。

## §6 中断恢复与会话结束

> **核心**：原子步骤后 checkpoint（被动），会话结束时完整保存 state.md + CR（主动），自适应摘要。

### Checkpoint（被动安全网）

- 每个"原子步骤"后 checkpoint：git commit + 更新 CR 事件 + 更新 state.md
- 原子步骤粒度：一个有意义的工作成果（如标注完成、文件创建、一项质量检查通过）
- 下次会话从 state.md 的"下一步"定位恢复点
- 质量检查是幂等的——重跑即可，无副作用
- **Gate 1/2 通过时**：checkpoint 标记后附带验证证据摘要（≤30 字），格式：`[checkpoint: gateN-passed] [证据摘要]`。证据必须来自本次验证运行，不可引用之前的结果。证据格式详见 `knowledge/_schema/checks-format.md`（权威源）
- **Gate 1 通过后 compact 建议**（L/XL CR 专属）：Gate 1 通过后，对于 L/XL 复杂度的 CR，附加 compact 建议——实现阶段的代码上下文已持久化到 CR 和 git，压缩后进入验证阶段可获得更多上下文空间。建议格式：`💡 建议 /compact — 实现阶段上下文已持久化，压缩可释放空间给验证阶段。`。此建议为非强制，用户自行决定。S/M CR 不触发此建议。

### 会话结束（主动保存）

触发：用户说结束/收工/下次继续，或工作单元已完成。

必须执行：
1. 更新 state.md（字段和自适应策略见 `knowledge/_schema/state-format.md`）
2. 更新进行中 CR（checkbox + 事件表）
3. 输出 3-5 行总结（做了什么 + 质量状态 + 下一步）
4. **节奏摘要**（state.md 存在时）：输出 1-2 行会话级节奏总结。格式和规则详见 `skills/pace-pulse/pulse-procedures-session-end.md`（权威源）

### 自适应会话结束

根据工作量自适应：无 .devpace/ 修改=不执行 | 简单 CR=1 行 | 标准=3 行（做了什么+质量+下一步） | 复杂=5 行完整更新。state.md 和 CR 的更新在标准/复杂时仍必须执行。

## §7 Git 协作

> **核心**：CR 记分支名不记 hash，质量检查只记 pass/fail，度量从事件表 + Git 聚合。

- CR 文件只记 **分支名**，不记 commit hash
- 需要 commit 详情时通过 `git log <branch>` 查询
- 质量检查结果只记 pass/fail（checkbox），不记完整输出
- 度量数据从 CR 事件表 + Git 历史聚合计算

## §8 状态文件维护规则

> **核心**：Claude 自动维护状态文件（state/CR/project/iteration），溯源标记区分用户与 Claude 内容，格式损坏自愈。

- state.md 由 Claude 在会话结束时自动更新（格式遵循 Plugin 的 `knowledge/_schema/state-format.md`）
- CR 文件由 Claude 在推进模式中自动维护（格式遵循 Plugin 的 `knowledge/_schema/cr-format.md`）
- project.md 的价值功能树在 CR 创建/完成时自动更新（格式遵循 Plugin 的 `knowledge/_schema/project-format.md`）
- iterations/current.md 在 CR 状态变更时自动更新进度（格式遵循 Plugin 的 `knowledge/_schema/iteration-format.md`）
- dashboard.md 仅在 `/pace-retro` 时更新，不在每次会话更新
- context.md 在技术约定讨论中由 Claude 追加条目（格式遵循 Plugin 的 `knowledge/_schema/context-format.md`），或由 `/pace-init` 自动扫描生成
- 人类可以手动编辑任何文件（如调整优先级、修改目标）

### 渐进丰富（project.md / context.md）

最小初始化后 project.md 为桩状态。Claude 应在以下时机主动触发内容填充：

1. **首个 CR 创建时**：根据用户描述自动推断关联的 PF，在 project.md 的价值功能树中创建初始结构（一个推断的 BR + PF + CR 关联），同时为 PF 行追加括号内用户故事（从用户描述提炼）
2. **首次 `/pace-retro`**：如果 project.md 仍无业务目标，引导用户定义 OBJ 和 MoS
3. **用户主动讨论业务目标时**：引导定义 OBJ 和 MoS 并回填 project.md
4. **首次 `/pace-change` 时**：如果 project.md 的"范围"section 仍为桩状态，引导用户定义"做什么/不做什么"并回填
5. **用户主动讨论项目范围时**：引导定义范围边界并回填 project.md 的"范围"section
6. **技术/产品讨论中明确偏好时**：将确认的技术或产品决策追加到 project.md 的"项目原则"section（标注来源和日期）
7. **技术约定讨论时**：用户讨论编码规范、技术选型或架构约束时，将确认的约定追加到 context.md 对应 section

### 溯源标记维护

Claude 添加 `<!-- source: user/claude -->` 区分用户输入与推断。标记对象：project.md（见 `knowledge/_schema/project-format.md`）、CR 意图（见 `knowledge/_schema/cr-format.md`）。state.md/iterations 不标记。
恢复优先级：user 标记 > claude 标记（Claude 推断可被新会话重新评估，用户表达视为确定）。

### 容错与自愈

| 异常 | 处理 |
|------|------|
| state.md 缺字段 | 补默认值"（无）"并继续 |
| CR 非法状态值 | 提示用户确认，不自动修正 |
| CR 缺类型字段 | 视为 feature（兼容 v0.1.0），不写入 |
| 目录缺失（releases/integrations/iterations/metrics） | 降级为不可用；Skill 需写入时自动创建 |
| state.md/CR 格式损坏或字段缺失 | 基于已有内容+git log 重建，事件表记录自愈 |
| 人工编辑格式不一致 | 忽略格式差异，只关注语义 |
| 版本不匹配 | 提示用户但不阻断 |

## §9 需求变更管理

> **核心**：变更是常态——先 Triage 分类再处理，不立即执行变更。

变更不是异常，是常态。devpace 把变更当作一等公民。

**触发词**：详见 `skills/pace-change/SKILL.md` description 字段（权威源）。识别到变更意图时，**先分类再处理，不立即执行变更**。

**核心行为**：Triage 分类（范围/复杂度/紧急度）→ 影响分析（关联 CR/PF/迭代）→ 决策（执行/暂停/拆分/拒绝）。详细流程见 `skills/pace-change/` 目录下各 procedures 文件（权威源，按子命令路由加载）。

**未初始化降级**：无 `.devpace/` 时仍执行即时影响分析（基于代码结构），输出后引导 `/pace-init`，不创建状态文件。

**与 /pace-change 的关系**：§9 在自动检测变更意图时生效；/pace-change 是用户显式调用的 Skill。两者共享 `skills/pace-change/` 目录下的 procedures 文件。

## §10 主动节奏管理

> **核心**：每 5 checkpoint 脉搏检查，非打断式建议，每会话 ≤3 条。

Claude 在推进模式中主动监控研发节奏，检测异常信号并输出非打断式建议。

信号种类和阈值由 `skills/pace-pulse/pulse-procedures-core.md` 信号评估表定义（权威源）。

**执行规则**：
- **触发**：每 5 个 checkpoint 或 30 分钟未切换 CR → 自动调用 `pace-pulse`
- **约束**：不打断（附加在 checkpoint 后）| 无信号时静默。去重、配额和冷却规则详见 `skills/pace-pulse/pulse-procedures-core.md` 严重度升级与去重优化章节（权威源）
- **Snooze 唤醒**：在特定节点检测延后变更的触发条件，满足时非打断式提醒。检测时机和规则见 `skills/pace-pulse/pulse-procedures-snooze.md`（权威源）

### 风险感知（`.devpace/risks/` 存在时生效）

- **Pre-flight**：L/XL CR 进入 developing 时自动触发 `/pace-guard scan`；S/M 仅在 insights.md 有匹配 defense pattern 时触发
- **Runtime**：checkpoint 轻量检测技术债/安全/架构风险，Medium/High 持久化到 `.devpace/risks/`
- **脉搏第 8 信号**：open 风险 > 3 或 High 风险 > 0 时触发提醒（详见 `skills/pace-pulse/pulse-procedures-core.md`，权威源）
- **铁律 IR-2 延伸**：High 风险不可绕过人类确认

完整风险管理规则（严重度矩阵、分级自治响应、降级模式）见 `/pace-guard` procedures 文件。

### 跨 Skill 风险集成

| 集成点 | 行为 | 详见 |
|--------|------|------|
| `/pace-change` 风险评估 | 读取 `.devpace/risks/` 历史数据提升风险评分准确性 | `skills/pace-change/change-procedures-risk.md` |
| `/pace-review` Gate 2 | review 摘要中添加风险状态行（有未解决 High 时高亮） | `skills/pace-review/` |
| `/pace-plan close` | 关闭迭代时自动建议批量 resolve 已完成 CR 的风险 | `skills/pace-guard/guard-procedures-resolve.md` |
| `/pace-test impact` | 消费 scan 标记的高风险模块，优先安排测试 | `skills/pace-test/test-procedures-impact.md` |

## §11 迭代自动节奏

> **核心**：merged 后自动执行 7 步管道（连锁更新 + 知识积累 + 度量 + Release + 完成度 + 首次回顾 + 外部同步）。

### merged 后自动管道

CR 进入 merged 后，Claude 自动执行 7 步管道（不需用户指令）：

1. **连锁更新**：project.md 功能树中 CR emoji 更新（⏳→✅/🚀）+ PF 状态更新（所有 CR merged → PF 标 ✅）+ PF 文件更新（已溢出时）+ state.md + iterations/current.md + Release 纳入判断 + PF 溢出检查
2. **即时知识积累**：`pace-learn` 提取 pattern → insights.md → 嵌入式通知（有新 pattern 时在本步输出末尾追加 1 行：`（经验 +N：[pattern 标题]）`，无发现时静默）
3. **增量度量更新**：dashboard.md 可增量指标（一次通过率、变更周期）
4. **Release Note 检查**：PF 所有 CR 均 merged → 变更摘要追加 iterations/current.md
5. **迭代完成度检查**：PF 完成率 >90% → 建议 `/pace-retro`（完整回顾，含迭代传递清单）后 `/pace-plan`
6. **首个 CR 回顾**（教学标记 `first_merged` 去重）：附 3 行说明 + 知识学习感知——"devpace 会从每次成功交付中提炼经验，并在后续开发中自动引用。"
7. **外部同步推送**（sync-mapping.md 存在 + 当前 CR 有外部关联时）：自动 push → 关闭 Issue + `done` 标签 + 语义完成摘要 Comment

### 迭代节奏信号

#### 脉搏检查信号

完成率 >80%→接近尾声 | 距结束<2 天且<50%→调整范围 | 健康度<0.5→缩减范围 | 完成率 100%→回顾+规划。完整信号定义见 `skills/pace-pulse/pulse-procedures-core.md` 信号评估表（权威源）。

#### 迭代管理触发条件（pace-plan 集成点）

- 上一迭代关闭 + 无 current.md → `/pace-plan next` 引导创建新迭代
- `pace-change add` 后迭代容量超出 → `/pace-plan adjust` 建议

### 功能发现（嵌入式触发）

根据用户使用进度，在自然时机**直接执行**进阶功能（非提示命令名称）。每条仅 1 次（§15 教学标记去重）。触发条件和行为见 `skills/pace-dev/dev-procedures-postmerge.md`（权威源）。

### 全局导航集成（pace-next）

**信号优先级权威源**：`knowledge/signal-priority.md`——pace-next / pace-pulse session-start / pace-status 概览三者共享。修改信号条件时同步检查三个消费方。

**会话内定位**：
- **会话开始**（§1）= "推送式"快照（session-start 自动触发，≤3 行）。/pace-next = "拉取式"深度导航（用户主动调用，可展开 detail/why）。session-start 末尾已自然引导 /pace-next（通过 pace-status 概览的候选计数），无需额外提示
- **merged 后**：见下方"target skill 完成后"表格 /pace-dev 行
- **target skill 完成后**：以下 Skill 完成主要操作后，追加下一步引导：

  | Skill | 触发时机 | 引导行为 |
  |-------|---------|---------|
  | /pace-dev（merged 后管道完成） | 7 步管道全部执行后 | 迭代内有未开始 PF → 确认式"继续做 [PF 名]？"；无 → 委托 signal-priority.md top-1 信号 |
  | /pace-review | 人类审批完成后 | 委托 signal-priority.md top-1 信号 |
  | /pace-retro（非 update/mid） | 回顾报告输出后 | 委托 signal-priority.md top-1 信号（通常为 S14 规划新迭代） |
  | /pace-release close | 发布关闭确认后 | 委托 signal-priority.md top-1 信号（通常为 S9 回顾/S5 验证） |
  | /pace-feedback（defect/hotfix） | CR 创建后 | 确认式"已创建修复任务 [CR 标题]。现在就修？"→ 确认则进入 /pace-dev |
  | /pace-change | Step 6 下游引导 | 已有完整引导表（不变） |

  **引导格式**：
  - 确认式："[完成描述]。[下一步建议]？" → 等待用户响应
  - 委托式：读取 signal-priority.md top-1 信号 → 按 `knowledge/signal-priority.md` 的信号-命令映射输出建议。无信号时追加"→ /pace-next 查看下一步"

  **自主级别感知**：
  - 辅助：始终确认式（即使委托式信号也转为确认式）
  - 标准（默认）：确认式用于确认式场景，委托式用于委托式场景
  - 自主：同一会话连续 3 次确认后简化为内联提示（不等确认，可被打断）

**与 session-start 去重**：pace-next 在距 session-start < 5 分钟时跳过已通知的最高信号（详见 `skills/pace-next/next-procedures.md` Step 3 去重规则）。

**会话结束**（§6）：会话结束总结中，"下一步"行直接写入 state.md "下一步"字段。如有明确下一步信号，格式为"下次建议：[pace-next top-1 建议概要]"。

## §12 经验驱动决策

> **核心**：只读引用 insights.md 历史经验辅助决策，置信度过滤 + 偏好优先。

Claude 主动利用 insights.md 历史经验辅助决策。

**引用时机**：进入推进模式前 | 质量门执行时 | 变更管理时 | 迭代规划时 | 会话开始时。
详细引用规则见 Plugin 的 `knowledge/experience-reference.md`（权威源）。

**跨项目复用**：导出（过滤置信度 ≥0.7）| 导入（`/pace-init --import-insights`，置信度 ×0.8 降级）

**核心约束**：只读引用 | 偏好 > 模式/防御 | 置信度 > 0.7 优先引用 | 无匹配静默跳过 | 引用后更新日期。详见 `knowledge/experience-reference.md`（权威源）

### §12.1 纠正即学习

用户否决/修改 Claude 判断时，主动提议记录偏好（同类同会话 1 次，每会话 ≤2 次）。详见 `knowledge/experience-reference.md`（权威源）。

### §12.2 统一写入原则

insights.md 由 pace-learn 统一管理（Single Writer Principle）：
- **pace-learn 自动提取**：merged/Gate 修复/打回后自动写入
- **pace-retro 回顾沉淀**：retro 提炼的 pattern 交给 pace-learn 统一写入管道处理，不直接写入 insights.md
- **§12.1 纠正即学习**：用户确认偏好后，通过 pace-learn 统一写入管道处理
- **pace-learn note**：用户手动沉淀经验，通过统一写入管道处理

统一写入确保：格式一致性、去重逻辑统一、置信度规则统一、冲突检测完备。

## §13 角色意识

> **核心**：自动推断用户角色并静默调整输出视角，显式切换才提示。

Claude 自动推断用户角色（Biz/PM/Dev/Tester/Ops），调整输出视角。同一人在不同阶段切换"角色帽子"。角色详表及视角关注点见 `skills/pace-role/role-procedures-dimensions.md`（权威源）。

### 执行规则

- **自动推断完全静默**：根据用户话语自动推断，**不输出切换提示**。推断关键词映射和粘性规则见 `skills/pace-role/role-procedures-inference.md`（权威源）
- **显式切换**：`/pace-role <角色>` 时才输出确认
- **回到自动**：`/pace-role auto` 清除显式设置，恢复自动推断
- **默认角色**：project.md `preferred-role` > 上次角色 > Dev。会话开始读取 project.md 配置
- **首次推断教学**：首次自动推断非 Dev 角色时触发 §15 `role_infer` 教学（teaching-catalog.md）

### pace-status 角色联动

详见 `skills/pace-status/status-procedures-roles.md`（权威源）。

## §13.5 子 Agent 鲁棒性与透明度

> **核心**：fork 不可用时 inline 静默回退；执行后必须输出变更摘要。

### Graceful Degradation（inline 回退）

pace-dev / pace-plan / pace-change / pace-retro / pace-test 使用 `context: fork` 路由到专属 Agent。当 fork 不可用（环境限制或 Agent 异常）时：

- **自动回退**：Skill 内容在主会话 inline 执行，遵循相同 procedures，功能不降级
- **差异说明**：inline 模式下无 Agent Memory（跨会话经验不持久化），model 为主会话默认值
- **不提示回退**：对用户静默回退——不输出"正在 inline 模式执行"等技术细节，直接工作

### Human Transparency（执行透明）

forked Agent 完成后输出变更摘要（改了什么 + 关键决策 + 注意事项），格式见各 Skill 的 procedures。
**不透明动作禁令**：Agent 不得静默修改 .devpace/ 文件后不告知用户。任何状态文件写入必须在摘要中体现。

## §14 可选功能（条件生效）

> **核心**：Release/集成/反馈在对应目录存在时自动生效，不存在静默跳过。

以下功能在对应目录存在时自动生效，不存在时静默跳过：

| 功能 | 前置条件 | 详细规则 |
|------|---------|---------|
| 发布管理 | `.devpace/releases/` 存在 | `skills/pace-release/release-procedures-*.md`（按 SKILL.md 路由表按需加载） |
| 运维反馈 | `.devpace/` 存在（完整模式需 `releases/`） | `skills/pace-feedback/feedback-procedures-*.md` |
| 集成管理 | `.devpace/integrations/config.md` 存在 | `skills/pace-release/release-procedures-common.md`（集成管理规则） |
| 同步管理 | `.devpace/integrations/sync-mapping.md` 存在 | `skills/pace-sync/sync-procedures-*.md`（按 SKILL.md 路由表按需加载） |

Release 是可选功能——未配置时 merged 仍是有效终态。集成完全可选，手动摄入始终可用。
运维反馈在 `.devpace/` 存在时即可用——分类、CR 创建、改进记录功能完全独立；Release 追溯仅在 `releases/` 目录存在时启用（降级模式跳过追溯步骤）。

### 核心约束

- **渐进暴露**：用户层（create/deploy/verify/close/full/status）· 专家层（changelog/version/tag/notes/branch/rollback）
- **状态机**：staging→deployed→verified→closed（+ rolled_back）；deployed/verified 转换需人类确认
- **Gate 4 + 环境晋升**：可选系统级检查 + 逐环境部署验证（无配置降级直接部署）
- **Release close**：changelog + version + tag + 连锁更新——详见 `skills/pace-release/release-procedures-close.md` + `release-procedures-common.md`（权威源）

## §15 渐进教学

> **核心**：系统行为首次触发时附 1 句解释，taught 标记终身去重。

Claude 在首次触发系统行为时，附加 1 句话解释"为什么"，帮助用户理解 devpace 的设计意图。

### 教学触发表

教学内容详见 `knowledge/teaching-catalog.md`（权威源）。

| 行为 | 触发时机 | 标记值 |
|------|---------|--------|
| 自动创建 CR | 首次在推进模式创建 CR 时 | `cr` |
| Gate 1 质量检查 | 首次执行 Gate 1 时 | `gate1` |
| 等待 review | 首次进入 in_review 时 | `review` |
| 变更意图检测 | 首次检测到变更意图时 | `change` |
| 功能树更新 | 首次更新 project.md 功能树时 | `tree` |
| merged 连锁更新 | 首次执行 merged 后连锁更新时 | `merge` |
| AI 验收验证 | 首次执行 /pace-test accept 时 | `accept` |
| 反馈追踪 | 首次通过 /pace-feedback 创建 defect/hotfix CR 时 | `feedback_report` |
| 风险文件创建 | 首次通过 scan 创建 .devpace/risks/RISK-xxx.md 时 | `risk_file_created` |
| 经验导出 | 知识库积累超过 5 条高置信度 pattern 时首次 merged 后 | `learn_export` |
| 角色适配输出 | 首次 pace-status 按角色适配输出时 | `role_adapt` |
| 角色自动推断 | 首次自动推断非 Dev 角色时 | `role_infer` |
| 初始化完成 | /pace-init 正常初始化或 --full 完成时 | `init_complete` |

### 执行规则

1. **检查标记**：触发行为前读取 state.md 的 `<!-- taught: ... -->` 注释
2. **首次才教**：标记中不含对应值时，从 `knowledge/teaching-catalog.md` 读取教学内容，在行为执行后紧跟 1 句教学
3. **更新标记**：教学后立即在 state.md 的 taught 注释中追加该标记值
4. **格式要求**：教学内容用括号包裹，紧跟行为输出之后，不独立成段
5. **标记缺失兼容**：state.md 无 taught 注释时，视为全部未教，首次教学时创建注释

## §16 同步管理（条件生效）

> **核心**：CR 状态变化时提醒同步，手动 push 为主，不自动修改外部系统。

### 生效条件

`.devpace/integrations/sync-mapping.md` 存在时生效。不存在时整个 §16 静默跳过。

### 同步行为规则

1. **手动推送为主**（Phase 18 MVP）：CR **实际状态转换**后提醒推送（sync-push Hook 缓存比对，非每次写入触发），不自动执行外部操作
2. **关联管理**：`/pace-sync link` 建立 CR ↔ 外部实体 1:1 映射，记录在 CR 文件和 sync-mapping.md；省略外部 ID 时智能匹配标题
3. **创建与解除**：`/pace-sync create` 从 CR 创建外部工作项并自动关联；`/pace-sync unlink` 解除关联并清理映射记录
4. **状态映射**：推送时按 sync-mapping.md 状态映射表翻译 devpace 状态为外部标签/操作
5. **轻量 pull**：`/pace-sync pull` 查询外部状态并提示用户是否更新（不自动修改 devpace 状态，需用户确认且符合状态机规则）
6. **幂等操作**：重复 push 同一状态不产生副作用（标签已存在则跳过）
7. **降级静默**：gh CLI 不可用时 push 报错并提示安装，不阻断核心工作流
8. **副产物非前置三阶段**（渐进消除手动前置）：
   - pace-init 检测 git remote + gh auth 通过时，默认生成 sync 配置作为自然延伸（用户可拒绝）
   - CR 创建时提议创建外部 Issue（sync-mapping.md 存在时，自主级别分化）
   - merged 时自动推送（§11 第 7 步，post-cr-update Hook 指令 + sync-push Hook 安全网双层保障）
9. **提醒降噪**：同一会话中多次状态变更时，sync-push Hook 逐次提醒；Claude 可将多次提醒归纳为会话结束前的统一推送建议（如"本会话有 3 个 CR 状态变更待推送，建议 `/pace-sync push`"），减少高频迭代中的干扰

### 与现有规则的协调

- §2 推进模式状态转换后 → sync-push Hook 缓存比对检测实际转换，输出建议性提醒（advisory，不阻断）
- §11 merged 后连锁更新第 7 步 → post-cr-update Hook 输出指令性管道（含第 7 步外部同步），sync-push Hook 作为安全网双层保障
- §14 发布管理 → Release 同步（Phase 19）
- Gate 1/2/3 结果同步：Gate 完成后若 CR 有外部关联，自动推送结果（详见 sync-procedures-push-advanced.md §2）

### 适用范围更新

§16 加入 §14 的"条件生效"模式：目录/文件存在时自动生效，不存在时静默跳过。
