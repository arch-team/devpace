# 回顾维度分析与知识管理规程

> **职责**：完整回顾的条件分析段（分区 B）和知识管理规程（分区 C）。由 `retro-procedures.md` 路由加载。共享规则见 `retro-procedures-common.md`。

## §0 速查卡片

- **分区 B**：条件分析段——按数据可用性渐进暴露（风险趋势 · 技术债务 · 缺陷分析 · MoS · DORA · 缺陷根因 · 验证-审批差异）
- **分区 C**：知识管理——经验沉淀 · 学习透明 · retro↔learn · 知识库元分析 · 学习效能

---

<!-- 分区 B：条件分析段 -->

以下条件段按数据可用性渐进暴露——数据不足时静默跳过，不输出空段。

| 条件段 | 出现条件 | 数据源 |
|--------|---------|--------|
| 风险趋势 | `.devpace/risks/` 存在 | 风险文件 + insights.md defense |
| 技术债务趋势 | 存在 type:tech-debt CR | backlog/ tech-debt CR + project.md 预算配置 |
| 缺陷分析 | 存在 type:defect/hotfix CR | backlog/ defect CR |
| MoS 进展评估 | project.md 有 MoS | project.md + dashboard.md |
| DORA 代理度量 | `.devpace/releases/` 存在 | Release 文件 |
| 缺陷根因报告 | 已分析的 defect CR | defect CR 根因字段 |
| 验证-审批差异 | 一致率 < 80% | backlog/ accept 结果（采集见 common） |
| 知识驱动改进 | insights.md 有 defense pattern | insights.md |
| 知识库健康度 | insights.md 有 ≥5 pattern | insights.md |
| 学习效能 | 有 pattern 引用数据 | CR 事件表 + insights.md |

新增条件段时：在此表注册 → 在下方对应分区添加段定义（含出现条件、数据采集、输出格式、持久化规则）。

## 风险趋势（`.devpace/risks/` 存在时）

数据采集：
1. `.devpace/risks/` 所有风险文件（来源、严重度、状态、关联 CR）
2. `insights.md` 中 defense 类型条目（置信度、引用次数）
3. `.devpace/iterations/` 历史迭代文件（关联 CR 列表，用于按迭代分组）

输出格式（追加到回顾报告中）：

```
## 风险趋势

### 跨迭代模式（最近 3 迭代）
| 风险类型 | {{Iter-N-2}} | {{Iter-N-1}} | {{Iter-N}} | 趋势 |
|---------|------------|------------|----------|------|

### 重复 Pattern Top 3
1. "{{pattern 描述}}" → 建议：{{行动}}

### 风险登记簿状态
- Open: {{N}}（High: {{H}}, Medium: {{M}}, Low: {{L}}）
- 本迭代解决: {{R}}
```

趋势判定规则：
- 连续 2 迭代同类型风险**增加** = ↑ 恶化
- 连续 2 迭代同类型风险**减少** = ↓ 改善
- 其他 = → 稳定

条件渐进暴露：`.devpace/risks/` 目录不存在时，整个风险趋势段**静默跳过**（不输出任何内容）。

---

## 技术债务趋势（存在 type:tech-debt CR 时）

数据采集：
1. `.devpace/backlog/` 中 type 为 `tech-debt` 的 CR 文件
2. `dashboard.md` 历史快照中 tech-debt CR 数量
3. `project.md` 配置中 `tech-debt-budget` 值（默认 20%）

输出格式（追加到回顾报告中）：

```
## 技术债务趋势

- 当前 tech-debt CR：{{N}} 个（完成 {{done}} · 进行中 {{wip}} · 待做 {{todo}}）
- 债务预算使用率：{{actual}}% / {{budget}}%（{{over/under}} 预算）
- 趋势：{{上升/下降/稳定}}（对比上迭代 {{prev}} 个）
```

趋势判定：
- 当前 > 上迭代 × 1.2 = 上升（债务积累）
- 当前 < 上迭代 × 0.8 = 下降（债务偿还有效）
- 其他 = 稳定

