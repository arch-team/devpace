# 发布文件格式契约

> **职责**：定义 REL-xxx.md 文件的结构。/pace-release 创建和管理 Release 时遵循此格式。

## §0 速查卡片

```
文件名：REL-xxx.md（xxx 为自增数字，三位补零）
存储：.devpace/releases/
状态值：staging → deployed → verified → closed（deployed → rolled_back 回滚路径）
必含：元信息（含摘要）+ 版本信息 + 包含 CR 表 + Changelog（含 Breaking Changes）+ Release Notes（可选）+ 部署记录 + 验证清单 + 迁移步骤（可选）
Release 关闭时连锁更新：生成 CHANGELOG.md → bump 版本文件 → git tag → 关联 CR → released → 功能树 🚀
```

## 文件结构

```markdown
# Release [REL-xxx]

- **ID**：REL-xxx
- **版本**：[语义化版本号或自定义标识]
- **状态**：[staging | deployed | verified | closed]
- **创建日期**：[YYYY-MM-DD]
- **目标环境**：[环境名称，如 production]
- **摘要**：[一句话描述本次发布核心变更，如"用户认证上线 + 搜索排序修复"]
- **发布分支**：[分支名称，如 release/v1.3.0，可选]
- **当前环境**：[已部署到的最新环境，如 canary]

## 版本信息

- **版本号**：[语义化版本号，如 1.3.0]
- **版本文件**：[已更新的版本文件路径列表，如 package.json]
- **Git Tag**：[tag 名称，如 v1.3.0，close 时创建]
- **GitHub Release**：[URL，close 时创建]

## 包含变更

| CR | 标题 | 类型 | PF | 状态 |
|----|------|------|-----|------|
| [CR-xxx] | [标题] | [feature/defect/hotfix] | [PF-xxx] | [merged/released] |

## Changelog

_Release 关闭时自动生成，按 CR 类型分组。Breaking Changes 置顶，无则省略。_

### Breaking Changes

- [CR-xxx] [标题]（[PF-xxx]）— [不兼容变更说明]

### Features

- [CR-xxx] [标题]（[PF-xxx]）

### Bug Fixes

- [CR-xxx] [标题]（[PF-xxx]）

### Hotfixes

- [CR-xxx] [标题]（[PF-xxx]）

## Release Notes

_用户请求或 close 时生成，按 BR/PF 组织，面向产品用户。_

### [BR 标题]
- **[PF 标题]**：[用产品语言描述的变更]

## 部署记录

多环境部署时，每个环境一行记录。最新部署的环境 = Release 的"当前环境"。

| 日期 | 环境 | 操作 | 结果 | 备注 |
|------|------|------|------|------|
| [日期] | [环境] | [部署/回滚] | [成功/失败] | [备注] |

## 验证清单

- [ ] 部署成功确认
- [ ] 核心功能验证通过
- [ ] 无新增错误日志
- [ ] 性能无明显回退
- [ ] [项目自定义验证项]

## 迁移步骤

_可选。有数据库迁移、配置变更、环境变量新增等前置操作时填充。无则省略此 section。_

| 序号 | 步骤 | 命令/操作 | 回滚方式 | 状态 |
|:----:|------|---------|---------|:----:|
| 1 | [步骤描述] | [命令或操作说明] | [回滚命令或操作] | [ ] |

## 部署后问题

| 日期 | 问题描述 | 严重度 | 关联 CR | 状态 |
|------|---------|--------|---------|------|

_无问题时此表为空。_
```

## 状态值

| 状态 | 含义 | 执行者 |
|------|------|--------|
| staging | 准备发布，收集候选 CR | Claude + 人类 |
| deployed | 已部署到目标环境 | 人类确认 |
| verified | 部署验证通过 | 人类确认 |
| closed | 发布完成，记录归档 | Claude 自动 |
| rolled_back | 部署已回滚 | 人类确认 |

### 状态转换

```
staging → deployed → verified → closed
              │          │
              │          └→ 发现问题 → 记录到"部署后问题"，不回退状态
              └→ rolled_back（部署失败/严重问题需回滚）
```

- **staging → deployed**：人类确认已完成部署操作
- **deployed → verified**：验证清单全部勾选
- **deployed → rolled_back**：部署后发现严重问题需要回滚，人类确认
- **verified → closed**：Claude 自动执行关闭流程

### 关闭连锁更新

Release 从 verified 转为 closed 时，Claude 自动执行：

1. Changelog 生成：按 CR 类型分组生成 changelog 内容，写入 Release 文件和用户产品的 CHANGELOG.md
2. 版本文件更新：根据 integrations/config.md 的版本管理配置，更新用户产品版本文件
3. Git Tag 创建：`git tag v{version}` + 可选 `gh release create`
4. 关联 CR 状态批量更新：merged → released
5. 更新 project.md 功能树：已 released 的 CR 标记 🚀
6. 更新 iterations/current.md 产品功能表 Release 列
7. 更新 state.md 发布状态段（移除已关闭 Release）
8. 更新 dashboard.md：部署频率 +1、计算变更前置时间、如有 defect CR 关联此 Release → 更新变更失败率

## 命名规则

- 文件名：`REL-001.md`、`REL-002.md`...（三位补零自增）
- ID 自增：扫描 `.devpace/releases/` 中现有 Release 文件的最大编号 +1

## 写入规则

- /pace-release：创建、更新状态、管理验证清单
- /pace-release changelog：生成和更新 Changelog
- /pace-release version：更新版本文件
- /pace-release tag：创建 Git Tag
- /pace-feedback：在"部署后问题"表追加问题记录
- §14 Release 关闭：自动连锁更新
- 人类：确认部署和验证结果

## 运行时扩展 section

以下 section 不属于初始创建模板，由子命令在特定流程中动态追加到 Release 文件：

| Section | 追加时机 | 来源 |
|---------|---------|------|
| `## Readiness Check` | create 增强（CR > 3） | release-procedures-create-enhanced.md |
| `## 影响预览` | create 增强（自动） | release-procedures-create-enhanced.md |
| `## Gate 4 检查结果` | create 增强（Gate 4 执行后） | release-procedures-create-enhanced.md |
