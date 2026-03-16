# 变更请求文件格式契约

> **职责**：定义 CR-xxx.md 文件的结构。Claude 自动创建 CR 时遵循此格式。

## §0 速查卡片

```
文件名：CR-xxx.md（xxx 为自增数字，三位补零）
标题：自然语言描述（不含 ID）
必含：元信息 + 意图（Claude 渐进填充）+ 验证证据（可选，/pace-test accept 产出）+ 质量检查 checkbox + 事件表（结构化事件类型枚举 + 分钟级时间戳）+ 执行快照（L/XL 可选）+ 外部关联（可选，/pace-sync link 产出）
意图：用户原话 → 范围 → 验收条件（复杂度自适应格式） → 方案 → 约束（复杂度越高填充越完整） → 执行计划（L/XL 必须）
验收条件格式：简单=自由文本 · 标准=编号清单 · 复杂=Given/When/Then
歧义标记：[待确认: ...] 标记未确认的假设，Gate 2 前必须解决
质量检查从项目 .devpace/rules/checks.md 复制
可选 section：根因分析（defect）| 影响分析（/pace-test impact）| 验证证据（/pace-test accept）| 风险预评估（/pace-guard scan）| 运行时风险（checkpoint 自动写入）
类型：feature（默认）| defect | hotfix
状态值：created → developing → verifying → in_review → approved → merged → released（可选）（+ paused）
复杂度：S|M|L|XL（可选，意图检查点自动评估）
关联：阻塞(硬依赖) · 前置(时序) · 关联(信息) — 向后兼容旧阻塞字段
```

## 文件结构

```markdown
# [自然语言标题]

- **ID**：CR-xxx
- **类型**：[feature | defect | hotfix]（默认 feature，可省略）
- **严重度**：[critical | major | minor | trivial]（仅 defect/hotfix 填写）
- **产品功能**：[PF 标题]（[PF-ID]）→ [BR 标题]（[BR-ID]）→ [Epic 标题]（[EPIC-ID]）
- **应用**：[应用名称]
- **分支**：[feature/branch-name]
- **状态**：[created | developing | verifying | in_review | approved | merged | released]
- **关联 Release**：[REL-xxx]（可选——纳入 Release 后填写）
- **外部关联**：[github:#42](https://github.com/owner/repo/issues/42)（可选——/pace-sync link 后填写）
- **复杂度**：[S | M | L | XL]（可选——created→developing 时自动评估）
- **关联**：（可选——存在依赖或关系时填写）
  - 阻塞：[CR-ID]（[原因]）
  - 前置：[CR-ID]（[原因]）
  - 关联：[CR-ID]（[说明]）

## 意图

<!-- Claude 自动捕获和渐进丰富，用户不需要手动填写 -->

- **用户原话**：[用户的原始请求]
- **范围**：[做什么 / 不做什么]
- **验收条件**：[怎样算完成]
- **方案**：[采取什么方案，为什么]（详见下方"方案字段"章节）
- **约束**：[边界条件、假设、限制]

### 方案字段（L/XL CR 必填，S/M 可选）

L/XL CR 填充以下字段：
- **选定方案**：[方案名 + 1 行描述]
- **备选方案**：[方案 B 名 + 为何未选]
- **决策理由**：[1-2 行选定理由]
- **关联 ADR**：[ADR-NNN]（如有）

S/M CR 可直接填写 1 行实现思路。

约束：
- L/XL 进入 developing 前必须填充
- S/M 无方案字段不报错（向后兼容）

### 验收条件格式（复杂度自适应）

验收条件格式根据 CR 复杂度自动选择，降低简单 CR 的负担，提升复杂 CR 的精度：

| 复杂度 | 格式 | 示例 |
|--------|------|------|
| 简单（S） | 自由文本 | "修复 typo 并确认显示正确" |
| 标准（M） | 编号清单 | `1. 支持邮箱登录` `2. 密码强度校验` |
| 复杂（L/XL） | Given/When/Then | `Given 用户已注册, When 输入正确凭据, Then 登录成功` |

规则：
- 简单 CR 不加格式负担，自由文本即可
- 标准/复杂由 Claude 在意图检查点自动生成对应格式
- Gate 2 按条目逐一比对验收条件与实际变更

### 执行计划（可选）

复杂度 L/XL 的 CR 在意图检查点时自动生成执行计划，作为意图 section 的可选扩展。S/M 不生成。

```markdown
### 执行计划

