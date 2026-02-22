# 发布文件格式契约

> **职责**：定义 REL-xxx.md 文件的结构。/pace-release 创建和管理 Release 时遵循此格式。

## §0 速查卡片

```
文件名：REL-xxx.md（xxx 为自增数字，三位补零）
存储：.devpace/releases/
状态值：staging → deployed → verified → closed
必含：元信息 + 包含 CR 表 + 部署记录 + 验证清单
Release 关闭时连锁更新：关联 CR 状态 → released，project.md 功能树 🚀
```

## 文件结构

```markdown
# Release [REL-xxx]

- **ID**：REL-xxx
- **版本**：[语义化版本号或自定义标识]
- **状态**：[staging | deployed | verified | closed]
- **创建日期**：[YYYY-MM-DD]
- **目标环境**：[环境名称，如 production]

## 包含变更

| CR | 标题 | 类型 | PF | 状态 |
|----|------|------|-----|------|
| [CR-xxx] | [标题] | [feature/defect/hotfix] | [PF-xxx] | [merged/released] |

## 部署记录

| 日期 | 环境 | 操作 | 结果 | 备注 |
|------|------|------|------|------|
| [日期] | [环境] | [部署/回滚] | [成功/失败] | [备注] |

## 验证清单

- [ ] 部署成功确认
- [ ] 核心功能验证通过
- [ ] 无新增错误日志
- [ ] 性能无明显回退
- [ ] [项目自定义验证项]

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

### 状态转换

```
staging → deployed → verified → closed
                        │
                        └→ 发现问题 → 记录到"部署后问题"，不回退状态
```

- **staging → deployed**：人类确认已完成部署操作
- **deployed → verified**：验证清单全部勾选
- **verified → closed**：Claude 自动执行关闭流程

### 关闭连锁更新

Release 从 verified 转为 closed 时，Claude 自动执行：

1. 关联 CR 状态批量更新：merged → released
2. 更新 project.md 功能树：已 released 的 CR 标记 🚀
3. 更新 iterations/current.md 产品功能表 Release 列
4. 更新 state.md 发布状态段（移除已关闭 Release）
5. 更新 dashboard.md：部署频率 +1、计算变更前置时间

## 命名规则

- 文件名：`REL-001.md`、`REL-002.md`...（三位补零自增）
- ID 自增：扫描 `.devpace/releases/` 中现有 Release 文件的最大编号 +1

## 写入规则

- /pace-release：创建、更新状态、管理验证清单
- /pace-feedback：在"部署后问题"表追加问题记录
- §14 Release 关闭：自动连锁更新
- 人类：确认部署和验证结果
