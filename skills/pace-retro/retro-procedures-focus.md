# focus 聚焦回顾规程

> **职责**：focus 子命令的完整流程。对指定维度进行深入分析，输出比完整回顾更详细的单维度报告。自包含，按 SKILL.md 路由表按需加载。

## §0 速查卡片

- **触发**：`/pace-retro focus <维度>`，维度为 quality | delivery | dora | defects | value | knowledge
- **数据源**：与完整回顾相同的 CR/project/iteration/dashboard 数据，但只采集指定维度
- **输出**：单维度深入分析报告（比完整回顾的对应段更详细）
- **不更新 dashboard.md**：轻量分析，不影响基准线
- **不执行经验沉淀**：Step 4 跳过
- **无效维度**：提示合法维度列表

## 触发

`/pace-retro focus <维度>`——维度参数必须为以下之一：

| 维度 | 含义 |
|------|------|
| `quality` | 质量保障（一次通过率、打回率、逃逸率、Gate 通过分布） |
| `delivery` | 交付效率（CR 周期、迭代速度、完成率、范围变更） |
| `dora` | DORA 代理度量（部署频率、前置时间、失败率、MTTR） |
| `defects` | 缺陷分析（严重度分布、根因分类、修复周期、引入追溯） |
| `value` | 业务价值（MoS 达成、价值链完整率、OBJ 进展） |
| `knowledge` | 知识库（pattern 分布、置信度、学习效能、冲突对） |

维度参数为空或无效时输出：`请指定分析维度：quality | delivery | dora | defects | value | knowledge`

## 流程

### Step 1：维度数据采集

根据指定维度，从对应数据源采集数据。各维度采集规则如下：

#### quality 维度

| 数据项 | 数据源 | 说明 |
|--------|--------|------|
| 质量检查一次通过率 | `.devpace/backlog/` CR 质量检查 checkbox | 首次即通过的 CR / 总 CR |
| 人类打回率 | CR 事件表 in_review→developing 次数 | 打回次数 / 总 review 次数 |
| 缺陷逃逸率 | backlog/ 中 type:defect CR vs 总 merged feature CR | merged 后发现缺陷的比例 |
| Gate 通过分布 | CR 事件表中各 Gate 的通过/失败记录 | Gate 1/2/3 各自的通过率 |
| 验证-审批一致率 | CR accept 结果 vs Gate 3 结果 | 一致率及不一致 case |
| 测试基准线 | `.devpace/rules/test-baseline.md`（如存在） | 通过率、耗时、趋势 |

#### delivery 维度

| 数据项 | 数据源 | 说明 |
|--------|--------|------|
| 平均 CR 周期 | CR 事件表 created→merged 时间戳 | 各 CR 天数 + 均值/中位数/最大/最小 |
| 迭代速度 | `iterations/current.md` 偏差快照 | 实际完成 PF 数 / 计划 PF 数 |
| PF 完成率 | `iterations/current.md` 产品功能表 | 已完成 / 总计 |
| 范围变更次数 | `iterations/current.md` 变更记录表 | 统计变更类型为"范围"的条目 |
| CR 状态分布 | `.devpace/backlog/` 所有 CR 状态 | merged / in-progress / pending 各数量 |
| 计划准确度 | iterations 偏差快照 | 1 - abs(实际 - 计划) / 计划 |

#### dora 维度

| 数据项 | 数据源 | 说明 |
|--------|--------|------|
| 部署频率 | `.devpace/releases/` closed Release 数量和时间 | 次数/时间段 |
| 变更前置时间 | Release 中各 CR 的 created→released 时间 | 天数均值 |
| 变更失败率 | Release 关闭后产生 defect CR 的 Release 数 | 有缺陷 Release / 总 Release |
| MTTR | defect/hotfix CR 的 created→merged 时间 | 天数均值 |

**前置条件**：`.devpace/releases/` 存在且有 Release 文件。不满足时输出："DORA 代理度量需要 Release 管理数据。请先通过 /pace-release 创建 Release。"

#### defects 维度

| 数据项 | 数据源 | 说明 |
|--------|--------|------|
| 严重度分布 | backlog/ 中 type:defect/hotfix CR 的严重度字段 | critical/major/minor/trivial 各数量 |
| 根因分类 | defect CR 的根因分析 section | 按引入原因分类统计 |
| 修复周期 | defect CR 事件表 created→merged 时间 | 均值/中位数/最大/最小 |
| 引入追溯 | defect CR 引入点字段 → 关联 feature CR | 可追溯比例 |
| Hotfix 比例 | type:hotfix CR / 总 defect+hotfix CR | 紧急修复频率 |
| 缺陷引入源 | 根因分析中引入模块/文件 | 高频引入源 Top-3 |

**前置条件**：存在 type:defect 或 type:hotfix 的 CR。不满足时输出："当前迭代无缺陷记录——这是正面信号。"

#### value 维度