1. **[文件路径]**：[做什么]
   - 预期：[可验证的结果描述]
   - 命令：`[验证命令]`（可选）
2. **[文件路径]**：[做什么]
   - 预期：[可验证的结果描述]
...
```

约束：
- **复杂度自适应**：S 不生成 | M 可选 | L/XL 必须生成
- 每步是一个原子动作，包含精确文件路径和可验证的预期结果
- "预期"字段为 Gate 2 验证提供可比对基准

### 歧义标记

当 Claude 在意图检查点发现歧义（需求不明确、多种解读、缺失前提）时，使用歧义标记：

```
[待确认: 具体疑问？建议 X，因为 Y]
```

规则：
- Claude 在意图检查点发现歧义时自动添加到 CR 意图 section
- 每个标记必须附带推荐值和理由（"建议 X，因为 Y"）
- Gate 2 前所有 `[待确认]` 标记必须已解决（已删除或替换为确认后的内容）
- Gate 2 检查时若发现未解决的歧义标记，自动失败并提示解决

### 溯源标记（意图 section）

CR 意图 section 使用溯源标记区分用户输入与 Claude 推断。溯源标记语法详见 `project-format.md` "溯源标记"章节。

**CR 意图中需标记的字段**：
- **用户原话**：始终 `<!-- source: user -->`
- **范围/验收条件/方案/约束**：Claude 补充时 `<!-- source: claude, [原因] -->`
- **歧义标记**：`[待确认]` 隐含 Claude 来源，无需额外标记
- **用户确认后不更新标记**——保留原始来源记录供审计

## 根因分析

<!-- 仅 type:defect 时使用。Claude 在创建 defect CR 时自动添加此 section -->

- **现象**：[用户报告或系统观察到的问题]
- **根因**：[问题的根本原因]
- **引入点**：[缺陷引入的 CR 或变更]（可选——可追溯时填写）
- **预防措施**：[防止类似问题的建议]（可选——修复后填写）

## 影响分析

<!-- 可选 section——由 /pace-test impact 产出自动写入。不使用 /pace-test impact 时此 section 不存在 -->

**变更范围**：N 文件 / M 模块
**风险等级**：[🟢 低 / 🟡 中 / 🔴 高]
**分析时间**：[日期]

| PF | 功能名 | 影响类型 | 建议测试 |
|----|--------|---------|---------|
| [PF-ID] | [功能名] | [直接变更 / 间接影响] | [测试列表] |

**测试建议**：
1. 必跑：[列表]
2. 建议跑：[列表]

**--run 结果**：[如已执行，附加执行结果摘要]

<!-- 多次执行 /pace-test impact 时覆盖更新此 section -->

## 验证证据

<!-- 可选 section——由 /pace-test accept 产出自动写入。不使用 /pace-test 时此 section 不存在 -->

验收验证报告（最近一次 /pace-test accept 结果）：

| # | 验收断言 | 状态 | 验证级别 | 证据 |
|---|---------|------|---------|------|
| A1 | [断言内容] | [✅ 通过 / ❌ 未通过 / ⚠️ 需人工] | [L1 动态 / L2 静态 / L3] | [证据摘要] |

通过率：N/M · 验证时间：[日期]

## 质量检查

<!-- 从项目 .devpace/rules/checks.md 复制对应阶段的检查项 -->
- [ ] [质量检查名称]：[描述]
- [ ] ...
- [ ] 人类审批：Code Review 通过

## 事件

| 时间戳 | 事件类型 | 操作者 | 备注 | 交接 |
|--------|---------|--------|------|------|
| [YYYY-MM-DDTHH:MM] | [事件类型枚举值] | [Claude/用户/系统] | [备注] | [可选] |

## 执行快照

<!-- 系统自动维护，仅 L/XL 复杂度 CR 包含此 section -->
<!-- S/M 级 CR 流程短，不需要快照 -->

| 字段 | 值 |
|------|---|
| 步骤进度 | N/M（仅 L/XL 有执行计划时） |
| 已通过 Gate | 无 / Gate 1 / Gate 1, Gate 2 |
| 变更文件 | file1(+N/-M), file2(+N/-M)（最多 5 个） |
| 最近 checkpoint | 时间戳 + 事件类型 |
| 恢复建议 | 一句话（<=30 字） |
```

