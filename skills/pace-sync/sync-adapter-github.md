# GitHub 适配器（gh CLI）

> **职责**：定义 /pace-sync 在 GitHub 平台上的具体执行方式。sync-procedures-*.md 定义"做什么"（操作语义），本文件定义"在 GitHub 上怎么做"。新增平台时创建对应的 sync-adapter-{platform}.md 实现相同操作语义即可，无需修改 procedures。

## 前置条件

- `gh` CLI 已安装且已认证（`gh auth status`）
- 不可用时降级（sync-procedures-common.md §4 降级行为生效）

## 操作表

sync-procedures-*.md 使用"操作语义"描述步骤，Claude 在本表中查找对应 gh CLI 命令执行。

### 通用操作

| 操作语义 | gh CLI 命令 | 说明 |
|---------|------------|------|
| 验证连接 | `gh repo view {owner}/{repo} --json name` | 检查仓库可访问 |
| 创建工作项 | `gh issue create --title "{title}" --body "{body}" --label "{labels}"` | 创建 Issue（labels 含实体类型标签 + 状态标签） |
| 获取状态 | `gh issue view {number} --json state,labels,title,locked` | 查询 Issue 状态 |
| 更新状态标记 | `gh issue edit {number} --remove-label "{old}" --add-label "{new}"` | 标签增删 |
| 添加评论 | `gh issue comment {number} --body "{comment}"` | 写入 Comment |
| 关闭工作项 | `gh issue edit {number} --state closed` | 关闭 Issue |
| 列出工作项 | `gh issue list --json number,title,state,labels --limit 50` | 查询候选 |
| 创建标签 | `gh label create "{name}" --description "devpace sync" --color "{color}"` | 预创建标签 |

### 多实体扩展操作

| 操作语义 | gh CLI 命令 | 说明 |
|---------|------------|------|
| 设置实体类型标记 | `gh issue edit {number} --add-label "devpace:{type}"` | 添加实体类型标签 |
| 建立父子关系 | `gh issue edit {child} --add-parent {parent}` 或 GraphQL 回退 | 建立 sub-issue（详见层级操作 section） |
| 解除父子关系 | `gh issue edit {child} --remove-parent {parent}` 或 GraphQL 回退 | 解除 sub-issue |
| 获取实体类型状态映射 | 按实体类型查下方对应的状态更新策略表 | 无 CLI 命令，为查表操作 |
| 生成工作项描述 | 按实体类型使用下方工作项描述模板 | 无 CLI 命令，为模板填充 |

## CR 状态更新策略

GitHub 使用 Issue state（open/closed）+ 标签组合表示状态。

| devpace 状态 | GitHub 操作 |
|-------------|-----------|
| created | 确保 Issue open + 添加 `backlog` 标签 |
| developing | 移除 `backlog` + 添加 `in-progress` 标签 |
| verifying | 移除 `in-progress` + 添加 `needs-review` 标签 |
| in_review | 移除 `needs-review` + 添加 `awaiting-approval` 标签 |
| approved | 移除 `awaiting-approval` + 添加 `approved` 标签 |
| merged | 关闭 Issue + 添加 `done` 标签 |
| released | 添加 `released` 标签 |
| paused | 添加 `on-hold` 标签 |

## Epic 状态更新策略

| devpace 状态 | GitHub 操作 |
|-------------|-----------|
| 规划中 | 确保 Issue open + 添加 `planning` 标签 |
| 进行中 | 移除 `planning` + 添加 `in-progress` 标签 |
| 已完成 | 关闭 Issue + 添加 `done` 标签 |
| 已搁置 | 添加 `on-hold` 标签 |

## BR 状态更新策略

| devpace 状态 | GitHub 操作 |
|-------------|-----------|
| 待开始 | 确保 Issue open + 添加 `backlog` 标签 |
| 进行中 | 移除 `backlog` + 添加 `in-progress` 标签 |
| 已完成 | 关闭 Issue + 添加 `done` 标签 |
| 暂停 | 添加 `on-hold` 标签 |

