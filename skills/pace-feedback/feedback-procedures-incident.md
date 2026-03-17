# 事件管理规程

> **职责**：结构化事件管理——创建、追踪、关闭和复盘。补全运维闭环。

## 与 report/hotfix 的关系

| 入口 | 定位 | 适用场景 |
|------|------|---------|
| `report` | 紧急通道，快速创建 Defect/Hotfix CR | 发现问题需要立即修复 |
| `incident open` | 事件管理，结构化记录和追踪 | 需要分级响应、时间线追踪、事后复盘 |

两者可并行使用：`incident open` 创建事件记录 → `report` 创建对应的 Hotfix CR → CR merged 后 `incident close` 关闭事件。

## incident open

### 严重度分级

复用现有严重度矩阵（feedback-procedures-hotfix.md），映射为事件等级：

| 严重度 | 事件等级 | 响应要求 | 示例 |
|--------|---------|---------|------|
| critical | P0 | 立即响应，所有工作暂停 | 全站不可用、数据丢失 |
| major | P1 | 1 小时内响应 | 核心功能不可用、性能严重降级 |
| minor | P2 | 当日响应 | 非核心功能异常、UI 错误 |
| trivial | P3 | 下个迭代处理 | 体验优化、文案问题 |

### 创建流程

1. 评估严重度（复用 hotfix 严重度矩阵）
2. 创建 `.devpace/incidents/` 目录（如不存在）
3. 生成 `INCIDENT-NNN.md`，包含：
   - 标题、严重度、状态（open）
   - 影响范围描述
   - 时间线（含创建时间）
   - 关联 CR 列表（初始为空）
4. P0/P1 事件 → 额外提醒："建议立即 `/pace-feedback report` 创建 Hotfix CR"
5. 输出摘要

### 事件文件格式

格式遵循 `knowledge/_schema/auxiliary/incident-format.md`。

## incident close

1. 读取事件文件，确认状态为 open/investigating/mitigated
2. 更新状态为 closed，记录关闭时间
3. 生成 Postmortem 模板（追加到事件文件 Postmortem section）：
   - **影响摘要**：持续时间、影响范围
   - **根本原因**：（待填写）
   - **修复措施**：关联 CR 的修复摘要
   - **预防措施**：（待填写）
   - **经验教训**：（待填写）
4. 提醒用户填写 Postmortem 的空白字段
5. 如有关联 CR → 检查是否全部 merged，未全部 merged 则警告

## incident timeline

只读展示事件时间线，按时间倒序排列。

## incident list

列出 `.devpace/incidents/` 中所有事件。`--open` 只显示非 closed 状态的事件。

## 容错

| 异常 | 处理 |
|------|------|
| incidents/ 不存在 | open 时自动创建；list/timeline/close 报告无事件记录 |
| INCIDENT 编号不存在 | 提示无效编号，列出可用选项 |
| 关闭已关闭的事件 | 提示已关闭，展示 Postmortem |