持久化规则：
- tech-debt CR 数量和预算使用率写入 `dashboard.md` 历史快照
- 连续 3 迭代超预算 → 在改进建议中追加"建议提高 tech-debt-budget 或加速偿还"

条件渐进暴露：无 tech-debt 类型 CR 时，整个技术债务趋势段**静默跳过**。

---

<!-- 分区 C：知识管理 -->

## 经验沉淀规则

从本次回顾数据中提取可复用的 pattern，**通过 pace-learn 统一写入管道处理**（不直接写入 insights.md）。

### 提取流程

1. 分析回顾中的正面趋势和问题，提炼为可复用的经验规律
2. 每个 pattern 按 `knowledge/_schema/auxiliary/insights-format.md` 标准格式构造：
   - 类型：改进（improvement）——回顾产出的 pattern 默认为改进类型
   - 来源：`retro 迭代回顾 [迭代名称]`
   - 标签：从回顾数据自动推断
   - 描述：1-2 句经验总结
   - 置信度：初始 0.5（首次提取），后续验证递增
3. 构造"学习请求"交给 pace-learn 统一处理：
   ```
   请求来源：pace-retro
   事件类型：retro-observation
   建议类型：改进
   建议标签：[从回顾数据推断]
   描述：[经验总结]
   证据：[回顾数据支撑]
   ```
4. pace-learn 的 Step 3 统一写入管道执行去重、置信度更新、冲突检测

### 规则

- 每次回顾提炼 1-3 个 pattern（质量优先于数量）
- 与 pace-learn 自动提取的 pattern 使用完全相同的格式和写入路径
- 回顾产出的改进 pattern 在后续迭代中如果被 CR 级数据验证，自动升级置信度

## 本次学习透明段

经验沉淀（Step 4）完成后，在回顾报告末尾输出透明段，让用户了解"这次回顾学到了什么"：

```
### 本次回顾经验提取

**提交给知识库的 pattern**：
1. 🆕 [类型] "[描述]"（置信度 X.X，待验证）
2. ✅ [验证] "[描述]"（置信度 X.X→Y.Y，+N 次验证）
3. ⚡ [冲突] "[描述]"——与已有 pattern #N 存在张力

处理状态：已提交 pace-learn 管道（去重检查 + 写入）
```

**规则**：
- 🆕 = 首次提取的新 pattern
- ✅ = 验证了已有 pattern（置信度变化）
- ⚡ = 与已有 pattern 冲突（需关注）
- ⏭️ = 被 pace-learn 去重跳过（已有高度相似的 pattern）
- 无 pattern 提取时输出"本迭代无新经验提取（已有 pattern 未被新数据触发）"

## retro↔learn 双向整合

迭代级回顾（retro）与 CR 级学习（learn）双向流动，形成知识闭环。

### retro→learn：回顾时批量验证

回顾报告生成过程中，对 `.devpace/metrics/insights.md` 中本迭代被引用的 pattern 进行批量验证：

1. 读取本迭代所有 merged CR 的事件表
2. 匹配 insights.md 中被 §12 引用的 pattern
3. 对每个匹配的 pattern：
   - CR 结果与 pattern 预测一致 → 验证次数 +1，置信度 +0.1
   - CR 结果与 pattern 预测矛盾 → 标注存疑，置信度 -0.2
4. 通过 pace-learn 统一写入管道处理更新

### learn→retro：defense 汇总改进方向

回顾报告中增加"知识驱动改进"段，从 insights.md 的 defense 类型 pattern 汇总宏观改进方向：

```
### 知识驱动改进

**本迭代触发的 defense pattern**：
1. [pattern 标题]（置信度 X.X，触发 N 次）→ 建议：[预防措施]
2. ...

**高频 defense 趋势**：[跨迭代重复出现的 defense pattern 归纳]
**改进方向建议**：[基于 defense 分析的系统性改进]
```

