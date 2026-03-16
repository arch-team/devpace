# 角色切换执行规程

> 由 SKILL.md 路由表加载。仅在 biz/pm/dev/tester/ops/auto/set-default 参数时读取。

## §0 速查卡片

- **角色切换**：5 角色别名映射（中英文），参数→标准角色名
- **模式恢复**：`auto` 清除显式设置，回到自动推断
- **持久化**：`set-default` 写入 project.md，`set-default auto` 移除

## Step 1：确定目标角色

- 有参数 → 映射到角色（支持中英文别名）
- 无参数 → 显示当前角色 + 5 种角色简介，等用户选择

角色别名映射：
- biz / business / 业务 / 业务负责人 → Biz Owner
- pm / product / 产品 / 产品经理 → PM
- dev / developer / 开发 / 开发者 → Dev
- tester / test / qa / 测试 / 测试者 → Tester
- ops / operations / 运维 / 运维工程师 → Ops

特殊子命令：
- `auto` → 清除显式角色设置，回到自动推断模式。状态机：`explicit → auto`
- `set-default <角色>` → 将 `preferred-role: <角色>` 写入 `.devpace/project.md` 配置 section。`set-default auto` 移除该字段

## Step 2：切换视角

1. 记录当前角色到会话上下文
2. 输出确认（2-3 行上限）：
   - 第 1 行：确认 + 来源标记："切换到 [角色名] 视角，后续输出关注 [关注点]。"
   - 第 2 行（仅当相关性评估识别出特殊聚焦维度时）：`当前聚焦：[维度 1]（[数据]）、[维度 2]（[数据]）`
   - 第 3 行（可选导航）：`→ 查看详情：/pace-status`
   - 无上下文特殊性时，保持 1 行确认
3. 执行**相关性评估**（结果可见化——融入确认输出第 2 行）：
   - 扫描当前会话上下文，识别与新角色最相关的 2-3 个关注维度
   - 评估结果存入会话上下文，后续命令可引用而不重复计算
   - 无法推断时，使用角色默认关注维度（`knowledge/role-adaptations.md` 角色定义表）

### 手动聚焦覆盖

支持 `--focus` 参数指定聚焦维度：`/pace-role pm --focus 审批,交付`
- 覆盖相关性评估的自动结果
- 后续命令使用手动指定的聚焦维度
- 仅在当前会话内有效