## 字段合法值

### 事件类型枚举

时间戳列格式：`YYYY-MM-DDTHH:MM`（精确到分钟，支持小时级度量）。

| 事件类型 | 含义 | 典型操作者 | 度量用途 |
|---------|------|-----------|---------|
| `created` | CR 创建 | Claude | 周期起点 |
| `intent_set` | 意图确认或更新 | Claude/用户 | — |
| `developing_start` | 进入 developing 状态 | Claude | 前置时间起点 |
| `step_N_done` | L/XL 执行计划步骤 N 完成 | Claude | 步骤粒度追踪 |
| `gate1_pass` | Gate 1 通过 | 系统 | 一次通过率分子 |
| `gate1_fail` | Gate 1 失败 | 系统 | 一次通过率分母 |
| `gate2_pass` | Gate 2 通过 | 系统 | 一次通过率分子 |
| `gate2_fail` | Gate 2 失败 | 系统 | 一次通过率分母 |
| `review_submit` | 提交人类审核 | Claude | — |
| `approved` | 人类批准 | 用户 | 打回率分母 |
| `rejected` | 人类打回 | 用户 | 打回率分子 |
| `merged` | 合并完成 | Claude | 周期终点 |
| `paused` | 暂停 | Claude/用户 | 阻塞时间起点 |
| `resumed` | 恢复 | Claude/用户 | 阻塞时间终点 |
| `change_scope` | 范围变更 | Claude/用户 | 返工率 |
| `released` | 纳入 Release | 系统 | — |

注：`step_N_done` 中 N 为实际步骤编号（如 `step_3_done`），不是固定枚举值。

### 类型

**合法值**：`feature`（默认）| `defect` | `hotfix`

| 类型 | 含义 | 使用场景 |
|------|------|---------|
| feature | 新功能或增强（默认） | 正常迭代中的产品功能开发 |
| defect | 缺陷修复 | 已发布功能发现的问题，通常由 /pace-feedback 创建 |
| hotfix | 紧急修复 | 生产环境紧急问题，可走加速路径（跳过部分门禁） |
| tech-debt | 技术债务偿还 | 重构、性能优化、依赖升级等非功能性改进 |

类型规则：
- `feature` 是默认值，现有无 type 字段的 CR 自动视为 feature（向后兼容）
- `defect` 和 `hotfix` 必须填写 severity 字段
- `hotfix` 可走加速路径：created → developing → verifying → merged（跳过 in_review，但仍需事后审批记录）
- `tech-debt` 走标准路径，但迭代规划时可计入技术债务预算（见 project-format.md 配置章节）

### 严重度

**合法值**（仅 defect/hotfix）：`critical` | `major` | `minor` | `trivial`

| 严重度 | 含义 | 适用范围 |
|--------|------|---------|
| critical | 系统不可用、数据丢失 | defect / hotfix |
| major | 核心功能受损、无可行替代方案 | defect / hotfix |
| minor | 次要功能受损、有替代方案 | defect / hotfix |
| trivial | 界面细节、文案错误 | defect / hotfix |

严重度规则：
- 仅 `defect` 和 `hotfix` 类型需要填写
- `feature` 类型不填写此字段（缺失不报错）
- `critical` 的 hotfix 可触发加速路径

### 复杂度

**合法值**（可选）：`S` | `M` | `L` | `XL`

| 等级 | 含义 | 量化标准 |
|------|------|---------|
| S | 简单 | ≤3 文件、≤1 目录、单一验收条件 |
| M | 中等 | 4-7 文件、2-3 目录、2-3 个验收条件 |
| L | 大型 | 8-15 文件、4-5 目录、4+ 验收条件 |
| XL | 超大 | >15 文件、>5 目录、跨模块架构级 |

约束：
- 可选字段——缺失时不影响流程，现有无复杂度字段的 CR 自动视为未评估（向后兼容）

### 状态

