# view 子命令 procedures

> **职责**：展示业务全景视图，从 Opportunity 到 CR 的完整价值流。

## 触发

`/pace-biz view` 或用户想看业务全景。

## 步骤

### Step 0：模式检查

读取 project.md 的 `mode` 字段。若为 `lite`：

- 跳过 opportunities.md 和 epics/ 采集
- 视图简化为 `OBJ→PF→CR` 树（与 `/pace-status tree` 类似但保留业务全景统计）
- 统计部分省略 Opportunity/Epic/BR 计数

### Step 1：采集数据

读取以下文件：
1. `opportunities.md` — 所有 Opportunity 及其状态
2. `epics/` — 所有 Epic 文件及其 BR 列表
3. `project.md` — 价值功能树（BR→PF→CR 关系）
4. `state.md` — 当前工作状态

### Step 2：构建全景视图

**排序模式选择**：

| 模式 | 触发条件 | 排序策略 |
|------|---------|---------|
| 默认（层级） | 无特殊触发 | 按 OBJ→Epic→BR→PF 层级树展示 |
| 问题优先 | 存在 3+ 个问题实体 | 将需要操作的实体前置为"待处理"段，其余折叠为"正常"段 |

**问题优先模式**：当检测到以下问题实体合计 >= 3 个时自动切换：
- Epic MoS 为空
- Epic/BR 待分解（无下级实体）
- BR 无 PF
- Opportunity 长期评估中
- 孤立 BR/PF（无上游关联）

输出结构变为：
```
业务全景（[项目名]）— 问题优先视图
══════════════════

[需要关注]（N 项）
├── EPIC-002（规划中，待分解）→ /pace-biz decompose EPIC-002
├── BR-005（孤立，无 Epic 关联）→ /pace-change modify BR-005
└── OPP-002（评估中 >7 天）→ /pace-biz epic OPP-002

[正常运行]
└── （折叠展示，OBJ→Epic→BR→PF 树）
```

按以下层次组织数据，对有问题的实体内联操作引导：

```
业务全景（[项目名]）
══════════════════

[OBJ-1：目标名]
├── [EPIC-001：专题名]（进行中）← OPP-001
│   MoS：2/3 达成 ✅（或"待定义 → 补充：直接描述指标，或 /pace-change modify EPIC-001"）
│   ├── BR-001：需求名 P0 进行中 [就绪度 85%]
│   │   ├── PF-001 → CR-001 🔄
│   │   └── PF-002 → (待创建 CR)
│   └── BR-002：需求名 P1 待开始 [就绪度 40% → /pace-biz refine BR-002]（待分解 → /pace-biz decompose BR-002）
└── [EPIC-002：专题名]（规划中）← OPP-003
    └── （待分解 → /pace-biz decompose EPIC-002）

[未关联 Epic 的 BR]（向后兼容路径）
└── BR-003：需求名 → PF-003 → CR-002 ✅

[未处理的业务机会]
├── OPP-002（评估中）：竞品 X 上线实时协作 → /pace-biz epic OPP-002
└── OPP-004（已搁置）：内部工具整合

[统计]
├── Opportunity：N 总计（M 评估中 / K 已采纳 / L 已搁置）
├── Epic：N 总计（M 进行中 / K 规划中 / L 已完成）
├── BR：N 总计
├── PF：N 总计（M 完成）
└── CR：N 总计（M 活跃）
```

**内联引导规则**：对以下状态的实体追加操作引导：
- Epic MoS 为空 → 提示补充
- Epic/BR 待分解 → 提示 decompose
- Opportunity 评估中 → 提示转化为 Epic
- BR 无 PF → 提示 decompose

**角色适配**（读取公共前置传入的 preferred-role，调整展示维度）：

| 角色 | 追加展示 |
|------|---------|
| Biz Owner | 每个 Epic 的 MoS 达成进度（[x]/[total] checkbox） |
| PM | 每个 BR 的 PF 完成度 + 依赖关系 |
| Dev | 每个 PF 的 CR 状态 + 技术复杂度标记（如有） |
| Tester | 每个 PF 的验收标准数量 + 是否有 CR 通过 Gate 2 |
| Ops | Release 关联状态（如有 /pace-release） |

角色适配仅增加展示列，不改变全景视图的基本结构。Dev 角色使用默认展示（零改变）。

### Step 3：适配项目规模

| 项目规模 | 展示策略 |
|---------|---------|
| 无 Epic/Opportunity | 简化为 OBJ→BR→PF→CR 树视图（与 /pace-status tree 类似） |
| 1-3 Epic | 完整展示所有层级 |
| 4+ Epic | 折叠已完成的 Epic，展开活跃的 |

### Step 4：输出

直接在终端输出格式化的全景视图。不写入文件。

## 注意

- 此子命令为**只读**，不修改任何文件
- 与 `/pace-status` 的区别：/pace-status 聚焦 CR/PF 的**开发进度**；/pace-biz view 聚焦 OPP→EPIC→BR 的**业务规划**视角
- 向后兼容：无 Epic/Opportunity 时退化为简单的 OBJ→BR→PF→CR 树视图
