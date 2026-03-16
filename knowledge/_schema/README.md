# _schema/ 索引

Schema 文件按功能域分为四组。Fan-in = 产品层中引用该文件的文件数。

## entity/ — 价值链实体

BizDevOps 管道上的持久化对象（OBJ→Epic→BR→PF→CR + 项目级对象）。

| 文件 | 行数 | Fan-in | 主要消费者 |
|------|------|--------|-----------|
| cr-format.md | 447 | 10 | pace-dev, pace-change, pace-feedback, pace-test, pace-pulse, rules |
| project-format.md | 550 | 1 | pace-init, pace-dev, rules |
| insights-format.md | 272 | 4 | pace-learn, pace-retro, pace-biz |
| br-format.md | 167 | 2 | pace-dev, pace-biz |
| pf-format.md | 126 | 2 | pace-dev, pace-biz |
| epic-format.md | 153 | 1 | pace-biz |
| obj-format.md | 160 | 1 | project-format.md (间接) |
| vision-format.md | 150 | 1 | project-format.md (间接) |
| opportunity-format.md | 107 | 1 | pace-biz |

## process/ — 流程与工作流

驱动状态流转的流程性 schema。

| 文件 | 行数 | Fan-in | 主要消费者 |
|------|------|--------|-----------|
| checks-format.md | 208 | 4 | pace-init, pace-change, rules |
| iteration-format.md | 104 | 4 | pace-plan, pace-change, rules |
| test-strategy-format.md | 185 | 2 | pace-test, pace-dev |
| test-baseline-format.md | 86 | 3 | pace-test, pace-retro |
| release-format.md | 138 | 1 | pace-release, theory.md |
| state-format.md | 136 | 1 | rules |

## integration/ — 外部集成

外部工具对接的配置格式。

| 文件 | 行数 | Fan-in | 主要消费者 |
|------|------|--------|-----------|
| sync-mapping-format.md | 152 | 4 | pace-sync |
| integrations-format.md | 212 | 3 | pace-init, pace-release |

## auxiliary/ — 辅助与支撑

决策记录、风险、上下文等支撑性 schema。

| 文件 | 行数 | Fan-in | 主要消费者 |
|------|------|--------|-----------|
| context-format.md | 150 | 2 | pace-dev, pace-init |
| risk-format.md | 126 | 2 | pace-guard, pace-dev |
| readiness-score.md | 53 | 2 | pace-biz |
| incident-format.md | 95 | 0 | (预留，当前无消费者) |
| accept-report-contract.md | 86 | 1 | pace-review |
| adr-format.md | 82 | 1 | pace-trace |
| merge-strategy.md | 41 | 1 | pace-biz |
