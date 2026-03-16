# 产品层组件架构

> **职责**：产品层组件间的协作关系——依赖方向、通信模式、合规检测。与 `info-architecture.md`（信息组织原则）、`plugin-dev-spec.md`（组件格式规范）、`project-structure.md`（文件放置规则）互补。

## §0 速查卡片

### 组件依赖矩阵（简版）

谁引用谁？`>` = 合法引用方向，`X` = 禁止。

| 引用方 \ 被引用方 | rules | SKILL.md | procedures | _schema | _signals | _guides | knowledge-root | hooks | agents |
|-------------------|-------|----------|-----------|---------|----------|---------|---------------|-------|--------|
| **rules** | — | X | X | > | > | X | > | X | X |
| **SKILL.md** | > | — | > (同 Skill) | > | > | > | > | X | X |
| **procedures** | > | X | — | > | > | > | > | X | X |
| **_schema** | X | X | X | > (同级) | X | X | X | X | X |
| **_signals** | X | X | X | > | — | X | > | X | X |
| **_guides** | X | X | X | > | > | — | > | X | X |
| **knowledge-root** | X | X | X | > | X | X | — | X | X |
| **hooks** | X | X | X | X | X | X | X | — | X |
| **agents** | X | X | X | X | X | X | X | X | — |

**关键约束**：
- **Schema 是纯契约层**——仅引用同级 Schema，不引用 Skill、Rules 或 Hooks 实现
- **Hooks 是独立守护层**——通过 `.devpace/` 运行时文件和 stdin JSON 感知状态，不解析 Markdown 引用
- **Agents 是纯人格定义**——仅包含 persona + 工具权限，不引用任何其他组件

**组件选择**：新增组件的类型判断和放置位置 → `project-structure.md` §3

### 合规检查清单

| 检查项 | 命令 / 方法 | 频率 |
|--------|------------|------|
| Schema 无反向引用 | `grep -r "skills/\|rules/" knowledge/_schema/` 应为空 | 每次 Schema 变更 |
| Hooks 无 Markdown 引用 | `grep -r "knowledge/\|skills/\|rules/" hooks/` 应为空 | 每次 Hook 变更 |
| Agents 无组件引用 | `grep -r "knowledge/\|skills/\|rules/\|hooks/" agents/` 应为空 | 每次 Agent 变更 |
| 跨 Skill procedures 引用 | `grep -rn "skills/pace-" skills/ --include="*-procedures*.md"` 应为空 | 每次 procedures 变更 |
| 分层完整性（全量） | `bash dev-scripts/validate-all.sh` | 每次提交前 |
| Schema 影响评估 | 新增字段后查 `_schema/README.md` fan-in 消费者 | 每次 Schema 变更 |
| Skill-Agent 路由匹配 | 新增 Skill 时确认 fork/inline 与职责域匹配 | 每次 Skill 新增 |
| Hook 状态感知 | 确认仅通过 stdin JSON / `.devpace/` 文件获取状态 | 每次 Hook 变更 |

## §1 核心架构原则

三大模式定义产品层组件如何协作，与 `info-architecture.md` 的 11 项组织原则互补——IA 原则回答"为什么这样组织信息"，本文件回答"组件之间如何协作"。

### 1. 六层信息栈（IA-1/IA-2 的运行时投影）

```
Layer 6: knowledge/theory      (Why  — 概念知识，被动加载，极少变更)
Layer 5: rules/               (Must — 行为约束，会话启动时自动加载)
Layer 4: knowledge/_schema/*/  (Shape — 数据格式契约，按需加载；分 entity/process/integration/auxiliary)
Layer 3: skills/*/SKILL.md    (What — 路由层，description 触发加载)
Layer 2: skills/*/*-procedures.md (How — 操作步骤，按状态/子命令条件加载)
Layer 1: knowledge/_templates/ (Instance — 具体实例，实例化时加载)
```

**依赖方向严格从下层指向上层**（权威定义见 `info-architecture.md` IA-1）——Layer 2 引用 Layer 4 合法；反向禁止。

**信息类型→资产映射**：

