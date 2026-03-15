---
description: Use when user says "业务机会", "专题", "Epic", "分解需求", "精炼", "细化", "补充需求", "战略对齐", "业务全景", "业务规划", "需求发现", "头脑风暴", "brainstorm", "导入需求", "从文档导入", "代码分析需求", "技术债务盘点", "discover", "import", "infer", "refine", "pace-biz", or wants to create opportunities/Epics, decompose/refine requirements, discover/import/infer features. NOT for implementation (/pace-dev), existing item changes (/pace-change), or iteration planning (/pace-plan).
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
| decompose | epics/EPIC-xxx.md 或 requirements/BR-xxx.md, project.md | project.md, epics/, requirements/ | biz-procedures-decompose.md |
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

### 空参数引导

当用户无参数调用 `/pace-biz` 时：

1. 读取 project.md 的 `mode` 字段判断模式
2. **完整模式**（默认）：
   - 扫描 opportunities.md 中 `评估中` 的 Opportunity 数量
   - 扫描 epics/ 中 `进行中` 和 `规划中` 的 Epic 数量
   - 扫描 project.md 树视图中未关联 Epic 的"孤立" BR 数量
   - 推荐优先级：未评估 Opportunity > 规划中 Epic 需分解 > 战略对齐
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

各子命令输出格式模板见 `biz-procedures-output.md`。
