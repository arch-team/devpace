# 即时知识积累详细规程

> **职责**：pace-learn 的详细提取和积累规则。Steps 2-4 的处理逻辑。

## Step 2：提取 Pattern

1. 读取触发 CR 的完整事件表（含交接列）和质量检查记录
2. 读取事件表中 Gate 反思内容（`[gate1-reflection]`、`[gate2-reflection]` 标记，如有）——反思内容包含技术债、测试覆盖、边界场景等观察，是高质量 pattern 输入
3. 读取打回事件的交接列（结构化打回信息），了解人类关注点
4. 分析关键决策点和转折事件
5. 提炼 1 个可复用的经验规律

## Step 3：对比与积累

1. 读取 `.devpace/metrics/insights.md`
2. 检查是否已存在相似 pattern：
   - **已存在且吻合** → 验证次数 +1，置信度 +0.1（clamp 0.9），追加验证记录：`再次验证：[日期] [数据]`
   - **已存在但矛盾** → 标注存疑，置信度 -0.2（clamp 0.2）：`存疑：[日期] [反例数据]`
   - **不存在** → 追加新 pattern（置信度 0.5）

### Pattern 格式

格式遵循 `knowledge/_schema/insights-format.md`（含 4 种条目类型：模式/防御/改进/偏好、置信度规则、引用过滤规则）。

## Step 4：静默完成

- 不输出任何内容给用户（静默执行）
- 仅在 insights.md 写入变更时 git commit（消息：`chore(knowledge): extract pattern from CR-xxx`）
