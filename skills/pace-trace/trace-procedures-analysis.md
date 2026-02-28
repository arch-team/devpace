# 分析类决策轨迹查询执行规程

> **职责**：pace-trace `intent`/`change`/`risk`/`autonomy` 子命令的类型特定规则。通用规则（输出格式框架、confidence 表、降级处理、执行步骤、规则）见 `trace-procedures-common.md`。

## §0 速查卡片

- **本文件覆盖**：各分析类型输出调整 · 分析类导航建议表
- **通用规则**（输出格式、confidence、降级、步骤、规则）→ `trace-procedures-common.md`

## 各分析类型的输出调整

- **intent**：无"逐项检查"，"评估过程"标题改为"推断过程"（复杂度判定 + 范围分析 + 执行计划生成逻辑）
- **change**：无"逐项检查"，"评估过程"标题改为"影响分析过程"（关联 CR/PF/迭代影响链）
- **risk**：无"逐项检查"，"评估过程"标题改为"风险评估过程"（5 维评估 + 综合等级判定）
- **autonomy**：无"逐项检查"，展示"自主级别影响"（当前级别 + 对 Gate/交互/简化审批的具体影响）

## 上下文导航（输出末尾）

| 决策类型 | 导航建议 |
|---------|---------|
| intent | → 设计理论：/pace-theory why intent · 变更历史：/pace-change history |
| change | → 测试影响：/pace-test impact · 风险扫描：/pace-guard scan |
| risk | → 风险总览：/pace-guard monitor · 相关经验：/pace-learn list |
| autonomy | → 角色视角：/pace-role · 理论基础：/pace-theory why autonomy |

导航建议用 `→` 前缀，跟在输出最后一行之后。
