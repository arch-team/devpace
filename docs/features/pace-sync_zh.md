# 外部工具同步（`/pace-sync`）

devpace 是一个封闭系统——CR 状态完全存储在 `.devpace/` 内部。`/pace-sync` 通过**语义级同步**将 devpace 与 GitHub Issues 桥接：不是机械地将字段 A 映射到字段 B，而是 Claude 理解"这个变更请求正在被实现"后生成对应的外部操作。v1.5.0 作为 **push-only MVP** 发布；双向同步计划在 Phase 20 实现。

## 前置条件

| 条件 | 用途 | 是否必须 |
|------|------|:--------:|
| `gh` CLI | GitHub API 操作（标签、评论、Issue 状态） | 推荐 |
| `git remote` 已配置 | setup 时自动检测仓库 owner/name | 是 |
| `.devpace/` 已初始化 | 核心 devpace 项目结构 | 是 |

> **优雅降级**：如果 `gh` CLI 未安装，`setup` 仍会生成配置文件（标注"未验证"）。`push` 和 `status` 需要 `gh` 才能运行。

## 快速上手

```
1. /pace-sync setup            → 检测 git remote → 生成 sync-mapping.md
2. /pace-sync link CR-003 #42  → 关联 CR-003 与 GitHub Issue #42
3. /pace-sync push             → 推送状态 → Issue #42 标签更新
```

配置完成后，sync-push advisory hook 会在 CR 状态变更后自动提醒你推送。

## 命令参考

### `setup`

引导式配置向导。

**语法**：`/pace-sync setup`

**行为**：
1. 检查 `gh` CLI 可用性（`gh --version`）
2. 读取 git remote：`git remote get-url origin` → 提取 `owner/repo`
3. 向用户确认：仓库、同步模式（MVP 推荐 push）、冲突策略
4. 验证连接：`gh repo view {owner}/{repo} --json name`
5. 生成 `.devpace/integrations/sync-mapping.md`（按 [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) Schema）
6. 输出配置摘要

**输出示例**：
```
同步配置完成：
- 平台：GitHub (myorg/myrepo)
- 同步模式：push
- 连接状态：✅ 已验证
下一步：用 /pace-sync link CR-xxx #Issue编号 关联变更请求
```

**降级**：`gh` 不可用时仍创建配置文件，标注"连接未验证"。

### `link`

关联 CR 与外部实体。

**语法**：`/pace-sync link <CR-ID> <#外部ID>`

**参数**：
| 参数 | 格式 | 示例 |
|------|------|------|
| CR-ID | `CR-xxx` 或 `xxx` | `CR-003`、`003` |
| 外部 ID | `#number` 或 `number` | `#42`、`42` |

**行为**：
1. 验证 CR 存在：检查 `.devpace/backlog/CR-{id}.md`
2. 验证外部实体存在：`gh issue view {number} --json number,title,state`
3. 将外部关联字段写入 CR 文件
4. 在 sync-mapping.md 追加关联记录
5. 确认：`CR-{id} ↔ Issue #{number} 已关联`

**错误处理**：
- CR 不存在 → 提示用户
- 外部实体不存在 → 提示用户确认 ID
- CR 已有关联 → 确认后覆盖

### `push`

推送 devpace 状态到外部工具。

**语法**：`/pace-sync push [CR-ID]`

**参数**：
| 参数 | 行为 |
|------|------|
| `CR-ID` | 仅推送指定 CR |
| *（空）* | 推送所有已关联的 CR |

**行为**（每个已关联 CR）：
1. 读取 CR 当前状态
2. 查询状态映射表 → 确定目标标签
3. 查询外部当前状态：`gh issue view {number} --json state,labels`
4. 比较：一致 → 跳过；不一致 → 更新
5. 更新外部状态：
   - 移除旧状态标签，添加新标签
   - 添加评论记录状态变更
6. 更新 sync-mapping.md 最后同步时间

**输出示例**：
```
| CR     | 状态       | 外部操作              | 结果 |
|--------|------------|----------------------|------|
| CR-003 | developing | 添加标签 in-progress  | ✅   |
| CR-005 | merged     | 关闭 Issue #18 + done | ✅   |
```

### `status`

查看所有已关联 CR 的同步状态。

**语法**：`/pace-sync status`

**行为**：
1. 读取 sync-mapping.md 关联记录
2. 对每条记录：读取 CR 状态、查询外部状态（可选——`gh` 不可用时显示"未知"）、比较一致性
3. 输出同步状态表

**输出示例**：
```
| CR     | 外部链接 | devpace 状态 | 外部状态      | 一致性    | 最后同步    |
|--------|---------|-------------|--------------|----------|------------|
| CR-003 | #42     | developing  | in-progress  | ✅       | 02-25 10:30 |
| CR-005 | #18     | merged      | open         | ❌ 需推送 | 02-24 15:00 |
```

