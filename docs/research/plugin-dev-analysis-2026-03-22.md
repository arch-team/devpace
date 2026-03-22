# plugin-dev 插件分析报告

> 日期：2026-03-22 | 分析范围：plugin-dev 插件功能特性、与 devpace 架构对比、Skill 分拆模式

---

## Part 1: plugin-dev 插件概览

### 基本信息

- **名称**：plugin-dev
- **作者**：Anthropic 官方（Daisy Hollman）
- **来源**：`claude-plugins-official` marketplace
- **版本**：0.1.0
- **定位**：Claude Code 插件开发的端到端专家级工具包

### 应用场景

| 场景 | 说明 |
|------|------|
| **从零创建插件** | 通过 `/plugin-dev:create-plugin` 8 阶段引导式工作流，从概念到成品 |
| **给已有插件添加组件** | 为现有插件增加 Hook、Agent、Skill、MCP 集成等 |
| **学习插件开发规范** | 了解 plugin.json 格式、目录结构、frontmatter 字段等 |
| **集成外部服务** | 通过 MCP 协议连接数据库、API、第三方工具 |
| **事件驱动自动化** | 创建 Hook 实现文件写入校验、安全策略执行、会话管理等 |
| **插件质量审查** | 使用内置 Agent 对插件结构、Skill 质量进行自动化验证 |

### 7 个 Skill（知识模块）

| Skill | 触发关键词 | 核心能力 |
|-------|-----------|---------|
| **plugin-structure** | "plugin 结构"、"plugin.json"、"目录布局" | 目录规范、manifest 配置、auto-discovery 机制、命名约定 |
| **hook-development** | "创建 Hook"、"PreToolUse"、"验证工具使用" | Prompt-based hooks、9 种事件类型、`${CLAUDE_PLUGIN_ROOT}` 便携路径 |
| **mcp-integration** | "MCP server"、"外部服务集成" | stdio/SSE/HTTP/WebSocket 四种 server 类型、OAuth 认证、.mcp.json 配置 |
| **command-development** | "创建斜杠命令"、"command frontmatter" | 命令 Markdown 格式、YAML frontmatter、动态参数、Bash 执行 |
| **agent-development** | "创建 Agent"、"子代理" | Agent frontmatter、description 设计、system prompt 模式、AI 辅助生成 |
| **skill-development** | "创建 Skill"、"改进 description" | SKILL.md 结构、渐进暴露原则、强触发描述编写 |
| **plugin-settings** | "插件配置"、".local.md" | `.claude/plugin-name.local.md` 配置模式、YAML frontmatter 解析 |

### 3 个 Agent（自动化代理）

| Agent | 触发方式 | 能力 |
|-------|---------|------|
| **plugin-validator** | 插件创建/修改后主动触发，或用户说"验证插件" | 全面检查 manifest、结构、命名、组件、安全性 |
| **skill-reviewer** | Skill 创建后主动触发，或用户说"审查 skill" | 检查 description 质量、渐进暴露、写作风格 |
| **agent-creator** | 用户说"创建 agent" | AI 辅助生成 Agent 定义——identifier、whenToUse、systemPrompt |

### 1 个 Command（引导式工作流）

**`/plugin-dev:create-plugin`** — 8 阶段端到端插件创建：

```
Discovery -> Component Planning -> Detailed Design -> Structure Creation
    -> Component Implementation -> Validation -> Testing -> Documentation
```

每个阶段都会交互式提问、加载对应 Skill、调用专业 Agent，确保高质量输出。

### 资源体量

| 类别 | 数量 |
|------|------|
| 核心 SKILL.md | 7 个（约 11,065 词） |
| 参考文档 | 10,000+ 词的详细指南 |
| 工作示例 | 12+ 个（Hook 脚本、MCP 配置、插件布局、设置文件） |
| 工具脚本 | 6 个（validate-hook-schema.sh、test-hook.sh、hook-linter.sh、validate-agent.sh、validate-settings.sh、parse-frontmatter.sh） |

### 设计特点

