---
description: Use when user mentions 业务机会/专题/Epic/需求发现/需求梳理/功能规划/业务分析/分解需求/精炼/战略对齐/业务全景/backlog/brainstorm/导入需求/代码分析需求/技术债务/discover/import/infer/refine, or wants to create/decompose/discover requirements. NOT for /pace-dev, /pace-change, /pace-plan.
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[opportunity|epic|decompose|refine|align|view|discover|import|infer] [EPIC-xxx|BR-xxx|PF-xxx] <描述|路径>"
model: sonnet
context: fork
agent: pace-pm
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/skill/pace-biz-scope-check.mjs"
          timeout: 5
    - matcher:
        tool_name: "Write"
        path_pattern: "**/.devpace/epics/EPIC-*.md"
      hooks:
        - type: prompt
          prompt: "检查即将写入的 Epic 文件：1) OBJ 关联是否存在于 project.md？2) MoS 是否使用了可度量的表述（含目标数值或可验证条件）？如两项均合格回复 PASS。如有问题输出改进建议并阻断。"
          timeout: 15
---

# /pace-biz — 业务规划域统一入口

管理从业务机会到专题（Epic）到业务需求（BR）的上游价值链。覆盖 Opportunity 捕获、Epic 创建与管理、需求分解、战略对齐检查和业务全景展示。

## 与现有机制的关系

- `/pace-biz`：业务规划域（Opportunity→Epic→BR 的**创建和分解**）
- `/pace-change`：需求变更域（已有 BR/PF/Epic 的**变更**——add/pause/resume/modify）
- `/pace-plan`：迭代规划域（PF/CR 的**排期**）
- `/pace-init`：项目初始化（首次 Vision/Strategy/OBJ 引导）
- `/pace-init full`：**项目不存在时**，从 0 到 1 建立 .devpace/ + OBJ + 功能树 + 迭代计划（一站式初始化）
- `/pace-biz discover`：**项目已存在时**，从模糊想法探索新的 OPP→Epic→BR→PF（增量扩展）
- `/pace-status`：开发状态（CR/PF **开发进度**视图）
- 协同场景：`/pace-biz discover` 探索需求 → `decompose` 细化 → `/pace-dev` 开始开发
- 协同场景：`/pace-biz import` 导入文档需求 → `align` 检查对齐 → `/pace-plan` 排期
- 协同场景：`/pace-biz decompose` 分解出 BR → `/pace-change add` 快速补充 PF → `/pace-dev` 开始开发

## 推荐使用流程

```
完整业务路径：  opportunity → epic → decompose → /pace-dev
探索式发现：    discover → decompose → /pace-plan next
多源导入：      import <文档> → align → /pace-plan next
代码库推断：    infer → align → /pace-dev
战略对齐检查：  align（只读分析）
业务全景：      view（只读展示）
直接创建 Epic： epic（跳过 Opportunity）
日常需求注入：  /pace-change add（跳过 Opportunity/Epic，走快速路径）
```

## 输入

$ARGUMENTS：

### 子命令

**创建型**（产出新实体）：
- `opportunity <描述>` → 捕获业务机会到 opportunities.md
- `epic [OPP-xxx] <描述>` → 从 Opportunity 转化或直接创建 Epic
- `decompose <EPIC-xxx|BR-xxx>` → 分解 Epic→BR 或 BR→PF

**精炼型**（深化已有实体）：
- `refine <BR-xxx|PF-xxx>` → 交互式补充验收标准、边界条件、用户故事

**发现型**（探索和导入需求）：
- `discover <描述>` → 交互式需求发现，从模糊想法产出 OPP→Epic→BR→PF 候选树
- `import <路径>... [--threshold N]` → 从文档批量提取需求实体，合并到功能树（阈值默认 0.8）
- `infer` → 从代码库推断未追踪功能和技术债务

**分析型**（只读查看和检查）：
- `align` → 检查 OBJ→Epic→BR 战略对齐度，发现孤立实体
- `view` → 业务全景视图（OPP→EPIC→BR 流）

### 空参数

- （空）→ 智能引导——扫描项目上下文（未处理 Opportunity、活跃 Epic、孤立 BR），给出个性化推荐
  - **发现型推荐**（上下文感知）：扫描工作目录，根据项目状态推荐最合适的发现入口：
    - 检测到 `.md`/`.txt` 文档（会议纪要、PRD 等）→ 推荐 `import <文件>`
    - 检测到 `src/`、`lib/` 等代码目录 → 推荐 `infer`（代码推断）
    - 有活跃 Epic 但 BR 为空 → 推荐 `decompose <EPIC-xxx>`
    - 其他 → 推荐 `discover`（交互式探索）

## 执行路由表

| 子命令 | 读取 | 写入 | procedures 文件 |
|--------|------|------|----------------|
| opportunity | project.md, opportunities.md | opportunities.md | biz-procedures-opportunity.md |
| epic | opportunities.md, project.md | epics/EPIC-xxx.md, project.md, opportunities.md | biz-procedures-epic.md |
| decompose EPIC-xxx | epics/EPIC-xxx.md, project.md | project.md, epics/ | biz-procedures-decompose-epic.md |
| decompose BR-xxx | requirements/BR-xxx.md, project.md | project.md, requirements/ | biz-procedures-decompose-br.md |
| refine | project.md, requirements/BR-xxx.md | project.md, requirements/ | biz-procedures-refine.md |
| align | project.md, epics/, requirements/, opportunities.md, metrics/insights.md | metrics/insights.md（趋势数据） | biz-procedures-align.md |
| view | project.md, epics/, requirements/, opportunities.md | （只读） | biz-procedures-view.md |
| discover | state.md, project.md, opportunities.md | opportunities.md, epics/, project.md, scope-discovery.md | biz-procedures-discover.md |
| import | project.md, insights.md | project.md, epics/, requirements/ | biz-procedures-import.md |
| infer | project.md, src/ | project.md | biz-procedures-infer.md |
| （空参） | state.md, project.md, opportunities.md | （只读） | 内联智能引导 |

