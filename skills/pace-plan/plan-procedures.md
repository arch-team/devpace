# 迭代规划详细规程

> **职责**：迭代规划的详细处理流程。/pace-plan 的 Step 1-4 详细逻辑。经验引用时机详见 `knowledge/experience-reference.md`。

## Step 1：评估当前迭代状态

1. 读取 `.devpace/iterations/current.md`（不存在则跳到 Step 3）
2. 读取 `.devpace/project.md` 的价值功能树
3. 汇总当前迭代状态：
   - PF 完成率（✅ 数 / 总数）
   - 未完成 PF 列表及其 CR 状态
   - 变更记录条数
4. 用 1-2 句话告知用户当前迭代进展

## Step 2：关闭当前迭代

> 仅在 `$ARGUMENTS` 为 `close` 或用户确认关闭时执行。

1. 更新 `iterations/current.md`：
   - 填写偏差快照（计划 PF 数 vs 实际完成数）
   - 标记未完成 PF 的状态（⏸️ 延后 / 🔄 续入下个迭代）
2. 归档：将 `current.md` 重命名为 `iter-N.md`（N = 已有归档文件数 +1）
3. 建议用户运行 `/pace-retro` 做迭代回顾（不自动触发）

## Step 3：规划新迭代

> `$ARGUMENTS` 为 `next` 时直接进入；否则在 Step 2 完成后或无当前迭代时进入。

1. 读取 `.devpace/project.md` 功能树，列出所有待开始（⏳）和进行中（🔄）的 PF
2. 如有上一迭代延后的 PF，优先列出并标注"上迭代延后"
3. **范围估算**（如有历史数据）：
   - 读取 `.devpace/metrics/dashboard.md` 获取历史平均变更周期
   - 读取已归档迭代（`iterations/iter-*.md`）统计历史 CR 完成天数
   - 按每个候选 PF 的预估 CR 数 × 平均变更周期计算工作量
   - 预估工作量超过迭代周期时，附加建议："预估工作量可能超出迭代周期，建议缩减 N 个 PF 或延长迭代"
   - 无历史数据时跳过估算，正常推进
4. **业务引导增强**：
   - 如有上一迭代 `.devpace/metrics/dashboard.md` 数据 → 分析上迭代 MoS 达成情况，输出风险预测
   - 基于 project.md 现有 BR/PF 结构推断功能分组，主动建议 MoS 指标
5. 使用 `AskUserQuestion` 引导用户选择：
   - 本次迭代目标（1 句话）
   - 纳入的 PF（从待选列表中选择，附带工作量估算）
   - 迭代周期（起止日期，可选）
6. 生成 `iterations/current.md`（格式遵循 `knowledge/_schema/iteration-format.md`）
7. 更新 `.devpace/state.md`：反映新迭代信息

## Step 4：确认与输出

1. 展示新迭代规划摘要（目标 + PF 列表 + 周期 + 工作量估算）
2. 告知用户"迭代已规划，可以开始推进"
