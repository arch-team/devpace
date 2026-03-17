# epic 子命令 procedures

> **职责**：从 Opportunity 转化或直接创建 Epic，定义 MoS，更新价值功能树。

## 触发

`/pace-biz epic [OPP-xxx] <描述>` 或用户要创建一个专题/Epic。

## 步骤

### Step 0：模式检查

lite 模式不可用（见 SKILL.md lite 模式子命令可用性表）。提示升级 `/pace-init --upgrade-mode` 或 `/pace-change add`，终止。

### Step 1：确定来源

- 有 `OPP-xxx` 参数 → 读取 opportunities.md 确认 OPP 存在且状态为 `评估中`
- 无 OPP 参数 → 直接创建模式（来源字段留空或标注"直接创建"）

### Step 2：确定 OBJ 关联

1. 读取 project.md 业务目标 section，列出可用 OBJ
2. 如果只有 1 个 OBJ → 自动关联
3. 如果多个 OBJ → 询问用户选择
4. 如果无 OBJ → 引导先定义业务目标（建议 /pace-init full）

### Step 3：引导定义 Epic 内容

向用户询问（如未在参数中提供）：

1. **专题名称**：一句话描述这个专题
2. **背景**：2-3 句话，为什么做这个专题
3. **成效指标（MoS）**：如何衡量这个专题的成功？（可选——渐进填充）
   - 引导时建议"客户价值/企业价值"分类，但不强制——如用户提供简单指标列表，保持简单格式即可

### Step 4：生成 EPIC 编号

1. 扫描 `.devpace/epics/` 目录（不存在则创建）
2. 取最大 EPIC 编号 +1
3. 三位补零：`EPIC-001`、`EPIC-002`...

### Step 5：创建 Epic 文件

创建 `.devpace/epics/EPIC-xxx.md`，文件结构遵循 `knowledge/_schema/entity/epic-format.md` §文件结构。

**创建时初始值**：
- **状态**：`规划中`
- **来源**：有 OPP 参数时填 `OPP-xxx（[描述]）`，无则留空或标注"直接创建"
- **时间框架**：留空（首次 /pace-plan 时填充）
- **MoS**：用户提供了指标则填充双维度格式，未提供则写占位"（待定义 — /pace-biz decompose 或讨论时填充）"
- **利益相关者**：创建空表头（后续 /pace-biz refine 时填充）
- **业务需求表**：创建空表（含全部 7 列）

**OBJ 引用格式**：有 `objectives/` 目录时用链接 `[OBJ-xxx：描述](../objectives/OBJ-xxx.md)`；无 `objectives/` 时用纯文本 `OBJ-x（描述）`。

### Step 6：更新 project.md 价值功能树

在对应 OBJ 下追加 Epic 链接行：

```markdown
OBJ-x（[目标名]）
├── ... (existing)
└── [EPIC-xxx：专题名](epics/EPIC-xxx.md)
```

### Step 7：更新 opportunities.md（如从 OPP 转化）

将对应 OPP 状态改为：`已采纳 → EPIC-xxx`

### Step 8：输出确认

```
已创建专题：EPIC-xxx — [名称]
关联：OBJ-x（[目标]）← OPP-xxx（如有）
MoS：[指标列表] 或 （待定义）
→ 下一步：/pace-biz decompose EPIC-xxx 分解为业务需求
```

## 容错

| 异常 | 处理 |
|------|------|
| OPP-xxx 不存在 | 提示 OPP 编号无效，列出可用 OPP |
| OPP 状态非"评估中" | 提示已处理，询问是否仍要创建 Epic |
| epics/ 目录不存在 | 自动创建 |
| project.md 无价值功能树 | 创建空树结构后追加 |
| 无 OBJ | 引导 /pace-init full 或先定义 OBJ |
