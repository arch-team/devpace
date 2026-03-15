# 业务规划（`/pace-biz`）

devpace 一直管理着从产品功能（PF）到代码变更（CR）的交付流程，但上游的问题——*这些功能从何而来？*——始终游离在体系之外。业务机会散落在各种笔记中，专题（Epic）活在外部工具里，战略目标与日常开发之间的关联只能靠默契维系。`/pace-biz` 补上了这一环，将结构化的业务规划纳入同一条价值链，让每一行代码都能追溯到它背后的业务机会。

## 快速上手

```
1. /pace-biz opportunity "企业客户需要 SSO"        → 捕获机会 → OPP-001 创建
2. /pace-biz epic OPP-001 "企业级认证"             → 创建专题 → EPIC-001 关联 OBJ
3. /pace-biz decompose EPIC-001                    → 分解需求 → 生成 BR 和 PF
4. /pace-biz refine BR-003                         → 精炼细节 → 补充验收标准
```

或者让 Claude 交互式引导：

```
你：    /pace-biz
Claude：[根据项目上下文推荐下一步操作]
        或选择：opportunity / epic / decompose / refine / align / view / discover / import / infer
```

从模糊想法开始：

```
5. /pace-biz discover "我想做一个任务管理工具"   → 多轮对话发现 → 完整候选树
6. /pace-biz import 会议纪要.md                  → 提取需求 → 合并到功能树
7. /pace-biz infer                               → 扫描代码库 → 差距报告
```
## 用户使用旅程

## 子命令

### `opportunity` — 捕获业务机会

业务机会是规划流程的原始输入——市场信号、客户反馈、利益相关者请求或竞争观察。`/pace-biz opportunity` 用结构化元数据捕获它们，确保没有遗漏。

每个机会包含：
- **自动编号**（OPP-001、OPP-002……）
- **来源分类** — 客户反馈、市场调研、利益相关者请求、竞争分析、技术债务、内部倡议
- **初步评估** — Claude 建议与现有 OBJ 的关联度和潜在影响级别
- **持久化记录** — 写入 `.devpace/opportunities.md`，含创建日期和状态（new / evaluating / accepted / declined / deferred）

多个机会可以指向同一战略目标，自然形成需求优先级的信号积累。

### `epic` — 创建战略专题

专题是原始机会与可执行业务需求之间的桥梁。`/pace-biz epic` 创建结构化专题，将相关工作归入清晰的业务意图之下。

专题包含：
- **OBJ 对齐** — 服务于哪些战略目标？Claude 根据专题描述和关联机会建议映射
- **成功度量（MoS）** — 具体的、可验证的业务级完成标准
- **范围边界** — 明确纳入和排除的内容
- **独立文件** — 每个专题存储为 `epics/EPIC-xxx.md`，支持追溯和交叉引用

专题可从现有机会创建（`/pace-biz epic OPP-001 "标题"`）或直接创建（`/pace-biz epic "标题"`）。从机会创建时，双向链接自动记录。

### `decompose` — 分解为可交付项

分解是战略意图与执行规划的交汇点。`/pace-biz decompose` 支持两条分解路径：

1. **Epic → BR** — 将专题分解为业务需求，每个代表一项独立的业务能力或成果
2. **BR → PF** — 将业务需求分解为产品功能，每个可在一到两个迭代内交付

Claude 分析父级实体并建议分解方案——子项数量、建议标题、各自范围。用户审查、调整并确认后才创建文件。分解遵循现有价值链：新 BR 链接回所属专题，新 PF 链接回所属 BR。

**优先级框架** — 每个分解产出的子项通过 Value x Effort 矩阵获得建议优先级：

| | 低成本 | 高成本 |
|---|---|---|
| **高价值** | P0 | P1 |
| **中价值** | P1 | P2 |
| **低价值** | P2 | P2 |

价值依据对父级实体 MoS 的贡献度评估；成本为预估实现复杂度。用户可覆盖建议或直接指定优先级。

**依赖追踪** — Epic → BR 分解时，Claude 会询问每个新 BR 是否依赖同 Epic 下的已有 BR。依赖关系记录在 Epic 文件中，并在 `/pace-biz align` 健康检查时浮现。

### `refine` — 精炼已有需求

`decompose` 将实体分解为子项，而 `refine` 则深化已有 BR 或 PF 的细节——补充验收标准、边界条件、用户故事、异常处理和非功能需求。