## PF 状态更新策略

| devpace 状态 | GitHub 操作 |
|-------------|-----------|
| 待开始 | 确保 Issue open + 添加 `backlog` 标签 |
| 进行中 | 移除 `backlog` + 添加 `in-progress` 标签 |
| 全部CR完成 | 关闭 Issue + 添加 `done` 标签 |
| 已发布 | 添加 `released` 标签 |
| 暂停 | 添加 `on-hold` 标签 |

## 工作项描述模板

### Epic Issue Body

```markdown
## {Epic 标题}

**业务目标**：{OBJ 关联}
**状态**：{当前状态}

### 背景
{背景描述}

### 成效指标
{MoS 列表}

### 业务需求
| BR | 标题 | 优先级 | 状态 |
|----|------|--------|------|
{BR 表格行}

---
_由 devpace 自动创建 · 类型：Epic_
```

### BR Issue Body

```markdown
## {BR 标题}

**Epic**：{Epic 名称}（{EPIC-ID}）
**优先级**：{P0/P1/P2}
**状态**：{当前状态}

### 业务上下文
{业务上下文描述}

### 产品功能
| PF | 标题 | 状态 |
|----|------|------|
{PF 表格行}

---
_由 devpace 自动创建 · 类型：BR_
```

### PF Issue Body

```markdown
## {PF 标题}

**业务需求**：{BR 名称}（{BR-ID}）
**用户故事**：{用户故事}
**状态**：{当前状态}

### 验收标准
{验收标准列表}

### 关联 CR
| CR | 状态 | 标题 |
|----|------|------|
{CR 表格行}

---
_由 devpace 自动创建 · 类型：PF_
```

### CR Issue Body（沿用现有模板）

```markdown
## {CR 标题}

**意图**：{意图描述}

**验收条件**：
{逐条列出验收条件}

**关联功能**：{PF 名称}

---
_由 devpace 自动创建 · 类型：CR_
```

## 实体类型标签

GitHub Issue 无原生类型字段，使用标签区分实体类型。

| 标签 | 颜色 | 说明 |
|------|------|------|
| `devpace:epic` | `7057ff`（紫色） | Epic 类型标识 |
| `devpace:br` | `0075ca`（蓝色） | BR 类型标识 |
| `devpace:pf` | `1a7f37`（绿色） | PF 类型标识 |
| `devpace:cr` | `e4e669`（黄色） | CR 类型标识 |

> **平台差异**：Jira 使用原生 issueType 字段（Epic/Story/Task/Sub-task），Linear 使用创建时的类型参数。仅 GitHub 需要通过标签实现类型区分。

## setup 补充步骤

### 标签预创建

setup 完成基础配置后，预创建所有映射标签：

```bash
# 状态标签
for label in backlog in-progress needs-review awaiting-approval approved done released on-hold planning gate-1-passed gate-2-passed gate-3-passed; do
  gh label create "$label" --description "devpace sync" --color "ededed" 2>/dev/null || true
done

# 实体类型标签
gh label create "devpace:epic" --description "devpace Epic" --color "7057ff" 2>/dev/null || true
gh label create "devpace:br" --description "devpace BR" --color "0075ca" 2>/dev/null || true
gh label create "devpace:pf" --description "devpace PF" --color "1a7f37" 2>/dev/null || true
gh label create "devpace:cr" --description "devpace CR" --color "e4e669" 2>/dev/null || true
```

gh 不可用时跳过，在配置摘要中标注"标签未预创建"。

## Issue 状态预检查（push 前）

push 前检查目标 Issue 是否可更新：
- state=closed 且 devpace 状态非 merged/released/已完成 → 警告跳过
- locked=true → 警告跳过

## Gate 结果标签

