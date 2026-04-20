# 同步映射配置格式契约

> **职责**：定义 integrations/sync-mapping.md 的结构。/pace-sync setup 创建，/pace-sync link 更新关联记录。

## §0 速查卡片

```
文件：.devpace/integrations/sync-mapping.md
可选文件——不存在时同步功能不可用，核心流程不受影响
包含：平台配置 + CR/Epic/BR/PF 状态映射 + 实体映射（含平台适配）+ Gate 结果同步 + 关联记录（含内容哈希）
写入规则：/pace-sync setup 创建，/pace-sync link 更新关联记录，/pace-sync 智能同步更新最后同步时间和内容哈希
```

## 文件结构

```markdown
# 同步映射配置

## 平台

- **类型**：[github | linear | jira | gitlab]
- **连接**：[owner/repo 或项目标识，如 myorg/myrepo]
- **同步模式**：[readonly | push | pull | bidirectional]
- **冲突策略**：[devpace-authoritative | external-authoritative | ask-user]
- **自动同步**：[suggest | auto | off]

## CR 状态映射

| devpace 状态 | 外部状态 | 同步方向 | 备注 |
|-------------|---------|---------|------|
| created | 待办 | ↔ | GitHub: `backlog` 标签 · Linear: Backlog 状态 |
| developing | 进行中 | ↔ | GitHub: `in-progress` 标签 · Linear: In Progress 状态 |
| verifying | 待审查 | → | GitHub: `needs-review` 标签 · Linear: In Review 状态 |
| in_review | 等待审批 | → | GitHub: `awaiting-approval` 标签 · Linear: In Review 状态 |
| approved | 已批准 | → | GitHub: `approved` 标签 · Linear: Done 状态 |
| merged | 已完成 | ↔ | GitHub: 关闭 Issue + `done` 标签 · Linear: Done 状态 |
| released | 已发布 | → | GitHub: `released` 标签 · Linear: Done 状态 |
| paused | 搁置 | ↔ | GitHub: `on-hold` 标签 · Linear: Paused 状态 |

## Epic 状态映射

| devpace 状态 | 外部状态 | 同步方向 | 备注 |
|-------------|---------|---------|------|
| 规划中 | 待办 | → | GitHub: `planning` 标签 · Jira: To Do |
| 进行中 | 进行中 | → | GitHub: `in-progress` 标签 · Jira: In Progress |
| 已完成 | 已完成 | → | GitHub: 关闭 Issue + `done` 标签 · Jira: Done |
| 已搁置 | 搁置 | → | GitHub: `on-hold` 标签 · Jira: On Hold |

> Epic/BR/PF 状态为 devpace 内部计算值（基于下游实体状态聚合），同步方向全部为 →（仅推送），外部平台不应反向修改。

## BR 状态映射

| devpace 状态 | 外部状态 | 同步方向 | 备注 |
|-------------|---------|---------|------|
| 待开始 | 待办 | → | GitHub: `backlog` 标签 |
| 进行中 | 进行中 | → | GitHub: `in-progress` 标签 |
| 已完成 | 已完成 | → | GitHub: 关闭 Issue + `done` 标签 |
| 暂停 | 搁置 | → | GitHub: `on-hold` 标签 |

## PF 状态映射

| devpace 状态 | 外部状态 | 同步方向 | 备注 |
|-------------|---------|---------|------|
| 待开始 | 待办 | → | GitHub: `backlog` 标签 |
| 进行中 | 进行中 | → | GitHub: `in-progress` 标签 |
| 全部CR完成 | 已完成 | → | GitHub: 关闭 Issue + `done` 标签 |
| 已发布 | 已发布 | → | GitHub: `released` 标签 |
| 暂停 | 搁置 | → | GitHub: `on-hold` 标签 |

## 实体映射

| devpace 概念 | 默认外部概念 | 层级关系 | 平台适配 |
|-------------|------------|---------|---------|
| Epic（史诗） | Issue/Epic | 无父级 | GitHub: Issue+`devpace:epic`标签 · Jira: Epic（原生类型） · Linear: Project/Issue |
| BR（业务需求） | Issue/Story | Epic 的子级 | GitHub: Issue+`devpace:br`标签+sub-issue · Jira: Story+Epic Link · Linear: Issue+sub-issue |
| PF（产品功能） | Issue/Task | BR 的子级 | GitHub: Issue+`devpace:pf`标签+sub-issue · Jira: Task+parent · Linear: Issue+sub-issue |
| CR（变更请求） | Issue/Sub-task | PF 的子级 | GitHub: Issue+`devpace:cr`标签+sub-issue · Jira: Sub-task · Linear: Sub-Issue |
| Release | Release | — | GitHub: GitHub Release · Jira: Fix Version · Linear: — |

## Gate 结果同步

### Gate 1（开发完成门禁）

| 结果 | 外部动作 | 说明 |
|------|---------|------|
| 通过 | Comment + gate-1-passed 标签 | 在关联 Issue 添加通过评论和标签 |
| 未通过 | Comment（含失败摘要） | 在关联 Issue 添加失败原因评论 |

### Gate 2（审批门禁）

| 结果 | 外部动作 | 说明 |
|------|---------|------|
| 通过 | PR Review（approve） | 在关联 PR 提交 approve review |
| 未通过 | Comment（含未通过项） | 在关联 Issue 添加未通过详情评论 |

### Gate 3（发布门禁）

| 结果 | 外部动作 | 说明 |
|------|---------|------|
| 待处理 | PR Review（request changes）+ review 摘要 | 在关联 PR 请求变更并附摘要 |
| 通过 | Comment + gate-3-passed 标签 | 在关联 Issue 添加通过评论和标签 |

## 关联记录

<!-- 以下记录由 /pace-sync 自动维护，请勿手动编辑 -->

| 实体 | 外部实体 | 关联时间 | 最后同步 | 内容摘要哈希 |
|------|---------|---------|---------|------------|
| [EPIC-xxx / BR-xxx / PF-xxx / CR-xxx] | [平台#编号，如 github#42] | [YYYY-MM-DD HH:mm] | [YYYY-MM-DD HH:mm] | [8 位 hex] |
```

