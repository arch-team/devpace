---
description: Use when user discusses business opportunities, wants to create or manage Epics, decompose requirements, check strategic alignment, or says "业务机会", "专题", "Epic", "分解需求", "战略对齐", "业务全景", "机会", "商业洞察", "业务规划", "pace-biz". NOT for code implementation (use /pace-dev), NOT for requirement changes on existing items (use /pace-change), NOT for iteration planning (use /pace-plan).
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash, Grep
argument-hint: "[opportunity|epic|decompose|align|view] [EPIC-xxx|BR-xxx] <描述>"
context: fork
agent: pace-pm
---

# /pace-biz — 业务规划域统一入口

管理从业务机会到专题（Epic）到业务需求（BR）的上游价值链。覆盖 Opportunity 捕获、Epic 创建与管理、需求分解、战略对齐检查和业务全景展示。

## 与现有机制的关系

- `/pace-biz`：业务规划域（Opportunity→Epic→BR 的**创建和分解**）
- `/pace-change`：需求变更域（已有 BR/PF/Epic 的**变更**——add/pause/resume/modify）
- `/pace-plan`：迭代规划域（PF/CR 的**排期**）
- `/pace-init`：项目初始化（首次 Vision/Strategy/OBJ 引导）
- `/pace-status`：开发状态（CR/PF **开发进度**视图）
- 协同场景：`/pace-biz decompose` 分解出 BR → `/pace-change add` 快速补充 PF → `/pace-dev` 开始开发

## 推荐使用流程

```
完整业务路径：  opportunity → epic → decompose → /pace-dev
战略对齐检查：  align（只读分析）
业务全景：      view（只读展示）
直接创建 Epic： epic（跳过 Opportunity）
日常需求注入：  /pace-change add（跳过 Opportunity/Epic，走快速路径）
```

## 输入

$ARGUMENTS：

### 子命令

- `opportunity <描述>` → 捕获业务机会到 opportunities.md
- `epic [OPP-xxx] <描述>` → 从 Opportunity 转化或直接创建 Epic
- `decompose <EPIC-xxx|BR-xxx>` → 分解 Epic→BR 或 BR→PF
- `align` → 检查 OBJ→Epic→BR 战略对齐度，发现孤立实体
- `view` → 业务全景视图（OPP→EPIC→BR 流）

### 空参数

- （空）→ 智能引导——扫描项目上下文（未处理 Opportunity、活跃 Epic、孤立 BR），给出个性化推荐

## 执行路由表

| 子命令 | 读取 | 写入 | procedures 文件 |
|--------|------|------|----------------|
| opportunity | project.md, opportunities.md | opportunities.md | biz-procedures-opportunity.md |
| epic | opportunities.md, project.md | epics/EPIC-xxx.md, project.md, opportunities.md | biz-procedures-epic.md |
| decompose | epics/EPIC-xxx.md 或 requirements/BR-xxx.md, project.md | project.md, epics/, requirements/ | biz-procedures-decompose.md |
| align | project.md, epics/, requirements/, opportunities.md | （只读） | biz-procedures-align.md |
| view | project.md, epics/, requirements/, opportunities.md | （只读） | biz-procedures-view.md |
| （空参） | state.md, project.md, opportunities.md | （只读） | 内联智能引导 |

## 流程

### 所有子命令的公共前置

1. 读取 state.md 和 project.md 确认项目上下文
2. 确认 .devpace/ 已初始化（未初始化时引导 /pace-init）
3. 按子命令路由到对应 procedures 文件

### 空参数引导

当用户无参数调用 `/pace-biz` 时：

1. 扫描项目上下文：
   - opportunities.md 中 `评估中` 的 Opportunity 数量
   - epics/ 中 `进行中` 和 `规划中` 的 Epic 数量
   - project.md 树视图中未关联 Epic 的"孤立" BR 数量
2. 生成个性化推荐（优先级：未评估 Opportunity > 规划中 Epic 需分解 > 战略对齐）
3. 附标准子命令列表兜底

## 输出

### 所有子命令的通用输出原则

- **渐进暴露**：默认输出简洁摘要，`--detail` 展示完整信息
- **操作确认**：写入操作前展示变更预览，用户确认后执行
- **追溯链**：每次创建实体时展示其在价值链中的位置

### opportunity 输出

```
已捕获业务机会：OPP-xxx — [描述]
来源：[类型]（[详情]）
状态：评估中
→ 下一步：/pace-biz epic OPP-xxx 评估并转化为 Epic
```

### epic 输出

```
已创建专题：EPIC-xxx — [名称]
关联：OBJ-x（[目标]）← OPP-xxx（如有）
MoS：[指标列表]
→ 下一步：/pace-biz decompose EPIC-xxx 分解为业务需求
```

### decompose 输出

```
已分解 [EPIC-xxx|BR-xxx]：
├── BR-001：[名称] P0
├── BR-002：[名称] P1
└── BR-003：[名称] P2
→ 下一步：/pace-change add 补充 PF 或 /pace-dev 开始开发
```

### align 输出

```
战略对齐度报告：
- OBJ 覆盖率：N/M OBJ 有 Epic 覆盖
- 孤立实体：[列表]
- 对齐建议：[建议]
```

### view 输出

```
业务全景：
OPP-001（评估中）
OPP-002 → EPIC-001（进行中）
  ├── BR-001 → PF-001 → CR-001 🔄
  └── BR-002 → PF-002（待开始）
OPP-003 → EPIC-002（规划中）
```