| 状态 | 含义 | 执行者 |
|------|------|--------|
| created | 已创建，未开始 | — |
| developing | 编码、测试中 | Claude 自治 |
| verifying | 集成验证中 | Claude 自治 |
| in_review | 等待人类审核 | 人类 |
| approved | 已审核，待合并 | Claude |
| merged | 已合并 | — |
| released | 已发布（可选终态） | Release 关闭后自动标记 |
| paused | 暂停 | 需求变更触发 |

`released` 状态说明：
- 可选终态——不使用 Release 流程时 `merged` 仍是有效终态（向后兼容）
- CR 纳入 Release 并完成部署验证后，由 Release 关闭流程自动标记
- 不可手动直接设置——仅通过 Release 关闭流程触发

`paused` 状态说明：
- 任何状态都可以转到 paused（需求暂停/砍掉时）
- 恢复时回到暂停前的状态
- 暂停期间保留：分支、代码、质量检查进度、事件记录
- CR 文件中增加 `暂停前状态` 字段记录恢复目标

### CR 间关联关系

| 关系类型 | 语义 |
|---------|------|
| 阻塞（blocks/blocked-by） | 硬依赖：B 必须等 A 完成 |
| 前置（follows/precedes） | 时序依赖（非硬阻塞） |
| 关联（relates-to） | 信息关联，无硬依赖 |

关联规则：
- **向后兼容**：仅含 `阻塞` 字段的旧 CR 自动视为 blocks 关系
- **格式迁移**：旧格式 `- **阻塞**：CR-ID（原因）` 等价于新格式 `关联` section 中的 `阻塞` 行
- **变更影响**：/pace-change 影响分析时遍历所有关联关系类型，blocks 和 follows 影响最高，relates-to 作为参考信息
- **简化写法**：仅有一种关系时可省略 section 结构，直接写 `- **阻塞**：...`

## 外部关联字段

可选字段——由 `/pace-sync link` 自动写入，记录 CR 与外部实体的关联。

**格式**：`[平台:ID](https://平台URL)`
- 示例：`[github:#42](https://github.com/owner/repo/issues/42)`
- 示例：`[linear:PROJ-123](https://linear.app/team/issue/PROJ-123)`

**规则**：
- 缺失时不影响任何流程（向后兼容）
- /pace-sync link 自动填写，用户也可手动编辑
- /pace-sync push/status 读取此字段定位外部实体
- 一个 CR 只关联一个外部实体（1:1 映射）

## 命名规则

- 文件名：`CR-001.md`、`CR-002.md`...（三位补零自增）
- ID 自增：扫描 `.devpace/backlog/` 中现有 CR 文件的最大编号 +1
- 分支名：`feature/` + 标题的 kebab-case 缩写（defect 类型用 `fix/`，hotfix 用 `hotfix/`）

## 事件表操作者字段

操作者标识谁执行了该事件，确保角色约束可审计：

| 操作者 | 含义 | 典型事件类型 |
|--------|------|-------------|
| Claude | Claude 自动执行 | `created`, `developing_start`, `gate1_pass`, `merged` |
| 用户 | 人类操作 | `approved`, `rejected`, `paused`, `resumed` |
| 系统 | 流程自动触发 | `released` |

规则：
- 新创建的 CR 事件表必须包含操作者列
- 事件类型必须使用上方枚举值（`step_N_done` 中 N 为实际编号）

## 事件表交接列

交接列为可选字段——仅在状态转换时记录上下文传递信息，帮助下游 Agent/Skill 理解前序决策上下文。

| 事件类型 | 交接内容 | 示例 |
|---------|---------|------|
| `gate1_pass` | 遗留事项或注意点 | "遗留：无新技术债" 或 "注意：新增 3 个 TODO 待后续处理" |
| `gate2_pass` | 验证中发现的边界情况 | "边界：大文件（>1MB）未测试" |
| `rejected` | 打回原因分类 + 期望方向 | "质量：错误提示不清晰，期望：用户可理解的错误消息" |
| `merged` | 后续注意事项 | "后续：性能优化可作为独立 CR" 或 "无特殊注意" |

规则：
- 无交接信息时留空或填"—"
- 交接内容 ≤30 字（简洁原则）

## 事件表备注列用法

备注列记录"为什么"——决策理由和关键假设。不重复 git log 已有的"做了什么"。

