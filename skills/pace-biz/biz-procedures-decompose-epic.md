# decompose Epic->BR 分解规程

> **职责**：分解 Epic 为业务需求（BR），填充价值链 Epic->BR 层。

## 触发

`/pace-biz decompose EPIC-xxx` 或用户要分解某个专题。

## 步骤

### Step 0：模式检查

lite 模式不支持 decompose EPIC（见 `knowledge/_guides/lite-mode-guide.md`）。提示："lite 模式无 Epic/BR 层，不支持 Epic 分解。升级：`/pace-init --upgrade-mode` 启用完整模式。"终止。

### Step 1：确定分解目标

确认参数为 `EPIC-xxx` 格式。无参数时列出可分解的 Epic，引导选择。

### Step 2：读取 Epic 信息

1. 读取 `epics/EPIC-xxx.md`
2. 确认状态为 `规划中` 或 `进行中`（`已搁置` 需先 resume）
3. 读取 Epic 背景和 MoS

### Step 3：引导需求分解

向用户展示 Epic 背景和 MoS，然后引导分解：

1. 基于 Epic 背景，Claude 建议 BR 分解方案（2-5 个 BR）
2. 每个 BR 包含：名称 + 一句话描述
3. **优先级评估**：方法论定义和选择条件见 `knowledge/_extraction/prioritization-methods.md`。默认 Value x Effort（向后兼容），用户可通过 `--moscow` 或 `--kano` 指定替代方法
4. **依赖关系**：对每个新 BR，询问是否依赖已有的 BR：
   - 列出同 Epic 下已有的其他 BR 供选择
   - 无依赖 -> 记为 `—`
   - 有依赖 -> 记录 BR-xxx（可多个，逗号分隔）
   - 依赖信息写入 Epic 文件"业务需求"表格的"依赖"列
5. **利益相关者关联**（可选——Epic 文件有"利益相关者"段时触发）：
   - 读取 Epic 的利益相关者表格
   - 对每个 BR，提示："这个需求主要影响哪些利益相关者？"
   - 用户跳过 -> 不记录（零摩擦）
   - 用户回答 -> 记录到 BR 描述中（如"主要影响：终端用户、运维团队"）
6. **角色追加考量**（通用维度见 `knowledge/role-adaptations.md`，读取公共前置传入的 preferred-role）：
   - Biz Owner -> 提示考虑"这个 BR 的商业价值如何量化？"
   - Dev -> 提示考虑"有哪些技术约束或 NFR（性能/安全/可用性）？"
   - Tester -> 提示考虑"这个 BR 的验收标准是什么？怎么测试？"
   - PM/Ops/Dev(默认) -> 无追加（零改变）
7. 用户确认/调整分解方案

### Step 4：创建 BR 条目

对每个确认的 BR：

1. 在 project.md 价值功能树中，在对应 Epic 下追加 BR 行（内联格式遵循 `knowledge/_schema/entity/br-format.md` §内联格式）：
   ```
   BR-xxx：[名称] `Px`
   ```
2. BR 编号自增（扫描 project.md 树中最大 BR 编号 +1）
3. 更新 Epic 文件的"业务需求"表格

### Step 5：更新 Epic 文件

更新 Epic 文件的"业务需求"表格（Step 4 已追加 BR 到 project.md 树，此处同步 Epic 文件内表格）。

**Epic 状态不变**——新分解的 BR 均为 `待开始`，按 epic-format 状态计算规则，Epic 保持 `规划中`。只有当 BR 下的 PF 有活跃 CR（developing/verifying/in_review）时，Epic 才自动转为 `进行中`。

### Step 6：输出分解结果

```
已分解 EPIC-xxx：
├── BR-001：[名称] [优先级]
├── BR-002：[名称] [优先级]
└── BR-003：[名称] [优先级]

依赖关系：
  BR-002 ──依赖──→ BR-001
  BR-003（无依赖，可并行）
  建议实施顺序：001 → 002 → 003

价值链：OBJ-x → EPIC-xxx → BR-xxx
→ 下一步：/pace-biz decompose BR-xxx 继续分解 | /pace-plan next 规划迭代
```

**依赖可视化规则**：
- 有依赖关系时展示 `A ──依赖──→ B` 箭头
- 无依赖的标记"可并行"
- 自动推算建议实施顺序（拓扑排序：先无依赖项，后有依赖项）
- 全部无依赖时省略此段

## 容错

| 异常 | 处理 |
|------|------|
| EPIC 编号不存在 | 提示无效编号，列出可用选项 |
| Epic 状态为"已搁置" | 提示需先 /pace-change resume |
| 已有 BR 的重复分解 | 展示现有分解，询问是否追加 |
| project.md 无树结构 | 创建树结构后执行分解 |
| project.md/Epic 文件在读取后被修改 | 重新读取最新内容后合并变更，冲突时询问用户 |