条件渐进暴露：insights.md 不存在或无 defense pattern 时，此段静默跳过。

## 知识库元分析

/pace-retro 回顾报告中增加"知识库健康度"段——对知识本身的知识（meta-learning）。

### 生成条件

`.devpace/metrics/insights.md` 存在且有 ≥5 条 pattern 时生成。不满足时静默跳过。

### 报告格式

```
### 知识库健康度

**概览**：共 N 条 pattern（Active: A | Dormant: D | Archived: R）
**类型平均置信度**：模式 X.X · 防御 X.X · 改进 X.X · 偏好 X.X
**高产标签 Top-3**：[标签1](N条) · [标签2](M条) · [标签3](K条)
**高效标签**（高置信度+高引用）：[标签列表]
**冲突对**：N 组未解决（[pattern A] ⚡ [pattern B]，...）
**进化方向**：
- 增长区（近 3 迭代新增最多）：[类型/标签]
- 衰退区（近 3 迭代衰减最多）：[类型/标签]
- 建议：[基于趋势的知识管理建议]
```

### 数据采集

1. 读取 insights.md 全部条目
2. 按类型、标签、置信度、状态分组统计
3. 对比 dashboard.md 上次知识库数据（如有），计算趋势
4. 识别冲突对列表
5. 分析标签分布，识别高产（条目多）和高效（高置信度+高引用）标签

### 元分析数据持久化

报告生成后，将知识库健康度关键指标写入 `dashboard.md` 的"知识库"section：

```
## 知识库（最后更新：[日期]）

| 维度 | 值 |
|------|---|
| 总条目 | [N] |
| Active/Dormant/Archived | [A]/[D]/[R] |
| 平均置信度 | [X.X] |
| 未解决冲突对 | [N] |
```

## 学习效能度量

回顾报告增加"学习效能"段——度量知识层本身的效能。

### 指标定义

| 指标 | 计算方式 | 含义 |
|------|---------|------|
| Pattern 引用命中率 | 被 §12 引用的 pattern 中，CR 结果与 pattern 一致的比例 | 经验的预测准确性 |
| Defense 预测准确率 | defense pattern 预警的风险中实际发生的比例 | 防御经验的有效性 |
| 偏好采纳率 | 偏好 pattern 引用后 Claude 行为调整正确的比例 | 用户偏好的学习质量 |
| 知识库增长率 | 本迭代新增 Active pattern 数 / 总 merged CR 数 | 知识提取效率 |

### 报告格式

```
### 学习效能

| 指标 | 值 | 趋势 |
|------|---|------|
| Pattern 引用命中率 | X% | ↑/↓/→/— |
| Defense 预测准确率 | Y% | ↑/↓/→/— |
| 偏好采纳率 | Z% | ↑/↓/→/— |
| 知识库增长率 | W 条/迭代 | ↑/↓/→/— |
```

### 采集规则

- 引用命中率：从本迭代 CR 事件表中匹配 §12 引用记录，对比 CR 最终结果
- Defense 准确率：从本迭代匹配 defense 类型 pattern 引用，检查预警风险是否实际触发
- 偏好采纳率：从本迭代匹配偏好类型 pattern 引用，检查 Claude 后续行为是否符合偏好
- 增长率：本迭代新建 pattern 数（insights.md 日期在迭代时间范围内）/ 本迭代 merged CR 数
- 无数据的指标标注"无数据"，不影响其他指标

---

<!-- 分区 B 续：缺陷与度量分析 -->

## 缺陷分析维度

当迭代中存在 type:defect 或 type:hotfix 的 CR 时，额外输出缺陷分析。

### 数据采集

从 `.devpace/backlog/` 中筛选 type:defect 和 type:hotfix 的 CR：
- 各严重度分布（critical/major/minor/trivial）
- 各 CR 的根因分析 section（如有）
- 缺陷引入追溯：引入点字段关联的 feature CR
- 修复周期：从创建到 merged 的天数