| 数据项 | 数据源 | 说明 |
|--------|--------|------|
| MoS 达成率 | `.devpace/project.md` MoS checkbox | 已满足 / 总项 |
| MoS 变化量 | dashboard.md 上次 MoS 记录对比 | 新增达标项数 |
| OBJ 进展 | project.md OBJ + 关联 PF 完成状态 | 各 OBJ 的功能交付进度 |
| 价值链完整率 | project.md 价值功能树 | 有完整 BR→PF→CR 链路的占比 |
| PF→MoS 贡献 | 已完成 PF 对各 MoS 的贡献关系 | 功能-指标映射 |

#### knowledge 维度

| 数据项 | 数据源 | 说明 |
|--------|--------|------|
| Pattern 总数与分布 | `.devpace/metrics/insights.md` | 按类型/标签/状态统计 |
| 平均置信度 | insights.md 各类型 pattern 置信度 | 分类型均值 |
| 冲突对 | insights.md 冲突标注 | 未解决冲突列表 |
| 学习效能四指标 | CR 事件表 + insights.md 引用记录 | 命中率/准确率/采纳率/增长率 |
| 高产/高效标签 | insights.md 标签分布 | 条目多/高置信度+高引用 |

**前置条件**：`.devpace/metrics/insights.md` 存在且有 ≥3 条 pattern。不满足时输出："知识库数据不足（需至少 3 条 pattern），请先积累更多开发经验。"

### Step 2：深入分析

对采集数据进行深入分析，深度超过完整回顾中的对应段落。包含：

1. **统计分析**：均值、中位数、极值、标准差（数据量 ≥3 时）
2. **趋势对比**：从 dashboard.md "度量趋势"表读取历史值，标注连续方向
3. **异常检测**：识别偏离均值 >2 标准差的数据点，标注可能原因
4. **根因归因**：对问题指标尝试关联具体 CR 或事件，而非泛泛描述
5. **基准对比**：与 `knowledge/metrics.md` 定义的分级标准对比

### Step 3：生成深入报告

## 输出格式

```
## 聚焦回顾：[维度中文名]（[迭代名称]）

### 核心指标

| 指标 | 当前值 | 上次 | Delta | 趋势 | 分级 |
|------|--------|------|-------|------|------|
| [指标名] | [值] | [值] | [+/-变化] | ↑/↓/→/— | [Elite/High/Medium/Low] |

### 详细分析

[维度特有的深入分析内容——见下方各维度输出模板]

### 关联 CR 明细

| CR | 相关指标 | 贡献 | 备注 |
|----|---------|------|------|
| [CR 编号] | [指标名] | [正面/负面/中性] | [具体说明] |

### 改进建议

1. [基于数据的具体建议，含量化目标]
2. [基于根因归因的针对性建议]

→ 完整回顾：/pace-retro | 对比上迭代：/pace-retro compare
```

### 各维度输出模板

**quality**——详细分析段包含：
- Gate 1/2/3 各自通过率 + 失败 CR 列表
- 打回原因分类（从 CR 事件备注提取）
- 验证-审批不一致 case（一致率 <80% 时展开）
- 测试基准线趋势（如有）

**delivery**——详细分析段包含：
- CR 周期分布直方图（按天数分段）
- 周期最长/最短 CR 的原因分析
- 范围变更事件时间线
- 计划准确度与历史对比

**dora**——详细分析段包含：
- 四项 DORA 指标的分级评估（含代理值说明）
- 各指标的连续迭代趋势
- 与 DORA State of DevOps 基准的差距分析
- 瓶颈识别（哪项指标最弱）

**defects**——详细分析段包含：
- 根因分类详细统计 + 占比饼图描述
- 高频引入源 Top-3 + 对应 CR 列表
- 修复周期按严重度分组统计
- 缺陷密度（defect CR / 总 feature CR）

**value**——详细分析段包含：
- 各 OBJ 的 MoS 达成明细
- 未达标 MoS 的差距分析 + 阻碍因素
- PF→MoS 贡献图（哪些功能推动了哪些指标）
- 价值链断裂点（无 BR 或无 MoS 的孤立 PF）

**knowledge**——详细分析段包含：
- 各类型 pattern 数量和平均置信度
- 高效标签分析（高置信度 + 高引用频次）
- 冲突对列表 + 建议解决方向
- 学习效能四指标趋势 + 薄弱环节

## 规则

- **不更新 dashboard.md**：focus 是轻量分析工具，不改变基准线数据
- **不执行经验沉淀**：不提炼 pattern、不调用 pace-learn
- **不生成迭代传递清单**：不写入 iterations/current.md
- **不输出报告质量自评**：仅完整回顾模式需要
- **趋势数据依赖 dashboard.md**：如 dashboard.md 无历史数据，趋势列标注"— 首次"
- **数据不足时降级**：对应维度的部分指标无数据时，标注"无数据"继续输出其余指标