| Gate | 结果 | 标签操作 |
|------|------|---------|
| Gate 1 | 通过 | 添加 `gate-1-passed` 标签 |
| Gate 2 | 通过 | 添加 `gate-2-passed` 标签 |
| Gate 3 | 通过 | 添加 `gate-3-passed` 标签 |

未通过时仅添加 Comment，不添加标签。

## 层级操作（Sub-Issue）

GitHub Sub-Issue 功能将 devpace 价值链层级映射到 Issue 父子关系。

### 主要方式：gh CLI（≥ 2.63.0）

| 操作语义 | gh CLI 命令 | 说明 |
|---------|------------|------|
| 建立父子关系 | `gh issue edit {child} --add-parent {parent}` | 建立 sub-issue |
| 解除父子关系 | `gh issue edit {child} --remove-parent {parent}` | 解除 sub-issue |
| 列出子 Issue | `gh issue view {parent} --json subIssues` | 查询子 Issue 列表 |

### 回退方式：GraphQL API（gh CLI 不支持 --add-parent 时）

```bash
gh api graphql -f query='
  mutation($parentId: ID!, $childId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $childId}) {
      issue { number }
      subIssue { number }
    }
  }' -f parentId="$(gh issue view {parent} --json id -q .id)" \
     -f childId="$(gh issue view {child} --json id -q .id)"
```

### 脚本封装

层级操作通过封装脚本执行，自动处理版本检测与降级：

```bash
# 单个操作
node $PLUGIN_DIR/skills/scripts/manage-sub-issues.mjs --action add --child {child_number} --parent {parent_number} --repo {owner/repo}

# 批量操作
echo '[{"child":6,"parent":2},{"child":7,"parent":3}]' | \
  node $PLUGIN_DIR/skills/scripts/manage-sub-issues.mjs --action add --repo {owner/repo} --batch

# 能力检测
node $PLUGIN_DIR/skills/scripts/manage-sub-issues.mjs --action check --repo {owner/repo}
```

### 版本检测与降级

版本检测由 `manage-sub-issues.mjs --action check` 执行，结果在进程内缓存：

| 缓存层级 | 方式 | 有效期 |
|---------|------|-------|
| 脚本进程内 | 全局变量 | 进程生命周期（批量操作自动复用） |
| 单次同步会话 | `--method cli\|graphql` 参数传递 | Claude 在同一次 /pace-sync 中缓存并传递 |

**检测流程**：
1. 执行 `gh issue edit --help 2>&1` → 检查输出是否包含 `--add-parent`
2. 包含 → `method: "cli"`，使用 gh CLI 原生命令
3. 不包含 → 尝试 GraphQL `addSubIssue` 测试 → 成功则 `method: "graphql"`
4. GraphQL 也失败（仓库未启用 sub-issue）→ `method: "unavailable"`，所有层级操作静默跳过

### 层级映射规则

| devpace 层级 | GitHub 映射 | 父 Issue 来源 |
|-------------|-----------|-------------|
| Epic → BR | Epic Issue → BR sub-issue | Epic 外部关联 |
| BR → PF | BR Issue → PF sub-issue | BR 外部关联 |
| PF → CR | PF Issue → CR sub-issue | PF 外部关联 |

**执行规则**：
- 创建任何实体 Issue 时，查找其上级实体的外部关联。有 → 自动添加为上级 Issue 的 sub-issue
- sub-issue 操作失败 → 静默跳过，不影响 Issue 创建

### 实体-Issue ID 双向标记

Issue 创建/关联成功后：
- 实体文件（独立文件）：`**外部关联**` 字段写入 Issue 链接
- 内联实体：仅更新 sync-mapping.md 关联记录
- Issue body：附带 `_由 devpace 自动创建 · 类型：{type}_` 标记

## 限流保护

每次 API 调用后等待 1 秒。检测到 403/429 → 暂停 60 秒重试 1 次。重试仍失败 → 标记跳过。
