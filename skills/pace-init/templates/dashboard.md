# 度量仪表盘

> 最近更新：— | 迭代：—

## 质量保障

| 指标 | 当前值 | 说明 |
|------|:------:|------|
| 质量检查一次通过率 | — | 首次检查即通过的 CR 比例 |
| 人类打回率 | — | review 打回次数 / 总 review 次数 |
| 缺陷逃逸 | — | merged 后发现的缺陷数 |

## 缺陷管理

| 指标 | 当前值 | 说明 |
|------|:------:|------|
| 缺陷修复周期 | — | defect CR 从 created 到 merged 的天数均值 |
| 缺陷严重度分布 | — | critical/major/minor/trivial 各数量 |
| 缺陷引入追溯 | — | 可追溯到引入 CR 的比例 |
| Hotfix 比例 | — | hotfix CR / 总 defect+hotfix CR |

## 业务价值对齐

| 指标 | 当前值 | 目标 |
|------|:------:|:----:|
| 成效指标达成率 | — | — |
| 价值链完整率 | — | — |
| 需求交付周期 | — | — |

## DORA 度量

> 完整 DORA 度量需要 Release 管理功能。无 Release 流程时部分指标不可用。

| 指标 | 当前值 | 说明 |
|------|:------:|------|
| 部署频率 | — | Release 关闭次数 / 时间段 |
| 变更前置时间 | — | CR created → released 的天数均值 |
| 变更失败率 | — | 产生 defect 的 Release / 总 Release |
| MTTR | — | defect/hotfix CR 从 created 到 merged 天数均值 |
