# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# devpace — 开发节奏管理器

> **devpace** 是一个 Claude Code 插件，为 AI 辅助开发带来完整的 BizDevOps 研发节奏管理。它将"业务目标→产品功能→代码变更"串成一条可追溯的价值链，让 Claude 不只是写代码的工具，而是理解业务意图的研发协作者。会话中断？自动恢复上下文，无需重复解释。需求变更？即时评估影响范围，有序调整而非推倒重来。质量跑偏？内置门禁自动拦截，未就绪的变更无法流入下游。**需求永远在变，但从规划到交付的研发节奏，不应该因此失控。**

详见 [vision.md](../docs/design/vision.md)。

## 快速上手

1. 读 `docs/planning/progress.md` 定位当前任务
2. 遵循 `.claude/rules/dev-workflow.md` 的会话协议
3. 实现时参照下方"权威文件索引"表查找规范文件

## 分层架构（硬性要求）

devpace 分为两个独立层次，**产品层不得依赖开发层**：

| 层次 | 目录 | 职责 | 分发 |
|------|------|------|------|
| **开发层** | `.claude/`、`docs/` | 开发 devpace 本身的规范和设计文档 | 不分发 |
| **产品层** | `rules/`、`skills/`、`knowledge/`、`.claude-plugin/` | Plugin 运行时资产，分发给用户 | 随 Plugin 分发 |

**硬性约束**：

1. **产品层独立可分发**：`rules/`、`skills/`、`knowledge/`、`.claude-plugin/` 必须作为独立整体分发，不依赖 `.claude/` 和 `docs/` 中的任何文件
2. **禁止产品→开发引用**：产品层文件（rules/、skills/、knowledge/）中不得出现指向 `docs/` 或 `.claude/` 的路径引用
3. **开发→产品引用允许**：开发层文件（.claude/CLAUDE.md、docs/design.md 等）可以引用产品层文件
4. **共享知识归产品层**：如果一份内容同时被开发和产品使用（如 theory.md），它必须放在产品层（knowledge/），开发层引用它
5. **编辑范围严格分层**：修改产品层文件（`rules/`、`skills/`、`knowledge/`）时，不得将开发层文件（`docs/`、`.claude/`）纳入同一批次的编辑范围；反之亦然。跨层引用（如 `docs/features/` 引用 `skills/` 中的章节编号）在产品层变更后可能过时，但应在独立的开发层维护任务中处理，不可混入产品层变更

**检查方法**：`grep -r "docs/\|\.claude/" rules/ skills/ knowledge/` 应返回空结果。

## 开发守则

1. **概念模型始终完整**：Opportunity→Epic→BR→PF→CR 价值链从第一天就存在，不可省略任何环节。内容可为空但结构必须完整
2. **Markdown 是唯一格式**：消费者是 LLM + 人类，不使用 YAML/JSON 作为状态文件格式
3. **Schema 是契约**：`knowledge/_schema/` 中的格式定义是强约束，Skill 输出必须符合 Schema
4. **plugin.json 必须与文件系统同步**：新增/删除 Skill 后立即更新 `.claude-plugin/plugin.json`
5. **Rules 是分发规范，不是开发规范**：`rules/devpace-rules.md` 面向 Plugin 用户，开发规范在 `.claude/rules/`
6. **UX 优先**：零摩擦、渐进暴露、副产物非前置、容错恢复（设计原则见 `design.md §2`）
7. **理论对齐**：新增功能或调整概念模型时，对照 `knowledge/theory.md` 确保一致性
8. **规范优先，不猜测**：开发 Claude Code 组件时，必须遵循 `.claude/rules/plugin-dev-spec.md` 的规范。对不确定的 API、frontmatter 字段或机制行为，通过 `claude-code-guide` agent 或官方文档查证，禁止凭记忆猜测

## 会话协议

详见 `.claude/rules/dev-workflow.md`（自动加载）。

## 权威文件索引

