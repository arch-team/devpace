---
description: "Use when user wants to sync devpace state with external tools (GitHub/Linear/Jira), says '同步/sync/push/pull/关联 Issue/配置同步/setup/解除关联/unlink/创建 Issue/create/同步状态/status/CI/构建/build/pipeline/workflow/GitHub Actions', or /pace-sync. NOT for internal devpace state changes (use /pace-dev) or release operations (use /pace-release)"
argument-hint: "[子命令] [参数]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
model: sonnet
---

# /pace-sync — 外部工具同步

将 devpace 研发状态与外部项目管理工具（GitHub/Linear/Jira/GitLab）双向桥接。

## 与现有机制的关系

- /pace-dev 管理 CR 内部状态转换 → /pace-sync 将状态变化推送到外部
- /pace-change 管理变更操作 → /pace-sync 同步变更后状态到外部
- /pace-release 管理发布流程 → /pace-sync 同步发布状态到外部（Phase 19）
- /pace-review Gate 2 结果 → /pace-sync 同步为外部 PR Review（Phase 19）
- /pace-status 展示内部状态 → /pace-sync status 展示同步状态和外部链接

## 推荐使用流程

首次配置：`setup` → 关联：`link` → 日常：`push` / `status`

## 输入

`$ARGUMENTS` 解析为子命令 + 参数。

### 子命令

| 子命令 | 参数 | 说明 | MVP |
|--------|------|------|:---:|
| setup | [--auto] | 引导式同步配置（--auto 跳过交互确认） | ✅ |
| link | CR-ID [#外部ID] | 关联 CR 与外部实体（省略外部 ID 则智能匹配） | ✅ |
| push | [CR-ID] [--dry-run] | 推送 devpace 状态到外部（指定 CR 或全部已关联） | ✅ |
| unlink | CR-ID | 解除 CR 与外部实体的关联 | ✅ |
| create | CR-ID | 从 CR 元数据创建外部 Issue 并自动关联 | ✅ |
| pull | CR-ID | 查询外部状态，提示用户是否更新 devpace（轻量 MVP） | ✅ |
| ci status | — | 查看当前分支的 CI/CD 运行状态 | ✅ |
| ci trigger | [workflow] | 手动触发 GitHub Actions workflow | ✅ |
| ci logs | [run-id] | 查看指定运行的日志摘要 | ✅ |
| sync | [CR-ID] | 双向同步 | Phase 20 |
| resolve | CR-ID | 解决同步冲突 | Phase 20 |
| status | — | 查看所有 CR 的同步状态和外部链接 | ✅ |

无参数时默认 `status`。

## 流程

1. 读取 `.devpace/integrations/sync-mapping.md`（不存在 → 引导 `setup`）
2. 加载 `sync-procedures-common.md`（始终加载）
3. **根据子命令，仅加载对应的 procedures 文件**：

| 参数 | 加载文件 |
|------|---------|
| `setup` | sync-procedures-setup.md |
| `link` | sync-procedures-link.md |
| `create` | sync-procedures-link.md（§6） |
| `push` | sync-procedures-push.md |
| `push --dry-run` | sync-procedures-push.md + sync-procedures-push-advanced.md |
| `pull` | sync-procedures-pull.md |
| `status` / `unlink` / （空） | sync-procedures-status.md |
| `ci status` / `ci trigger` / `ci logs` | sync-procedures-ci.md |
| `sync` / `resolve` | Phase 20，暂不支持 |

Gate 结果同步（被动触发）：sync-procedures-push.md + sync-procedures-push-advanced.md
