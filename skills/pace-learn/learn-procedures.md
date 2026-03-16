# 即时知识积累详细规程

> **职责**：pace-learn 自动模式的详细提取和积累规则。

## §0 速查卡片

```
前置：.devpace/ 不存在 → 静默退出
提取源：事件表 + Gate 反思 + 打回交接 + 意图推断 + 风险记录 + diff stat + 变更记录
自适应：S→1 | M→1-2 | L/XL→最多 3 个 pattern
写入：统一写入——pace-learn 是 insights.md 唯一写入者（SSOT：此处 + rules §12.2）
衰减：180 天未引用 → -0.1/月至下限 0.2
生命周期：Active → Dormant → Archived
关系：自动=CR级学习 | 手动=知识库管理 | retro=迭代级→学习请求 | §12=只读消费 | §12.5=纠正→学习请求
```

## Step 1：前置检查

1. 检查 `.devpace/` 是否存在
   - **不存在** → 静默退出（不报错、不提示创建），结束流程
   - **存在** → 继续 Step 2
2. 检查 `.devpace/metrics/insights.md` 是否存在
   - **不存在** → 自动创建 `metrics/` 目录和 `insights.md` 文件（空模板）

## Step 2：提取 Pattern

### 数据源矩阵

从触发 CR 中收集以下维度的数据：

| 数据源 | 读取内容 | 提取价值 |
|--------|---------|---------|
| CR 事件表 | 状态转换记录、时间戳、交接列 | 流程模式、关键决策点 |
| Gate 反思 | `[gate1-reflection]`、`[gate2-reflection]` 标记内容 | 技术债、测试覆盖、边界场景观察 |
| 打回交接列 | 结构化打回信息 | 人类关注点、设计质量期望 |
| CR 意图推断准确度 | 意图 section 的溯源标记 vs 最终实现 | 推断校准——Claude 推断与实际结果的偏差 |
| 风险解决记录 | `.devpace/risks/` 中与该 CR 关联的风险文件 | 风险预测准确性、缓解措施有效性 |
| diff 统计 | `git diff --stat` 输出 | 复杂度校准——实际变更规模 vs 预估 |
| 变更管理记录 | iterations/current.md 变更记录表中与该 CR 相关的条目 | 变更模式、范围蔓延信号 |
| 挣扎信号 | 事件表中 gate1_fail/gate2_fail 次数、pulse-counter stuck 检测记录、自修复循环次数 | 环境缺陷定位——哪个 Skill/procedure/Schema 导致了困难 |

### 提取规则

1. 按数据源矩阵收集信息
2. 分析关键决策点和转折事件
3. **自适应提取**——根据 CR 复杂度（checkpoint 数量）调整提取深度：
   - S 复杂度（≤3 checkpoint）→ 提炼最多 1 个核心 pattern
   - M 复杂度（4-7 checkpoint）→ 提炼最多 2 个 pattern（1 个核心 + 1 个次要）
   - L/XL 复杂度（>7 checkpoint）→ 提炼最多 3 个 pattern（多维度提取）
4. 每个 pattern 必须有明确的证据支撑（不可凭感觉提炼）

### 挣扎信号提取（struggle 触发）

CR merged 时，如果满足以下任一条件，附加挣扎信号提取（与成功模式提取叠加执行）：
- Gate 1 自修复循环 ≥ 3 次（事件表中 gate1_fail 计数）
- 同一 CR 文件写入 ≥ 5 次且状态未变（事件表中 stuck-warning 或 pulse-counter 记录）
- Gate 2 对抗审查发现 ≥ 3 个问题（事件表备注）

**提取方向**（与其他触发源不同）：
- 不提取"代码怎么改"，提取"环境哪里不足"
- pattern 类型标记为 `harness-improvement`
- 描述格式：`[Skill/procedure/Schema 名称] 在 [场景] 下导致 [困难类型]，建议 [改进方向]`

示例：
```
标题：Gate 1 lint 修复循环过多
类型：harness-improvement
标签：[gate, lint, efficiency]
描述：dev-procedures-gate 未指导 Claude 在首次 lint 前执行 auto-fix 命令，导致连续 3 次自修复
建议：在 Gate 1 流程中增加"先执行 auto-fix 再跑 lint"的步骤
证据：CR-005 事件表 gate1_fail ×3，均为 lint 相关
```

