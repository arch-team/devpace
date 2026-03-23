# pace-role — 角色视角切换

> 在五个 BizDevOps 角色之间切换 Claude 的输出视角，用不同镜头观察同一个项目。

## 核心特性

### 多角色视角
在五个内置角色之间切换，对齐 BizDevOps 理论：

| 角色 | 关注领域 | 输出风格 |
|------|---------|---------|
| **Biz Owner** | MoS 达成率、业务价值交付 | 业务术语，关联 OBJ |
| **PM** | 迭代进度、交付节奏、依赖 | 功能维度，关注排期 |
| **Dev**（默认） | CR 状态、质量门、技术细节 | 技术术语，关注实现 |
| **Tester** | 缺陷分布、测试覆盖、验证状态 | 质量维度，关注缺陷预防 |
| **Ops** | Release 状态、部署健康度、MTTR | 运维术语，关注稳定性 |

### 自动推断
devpace 自动从对话关键词检测角色上下文并调整输出。推断使用粘性规则防止角色抖动——需要连续 2+ 轮对话的一致信号才会切换。

### 上下文感知适配
切换角色时，devpace 执行相关性评估——扫描当前项目上下文（活跃 CR、迭代进度、风险状态），识别新角色最相关的 2-3 个聚焦维度。

### 跨会话持久化
通过 `/pace-role set-default <角色>` 设置偏好角色，跨会话持久化。存储在 project.md 配置中。

### 多视角快照
`/pace-role compare` 输出紧凑的 5 行快照，同时展示所有角色视角——适用于决策时刻（合并、变更审批、迭代规划）。

## 子命令

| 子命令 | 说明 |
|--------|------|
| `/pace-role <角色>` | 切换到指定角色视角 |
| `/pace-role`（无参数） | 显示当前角色及来源 |
| `/pace-role auto` | 回到自动推断模式 |
| `/pace-role compare` | 多视角快照 |
| `/pace-role set-default <角色>` | 设置跨会话默认角色 |
| `/pace-role pm --focus X,Y` | 切换并手动指定聚焦维度 |

## 跨 Skill 集成

角色感知影响多个 Skill 的输出：

| Skill | 集成深度 | 行为 |
|-------|---------|------|
| pace-status | 深度（5 套角色模板） | 按角色完全重组输出 |
| pace-next | 中度 | Step 5 表格调整术语 |
| pace-retro | 中度 | 报告摘要按角色关注点重排序 |
| pace-change | 轻度 | 影响摘要按角色措辞适配 |
| pace-pulse | 轻度 | 信号提示按角色上下文调整 |

## 相关资源

- 角色关注维度（权威源）：`skills/pace-role/role-procedures-dimensions.md`
- 角色切换规程：`skills/pace-role/role-procedures-switch.md`
- 多视角快照规程：`skills/pace-role/role-procedures-compare.md`
- 角色推断规则：`skills/pace-role/role-procedures-inference.md`
- 状态角色模板：`skills/pace-status/status-procedures-roles.md`
- 教学条目：`knowledge/_guides/teaching-catalog.md`（`role_adapt`、`role_infer`）
- 理论背景：`knowledge/theory.md` §4（BizDevOps 角色）
