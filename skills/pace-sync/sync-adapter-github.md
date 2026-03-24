# GitHub 适配器（gh CLI）

> **职责**：定义 /pace-sync 在 GitHub 平台上的具体执行方式。sync-procedures-*.md 定义"做什么"，本文件定义"在 GitHub 上怎么做"。

## 前置条件

- `gh` CLI 已安装且已认证（`gh auth status`）
- 不可用时降级（sync-procedures-common.md §4 降级行为生效）

## 操作表

sync-procedures-*.md 子命令使用"操作语义"描述步骤，Claude 在本表中查找对应 gh CLI 命令执行。

| 操作语义 | gh CLI 命令 | 说明 |
|---------|------------|------|
| 验证连接 | `gh repo view {owner}/{repo} --json name` | 检查仓库可访问 |
| 创建工作项 | `gh issue create --title "{title}" --body "{body}" --label "{labels}"` | 创建 Issue |
| 获取状态 | `gh issue view {number} --json state,labels,title,locked` | 查询 Issue 状态 |
| 更新状态标记 | `gh issue edit {number} --remove-label "{old}" --add-label "{new}"` | 标签增删 |
| 添加评论 | `gh issue comment {number} --body "{comment}"` | 写入 Comment |
| 关闭工作项 | `gh issue edit {number} --state closed` | 关闭 Issue |
| 列出工作项 | `gh issue list --json number,title,state,labels --limit 50` | 查询候选 |
| 创建标签 | `gh label create "{name}" --description "devpace sync" --color "ededed"` | 预创建标签 |

## 状态更新策略

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

## setup 补充步骤

### 标签预创建

setup 完成基础配置后，预创建所有映射标签：

```bash
for label in backlog in-progress needs-review awaiting-approval approved done released on-hold gate-1-passed gate-2-passed gate-3-passed; do
  gh label create "$label" --description "devpace sync" --color "ededed" 2>/dev/null || true
done
```

gh 不可用时跳过，在配置摘要中标注"标签未预创建"。

## Issue 状态预检查（push 前）

push 前检查目标 Issue 是否可更新：
- state=closed 且 devpace 状态非 merged/released → 警告跳过
- locked=true → 警告跳过

## Gate 结果标签

| Gate | 结果 | 标签操作 |
|------|------|---------|
| Gate 1 | 通过 | 添加 `gate-1-passed` 标签 |
| Gate 2 | 通过 | 添加 `gate-2-passed` 标签 |
| Gate 3 | 通过 | 添加 `gate-3-passed` 标签 |

未通过时仅添加 Comment，不添加标签。

> **Phase 19 扩展**：Schema 定义的 Gate 2 PR Review（approve）和 Gate 3 PR Review（request changes）操作在 Phase 19 实现。当前 MVP 统一使用 Comment + 标签。

## 层级操作（Sub-Issue）

GitHub Sub-Issue 功能将 devpace 价值链层级映射到 Issue 父子关系。需要 GitHub Sub-Issues 功能已启用（仓库设置）。

### 主要方式：gh CLI（≥ 2.63.0）

| 操作语义 | gh CLI 命令 | 说明 |
|---------|------------|------|
| 添加子 Issue | `gh issue edit {child} --add-parent {parent}` | 建立父子关系 |
| 移除子 Issue | `gh issue edit {child} --remove-parent {parent}` | 解除父子关系 |
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

### 版本检测与降级

**执行顺序**：
1. 尝试 `gh issue edit {child} --add-parent {parent}`
2. 若报 `unknown flag: --add-parent` → 回退到 GraphQL API
3. 若 GraphQL 返回错误（仓库未启用 sub-issue）→ 静默跳过，输出提示"层级映射不可用：仓库未启用 Sub-Issues 功能"

### 层级映射规则

| devpace 层级 | GitHub 映射 | 父 Issue 来源 |
|-------------|-----------|-------------|
| Epic → BR | Epic Issue → BR sub-issue | Epic 外部关联 |
| BR → PF | BR Issue → PF sub-issue（若 BR 有外部关联） | BR 外部关联 |
| PF → CR | PF Issue → CR sub-issue | PF 外部关联 |

**执行规则**：
- 创建 CR Issue 时，查找 CR 所属 PF 的外部关联。有 → 自动添加为 PF Issue 的 sub-issue
- 创建 PF Issue 时，查找 PF 所属 BR 的外部关联。有 → 自动添加为 BR Issue 的 sub-issue
- sub-issue 操作失败（仓库未启用 sub-issue 功能）→ 静默跳过，不影响 Issue 创建

### CR-Issue ID 双向标记

Issue 创建/关联成功后：
- CR 文件：`**外部关联**` 字段已包含 Issue 链接
- Issue body：附带 `_由 devpace 自动创建_` 标记（create 流程已有）

## 限流保护

每次 API 调用后等待 1 秒。检测到 403/429 → 暂停 60 秒重试 1 次。重试仍失败 → 标记跳过。
