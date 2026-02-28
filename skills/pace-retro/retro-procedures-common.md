# 回顾通用规程

> **职责**：完整回顾、update、focus 三条路径的共享规则。/pace-retro 触发后，由 SKILL.md 路由表按需加载本文件。

## §0 速查卡片

- **本文件覆盖**：Agent 记忆利用 · 数据收集详情（CR 提取 + 测试基准线 + 验证-审批一致率采集 + 基准线检测）· 一致率的报告输出格式见 `retro-procedures.md` 分区 B
- **路由索引**：完整回顾详细规则 → `retro-procedures.md` · update 反馈规则 → `retro-procedures-update.md` · focus 深入分析 → `retro-procedures-focus.md`
- **自包含子命令**（不加载本文件）：compare · history · mid · accept
- **趋势相关规则分布**：趋势标签判定 → `retro-procedures-update.md` · Delta 改善/恶化判定 → `retro-procedures-compare.md` · 稳定性+拐点分析 → `retro-procedures-history.md`

## Agent 记忆利用规范

pace-analyst Agent 配置了 `memory: project`（项目级持久化记忆）。以下规范确保记忆被有效利用：

### 回顾开始时（读取记忆）

1. 读取 Agent 记忆中的"上次回顾关键发现"——快速定位上次主要问题
2. 读取"累计趋势方向"——了解哪些指标在持续改善/恶化
3. 读取"分析模型"——如"本项目缺陷主要来自集成问题"等项目特征
4. 基于记忆信息，优先检查上次识别的问题是否改善

### 回顾结束时（保存记忆）

1. 保存"本次回顾关键发现"：最多 3 条（格式：`[维度]: [发现]`）
2. 保存"累计趋势方向"：各核心指标的连续趋势（如"一次通过率：连续 3 迭代 ↑"）
3. 保存"分析模型"：项目级别的缺陷模式、质量特征等
4. 清理过时记忆：超过 5 个迭代未更新的记忆条目可删除

### 记忆格式

```
## 上次回顾关键发现（[迭代名]）
1. [维度]: [发现]
2. [维度]: [发现]

## 累计趋势方向
| 指标 | 方向 | 连续迭代数 |
|------|------|-----------|

## 分析模型
- [项目特征观察]
```

## 数据收集详情

### CR 文件数据提取

从 `.devpace/backlog/` 所有 CR 文件提取：
- 各 CR 状态分布（merged / in-progress / pending）
- 质量检查一次通过率（首次检查即 `[x]` 的比例）
- 人类打回次数（事件表中 in_review → developing 的次数）
- 各 CR 从创建到 merged 的天数

从 `.devpace/project.md` 提取：
- 成效指标（MoS）达成情况（已勾选 / 总数）
- MoS 变化量：对比 dashboard.md 上次 MoS 记录（如有），计算新增达标项数

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