| 信息类型 | Plugin 资产 | 特征 |
|---------|------------|------|
| 步骤（Procedure） | `*-procedures.md` | 按步操作指令 |
| 约束（Principle） | `rules/*.md` | 行为规范 |
| 概念（Concept） | `knowledge/*.md` | 背景知识 |
| 结构（Structure） | `knowledge/_schema/*/*.md` | 数据格式定义（四子目录分组） |
| 路由（Process） | `SKILL.md` | 工作流分发 |
| 实例（Fact） | `knowledge/_templates/*.md` | 具体模板 |

### 2. 事件驱动守护（Hook 层独立性）

Hooks 通过 **stdin JSON + exit code + stdout** 与 Skill 层通信，**不解析 Markdown 文件引用**。Guard 通过 `.devpace/` 运行时文件感知状态。这保证 Hook 逻辑的可测试性和独立演进。

### 3. 契约协作（Schema 中介模式）

Skills 通过 **Schema + `.devpace/` 状态文件**间接协作，不直接引用对方 procedures。生产方和消费方都依赖契约，不依赖对方内部实现。

## §2 组件类型与依赖规则

### 六类组件职责边界

| 组件类型 | 职责 | 引用规则 |
|---------|------|---------|
| **rules/** | 行为约束，始终加载 | 可引用 knowledge/（Schema + root），不引用 Skill 实现 |
| **skills/SKILL.md** | 工作流路由（做什么） | 可引用 rules、knowledge 全域、同 Skill 的 procedures |
| **skills/procedures** | 操作步骤（怎么做） | 可引用 rules、knowledge 全域，不引用其他 Skill 的 procedures |
| **knowledge/_schema/** | 数据格式契约 | 仅引用同级 Schema（如 cr-format 引用 checks-format），不引用 Skill/Rules |
| **knowledge/ (root + _signals + _guides + _extraction)** | 领域知识 | 可引用同层 knowledge，不引用 Skill/Rules |
| **hooks/** | 质量守护（事件驱动） | 零 Markdown 引用（§1.2） |
| **agents/** | 角色人格定义 | 零外部引用（§0） |

### 禁止模式（附预防合理化）

| 禁止模式 | 常见借口 | 反驳 |
|---------|---------|------|
| Schema 引用 Skill procedures | "方便说明填充规则" | Schema 只定义格式和验证约束，填充规则属于 procedures |
| procedures 引用其他 Skill 的 procedures | "复用步骤" | 提取共享步骤到 `knowledge/_guides/`，让两个 Skill 各自引用 |
| Hooks 解析 Markdown 文件 | "需要读 CR 状态" | Hook 通过 `.devpace/state.md` 的 JSON/文本解析获取状态 |
| Agents 包含业务逻辑 | "Agent 需要知道流程" | 业务逻辑在 SKILL.md + procedures 中；Agent 只定义 persona |

## §3 数据流与通信模式

完整映射表 → `references/product-arch-details.md`（按需加载）。

### Skill-Agent 路由

- **fork**：需写入 `.devpace/` 或复杂多步操作——上下文隔离
- **inline**：查询型或轻量操作——避免子 agent 开销
- **鲁棒性**：fork 不可用时静默回退 inline（rules §13.5）
- 三角色：pace-engineer（工程）、pace-pm（产品）、pace-analyst（度量）
- 完整路由矩阵 → `references/product-arch-details.md` §A

### Hook 通信

事件 → stdin JSON → Hook 脚本 → exit 0（放行）| exit 2（阻断）→ stdout 反馈。
完整事件-Hook 映射 → `references/product-arch-details.md` §B

### Schema 依赖

高 fan-in Schema（变更前必查影响）：cr-format(10)、checks-format(4)、iteration-format(4)、insights-format(4)。
完整 Skill→Schema 矩阵 → `references/product-arch-details.md` §D

### 信号系统

三方同步：变更信号时 signal-priority + signal-collection + 消费 Skill 同步更新。
详见 `references/sync-checklists.md` + `references/product-arch-details.md` §E

## §4 合规检测

所有检查项（自动+手动）见 §0 合规检查清单。全量自动检测：`bash dev-scripts/validate-all.sh`。