## 流程

### 所有子命令的公共前置

1. 读取 state.md 和 project.md 确认项目上下文
2. 确认 .devpace/ 已初始化（未初始化时引导 /pace-init）
3. 读取 project.md 配置 section 的 `mode` 字段（缺省 = 完整模式，`lite` = 轻量模式）
4. 读取 project.md 配置 section 的 `preferred-role` 字段（缺省 = Dev）。角色影响：输出措辞、追问方向、展示维度排序。参见各 procedures 文件中的"角色适配"段落
5. 按子命令路由到对应 procedures 文件（各 procedure 内部根据 mode 和 role 调整行为）

### lite 模式子命令可用性

| 子命令 | lite 模式行为 |
|--------|-------------|
| opportunity / epic | 不可用（提示升级到完整模式或 /pace-change add） |
| decompose EPIC-xxx | 不可用（lite 无 Epic/BR 层） |
| decompose BR-xxx | 不可用（lite 无 BR 层） |
| refine | 仅支持 PF（BR-xxx 参数终止） |
| align | 简化为 OBJ→PF→CR 链路检查 |
| view | 简化为 OBJ→PF→CR 树视图 |
| discover / import / infer | 可用（映射目标简化为 PF） |

### 空参数引导

当用户无参数调用 `/pace-biz` 时：

1. 读取 project.md 的 `mode` 字段判断模式
2. **完整模式**（默认）：
   - 扫描 opportunities.md 中 `评估中` 的 Opportunity 数量
   - 扫描 epics/ 中 `进行中` 和 `规划中` 的 Epic 数量
   - 扫描 project.md 树视图中未关联 Epic 的"孤立" BR 数量
   - **阶段判断**（内部逻辑，用于选择推荐策略，不直接输出阶段名称给用户）：
     - 无 OPP 且无 Epic/BR → **Sense 阶段**（需求感知期）→ 侧重发现型推荐
     - 有 OPP 未转化 或 有活跃 discover 会话 → **Ideate 阶段**（构思期）→ 侧重转化和探索
     - 有 Epic 未分解 或 有 BR 未分解出 PF → **Structure 阶段**（结构化期）→ 侧重 decompose
     - 有 BR/PF 平均就绪度 < 60% → **Refine 阶段**（精炼期）→ 侧重 refine
     - 距上次 align > 5 天 或 从未执行 → **Validate 阶段**（验证期）→ 侧重 align
     - 大部分 BR/PF 就绪度 >= 80% → **Ready 阶段**→ 推荐移交 /pace-dev
     - 多阶段条件同时满足时，按上述顺序取最早未完成的阶段
   - 推荐优先级（生命周期感知）：
     1. 未评估 Opportunity → `opportunity` 或 `epic`
     2. 规划中 Epic 需分解 → `decompose`
     3. BR/PF 平均就绪度 < 60%（扫描功能树实体的描述/验收标准丰富度）→ `refine` Top-3 最需精炼项
     4. 距上次 align 超过 5 天或从未执行 → `align`
     5. 以上均不满足 → 上下文发现型推荐（import/infer/discover）
   - 附完整子命令列表
3. **lite 模式**：
   - 扫描 project.md 树视图中 OBJ 下的 PF 数量和状态
   - **上下文感知推荐**：同完整模式的发现型推荐逻辑——检测 .md 文件推荐 import、检测 src/ 推荐 infer、其他推荐 discover
   - 隐藏 opportunity/epic/decompose（Epic→BR 路径），仅展示 lite 兼容子命令
   - 提示：如需 OPP/Epic/BR 能力，可通过 `/pace-init --upgrade-mode` 升级到完整模式

## 输出

- **渐进暴露**：默认输出简洁摘要，`--detail` 展示完整信息
- **操作确认**：写入操作前展示变更预览，用户确认后执行
- **追溯链**：每次创建实体时展示其在价值链中的位置

### 各子命令输出格式索引

> 权威模板在各 procedures 文件中。

| 子命令 | 输出摘要 | 权威源 |
|--------|---------|--------|
| opportunity | 已捕获业务机会：OPP-xxx -- [描述]，状态：评估中 | biz-procedures-opportunity.md Step 4 |
| epic | 已创建专题：EPIC-xxx -- [名称]，关联 OBJ + MoS | biz-procedures-epic.md Step 8 |
| decompose (Epic) | 已分解 EPIC-xxx：BR 列表 + 依赖关系 + 价值链 | biz-procedures-decompose-epic.md Step 6 |
| decompose (BR) | 已分解 BR-xxx：PF 列表 + 优先级 + 价值链 | biz-procedures-decompose-br.md Step 6 |
| refine | 已精炼 [BR/PF]：变更摘要 + 就绪度变化 | biz-procedures-refine.md Step 4 |
| align | 战略对齐度报告：覆盖率 + 孤立实体 + 就绪度 + 趋势 | biz-procedures-align.md Step 3 |
| view | 业务全景：OPP->EPIC->BR->PF->CR 树视图 + 统计 | biz-procedures-view.md Step 2 |
| discover | 已从发现会话创建：OPP + Epic + BR + PF 汇总 | biz-procedures-discover.md Step 6 |
| import | 导入完成：新增 + 丰富 + 跳过 汇总 | biz-procedures-import.md Step 6 |
| infer | 代码库推断完成：追踪 + 技术债务 + 未实现 汇总 | biz-procedures-infer.md Step 6 |
