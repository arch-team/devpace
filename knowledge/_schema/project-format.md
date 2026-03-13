# 产品线文件格式契约

> **职责**：定义 project.md 的结构。/pace-init 创建和 Claude 更新时遵循此格式。

## §0 速查卡片

```
project.md 是项目的战略全景图 + 导航地图
完整版包含：配置（可选）+ 愿景（链接 vision.md 或内联）+ 战略上下文（链接 vision.md 或内联）+ 业务目标（索引表链接 objectives/ 或内联）+ 成效指标 + 实施路径 + 范围 + 原则 + 价值功能树（OBJ→Epic→BR→PF→CR）
配置：自主级别（辅助/标准/自主，默认标准）— 控制 Claude 在推进模式中的自主程度
模式：完整（默认）或 lite（OBJ→PF→CR，跳过 OPP/Epic/BR，适合个人小项目）
最小版（v0.4.0 init）：项目名 + 描述 + 空桩（随开发自然生长）
愿景：独立文件 vision.md（有时链接引用，无时保持内联格式，向后兼容）
战略上下文：vision.md 内 section（有 vision.md 时链接引用，无时保持内联格式）
范围：做什么 / 不做什么（首次 /pace-change 或范围讨论时填充）
原则：项目级技术/产品原则（首次 /pace-retro 或技术讨论时积累）
PF 可选丰富：用户故事(首个 CR) + 验收标准(verifying) + 边界(变更管理)
PF 溢出：功能规格 >15 行 | 关联 3+ CR | 经历 modify → 自动溢出到 features/PF-xxx.md，树视图保留链接
BR 溢出：关联 3+ PF | 业务上下文 >5 行 | 经历 modify → 自动溢出到 requirements/BR-xxx.md，树视图保留链接
价值功能树：OBJ → Epic → BR → PF → CR 的完整链路（Epic 始终用链接指向独立文件）
CR 状态用 emoji：🔄 进行中 | ✅ 完成 | ⏳ 待开始 | 🚀 已发布
Release 标记：📦 待发布 | 🚀 已发布
业务机会看板在独立的 opportunities.md 中（不在 project.md）
```

## 最小状态（v0.4.0 渐进式初始化）

最小初始化（`/pace-init`）时 project.md 可以是桩文件，仅包含项目名和描述：

```markdown
# [项目名称]

> [一句话项目定位]

## 愿景

（首次 /pace-biz 或 /pace-init full 时填充）

## 战略上下文

（首次 /pace-biz 或讨论战略时填充）

## 业务目标

（随开发自然生长 — 首次 /pace-retro 或讨论业务目标时引导定义）

## 实施路径

（首次 /pace-plan 时规划）

## 范围

（首次 /pace-change 或讨论项目范围时填充）

## 项目原则

（首次 /pace-retro 或讨论技术/产品决策时积累）

## 价值功能树

（功能树随工作自动生长 — 开始做第一个功能时自动出现）
```

桩文件中的占位文字在以下时机被替换为实际内容：
- **愿景**：首次 `/pace-biz` 或 `/pace-init full` 时引导定义（创建 vision.md 独立文件，project.md 改为链接引用）
- **战略上下文**：首次 `/pace-biz` 或讨论战略时填充（纳入 vision.md）
- **价值功能树**：首个 CR 创建时，Claude 自动推断 PF 并回填
- **业务目标**：首次 `/pace-retro` 或用户主动讨论业务目标时引导定义
- **实施路径**：首次 `/pace-plan` 时规划
- **范围**：首次 `/pace-change` 或用户主动讨论项目范围时填充
- **项目原则**：首次 `/pace-retro` 或讨论技术/产品决策时积累

Claude 在更新 project.md 时，如果发现是桩状态（含占位文字），先补充对应 section 的结构再填充内容。

## 完整内容

### 1. 项目标题和 blockquote 定位

```markdown
# [项目名称]

> [一句话项目定位]
```

### 1.5 项目配置（可选）

