# 共享断言模式

> 定义跨 Skill 可复用的 eval 断言模式。各 Skill 的 `evals.json` 可引用模式 ID，避免重复定义。
> 当共享行为变化（如 state.md 格式升级）时，只需更新此处一次。

## 模式定义

### SA-01: state_updated

**适用 Skill**：几乎所有（pace-dev, pace-change, pace-status, pace-review, pace-next, pace-plan 等）

**断言**：
- state.md `current-work` 字段反映最新操作结果
- state.md `next-step` 字段包含下一步建议
- state.md `last-updated` 时间戳已更新

**eval 引用示例**：
```json
{
  "assertion": "state.md is updated with current-work and next-step",
  "shared_pattern": "SA-01"
}
```

### SA-02: cr_lifecycle

**适用 Skill**：pace-dev, pace-review, pace-change

**断言**：
- CR 文件 `status` 字段遵循状态机定义（created→developing→verifying→in_review→approved→merged）
- CR 状态变更时 `events` 列表追加新事件
- 事件记录包含时间戳和触发原因

### SA-03: natural_language

**适用 Skill**：所有用户可见输出

**断言**：
- 输出不包含内部 ID 格式（如 `CR-001`、`PF-002`）
- 输出不包含状态机术语（如 `developing`、`in_review`）
- 使用自然语言描述进度（如"正在开发中"而非 `status: developing`）

### SA-04: p2_progressive

**适用 Skill**：pace-status, pace-next

**断言**：
- 默认输出 ≤ 3 行概览
- `detail` 参数展开到 PF 级别详情
- `tree` 参数展示完整功能树结构

### SA-05: git_committed

**适用 Skill**：pace-dev

**断言**：
- 每个有意义的工作单元完成后执行 git commit
- commit message 遵循 `<type>(<scope>): <description>` 格式
- 不跳过 pre-commit hooks

### SA-06: schema_compliant

**适用 Skill**：所有写入 `.devpace/` 文件的 Skill

**断言**：
- 产出文件的 Markdown 结构符合 `knowledge/_schema/` 对应格式定义
- 必填字段全部存在
- 字段值类型正确（如枚举值在允许范围内）

## 跨 Skill 交叉污染测试对

以下 Skill 对的触发关键词存在交叉风险，trigger eval 必须包含对方的典型查询作为负面测试用例：

| 测试对 | Skill A 关键词 | Skill B 关键词 | 混淆风险 |
|--------|---------------|---------------|---------|
| pace-dev ↔ pace-change | "开始做/帮我改/实现/修复" | "加一个需求/不做了/先暂停" | 高 |
| pace-status ↔ pace-trace | "看看进度/现在什么状态" | "为什么这么决定/决策追溯" | 中 |
| pace-test ↔ pace-review | "跑一下测试/验证" | "提交审核/review" | 中 |
| pace-guard ↔ pace-test | "风险检查/有什么风险" | "测试覆盖/质量验证" | 中 |
| pace-next ↔ pace-status | "下一步做什么" | "当前状态" | 中 |
| pace-plan ↔ pace-next | "规划迭代/安排任务" | "推荐下一步" | 低 |

**使用方式**：在创建 Skill A 的 `trigger-evals.json` 时，将 Skill B 的典型查询作为 `should_not_trigger` 用例。
