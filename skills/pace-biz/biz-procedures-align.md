# align 子命令 procedures

> **职责**：检查 OBJ→Epic→BR 战略对齐度，发现孤立实体和覆盖缺口。

## 触发

`/pace-biz align` 或用户想检查战略对齐。

## 步骤

### Step 0：模式检查

读取 project.md 的 `mode` 字段。若为 `lite`：

- 跳过 Step 2.2 中 Epic 相关检查（孤立 BR、空 Epic、未处理 Opportunity）
- 跳过 Step 2.3 中 Epic 级 MoS 检查
- 对齐检查简化为：OBJ 覆盖率（OBJ→PF）+ 孤立 PF 检测 + OBJ 级 MoS 完整性 + 价值链完整性（OBJ→PF→CR）

### Step 1：采集实体数据

读取以下文件：
1. `project.md` — OBJ 列表、价值功能树（Epic→BR→PF→CR 关系）
2. `epics/` — 所有 Epic 文件（状态、MoS、BR 列表）
3. `requirements/` — 溢出的 BR 文件（如有）
4. `opportunities.md` — 未处理的 Opportunity（如有）

### Step 2：分析对齐度

执行以下检查：

#### 2.1 OBJ 覆盖率

- 每个 OBJ 是否至少有一个 Epic 或 BR？
- 没有 Epic/BR 的 OBJ 标记为"未覆盖"

#### 2.2 孤立实体检测

- BR 未关联任何 Epic 也未直接挂 OBJ → 孤立 BR
- PF 未关联任何 BR → 孤立 PF
- Epic 中 BR 列表为空 → 空 Epic（需分解）
- Opportunity 状态长期为"评估中" → 未处理的机会

#### 2.3 MoS 完整性

- OBJ 有 MoS 定义？
- Epic 有 MoS 定义？
- MoS 与 BR/PF 完成度的对应关系是否合理？

#### 2.4 价值链完整性

- 检查每条从 OBJ 到 CR 的链路是否连续
- 标记断裂点（如 BR→PF 为空）

### Step 3：生成对齐报告

```
战略对齐度报告
══════════════

OBJ 覆盖率：[N/M] OBJ 有 Epic/BR 覆盖
├── OBJ-1（[名称]）：[N] Epic, [M] BR — [覆盖/未覆盖]
└── OBJ-2（[名称]）：[N] Epic, [M] BR — [覆盖/未覆盖]

孤立实体：
├── 孤立 BR：[列表]（未关联 Epic 或 OBJ）
├── 空 Epic：[列表]（无 BR，需分解）
└── 未处理机会：[列表]（评估中 Opportunity）

MoS 完整性：
├── OBJ 级 MoS：[N/M] 已定义
└── Epic 级 MoS：[N/M] 已定义

建议：
1. [具体对齐建议]
2. [具体对齐建议]
```

## 注意

- 此子命令为**只读分析**，不修改任何文件
- 无 Epic 和 Opportunity 时简化报告（只检查 OBJ→BR→PF→CR 链路）
- 向后兼容：旧项目无 Epic 层时仍能生成有意义的对齐报告
