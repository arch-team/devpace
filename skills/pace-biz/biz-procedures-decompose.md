# decompose 子命令 procedures

> **职责**：分解 Epic→BR 或 BR→PF，填充价值链中间层。

## 触发

`/pace-biz decompose <EPIC-xxx|BR-xxx>` 或用户要分解专题/需求。

## 步骤

### Step 0：模式检查

读取 project.md 的 `mode` 字段。若为 `lite`：

- `EPIC-xxx` 参数 → 提示"轻量模式无 Epic 层"，终止
- `BR-xxx` 参数 → 提示"轻量模式无 BR 层，PF 直接挂在 OBJ 下"，终止
- 无参数 → 提示"轻量模式下建议使用 `/pace-change add` 添加 PF，或 `/pace-init --upgrade-mode` 升级"，终止

> lite 模式价值链为 OBJ→PF→CR，没有 Epic/BR 层可分解。

### Step 1：确定分解目标

根据参数判断分解方向：
- `EPIC-xxx` → Epic→BR 分解
- `BR-xxx` → BR→PF 分解
- 无参数 → 列出可分解的 Epic/BR，引导选择

### Epic→BR 分解路径

#### Step 2E：读取 Epic 信息

1. 读取 `epics/EPIC-xxx.md`
2. 确认状态为 `规划中` 或 `进行中`（`已搁置` 需先 resume）
3. 读取 Epic 背景和 MoS

#### Step 3E：引导需求分解

向用户展示 Epic 背景和 MoS，然后引导分解：

1. 基于 Epic 背景，Claude 建议 BR 分解方案（2-5 个 BR）
2. 每个 BR 包含：名称 + 一句话描述
3. **优先级评估**：支持多种方法论，默认 Value x Effort（向后兼容）：

   **方法 A：Value x Effort 矩阵**（默认）：
   - Value（价值）：高/中/低 — 对 Epic MoS 的贡献度
   - Effort（成本）：高/中/低 — 预估实现复杂度
   - 映射：高价值+低成本=P0 | 高价值+高成本 或 中价值+低成本=P1 | 其他=P2
   - 展示评估矩阵让用户确认或覆盖（用户可直接指定优先级跳过矩阵）

   **方法 B：MoSCoW**（用户指定 `--moscow` 或 Claude 检测到大量 BR 需分类时建议）：
   - Must have → P0 | Should have → P1 | Could have → P2 | Won't have → 标记"不做"
   - 引导问题："这个需求不做的话，Epic 还能交付核心价值吗？"（Must 判定）

   **方法 C：Kano 模型**（用户指定 `--kano` 或面向终端用户的产品功能时建议）：
   - 基本型（缺失则不满）→ P0 | 期望型（有则满意）→ P1 | 兴奋型（超预期）→ P2
   - 引导问题："如果没有这个功能，用户会觉得产品有问题吗？"（基本型判定）

   **方法选择**：用户可通过参数指定（`decompose EPIC-xxx --moscow`），或 Claude 基于上下文建议最合适的方法。默认行为不变（Value x Effort），确保向后兼容
4. **依赖关系**：对每个新 BR，询问是否依赖已有的 BR：
   - 列出同 Epic 下已有的其他 BR 供选择
   - 无依赖 → 记为 `—`
   - 有依赖 → 记录 BR-xxx（可多个，逗号分隔）
   - 依赖信息写入 Epic 文件"业务需求"表格的"依赖"列
5. **利益相关者关联**（可选——Epic 文件有"利益相关者"段时触发）：
   - 读取 Epic 的利益相关者表格
   - 对每个 BR，提示："这个需求主要影响哪些利益相关者？"
   - 用户跳过 → 不记录（零摩擦）
   - 用户回答 → 记录到 BR 描述中（如"主要影响：终端用户、运维团队"）
6. **角色追加考量**（读取公共前置传入的 preferred-role）：
   - Biz Owner → 提示考虑"这个 BR 的商业价值如何量化？"
   - Dev → 提示考虑"有哪些技术约束或 NFR（性能/安全/可用性）？"
   - Tester → 提示考虑"这个 BR 的验收标准是什么？怎么测试？"
   - PM/Ops/Dev(默认) → 无追加（零改变）
