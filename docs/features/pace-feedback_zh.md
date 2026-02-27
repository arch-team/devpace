# 反馈收集与事件管理（`/pace-feedback`）

> **核心价值**：将"部署后的世界"——生产问题、用户反馈、改进建议——有序回流到价值链，闭合"交付→反馈→改进"和"部署→反馈→修复"两大循环。

每条反馈获得唯一 **FB-ID**（格式 `FB-NNN`），从初次记录到最终处置全程可追踪。无论是紧急生产事件还是功能改进建议，pace-feedback 都能帮你追溯"为什么会发生"并路由到正确的处理流程。

## 快速上手

```
1. /pace-feedback report "支付接口 500 错误"  → 紧急通道 → 创建 hotfix CR
2. /pace-feedback "搜索结果不准确"             → 分类 → 改进建议池
3. /pace-feedback                              → 渐进式两轮引导收集
```

紧急通道用法：

```
你:    /pace-feedback report "登录超时，大量用户受影响"
Claude: [紧急通道] 严重度：critical | 关联：用户认证（PF-03）
        已创建 hotfix CR-042。建议走加速路径（跳过 in_review）？
```

## 工作流程

### Step 0：草稿恢复检查

检查 `.devpace/backlog/FEEDBACK-DRAFT.md` 是否存在：
- **存在** → "上次反馈（FB-xxx：[症状摘要]）未完成，是否继续？"
  - 继续 → 从草稿恢复，跳到上次中断的步骤
  - 放弃 → 删除草稿，从头开始
- **不存在** → 进入 Step 1

### Step 1：分类反馈

根据反馈内容分为 5 种类型（生产事件、缺陷、改进、新需求、记录待定），分类后路由到对应处理流程。完整分类定义见 `SKILL.md` 的分类表。

`report` 参数直接进入"生产事件"分支并评估加速路径资格。

### Step 2：严重度评估 + 价值链追溯

- 根据影响范围×紧急程度矩阵自动建议严重度（critical/major/minor/trivial）
- 追溯路径：问题描述 → 匹配 PF → 查找 CR 历史 → 定位 Release → 缩小引入范围
- 同时检查历史反馈匹配（同一 PF 下的相似反馈）

### Step 3：MoS 更新

反馈涉及已定义的成效指标时：
- 缺陷/生产事件 → 在 project.md 对应 MoS 处追加备注
- 改进 → 建议调整或新增 MoS 指标

### Step 4：执行后续动作

按分类路由到对应处理流程（创建 CR、写入建议池、路由到 /pace-change、保存到 Inbox）。

### Step 5：状态与度量更新

- 更新 project.md 功能树（🐛 或 🔥 标记）
- 更新 `.devpace/feedback-log.md`（新增 FB 条目）
- 更新 dashboard.md 缺陷逃逸率

### Step 6：草稿清理

处理完成后删除 `.devpace/backlog/FEEDBACK-DRAFT.md`。

## 核心特性

### FB-ID 全链路追踪

每条反馈分配唯一 FB-ID，记录在 `.devpace/feedback-log.md`。状态按分类路径流转（已创建→处理中→已修复、已创建→待规划→已采纳、已创建→待处理→重新分类、已创建→已转交），完整定义见 `feedback-procedures-status.md`。

### 渐进式两轮收集

空参数调用时分两轮收集信息：
- **第一轮**（必要）：症状描述 + 影响范围/紧急程度
- **第二轮**（仅 severity ≥ major）：复现步骤 + 首次发现时间

trivial/minor 级别直接跳过第二轮，减少 80% 场景下的交互轮次。

### 中断恢复（草稿机制）

收集到第一个有效信息时自动保存草稿。下次调用自动检测并提示恢复，已收集信息不丢失。完整机制见 `feedback-procedures-common.md`。

### 追溯报告三层输出

追溯结果按需展开：
- **表层**（默认）：`追溯：关联 PF-03，疑似由 CR-012 引入（置信度：高）`——1 行
- **中层**（追问"为什么"）：完整追溯链 + 置信度依据——3-5 行
- **深层**（/pace-trace）：完整决策审计链