| 概念 | 权威文件 | 权威范围 |
|------|---------|---------|
| 北极星、OBJ、MoS | `docs/design/vision.md` | 为什么做、做什么 |
| UX 原则（P1-P7） | `docs/design/design.md §2` | 设计约束 |
| 概念模型映射 | `docs/design/design.md §3` | 价值交付链路、闭环、渐进丰富 |
| 端到端工作流（Phase 0-5） | `docs/design/design.md §4` | 完整流程、Skill 映射 |
| CR 状态机 | `docs/design/design.md §5` | 状态、转换、门禁完整定义 |
| 质量门系统 | `docs/design/design.md §6` | Gate 1/2/3 定义 |
| 变更管理 | `docs/design/design.md §7` | 设计原则、四种场景、操作流程 |
| BizDevOps 理论 | `knowledge/theory.md` | 方法论参考（/pace-theory 运行时数据源） |
| 需求场景 S1-S42 | `docs/planning/requirements.md` | 验收标准 |
| 功能需求 F1-F12、非功能需求 NF1-NF11 | `docs/planning/requirements.md` | 特性规格与质量约束 |
| 战略规划 | `docs/planning/roadmap.md` | 阶段、里程碑、任务定义 |
| 操作跟踪 | `docs/planning/progress.md` | 当前任务状态、会话历史、变更记录 |
| 运行时行为规则 | `rules/devpace-rules.md` | 插件加载后 Claude 的行为 |
| 文件格式契约 | `knowledge/_schema/*.md` | state/project/CR 的字段定义 |
| 度量指标定义 | `knowledge/metrics.md` | 指标名称、计算方式、用途 |

### 开发规范索引（.claude/rules/，自动加载）

| 规范文件 | 职责 |
|---------|------|
| `common.md` | 响应语言、Git 提交规范、文档命名 |
| `dev-workflow.md` | 开发会话协议、任务执行、质量检查、跨会话连续性、文档级联 |
| `plugin-dev-spec.md` | Claude Code 核心组件规范（Plugin 结构、Skill 规范、常见陷阱；Agent/Hook/MCP 参考见 `references/component-reference.md`） |
| `info-architecture.md` | 信息架构（devpace 适配）：IA-1 至 IA-11 索引、六层架构映射、约束分级、分发层分离规则；完整原则见 `references/ia-principles.md` |

## 质量检查

- plugin.json 与文件系统同步（新增/删除 Skill 后立即更新）
- 每个 rules/ 和 _schema/ 文件有 §0 速查卡片
- 模板文件用 `{{PLACEHOLDER}}` 标记需填充的内容
- Skill 的 SKILL.md 遵循 `.claude/rules/plugin-dev-spec.md` 的 frontmatter 字段定义
- Skill 分拆模式：详见 `plugin-dev-spec.md` "分拆模式"章节。参考 pace-dev 和 pace-change
- **分层完整性**：产品层文件不得引用 `docs/` 或 `.claude/`（见分层架构章节）
- **多处出现内容的同步维护**：以下信息在多个文件中出现，修改时须全部同步（箭头表示权威方向：源→派生）：
  - accept 能力描述：`skills/pace-test/SKILL.md`（权威）→ `rules/devpace-rules.md §15`（教学派生）→ `docs/user-guide.md`（文档派生）
  - 子命令列表：各 `SKILL.md`（权威）→ `devpace-rules.md §0`（目录索引）→ `user-guide.md`（文档派生）→ `test-procedures.md 职责行`（测试派生）
  - 推荐使用流程：`SKILL.md`（权威）→ `user-guide.md`（文档派生）
  - 特性文档同步：各 `SKILL.md`（权威）→ `docs/features/<skill-name>.md`（文档派生）→ `docs/features/<skill-name>_zh.md`（翻译派生）
  - pace-next 信号摘要：`knowledge/signal-priority.md` + `knowledge/signal-collection.md`（权威）→ `skills/pace-next/SKILL.md` Step 2/3（内联摘要派生）→ `skills/pace-next/next-procedures-output-default.md`（命令引导派生）→ `docs/features/pace-next.md` + `pace-next_zh.md`（信号概览和示例派生）
  - Schema→脚本规则同步：`knowledge/_schema/*.md`（权威）→ `skills/pace-init/scripts/validate-schema.mjs` RULES 注册表（派生）→ `skills/pace-next/scripts/collect-signals.mjs` 信号条件（派生）→ `skills/pace-retro/scripts/compute-metrics.mjs` 指标公式（派生）
- **扩展清单**：新增角色或 pace-plan 子命令时，详见 `.claude/references/sync-checklists.md` 获取完整同步文件列表
