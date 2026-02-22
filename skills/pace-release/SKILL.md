---
description: Use when user says "发布", "部署", "上线", "release", "pace-release", or wants to manage a release lifecycle.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash
argument-hint: "[create|deploy|verify|close|changelog|version|tag|rollback|full|notes|branch|status]"
---

# /pace-release — 发布管理

> **可选功能**：如果你没有正式的发布流程，不需要使用这个命令。任务 merged 就是你的完成点，不需要 Release 管理。

管理 Release 生命周期：收集候选变更 → 创建 Release → 追踪部署 → 验证 → 关闭。支持 Changelog、版本 bump、Git Tag、GitHub Release、Release Notes 和发布分支管理。

详细流程见 `release-procedures.md`。

## 输入

$ARGUMENTS：
- `create` → 创建新 Release（收集 merged CR + Gate 4 系统级检查）
- `deploy` → 记录部署操作
- `verify` → 执行验证清单（支持自动化验证命令）
- `close` → 关闭 Release（触发连锁更新 + changelog + tag）
- `changelog` → 从 Release CR 元数据生成 CHANGELOG.md
- `version` → 更新用户产品版本文件（读取 integrations/config.md 配置）
- `tag` → 创建 Git Tag + 可选 GitHub Release
- `rollback` → 记录回滚操作（deployed → rolled_back）
- `full` → 一键执行：changelog + version + tag + close
- `notes` → 生成面向最终用户的 Release Notes（按 BR/PF 组织）
- `branch` → 管理发布分支（创建 release/v{version} 或生成 Release PR）
- `status` → 查看当前 Release 状态
- （空）→ 智能判断（有 staging → 提示部署，有 deployed → 提示验证）

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

1. 用户确认已完成部署操作
2. 在 Release 部署记录表追加记录
3. Release 状态 staging → deployed

### verify：执行验证

1. 如果 integrations/config.md 配置了验证命令 → 自动执行并报告结果
2. 展示验证清单，逐项确认（自动验证的结果预填）
3. 全部通过 → Release 状态 deployed → verified
4. 发现问题 → 记录到"部署后问题"表，引导创建 defect CR

### close：关闭 Release

1. 确认 Release 处于 verified 状态
2. 执行关闭连锁更新（见 `release-procedures.md`）
3. Release 状态 verified → closed

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

### full：一键发布

按顺序执行：changelog → version → tag → close。每步执行前确认，任一步失败或用户取消可跳过继续或中断。

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