7. 用户确认/调整分解方案

#### Step 4E：创建 BR 条目

对每个确认的 BR：

1. 在 project.md 价值功能树中，在对应 Epic 下追加 BR 行：
   ```
   BR-xxx：[名称] `Px`
   ```
2. BR 编号自增（扫描 project.md 树中最大 BR 编号 +1）
3. 更新 Epic 文件的"业务需求"表格

#### Step 5E：更新 Epic 文件

更新 Epic 文件的"业务需求"表格（Step 4E 已追加 BR 到 project.md 树，此处同步 Epic 文件内表格）。

**Epic 状态不变**——新分解的 BR 均为 `待开始`，按 epic-format 状态计算规则，Epic 保持 `规划中`。只有当 BR 下的 PF 有活跃 CR（developing/verifying/in_review）时，Epic 才自动转为 `进行中`。

### BR→PF 分解路径

#### Step 2P：读取 BR 信息

1. 从 project.md 树视图或 `requirements/BR-xxx.md` 读取 BR 信息
2. 读取关联 Epic 和 OBJ 上下文

#### Step 3P：引导功能分解

向用户展示 BR 上下文，然后引导分解：

1. 基于 BR 描述，Claude 建议 PF 分解方案（1-3 个 PF）
2. 每个 PF 包含：名称 + 用户故事建议
3. **优先级继承与调整**：PF 默认继承所属 BR 优先级，同一 BR 下多个 PF 时可微调：
   - 核心路径 PF（必须有才能交付 BR 价值）→ 可提升
   - 锦上添花 PF（增强但非必需）→ 可降级
   - 用户可直接指定优先级跳过评估
   - 继承 Epic→BR 分解时使用的优先级方法（若 BR 使用了 MoSCoW/Kano，PF 微调时参考同一框架）
4. **角色追加考量**（读取公共前置传入的 preferred-role）：
   - Dev → 提示考虑"这个 PF 的实现复杂度？有架构影响吗？"
   - Tester → 提示考虑"边界条件有哪些？需要什么测试数据？"
   - Biz Owner/PM/Ops/Dev(默认) → 无追加（零改变）
5. 用户确认/调整分解方案

#### Step 4P：创建 PF 条目

对每个确认的 PF：

1. 在 project.md 价值功能树中，在对应 BR 下追加 PF 行：
   ```
   PF-xxx：[名称]（[用户故事]）→ (待创建 CR)
   ```
2. PF 编号自增（扫描 project.md 树中最大 PF 编号 +1）

#### Step 5P：更新 BR 状态

如果 BR 有溢出文件 → 更新 `requirements/BR-xxx.md` 的 PF 列表

### 公共结束步骤

#### Step 6：输出分解结果

```
已分解 [EPIC-xxx|BR-xxx]：
├── [BR|PF]-001：[名称] [优先级]
├── [BR|PF]-002：[名称] [优先级]
└── [BR|PF]-003：[名称] [优先级]

依赖关系：
  [BR|PF]-002 ──依赖──→ [BR|PF]-001
  [BR|PF]-003（无依赖，可并行）
  建议实施顺序：001 → 002 → 003

价值链：OBJ-x → EPIC-xxx → BR-xxx → PF-xxx
→ 下一步：/pace-plan next 规划迭代 | 继续分解：/pace-biz decompose [编号]
```

**依赖可视化规则**：
- 有依赖关系时展示 `A ──依赖──→ B` 箭头
- 无依赖的标记"可并行"
- 自动推算建议实施顺序（拓扑排序：先无依赖项，后有依赖项）
- 全部无依赖时省略此段

## 容错

| 异常 | 处理 |
|------|------|
| EPIC/BR 编号不存在 | 提示无效编号，列出可用选项 |
| Epic 状态为"已搁置" | 提示需先 /pace-change resume |
| 已有 BR/PF 的重复分解 | 展示现有分解，询问是否追加 |
| project.md 无树结构 | 创建树结构后执行分解 |
