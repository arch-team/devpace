# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# devpace — 开发节奏管理器

> **devpace** 是一个 Claude Code 插件，为产品交付带来完整的 BizDevOps 研发节奏管理。它将"业务目标→产品功能→代码变更"串成一条可追溯的价值链，让业务方、产品、开发、测试、运维通过统一概念模型协作——Claude 不只是写代码的工具，而是理解业务意图的研发协作者。业务机会散落？AI 引导结构化梳理，对齐战略目标。会话中断？自动恢复上下文，无需重复解释。需求变更？即时评估影响范围，有序调整而非推倒重来。质量跑偏？内置门禁自动拦截，未就绪的变更无法流入下游。**需求永远在变，但从规划到交付的研发节奏，不应该因此失控。**

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
| 文件格式契约 | `knowledge/_schema/<subdir>/*.md` | state/project/CR 的字段定义（entity/process/integration/auxiliary 四组） |
| 度量指标定义 | `knowledge/metrics.md` | 指标名称、计算方式、用途 |
| Skill 评估工具 | `eval/` | eval-trigger/eval-fix/eval-regress 自动化管线 |

### 开发规范索引（.claude/rules/，自动加载）

| 规范文件 | 职责 |
|---------|------|
| `project-structure.md` | 项目目录结构、文件放置规则、配置文件索引；分层架构约束见本文件"分层架构"章节 |
| `common.md` | 响应语言、Git 提交规范、文档命名 |
| `dev-workflow.md` | 开发会话协议、任务执行、质量检查、跨会话连续性、文档级联 |
| `plugin-dev-spec.md` | Claude Code 核心组件规范（Plugin 结构、Skill 规范、常见陷阱；Agent/Hook/MCP 参考见 `references/component-reference.md`） |
| `info-architecture.md` | 信息架构元规则：IA-1 至 IA-11 索引（高冗余原则折叠为指针）、稳定性/分类/权威/预算/分级/职责的独有规则；完整原则见 `references/ia-principles.md` |
| `product-architecture.md` | 产品层组件架构：依赖矩阵、通信模式、合规检测（详细映射表见 `references/product-arch-details.md`） |

## 质量检查

质量检查流程详见 `dev-workflow.md` §4。补充提醒：修改 Skill 子命令、能力描述、信号定义或 Schema 时，查阅 `.claude/references/sync-checklists.md` 获取完整同步链路。