```markdown
## 配置

- **自主级别**：[辅助 | 标准 | 自主]（默认：标准）
```

| 值 | 含义 | 适用场景 |
|---|------|---------|
| 辅助 | Claude 在 Gate 失败时询问而非自动修复 | 新项目/新用户/建立信任阶段 |
| 标准（默认） | Claude 自动执行+自修复，Gate 3 人类审批 | 已建立信任/标准开发流程 |
| 自主 | 标准行为 + 简化审批条件放宽 | 高信任/批量操作/熟练用户 |

规则：
- 字段不存在时默认"标准"（向后兼容）
- 用户可随时修改，修改后即时生效（下一个 CR 生效）
- Claude 不自动修改此字段——仅用户主动调整
- **智能建议**：pace-pulse 每 5 个 CR merged 后自动评估 Gate 通过率和打回率，建议级别调整（需用户确认）

#### preferred-role（可选）

```markdown
- **偏好角色**：[biz | pm | dev | tester | ops]
```

| 值 | 含义 | 适用场景 |
|---|------|---------|
| biz | 会话开始默认 Biz Owner 视角 | 持续做业务规划的用户 |
| pm | 会话开始默认 PM 视角 | 持续做迭代管理的用户 |
| dev（默认） | 会话开始默认 Dev 视角 | 标准开发流程 |
| tester | 会话开始默认 Tester 视角 | 持续做质量保证的用户 |
| ops | 会话开始默认 Ops 视角 | 持续做运维管理的用户 |

规则：
- 字段不存在时默认 Dev（当前行为不变，向后兼容）
- 通过 `/pace-role set-default <角色>` 设置，`/pace-role set-default auto` 移除
- 会话启动时读取此字段作为初始角色（优先级低于显式 `/pace-role` 设置）
- Claude 不自动修改此字段——仅用户通过 `/pace-role set-default` 调整

#### tech-debt-budget（可选）

```markdown
- **技术债务预算**：[0-100]%（默认：20%）
```

| 属性 | 说明 |
|------|------|
| 含义 | 每个迭代预留给 tech-debt 类型 CR 的容量百分比 |
| 默认值 | 20%（字段不存在时） |
| 消费方 | `/pace-plan`（迭代规划时预留容量）、`/pace-retro`（技术债务趋势指标） |
| 修改方式 | 用户手动编辑 project.md 或通过 `/pace-plan adjust` |

规则：
- 字段不存在时默认 20%（向后兼容）
- `/pace-plan` 在计算迭代容量时，将总容量 × tech-debt-budget% 作为 tech-debt CR 预留容量
- Claude 在 `/pace-biz infer` 发现大量技术债务时，可建议用户提高此预算

#### mode（可选）

```markdown
- **模式**：[lite]
```

| 值 | 含义 |
|---|------|
| （缺省） | 完整模式（OPP→Epic→BR→PF→CR） |
| `lite` | 轻量模式（OBJ→PF→CR，跳过 OPP/Epic/BR） |

规则：
- 字段不存在时默认完整模式（向后兼容）
- 通过 `/pace-init --lite` 设置
- lite 模式下价值功能树跳过 Epic/BR 层，PF 直接挂在 OBJ 下
- 首次通过 `/pace-biz` 创建 Epic/BR 时自动升级为完整模式（移除 `mode: lite` 标记）
- Claude 不自动修改此字段——仅用户通过 `/pace-init` 参数或 `/pace-biz` 触发升级

### 1.6 愿景（可选，渐进填充）

**有 vision.md 时**（独立文件，推荐）：

```markdown
## 愿景

→ [查看完整愿景](vision.md)
```

**无 vision.md 时**（内联格式，向后兼容）：

```markdown
## 愿景

- **目标用户**：[谁会用这个产品]
- **核心问题**：[他们的什么痛点]
- **差异化**：[为什么选你而不是替代方案]（首次 /pace-biz 时填充）
- **成功图景**：[做成了是什么样]（首次 /pace-retro 时填充）
```