精炼流程：
1. **定位实体** — 读取指定 BR 或 PF 的当前内容
2. **缺口分析** — Claude 识别哪些维度缺失或不完善（验收标准、用户故事、异常场景、NFR 等）
3. **引导追问** — 每轮 2-3 个针对性问题，仅针对需要补充的维度；已完善的维度自动跳过
4. **预览确认** — 变更以 diff 风格预览展示，确认后才写入

`refine` 与 `/pace-change modify` 的区别：refine 深化同一需求方向（内容更丰富，意图不变），modify 改变需求方向（重命名、调整范围、变更优先级）。

### `align` — 战略对齐检查

随着项目增长，业务规划容易偏移。`/pace-biz align` 对整个上游价值链做健康检查：

| 检查项 | 检测内容 |
|--------|---------|
| **OBJ 覆盖率** | 没有专题或 BR 映射的战略目标 |
| **孤立实体** | 未链接到任何上游实体的专题、BR 或 PF |
| **MoS 完整性** | 缺少可度量成功标准的专题或 BR |
| **分解空白** | 没有 BR 的专题，或没有 PF 的 BR |
| **停滞检测** | 长时间停留在"new"状态的机会 |
| **优先级分布** | 检测优先级通胀（P0 > 60%）或核心优先级缺失（无 P0），附健康比例参考 |
| **依赖健康度** | 循环依赖、关键路径瓶颈、就绪风险（BR 已排期但依赖项未完成） |
| **MoS 达成度** | 反向回溯 Epic MoS 完成度与 BR/PF 进度的对应关系；标记 BR 已完成但 MoS 未勾选的 Epic |

输出为简洁的对齐报告，每个问题附带内联修复命令（如 `→ /pace-biz decompose EPIC-002`、`→ /pace-change modify EPIC-001`）。

### `view` — 业务全景视图

`/pace-biz view` 渲染从机会到 CR 的完整价值流，鸟瞰业务意图如何贯穿整个系统：

```
OPP-001 "企业 SSO 需求"
  └─ EPIC-001 "企业级认证"  [OBJ-1]
       MoS：2/3 达成
       ├─ BR-003 "SSO 集成" P0
       │    ├─ PF-007 "SAML 提供商"      → CR-012 (developing)
       │    └─ PF-008 "OIDC 提供商"      → CR-013 (created)
       └─ BR-004 "会话管理" P1
            └─ PF-009 "Token 生命周期"    → CR-014 (created)
```

支持按 OBJ、专题、状态或层级深度过滤。无过滤条件时展示完整树状结构及状态指示。

**内联操作引导** — 处于可操作状态的实体会显示下一步提示：空 MoS 提示补充定义、未分解的专题/BR 建议 `/pace-biz decompose`、评估中的机会建议 `/pace-biz epic`。

**角色适配展示** — 通过 `/pace-role` 设置首选角色后，view 在不改变基础结构的前提下增加角色相关列（如 Biz Owner 看每个 Epic 的 MoS 进度，PM 看 PF 完成率和依赖信息，Tester 看验收标准数量和 Gate 2 状态）。

### `discover` — 交互式需求发现

当只有一个模糊想法——"我想做一个智能客服系统"——`/pace-biz discover` 启动多轮引导对话，逐步将想法塑造为结构化的价值链。

流程分阶段展开：
1. **目标框定**（1-2 轮）——要解决什么问题？目标用户是谁？
2. **功能头脑风暴**（2-4 轮）——用户必须能做什么？异常情况怎么办？
3. **边界定义**（1-2 轮）——明确不做什么？有什么约束？
4. **验证确认**（1 轮）——审查结构化候选树（OPP→Epic→BR→PF），调整后写入

会话状态持久化到 `.devpace/scope-discovery.md`，发现过程可跨多次对话。确认后所有候选写入对应 `.devpace/` 文件，临时会话文件删除。

**角色适配追问** — 设置首选角色后，头脑风暴阶段调整追问侧重：Biz Owner 侧重营收影响和市场拓展，PM 侧重用户场景和竞品对比，Dev 侧重技术可行性和架构约束，Tester 侧重可测试性和边界条件，Ops 侧重部署需求和基础设施影响。核心流程和产出结构不因角色而改变。

### `import` — 多源文档导入

团队在很多地方积累需求——会议纪要、用户反馈调研、竞品分析、技术债务清单。`/pace-biz import` 读取这些文档，提取需求实体，合并到现有功能树。

支持的源类型（自动检测）：
- **会议纪要** — Action Items 转为 BR/PF 候选
- **用户反馈** — 痛点转为 BR，功能请求转为 PF
- **竞品分析** — 差距功能转为 PF 候选
- **技术债务清单** — 债务项转为 PF（标记技术债务）
- **Issue 导出**（CSV/JSON）— Issues 映射为 PF/CR 候选
- **PRD / API 规格** — 同 `/pace-init --from` 的解析规则

