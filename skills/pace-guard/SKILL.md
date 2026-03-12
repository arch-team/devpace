---
description: Use when user wants to assess risks before development, check current risk status, analyze risk trends, or says "风险/预检/预分析/guard/risk/隐患/安全检查". Also auto-invoked during advance mode intent checkpoint for L/XL CRs. NOT for /pace-dev (implementation), NOT for /pace-review (quality gate), NOT for /pace-test (testing).
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
model: sonnet
argument-hint: "[scan|monitor|trends|report|resolve] [CR编号] [--full|--brief|--detail|--batch]"
context: fork
agent: pace-analyst
---

# /pace-guard — 风险预判与管理

统一管理开发全生命周期的风险：从编码前的 Pre-flight 扫描，到开发中的实时监控，再到跨迭代的趋势分析——让风险可见、可追踪、可解决。风险评估覆盖 Epic 级别（Epic 范围风险影响其下所有 BR/PF/CR）。

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

- `scan [CR编号] [--full|--detail]` → 对指定 CR（或当前活跃 CR）执行 Pre-flight 风险扫描。`--full` 强制完整 5 维扫描，`--detail` 展示全维度矩阵
- `monitor [CR编号] [--detail|--brief]` → 汇总当前 CR 的实时风险状态。默认简要输出，`--detail` 展开完整表格
- `trends [迭代ID] [--detail]` → 分析跨 CR 的风险趋势（默认当前迭代）。默认摘要，`--detail` 展示完整趋势报告
- `report [--brief|--detail]` → 生成项目级风险全局视图
- `resolve <RISK编号> <目标状态>` → 更新指定风险的状态（mitigated / accepted / resolved）
- `resolve --batch [严重度]` → 批量处理同等级的 open 风险
- （空）→ 等同于 `scan`，对当前 CR 执行风险扫描

## 流程

### Step 1：上下文加载

1. 检查 `.devpace/` 是否存在：
   - **存在** → 读取 `state.md` 确定当前 CR 和项目状态，继续 Step 2
   - **不存在（降级模式）** → 基于代码库直接分析（无 CR 级风险追踪，仅提供即时风险评估）
2. 如果指定了 CR 编号 → 定位对应 CR 文件
3. 如果未指定 → 读取 state.md 当前活跃 CR

### Step 2：路由到子命令

根据 $ARGUMENTS 第一个参数路由（**仅读取匹配子命令的规程文件**）：

| 参数 | 流程 | 加载文件 |
|------|------|---------|
| （空）/ `scan` | Pre-flight 风险扫描 | `guard-procedures-common.md` + `guard-procedures-scan.md` |
| `monitor` | 实时风险汇总 | `guard-procedures-common.md` + `guard-procedures-monitor.md` |
| `trends` | 跨 CR 趋势分析 | `guard-procedures-trends.md`（自包含） |
| `report` | 风险全局视图 | `guard-procedures-report.md`（自包含） |
| `resolve` | 更新风险状态 | `guard-procedures-common.md` + `guard-procedures-resolve.md` |

### Step 3：执行并报告

1. 按子命令流程执行
2. 将风险发现写入 CR 文件"风险预评估"section（scan/monitor 产出）
3. 更新 state.md（如有状态变化）
4. **智能推荐**：风险评估类报告末尾根据风险等级推荐下一步操作（详见各子命令规程文件）

## 输出

各子命令均支持 `--brief`/`--detail` 分层输出，具体格式和降级模式见对应 procedures 文件。
