# devpace 可选功能规则

> **职责**：定义条件生效的可选功能——发布管理、运维反馈、集成管理、同步管理。从 `devpace-rules.md §14` 拆分。

## §0 速查卡片

- 条件生效：对应目录/文件存在时自动启用，不存在时静默跳过
- Release：`releases/` 存在 → 发布管理生效；merged 仍是有效终态
- 反馈：`.devpace/` 存在即可用；`releases/` 启用完整追溯
- 集成：`integrations/config.md` 存在 → 集成管理生效
- 同步：`integrations/sync-mapping.md` 存在 → 同步管理生效（详见 `rules/devpace-rules-sync.md`）

## §14 可选功能（条件生效）

> **核心**：Release/集成/反馈在对应目录存在时自动生效，不存在静默跳过。

以下功能在对应目录存在时自动生效，不存在时静默跳过：

| 功能 | 前置条件 | 详细规则 |
|------|---------|---------|
| 发布管理 | `.devpace/releases/` 存在 | `skills/pace-release/release-procedures-*.md`（按 SKILL.md 路由表按需加载） |
| 运维反馈 | `.devpace/` 存在（完整模式需 `releases/`） | `skills/pace-feedback/feedback-procedures-*.md` |
| 集成管理 | `.devpace/integrations/config.md` 存在 | `skills/pace-release/release-procedures-common.md`（集成管理规则） |
| 同步管理 | `.devpace/integrations/sync-mapping.md` 存在 | `skills/pace-sync/sync-procedures-*.md`（按 SKILL.md 路由表按需加载） |

Release 是可选功能——未配置时 merged 仍是有效终态。集成完全可选，手动摄入始终可用。
运维反馈在 `.devpace/` 存在时即可用——分类、CR 创建、改进记录功能完全独立；Release 追溯仅在 `releases/` 目录存在时启用（降级模式跳过追溯步骤）。

### 核心约束

- **渐进暴露**：用户层（create/deploy/verify/close/full/status）· 专家层（changelog/version/tag/notes/branch/rollback）
- **状态机**：staging→deployed→verified→closed（+ rolled_back）；deployed/verified 转换需人类确认
- **Gate 4 + 环境晋升**：可选系统级检查 + 逐环境部署验证（无配置降级直接部署）
- **Release close**：changelog + version + tag + 连锁更新——详见 `skills/pace-release/release-procedures-close.md` + `release-procedures-common.md`（权威源）
