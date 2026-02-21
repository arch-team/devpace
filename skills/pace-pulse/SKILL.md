---
description: Internal health pulse check. Auto-invoked during advance mode after 3 checkpoints or 30+ minutes on same CR. Detects rhythm anomalies and suggests corrections.
user-invocable: false
allowed-tools: Read, Glob
---

# pace-pulse — 节奏心跳检查

Claude 自动调用的健康度检查 Skill，不暴露给用户。在推进模式中周期性执行，检测研发节奏异常并输出非打断式建议。

## 触发条件

由 `rules/devpace-rules.md` §10 定义触发时机：
- 推进模式中每完成 3 个 checkpoint 后
- 会话中超过 30 分钟未切换 CR

## 流程

### Step 1：采集信号

1. 读取 `.devpace/state.md`：当前工作状态
2. 读取 `.devpace/iterations/current.md`（如存在）：PF 完成率
3. 扫描 `.devpace/backlog/` 所有 CR 文件：状态分布
4. 读取 `.devpace/metrics/dashboard.md`（如存在）：最近更新日期

### Step 2：评估信号

| 信号 | 检测方式 | 阈值 |
|------|---------|------|
| CR 滞留 | 当前 CR 在 developing 的 checkpoint 计数 | > 5 次 |
| 迭代接近尾声 | current.md PF 完成率 | > 80% |
| Review 积压 | backlog/ 中 in_review 状态 CR 数 | > 2 个 |
| 检查项重复失败 | 当前 CR 质量检查同一项失败次数 | > 2 次 |
| 会话高产出 | 本会话已 merged 的 CR 数 | ≥ 2 个 |
| 迭代频繁变更 | current.md 变更记录条数 | > 3 条 |

### Step 3：输出建议

- 无信号触发 → 静默，不输出任何内容
- 有信号触发 → 输出 1-2 行自然语言建议，格式：

```
💡 [建议内容]
```

**建议模板**：

| 信号 | 建议 |
|------|------|
| CR 滞留 | "当前变更范围较大，考虑拆分为更小的变更？" |
| 迭代接近尾声 | "迭代完成率已超 80%，建议安排 /pace-plan 规划下一迭代。" |
| Review 积压 | "有 N 个变更等待 review，建议先处理积压。" |
| 检查项重复失败 | "质量检查 [项目] 连续失败，建议调整检查策略或修改实现方案。" |
| 会话高产出 | "本次会话已完成 N 个变更，建议做一次增量回顾（/pace-retro update）。" |
| 迭代频繁变更 | "本迭代已有 N 次范围变更，注意目标偏移风险。" |

## 输出

0-2 行非打断式建议（自然语言，不含 ID、状态机术语）。无异常时完全静默。