**规则**：
- 延迟提取：仅在 CR merged 后回顾性提取，不在挣扎发生时干扰工作
- 最多 1 个 harness-improvement pattern/CR（聚焦最显著的环境缺陷）
- 与成功模式 pattern 独立计数（不占自适应提取的 1-3 个名额）

## Step 3：对比与积累（统一写入管道）

此步骤是 insights.md 的**唯一写入路径**。处理两类输入：
- pace-learn 自动提取的 pattern（Step 2 输出）
- 其他 Skill 的学习请求（pace-retro 回顾沉淀、§12.5 纠正即学习）

### 写入流程

1. 读取 `.devpace/metrics/insights.md`
2. 对每个待写入 pattern，执行去重检查：
   - **已存在且吻合** → 验证次数 +1，置信度 +0.1（clamp 0.9），追加验证记录：`再次验证：[日期] [数据]`
   - **已存在但矛盾** → 生成"冲突对"标记（见 §3.2），置信度 -0.2（clamp 0.2）：`存疑：[日期] [反例数据]`
   - **不存在** → 追加新 pattern（置信度 0.5，偏好类型初始 0.7）
3. 格式遵循 `knowledge/_schema/entity/insights-format.md`（含生命周期状态和上下文置信度）
4. 写入后 git commit

### §3.2 冲突对标记

当新 pattern 与已有 pattern 矛盾时：
1. 在两条 pattern 中互相标记冲突对：`- **冲突对**：[对方 pattern 标题]`
2. 矛盾方置信度 -0.2
3. 冲突对信息在 §12 引用时附注，供用户裁决
4. `/pace-retro` 输出时列出未解决的冲突对

### §3.3 学习请求协议

其他 Skill 通过以下格式提交学习请求（概念协议，非独立文件）：

```
请求来源：[Skill 名称]
事件类型：[retro-observation | correction | flaky-test | manual-note]
建议类型：[模式 | 防御 | 改进 | 偏好]
建议标签：[标签列表]
描述：[经验总结]
证据：[支持数据]
```

pace-learn 对学习请求执行与自提取 pattern 完全相同的 §3.1 写入流程。

## Step 4：嵌入式反馈

- 有新 pattern → 在 §11 管道输出末尾追加：`（经验 +N：[pattern 标题简写]）`
- 仅验证 → `（经验验证：[pattern 标题] 置信度 → X.X）`
- 无发现 → 静默
- git commit（消息：`chore(knowledge): extract pattern from CR-xxx`）

## 置信度衰减规则

长期未引用的 pattern 自动降低置信度，维护知识库健康：

| 条件 | 衰减 | 说明 |
|------|------|------|
| 180 天未被 §12 引用 | -0.1/月 | 从第 181 天起每月衰减 |
| 衰减下限 | 0.2 | 不低于 0.2（保留但不主动引用） |
| 重新引用 | 停止衰减 | 更新"最近引用"日期后衰减重置 |
| 归档条件 | 置信度 0.2 + 超 1 年未引用 + 验证次数 = 0 | 建议归档（移至 Archived section） |

衰减在 pace-learn 每次写入 insights.md 时顺便检查和更新。

## 纠正即学习交互优化

纠正行为按严重度分级处理（减少轻微纠正的打断感）：

| 纠正类型 | 示例 | 交互模式 |
|---------|------|---------|
| **轻微纠正** | PF 名称修改、风险等级微调 | 会话结束时批量确认——"本次有 N 个偏好变化，记住？[列表]" |
| **重大纠正** | 否决 Gate 2、否决简化审批、打回 CR | 保持即时提问——"记住这个偏好？" |

### 溯源标记缺失后备

当 `source: claude` 溯源标记缺失（如早期 CR 或手动创建的 CR）时，使用 diff 比对作为后备检测：
- `git diff` 检测 Claude 生成内容被用户修改的区域
- 识别为潜在纠正行为后，仍遵循上述分级交互