### 反馈收件箱（Inbox）

"记录待定"类型保存到 `.devpace/feedback-inbox.md`。pace-plan 规划新迭代时自动扫描 Inbox，提醒"有 N 条待处理反馈"。用户不确定如何分类时可先记录，之后再处理。

### 改进建议池

改进建议写入 project.md 对应 PF 的"改进建议池"表格（结构化记录：FB-ID + 描述 + 日期 + 状态）。pace-plan 规划迭代时可扫描"待规划"条目，确保改进建议不被遗忘。

### 历史反馈匹配与聚合

关联价值链时自动检查同一 PF 下的历史反馈。多次报告相同问题时建议提升严重度。同一 PF 累计 ≥3 条缺陷反馈时触发质量风险提醒。

### 根因分析智能辅助

创建 defect CR 时自动扫描 `insights.md` 的防御 pattern，匹配相似历史根因。命中时输出：`💡 相似历史：CR-008（认证超时问题），根因是 token 刷新逻辑，建议优先检查类似路径`。

### Git 原生追溯增强

当结构化追溯置信度为"低"时，自动补充 `git log` 和 `git blame` 分析作为辅助证据，帮助定位疑似引入变更。

### 紧急通道与加速路径

`report` 参数跳过分诊，直接进入生产事件处理。type:hotfix + severity:critical 时自动评估加速路径资格（跳过 in_review），用户确认后启用。

### 降级模式

`.devpace/` 存在但 `releases/` 不存在时以降级模式运行：核心功能（分类、严重度评估、CR 创建、改进建议池、收件箱、FB-ID 追踪）保持完整，仅 Release 追溯和部署时间关联被跳过。详见 `feedback-procedures-common.md`。

## 使用场景

### 场景 1：生产事件紧急处理

```
你:    /pace-feedback report "支付网关超时，用户无法完成付款"
Claude: [FB-012] 紧急通道——生产事件
        严重度：critical | 关联：支付功能（PF-05）
        追溯：疑似由 CR-038（支付优化）引入（置信度：高）
        已创建 hotfix CR-045。建议走加速路径？

你:    是
Claude: 加速路径已启用。开始修复？→ /pace-dev
```

### 场景 2：改进建议进入建议池

```
你:    /pace-feedback "搜索结果排序不够智能，相关性低的排在前面"
Claude: [FB-013] 分类：改进 | 关联：搜索功能（PF-08）
        已记入 PF-08 改进建议池。建议纳入下次迭代规划。
```

### 场景 3：中断恢复

```
你:    /pace-feedback
Claude: 发现未完成反馈草稿（FB-014：接口超时问题），是否继续？

你:    继续
Claude: 已恢复。上次收集到：症状=接口超时、影响=部分用户。
        需要多快修复？（立即/尽快/可等待）
```

## 与其他命令的协作

| 命令 | 协作方式 |
|------|---------|
| `/pace-dev` | 创建 defect/hotfix CR 后，用户可直接进入 /pace-dev 修复 |
| `/pace-change` | 新需求类反馈路由到 /pace-change 走变更管理流程 |
| `/pace-plan` | 规划迭代时扫描改进建议池和反馈收件箱 |
| `/pace-test` | insights.md 的 `test-gap: true` 条目供 pace-test strategy 扫描 |
| `/pace-retro` | 回顾时展示反馈转化率、热点 PF、缺陷逃逸趋势 |
| `/pace-pulse` | 运维关键词信号检测，建议使用 /pace-feedback report |
| `pace-learn` | defect CR merged 后提取防御 pattern 到 insights.md |

## 相关资源

- [User Guide — /pace-feedback](../user-guide.md) — 参数速查
- [英文版本](./pace-feedback.md) — English version
- [skills/pace-feedback/](../../skills/pace-feedback/) — Skill 实现和详细规程
- [devpace-rules.md §14](../../rules/devpace-rules.md) — 条件生效规则
- [metrics.md](../../knowledge/metrics.md) — 度量指标定义
