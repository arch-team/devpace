# pace-sync 同步操作规程

> **职责**：定义 /pace-sync 各子命令的详细执行步骤。SKILL.md 定义"做什么"，本文件定义"怎么做"。

## §0 速查

| 子命令 | 前置条件 | 输出 |
|--------|---------|------|
| setup | gh CLI 可用 + git remote 已配置 | sync-mapping.md |
| link | sync-mapping.md 存在 + CR 存在 + 外部实体存在 | CR 外部关联 + 关联记录 |
| push | CR 已关联 | 外部状态更新 |
| status | sync-mapping.md 存在 | 同步状态表 |

## §1 适配器工具路由表

Claude 根据 sync-mapping.md 的"平台"字段选择工具。

### GitHub（gh CLI）

| 操作 | 命令 | 说明 |
|------|------|------|
| 验证连接 | `gh repo view {owner}/{repo} --json name` | 检查仓库可访问 |
| 创建 Issue | `gh issue create --title "{title}" --body "{body}" --label "{labels}"` | 创建工作项 |
| 更新标签 | `gh issue edit {number} --add-label "{label}" --remove-label "{old}"` | 更新状态标签 |
| 添加评论 | `gh issue comment {number} --body "{comment}"` | Gate 结果/状态变化 |
| 获取状态 | `gh issue view {number} --json state,labels,title` | 查询外部状态 |
| 列出 Issue | `gh issue list --json number,title,state,labels --limit 50` | 查询关联候选 |

### Linear（MCP）——Phase 19+

| 操作 | 工具 |
|------|------|
| 创建 Issue | `mcp__linear__create_issue` |
| 更新状态 | `mcp__linear__update_issue` |
| 添加评论 | `mcp__linear__create_comment` |
| 获取状态 | `mcp__linear__get_issue` |

### Jira（MCP/CLI）——Phase 19+

预留，具体工具路由待 Phase 19 定义。

## §2 setup — 引导式配置

**前置检查**：
1. 检查 `gh` CLI 是否可用：`gh --version`（不可用 → 提示安装，不阻断）
2. 检查 `.devpace/` 是否存在（不存在 → 引导 /pace-init）

**执行步骤**：
1. 读取 git remote：`git remote get-url origin` → 提取 owner/repo
2. 向用户确认：
   - 仓库：{owner}/{repo}
   - 同步模式：push（推荐 MVP）/ bidirectional
   - 冲突策略：ask-user（推荐 MVP）
3. 验证连接：`gh repo view {owner}/{repo} --json name`
4. 生成 `.devpace/integrations/sync-mapping.md`（按 Plugin `knowledge/_schema/sync-mapping-format.md` Schema）
5. 更新 `.devpace/integrations/config.md` 的"外部同步"section（如 config.md 存在）
6. 输出配置摘要

**配置摘要格式**：
```
同步配置完成：
- 平台：GitHub ({owner}/{repo})
- 同步模式：push
- 连接状态：✅ 已验证 / ⚠️ 未验证（gh 不可用）
下一步：用 /pace-sync link CR-xxx #Issue编号 关联变更请求
```

**降级**：gh 不可用时仍生成配置文件，标注"连接未验证"。

## §3 link — 关联 CR 与外部实体

**输入解析**：`$1` = CR-ID（如 CR-003 或 003），`$2` = 外部 ID（如 #42 或 42）

**执行步骤**：
1. 验证 CR 存在：检查 `.devpace/backlog/CR-{id}.md`
2. 验证外部实体存在：`gh issue view {number} --json number,title,state`（GitHub）
3. 写入 CR 文件"外部关联"字段：`[github:#{number}]({url})`
4. 更新 sync-mapping.md 关联记录表（追加行）
5. 输出确认：CR-{id} ↔ Issue #{number} 已关联

**关联记录行格式**（按 Plugin `knowledge/_schema/sync-mapping-format.md`）：
```markdown
| CR-{id} | github#{number} | {YYYY-MM-DD HH:mm} | — |
```