**无关联记录时**：
```
当前没有已关联的外部实体。
用 /pace-sync link CR-xxx #Issue编号 创建关联。
```

## 状态映射

devpace CR 状态与 GitHub Issue 标签的映射：

| devpace 状态 | GitHub 标签 | 方向 | 说明 |
|-------------|------------|:----:|------|
| `created` | `backlog` | ↔ | 新建 CR 对应 backlog 标签 |
| `developing` | `in-progress` | ↔ | 开发中 |
| `verifying` | `needs-review` | → | MVP 仅推送 |
| `in_review` | `awaiting-approval` | → | MVP 仅推送 |
| `approved` | `approved` | → | MVP 仅推送 |
| `merged` | 关闭 Issue + `done` | ↔ | 关闭 Issue |
| `released` | `released` | → | 仅推送 |
| `paused` | `on-hold` | ↔ | 暂停 |

**方向与同步模式的关系**：实际生效的同步方向取"平台同步模式"与"状态同步方向"的交集。当同步模式为 `push` 时，即使状态映射标记为 ↔，实际也只执行 → 方向。

## 使用场景

### 场景 1：首次配置

你有一个已有的 devpace 项目，想要开始与 GitHub Issues 同步。

```
你：    /pace-sync setup
Claude: 检测到仓库：myorg/my-project
        同步模式：push（MVP 推荐）
        冲突策略：ask-user
        是否验证连接？[Y/n]

你：    Y
Claude: ✅ 连接已验证
        配置已写入 .devpace/integrations/sync-mapping.md

        下一步：/pace-sync link CR-xxx #Issue编号
```

### 场景 2：日常开发推送

`/pace-dev` 将 CR-003 从 `created` 转换为 `developing` 后，sync-push hook 提醒你：

```
Hook:   devpace:sync-push CR state=developing, linked to github#42.
        Consider running /pace-sync push to sync status.

你：    /pace-sync push CR-003
Claude: | CR     | 状态       | 操作                 | 结果 |
        |--------|------------|---------------------|------|
        | CR-003 | developing | 添加标签 in-progress | ✅   |
```

### 场景 3：一致性检查

发布前验证所有 CR 同步状态：

```
你：    /pace-sync status
Claude: | CR     | 外部链接 | devpace    | 外部状态       | 一致 | 最后同步    |
        |--------|---------|------------|---------------|------|------------|
        | CR-003 | #42     | merged     | done (closed) | ✅   | 02-25 14:00 |
        | CR-005 | #18     | developing | backlog       | ❌   | 02-24 15:00 |

        1 个 CR 未同步。运行 /pace-sync push 更新。
```

## 配置参考

同步配置存储在 `.devpace/integrations/sync-mapping.md`，遵循 [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) Schema。

### 平台

```markdown
## 平台

- **类型**：github
- **连接**：myorg/myrepo
- **同步模式**：push
- **冲突策略**：ask-user
```

| 字段 | 可选值 | 说明 |
|------|--------|------|
| 类型 | `github` / `linear` / `jira` / `gitlab` | 外部平台标识 |
| 连接 | 平台标识（如 GitHub 为 `owner/repo`） | 目标端点 |
| 同步模式 | `readonly` / `push` / `pull` / `bidirectional` | 数据流向 |
| 冲突策略 | `devpace-authoritative` / `external-authoritative` / `ask-user` | 双向冲突解决 |

### 状态映射表