1. **渐进暴露（Progressive Disclosure）**：metadata -> SKILL.md -> references/examples 三层加载，节省上下文
2. **自身即范例**：plugin-dev 自身就是用最佳实践构建的插件，可作为模板参考
3. **安全优先**：强调输入验证、HTTPS、环境变量管理、最小权限
4. **便携性**：全面使用 `${CLAUDE_PLUGIN_ROOT}` 避免硬编码路径

---

## Part 2: plugin-dev 规范 vs devpace 架构对比

### 整体规模对比

| 维度 | plugin-dev | devpace |
|------|-----------|---------|
| **定位** | 通用工具包插件（教你做插件） | 领域专业插件（BizDevOps 管理器） |
| **Skills** | 7 个 | **20 个** |
| **Agents** | 3 个 | 3 个 |
| **Commands** | 1 个（create-plugin） | 0 个（全部用 Skill 替代） |
| **Hooks** | 0 个 | **13 个**（.mjs + .sh） |
| **Knowledge** | 分散在各 Skill 的 references/ | **独立知识层**（约 40 个文件） |
| **Rules** | 无 | 1 个始终加载文件（580 行） |
| **Output Styles** | 无 | 1 个 |
| **总规模** | 约 11K 词核心 + 10K 词参考 | **约 181 文件 / 约 21,573 行** |

### 目录结构对比

```
plugin-dev/（通用规范结构）          devpace/（领域深耕结构）
+-- .claude-plugin/                  +-- .claude-plugin/
|   +-- plugin.json                  |   +-- plugin.json
|                                    |   +-- marketplace.json
+-- commands/                        |   （无 commands/——全用 skills/）
|   +-- create-plugin.md             |
+-- agents/                          +-- agents/
|   +-- agent-creator.md             |   +-- pace-engineer.md
|   +-- skill-reviewer.md            |   +-- pace-pm.md
|   +-- plugin-validator.md          |   +-- pace-analyst.md
+-- skills/                          +-- skills/
|   +-- hook-development/            |   +-- pace-dev/
|   |   +-- SKILL.md                 |   |   +-- SKILL.md          <- 路由层
|   |   +-- references/              |   |   +-- dev-procedures-*.md <- 步骤层（6个）
|   |   +-- examples/                |   +-- pace-change/
|   |   +-- scripts/                 |   +-- ... (20 个 Skill 目录)
|                                    +-- knowledge/               <- 独立知识层
|   （知识分散在各 skill 内部）         |   +-- _schema/
|                                    |   |   +-- entity/  (8 个 Schema)
|                                    |   |   +-- process/ (7 个 Schema)
|                                    |   |   +-- integration/ (2)
|                                    |   |   +-- auxiliary/ (7)
|                                    |   +-- _signals/  (2)
|                                    |   +-- _guides/   (6)
|                                    |   +-- _extraction/ (2)
|                                    |   +-- *.md (theory/metrics/roles)
|                                    +-- hooks/                <- 事件守护层
|                                    |   +-- hooks.json
|                                    |   +-- lib/
|                                    |   +-- skill/
|                                    |   +-- *.mjs / *.sh (13 个)
|                                    +-- rules/
|                                    |   +-- devpace-rules.md  <- 始终加载
|                                    +-- output-styles/
|                                    +-- settings.json
```

### 核心架构差异

#### 1. Skill 内部结构：平铺 vs 分拆

| 模式 | plugin-dev | devpace |
|------|-----------|---------|
| **组织方式** | SKILL.md 单体 + references/examples/scripts | SKILL.md（路由）+ `*-procedures.md`（步骤） |
| **分拆阈值** | 无明确规则 | 详细步骤超约 50 行即拆出 procedures |
| **加载策略** | 触发后全量加载 SKILL.md | SKILL.md 先加载做路由，procedures 按状态/子命令条件加载 |
| **典型规模** | 约 1,500 词/Skill | SKILL.md 约 200 行 + procedures 合计约 500-800 行 |

#### 2. 知识管理：内聚 vs 中央集权

