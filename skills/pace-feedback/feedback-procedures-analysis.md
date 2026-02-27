# 根因分析与度量规程

> **职责**：根因分析智能辅助、MoS 更新、度量更新。创建 defect/hotfix CR 时加载。

## 根因分析智能辅助

### 创建时填充

创建 defect/hotfix CR 时自动填充根因分析 section：

```markdown
## 根因分析

- **现象**：[用户报告的问题描述]
- **根因**：待调查
- **引入点**：[追溯结果，如 CR-xxx] 或 待确认
- **预防措施**：待修复后填写
```

### 历史根因推荐

创建 defect CR 时，扫描 `insights.md` 的防御 pattern，匹配同一 PF 或相似症状的历史根因：

- 匹配到 → 在 CR 创建输出中附加：`💡 相似历史：[CR-ID]（[PF 名] 的 [问题类型]），根因是 [历史根因]，建议优先检查类似路径`
- 未匹配 → 静默跳过

### 修复后填充

defect CR merged 后，pace-learn 自动提取根因分析：
- 更新"根因"为实际原因
- 更新"引入点"为确认的 CR
- 填充"预防措施"
- 提取为 insights.md 的防御 pattern（如该类问题可泛化）
- 标记 `test-gap: true`（当缺陷逃逸表明测试盲区时），供 pace-test strategy 扫描

## MoS 更新规则

如反馈涉及已定义的成效指标（MoS）：
- 缺陷/生产事件 → 在 project.md 对应 MoS 处追加备注"[日期] 反馈：[问题]"
- 改进 → 建议调整 MoS 指标或新增指标

## 度量更新

### 缺陷逃逸率增量更新

每创建一个 defect/hotfix CR，自动在 dashboard.md 更新：
- 缺陷逃逸计数 +1
- 重新计算缺陷逃逸率

### 缺陷修复周期

defect CR merged 后，计算从创建到 merged 的天数，更新到 dashboard.md。

### 反馈转化率（pace-retro 可用）

pace-retro 回顾时可从 feedback-log.md 计算：
- 反馈总数 / 已采纳或已修复数 = 转化率
- 按分类统计分布（生产事件/缺陷/改进/新需求/待定）
