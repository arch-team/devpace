# pace-sync 通用规程

> **职责**：/pace-sync 始终加载的通用规则。其他 procedures 文件按子命令路由加载（见 SKILL.md 执行路由表）。

## §0 速查卡片

> 子命令→文件路由表见 SKILL.md "流程" section（权威源）。以下为各文件核心内容摘要。

| 文件 | 核心内容 |
|------|---------|
| `sync-procedures-common.md` | 适配器路由 · 前置检查 · 操作语义 · 降级 · 集成 |
| `sync-procedures-entity.md` | **智能同步主流程** · 实体 ID 解析 · 增量检测 · 层级创建 |
| `sync-procedures-setup.md` | 引导式配置 · pace-init 延伸 |
| `sync-procedures-link.md` | 标准/智能/批量 link · create（全实体类型） |
| `sync-procedures-push.md` | 单实体推送步骤（内部模块，被 entity.md 调用） |
| `sync-procedures-push-advanced.md` | Gate 结果同步 |
| `sync-procedures-auto.md` | auto-link · auto-create（Hook 触发） |
| `sync-procedures-pull.md` | 外部状态检查 · 状态一致性比较 |
| `sync-procedures-status.md` | 同步状态表（支持 --all）· 解除关联 |

## §1 适配器路由

> Claude 根据 sync-mapping.md "平台"字段加载对应适配器文件执行。

| 平台 | 适配器文件 | 域名匹配 | 工具 | 状态 |
|------|-----------|---------|------|------|
| GitHub | sync-adapter-github.md | github.com | gh CLI | 可用 |
| GitLab | sync-adapter-gitlab.md | gitlab.com | — | Phase 19 |
| Linear | sync-adapter-linear.md | — | MCP | Phase 19 |
| Jira | sync-adapter-jira.md | — | MCP/CLI | Phase 19+ |

**执行规则**：子命令步骤使用操作语义（如"验证连接"、"更新状态标记"），Claude 在适配器文件的操作表中查找对应命令执行。

## §2 通用前置检查

所有子命令执行前（setup 除外）：
1. 读取 `.devpace/integrations/sync-mapping.md`
   - 不存在 → 引导运行 `setup`，终止当前操作
2. 根据 sync-mapping.md "平台"字段加载适配器文件

## §3 输出约定

- 外部实体编号（如 `#42`）附带完整 URL，便于终端点击跳转
- URL 从 sync-mapping.md 平台配置的"连接"字段拼装
- 各子命令的具体输出格式定义在对应 procedures 文件中

## §4 降级行为

降级矩阵定义于 `knowledge/_schema/integration/sync-mapping-format.md` "降级行为" section（权威源）。各子命令步骤中已内嵌具体降级逻辑。

## §5 与现有 Skill 的集成

| Skill | 集成方式 |
|-------|---------|
| pace-dev | CR 状态转换后 sync-push Hook 提醒运行 /pace-sync 同步 |
| pace-change | 变更操作后同步状态到外部 |
| pace-release | Release 状态变化同步（Phase 19） |
| pace-review | Gate 结果自动推送 Comment + 标签（post-cr-update Hook 触发） |
| pace-status | 展示同步状态和外部链接 |
| pace-dev（CR 创建） | CR created → post-cr-update Hook 触发 auto-link/create |

## §6 操作语义词表

所有 procedures 使用平台无关的操作语义描述步骤。Claude 在适配器文件（如 `sync-adapter-github.md`）的操作表中查找对应的平台命令执行。

### 已有操作语义（通用）

| 操作语义 | 说明 |
|---------|------|
| 验证连接 | 检查外部平台可访问 |
| 创建工作项 | 创建外部 Issue/工作项（含 entity_type 参数） |
| 获取状态 | 查询外部实体当前状态 |
| 更新状态标记 | 更新外部实体的状态标记（标签/字段） |
| 添加评论 | 在外部实体上添加 Comment |
| 关闭工作项 | 关闭外部实体 |
| 列出工作项 | 查询外部平台的实体列表 |
| 创建标签 | 预创建状态/类型标签 |

### 多实体扩展操作语义

| 操作语义 | 说明 |
|---------|------|
| 设置实体类型标记 | 标识实体类型（GitHub: 标签 / Jira: issueType / Linear: 类型参数） |
| 建立父子关系 | 建立 Issue 层级（GitHub: sub-issue / Jira: parent link） |
| 解除父子关系 | 取消 Issue 层级关系 |
| 获取实体类型状态映射 | 按实体类型查询对应的状态映射表 |
| 生成工作项描述 | 按实体类型+平台生成 Issue body（模板在适配器中定义） |
