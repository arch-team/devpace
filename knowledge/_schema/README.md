# _schema/ 索引

Schema 文件按功能角色分为四组。Fan-in = 产品层中引用该文件的文件数。

## 分类标准

**一级判断：功能角色**（文件在 devpace 系统中扮演什么角色）
**二级消歧：结构特征**（当功能角色有重叠时，用客观结构属性消歧）

### 新文件判断决策树

```
新 Schema 文件
│
├─ 定义的对象在 Vision→OBJ→Epic→OPP→BR→PF→CR 链上或其承载容器？
│  └─ Yes → entity/
│
├─ 定义 devpace 与外部系统的对接配置？
│  └─ Yes → integration/
│
├─ 有独立状态机且驱动其他对象状态转换？
│  └─ Yes → process/
│
├─ 作为执行类 Skill 的运行时输入，直接约束执行路径？
│  └─ Yes → process/
│
└─ 以上均否 → auxiliary/
```

## entity/ — 价值交付链对象

BizDevOps 价值交付链上的业务对象及其承载容器。

**判断标准**（满足任一）：
1. 属于 Vision → OBJ → Epic → (Opportunity →) BR → PF → CR 链上的节点
2. 是承载价值链的项目级容器（project）

**排除标准**：有 ID + 状态机但不在价值链上 → 不属于 entity（如 RISK-NNN → auxiliary）。

| 文件 | 行数 | Fan-in | 主要消费者 |
|------|------|--------|-----------|
| cr-format.md | 447 | 10 | pace-dev, pace-change, pace-feedback, pace-test, pace-pulse, rules |
| project-format.md | 550 | 1 | pace-init, pace-biz, rules |
| br-format.md | 167 | 1 | pace-dev |
| pf-format.md | 126 | 1 | pace-dev |
| epic-format.md | 153 | 1 | pace-biz |
| obj-format.md | 160 | 2 | pace-biz, pace-init + project-format.md (间接) |
| vision-format.md | 150 | 1 | pace-init + project-format.md (间接) |
| opportunity-format.md | 107 | 1 | pace-biz |

## process/ — 运行时流程机制

定义运行时流程行为的 Schema——在 Skill 执行过程中被读取，直接决定或约束执行路径。

**判断标准**（满足任一）：
1. 有独立状态机且主动驱动工作流转换（如 Gate 触发状态跃迁、迭代推进 PF 状态）
2. 作为执行类 Skill 的**运行时输入**直接约束执行行为（如 test-strategy 决定测试执行范围）

**消歧**："运行时输入"vs"背景参考"——运行时输入在 Skill 执行路径中被程序性读取并影响分支逻辑；背景参考仅提供上下文但不改变执行路径。

| 文件 | 行数 | Fan-in | 主要消费者 | 归属理由 |
|------|------|--------|-----------|---------|
| checks-format.md | 208 | 7 | pace-init, pace-sync, rules, cr-format, checks-guide | Gate 1/2 驱动 CR 状态转换 |
| iteration-format.md | 104 | 4 | pace-plan, pace-change, rules | 驱动 PF 状态进展 |
| release-format.md | 138 | 3 | pace-release, pace-init, theory.md | staging→deployed→verified→closed 状态机 |
| test-strategy-format.md | 185 | 2 | pace-test, pace-dev | pace-test 运行时读取，决定测试范围和覆盖阈值 |
| test-baseline-format.md | 86 | 3 | pace-test, pace-retro | pace-test 运行时读取基线数据，决定回归对比基准 |
| state-format.md | 136 | 1 | rules | 会话启动必读，决定恢复起点和当前任务 |

## integration/ — 外部系统集成

devpace 与外部工具（GitHub/Linear/Jira/CI/CD）对接的配置格式。

**判断标准**：定义 devpace 与外部系统的映射关系或连接配置。

| 文件 | 行数 | Fan-in | 主要消费者 |
|------|------|--------|-----------|
| sync-mapping-format.md | 152 | 4 | pace-sync |
| integrations-format.md | 212 | 3 | pace-init, pace-release |

## auxiliary/ — 辅助记录与支撑契约

不属于价值链对象、不直接约束流程执行路径的 Schema——包括跨 CR 辅助记录、经验积累、评估算法、跨 Skill 数据契约、项目配置。

**判断标准**：不满足 entity / process / integration 任一条件，具体包括：
1. **辅助记录**：有 ID + 生命周期但不在价值链上的跨 CR 记录（risk, adr, incident）
2. **经验积累**：度量/学习产出物，被回顾和决策参考消费（insights）
3. **评估算法**：可复用的评分/分类规则，被流程作为参数消费但本身不是流程（readiness-score, merge-strategy）
4. **跨 Skill 契约**：Skill 间传递数据的接口格式定义（accept-report-contract）
5. **项目配置**：项目级技术约定和上下文（context）

| 文件 | 行数 | Fan-in | 主要消费者 | 子类 |
|------|------|--------|-----------|------|
| insights-format.md | 277 | 4 | pace-learn, pace-retro, pace-init | 经验积累 |
| context-format.md | 150 | 2 | pace-dev, pace-init | 项目配置 |
| risk-format.md | 126 | 2 | pace-guard, pace-dev | 辅助记录 |
| readiness-score.md | 53 | 2 | pace-biz | 评估算法 |
| incident-format.md | 95 | 1 | pace-feedback (incident procedures) | 辅助记录 |
| accept-report-contract.md | 86 | 1 | pace-review | 跨 Skill 契约 |
| adr-format.md | 82 | 1 | pace-trace | 辅助记录 |
| merge-strategy.md | 41 | 1 | pace-biz | 评估算法 |

## 边界文件归属记录

以下文件在分类边界，新标准下有明确归属，无需移动：

| 文件 | 目录 | 判断路径 |
|------|------|---------|
| test-strategy-format | process/ | 判断标准 2：pace-test 运行时读取决定测试范围 |
| test-baseline-format | process/ | 判断标准 2：pace-test 运行时读取决定回归基准 |
| state-format | process/ | 判断标准 2：会话启动必读，决定恢复起点 |
| readiness-score | auxiliary/ | 评估算法，被作为参数消费而非驱动流程 |
| accept-report-contract | auxiliary/ | 跨 Skill 数据契约 |
| incident-format | auxiliary/ | 辅助记录(预留)，激活后仍属 auxiliary（不在价值链上） |
