# 产品功能文件格式契约

> **职责**：定义 PF 溢出后独立文件 `features/PF-xxx.md` 的结构。溢出触发时 Claude 自动创建此文件。

## §0 速查卡片

```
文件名：PF-xxx.md（xxx 为 PF 编号，三位补零）
目录：.devpace/features/
创建时机：溢出触发（功能规格 >15 行 | 关联 3+ CR | 经历过 /pace-change modify）
内容：BR 关联 + 状态 + 用户故事 + 验收标准（含 history 注释）+ 边界 + 关联 CR 表 + 风险
project.md 保留：树视图行 + [详情] 链接，功能规格 section 中该 PF 段落移除
向后兼容：无 features/ 目录的项目不受影响——所有 PF 行为保持 project.md 内联
容错：PF 文件丢失时从 project.md 残留内容 + CR 文件重建
```

## 溢出触发条件

当以下任一条件满足时，Claude 自动将 PF 从 project.md 内联溢出为独立文件：

| 条件 | 检测方式 | 说明 |
|------|---------|------|
| 功能规格超过 ~15 行 | 计算 project.md 中该 PF 的功能规格 section 行数 | 信息量足以支撑独立文件 |
| 关联 3+ 个 CR | 计算价值功能树中该 PF 关联的 CR 数（含已完成） | 生命周期复杂度上升 |
| 经历过 `/pace-change modify` | 检查 CR 事件表或迭代变更记录中该 PF 的 modify 记录 | 变更历史需要版本化追踪 |

**溢出是单向的**——一旦溢出不回退。project.md 树视图始终是入口。

## 溢出执行步骤

1. 创建 `.devpace/features/` 目录（如不存在）
2. 创建 `features/PF-xxx.md`，按下方文件结构填充
3. 将 project.md 功能规格 section 中该 PF 的段落内容迁移到新文件
4. project.md 功能规格 section 中移除该 PF 段落（若 section 变为空则移除整个 section）
5. project.md 价值功能树中该 PF 行追加链接：`→ [详情](features/PF-xxx.md)`

## 文件结构

```markdown
# PF-xxx：[产品功能名称]

- **BR**：[BR 名称]（[BR-ID]）→ [OBJ-ID]
- **状态**：[进行中 | 全部 CR 完成 | 已发布 | 暂停]
- **用户故事**：[作为...，我希望...]

## 验收标准

1. [x] [标准 1]
2. [x] [标准 2]
3. [ ] [标准 3]
<!-- history: [日期] 原始 N 项; [日期] +[新增内容] via /pace-change -->

## 边界

- [不包含 X]
- [不包含 Y]

## 关联 CR

| CR | 状态 | 类型 | 标题 |
|----|------|------|------|
| CR-001 | ✅ merged | feature | [标题] |
| CR-005 | 🔄 developing | defect | [标题] |

## 风险

- [RISK-ID]：[风险描述]（[状态]）
```

## 字段说明

| 字段 | 必填 | 来源 | 说明 |
|------|------|------|------|
| 标题 | 是 | project.md PF 行 | PF 编号 + 名称 |
| BR 关联 | 是 | project.md 价值功能树 | BR 名称和 ID + OBJ ID |
| 状态 | 是 | 计算得出 | 基于关联 CR 状态聚合 |
| 用户故事 | 否 | project.md PF 行括号内容 | 首个 CR 创建时填充 |
| 验收标准 | 否 | project.md 功能规格迁移 | 带 checkbox 和 history 注释 |
| 边界 | 否 | project.md 功能规格迁移 | /pace-change 涉及该 PF 时填充 |
| 关联 CR | 是 | 价值功能树 + backlog/ | 溢出时从现有数据聚合 |
| 风险 | 否 | `.devpace/risks/` | 有关联风险时填充 |

### 状态计算规则

| 条件 | PF 状态 |
|------|--------|
| 所有关联 CR 均 merged 或 released | ✅ 全部 CR 完成 |
| 有至少一个 CR 为 released | 🚀 已发布（如部分发布则标注） |
| 有至少一个 CR 为 developing/verifying/in_review | 🔄 进行中 |
| 所有关联 CR 均 paused | ⏸️ 暂停 |
| 仅有 created 状态 CR 或无 CR | ⏳ 待开始 |

### 验收标准 history 注释

验收标准变更时，在标准列表下方用 HTML 注释记录变更历史：

```markdown
<!-- history: 2026-02-20 原始 2 项; 2026-02-25 +锁定机制 via /pace-change -->
```

格式：`<!-- history: [日期] [摘要]; [日期] [摘要] -->`

此注释保留完整变更轨迹，`git log features/PF-xxx.md` 提供更详细的文件级历史。

## 更新时机

| 事件 | 更新内容 |
|------|---------|
| CR 状态变更（merged/released/paused） | 关联 CR 表 + PF 状态 |
| `/pace-change modify` 涉及该 PF | 验收标准 + history 注释 + 边界 |
| `/pace-change add` 新增 CR 关联该 PF | 关联 CR 表 |
| 新风险关联该 PF | 风险 section |
| `/pace-retro` 涉及该 PF | 状态确认 |

## 容错

| 异常 | 处理 |
|------|------|
| PF 文件丢失 | 从 project.md 功能规格残留（如有）+ backlog/ CR 文件重建 |
| features/ 目录不存在 | 溢出时自动创建 |
| project.md 链接指向不存在的 PF 文件 | 按"PF 文件丢失"处理 |
| PF 文件与 project.md 树视图状态不一致 | 以 PF 文件为准（更详细），同步更新树视图 |
