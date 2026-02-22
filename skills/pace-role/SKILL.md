---
description: Use when user says "切换角色", "以XX视角", "pace-role", "作为产品经理", "作为运维", or wants to view from a different role perspective.
allowed-tools: Read, Glob
argument-hint: "[biz|pm|dev|tester|ops]"
---

# /pace-role — 角色视角切换

显式切换角色视角，调整 Claude 的输出关注点和术语。

## 输入

$ARGUMENTS：
- `biz` → Biz Owner（业务负责人）
- `pm` → PM（产品经理）
- `dev` → Dev（开发者，默认）
- `tester` → Tester（测试者）
- `ops` → Ops（运维）
- （空）→ 显示当前角色和可选角色

## 流程

### Step 1：确定目标角色

- 有参数 → 映射到角色（支持中英文别名）
- 无参数 → 显示当前角色 + 5 种角色简介，等用户选择

角色别名映射：
- biz / business / 业务 / 业务负责人 → Biz Owner
- pm / product / 产品 / 产品经理 → PM
- dev / developer / 开发 / 开发者 → Dev
- tester / test / qa / 测试 / 测试者 → Tester
- ops / operations / 运维 / 运维工程师 → Ops

### Step 2：切换视角

1. 记录当前角色到会话上下文
2. 用 1 句话确认切换："切换到 [角色名] 视角，后续输出关注 [关注点]。"
3. 切换后自动执行**相关性评估**（静默执行，不额外输出）：
   - 扫描当前会话上下文，识别与新角色最相关的 2-3 个关注维度
   - 后续输出自动聚焦这些维度（如 PM+当前有多个 in_review CR → 聚焦"交付节奏"和"审批瓶颈"）
   - 无法推断时，使用角色默认关注维度（Step 3 表格定义）

### Step 3：调整后续行为

切换后，同一会话中所有后续输出自动应用新角色视角：

| 角色 | /pace-status 关注 | /pace-retro 关注 | 通用输出风格 |
|------|-------------------|------------------|-------------|
| Biz Owner | MoS 达成率、业务价值交付 | ROI、目标对齐、战略偏差 | 业务术语，关联 OBJ |
| PM | 迭代进度、功能完成度、依赖 | 交付效率、范围变更、资源 | 功能维度，关注节奏 |
| Dev | CR 状态、质量门、技术细节 | 代码质量、技术债、复杂度 | 技术术语，关注实现 |
| Tester | 缺陷分布、测试覆盖、验证状态 | 缺陷逃逸、回归风险、覆盖率 | 质量维度，关注缺陷 |
| Ops | Release 状态、部署健康、MTTR | 部署频率、故障恢复、稳定性 | 运维术语，关注稳定 |

## 输出

角色切换确认（1 句话）。
