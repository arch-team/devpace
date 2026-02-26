# 关闭迭代详细规程

> **职责**：关闭当前迭代的详细处理流程（Step 2）。

## Step 2：关闭当前迭代

> 仅在 `$ARGUMENTS` 为 `close` 或用户确认关闭时执行。

1. 更新 `iterations/current.md`：
   - 填写偏差快照（计划 PF 数 vs 实际完成数）
   - 标记未完成 PF 的状态（⏸️ 延后 / 🔄 续入下个迭代）
2. 归档：将 `current.md` 重命名为 `iter-N.md`（N = 已有归档文件数 +1）
3. **自动轻量回顾**（归档完成后立即执行）：
   - 从归档的 `iter-N.md` 偏差快照 + `.devpace/backlog/` CR 事件表提取基本指标：
     - PF 完成率（计划 vs 实际完成）
     - 平均 CR 周期（created→merged 天数均值）
     - 迭代速度（实际完成 PF 数 / 计划 PF 数）
   - 更新 `.devpace/metrics/dashboard.md`（追加或更新上述 3 项指标）
   - 输出 2 行数据摘要："本迭代完成率 X%，平均 CR 周期 N 天，迭代速度 Y。"
   - 完整回顾报告仍需 `/pace-retro`——这里只确保 dashboard.md 基础数据不缺失
4. 建议用户运行 `/pace-retro` 做完整迭代回顾（不自动触发）
