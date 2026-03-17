# decompose BR->PF 分解规程

> **职责**：分解业务需求（BR）为产品功能（PF），填充价值链 BR->PF 层。

## 触发

`/pace-biz decompose BR-xxx` 或用户要分解某个业务需求为功能。

## 步骤

### Step 0：模式检查

lite 模式不可用（见 SKILL.md lite 模式子命令可用性表）。提示"轻量模式无 BR 层，如需 BR 能力可通过 `/pace-init --upgrade-mode` 升级"，终止。

### Step 1：确定分解目标

确认参数为 `BR-xxx` 格式。无参数时列出可分解的 BR，引导选择。

### Step 2：读取 BR 信息

1. 从 project.md 树视图或 `requirements/BR-xxx.md` 读取 BR 信息
2. 读取关联 Epic 和 OBJ 上下文

### Step 3：引导功能分解

向用户展示 BR 上下文，然后引导分解：

1. 基于 BR 描述，Claude 建议 PF 分解方案（1-3 个 PF）
2. 每个 PF 包含：名称 + 用户故事建议
3. **优先级继承与调整**：PF 默认继承所属 BR 优先级，同一 BR 下多个 PF 时可微调：
   - 核心路径 PF（必须有才能交付 BR 价值）-> 可提升
   - 锦上添花 PF（增强但非必需）-> 可降级
   - 用户可直接指定优先级跳过评估
   - 继承 Epic->BR 分解时使用的优先级方法（若 BR 使用了 MoSCoW/Kano，PF 微调时参考同一框架，方法论见 `knowledge/_extraction/prioritization-methods.md`）
4. **角色追加考量**（通用维度见 `knowledge/role-adaptations.md`，读取公共前置传入的 preferred-role）：
   - Dev -> 提示考虑"这个 PF 的实现复杂度？有架构影响吗？"
   - Tester -> 提示考虑"边界条件有哪些？需要什么测试数据？"
   - Biz Owner/PM/Ops/Dev(默认) -> 无追加（零改变）
5. 用户确认/调整分解方案

### Step 4：创建 PF 条目

对每个确认的 PF：

1. 在 project.md 价值功能树中，在对应 BR 下追加 PF 行：
   ```
   PF-xxx：[名称]（[用户故事]）→ (待创建 CR)
   ```
2. PF 编号自增（扫描 project.md 树中最大 PF 编号 +1）

### Step 5：更新 BR 状态

如果 BR 有溢出文件 -> 更新 `requirements/BR-xxx.md` 的 PF 列表

### Step 6：输出分解结果

```
已分解 BR-xxx：
├── PF-001：[名称] [优先级]
├── PF-002：[名称] [优先级]
└── PF-003：[名称] [优先级]

价值链：OBJ-x → EPIC-xxx → BR-xxx → PF-xxx
→ 下一步：/pace-dev 开始开发 | /pace-plan next 规划迭代
```

## 容错

| 异常 | 处理 |
|------|------|
| BR 编号不存在 | 提示无效编号，列出可用选项 |
| 已有 PF 的重复分解 | 展示现有分解，询问是否追加 |
| project.md 无树结构 | 创建树结构后执行分解 |
