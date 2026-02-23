# 回顾执行规程

> **职责**：迭代回顾的详细执行规则。/pace-retro 触发后，Claude 按需读取本文件。经验引用时机详见 `knowledge/experience-reference.md`。

## 数据收集详情

### CR 文件数据提取

从 `.devpace/backlog/` 所有 CR 文件提取：
- 各 CR 状态分布（merged / in-progress / pending）
- 质量检查一次通过率（首次检查即 `[x]` 的比例）
- 人类打回次数（事件表中 in_review → developing 的次数）
- 各 CR 从创建到 merged 的天数

从 `.devpace/project.md` 提取：
- 成效指标（MoS）达成情况（已勾选 / 总数）

从 `.devpace/iterations/current.md` 提取：
- 计划 vs 实际完成的产品功能数

### 测试基准线数据

读取 `.devpace/rules/test-baseline.md`（如存在，格式见 `knowledge/_schema/test-baseline-format.md`）：
- 提取"当前基准"的通过率和总执行时间
- 提取"历史趋势"表的趋势方向
- 用于回顾报告"质量"段的测试基准对比

文件不存在时静默跳过——不影响回顾报告的其他段落。

### 验证-审批一致率采集

从 `.devpace/backlog/` 中已 merged 的 CR 提取验证-审批一致率数据：

1. **数据提取**：对每个 merged CR：
   - 读取验证证据 section 的 accept 结果（通过/未通过）
   - 读取事件表中 Gate 3（in_review→approved）事件的存在性
2. **一致性判定**：
   - accept 通过 + Gate 3 通过 = **一致**
   - accept 通过 + Gate 3 打回（in_review→developing）= **不一致**
   - 无 accept 数据 = **跳过**（不计入统计）
3. **统计写入**：一致率 = 一致数 / (一致数 + 不一致数)，写入 `.devpace/metrics/dashboard.md` 验证-审批一致率行

### 基准线检测

读取 `.devpace/metrics/dashboard.md`，检查数据列是否全为 `—`（初始占位符）：
- **全为占位符（首次度量）**：本次数据即为基准线快照，报告中注明"首次度量，已建立基准"
- **有历史数据（非首次）**：对比本次与上次数据，计算趋势方向（↑ 上升 / ↓ 下降 / → 持平），在报告中展示趋势变化

## 回顾报告格式

```
## 迭代回顾：[迭代名称]

**交付**：计划 N 个产品功能，完成 M 个
**质量**：质量检查一次通过率 X%，打回率 Y%
**缺陷**：新增 N 个 defect（critical:A / major:B / minor:C），已修复 M 个，逃逸率 X%
**价值**：成效指标达成 A/B
**周期**：平均变更周期 Z 天，缺陷修复周期 W 天

**做得好的**：[从数据中识别正面趋势]
**需改进的**：[从数据中识别问题]
**缺陷分析**：[缺陷引入追溯 + 根因分类 + 预防建议]
**下个迭代建议**：[基于数据的改进建议]
```

## 经验沉淀规则

从本次回顾数据中提取可复用的 pattern：

1. 分析回顾中的正面趋势和问题，提炼为可复用的经验规律
2. 读取 `.devpace/metrics/insights.md`（如不存在则创建）
3. 将新 pattern 追加到 insights.md（不覆盖已有内容）
4. 如果已有 pattern 与本次数据吻合，在该 pattern 下追加验证记录

### Pattern 格式

```
### [日期] [pattern 标题]

**观察**：[从数据中观察到的现象]
**规律**：[提炼的可复用经验]
**证据**：[支持该规律的数据]
**建议**：[基于该规律的行动建议]
```

### 规则

- 每次回顾提炼 1-3 个 pattern（质量优先于数量）
- 已有 pattern 被本次数据再次验证时，追加"再次验证：[日期] [数据]"
- 已有 pattern 被本次数据否定时，标注"存疑：[日期] [反例数据]"

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

### MoS 进展评估

回顾报告中增加 MoS 进展段（闭合业务闭环）：

```
### 业务目标进展

**OBJ-1**：[目标名]
- MoS 达成：M/N
- 本迭代贡献：[已完成的 PF 对 MoS 的贡献描述]
- 风险：[未达成 MoS 的风险和建议]
```

数据来源：project.md MoS checkbox + 本迭代已完成 PF 的 BR→OBJ 追溯

## DORA 度量报告

当项目使用 Release 管理时（`.devpace/releases/` 存在且有 Release 文件），回顾报告增加 DORA 维度。

### 数据采集

从 `.devpace/releases/` 所有 Release 文件提取：
- closed Release 数量和时间（部署频率）
- Release 中各 CR 的 created→released 时间（变更前置时间）
- Release 关闭后产生 defect CR 的 Release 数（变更失败率）
- defect/hotfix CR 的 created→merged 时间（MTTR）

### DORA 报告格式

```
### DORA 度量

| 指标 | 值 | 趋势 | 行业参考 |
|------|---|------|---------|
| 部署频率 | N 次/[时段] | ↑/↓/→ | 按需/周/月 |
| 变更前置时间 | X 天 | ↑/↓/→ | < 1 天 (Elite) |
| 变更失败率 | Y% | ↑/↓/→ | < 15% (Elite) |
| MTTR | Z 天 | ↑/↓/→ | < 1 天 (Elite) |
```

### DORA 维度缺省处理

| 维度 | 无数据时 | 显示 |
|------|---------|------|
| 部署频率 | 无 Release | "未使用 Release 管理" |
| 变更前置时间 | 无 released CR | "无数据" |
| 变更失败率 | 无 closed Release | "无数据" |
| MTTR | 无 defect/hotfix CR | "无缺陷记录" |

有数据的维度正常展示，无数据维度标注原因，不影响其他维度。

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
- 根因分类遵循 ops-procedures.md 定义的引入原因分类
- 预防建议应具体可执行，不输出泛泛的"加强测试"

## Release Note 自动生成

当 PF 的所有 CR 均 merged 后（由 §11 merged 后自动管道触发），自动生成变更摘要。

### 生成条件

- 某 PF 在 project.md 中关联的所有 CR 状态均为 merged
- 该 PF 尚未生成过变更摘要（避免重复）

### 生成步骤

1. 从 project.md 读取该 PF 的描述和关联的 BR
2. 从各 CR 事件表中提取关键变更描述
3. 合成变更摘要

### 输出格式

追加到 `iterations/current.md` 的"变更摘要"section：

```
### [PF 标题]（[BR 标题]）

**变更内容**：
- [CR-1 标题]：[关键变更]
- [CR-2 标题]：[关键变更]

**影响范围**：[涉及的模块/目录]
```

### 规则

- **自动执行**：不需用户触发
- **追加模式**：不覆盖已有摘要
- **简洁性**：每个 CR 的变更描述不超过 1 行
