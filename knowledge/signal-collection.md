# 信号采集共享规程

> **职责**：定义 pace-next / pace-pulse / pace-status 共用的数据源读取步骤。各 Skill 引用本文件执行采集，避免同一会话重复扫描。

## 数据源与读取规则

按以下顺序读取（目录/文件不存在时静默跳过）：

| # | 数据源 | 读取内容 | 消费信号 |
|:-:|--------|---------|---------|
| 1 | `.devpace/backlog/*.md` | 所有 CR 的状态字段、类型字段、blocked_by 字段 | S1/S3/S4/S9/S10/S13/S15/S21/S22/S24 |
| 2 | `.devpace/state.md` | 当前工作、下一步、进行中摘要 | S3（上下文连续性） |
| 3 | `.devpace/releases/*.md` | Release 状态字段 | S5 |
| 4 | `.devpace/risks/*.md` | 风险严重度、状态字段 | S2/S6 |
| 5 | `.devpace/iterations/current.md` | PF 完成率、周期字段、变更记录 | S7/S8/S14 |
| 6 | `.devpace/metrics/dashboard.md` | 最近更新日期 | S9 |
| 7 | `.devpace/project.md` | MoS checkbox、PF 列表、BR 列表、Epic 链接、范围 section | S12/S13/S16/S17/S18/S19（价值链上下文+发现信号） |
| 8 | `.devpace/integrations/sync-mapping.md` | CR 关联映射、最后同步时间 | S11 |
| 9 | `.devpace/metrics/insights.md` | 经验 pattern（可选增强） | 经验增强（Step 4） |
| 10 | `.devpace/epics/*.md` | Epic 状态、MoS、BR 列表、完成度 | S16（Epic 进度信号） |
| 11 | `.devpace/opportunities.md` | Opportunity 状态 | S17（未处理机会信号） |

## 读取策略

- 使用 Glob 扫描 `backlog/*.md`、`releases/*.md`、`risks/*.md`，再用 Grep 提取状态字段
- 文件不存在或目录为空时，相关信号视为"未命中"
- **不全量读取文件内容**，只提取决策所需字段（状态、类型、日期、完成率等）
- 信号编号引用 `knowledge/signal-priority.md`（权威源）

## 价值链上下文采集

为支持建议模板中的价值链信息（A2 需求），采集时额外读取：

| 采集项 | 来源 | 用途 |
|--------|------|------|
| CR → PF 映射 | CR 文件中的功能关联字段 | 建议模板附加 PF 名称 |
| PF → BR 映射 | project.md 功能树中 PF 的父 BR | 建议模板附加 BR 名称（Biz/PM 角色） |
| BR → Epic 映射 | project.md 功能树中 BR 的父 Epic（如有） | 建议模板附加 Epic 信息（Biz 角色） |
| BR → OBJ 映射 | project.md 功能树中 BR 的父 OBJ | 建议模板附加 OBJ 信息（Biz 角色） |
| Epic → OPP 映射 | Epic 文件中的来源字段 | 建议模板附加 Opportunity 追溯（Biz 角色） |

**角色差异化**：Dev 仅采集 CR→PF 层 | PM 采集到 PF+BR+迭代层 | Biz 采集到 PF+BR+Epic+OBJ+OPP 层。

## 信号快照缓存（中期优化）

当 pace-pulse 执行后，可将信号快照写入 `.devpace/.signal-cache`：

```
# .signal-cache format (plain text)
timestamp: <ISO 8601>
triggered: S1(count=2), S8(rate=85%)
```

pace-next 检测到新鲜快照（< 5 分钟）时可直接读取，避免重复扫描。快照超期或不存在时正常执行完整采集。

**当前阶段**：各 Skill 独立执行采集步骤（引用本文件的读取规则），缓存机制待后续实现。
