---
description: Use when user asks "下一步做什么", "接下来做什么", "该做什么", "什么最重要", "应该先做哪个", "最紧急", "优先级", "推荐做什么", "为什么推荐这个", "pace-next", or wants a recommendation for the most important next action across all domains. NOT for current progress overview (use /pace-status).
allowed-tools: Read, Glob, Grep
argument-hint: "[detail|why]"
model: haiku
---

# /pace-next — 下一步导航

跨域全局导航：综合 CR、迭代、Release、度量、风险等多维信号，推荐当前最该做的 1 件事。

## 输入

$ARGUMENTS：
- （空）→ 最高优先级 1 条建议（默认，≤ 3 行）
- `detail` → 展开候选列表（≤ 8 行，含 top-3 建议）
- `why` → 展开推理链（2-5 行，信号扫描 + 优先级对比 + 角色影响 + 备选）

## 执行路由

**重要**：根据 $ARGUMENTS 值，仅读取对应的输出规程文件，不加载全部规程。所有模式先加载 `next-procedures.md`（核心决策逻辑）。

| 参数 | 加载文件 |
|------|---------|
| （空） | `next-procedures.md` + `next-procedures-output-default.md` |
| `detail` | `next-procedures.md` + `next-procedures-output-detail.md` |
| `why` | `next-procedures.md` + `next-procedures-output-why.md` |

## 流程

### Step 1：检测项目状态

1. 检查项目根目录是否存在 `.devpace/state.md`
2. 不存在 → 输出未初始化引导（见 next-procedures.md），结束
3. 存在 → 继续

### Step 2：采集信号

读取 `.devpace/` 下的数据源（目录/文件不存在时静默跳过）：

| 数据源 | 读取内容 |
|--------|---------|
| `backlog/*.md` | CR 状态、类型 |
| `state.md` | 当前工作摘要 |
| `releases/*.md` | Release 状态 |
| `risks/*.md` | 风险严重度 |
| `iterations/current.md` | PF 完成率、周期 |
| `metrics/dashboard.md` | 最近更新日期 |
| `project.md` | MoS、PF/BR/OBJ 映射 |
| `integrations/sync-mapping.md` | 同步状态（存在时） |

提取关键状态字段（不全量读取）。额外采集 CR→PF→BR 价值链映射。

### Step 3：优先级决策

从高到低遍历信号分组，取首个命中（判断细节见 next-procedures.md）：

| 组 | 信号 |
|----|------|
| Blocking | S1 审批阻塞（in_review > 0）· S2 高风险阻塞（High 且 open） |
| In Progress | S3 继续开发（developing CR）· S4 恢复暂停（paused 阻塞解除） |
| Delivery | S5 Release 待验证 · S6 风险积压（open > 3）· S7 迭代紧迫（< 2 天且 < 50%）· S8 迭代接近完成（> 80%） |
| Strategic | S9 回顾提醒（> 7 天 + merged）· S10 缺陷占比（> 30%）· S11 同步滞后（> 24h）· S12 MoS 达成（> 80%） |
| Growth | S13 功能未开始 · S14 规划新迭代 · S15 全部完成 |
| Idle | S16 无信号 |

### Step 4：经验增强

匹配历史经验 pattern（`.devpace/metrics/insights.md`，如存在），在建议中附加 ≤1 行经验参考。

### Step 5：角色适配

根据当前角色（Dev/PM/Biz/Tester/Ops）调整建议措辞维度和信号组内排序。

### Step 6：输出

按路由表加载的输出规程文件格式化输出。

## 输出

≤ 3 行（默认）或 ≤ 8 行（detail）或 2-5 行推理链（why）。自然语言为主，不暴露 ID。建议体现价值链上下文。

<!-- 信号摘要同步自 knowledge/signal-priority.md + knowledge/signal-collection.md，修改信号时须同步 -->
