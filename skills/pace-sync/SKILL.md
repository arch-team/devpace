---
description: Use when user says "同步/sync/同步到GitHub/关联Issue/unlink/Gate同步/sub-issue/全量同步/增量同步" or /pace-sync. Syncs Epic/BR/PF/CR to GitHub Issues. NOT for internal state (use /pace-dev).
argument-hint: "[子命令] [参数]"
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Grep, Bash
model: sonnet
---

# /pace-sync — 外部工具同步

将 devpace 全部实体（Epic/BR/PF/CR）与外部项目管理工具同步。支持 GitHub（当前），设计为 Linear/Jira 可扩展。

## 与现有机制的关系

- /pace-dev 管理 CR 内部状态转换 → /pace-sync 将状态变化推送到外部
- /pace-change 管理变更操作 → /pace-sync 同步变更后状态到外部
- /pace-release 管理发布流程 → /pace-sync 同步发布状态到外部
- /pace-review Gate 2 结果 → /pace-sync Gate 结果自动推送（Comment + 标签）
- /pace-status 展示内部状态 → /pace-sync status 展示同步状态和外部链接

## 推荐使用流程

首次配置：`setup` → 日常同步：`/pace-sync`（智能同步）→ 查看状态：`status`

## 输入

`$ARGUMENTS` 解析为子命令 + 参数。

### 子命令

| 子命令 | 参数 | 说明 |
|--------|------|------|
| sync | [--dry-run] | **智能同步**（默认行为）：自动检测变更，呈现摘要，确认后执行。无参数时等价。 |
| link | 实体ID [#外部ID] | 关联实体与已有外部 Issue（支持 EPIC-xxx/BR-xxx/PF-xxx/CR-xxx；省略外部 ID 则智能匹配） |
| unlink | 实体ID | 解除实体与外部的关联 |
| status | [--all] | 查看同步状态（--all 显示全部实体类型，默认仅 CR） |
| setup | [--auto] | 引导式同步配置（--auto 跳过交互确认） |
| pull | 实体ID | 查询外部状态，提示用户是否更新 devpace（轻量检查） |

**无参数时默认执行智能同步（sync）。**

**实体 ID 格式**：`EPIC-001`、`BR-002`、`PF-003`、`CR-004`（前缀确定类型）。纯数字默认为 CR（向后兼容）。

## 流程

1. 读取 `.devpace/integrations/sync-mapping.md`（不存在 → 引导 `setup`）
2. 加载 `sync-procedures-common.md`（始终加载）
3. **根据子命令，仅加载对应的 procedures 文件**：

| 参数 | 加载文件 |
|------|---------|
| `sync` / （空） | sync-procedures-entity.md（智能同步主流程） |
| `sync --dry-run` | sync-procedures-entity.md（dry-run 模式） |
| `link` | sync-procedures-link.md + sync-procedures-entity.md（§1 ID 解析） |
| `unlink` | sync-procedures-status.md + sync-procedures-entity.md（§1 ID 解析） |
| `status` [--all] | sync-procedures-status.md [+ sync-procedures-entity.md] |
| `setup` | sync-procedures-setup.md |
| `pull` | sync-procedures-pull.md + sync-procedures-entity.md（§1 ID 解析） |

Gate 结果同步（被动触发）：sync-procedures-push-advanced.md

Auto-link/create（Hook 触发）：sync-procedures-auto.md

## 输出

智能同步输出格式：

```
同步检测：
- 3 个实体有变更（CR-003 状态→developing, EPIC-001 完成度↑, PF-002 新增验收）
- 2 个新实体未关联（BR-003, CR-008）
- 7 个已关联且无变化

[用户确认后]

| 实体 | 类型 | 外部链接 | 操作 | 结果 |
|------|------|---------|------|------|
| EPIC-001 | Epic | [#10](URL) | 更新标签 | ✅ |
| BR-003 | BR | [#15](URL) | 新建 Issue | ✅ |
| CR-003 | CR | [#42](URL) | 更新标签 + Comment | ✅ |

汇总：3 已同步 / 2 新建 / 7 无变化
层级：2 个 sub-issue 关系已建立
```
