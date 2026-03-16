# 需求变更通用规程

> **职责**：跨步骤共享规则。按 SKILL.md 路由表按需加载。

## §0 速查卡片

| 步骤 | 编号 | 文件 | 核心内容 |
|------|:----:|------|---------|
| 经验预加载 | 0 | common | insights.md pattern 匹配 |
| Triage 分流 | 1 | triage | Accept/Decline/Snooze 路由 |
| 影响分析 | 2 | impact | 四层追踪 + 三层分级输出 + 可视化 |
| 风险量化 | 3 | risk | 3 维评分 + 成本估算 |
| 调整方案 + 确认 | 4 | execution | 预览变更清单 + 用户确认 |
| 执行 + 记录 | 5 | execution | CR/功能树/迭代/state 更新 |
| 下游引导 + 外部同步 | 6 | execution | 按类型引导 + sync 提醒 |

- **类型细节**：各类型的分析逻辑和执行细节见 `change-procedures-types.md`
- **降级场景**：无 .devpace/ 时见 `change-procedures-degraded.md`

## Step 0：经验预加载

> OPT-14：将 experience-reference.md 时机 3 的规则落地到执行流程。

读取 `.devpace/metrics/insights.md`（不存在则静默跳过）：

1. 匹配当前变更类型（add/pause/resume/reprioritize/modify）与已有 pattern 的标签
2. **有同类变更 pattern** → 在 Step 2 影响分析报告中引用："历史上类似范围的变更平均影响 N 个模块"
3. **有变更回滚 pattern** → Step 3 风险量化中提升风险等级并引用原因
4. **有成功 pattern** → 在 Step 4 调整方案中采用推荐策略
5. 无匹配 → 静默跳过，不影响后续流程

## 上下文感知引导

> OPT-03：空参数时基于项目上下文智能推荐，替代静态选项列表。

当 $ARGUMENTS 为空时执行：

### 正常模式（.devpace/ 存在）

1. **扫描 paused CR**：遍历 `.devpace/backlog/` 中 paused 状态 CR → 有则推荐："恢复「[功能名]」？（已暂停 [N] 天）"
2. **扫描 Snooze 条目**：检查 CR 事件表和迭代变更记录中 Snooze 条目的触发条件 → 已满足则推荐："之前延后的「[描述]」条件已满足，现在评估？"
3. **评估迭代容量**：读取 iterations/current.md → 有余量则推荐 "插入新需求？（当前容量还有空间）"；已满则提示 "迭代容量已满，新增需求需要延后或调整现有优先级"
4. **检查频繁变更 PF**：统计 iterations/current.md 变更记录表中同一 PF 出现次数 → >2 次则提醒 "功能「[名称]」已变更 [N] 次，是否再次调整？"
5. **标准选项兜底**：上述推荐后附标准列表——"或选择：插入 / 暂停 / 恢复 / 调优先级 / 修改范围 / 批量变更"

### 降级模式（无 .devpace/）

无上下文数据，直接展示标准选项列表："你想做什么变更？（插入新需求 / 暂停某功能 / 恢复 / 调整优先级 / 修改范围）"

## paused 状态规则

paused 状态完整定义及操作规则见 `knowledge/_schema/entity/cr-format.md`。

## 变更后的功能树标记

```
⏸️ — 暂停       🔄 — 进行中     ✅ — 完成
⏳ — 待开始     🆕 MM-DD — 变更新增    ⏫ — 优先级提升
```
