---
description: Use when user says "发布", "部署", "上线", "release", "pace-release", or wants to manage a release lifecycle.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash
argument-hint: "[create 创建发布|deploy 记录部署|verify 验证部署|close 完成发布|full 一键完成|status 查看状态]"
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

## 流程概览

### create：创建 Release

1. 扫描 `.devpace/backlog/` 中所有 merged 且未关联 Release 的 CR
2. 展示候选 CR 列表，用户确认纳入范围
3. 根据 CR 类型建议版本号（feature→minor, defect/hotfix→patch）
4. **Gate 4 系统级检查**（如有 integrations/config.md）：
   - 运行构建/测试命令验证代码可构建
   - 检查 CI pipeline 状态（如 `gh run list`）
   - 检查未通过 → 提示用户修复后重试
5. 创建 REL-xxx.md（格式参考 `knowledge/_schema/release-format.md`）
6. 更新关联 CR 的"关联 Release"字段
7. 可选：如果用户配置了发布分支模式，创建 `release/v{version}` 分支

### deploy：记录部署

1. 检查 integrations/config.md 环境配置：
   - 单环境或无配置 → 直接部署确认
   - 多环境 → 展示晋升路径，按顺序逐环境部署
2. 用户确认已完成当前环境部署操作
3. 在 Release 部署记录表追加记录（含环境名称）
4. 单环境 → Release 状态 staging → deployed
5. 多环境 → 更新"当前环境"字段，最终环境部署后 staging → deployed

### verify：执行验证

0. 多环境模式：当前环境验证通过后 → 提示晋升到下一环境（deploy → verify 循环直到最终环境）
1. 如果 integrations/config.md 配置了验证命令 → 自动执行并报告结果
2. 展示验证清单，逐项确认（自动验证的结果预填）
3. 全部通过 → Release 状态 deployed → verified
4. 发现问题 → 记录到"部署后问题"表，引导创建 defect CR

### close：完成发布（自动包含工具操作）

1. 确认 Release 处于 verified 状态
2. **自动执行**：changelog 生成 → 版本 bump → Git Tag 创建（每步前简短提示，用户可跳过任一步）
3. 执行关闭连锁更新：CR 状态批量更新 + 功能树更新 + 度量更新
4. Release 状态 verified → closed

> close 默认自动触发 changelog + version + tag，用户不再需要单独调用这些子命令。full 是 close 的推荐别名。

### changelog：生成 Changelog

1. 读取 Release 包含的 CR 列表
2. 按类型分组：Features / Bug Fixes / Hotfixes
3. 包含 PF 关联信息（如"改进了 [PF-001 用户认证]"）
4. 写入 Release 文件的 Changelog section + 用户产品根目录的 CHANGELOG.md
5. 可选：按 BR 分组生成高层 Release Notes

### version：版本号 Bump

1. 读取 integrations/config.md 的版本管理配置
2. 根据 CR 类型推断 semver 变更（feature→minor, defect/hotfix→patch）
3. 用户确认版本号
4. 更新配置中指定的版本文件
5. 无版本管理配置 → 提示用户手动更新

### tag：创建 Git Tag

1. 读取 Release 版本号
2. 创建 `git tag v{version}`（前缀来自 integrations/config.md 配置）
3. 可选：`gh release create v{version}` 创建 GitHub Release（附 changelog 内容）
4. 用户确认后执行

### rollback：记录回滚

1. 确认 Release 处于 deployed 状态
2. 记录回滚原因
3. Release 状态 deployed → rolled_back
4. 在部署记录表追加回滚记录
5. 引导用户创建 defect/hotfix CR 关联本次回滚原因

### full：一键发布（close 的推荐别名）

行为与 close 完全相同：自动执行 changelog → version → tag → 关闭连锁更新。每步前简短提示，任一步可跳过。推荐使用 `full` 因为语义更明确。

### notes：生成 Release Notes

1. 读取 Release 包含的 CR 列表及其 PF、BR 关联
2. 按 BR 分组，每个 BR 下列出关联的 PF 及其 CR 变更
3. 用产品语言描述（不含 CR 编号等技术细节）
4. 写入 Release 文件的 Release Notes section
5. 可选：输出到独立文件（如 RELEASE_NOTES.md）

### branch：发布分支管理

1. `branch create` → 从 main 创建 `release/v{version}` 分支
   - 自动切换到 release 分支
   - 在 release 分支上做最终修复和验证
2. `branch pr` → 创建 Release PR（含 changelog + version bump 变更）
   - PR 标题：`Release v{version}`
   - PR 内容：changelog 预览 + 包含的 CR 列表
   - 用户 merge PR = 确认发布
3. `branch merge` → 将 release 分支合并回 main
   - close 时自动提示（如存在 release 分支）

## 输出

Release 操作结果摘要（3-5 行）。