可按项目自定义。默认映射（见上方[状态映射](#状态映射)）可修改为自定义标签名：

```markdown
| devpace 状态 | 外部状态                | 方向 | 备注           |
|-------------|------------------------|------|---------------|
| created     | open + my-custom-label | ↔    | 自定义标签名    |
```

### 实体映射

devpace 概念与外部平台概念的映射：

| devpace 概念 | 外部概念 | 说明 |
|-------------|---------|------|
| BR（业务需求） | Milestone | 业务目标对应里程碑 |
| PF（产品功能） | Epic / 大 Issue | 功能对应 Epic |
| CR（变更请求） | Issue | 变更请求对应 Issue |
| Release | Release | 发布对应平台 Release |

### 质量门结果同步

质量门结果可同步到外部工具：

| 质量门 | 通过动作 | 未通过动作 |
|--------|---------|-----------|
| Gate 1（开发完成） | 评论 + `gate-1-passed` 标签 | 评论（含失败摘要） |
| Gate 2（审批） | PR Review（approve） | 评论（含审查项） |
| Gate 3（发布） | 评论 + `gate-3-passed` 标签 | PR Review（request changes） |

## 与其他命令的集成

| 命令 | 集成方式 |
|------|---------|
| `/pace-dev` | CR 状态转换触发 sync-push hook 提醒 |
| `/pace-change` | 变更操作后同步状态到外部 |
| `/pace-release` | Release 状态同步（Phase 19） |
| `/pace-review` | Gate 2 结果同步为 PR Review（Phase 19） |
| `/pace-status` | 展示同步状态和外部链接 |

## 架构说明（开发者向）

### 语义桥接概念

传统集成做的是机械的"字段 A → 字段 B"映射。devpace 采取了根本不同的方法：

- **语义理解**：CR `developing` 不是简单映射为 GitHub `in-progress` 标签，而是 Claude 理解"这个变更请求正在被实现"后生成对应操作。
- **上下文动作**：外部 PR merge 不只是触发状态变化——Claude 理解"代码已合入，需要推进质量门检查"。
- **智能冲突解决**：冲突不是用"谁赢"的规则解决，而是 Claude 分析双方上下文后给出建议。

### 分层架构

```
┌──────────────────────────────────┐
│        pace-sync Skill 层        │
│  setup / link / push / status    │
├──────────────────────────────────┤
│      语义桥接层（核心价值）        │
│  意图映射 + 冲突检测 + 适配器路由  │
├──────────────────────────────────┤
│    现有 MCP/CLI（不自建）         │
│  gh CLI / Linear MCP / Jira MCP  │
├──────────────────────────────────┤
│           配置层                  │
│  sync-mapping.md + config.md     │
└──────────────────────────────────┘
```

**关键决策**：devpace **不**自建 MCP Server——GitHub、Linear、Jira、GitLab 都有成熟的现有工具。devpace 专注于语义编排层。

### 适配器路由

| 操作 | GitHub (gh CLI) | Linear (MCP) | Jira (MCP/CLI) |
|------|----------------|--------------|----------------|
| 创建工作项 | `gh issue create` | `mcp__linear__create_issue` | Phase 19+ |
| 更新状态 | `gh issue edit --add-label` | `mcp__linear__update_issue` | Phase 19+ |
| 添加评论 | `gh issue comment` | `mcp__linear__create_comment` | Phase 19+ |
| 获取状态 | `gh issue view --json` | `mcp__linear__get_issue` | Phase 19+ |

MVP 默认使用 GitHub（通过 gh CLI，零额外依赖）。

### 扩展点

添加新平台适配器的步骤：

1. 在 sync-mapping-format.md 的 `类型` 字段添加新平台值
2. 在 `sync-procedures.md §1` 添加工具路由 section
3. 添加该平台的默认状态映射
4. 无需修改 Skill——适配器路由在 procedures 层

## 降级行为与故障排除

### 降级行为

| 条件 | 行为 |
|------|------|
| 无 sync-mapping.md | 所有子命令 → 引导运行 `setup` |
| `gh` CLI 不可用 | `setup` 生成配置（标注未验证）；`push`/`status` 不可用 |
| 外部实体已删除 | `push` 报错，建议 unlink |
| CR 无外部关联 | `push` 跳过，`status` 显示"未关联" |
| config.md 无同步 section | 仅依赖 sync-mapping.md，不报错 |

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `gh auth` 错误 | 未登录 | 运行 `gh auth login` |
| 标签不存在 | 自定义标签未创建 | 首次 push 时自动创建 |
| 仓库错误 | 多个 remote | 重新运行 `setup` 选择正确 remote |
| 同步状态过时 | 手动修改了外部状态 | 运行 `status` 检测漂移，再 `push` |

### Advisory Hook

`sync-push.mjs` hook（PostToolUse）监控 CR 文件写入。当已关联 CR 的状态变更时，输出非阻断提醒：

```
devpace:sync-push CR state=developing, linked to github#42.
Consider running /pace-sync push to sync status.
```

此 hook 永远不阻断工作流（始终 exit 0）。

## 路线图

| 阶段 | 功能 | 状态 |
|------|------|------|
| Phase 18 (v1.5.0) | 手动推送 + GitHub MVP（`setup`/`link`/`push`/`status`） | ✅ 当前 |
| Phase 19 | 状态变更自动推送 + 多平台（Linear、Jira）+ `pull` 子命令 | 计划中 |
| Phase 20 | 双向同步 + AI 冲突解决 + `sync`/`resolve` 子命令 | 计划中 |

## 相关资源

- [用户指南 — /pace-sync 章节](../user-guide_zh.md) — 快速参考
- [设计文档 §19](../design/design.md) — 架构决策
- [sync-mapping-format.md](../../knowledge/_schema/sync-mapping-format.md) — 配置格式 Schema
- [sync-procedures.md](../../skills/pace-sync/sync-procedures.md) — 详细操作规程
- [devpace-rules.md §16](../../rules/devpace-rules.md) — 运行时行为规则
