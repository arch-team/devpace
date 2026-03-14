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

## 信号快照缓存

### 脚本采集（推荐）

信号采集脚本 `skills/pace-next/scripts/collect-signals.mjs` 实现全部 24 个信号条件的确定性评估：

```
Bash: node ${CLAUDE_PLUGIN_ROOT}/skills/pace-next/scripts/collect-signals.mjs .devpace [--role <角色>] [--cache] [--cache-read]
```

- `--cache`：采集后自动写入 `.signal-cache`（JSON 格式）
- `--cache-read`：先检查缓存（< 5 分钟），命中则跳过采集
- 输出 JSON：`{ triggered[], top_signal, role, cr_summary, timestamp, cached }`

### 写入方

pace-pulse 执行信号采集后（或脚本 `--cache` 模式），将结果写入 `.devpace/.signal-cache`：

```
# .signal-cache — 脚本输出时为 JSON 格式，手动采集时为纯文本格式
# JSON 格式（脚本产出）：{ triggered[], top_signal, cr_summary, timestamp }
# 纯文本格式（向后兼容）：
timestamp: <ISO 8601>
cr_summary: total=N, developing=N, in_review=N, merged=N, paused=N
triggered: S1(count=2), S8(rate=85%), S13(pf=PF-003)
top_signal: S1
risk_summary: open=N, high=N
```

**写入时机**：
- 脚本 `--cache` 模式执行后（JSON 格式）
- pace-pulse session-start 完成信号检测后（纯文本格式）
- pace-pulse core 周期性检查完成后（纯文本格式）

### 读取方

pace-next 和 pace-status 在执行信号采集前，先检查缓存：

1. 检查 `.devpace/.signal-cache` 是否存在
2. 存在 → 读取 `timestamp` 字段，计算距当前时间的差值
3. 差值 < 5 分钟 → **命中缓存**，直接使用 `triggered` 和 `top_signal` 字段，跳过完整采集
4. 差值 ≥ 5 分钟 或文件不存在 → **缓存过期**，执行完整采集流程

### 缓存失效

以下事件使缓存立即失效（消费方忽略缓存，重新采集）：
- CR 状态变更（merged/paused/created 等）后，pace-dev 会写入新的 CR 文件，时间戳自然超过缓存
- 用户手动删除 `.signal-cache`
- **不主动删除缓存**——依靠 TTL（5 分钟）自然过期

### 容错

- `.signal-cache` 格式错误或字段缺失 → 视为过期，执行完整采集
- `.signal-cache` 不在 .gitignore 中（每次写入覆盖，无需版本控制）
- 缓存仅是性能优化，不是正确性依赖——任何异常都 fallback 到完整采集
