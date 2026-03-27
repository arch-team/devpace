# 架构决策记录规程

> **职责**：/pace-trace arch 子命令——创建、查看和管理架构决策记录（ADR）。

## §0 速查卡片

| 操作 | 命令 | 说明 |
|------|------|------|
| 创建 ADR | `/pace-trace arch "决策标题"` | 交互式引导创建 ADR |
| 查看 ADR | `/pace-trace arch ADR-NNN` | 查看指定 ADR |
| 列出所有 | `/pace-trace arch list` | 列出所有 ADR 及状态 |
| 取代 ADR | `/pace-trace arch supersede ADR-NNN` | 标记旧 ADR 为 superseded |

## 从 pace-dev 自动触发

当 L/XL CR 的技术方案评审（`skills/pace-dev/dev-procedures-intent.md` Phase B0）满足 ADR 触发条件时：
- pace-dev 在 merged 后的连锁更新中提醒："此 CR 涉及架构决策，建议 `/pace-trace arch` 记录"
- 用户确认 → 进入标准 ADR 创建流程（预填 CR 编号和方案信息）
- 用户跳过 → 在 CR 事件表标注"ADR 建议未采纳"

## 创建流程

### Step 1: 确定 ADR 编号

1. 读取 `.devpace/decisions/` 目录
2. 找到最大编号 → 新编号 = 最大 + 1
3. 目录不存在 → 创建目录 + ADR-001

### Step 2: 交互式引导

引导用户填写以下信息（按 `knowledge/_schema/auxiliary/adr-format.md` 格式）：

1. **决策标题**：从 $ARGUMENTS 获取，或询问
2. **上下文**：面临什么技术问题？
3. **决策**：选择了什么方案？
4. **理由**：为什么选择这个？
5. **替代方案**（可选）：考虑过哪些？

### Step 3: 写入文件

1. 按 adr-format.md 模板生成文件
2. 状态设为 `accepted`（用户已确认决策）
3. 如有关联 CR → 同时在 CR 事件表记录 `ADR-NNN created`

### Step 4: 输出确认

```
已创建架构决策：ADR-NNN — [标题]
状态：accepted
位置：.devpace/decisions/ADR-NNN.md
```

## 查看流程

1. 读取指定 ADR 文件
2. 格式化输出（标题、状态、日期、摘要）
3. 如 ADR 被取代 → 显示取代者链接

## 列表流程

1. 扫描 `.devpace/decisions/ADR-*.md`
2. 提取每个 ADR 的标题和状态
3. 表格输出：

```
| # | 标题 | 状态 | 日期 |
|---|------|------|------|
| ADR-001 | 选择 PostgreSQL | accepted | 2026-01-15 |
| ADR-002 | 微服务架构 | superseded → ADR-005 | 2026-02-01 |
```

## 取代流程

1. 读取目标 ADR
2. 将状态改为 `superseded`
3. 填写"被取代"字段 → 指向新 ADR
4. 引导创建新 ADR（替代方案）

## 规则

- ADR 一旦 accepted，内容不可修改（只能 supersede 后创建新版本）
- 目录不存在时自动创建（首次使用无门槛）
- 与 `/pace-trace timeline` 互补：timeline 追踪 CR 级决策，arch 追踪架构级决策
