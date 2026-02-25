# GitHub 适配器（gh CLI）

> **职责**：定义 /pace-sync 在 GitHub 平台上的具体执行方式。sync-procedures.md 定义"做什么"，本文件定义"在 GitHub 上怎么做"。

## 前置条件

- `gh` CLI 已安装且已认证（`gh auth status`）
- 不可用时降级（sync-procedures.md §8 降级行为生效）

## 操作表

sync-procedures.md 子命令使用"操作语义"描述步骤，Claude 在本表中查找对应 gh CLI 命令执行。

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

## 限流保护

每次 API 调用后等待 1 秒。检测到 403/429 → 暂停 60 秒重试 1 次。重试仍失败 → 标记跳过。