填充时机：首次 `/pace-biz` 或 `/pace-init full` 时引导填充。愿景帮助 Claude 在后续决策中保持方向一致性。有 vision.md 时愿景详情在独立文件中维护，project.md 仅保留链接引用。

规则：
- 字段为空时保持空值或占位文字，不影响任何功能
- Claude 不自动推断愿景内容——愿景必须来自人类
- 向后兼容：无 vision.md 且无愿景 section 时保持现有一行 blockquote 格式
- 独立文件格式契约见 `knowledge/_schema/vision-format.md`

### 1.7 战略上下文（可选，渐进填充）

**有 vision.md 时**（独立文件，推荐）：

```markdown
## 战略上下文

→ [查看战略上下文](vision.md#战略上下文)
```

**无 vision.md 时**（内联格式，向后兼容）：

```markdown
## 战略上下文

**核心假设**：
- [假设 1]（[待验证 | 已验证 | 已推翻]）

**外部约束**：
- [约束 1]
```

填充时机：首次 `/pace-biz` 或讨论战略时填充。战略上下文帮助 Claude 理解决策约束和不确定性。有 vision.md 时战略上下文在独立文件中维护。

规则：
- 核心假设的状态由人类维护（`待验证` / `已验证` / `已推翻`）
- Claude 可在 /pace-retro 时建议更新假设状态，但需人类确认
- 字段为空时不影响任何功能（向后兼容）

### 2. 业务目标

**有 objectives/ 时**（独立文件，推荐）：

```markdown
## 业务目标

| OBJ | 目标 | 类型 | 状态 | MoS 进度 |
|-----|------|------|------|---------|
| [OBJ-001](objectives/OBJ-001.md) | [描述] | business | 活跃 | 2/3 |
| [OBJ-002](objectives/OBJ-002.md) | [描述] | product | 活跃 | 1/2 |
```

摘要索引表提供 OBJ 全景概览，点击链接查看完整 OBJ 定义（含双维度 MoS、关联专题等）。

**无 objectives/ 时**（内联格式，向后兼容）：

```markdown
## 业务目标

### OBJ-1：[目标描述]（[business | product | tech | growth | efficiency | compliance]，[短期 | 中期 | 长期]）

**成效指标（MoS）**：
- [ ] [指标 1]
- [ ] [指标 2]（目标：[值]，当前：[值] → 进度 [N]%）
- [x] [指标 3]
```

成效指标用 checkbox，达成时勾选。

**OBJ 产品维度属性**：每个 OBJ 可标注类型和时间维度：
- **类型**：`business` / `product` / `tech` / `growth` / `efficiency` / `compliance`（6 类）
- **时间维度**：`短期`（当前迭代）/ `中期`（2-3 迭代）/ `长期`（季度+）
- 这些属性为可选标注——缺失时不影响功能（向后兼容）
- 多个 OBJ 时每个 OBJ 用三级标题（`### OBJ-N：...`）
- 独立文件格式契约见 `knowledge/_schema/obj-format.md`

**量化进度标注（可选）**：对连续性指标（如"响应时间 < 200ms"、"部署频率 ≥ 1 次/周"），可在括号内追加当前测量值和进度百分比。此标注由 `/pace-retro` 在有 dashboard.md 数据时自动计算并建议追加（需用户确认），二值指标（如"首个 CR 全流程走通"）保持简单 checkbox。

### 3. 实施路径

```markdown
## 实施路径

| Step | 名称 | 状态 |
|------|------|------|
| 1 | [名称] | 🔄 进行中 |
| 2 | [名称] | ⏳ 待开始 |
```

### 3.5 范围

```markdown
## 范围

**做什么**：
- [核心能力 1]

**不做什么**：
- [明确排除 1]
```

填充时机：首次 `/pace-change` 或用户主动讨论项目范围时。范围明确后有助于 Claude 在变更管理中判断需求是否在范围内。

### 3.6 项目原则

```markdown
## 项目原则

- [原则 1：简述]（[来源：第 N 次回顾 / 讨论日期]）
```

