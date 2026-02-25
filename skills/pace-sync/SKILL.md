---
description: "Use when user wants to sync devpace state with external tools (GitHub/Linear/Jira), says '同步/sync/push/pull/关联 Issue', or /pace-sync. NOT for internal devpace state changes (use /pace-dev) or release operations (use /pace-release)"
argument-hint: "[子命令] [参数]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
model: sonnet
---

# /pace-sync — 外部工具同步

将 devpace 研发状态与外部项目管理工具（GitHub/Linear/Jira/GitLab）双向桥接。

## 与现有机制的关系

- /pace-dev 管理 CR 内部状态转换 → /pace-sync 将状态变化推送到外部
- /pace-release 管理发布流程 → /pace-sync 同步发布状态到外部
- /pace-status 展示内部状态 → /pace-sync status 展示同步状态和外部链接

## 推荐使用流程

首次配置：`setup` → 关联：`link` → 日常：`push` / `status`

## 输入

`$ARGUMENTS` 解析为子命令 + 参数。

### 子命令

| 子命令 | 参数 | 说明 | MVP |
|--------|------|------|:---:|
| setup | — | 引导式同步配置（检测 git remote → 生成 sync-mapping.md） | ✅ |
| link | CR-ID #外部ID | 关联 CR 与外部实体 | ✅ |
| push | [CR-ID] | 推送 devpace 状态到外部（指定 CR 或全部已关联） | ✅ |
| pull | [CR-ID] | 拉取外部状态到 devpace | Phase 19 |
| sync | [CR-ID] | 双向同步 | Phase 20 |
| resolve | CR-ID | 解决同步冲突 | Phase 20 |
| status | — | 查看所有 CR 的同步状态和外部链接 | ✅ |

无参数时默认 `status`。

## 流程

1. 读取 `.devpace/integrations/sync-mapping.md`
   - 不存在 → 引导运行 `setup`
2. 根据子命令路由到对应操作（详见 `sync-procedures.md`）
3. 执行后更新 sync-mapping.md 关联记录

### 执行路由

| 参数 | 执行规程 |
|------|---------|
| `setup` | sync-procedures.md §2 |
| `link` | sync-procedures.md §3 |
| `push` | sync-procedures.md §4 |
| `status` | sync-procedures.md §5 |
| （空） | 等同 `status` |

## 输出

- **setup**：配置摘要（平台 + 仓库 + 同步模式）
- **link**：关联确认（CR ↔ 外部实体）
- **push**：同步结果表（CR | 状态 | 外部操作 | 结果）
- **status**：同步状态表（CR | 外部链接 | 最后同步 | 状态一致性）