**错误处理**：
- CR 不存在 → 提示用户
- 外部实体不存在 → 提示用户确认 ID
- CR 已有关联 → 提示已关联，确认是否覆盖

## §4 push — 推送状态到外部

**输入**：`$1` = CR-ID（可选，省略则推送所有已关联 CR）

**执行步骤**：
1. 读取 sync-mapping.md 关联记录
2. 对每个目标 CR：
   a. 读取 CR 当前状态
   b. 查询状态映射表 → 获取对应外部状态和标签
   c. 查询外部当前状态：`gh issue view {number} --json state,labels`
   d. 比较：一致 → 跳过，不一致 → 执行更新
   e. 更新外部状态：
      - 标签更新：先移除旧状态标签，再添加新标签
      - 添加 Comment：说明状态变更原因
   f. 更新 sync-mapping.md 最后同步时间
3. 输出同步结果表

**状态映射执行**（按 Plugin `knowledge/_schema/sync-mapping-format.md` 的 CR 状态映射表）：

| devpace 状态 | 外部操作 |
|-------------|---------|
| created | 确保 Issue open + 添加 `backlog` 标签 |
| developing | 移除 `backlog` + 添加 `in-progress` 标签 |
| verifying | 移除 `in-progress` + 添加 `needs-review` 标签 |
| in_review | 移除 `needs-review` + 添加 `awaiting-approval` 标签 |
| merged | 关闭 Issue + 添加 `done` 标签 |
| paused | 添加 `on-hold` 标签 |

**标签更新命令**（GitHub）：
```bash
# 移除旧标签
gh issue edit {number} --remove-label "{old_label}"
# 添加新标签
gh issue edit {number} --add-label "{new_label}"
```

**Comment 格式**：
```
🔄 devpace sync: CR 状态变更为 [{状态}]
---
变更请求：{CR 标题}
时间：{时间}
```

**同步结果表格式**：
```
| CR | 状态 | 外部操作 | 结果 |
|----|------|---------|------|
| CR-003 | developing | 添加 in-progress 标签 | ✅ |
| CR-005 | merged | 关闭 Issue #18 | ✅ |
```

## §5 status — 同步状态查看

**执行步骤**：
1. 读取 sync-mapping.md
2. 对每个关联记录：
   a. 读取 CR 当前状态
   b. 查询外部当前状态（可选——gh 不可用时显示"未知"）
   c. 比较一致性
3. 输出同步状态表

**输出格式**：
```
| CR | 外部链接 | devpace 状态 | 外部状态 | 一致性 | 最后同步 |
|----|---------|-------------|---------|--------|---------|
| CR-003 | [#42](url) | developing | in-progress | ✅ | 02-25 10:30 |
| CR-005 | [#18](url) | merged | open | ❌ 需推送 | 02-24 15:00 |
```

**无关联记录时**：
```
当前没有已关联的外部实体。
用 /pace-sync link CR-xxx #Issue编号 创建关联。
```

## §6 降级行为

| 条件 | 行为 |
|------|------|
| sync-mapping.md 不存在 | 所有子命令 → 引导 setup |
| config.md 无"外部同步"section | 仅依赖 sync-mapping.md，不报错 |
| gh CLI 不可用 | setup 仍可生成配置（标注未验证）；push/status 报错并提示安装 |
| 外部实体已删除 | push 时报错，建议 unlink |
| CR 无外部关联 | push 跳过，status 显示"未关联" |

## §7 与现有 Skill 的集成

| Skill | 集成方式 |
|-------|---------|
| pace-dev | CR 状态转换后 sync-push Hook 提醒推送 |
| pace-change | 变更操作后同步状态到外部 |
| pace-release | Release 状态变化同步（Phase 19） |
| pace-review | Gate 2 结果同步为 PR Review（Phase 19） |
| pace-status | 展示同步状态和外部链接 |
