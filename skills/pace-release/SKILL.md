---
description: Use when user says "发布", "部署", "上线", "release", "pace-release", or wants to manage a release lifecycle.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob
argument-hint: "[create|deploy|verify|close|status]"
---

# /pace-release — 发布管理

> **可选功能**：如果你没有正式的发布流程，不需要使用这个命令。任务 merged 就是你的完成点，不需要 Release 管理。

管理 Release 生命周期：收集候选变更 → 创建 Release → 追踪部署 → 验证 → 关闭。

详细流程见 `release-procedures.md`。

## 输入

$ARGUMENTS：
- `create` → 创建新 Release（收集 merged CR）
- `deploy` → 记录部署操作
- `verify` → 执行验证清单
- `close` → 关闭 Release（触发连锁更新）
- `status` → 查看当前 Release 状态
- （空）→ 智能判断（有 staging → 提示部署，有 deployed → 提示验证）

## 流程概览

### create：创建 Release

1. 扫描 `.devpace/backlog/` 中所有 merged 且未关联 Release 的 CR
2. 展示候选 CR 列表，用户确认纳入范围
3. 创建 REL-xxx.md（格式参考 `knowledge/_schema/release-format.md`）
4. 更新关联 CR 的"关联 Release"字段

### deploy：记录部署

1. 用户确认已完成部署操作
2. 在 Release 部署记录表追加记录
3. Release 状态 staging → deployed

### verify：执行验证

1. 展示验证清单，逐项确认
2. 全部通过 → Release 状态 deployed → verified
3. 发现问题 → 记录到"部署后问题"表，引导创建 defect CR

### close：关闭 Release

1. 确认 Release 处于 verified 状态
2. 执行关闭连锁更新（见 `release-procedures.md`）
3. Release 状态 verified → closed

## 输出

Release 操作结果摘要（3-5 行）。
