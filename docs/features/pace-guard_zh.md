# 风险管理（`/pace-guard`）

devpace 风险管理提供统一的生命周期风险追踪：从编码前的 Pre-flight 扫描，到开发中的实时监控，再到跨迭代的趋势分析——让风险可见、可追踪、可解决。

## 前置条件

| 需求 | 用途 | 必要? |
|------|------|:-----:|
| `.devpace/` 已初始化 | 项目结构、CR 追踪 | 是 |
| `.devpace/risks/` 目录 | 风险文件存储（首次扫描时自动创建） | 自动 |

> **优雅降级**：无 `.devpace/` 时 `scan` 仍可用（基于代码库即时评估）。`trends`、`report`、`resolve` 需要历史数据，降级模式下不可用。

## 快速开始

```
1. /pace-guard scan              --> Pre-flight 5 维风险评估
2. /pace-guard monitor           --> 实时风险状态汇总
3. /pace-guard resolve RISK-001 mitigated  --> 更新风险状态
4. /pace-guard trends            --> 跨迭代趋势分析
5. /pace-guard report            --> 项目级风险仪表盘
```

日常工作流：L/XL CR 在意图检查点自动触发 `scan`。开发中用 `monitor` 跟踪风险状态。迭代边界用 `trends` 和 `report` 审视全局。

## 命令参考

### `scan`（默认，无参数）

Pre-flight 风险扫描，5 维评估：

| 维度 | 检查内容 | 数据源 |
|------|---------|--------|
| 历史教训 | 相似 CR 的失败/打回 pattern | insights.md（defense 类型，置信度 ≥ 0.5） |
| 依赖影响 | 改动文件的反向依赖链 | 代码文件 import/require 分析 |
| 架构兼容性 | 变更是否违反项目技术约定 | .devpace/context.md |
| 范围复杂度 | 实际工作量 vs 预期 | CR 描述 + 项目文件树 |
| 安全敏感度 | 涉及认证/授权/数据/加密 | 文件路径关键词分析 |

**复杂度自适应**：显式调用 `scan` 时按 CR 复杂度自动调整扫描深度——S 级仅扫描 2 个维度（历史教训+安全敏感度），M 级扫描 3 个维度，L/XL 执行完整 5 维扫描。使用 `scan --full` 可强制完整扫描。

**异常驱动输出**：默认只展示 Medium/High 维度。若全部为 Low，输出 1 行："5 维扫描均为 Low，风险可控。" 使用 `--detail` 查看完整矩阵。

### `monitor`

汇总当前 CR 的实时风险状态。

**分层输出**：
- **简要**（默认）：`CR-003 风险：0 新增 / 1 待处理(M) / 2 已缓解 — 风险可控`
- **标准**（`--detail` 或检测到 Medium/High 时自动升级）：完整表格格式
- **详细**：历史对比 + 缓解建议展开

### `trends`

跨 CR 趋势分析。

**默认**：3-5 行趋势摘要（方向指示 + 最关键模式）。`--detail` 或被 `/pace-retro` 消费时输出完整报告。

**风险老化**：open 超过 2 个迭代的风险自动标注老化警告，建议评估升级或 resolve。

### `report`

项目级风险仪表盘，展示所有 open 风险按严重度分组排列。

### `resolve`

更新风险状态：`resolve <RISK编号> <目标状态>`，目标状态为 `mitigated`、`accepted` 或 `resolved`。

**批量处理**：`resolve --batch <严重度>` 一次性处理同等级的多个风险。

**自动建议**：Gate 2 通过时建议 resolve 关联的 Low 风险。`/pace-plan close` 时建议 resolve 已完成 CR 的所有风险。

## 风险等级与响应

| 等级 | 标准模式 | 自主模式 |
|------|---------|---------|
| Low | 静默记录 | 静默记录 |
| Medium | 记录+提醒+方案建议 | 记录+自动缓解+报告 |
| High | **暂停，等待人类确认** | 提醒+方案+**等待人类确认** |

> **铁律**：High 风险不可绕过人类确认——与 Gate 3 审批不可绕过同级别。

## 自动触发

- L/XL CR 进入开发时自动触发 `scan`（意图检查点）
- 推进模式每个 checkpoint 执行轻量风险检测
- 脉搏检查发现风险积压时触发 `monitor`（open > 3 或有 High）

## 跨 Skill 集成

| 集成点 | 行为 |
|--------|------|
| `/pace-change` 风险评估 | 读取 `.devpace/risks/` 历史数据提升风险评分准确性 |
| `/pace-review` Gate 2 | review 摘要中添加风险状态行（有未解决 High 时高亮） |
| `/pace-plan close` | 关闭迭代时自动建议批量 resolve 已完成 CR 的风险 |
| `/pace-test impact` | 消费 scan 标记的高风险模块，优先安排测试 |

## 相关资源

- [风险文件格式](../../knowledge/_schema/auxiliary/risk-format.md)
- [风险度量指标](../../knowledge/metrics.md#风险管理指标)
- [脉搏风险信号](../../skills/pace-pulse/pulse-procedures-core.md)