填充时机：首次 `/pace-retro` 或讨论技术/产品决策时积累。项目原则帮助 Claude 在后续 CR 中保持决策一致性。

### 5. 价值功能树

**有 objectives/ 时**（OBJ 行使用链接）：
```markdown
## 价值功能树

[OBJ-001：目标名](objectives/OBJ-001.md)
├── [EPIC-001：专题名](epics/EPIC-001.md)
│   ├── BR-001：需求名 `P0` `进行中` → PF-001 → CR-001 🔄
│   └── [BR-002：需求名](requirements/BR-002.md) `P1` → PF-002, PF-003
└── [EPIC-002：专题名](epics/EPIC-002.md)
    └── BR-003：需求名 `P0` → PF-004 → CR-003 ✅
```

**无 objectives/ 时**（OBJ 行使用纯文本，向后兼容）：
```markdown
## 价值功能树

OBJ-001（[目标名]）
├── [EPIC-001：专题名](epics/EPIC-001.md)
│   ├── BR-001：需求名 `P0` `进行中` → PF-001 → CR-001 🔄
│   └── [BR-002：需求名](requirements/BR-002.md) `P1` → PF-002, PF-003
└── [EPIC-002：专题名](epics/EPIC-002.md)
    └── BR-003：需求名 `P0` → PF-004 → CR-003 ✅
```

**无 Epic 时**（向后兼容）：BR 直接挂在 OBJ 下，与当前行为一致：
```markdown
OBJ-001（[目标名]）
├── BR-001：[业务需求名]
│   ├── PF-001：[产品功能名] ✅ → [详情](features/PF-001.md)
│   └── PF-002：[产品功能名] → (待创建 CR)
```

**Epic 行格式**：始终使用 Markdown 链接指向独立文件：
```markdown
[EPIC-xxx：专题名](epics/EPIC-xxx.md)
```

**BR 行格式**（两种，与 PF 溢出模式类似）：

未溢出：
```
BR-xxx：[需求名] `P0` `进行中` → PF-001 → CR-001 🔄
```

已溢出：
```
[BR-xxx：需求名](requirements/BR-xxx.md) `P1` → PF-002, PF-003
```

BR 行的标签说明：
- 优先级标签：`P0` / `P1` / `P2`（无优先级时省略）
- 状态标签：仅非默认时显示，如 `暂停`

PF 溢出后的树视图格式（已溢出的 PF 用 `[详情]` 链接替代 CR 列表）：
```markdown
PF-xxx：[产品功能名] [状态] → [详情](features/PF-xxx.md)
```
`[详情](features/PF-xxx.md)` 是实际的 Markdown 链接，在 IDE 中可点击跳转到 PF 文件。
未溢出的 PF 保持原格式（直接列出 CR）。三种溢出格式（Epic链接、BR溢出、PF溢出）可在同一棵树中共存。

CR 状态标记：
- `🔄` — 进行中
- `✅` — 已完成（merged）
- `🚀` — 已发布（released）
- `⏳` — 待开始
- `🐛` — 缺陷修复（type:defect）
- `🔥` — 紧急修复（type:hotfix）
- `(待创建 CR)` — 产品功能已定义但尚未创建变更请求

### 功能树格式校验规则

Claude 每次写入或更新价值功能树时，确保格式一致性：

```
OBJ 行（有 objectives/）：[OBJ-xxx：目标名](objectives/OBJ-xxx.md) — 链接格式
OBJ 行（无 objectives/）：OBJ-xxx（目标名）                       — 纯文本（向后兼容）
Epic 行：        [EPIC-xxx：名称](epics/EPIC-xxx.md)        — 始终链接，不内联
未溢出 BR 行：   BR-xxx：[名称] `Px` → PF-xxx → CR-yyy 🔄   — 纯文本
已溢出 BR 行：   [BR-xxx：名称](requirements/BR-xxx.md) `Px`  — 溢出后用链接
PF 行（有 CR）： PF-xxx：[名称] → CR-yyy 🔄                  — 多 CR 逗号分隔
PF 行（无 CR）： PF-xxx：[名称] → (待创建 CR)                — 规划阶段
已溢出 PF 行：   PF-xxx：[名称] [状态] → [详情](features/PF-xxx.md) — 溢出后用链接
```

