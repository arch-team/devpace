# 发布管理执行规程——Rollback

> **职责**：部署后回滚流程。
>
> **自包含**：本文件独立执行，不需要加载其他 procedures 文件。

## §0 速查卡片

- **前置检查**：Release 必须处于 `deployed` 状态
- **流程**：询问原因 → 记录回滚 → 状态 deployed→rolled_back → 引导创建修复 CR
- **后续**：引导创建修复 CR，回滚后候选预填见 create.md

## 前置检查

1. Release 必须处于 `deployed` 状态
2. 如不处于 deployed → 提示当前状态，不允许操作

## 回滚记录

1. 询问回滚原因
2. 在 Release 部署记录表追加回滚记录：

```markdown
| 日期 | 环境 | 操作 | 结果 | 备注 |
|------|------|------|------|------|
| 2026-02-22 | production | 回滚 | 成功 | [回滚原因] |
```

3. Release 状态 deployed → rolled_back
4. 更新 state.md 发布状态段

## 后续处理

1. 引导用户创建 defect/hotfix CR 关联本次回滚原因
2. 新 CR 的"关联 Release"指向当前 Release
3. 提示：修复后需创建新 Release（rolled_back 是终态）
4. 回滚后创建新 Release 时，create 流程自动预填候选 CR（详见 `release-procedures-create.md`「回滚后候选预填」）
