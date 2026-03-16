# 事件记录格式定义

> **职责**：定义 `.devpace/incidents/INCIDENT-NNN.md` 的文件格式。
>
> Reserved: 预留给 pace-feedback incident tracking，当前无消费者。

## §0 速查卡片

| 维度 | 值 |
|------|---|
| 文件位置 | `.devpace/incidents/INCIDENT-NNN.md` |
| 编号规则 | 扫描目录最大编号 +1，3 位补零 |
| 状态流转 | open → investigating → mitigated → closed |
| 写入方 | pace-feedback incident open/close |

## 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| 标题 | 字符串 | 事件简述 |
| 严重度 | P0/P1/P2/P3 | 事件等级 |
| 状态 | open/investigating/mitigated/closed | 当前状态 |
| 影响范围 | 字符串 | 受影响的用户/功能/模块 |
| 开始时间 | ISO 8601 | 事件发现时间 |
| 关联 CR | 列表 | 相关 Hotfix/Defect CR 编号 |

## 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| 结束时间 | ISO 8601 | 事件关闭时间（closed 时填充） |
| Postmortem | 结构化文本 | 事后复盘（closed 时生成模板） |

## 时间线格式

时间线是事件文件内嵌的表格，每行记录一个事件节点。

## 文件结构

```markdown
# INCIDENT-NNN：[标题]

- **严重度**：[P0 | P1 | P2 | P3]
- **状态**：[open | investigating | mitigated | closed]
- **影响范围**：[描述]
- **开始时间**：[YYYY-MM-DDTHH:MM:SS]
- **结束时间**：[YYYY-MM-DDTHH:MM:SS | —]
- **关联 CR**：[CR-xxx, CR-yyy | 无]

## 时间线

| 时间 | 事件 |
|------|------|
| [ISO 8601] | 事件创建 |

## Postmortem

（事件关闭后由 incident close 生成模板）
```

## 状态机

```
open ──→ investigating ──→ mitigated ──→ closed
  │            │                           ↑
  │            └───────────────────────────┘
  └──→ closed（轻微事件可直接关闭）
```

### 转换规则

| 转换 | 触发者 | 条件 |
|------|--------|------|
| open → investigating | Claude 或人类 | 开始调查 |
| open → closed | Claude 或人类 | 轻微事件直接关闭 |
| investigating → mitigated | Claude 或人类 | 影响已缓解但根因未修复 |
| investigating → closed | Claude 或人类 | 根因已修复 |
| mitigated → closed | Claude 或人类 | 根因已修复、Postmortem 完成 |

**约束**：closed 是终态，不可回退。每次状态变更必须在时间线追加一行。

## 编号规则

- 文件名格式：`INCIDENT-NNN.md`，NNN 为三位数字，从 001 开始递增
- 存储目录：`.devpace/incidents/`
- 编号规则：取 `.devpace/incidents/` 目录下现有 `INCIDENT-*.md` 文件的最大编号 +1
- 目录不存在时由 `incident open` 自动创建
- 编号不复用：即使事件已 closed，其编号不回收

## 更新时机

| 操作 | 触发场景 | 动作 |
|------|---------|------|
| 创建 | incident open | 新建 INCIDENT-NNN.md，状态 open |
| 时间线追加 | 状态变更、关键事件发生 | 时间线表格追加行 |
| 状态更新 | incident close 或手动更新 | 更新头部状态 + 时间线追加行 |
| Postmortem 生成 | incident close | 填充 Postmortem section 模板 |