CR 创建时：在 PF 行追加 CR 引用。CR 状态变更时：更新对应 emoji。
Epic/BR 创建时：在树中追加对应行。Epic 状态变更时：更新 Epic 文件（不在树中标记状态）。

Release 标记（价值功能树下方，可选）：
```markdown
## 发布记录

| Release | 状态 | 包含 CR | 部署日期 |
|---------|------|--------|---------|
| REL-001 | 📦 staging | CR-001, CR-002 | — |
| REL-002 | 🚀 deployed | CR-003 | 2026-02-20 |
```

Release 状态标记：
- `📦` — staging（待发布/准备中）
- `🚀` — deployed/verified/closed（已发布）

### PF 渐进丰富（可选）

PF 行可追加括号内用户故事，丰富功能描述：

```markdown
PF-001：用户认证（作为用户，我希望能安全登录）→ CR-001 🔄
```

当 PF 有验收标准或边界定义时，在价值功能树下方追加功能规格 section：

```markdown
## 功能规格

### PF-001：用户认证

**验收标准**：
1. 支持邮箱+密码登录
2. 密码强度校验（≥8 位，含大小写和数字）

**边界**：
- 不包含第三方 OAuth 登录

**依赖**：（可选）
- PF-001（需要 session 管理）
```

| 信息 | 填充时机 | 位置 |
|------|---------|------|
| 用户故事 | 首个 CR 创建时 | PF 行括号内 |
| 验收标准 | CR 进入 verifying 时 | 功能规格 section |
| 边界 | /pace-change 涉及该 PF 时 | 功能规格 section |
| 依赖 | /pace-plan 或讨论 PF 间关系时 | 功能规格 section（可选） |

### PF 溢出模式（Overflow Pattern）

当 PF 信息量增长到一定规模时，自动溢出为独立文件 `features/PF-xxx.md`，project.md 保留树视图和链接。

**触发条件**（满足任一）：
- PF 的功能规格超过 ~15 行
- PF 关联 3+ 个 CR（含已完成）
- PF 经历过 `/pace-change modify`

**溢出后 project.md 变化**：
1. 价值功能树中该 PF 行改为链接格式（见功能树格式校验规则中的"已溢出 PF 行"）
2. 功能规格 section 中该 PF 段落移除（如 section 变为空则移除整个 section）

**规则**：
- 溢出是自动、零摩擦的（用户无感知，对齐 P1 零摩擦原则）
- 溢出是单向的——一旦溢出不回退
- 无 `features/` 目录的项目不受影响（完全向后兼容）
- PF 文件格式契约见 `knowledge/_schema/pf-format.md`

**验收标准变更历史（溢出前）**：

在功能规格 section 内用 HTML 注释记录变更历史：

```markdown
### PF-001：用户认证

**验收标准**：
1. 支持邮箱+密码登录
2. 密码强度校验（≥8 位，含大小写和数字）
3. 登录失败 3 次后锁定 15 分钟
<!-- history: 2026-02-20 原始 2 项; 2026-02-25 +锁定机制 via /pace-change -->
```

溢出后 history 注释迁移到 PF 文件中，`git log features/PF-xxx.md` 提供完整文件级历史。

### BR 溢出模式（Overflow Pattern）

当 BR 信息量增长到一定规模时，自动溢出为独立文件 `requirements/BR-xxx.md`，project.md 保留树视图和链接。

**触发条件**（满足任一）：
- BR 关联 3+ 个 PF
- 业务上下文超过 ~5 行
- BR 经历过 `/pace-change modify`

**溢出后 project.md 变化**：
1. 价值功能树中该 BR 行改为链接格式（见功能树格式校验规则中的"已溢出 BR 行"）

