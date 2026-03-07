# 业务规划（`/pace-biz`）

devpace 一直管理着从产品功能（PF）到代码变更（CR）的交付流程，但上游的问题——*这些功能从何而来？*——始终游离在体系之外。业务机会散落在各种笔记中，专题（Epic）活在外部工具里，战略目标与日常开发之间的关联只能靠默契维系。`/pace-biz` 补上了这一环，将结构化的业务规划纳入同一条价值链，让每一行代码都能追溯到它背后的业务机会。

## 快速上手

```
1. /pace-biz opportunity "企业客户需要 SSO"        → 捕获机会 → OPP-001 创建
2. /pace-biz epic OPP-001 "企业级认证"             → 创建专题 → EPIC-001 关联 OBJ
3. /pace-biz decompose EPIC-001                    → 分解需求 → 生成 BR 和 PF
```

或者让 Claude 交互式引导：

```
你：    /pace-biz
Claude：[根据项目上下文推荐下一步操作]
        或选择：opportunity / epic / decompose / align / view
```

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

### `align` — 战略对齐检查

随着项目增长，业务规划容易偏移。`/pace-biz align` 对整个上游价值链做健康检查：

| 检查项 | 检测内容 |
|--------|---------|
| **OBJ 覆盖率** | 没有专题或 BR 映射的战略目标 |
| **孤立实体** | 未链接到任何上游实体的专题、BR 或 PF |
| **MoS 完整性** | 缺少可度量成功标准的专题或 BR |
| **分解空白** | 没有 BR 的专题，或没有 PF 的 BR |
| **停滞检测** | 长时间停留在"new"状态的机会 |

输出为简洁的对齐报告，针对每个发现的问题给出具体建议。

### `view` — 业务全景视图

`/pace-biz view` 渲染从机会到 CR 的完整价值流，鸟瞰业务意图如何贯穿整个系统：

```
OPP-001 "企业 SSO 需求"
  └─ EPIC-001 "企业级认证"  [OBJ-1]
       ├─ BR-003 "SSO 集成"
       │    ├─ PF-007 "SAML 提供商"      → CR-012 (developing)
       │    └─ PF-008 "OIDC 提供商"      → CR-013 (created)
       └─ BR-004 "会话管理"
            └─ PF-009 "Token 生命周期"    → CR-014 (created)
```

支持按 OBJ、专题、状态或层级深度过滤。无过滤条件时展示完整树状结构及状态指示。

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

## 相关资源

- [epic-format.md](../../knowledge/_schema/epic-format.md) — 专题文件 schema
- [br-format.md](../../knowledge/_schema/br-format.md) — 业务需求文件 schema
- [opportunity-format.md](../../knowledge/_schema/opportunity-format.md) — 机会记录 schema
- [skills/pace-biz/](../../skills/pace-biz/) — 操作规程
- [devpace-rules.md](../../rules/devpace-rules.md) — 运行时行为规则
- [用户指南](../user-guide.md) — 所有命令快速参考
