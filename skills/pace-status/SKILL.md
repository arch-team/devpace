---
description: Use when user asks "进度怎样", "做到哪了", "项目状态", "当前状态", "进展", "看看进度", "总览", "dashboard", "pace-status", or wants to see project development progress and current state overview. NOT for next-step recommendations (use /pace-next).
allowed-tools: Read, Glob, Grep
argument-hint: "[detail|tree|trace <名称>|metrics [quality|delivery|risk]|since <时间>|<关键词>]"
model: haiku
context: fork
agent: pace-analyst
---

# /pace-status — 查看项目状态

按不同粒度展示项目研发状态。L1 概览回答"整体怎样"，L2 detail（广度）和 trace（深度）是正交视角，L3 tree 展示全貌。

## 输入

$ARGUMENTS：

**核心层**：（空）概览 | `detail` 功能展开 | `tree` 价值链全貌 | `trace <名称>` 反向追溯 | `metrics [quality|delivery|risk]` 度量 | `<关键词>` 搜索

**视角层**（由 /pace-role 管理，显式子命令 > 自动适配）：`biz` | `pm` | `dev` | `tester` | `ops` | `chain`

**修饰符**：`since <时间>` 时间段变更摘要（`3d`/`1w`/`last-session`），可与其他子命令组合

## 执行路由

**重要**：根据 $ARGUMENTS 匹配的子命令，仅读取对应的 procedures 文件，**不加载其他 procedures**。

| 子命令 | 加载文件 | 说明 |
|--------|---------|------|
| （空） | `status-procedures-overview.md` | 进度条 + 建议下一步 + 同步摘要 + 附加行上限 |
| `detail` | `status-procedures-detail.md` | 功能树格式 + 同步标记 + 角色适配 + 导航 |
| `trace <名称>` | `status-procedures-trace.md` | 匹配规则 + 3 种追溯格式 + 导航 |
| `metrics [类别]` | `status-procedures-metrics.md` | 实时快照（≠ pace-retro 回顾报告）+ 趋势箭头 + 类别聚焦 + 导航 |
| `tree` | `status-procedures-tree.md` | 完整价值链格式（含 Epic 链接层）+ 导航 |
| `since <时间>` | `status-procedures-since.md` | 时间标记解析 + 数据采集 + 组合规则 |
| `chain` | `status-procedures-chain.md` | 价值链定位格式 + 导航 |
| `<关键词>` | `status-procedures-keyword.md` | 搜索逻辑 + fallback 引导 |
| `biz/pm/dev/tester/ops` | `status-procedures-roles.md` | 5 种角色视图格式 + 优先级规则 + 导航 |

### 角色适配（所有子命令的前置步骤）

1. 有显式角色子命令（biz/pm/dev/tester/ops）→ 按对应视角输出
2. 无显式角色 → 读取 pace-role 设置 → 有则自动调整关注点
3. 无角色设置 → 默认全视角
4. 首次适配教学（§15 `role_adapt` 标记去重）：末尾追加 `（提示：当前按 [角色] 视角输出，切换：/pace-role [biz|pm|dev|tester|ops]）`

## 输出

按请求粒度展示的项目状态。自然语言为主，不主动暴露 ID。非概览子命令末尾追加 1 行导航提示。