示例：
- "方案：Middleware 模式，因为需要请求上下文"
- "假设：空输入返回空结果"
- "调整：原计划单文件，拆分为 3 模块支持测试"
- "根因：REL-001 部署后发现 CR-003 引入的 null check 缺失"
- "验收条件 2→4 项: +OAuth 支持, +手机号验证"（/pace-change modify 时记录 PF 验收标准变更摘要）

### Checkpoint 与事件类型的关系

门禁通过/失败直接使用事件类型枚举（`gate1_pass`、`gate2_pass`、`approved`），不再需要备注列的 `[checkpoint: ...]` 标记。备注列专注记录"为什么"——决策理由、证据摘要、反思观察。

L/XL CR 执行计划步骤完成时使用事件类型 `step_N_done`（如 `step_3_done`），用于跨会话精确恢复到步骤级。S/M CR 无此事件。

用途：变更管理恢复定位 · 门禁审计 · Gate 3 人类审批参考 · L/XL 跨会话步骤级恢复。

**证据摘要格式**：详见 `../process/checks-format.md` "验证证据格式"章节。Gate 3 由人类操作，不附带自动证据。

示例事件表：

| 时间戳 | 事件类型 | 操作者 | 备注 | 交接 |
|--------|---------|--------|------|------|
| 2026-02-21T10:30 | created | Claude | — | — |
| 2026-02-21T11:15 | developing_start | Claude | — | — |
| 2026-02-21T14:00 | gate1_pass | 系统 | tsc 0 error, 8/8 tests passed [gate1-reflection: 无新技术债] | 遗留：无新技术债 |
| 2026-02-21T15:30 | gate2_pass | 系统 | 3/3 验收条件满足 [gate2-reflection: 边界已覆盖] | 边界：大文件未测试 |
| 2026-02-21T15:35 | review_submit | Claude | — | — |
| 2026-02-21T16:00 | approved | 用户 | — | — |
| 2026-02-22T09:00 | paused | 用户 | 需求变更：暂停等待新方案 | — |
| 2026-02-23T10:00 | resumed | 用户 | 恢复至 approved | — |

## 执行快照规则

- **仅 L/XL 复杂度 CR 自动生成**：S/M 流程短，state.md 足够恢复
- **"恢复建议"字段**：给下次会话的 Claude 看，用命令式语句（如"继续步骤 4 编写集成测试"），≤30 字
- **"变更文件"字段**：从 `git diff --stat` 获取，不手动维护（P7 Git 为源），最多 5 个文件
- **更新时机**：Gate 通过时、L/XL 步骤完成时、会话结束时（session-end 提醒）
- **位置**：在事件表 section 之后，质量检查 section 之前

## 风险预评估（可选）

Pre-flight 风险扫描结果。由 `/pace-guard scan` 或推进模式意图检查点（L/XL）写入。

格式：

| # | 维度 | 等级 | 发现 | 建议 |
|---|------|------|------|------|
| R1 | [维度] | [Low/Medium/High] | [发现描述] | [建议动作] |

**综合风险等级**：[Low/Medium/High]

### 字段合法值

- **维度**：历史教训、依赖影响、架构兼容性、范围复杂度、安全敏感度
- **等级**：Low、Medium、High
- **综合风险等级**：取所有维度的最高等级

### 写入条件

- L/XL CR：进入 developing 前触发
- S/M CR：仅在 insights.md 有匹配 defense pattern（置信度 ≥ 0.5）时触发

## 运行时风险（可选）

推进模式中 checkpoint 实时检测到的风险信号。由 Claude 在推进模式 checkpoint 时追加。

格式：

| 时间 | 信号类型 | 等级 | 发现 | 处理 |
|------|---------|------|------|------|
| [HH:MM] | [信号类型] | [Low/Medium/High] | [发现描述] | [处理方式] |

### 字段合法值

- **信号类型**：技术债引入、安全隐患、架构腐化
- **等级**：Low、Medium、High
- **处理**：已记录（Low 默认）、已提醒（Medium 默认）、已暂停（High 默认）

### 写入条件

- 推进模式 checkpoint 产出
- Medium/High 风险同步创建 `.devpace/risks/RISK-NNN.md` 持久化

## Consumers

pace-dev, pace-change, pace-feedback, pace-test, pace-pulse, pace-init, pace-guard, rules
