# pace-sync 同步操作规程

> **职责**：定义 /pace-sync 各子命令的详细执行步骤。SKILL.md 定义"做什么"，本文件定义"怎么做"。

## §0 速查

| 子命令 | 前置条件 | 输出 |
|--------|---------|------|
| setup | gh CLI 可用 + git remote 已配置 | sync-mapping.md |
| link | sync-mapping.md 存在 + CR 存在 + 外部实体存在 | CR 外部关联 + 关联记录 |
| push | CR 已关联 | 外部状态更新 |
| unlink | CR 存在 + 有外部关联 | 关联解除确认 |
| create | CR 存在 + sync-mapping.md 存在 + gh 可用 | 创建 Issue + 自动关联 |
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
5. 预创建映射标签：按 CR 状态映射表在 GitHub 仓库中预创建所有必需标签
   ```bash
   # 检查并创建标签（不存在时创建，已存在时跳过）
   for label in backlog in-progress needs-review awaiting-approval done on-hold; do
     gh label create "$label" --description "devpace sync" --color "ededed" 2>/dev/null || true
   done
   ```
   - gh 不可用时跳过，在配置摘要中标注"标签未预创建"
6. 更新 `.devpace/integrations/config.md` 的"外部同步"section（如 config.md 存在）
7. 输出配置摘要

**配置摘要格式**：
```
同步配置完成：
- 平台：GitHub ({owner}/{repo})
- 同步模式：push
- 连接状态：✅ 已验证 / ⚠️ 未验证（gh 不可用）
- 标签状态：✅ 已预创建 / ⚠️ 标签未预创建（gh 不可用）
下一步：用 /pace-sync link CR-xxx #Issue编号 关联变更请求
```

**降级**：gh 不可用时仍生成配置文件，标注"连接未验证"。

## §3 link — 关联 CR 与外部实体

**输入解析**：`$1` = CR-ID（如 CR-003 或 003），`$2` = 外部 ID（如 #42 或 42）

**执行步骤**：
1. 验证 CR 存在：检查 `.devpace/backlog/CR-{id}.md`
2. 验证外部实体存在：`gh issue view {number} --json number,title,state`（GitHub）
3. 写入 CR 文件"外部关联"字段：`[github:#<number>](https://github.com/<owner>/<repo>/issues/<number>)`
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

**模式检测**：`$ARGUMENTS` 包含 `--dry-run` 时进入预览模式。

**执行步骤**：
1. 读取 sync-mapping.md 关联记录
2. 对每个目标 CR：
   a. 读取 CR 当前状态
   b. 查询状态映射表 → 获取对应外部状态和标签
   c. 查询外部当前状态：`gh issue view {number} --json state,labels`
   c2. **Issue 状态检查**：验证外部 Issue 可更新
       - Issue 已关闭（state=closed）且 devpace 状态非 merged/released → 输出警告"Issue #{number} 已关闭，跳过更新。建议 unlink 或手动重开"
       - Issue 已锁定（locked=true）→ 输出警告"Issue #{number} 已锁定，跳过更新"
       - 状态检查通过 → 继续执行
   d. 比较：一致 → 跳过，不一致 → 执行更新
   d2. **dry-run 模式**：输出将要执行的操作后停止，不实际执行。预览格式：`[预览] 将对 CR-{id} (#{number}) 执行：移除标签 {old} / 添加标签 {new} / 添加 Comment`。所有 CR 处理完后输出汇总表（同正常模式格式，结果列显示"预览"）
   e. 更新外部状态：
      - 标签更新：先移除旧状态标签，再添加新标签
      - 添加 Comment：说明状态变更原因
   f. 更新 sync-mapping.md 最后同步时间
   g. **限流保护**：每次外部 API 调用后等待 1 秒（避免 GitHub rate limit）
      - 检测到 403/429 响应 → 暂停 60 秒后重试 1 次
      - 重试仍失败 → 标记该 CR 为"跳过（限流）"，继续处理下一个
      - 批量推送完成后，汇总被跳过的 CR 列表
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

**语义 Comment 生成规则**（替代固定模板）：

