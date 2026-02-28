---
description: Auto-invoked during advance mode after 5 checkpoints or 30+ minutes on same CR, at session start/end, or when rhythm anomalies are detected.
user-invocable: false
allowed-tools: Read, Glob, Write
model: haiku
---

# pace-pulse — 节奏心跳检查

Claude 自动调用的健康度检查 Skill，不暴露给用户。在推进模式中周期性执行，检测研发节奏异常并输出非打断式建议。

## 触发条件

由 `rules/devpace-rules.md` §10 和 §6 定义触发时机：
- 推进模式中每完成 5 个 checkpoint 后（脉搏检查）
- 会话中超过 30 分钟未切换 CR
- 会话开始时（§1 分层摘要）
- 会话结束时（§6 节奏摘要）
- 提醒配额：标准 ≤3 条/会话（长会话 >2h 放宽至 ≤5 条），正向反馈和会话结束摘要不计配额

## 执行路由

**重要**：根据触发场景，仅读取路由表中对应的 procedures 文件，不加载其他 procedures。

| 触发场景 | 加载文件 |
|---------|---------|
| 脉搏检查（§10，每 5 checkpoint） | `pulse-procedures-core.md` |
| 会话开始（§1） | `pulse-procedures-session-start.md` + `pulse-procedures-snooze.md` |
| 会话结束（§6） | `pulse-procedures-session-end.md` |
| CR merged 后 Snooze 检测（§11） | `pulse-procedures-snooze.md` |

## 流程

### Step 1：采集信号

1. 读取 `.devpace/state.md`：当前工作状态
2. 读取 `.devpace/iterations/current.md`（如存在）：PF 完成率、迭代阶段
3. 扫描 `.devpace/backlog/` 所有 CR 文件：状态分布
4. 读取 `.devpace/metrics/dashboard.md`（如存在）：最近更新日期
5. 读取 `.devpace/risks/`（如存在）：风险积压状态

### Step 2：按路由表加载对应文件执行评估

根据触发场景加载对应 procedures 文件，执行信号评估和建议输出。

### Step 3：记录执行时间戳

将当前时间戳（`Date.now()` 毫秒值）写入 `.devpace/.pulse-last-run`，供 pulse-counter Hook 协调避免双重提醒。

## 输出

- **脉搏检查**：0-2 行 `💡` 建议，含可操作命令。严重度升级用 `⚠️`
- **正向反馈**：`✓` 前缀，≤1 次/会话
- **会话结束**：`📊` 前缀，1-2 行节奏总结
- **会话开始**：分层摘要（最高 1 条完整建议 + 精简列表），≤3 行