### 缺陷分析报告

```
### 缺陷分析

**分布**：critical N / major M / minor K / trivial L
**修复周期**：平均 X 天（最快 Y 天，最慢 Z 天）
**引入追溯**：
- [defect CR 标题] ← [引入 CR 标题]（[引入原因分类]）
- ...
**根因分类**：
- 逻辑错误：N 个
- 边界条件遗漏：M 个
- 集成问题：K 个
- 其他：L 个
**预防建议**：[基于根因分类的针对性建议]
```

### 引入原因分类

| 分类 | 说明 |
|------|------|
| 逻辑错误 | 算法或条件判断错误 |
| 边界条件遗漏 | 未处理空值、极值、特殊输入 |
| 集成问题 | 模块间接口不匹配、版本兼容 |
| 回归 | 修改 A 导致 B 功能异常 |
| 配置错误 | 环境配置、参数设置不当 |
| 未知 | 根因尚未确定 |

**自定义分类扩展**：当 `project.md` 或 `insights.md` 中定义了项目特定的缺陷分类（如 CSS 布局、API 兼容性、数据质量等），优先使用项目分类。当"未知"占比 > 30% 时，在报告中建议用户细化分类体系。

### MoS 进展评估

回顾报告中增加 MoS 进展段（闭合业务闭环）：

```
### 业务目标进展

**OBJ-1**：[目标名]
- MoS 达成：M/N（上次回顾 X/N → 本次 M/N，变化 +Y 项达标）
- 本迭代贡献：[已完成的 PF 对 MoS 的贡献描述]
- 风险：[未达成 MoS 的风险和建议]
```

数据来源：project.md MoS checkbox + 本迭代已完成 PF 的 BR→OBJ 追溯

### MoS 量化进度更新

对 project.md 中的连续性 MoS 指标（含数值目标，如"响应时间 < 200ms"、"Gate 一次通过率 > 80%"），尝试从 dashboard.md 匹配对应度量值并计算进度：

**匹配规则**：
- MoS 文本包含 dashboard.md 已有指标的关键词（如"一次通过率"↔ dashboard "Gate 1 一次通过率"）
- 匹配成功 → 提取当前值，计算进度百分比 = 当前值 / 目标值 × 100%
- 匹配失败 → 跳过（不是所有 MoS 都能自动匹配）

**输出**：在行动摘要的"待确认操作"中前置 MoS 更新建议：
```
📌 **待确认操作**（N 项）：
- MoS 达标更新：M 个指标建议勾选（`/pace-retro accept` 一键确认）
  · "Gate 一次通过率 > 80%"→ 当前 95%，已达标
  · "平均 CR 周期 < 2 天"→ 当前 1.5 天，已达标
```

**规则**：
- 仅建议，不自动修改 project.md（人类拥有业务数据，对齐 P3 原则）
- 用户可通过 `/pace-retro accept` 一键确认所有建议操作
- 无 dashboard.md 或全为占位符时静默跳过

## DORA 代理度量报告

当项目使用 Release 管理时（`.devpace/releases/` 存在且有 Release 文件），回顾报告增加 DORA 维度。

> ⚠️ 以下均为**代理值**——基于 .devpace/ 数据计算，反映开发阶段交付节奏，不等同于生产级 DORA。详见 `knowledge/metrics.md` DORA 代理度量章节。

### 数据采集

从 `.devpace/releases/` 所有 Release 文件提取：
- closed Release 数量和时间（部署频率）
- Release 中各 CR 的 created→released 时间（变更前置时间）
- Release 关闭后产生 defect CR 的 Release 数（变更失败率）
- defect/hotfix CR 的 created→merged 时间（MTTR）

### 趋势对比逻辑

1. 读取 `dashboard.md` 中上次 DORA 报告的值（如存在）
2. 逐指标对比当前值与上次值：
   - 部署频率、变更前置时间、MTTR：当前值更小/更快 = ↑（趋好），更大/更慢 = ↓（趋差）
   - 变更失败率：当前值更低 = ↑（趋好），更高 = ↓（趋差）
   - 变化幅度 <10% = →（持平）