每个提取的实体按 NEW/DUPLICATE/ENRICHMENT/CONFLICT 分类。用户审查 diff 格式的合并计划后才写入文件。import 在 OPP/Epic/BR/PF 层面操作——不创建 CR。

### `infer` — 代码库功能推断

对于遗留项目或文档滞后的项目，`/pace-biz infer` 扫描代码库，反向推导功能地图：

- **结构分析** — 目录、路由、API 端点、数据模型、UI 组件
- **信号挖掘** — TODO/FIXME 密度、README 与代码漂移、构建脚本
- **Git 增强分析**（可用时）— 文件热点、共变耦合、贡献者分布

输出为三段式差距报告：
1. **未追踪功能** — 代码存在但功能树中无对应 PF
2. **未实现功能** — 功能树有 PF 但无代码实现
3. **技术债务** — TODO/FIXME 高密度区域

用户选择哪些项纳入功能树。技术债务 PF 附"（技术债务）"后缀，便于过滤。

## 角色感知

`/pace-biz` 根据通过 `/pace-role` 设置的首选角色调整行为。角色感知影响三个维度，但不改变核心工作流和产出结构：

| 维度 | 角色如何影响行为 |
|------|-----------------|
| **追问方向** | `discover` 和 `decompose` 调整追问焦点（如 Biz Owner → 营收影响，Dev → 技术约束，Tester → 验收标准） |
| **展示内容** | `view` 增加角色相关列（如 PM 看依赖信息，Ops 看发布状态） |
| **分解提示** | `decompose` 在 BR/PF 创建时追加角色相关考量 |

默认角色（Dev）不产生任何行为变化——角色适配是纯粹的增量叠加。

## 写入范围保护

`/pace-biz` 是规划域 Skill，不得修改源代码或非规划文件。运行时通过 PreToolUse Hook 强制执行：

- **允许目标**：`.devpace/` 下的所有文件（opportunities.md、epics/、project.md、requirements/、scope-discovery.md、state.md 等）
- **阻断目标**：`.devpace/` 以外的所有文件——Hook 以 exit code 2 退出并输出描述性错误信息
- **Epic 质量门**：prompt Hook 验证即将写入的 Epic 文件是否包含有效 OBJ 引用和可度量的 MoS 定义

此保护自动运行，用户无需配置或手动调用。

## 向后兼容

在 `/pace-biz` 引入之前初始化的项目——没有 `opportunities.md`、`epics/` 目录或上游 BR 链接——继续正常工作，不受任何影响。现有的 PF → CR 流程完全不变。`/pace-biz` 的能力渐进式可用：在你准备好时捕获第一个机会或创建第一个专题，价值链自然向上延伸。

## 与其他命令的集成

| 命令 | 与 `/pace-biz` 的关系 |
|------|---------------------|
| `/pace-init` | 初始化 `.devpace/` 结构。`/pace-biz` 可用后，`pace-init` 可选择性地创建 `opportunities.md` 和 `epics/` 目录。 |
| `/pace-change` | 处理 PF 级需求变更。`/pace-biz` 在上游操作——创建 BR 和 PF，由 `/pace-change` 后续管理。 |
| `/pace-plan` | 通过选择 PF 规划迭代。`/pace-biz decompose` 产出的 PF 直接进入 `/pace-plan next` 的候选池。 |
| `/pace-status` | 展示完整项目状态。有 `/pace-biz` 数据时，状态视图可包含上游上下文（专题进度、OBJ 覆盖率）。 |
| `/pace-trace` | 追溯价值链连接。`/pace-biz` 在现有 BR → PF → CR 链之上增加 OPP → EPIC → BR 层级，丰富追溯能力。 |
| `/pace-role` | 设置首选角色视角。`/pace-biz` 读取此设置，按角色调整追问方向、展示列和分解提示。 |

## 相关资源

- [epic-format.md](../../knowledge/_schema/epic-format.md) — 专题文件 schema
- [br-format.md](../../knowledge/_schema/br-format.md) — 业务需求文件 schema
- [opportunity-format.md](../../knowledge/_schema/opportunity-format.md) — 机会记录 schema
- [skills/pace-biz/](../../skills/pace-biz/) — 操作规程
- [devpace-rules.md](../../rules/devpace-rules.md) — 运行时行为规则
- [用户指南](../user-guide.md) — 所有命令快速参考