**规则**：
- 溢出是自动、零摩擦的（对齐 P1 零摩擦原则）
- 溢出是单向的——一旦溢出不回退
- 无 `requirements/` 目录的项目不受影响（完全向后兼容）
- BR 文件格式契约见 `knowledge/_schema/br-format.md`

## 溯源标记

project.md 中 Claude 自动生成的内容使用 HTML 注释标记来源，区分用户输入与 Claude 推断。标记不影响 Markdown 渲染，仅在深入层（/pace-trace 或 --detail）时可见。

### 语法

```
<!-- source: user -->                              用户通过自然语言明确表达的内容
<!-- source: claude, [推断原因] -->                  Claude 推断/分解/自动补充的内容
<!-- source: claude, inferred from "[用户原话]" -->   Claude 从用户原话推断得出
<!-- source: claude, decomposed from [BR/PF-ID] -->  Claude 从上级实体分解得出
<!-- source: claude, auto-created -->                Claude 自动创建（如 CR 创建）
```

### 标记位置

| 内容类型 | 标记位置 | 示例 |
|---------|---------|------|
| BR 行 | 行末 | `BR-001：用户认证系统 <!-- source: user -->` |
| PF 行 | 行末 | `PF-001：登录流程（用户可以通过邮箱密码登录） <!-- source: claude, inferred from "做个登录功能" -->` |
| CR 关联 | 行末 | `CR-001 🔄 <!-- source: claude, auto-created -->` |
| 范围条目 | 条目末 | `- 支持邮箱+密码登录 <!-- source: user -->` |
| 功能规格 | section 级 | `### PF-001 验收标准 <!-- source: claude, from CR-001 verifying -->` |

### 规则

- **默认不显示**：日常操作和 /pace-status 输出中不展示溯源标记（对齐 P2 渐进暴露）
- **深入层可见**：/pace-trace 或 `--detail` 查询时展示溯源信息
- **新增内容必须标记**：Claude 新增或修改 project.md 内容时必须添加溯源标记
- **用户手动编辑**：人类直接编辑 project.md 时 Claude 无法标记来源，视为 `user`
- **向后兼容**：无溯源标记的既有内容不影响任何功能，视为 `user`（保守假设）
- **跨会话区分**：新会话恢复时，Claude 可通过溯源标记区分"用户明确说的"和"上次推断的"

## 更新时机

- 愿景在 `/pace-biz` 或 `/pace-init full` 时引导填充（人类内容，Claude 不自动推断）；有 vision.md 时 project.md §1.6 为链接引用
- 战略上下文在 `/pace-biz` 或讨论战略时填充，假设状态由人类维护；有 vision.md 时 project.md §1.7 为链接引用
- 业务目标更新：有 objectives/ 时更新 OBJ 文件 + project.md 索引表同步；无 objectives/ 时直接更新 project.md 内联内容
- 价值功能树在 CR 创建/状态变更时由 Claude 自动更新
- Epic 创建时在树中追加 Epic 链接行，Epic 文件独立管理
- BR 创建时在树中追加 BR 行，溢出触发后改为链接格式
- 业务目标和成效指标由人类维护
- 实施路径的 Step 状态在对应阶段完成时更新
- 发布记录在 Release 创建/状态变更时自动更新（有 Release 流程时）
- 范围在 `/pace-change` 或讨论项目范围时更新
- 项目原则在 `/pace-retro` 或技术/产品决策讨论后更新
- 功能规格在 PF 相关 CR 进入 verifying 或 /pace-change 涉及该 PF 时更新
- PF 溢出触发时，功能规格段落迁移到 `features/PF-xxx.md`，树视图更新为链接格式
- BR 溢出触发时，树视图 BR 行改为链接格式
- 偏好角色在用户通过 `/pace-role set-default` 设置时更新
- `/pace-init` 推断 OBJ 后，§2 业务目标从桩占位替换为索引表（有 objectives/ 时）或内联格式
- OBJ 文件变更（状态、MoS 进度）时，project.md §2 索引表同步更新