Claude 读取 CR 上下文后生成语义丰富的 Comment，而不是套用固定模板。

**信息采集**：
1. CR 标题和意图描述
2. 当前状态和转换原因
3. 最近的 Gate 结果（如有）
4. 关键验收条件达成情况（如有）

**Comment 格式**：
```
🔄 [{状态}] {CR 标题}

{1-2 句上下文说明，如"用户认证模块进入审查，Gate 1 已通过 12/12 检查项"}

{仅在 merged 时附加：关键交付摘要}
```

**约束**：
- 不超过 5 行
- 不包含 devpace 内部术语（如 checkpoint、state.md）
- 信息采集失败时回退到简单格式：`🔄 [{状态}] {CR 标题}`

**同步结果表格式**：
```
| CR | 状态 | 外部操作 | 结果 |
|----|------|---------|------|
| CR-003 | developing | 添加 in-progress 标签 | ✅ |
| CR-005 | merged | 关闭 Issue #18 | ✅ |
```

### §4.8 Gate 结果同步

Gate 检查完成时，如果 CR 有外部关联，自动推送结果到外部。

**触发时机**：Gate 1 完成后 | Gate 2 完成后 | Gate 3 待处理时

**同步动作**（按 sync-mapping-format.md "Gate 结果同步" section）：

| Gate | 结果 | 外部操作 |
|------|------|---------|
| Gate 1 | 通过 | Comment（检查通过摘要）+ `gate-1-passed` 标签 |
| Gate 1 | 未通过 | Comment（失败项摘要） |
| Gate 2 | 通过 | Comment（审查通过）+ `gate-2-passed` 标签 |
| Gate 2 | 未通过 | Comment（未通过项列表） |
| Gate 3 | 待处理 | Comment（审批摘要）+ 请求 review |
| Gate 3 | 通过 | Comment（已批准）+ `gate-3-passed` 标签 |

**Comment 格式**（遵循语义 Comment 规则）：
```
✅ Gate {N} 通过：{1 句摘要}
```
或
```
❌ Gate {N} 未通过：{失败项数}/{总数}，主要问题：{问题摘要}
```

**约束**：
- sync-mapping.md 不存在 → 静默跳过
- CR 无外部关联 → 静默跳过
- gh 不可用 → 在 Gate 结果输出中附加提醒"外部同步失败"

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
| CR-003 | #42 | developing | in-progress | ✅ | 02-25 10:30 |
| CR-005 | #18 | merged | open | ❌ 需推送 | 02-24 15:00 |
```

**无关联记录时**：
```
当前没有已关联的外部实体。
用 /pace-sync link CR-xxx #Issue编号 创建关联。
```

## §5.5 unlink — 解除关联

**输入**：`$1` = CR-ID

**执行步骤**：
1. 验证 CR 存在且有外部关联
2. 清除 CR 文件中的"外部关联"字段
3. 从 sync-mapping.md 关联记录表中移除对应行
4. 输出确认：CR-{id} 已解除与 {外部实体} 的关联

**错误处理**：
- CR 无外部关联 → 提示"CR-{id} 当前没有外部关联"
- CR 不存在 → 提示用户

## §5.6 create — 从 CR 创建外部 Issue

**输入**：`$1` = CR-ID

**执行步骤**：
1. 验证 CR 存在且无外部关联
2. 读取 CR 元数据：标题、意图描述、验收条件、关联 PF
3. 生成 Issue body：
   ```
   ## 变更请求：{CR 标题}

   **意图**：{意图描述}

   **验收条件**：
   {逐条列出验收条件}

   **关联功能**：{PF 名称}

   ---
   _由 devpace 自动创建_
   ```
4. 查询状态映射表获取当前状态对应标签
5. 创建 Issue：`gh issue create --title "{CR 标题}" --body "{body}" --label "{label}"`
6. 自动执行 link（复用 §3 流程）
7. 输出确认：CR-{id} → Issue #{number} 已创建并关联

**错误处理**：
- CR 已有外部关联 → 提示已关联，确认是否创建新 Issue 并覆盖
- gh 不可用 → 提示安装
- CR 不存在 → 提示用户

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