| 维度 | plugin-dev | devpace |
|------|-----------|---------|
| **知识存放** | 各 Skill 内部的 `references/` | 独立 `knowledge/` 目录 |
| **共享方式** | Skill 之间无共享机制 | Schema 中介模式——Skill A 写 `.devpace/` 文件，Skill B 读取 |
| **契约层** | 无 | `_schema/` 24 个 Schema（四子目录：entity/process/integration/auxiliary） |
| **信号系统** | 无 | `_signals/` 定义信号优先级和采集规程 |

devpace 独有的六层信息栈：

```
L6: knowledge/ root (Why)  -> 概念知识，被动加载
L5: rules/      (Must)     -> 行为约束，始终加载
L4: _schema/    (Shape)    -> 数据格式契约，按需加载
L3: SKILL.md    (What)     -> 路由层，description 触发
L2: procedures  (How)      -> 操作步骤，条件加载
L1: _templates/ (Instance) -> 具体实例
```

#### 3. Hook 使用：零 vs 重度

| 维度 | plugin-dev | devpace |
|------|-----------|---------|
| **Hook 数量** | 0（但教你怎么写） | 13 个生产级 Hook |
| **覆盖事件** | — | PreToolUse、PostToolUse、Stop、SubagentStop、SessionStart、SessionEnd、PreCompact、UserPromptSubmit |
| **实现语言** | 推荐 bash | `.mjs`（Node.js）为主 + `.sh` 辅助 |
| **共享库** | 无 | `hooks/lib/` 公共库 + `hooks/skill/` Skill 域 Hook |
| **状态感知** | — | 通过 `.devpace/` + stdin JSON，不解析 Markdown |

#### 4. Agent 设计哲学

| 维度 | plugin-dev | devpace |
|------|-----------|---------|
| **Agent 职责** | 工具型（validator、reviewer、creator） | **角色型**（engineer、pm、analyst） |
| **触发方式** | 主要用户显式调用或 proactive | Skill 通过 fork/inline 路由 |
| **业务逻辑** | Agent 内含逻辑 | Agent 纯人格定义（零业务逻辑，逻辑在 Skill+procedures 中） |

#### 5. 组件依赖治理

| 维度 | plugin-dev | devpace |
|------|-----------|---------|
| **依赖规则** | 隐式，由开发者自行管理 | **显式依赖矩阵**（product-architecture.md） |
| **禁止模式** | 无 | 5 类禁止模式 + 预防合理化清单 |
| **合规检测** | plugin-validator Agent 手动检查 | `validate-all.sh` 自动化 + 10+ grep 检查命令 |

### devpace 超越 plugin-dev 规范的地方

