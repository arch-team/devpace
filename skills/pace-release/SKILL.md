---
description: Use when user says "发布", "部署", "上线", "release", "pace-release", or wants to create, deploy, or close a release.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash
argument-hint: "[create 创建发布|deploy 部署/记录|verify 验证部署|close 完成发布|full 一键完成|status 查看状态]"
---

# /pace-release — 发布管理

> **可选功能**：如果你没有正式的发布流程，不需要使用这个命令。任务 merged 就是你的完成点，不需要 Release 管理。

管理 Release 生命周期：收集候选变更 → 创建 Release → 追踪部署 → 验证 → 关闭。支持 Changelog、版本 bump、Git Tag、GitHub Release、Release Notes 和发布分支管理。

详细流程见 `release-procedures.md`。

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
- `notes` → 生成面向用户的 Release Notes（按 BR/PF 组织）
- `branch` → 管理发布分支（创建 / PR / 合并）
- `rollback` → 记录回滚（deployed 状态下出现严重问题时）

## 空参数引导式向导

当用户不带参数调用 `/pace-release` 时，Claude 读取当前 Release 状态，自动引导到合适的下一步：

- **无活跃 Release**："有 N 个已完成的任务可以发布。要创建新发布吗？" → 用户确认 → 自动执行 create 流程
- **有 staging Release**："Release v{version} 已准备好，包含 N 个变更。下一步：部署到 [环境]？" → 用户确认 → 自动执行 deploy 流程
- **有 deployed Release**："Release v{version} 已部署。要开始验证吗？" → 用户确认 → 自动执行 verify 流程；或"出了问题" → 自动引导 rollback 流程
- **有 verified Release**："Release v{version} 验证通过。完成发布？（将自动生成 Changelog、更新版本号、创建 Git Tag）" → 用户确认 → 自动执行 close 流程
- **无 merged CR 且无活跃 Release**："当前没有待发布的变更。"

引导流程让用户无需知道任何子命令名称，始终做正确的下一步。详细流程见 `release-procedures.md`。

## 执行路由

| 参数 | 执行规程 |
|------|---------|
| `create` | release-procedures.md「Create 详细流程」 |
| `deploy` | release-procedures.md「Deploy 详细流程」 |
| `verify` | release-procedures.md「Verify 详细流程」 |
| `close` / `full` | release-procedures.md「Close 详细流程」 |
| `changelog` | release-procedures.md「Changelog 生成流程」 |
| `version` | release-procedures.md「Version Bump 流程」 |
| `tag` | release-procedures.md「Git Tag 流程」 |
| `rollback` | release-procedures.md「Rollback 流程」 |
| `notes` | release-procedures.md「Release Notes 生成流程」 |
| `branch` | release-procedures.md「发布分支管理流程」 |
| `status` | release-procedures.md「Status 详细流程」 |
| （空） | release-procedures.md「引导式向导流程」 |

## 输出

Release 操作结果摘要（3-5 行）。