3. 无历史数据 = —（首次）

### 基准分级逻辑

按 `knowledge/metrics.md` "DORA 代理度量"章节的"基准分级映射表"，将每个指标的代理值映射为 Elite/High/Medium/Low。阈值的权威定义在 metrics.md——修改阈值时只需改该文件一处。

### DORA 报告格式

```
### DORA 代理度量

> ⚠️ 代理值：基于 .devpace/ 数据，反映开发阶段交付节奏，非生产级 DORA。

| 指标 | 代理值 | 分级 | 趋势 | 备注 |
|------|-------|------|------|------|
| 部署频率 | N 次/周 | Elite/High/Medium/Low | ↑/↓/→/— | 基于 Release 关闭频率 |
| 变更前置时间 | X 天 | Elite/High/Medium/Low | ↑/↓/→/— | CR created→released 均值 |
| 变更失败率 | Y% | Elite/High/Medium/Low | ↑/↓/→/— | 有缺陷 Release / 总 Release |
| MTTR | Z 天 | Elite/High/Medium/Low | ↑/↓/→/— | defect CR created→merged 均值 |
```

### DORA 维度缺省处理

| 维度 | 无数据时 | 显示 |
|------|---------|------|
| 部署频率 | 无 Release | "未使用 Release 管理"（不分级） |
| 变更前置时间 | 无 released CR | "无数据"（不分级） |
| 变更失败率 | 无 closed Release | "无数据"（不分级） |
| MTTR | 无 defect/hotfix CR | "无缺陷记录 ✅"（视为正面信号） |

有数据的维度正常展示（含分级和趋势），无数据维度标注原因，不影响其他维度。

### DORA 数据持久化

报告生成后，将当前 DORA 代理值写入 `dashboard.md` 的 DORA section（覆盖上次值），作为下次趋势对比的基线。格式：

```
## DORA 代理度量（最后更新：[日期]）

| 指标 | 代理值 | 分级 |
|------|-------|------|
| 部署频率 | [值] | [分级] |
| 变更前置时间 | [值] | [分级] |
| 变更失败率 | [值] | [分级] |
| MTTR | [值] | [分级] |
```

## 缺陷根因报告

当存在已修复（merged）的 defect CR 且根因分析已填充时，生成缺陷根因报告。

### 报告格式

```
### 缺陷根因分析总结

**已分析缺陷**：N 个（共 M 个 defect CR）

**根因分布**：
- 逻辑错误：A 个 (X%)
- 边界条件遗漏：B 个 (Y%)
- 集成问题：C 个 (Z%)
- 其他：D 个

**高频引入源**：
- [模块/文件]：N 次缺陷引入

**系统性预防建议**：
1. [基于根因分布的具体建议]
2. [基于高频引入源的具体建议]
```

### 规则

- 仅当有已分析的 defect CR（根因字段非"待调查"）时生成
- 根因分类遵循上方定义的引入原因分类（6 种基础 + 项目自定义）
- 预防建议应具体可执行，不输出泛泛的"加强测试"

## 验证-审批差异分析（一致率 < 80% 时）

当验证-审批一致率 < 80% 时（采集规则见 `retro-procedures-common.md`），在回顾报告中额外输出不一致 case 分析：

```
### 验证-审批差异分析

**一致率**：X%（低于 80% 阈值）

**不一致 case**：
| CR | accept 结果 | Gate 3 结果 | 差异原因 |
|----|------------|------------|---------|
| [CR 编号] | 通过 | 打回 | [从打回事件的备注推断原因] |

**改进建议**：
- [基于差异模式的具体建议，反馈给 pace-test 验收策略]
```

不一致的 case 同时作为 pace-learn 的输入——学习"哪些场景下 AI 验证容易误判"。
