# devpace 度量指标定义

> **职责**：定义 devpace 使用的度量指标——名称、计算方式、用途。这是度量指标的唯一定义来源。

**消费者**：
- `knowledge/theory.md §8`：度量理论框架（BizDevOps 方法论）
- `/pace-retro` Skill：运行时度量采集和仪表盘生成

## §0 速查卡片

```
6 类度量：质量保障 | 缺陷管理 | 业务价值对齐 | DORA（需 Release）| 迭代速度 | 测试效能
数据来源：CR 事件表 + Git 历史 + project.md + dashboard.md
指标定义见各 section 表格
```

---

## 质量保障指标

| 指标 | 计算方式 | 用途 | 数据来源 |
|------|---------|------|---------|
| 质量检查一次通过率 | 首次即通过的 CR / 总 CR | 反映代码质量趋势 | CR 质量检查 checkbox |
| 人类打回率 | 打回次数 / 总 review 次数 | 反映设计质量 | CR 事件表 in_review→developing 次数 |
| 缺陷逃逸率 | merged 后发现的缺陷数 / 总 merged CR | 反映验证充分性 | backlog/ 中 type:defect CR 数量 vs 总 merged feature CR |

## 缺陷管理指标

| 指标 | 计算方式 | 用途 | 数据来源 |
|------|---------|------|---------|
| 缺陷修复周期 | type:defect CR 从 created 到 merged 的天数均值 | 反映缺陷响应速度 | defect CR 事件表时间戳 |
| 缺陷严重度分布 | 各严重度（critical/major/minor/trivial）的 defect CR 数量 | 反映问题严重程度趋势 | defect CR 严重度字段 |
| 缺陷引入追溯 | defect CR 根因分析中"引入点"可追溯到具体 feature CR 的比例 | 反映根因分析能力 | defect CR 根因分析 section |
| Hotfix 比例 | type:hotfix CR / 总 defect+hotfix CR | 反映紧急修复频率 | backlog/ CR type 字段 |

## 业务价值对齐指标

| 指标 | 计算方式 | 用途 | 数据来源 |
|------|---------|------|---------|
| 成效指标达成率（MoS） | MoS 已满足项 / 总项 | 目标对齐度 | project.md MoS checkbox |
| 需求交付周期 | 功能首个 CR 创建到所有 CR merged | 交付效能 | CR 事件表时间戳 + git log |
| 价值链完整率 | 有完整 BR→PF→CR 链路的占比 | 可追溯性健康度 | project.md 价值功能树 |

## DORA 代理度量

> ⚠️ devpace 的 DORA 指标是**代理值**——基于 .devpace/ 内的 CR 和 Release 数据计算，不等同于生产级 DORA（后者需要 CI/CD 平台的部署和监控数据）。代理值反映"开发阶段的交付节奏"，适合个人开发者和小团队自我衡量。

| 指标 | 计算方式 | 用途 | 数据来源 |
|------|---------|------|---------|
| 部署频率 | Release 关闭次数 / 时间段 | 反映交付节奏 | releases/ 目录中 closed 状态 Release 数 |
| 变更前置时间 | CR created → released 的天数均值 | 反映从代码到生产的速度 | CR 事件表（created + released 时间戳） |
| 变更失败率 | Release 后产生 defect 的 Release / 总 Release | 反映发布质量 | Release 关联的 defect CR |
| MTTR（平均恢复时间） | type:defect/hotfix CR 从 created 到 merged 天数均值 | 反映故障恢复速度 | defect/hotfix CR 事件表时间戳 |

### 基准分级映射表

/pace-retro 使用以下规则将代理值映射为 Elite/High/Medium/Low 分级（参考 DORA State of DevOps Report，针对代理值场景适当放宽）：

| 指标 | Elite | High | Medium | Low |
|------|-------|------|--------|-----|
| 部署频率 | ≥1 次/周 | 1 次/2 周 | 1 次/月 | <1 次/月 |
| 变更前置时间 | ≤1 天 | ≤3 天 | ≤7 天 | >7 天 |
| 变更失败率 | ≤15% | ≤30% | ≤45% | >45% |
| MTTR | ≤1 天 | ≤3 天 | ≤7 天 | >7 天 |

**分级规则**：
- 每个指标独立分级，不取综合评分
- 无数据的指标标注"无数据"，不参与分级
- 趋势对比基于 dashboard.md 中上次 DORA 报告的值：值改善 → ↑（趋好），值恶化 → ↓（趋差），变化 <10% → →（持平），无历史数据 → —（首次）

## 迭代速度指标

| 指标 | 计算方式 | 用途 | 数据来源 |
|------|---------|------|---------|
| 迭代速度 | 实际完成 PF 数 / 计划 PF 数 | 范围估算基准——pace-plan 引用此值限制下迭代纳入 PF 数 | iterations/iter-*.md 偏差快照 |
| 计划准确度 | 1 - \|实际 - 计划\| / 计划 | 估算校准——反映估算与实际的偏差程度 | iterations/iter-*.md 偏差快照 |

### 使用规则

- `/pace-plan` Step 3.3 范围估算时引用迭代速度：速度 <1.0 → 建议纳入 PF 数不超过上迭代实际完成数
- `/pace-plan close` Step 2 自动计算并更新到 dashboard.md
- 无历史数据（首次迭代）时使用启发式估算（S/M/L 分级，详见 plan-procedures.md）

## 测试效能指标

| 指标 | 计算方式 | 用途 | 数据来源 |
|------|---------|------|---------|
| 需求验证覆盖率 | 有自动验证的 PF 验收条件 / 总 PF 验收条件 | 反映测试与需求的对齐度 | test-strategy.md 策略总览表 |
| AI 验收通过率 | /pace-test accept 一次通过的 CR / 总执行 accept 的 CR | 反映 AI 验收验证效能 | CR 验证证据 section |
| 验证-审批一致率 | AI accept 通过且 Gate 3 也通过 / 总 AI accept 通过的 CR | 反映 AI 验证与人类判断的一致性 | accept 结果 + CR 事件表 Gate 3 记录 |
| 测试策略完备度 | 有测试策略的 PF / 总 PF | 反映测试规划完整性 | .devpace/rules/test-strategy.md |
