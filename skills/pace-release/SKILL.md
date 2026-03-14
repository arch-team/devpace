---
description: Use when user says "发布", "部署", "上线", "release", "pace-release", or wants to create, deploy, or close a release. NOT for CI/CD pipeline management (use /pace-sync). NOT for code implementation (use /pace-dev).
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Bash
argument-hint: "[create|deploy|verify|close|full|status|status history|changelog|version|tag|notes --role biz|ops|pm|branch|rollback]"
model: sonnet
disable-model-invocation: true
context: fork
agent: pace-engineer
---

# /pace-release — 发布管理

> **可选功能**：如果你没有正式的发布流程，不需要使用这个命令。任务 merged 就是你的完成点，不需要 Release 管理。

管理 Release 生命周期：收集候选变更 → 创建 Release → 追踪部署 → 验证 → 关闭。支持 Changelog、版本 bump、Git Tag、GitHub Release、Release Notes 和发布分支管理。

## 输入

$ARGUMENTS：

**日常使用**（大多数场景只需这些）：
- `create` → 创建新 Release（收集 merged CR + Gate 4 检查）
- `deploy` → 记录部署操作（支持多环境晋升）
- `verify` → 执行验证清单（支持自动化验证）
- `close` → 完成发布（自动 changelog + 版本 bump + tag + 连锁更新）
- `full` → close 的推荐别名（语义更明确）
- `status` → 查看当前 Release 状态和建议下一步
- （空）→ 引导式发布向导（推荐新用户使用）

**单独使用**（当你只需要其中某个步骤时）：
- `changelog` → 仅生成 CHANGELOG.md
- `version` → 仅更新版本文件
- `tag` → 仅创建 Git Tag / GitHub Release
- `notes` → 生成面向用户的 Release Notes（按 Epic→BR→PF 组织，支持 `--role biz|ops|pm`）
- `branch` → 管理发布分支（创建 / PR / 合并）
- `rollback` → 记录回滚（deployed 状态下出现严重问题时）
- `status history` → 发布历史时间线（跨 Release 纵向视图 + DORA 趋势）

## 执行路由

根据子命令，**只读取路由表中对应的 procedures 文件，不加载其他 procedures 文件。**

### 核心操作固定加载

core 子命令（create/deploy/verify/close/full）加载 `release-procedures-common.md`（发布规则 + 集成规则 + 版本推断 SSOT）。

### 按子命令加载

| 参数 | 加载文件 | 说明 |
|------|---------|------|
| （空） | wizard.md | 自包含；引导式向导（含 rolled_back 追踪） |
| `create` | common.md + create.md；CR>3 或有 config.md 时追加 create-enhanced.md | 分层加载 |
| `deploy` | common.md + deploy.md | 环境晋升 + 路径全景 |
| `verify` | common.md + verify.md | 自动健康检查 + 问题处理 |
| `close` / `full` | common.md + close.md；步骤 1-3 按执行进度加载 changelog.md / version.md / tag.md | 步进式增量加载 |
| `changelog` | changelog.md | 自包含 |
| `version` | version.md | 自包含（含精简版本推断规则） |
| `tag` | tag.md | 自包含 |
| `rollback` | rollback.md | 自包含（含候选预填） |
| `notes` | notes.md | 自包含（支持 `--role biz\|ops\|pm`） |
| `branch` | branch.md | 自包含 |
| `status` / `status history` | status.md | 自包含 |

> **scheduling.md** 不对应用户子命令，由 wizard（发布窗口提醒）或 pace-pulse 按需加载。

**文件名前缀**：所有文件名均以 `release-procedures-` 开头，上表省略前缀。如 `wizard.md` 实际为 `release-procedures-wizard.md`。

## 输出

Release 操作结果摘要（3-5 行）。
