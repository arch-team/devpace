# 角色自动推断规程

> **职责**：定义自动推断用户角色的关键词映射和粘性规则。被 devpace-rules.md §13 引用为权威源。

## §0 速查卡片

- **关键词映射**：6 组关键词→角色映射（含中英文）
- **粘性规则**：推断后需连续 2+ 不同信号才切换，防抖动
- **置信度**：≥2 个同角色关键词命中才触发推断，否则保持当前角色
- **优先级**：显式设置 > 项目默认 > 自动推断 > Dev 兜底

## 关键词→角色映射表

| 角色 | 触发关键词（中文） | 触发关键词（英文） | 上下文线索 |
|------|-------------------|-------------------|-----------|
| Biz Owner | 业务目标、ROI、MoS、收入、商业、营收、投资回报、市场 | business, revenue, ROI, market, objective, strategy | 讨论业务目标、商业模式、市场策略 |
| PM | 交付、迭代、排期、需求、优先级、路线图、里程碑、范围 | delivery, iteration, sprint, priority, roadmap, milestone, scope | 讨论排期、功能优先级、迭代规划 |
| Dev | 代码、实现、重构、架构、API、模块、函数、调试、修复 | code, implement, refactor, architecture, API, module, debug, fix | 讨论技术实现、代码结构、Bug 修复 |
| Tester | 测试、缺陷、覆盖率、回归、验证、质量、Bug、QA | test, defect, coverage, regression, verify, quality, bug, QA | 讨论测试策略、缺陷追踪、质量保证 |
| Ops | 部署、发布、监控、运维、性能、稳定、SLA、告警 | deploy, release, monitor, operations, performance, stability, SLA | 讨论部署流程、运维监控、生产稳定性 |
| Dev（默认） | — | — | 无明确信号时维持 Dev |

## 粘性规则（防抖动）

1. **初始状态**：会话开始默认 Dev（除非 project.md 有 `preferred-role` 配置）
2. **推断阈值**：单轮对话中需命中 ≥2 个同角色关键词才触发推断
3. **切换惰性**：推断出新角色后，不立即切换——需在连续 2 轮对话中持续命中该角色关键词
4. **回退保护**：单轮对话中出现多角色混合关键词时，保持当前角色不切换
5. **显式覆盖清除**：用户显式 `/pace-role <角色>` 后，自动推断暂停直到 `/pace-role auto`

## 会话级状态

```
current_role: dev          # 当前生效角色
role_source: auto|explicit|project_default  # 角色来源
inference_buffer: []       # 最近 3 轮推断信号缓冲
```