| 领域 | devpace 的扩展 |
|------|---------------|
| **产品/开发分层** | 独创的二层架构——产品层独立可分发，开发层不随插件分发 |
| **Schema 契约层** | 4 类 24 个 Schema 定义所有 `.devpace/` 状态文件的格式 |
| **信号路由系统** | `_signals/` 定义跨 Skill 的优先级排序和信息采集规程 |
| **Harness Engineering** | HE-1 到 HE-6 原则——将"Agent 行为优化"编码为工程实践 |
| **信息架构规则** | IA-1 到 IA-11 原则——系统化的信息组织方法论 |
| **Eval 体系** | `eval/` 目录提供 Skill 评估自动化管线 |
| **output-styles/** | 可切换的输出风格 |
| **settings.json** | 插件级默认配置 |

### devpace 遵循 plugin-dev 规范的地方

| 规范项 | 合规状态 |
|--------|---------|
| `.claude-plugin/plugin.json` manifest | 完全合规 |
| kebab-case 命名 | 完全合规 |
| `skills/` 子目录 + SKILL.md | 完全合规 |
| `agents/` 目录 `.md` 文件 | 完全合规 |
| `hooks/hooks.json` 配置 | 完全合规 |
| description 使用 "Use when" 触发 | 完全合规 |
| 组件不放 `.claude-plugin/` | 完全合规 |
| `${CLAUDE_PLUGIN_ROOT}` 便携路径 | Hooks 中使用 |
| 无 `commands/` 目录 | 采用更现代的纯 Skill 模式 |

---

## Part 3: Skill 分拆模式详解

### 两种模式一览

#### plugin-dev 模式（平铺）

```
skills/hook-development/
+-- SKILL.md              <- 单体文件（约 700 行，所有知识）
+-- references/           <- 辅助参考（patterns.md, migration.md, advanced.md）
+-- examples/             <- 工作示例（validate-write.sh, load-context.sh）
+-- scripts/              <- 工具脚本（validate-hook-schema.sh, test-hook.sh）
```

SKILL.md = 路由 + 知识 + 步骤一体化

#### devpace 模式（分拆）

```
skills/pace-dev/
+-- SKILL.md                        <- 路由层（约 113 行，只做分发）
+-- dev-procedures-common.md        <- 通用规程（始终加载）
+-- dev-procedures-intent.md        <- 意图检查点（CR=created 时加载）
+-- dev-procedures-developing.md    <- 推进中规程（CR=developing 时加载）
+-- dev-procedures-gate.md          <- 门禁反思（CR=verifying/in_review 时加载）
+-- dev-procedures-postmerge.md     <- 合并后规程（CR=merged 时加载）
+-- dev-procedures-defect.md        <- 缺陷处理（CR type=defect 时追加加载）

skills/pace-change/
+-- SKILL.md                        <- 路由层
+-- change-procedures-common.md     <- 通用规程
+-- change-procedures-triage.md     <- 变更分诊
+-- change-procedures-impact.md     <- 影响分析
+-- change-procedures-apply.md      <- 应用变更
+-- change-procedures-types.md      <- 变更类型定义
+-- change-procedures-undo.md       <- 撤销操作
+-- change-procedures-risk.md       <- 风险评估
+-- change-procedures-batch.md      <- 批量变更
+-- change-procedures-history.md    <- 历史查询
+-- change-procedures-degraded.md   <- 降级模式
+-- change-procedures-execution.md  <- 执行引擎
```

SKILL.md = 纯路由，procedures = 按条件加载的步骤

### SKILL.md 结构对比

#### plugin-dev: hook-development/SKILL.md（约 700 行）

```
---
name: hook-development
description: This skill should be used when...
---
# Hook Development for Claude Code Plugins
## Overview               <- 概述
## Hook Types             <- 分类知识
## Hook Configuration     <- 配置知识
## Hook Events            <- 9 种事件的完整 API
  ### PreToolUse          <- 每个事件的输入/输出/示例
  ### PostToolUse / Stop / SessionStart / ...
## Hook Output Format     <- 输出格式
## Hook Input Format      <- 输入格式
## Environment Variables  <- 环境变量
## Matchers               <- 匹配器
## Security Practices     <- 安全实践
## Performance            <- 性能考虑
## Debugging              <- 调试方法
## Quick Reference        <- 速查表
## Additional Resources   <- 指向 references/ 和 examples/
```

特点：All-in-one。触发后全量加载约 700 行。

#### devpace: pace-dev/SKILL.md（约 113 行）

```
---
description: Use when user says "开始做"...
context: fork              <- fork 到 pace-engineer Agent
agent: pace-engineer
hooks:                     <- Skill 级 Hook
  PreToolUse: ...
---
# /pace-dev -- 推进变更请求

## 输入                   <- 参数定义 + 路由规则
## 执行路由               <- 条件加载表（核心！）
  | CR 状态 | 加载文件 | 说明 |
  | created | dev-procedures-intent.md | ... |
  | developing | dev-procedures-developing.md | ... |
## 流程                   <- 高层 4 步骤
## 输出                   <- 输出格式
```

特点：纯路由器。不包含任何具体步骤。

### 加载策略对比

#### plugin-dev: 触发后全量加载

```
用户意图匹配 description
        |
   加载 SKILL.md（全量约 700 行）
        |
   LLM 从中找到相关段落执行
        |
   （需要时）读取 references/ 补充
```

#### devpace: 触发后路由加载

```
用户意图匹配 description
        |
   加载 SKILL.md（约 113 行路由表）
        |
   读取 CR 当前状态（如 status=created）
        |
   按路由表加载对应 procedures（约 150-270 行）
   + 固定加载 common procedures（约 142 行）
        |
   LLM 按 procedures 步骤执行
```

### 量化对比

| 指标 | plugin-dev (hook-dev) | devpace (pace-dev) |
|------|----------------------|-------------------|
| SKILL.md 行数 | 约 700 行 | 约 113 行 |
| 总 procedures 行数 | -- | 约 1,100 行（6 个文件） |
| 单次加载行数 | 约 700 行（全量） | 约 400-525 行（路由+common+条件） |
| 上下文节省率 | 0%（无条件加载） | **约 52%**（只加载相关状态） |
| 最差情况 | 约 700 行 | 约 525 行（L/XL + defect） |

### 分拆的设计逻辑

#### 为什么 devpace 需要分拆？

1. **状态驱动的差异化行为**：pace-dev 在 CR 的不同状态下做完全不同的事——created 时做意图检查+复杂度评估，developing 时做漂移检测+步骤隔离，merged 时做功能发现。混在一起会导致 LLM **步骤泄漏**（在 developing 阶段执行了 created 阶段的逻辑）。

2. **上下文窗口紧张**：devpace 有 20 个 Skill + rules（580 行始终加载）+ knowledge，每减少一行浪费都有价值。

3. **变更频率不同**：intent procedures 频繁迭代（复杂度评估规则），但 common 和 gate procedures 相对稳定。分拆后**变更隔离**——改 intent 不需要读整个 pace-dev。

#### 为什么 plugin-dev 不需要分拆？

1. **无状态差异**：hook-development 的知识是**参考型**——不论用户处于什么状态，都可能需要任何一部分知识。
2. **规模可控**：约 700 行在可接受范围内。
3. **低耦合**：各 Skill 独立，没有共享 Schema 或状态文件。

### 分拆模式的关键设计规则

devpace 的 `plugin-spec.md` 定义了分拆阈值和规范：

| 规则 | 说明 |
|------|------|
| **分拆阈值** | 详细步骤超约 50 行即从 SKILL.md 拆出 procedures |
| **SKILL.md 放什么** | "做什么"——输入/输出/路由表 |
| **procedures 放什么** | "怎么做"——具体操作步骤 |
| **命名规范** | `<skill-name>-procedures-<aspect>.md` |
| **引用规则** | SKILL.md 可引用同 Skill 的 procedures；procedures 不引用其他 Skill 的 procedures |
| **共享步骤** | 提取到 `knowledge/_guides/`，让多个 Skill 各自引用 |

### Anti-pattern：步骤泄漏

```
错误：SKILL.md 包含所有状态的详细步骤
   -> LLM 在 developing 阶段看到 intent 检查步骤
   -> 可能重复执行意图检查（已在 created 阶段完成）

正确：SKILL.md 只有路由表，按状态加载对应 procedures
   -> LLM 在 developing 阶段只看到 developing 的步骤
   -> 不可能误执行其他阶段的逻辑
```

### 何时选择哪种模式

| 选择条件 | 平铺模式（plugin-dev） | 分拆模式（devpace） |
|---------|----------------------|-------------------|
| Skill 类型 | 参考型知识 / 工具型 | 状态驱动的工作流 |
| 内容规模 | < 500 行 | > 500 行或有多个执行路径 |
| 状态差异 | 无/弱 | 强（不同状态=完全不同步骤） |
| 上下文预算 | 宽裕 | 紧张（大型插件） |
| 变更频率 | 均匀 | 不同部分变更频率差异大 |
| 步骤泄漏风险 | 低 | 高（复杂状态机） |

---

## 总结

```
plugin-dev = Claude Code 插件的"通用教科书"
devpace   = 将教科书内化后，按领域需求大幅扩展的"毕业设计"
```

plugin-dev 定义了**平台层的结构规范**（manifest、目录、命名、组件类型），devpace 完全遵循这些基础规范，然后在其上构建了**领域层的信息架构**（六层信息栈、Schema 契约、信号路由、依赖矩阵、Harness Engineering 原则）。

两种 Skill 组织模式各有适用场景：plugin-dev 的平铺模式是 Skill 的默认最佳实践；devpace 的分拆模式是大型领域插件应对复杂状态驱动工作流的进阶演进。
