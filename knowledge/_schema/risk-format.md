# risk.md 格式契约

> **职责**：定义 RISK-NNN.md 文件的结构。/pace-scan 创建风险文件时遵循此格式，/pace-checkpoint 和 /pace-retro 更新时亦遵循。

## §0 速查卡片

```
文件名：RISK-NNN.md（NNN 三位补零，按 .devpace/risks/ 现有最大编号 +1）
存储位置：.devpace/risks/
4 种来源：pre-flight（开发前扫描）| runtime（开发中发现）| retrospective（回顾总结）| external（外部报告）
3 级严重度：Low（可延后处理）| Medium（需计划处理）| High（需立即处理）
4 种状态：open → mitigated / accepted / resolved
综合风险等级：取所有扫描维度的最高严重度等级
关联：每个风险可关联 0~N 个 CR
```

## 文件结构

```markdown
# [风险标题]

> - **ID**：RISK-[NNN]
> - **来源**：[pre-flight | runtime | retrospective | external]
> - **严重度**：[Low | Medium | High]
> - **状态**：[open | mitigated | accepted | resolved]
> - **关联 CR**：[CR-xxx, CR-yyy | 无]
> - **发现日期**：[YYYY-MM-DD]

## 发现

[问题描述：什么风险、在什么条件下会发生、可能造成什么影响]

## 建议

[缓解或解决方案：推荐的处理方式、替代方案、预期效果]

## 处理记录

| 日期 | 操作 | 状态变更 | 说明 |
|------|------|---------|------|
| [YYYY-MM-DD] | [操作描述] | [旧状态 → 新状态] | [补充说明] |
```

## 字段合法值

### 来源（source）

| 值 | 定义 | 典型场景 |
|----|------|---------|
| pre-flight | 开发前扫描发现的风险 | /pace-scan 在 CR 进入 developing 前识别 |
| runtime | 开发过程中发现的风险 | /pace-checkpoint 或开发中主动识别 |
| retrospective | 回顾总结中识别的风险 | /pace-retro 分析历史模式得出 |
| external | 外部报告或人工录入的风险 | 安全审计、依赖漏洞通报、团队成员报告 |

### 严重度（severity）

| 值 | 定义 | 处理优先级 |
|----|------|-----------|
| Low | 影响有限，可延后处理 | 记录并在合适时机处理，不阻塞当前工作 |
| Medium | 有实质影响，需计划处理 | 应在当前迭代或下一迭代内解决 |
| High | 影响严重，需立即处理 | 必须在继续开发前处理或制定明确缓解措施 |

### 状态（status）

| 值 | 定义 | 后续可转换到 |
|----|------|-------------|
| open | 已识别，尚未处理 | mitigated / accepted / resolved |
| mitigated | 已采取缓解措施，风险降低但未完全消除 | resolved |
| accepted | 已知风险，经评估决定接受 | resolved |
| resolved | 风险已消除，不再存在 | （终态） |

## 状态机

```
open ──→ mitigated ──→ resolved
  │                       ↑
  ├──→ accepted ──────────┘
  │
  └──→ resolved
```

### 转换规则

| 转换 | 触发者 | 条件 | 处理记录要求 |
|------|--------|------|-------------|
| open → mitigated | Claude 或人类 | 已实施缓解措施且验证有效 | 记录缓解措施内容和验证方式 |
| open → accepted | 人类（需明确决策） | 风险可控且处理成本高于收益 | 记录接受理由和风险边界 |
| open → resolved | Claude 或人类 | 风险根因已消除 | 记录消除方式和验证结果 |
| mitigated → resolved | Claude 或人类 | 残余风险已完全消除 | 记录最终解决方式 |
| accepted → resolved | Claude 或人类 | 条件变化使风险不再存在 | 记录风险消失的原因 |

**约束**：

- resolved 是终态，不可回退
- accepted 必须由人类决策，Claude 不可自动将风险标记为 accepted
- 每次状态变更必须在"处理记录"表追加一行

## 综合风险等级计算

当一次扫描产生多个风险条目时，**综合风险等级 = 所有风险条目中严重度的最高值**。

| 场景 | 各风险严重度 | 综合等级 |
|------|------------|---------|
| 全部低风险 | Low, Low, Low | Low |
| 存在中等风险 | Low, Medium, Low | Medium |
| 存在高风险 | Low, Medium, High | High |
| 单一风险 | High | High |

综合等级用于 /pace-scan 的扫描报告摘要，帮助快速判断整体风险水位。单个 RISK-NNN.md 文件只记录自身的严重度，不记录综合等级。

## 命名规则

- 文件名格式：`RISK-NNN.md`，NNN 为三位数字，从 001 开始递增
- 存储目录：`.devpace/risks/`
- 编号规则：取 `.devpace/risks/` 目录下现有 `RISK-*.md` 文件的最大编号 +1
- 目录不存在时由创建方（如 /pace-scan）自动创建
- 编号不复用：即使旧风险已 resolved，其编号不回收

## 更新时机

| 操作 | 触发场景 | 动作 |
|------|---------|------|
| 创建 | /pace-scan 发现新风险 | 新建 RISK-NNN.md，状态 open |
| 追加记录 | /pace-checkpoint 检查进展 | 在处理记录表追加进展行 |
| 状态更新 | 风险被缓解/接受/解决 | 更新头部状态 + 处理记录追加行 |
| 趋势引用 | /pace-retro 回顾分析 | 引用已有风险文件做趋势统计，不修改原文件 |
