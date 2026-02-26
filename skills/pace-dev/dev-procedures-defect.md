# Defect/Hotfix CR 规程

> **职责**：CR 类型为 defect 或 hotfix 时的额外创建规则和修复后处理。与 `dev-procedures-intent.md` 追加加载。

## Defect CR 创建规则

当 CR 类型为 defect 时，意图检查点有额外步骤：

1. 自动添加"根因分析"section（格式参考 `knowledge/_schema/cr-format.md`）
2. 现象字段：从用户描述自动填充
3. 根因字段：初始为"待调查"，developing 阶段定位后填充
4. 引入点字段：尝试追溯到引入问题的 CR（通过 git blame 或 Release 追溯）
5. 分支名前缀：`fix/` 而非 `feature/`

## Hotfix CR 创建规则

当 CR 类型为 hotfix 时：

1. 同 defect 规则，额外检查 severity
2. severity:critical → 告知用户可走加速路径（跳过 in_review）
3. 用户确认加速路径后：
   - 在 CR 事件表记录"加速路径：跳过 in_review，原因 [描述]"
   - developing → verifying → merged（跳过 in_review + approved）
   - merged 后提醒补充事后审批
4. 分支名前缀：`hotfix/` 而非 `feature/`

## Defect/Hotfix 修复后处理

1. merged 后自动触发 pace-learn 提取根因 pattern
2. 更新 CR 根因分析 section：填充根因、预防措施
3. 如该 defect 关联了 Release → 更新 Release 文件的缺陷记录
4. 更新 dashboard.md 缺陷修复周期指标
