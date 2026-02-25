---
description: Use when user wants to assess risks before development, check current risk status, analyze risk trends, or says "风险/预检/预分析/guard/risk/隐患/安全检查". Also auto-invoked during advance mode intent checkpoint for L/XL CRs. NOT for /pace-dev (implementation), NOT for /pace-review (quality gate), NOT for /pace-test (testing).
allowed-tools: Read, Glob, Grep, Write, Edit
argument-hint: "[scan|monitor|trends|report|resolve] [CR编号]"
---

# /pace-guard — 风险预判与管理

统一管理开发全生命周期的风险：从编码前的 Pre-flight 扫描，到开发中的实时监控，再到跨迭代的趋势分析——让风险可见、可追踪、可解决。

## 子命令

| 子命令 | 用途 | 输入 | 自动触发 |
|--------|------|------|---------|
| `scan` | Pre-flight 风险扫描 | CR 编号或当前 CR | L/XL 意图检查点 |
| `monitor` | 实时风险汇总 | 当前 CR | pace-pulse 第 8 信号 |
| `trends` | 跨 CR 趋势分析 | 迭代 ID（可选） | pace-retro 报告 |
| `report` | 风险全局视图 | — | 用户显式调用 |
| `resolve` | 更新风险状态 | RISK 编号 + 目标状态 | Gate 通过后自动提议 |

## 输入

$ARGUMENTS：

- `scan [CR编号]` → 对指定 CR（或当前活跃 CR）执行 Pre-flight 风险扫描
- `monitor [CR编号]` → 汇总当前 CR 的实时风险状态
- `trends [迭代ID]` → 分析跨 CR 的风险趋势（默认当前迭代）
- `report` → 生成项目级风险全局视图
- `resolve <RISK编号> <目标状态>` → 更新指定风险的状态（mitigated / accepted / closed）
- （空）→ 等同于 `scan`，对当前 CR 执行风险扫描

### 各子命令读取的数据源

| 子命令 | 数据源 |
|--------|--------|
| `scan` | CR 文件（意图、技术方案）、`project.md` 功能树、关联 CR 文件、代码库（Glob/Grep） |
| `monitor` | CR 文件（风险登记表）、`state.md`（当前状态）、最近 git diff |
| `trends` | 迭代目录下所有 CR 的风险登记表、`knowledge/metrics.md` 度量定义 |
| `report` | `project.md` 全部 PF、所有活跃 CR 的风险登记表、迭代历史 |
| `resolve` | 目标 RISK 条目所在 CR 文件、关联 Gate 检查结果 |

## 流程

### Step 1：上下文加载

1. 检查 `.devpace/` 是否存在：
   - **存在** → 读取 `state.md` 确定当前 CR 和项目状态，继续 Step 2
   - **不存在（降级模式）** → 基于代码库直接分析（无 CR 级风险追踪，仅提供即时风险评估）
2. 如果指定了 CR 编号 → 定位对应 CR 文件
3. 如果未指定 → 读取 state.md 当前活跃 CR

### Step 2：路由到子命令

根据 $ARGUMENTS 第一个参数路由（**仅读取匹配子命令的规程文件**）：

| 参数 | 流程 | 详细规程 |
|------|------|---------|
| （空）/ `scan` | Pre-flight 风险扫描 | `guard-procedures.md` §1 |
| `monitor` | 实时风险汇总 | `guard-procedures.md` §2 |
| `trends` | 跨 CR 趋势分析 | `guard-procedures.md` §3 |
| `report` | 风险全局视图 | `guard-procedures.md` §4 |
| `resolve` | 更新风险状态 | `guard-procedures.md` §5 |

### Step 3：执行并报告

1. 按子命令流程执行
2. 将风险发现写入 CR 文件"风险登记表"section（scan/monitor 产出）
3. 更新 state.md（如有状态变化）
4. **智能推荐**（仅 scan 和 monitor 子命令）：报告末尾根据风险等级推荐下一步操作：
   - 存在 High 风险 → "建议：先处理高风险项再进入开发，或执行 `/pace-guard resolve` 标记已接受"
   - 仅 Medium 风险 → "建议：开发时关注这些风险点，可用 `/pace-guard monitor` 持续跟踪"
   - 仅 Low 风险 → "风险可控，可安全进入开发"

## 输出

| 子命令 | 产出 |
|--------|------|
| `scan` | 风险清单（编号、等级、描述、建议缓解措施），写入 CR 文件风险登记表 |
| `monitor` | 当前 CR 风险状态摘要（3-5 行），含已缓解/待处理/新增统计 |
| `trends` | 跨 CR 风险趋势报告（按类别统计、重复风险识别、改进建议） |
| `report` | 项目级风险仪表盘（按 PF 分组、按等级排序、总体风险评分） |
| `resolve` | 更新确认（1-2 行），含状态变更和关联影响说明 |

**降级模式**（无 .devpace/）：
- `scan` / `monitor` → 基于代码库的即时风险评估（不写文件）
- `trends` / `report` → 不可用（需要历史数据）
- `resolve` → 不可用（需要风险登记表）