## 字段说明

### 平台

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 类型 | 外部平台标识，支持 github / linear / jira / gitlab | ✅ |
| 连接 | 平台连接标识，格式取决于平台类型（如 GitHub 为 owner/repo） | ✅ |
| 同步模式 | 数据流向控制：readonly（只读）/ push（仅推送）/ pull（仅拉取）/ bidirectional（双向） | ✅ |
| 冲突策略 | 双向同步时的冲突解决方式：devpace-authoritative / external-authoritative / ask-user | ❌ |
| 自动同步 | CR 创建时的外部同步行为：suggest（询问用户）/ auto（自动创建）/ off（关闭）。默认 suggest | ❌ |

**冲突策略说明**：
- `devpace-authoritative`：冲突时以 devpace 状态为准（默认值）
- `external-authoritative`：冲突时以外部平台状态为准
- `ask-user`：冲突时暂停并询问用户决定

**同步模式说明**：
- `readonly`：仅读取外部状态，不做任何写入。适合观察阶段
- `push`：devpace 状态变更时推送到外部，不读取外部变更
- `pull`：从外部拉取状态变更到 devpace，不推送
- `bidirectional`：双向同步，需配合冲突策略

### CR 状态映射

| 字段 | 说明 | 必填 |
|------|------|:----:|
| devpace 状态 | devpace CR 状态机中的状态值 | ✅ |
| 外部状态 | 对应的外部平台状态语义（具体执行见适配器文件） | ✅ |
| 同步方向 | ↔（双向）或 →（仅 devpace→外部） | ✅ |
| 备注 | 映射规则的补充说明 | ❌ |

**同步方向与同步模式的关系**：状态映射中的同步方向是逐状态的精细控制。实际生效的方向取"平台同步模式"与"状态同步方向"的交集。例如平台同步模式为 push 时，即使状态映射标记为 ↔，实际也只执行 → 方向。

### 实体映射

| 字段 | 说明 | 必填 |
|------|------|:----:|
| devpace 概念 | devpace 价值链中的实体（Epic / BR / PF / CR / Release） | ✅ |
| 外部概念 | 对应的外部平台实体类型 | ✅ |
| 层级关系 | 父子 Issue 关系（sub-issue），平台支持时自动建立 | ❌ |
| 说明 | 映射关系的补充说明 | ❌ |

### Gate 结果同步

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 结果 | Gate 检查的结果状态 | ✅ |
| 外部动作 | 在外部平台执行的动作（Comment / Label / PR Review） | ✅ |
| 说明 | 动作的补充说明 | ❌ |

### Epic/BR/PF 状态映射

字段结构与 CR 状态映射相同。同步方向全部为 `→`（仅推送），因为 Epic/BR/PF 状态是 devpace 内部基于下游实体聚合计算的值。

### 关联记录

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 实体 | devpace 实体编号（EPIC-xxx / BR-xxx / PF-xxx / CR-xxx） | ✅ |
| 外部实体 | 外部平台实体标识（格式：平台#编号，如 github#42） | ✅ |
| 关联时间 | 首次建立关联的时间戳（YYYY-MM-DD HH:mm） | ✅ |
| 最后同步 | 最近一次成功同步的时间戳（YYYY-MM-DD HH:mm） | ✅ |
| 内容摘要哈希 | 实体关键字段的 MD5 前 8 位 hex（用于增量同步检测）。由 `skills/pace-sync/scripts/compute-sync-diff.mjs` 脚本计算。 | ❌ |

**向后兼容**：旧格式列名 `CR` 等价 `实体`；`内容摘要哈希` 列缺失时视为空（首次同步时自动补填）。

## 降级行为

当 `integrations/sync-mapping.md` 不存在时：
- /pace-sync：所有子命令提示先运行 `/pace-sync setup` 创建映射配置
- /pace-dev、/pace-change：不显示同步提醒
- /pace-test：Gate 结果不推送到外部平台
- /pace-release：Release 不同步到外部平台
- 核心流程（CR 状态机、质量门、变更管理）完全不受影响

当映射配置存在但部分 section 或字段缺失时：
- 缺少"平台"：视为配置损坏，所有子命令提示重新运行 `/pace-sync setup`
- 缺少"自动同步"字段：默认 `suggest`（询问用户确认）
- 缺少"冲突策略"字段：默认 `devpace-authoritative`
- 缺少"CR 状态映射"：CR 状态变更不同步，其他功能正常
- 缺少"Epic/BR/PF 状态映射"：对应类型状态变更不同步，仅 CR 同步（向后兼容）
- 缺少"实体映射"：仅同步 CR 级别，Epic/BR/PF/Release 不同步
- 缺少"Gate 结果同步"：Gate 检查正常执行但结果不推送到外部
- 缺少"关联记录"：视为无已关联实体，/pace-sync link 时自动创建此 section
- 关联记录中无"内容摘要哈希"列：同步时视为首次同步（全量推送），推送后自动补填 hash
