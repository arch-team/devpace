---
description: Auto-invoked during advance mode after 5 checkpoints or 30+ minutes on same CR, or when rhythm anomalies are detected (stalled CR, skipped gates, overdue review).
user-invocable: false
allowed-tools: Read, Glob
model: haiku
---

# pace-pulse — 节奏心跳检查

Claude 自动调用的健康度检查 Skill，不暴露给用户。在推进模式中周期性执行，检测研发节奏异常并输出非打断式建议。

## 触发条件

由 `rules/devpace-rules.md` §10 定义触发时机：
- 推进模式中每完成 5 个 checkpoint 后
- 会话中超过 30 分钟未切换 CR
- 每会话总提醒上限 3 条（含 §1 会话开始提醒），达上限后静默

## 流程

### Step 1：采集信号

1. 读取 `.devpace/state.md`：当前工作状态
2. 读取 `.devpace/iterations/current.md`（如存在）：PF 完成率
3. 扫描 `.devpace/backlog/` 所有 CR 文件：状态分布
4. 读取 `.devpace/metrics/dashboard.md`（如存在）：最近更新日期

### Step 2：评估信号并输出建议

读取 `pulse-procedures.md` 中的信号评估表和建议模板执行评估。无信号时静默，有信号时输出最高优先级的 1-2 条建议。

## 输出

0-2 行非打断式建议（自然语言，不含 ID、状态机术语）。无异常时完全静默。详细评估规则和建议模板见 `pulse-procedures.md`。
