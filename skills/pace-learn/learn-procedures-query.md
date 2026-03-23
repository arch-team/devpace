# 知识库查询与管理规程

> **职责**：pace-learn 手动模式的子命令执行规则。用户通过 `/pace-learn [子命令]` 调用。

## §0 速查卡片

```
note：手动沉淀经验 | list：筛选查看 | stats：统计概览 | export：导出复用 | prune：清理/衰减
前置：.devpace/metrics/insights.md 存在（不存在提示 /pace-init）
衰减：180 天未引用 → -0.1/月至下限 0.2 | prune --decay-only 仅执行衰减
```

## §1 note — 手动知识沉淀

**用途**：在探索模式或非 CR 场景中，用户主动沉淀有价值的经验。

**输入**：`/pace-learn note <描述>`

**流程**：
1. 解析用户描述，推断 pattern 类型（模式/防御/改进）和标签
2. 构造 pattern 条目（置信度初始 0.5，来源标记"手动沉淀"）
3. 通过 `learn-procedures.md` Step 3 统一写入管道处理（去重、冲突检测）
4. 输出确认：`已记录：[pattern 标题]（置信度 0.5，标签：[标签]）`

**示例**：
```
用户：/pace-learn note 大型重构前先建立测试基准线可以显著降低回归风险
输出：已记录：重构前建立测试基准线（置信度 0.5，标签：重构、测试、质量）
```

## §2 list — 知识库查询

**用途**：按条件筛选和查看 pattern。

**输入**：`/pace-learn list [--type TYPE] [--tag TAG] [--confidence MIN]`

**流程**：
1. 读取 `.devpace/metrics/insights.md`
2. 按参数过滤：
   - `--type`：模式/防御/改进/偏好
   - `--tag`：标签匹配（支持多标签 AND）
   - `--confidence`：最低置信度（默认 0，显示全部）
3. 按置信度降序排列输出

**输出格式**：
```
知识库（共 N 条，筛选 M 条）：

| # | 标题 | 类型 | 置信度 | 验证 | 最近引用 | 状态 |
|---|------|------|--------|------|---------|------|
| 1 | [标题] | 模式 | 0.8 | 5次 | 2026-02-20 | Active |
| 2 | [标题] | 防御 | 0.5 | 2次 | （未引用） | Active |
```

**无参数时**：显示 Active 状态的全部条目（不含 Archived）。

## §3 stats — 知识库统计

**用途**：概览知识库健康状况。

**输入**：`/pace-learn stats`

**流程**：
1. 读取 insights.md，统计各维度数据
2. 计算健康度指标

**输出格式**：
```
知识库统计：

总条目：N（Active: A | Dormant: D | Archived: R）
类型分布：模式 X · 防御 Y · 改进 Z · 偏好 W
置信度分布：高(>0.7) N · 中(0.4-0.7) M · 低(<0.4) K
Top-5 高引用：[pattern 列表]
未引用条目：N 条（建议关注）
冲突对：N 组未解决
衰减预警：N 条将在 30 天内进入 Dormant
```

## §4 export — 导出经验

**用途**：导出可复用经验供其他项目导入。

**输入**：`/pace-learn export [--path FILE]`

**流程**：
1. 过滤条件：置信度 ≥ 0.7 且类型 ≠ 偏好（偏好是项目特定的）
2. 按 `knowledge/_schema/auxiliary/insights-format.md` 导出格式生成文件
3. 默认导出到 `./insights-export.md`

**渐进教学触发**：当 insights.md 积累超过 5 条高置信度（≥0.7）pattern 时，在 merged 后管道输出中触发一次性提示：
`（知识库已积累 N 条高质量经验，可用 /pace-learn export 导出到其他项目复用。）`
教学标记：`learn_export`（taught 去重）

**输出**：
```
已导出 N 条经验到 [路径]
过滤规则：置信度 ≥ 0.7，排除偏好类型
```

## §5 prune — 知识库清理与衰减

**用途**：清理低置信度/过期条目，或独立执行置信度衰减（解除衰减冻结）。

**输入**：`/pace-learn prune [--dry-run] [--decay-only]`

### 衰减专用模式（`--decay-only`）

由 pace-pulse GC 检测后委托调用，也可用户手动触发。

**流程**：
1. 读取 `.devpace/metrics/insights.md`（不存在 → 提示 `/pace-init`）
2. 对所有 Active 条目检查"最近引用"日期：
   - 超 180 天未引用 → 从第 181 天起按月计算累计衰减值（-0.1/月），更新置信度（clamp 0.2）
   - 衰减后置信度 < 0.4 或超 180 天未引用 → 状态标记为 Dormant
3. 有状态变更（Active → Dormant）→ 输出 `衰减完成：N 条 Active → Dormant`
4. 无变更 → 静默
5. git commit（仅在有变更时，消息：`chore(knowledge): decay confidence scores`）

### 完整清理模式（默认）

**流程**：
1. 读取 `.devpace/metrics/insights.md`（不存在 → 提示 `/pace-init`）
2. 先执行衰减扫描（同 `--decay-only` 步骤 2）
3. 识别清理候选（满足任一条件即为候选）：
   - 状态为 Archived
   - 状态为 Dormant + 置信度 = 0.2 + 验证次数 = 0
   - 状态为 Active + 置信度 ≤ 0.3 + 超 360 天未引用
4. `--dry-run` → 仅列出候选，不修改文件
5. 默认 → 列出候选 + 等待用户确认
6. 用户确认后执行：Archived 条目从文件删除；其他候选移至 `## Archived` section
7. git commit（消息：`chore(knowledge): prune insights`）

**输出格式**（完整清理）：
```
知识库清理：待处理 N 条（Archived: A / Dormant: D / 低置信 Active: E）

| # | 标题 | 类型 | 置信度 | 验证 | 最近引用 | 原因 |
|---|------|------|--------|------|---------|------|
| 1 | [标题] | 模式 | 0.2 | 0次 | 2025-01-15 | Archived |
| 2 | [标题] | 防御 | 0.2 | 0次 | 2025-06-01 | Dormant+零验证 |

确认清理？（输入"确认"执行，"取消"放弃）
```

**规则**：
- 衰减公式与 `insights-format.md` §置信度衰减 和 `learn-procedures.md` §置信度衰减规则保持一致
- 清理操作不可撤销（Archived 删除后无法恢复），因此必须等待用户确认
- `--decay-only` 模式无需用户确认（衰减是可预期的自动行为）
