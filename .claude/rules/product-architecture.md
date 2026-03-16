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

### 组件选择决策树

```
新功能需求
├─ 定义行为约束？ → rules/devpace-rules.md（§N 新增）
├─ 定义工作流程？
│  ├─ 需要专属 Agent？ → skills/pace-xxx/（context: fork）
│  └─ 轻量操作？ → skills/pace-xxx/（inline）
├─ 定义数据格式？ → knowledge/_schema/<subdir>/
├─ 定义信号路由？ → knowledge/_signals/
├─ 定义操作指南？ → knowledge/_guides/
├─ 守护质量门禁？ → hooks/（Gate 3 = Hook 阻断）
└─ 定义角色人格？ → agents/pace-xxx.md
```

### 合规检查清单

| 检查项 | 命令 / 方法 | 频率 |
|--------|------------|------|
| Schema 无反向引用 | `grep -r "skills/\|rules/" knowledge/_schema/` 应为空 | 每次 Schema 变更 |
| Hooks 无 Markdown 引用 | `grep -r "knowledge/\|skills/\|rules/" hooks/` 应为空 | 每次 Hook 变更 |
| Agents 无组件引用 | `grep -r "knowledge/\|skills/\|rules/\|hooks/" agents/` 应为空 | 每次 Agent 变更 |
| 分层完整性（全量） | `bash dev-scripts/validate-all.sh` | 每次提交前 |

## §1 核心架构原则

三大模式定义产品层组件如何协作，与 `info-architecture.md` 的 11 项组织原则互补——IA 原则回答"为什么这样组织信息"，本文件回答"组件之间如何协作"。

### 1. 六层信息栈（IA-1/IA-2 的运行时投影）

六层架构定义见 `references/plugin-info-layers.md`。**依赖方向严格从下层指向上层**（权威定义见 `info-architecture.md` §1）——Layer 2 (procedures) 引用 Layer 4 (schema) 合法；反向禁止。

### 2. 事件驱动守护（Hook 层独立性）

Hooks 通过 **stdin JSON + exit code + stdout** 与 Skill 层通信，**不解析 Markdown 文件引用**。Guard 通过 `.devpace/` 运行时文件感知状态。这保证 Hook 逻辑的可测试性和独立演进。

### 3. 契约协作（Schema 中介模式）

Skills 通过 **Schema + `.devpace/` 状态文件**间接协作，不直接引用对方 procedures。契约交互模型详见 `info-architecture.md` §10。

## §2 组件类型与依赖规则

### 六类组件职责边界

| 组件类型 | 职责 | 引用规则 |
|---------|------|---------|
| **rules/** | 行为约束，始终加载 | 可引用 knowledge/（Schema + root），不引用 Skill 实现 |
| **skills/SKILL.md** | 工作流路由（做什么） | 可引用 rules、knowledge 全域、同 Skill 的 procedures |
| **skills/procedures** | 操作步骤（怎么做） | 可引用 rules、knowledge 全域，不引用其他 Skill 的 procedures |
| **knowledge/_schema/** | 数据格式契约 | 仅引用同级 Schema（如 cr-format 引用 checks-format），不引用 Skill/Rules |
| **knowledge/ (root + _signals + _guides + _extraction)** | 领域知识 | 可引用同层 knowledge，不引用 Skill/Rules |
| **hooks/** | 质量守护（事件驱动） | 零 Markdown 引用——通过 stdin JSON + `.devpace/` 文件感知状态 |
| **agents/** | 角色人格定义 | 零外部引用——仅定义 persona + tools + model |

### 禁止模式（附预防合理化）

| 禁止模式 | 常见借口 | 反驳 |
|---------|---------|------|
| Schema 引用 Skill procedures | "方便说明填充规则" | Schema 只定义格式和验证约束，填充规则属于 procedures |
| procedures 引用其他 Skill 的 procedures | "复用步骤" | 提取共享步骤到 `knowledge/_guides/`，让两个 Skill 各自引用 |
| Hooks 解析 Markdown 文件 | "需要读 CR 状态" | Hook 通过 `.devpace/state.md` 的 JSON/文本解析获取状态 |
| Agents 包含业务逻辑 | "Agent 需要知道流程" | 业务逻辑在 SKILL.md + procedures 中；Agent 只定义 persona |

## §3 数据流与通信模式

### Skill-Agent 路由矩阵

| Agent | 路由 Skills (fork) | 职责域 |
|-------|-------------------|--------|
| pace-engineer | pace-dev, pace-review, pace-test, pace-feedback, pace-release | 工程执行 |
| pace-pm | pace-change, pace-plan, pace-biz | 产品规划 |
| pace-analyst | pace-retro, pace-guard, pace-pulse, pace-next, pace-status | 度量分析 + 信号导航 |
| _(inline)_ | pace-init, pace-learn, pace-theory, pace-role, pace-trace, pace-sync | 轻量操作 |

### Schema Fan-in（高 fan-in = 高稳定性要求）

| Schema 文件 | Fan-in | 稳定性要求 |
|------------|--------|-----------|
| cr-format.md | 10 | 极高——变更需评估 5+ Skill 影响 |
| checks-format.md | 4 | 高 |
| iteration-format.md | 4 | 高 |
| insights-format.md | 4 | 高 |
| sync-mapping-format.md | 4 | 高 |
| integrations-format.md | 3 | 中 |
| test-baseline-format.md | 3 | 中 |

完整依赖矩阵、Hook 映射表、Agent 协作模型 → `references/architecture-details.md`（按需加载）。

## §4 合规检测

### 自动化检测（完整检查表，整合自 CLAUDE.md 和 info-architecture.md）

```bash
# Schema 纯净性（零反向引用）
grep -r "skills/\|rules/" knowledge/_schema/

# Hook 独立性（零 Markdown 引用）
grep -r "knowledge/\|skills/\|rules/" hooks/ --include="*.mjs" --include="*.sh"

# Agent 纯净性（零外部引用）
grep -r "knowledge/\|skills/\|rules/\|hooks/" agents/

# 跨 Skill procedures 引用（应为空）
grep -rn "skills/pace-" skills/ --include="*-procedures*.md" | grep -v "自身目录"

# 全量检测
bash dev-scripts/validate-all.sh
```

### 手动检查

- [ ] 新增 Schema 字段后，检查 fan-in 消费者（查 `_schema/README.md`）是否需要适配
- [ ] 新增 Skill 时，确认 Agent 路由（fork vs inline）与职责域匹配
- [ ] Hook 逻辑变更后，确认仅通过 stdin JSON / `.devpace/` 文件获取状态
