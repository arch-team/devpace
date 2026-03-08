# Epic 文件格式契约

> **职责**：定义 Epic 独立文件 `epics/EPIC-xxx.md` 的结构。/pace-biz epic 创建时遵循此格式。

## §0 速查卡片

```
文件名：EPIC-xxx.md（xxx 为自增数字，三位补零）
目录：.devpace/epics/
创建时机：/pace-biz epic（从 Opportunity 转化或直接创建）
始终独立文件：Epic 不内联在 project.md 中，始终有独立文件
内容：OBJ 关联（主/副）+ 状态 + 来源 + 时间框架 + 背景 + 双维度 MoS + BR 列表
OBJ 引用：有 objectives/ 时链接到 OBJ 文件；无 objectives/ 时保持纯文本格式（向后兼容）
MoS 格式：双维度（客户价值 + 企业价值），无维度标签的简单 checkbox 列表仍合法
project.md 保留：价值功能树中 Epic 行用 Markdown 链接指向文件
向后兼容：无 epics/ 目录的项目不受影响——BR 直挂 OBJ（现有行为不变）
容错：Epic 文件丢失时从 project.md 树视图 + BR 文件重建
```

## 文件结构

```markdown
# EPIC-xxx：[专题名称]

- **OBJ**：[OBJ-xxx：目标描述](../objectives/OBJ-xxx.md)（主）；OBJ-y（副）
- **状态**：[规划中 | 进行中 | 已完成 | 已搁置]
- **来源**：[OPP-xxx（[描述]）]（可选——首次 /pace-biz 时填充）
- **时间框架**：[Iter-x]（可选——首次 /pace-plan 时填充）

## 背景

[2-3 句话：为什么做这个专题，要解决什么问题]

## 成效指标（MoS）

**客户价值**：
- [ ] [指标 1]（目标：[值]）

**企业价值**：
- [ ] [指标 2]（目标：[值]）

> 当前值和进度为可选字段，/pace-retro 时可追加（格式：`目标：[值]，当前：[值] → 进度 [N]%`）

## 业务需求

| BR | 标题 | 优先级 | 状态 | PF 数 | 完成度 |
|----|------|:------:|------|:-----:|:------:|
| BR-001 | [需求名] | P0 | 进行中 | 2 | 1/2 |
| BR-002 | [需求名] | P1 | 待开始 | 0 | — |
```

## 字段说明

| 字段 | 核心/渐进 | 来源 | 说明 |
|------|:---------:|------|------|
| 标题 | 核心 | /pace-biz epic 创建时 | EPIC 编号 + 专题名称 |
| OBJ 关联 | 核心 | 创建时 Claude 关联 | 主 OBJ ID + 描述（链接到 OBJ 文件）；副 OBJ 可选 |
| 状态 | 核心 | Claude 自动维护 | 基于 BR 完成度聚合计算 |
| 来源 | 渐进 | Claude 推断 | 关联 OPP-ID（从 Opportunity 转化时） |
| 时间框架 | 渐进 | /pace-plan 或讨论排期时 | 迭代 ID |
| 背景 | 核心 | 人类提供 | 2-3 句话说明专题原因 |
| MoS | 渐进 | 人类定义或 /pace-biz 引导 | 专题级成效指标，双维度（客户价值 + 企业价值） |
| BR 列表 | 核心(自动) | BR 创建时 Claude 自动关联 | 含优先级、状态、PF 数、完成度 |

### 状态计算规则

| 条件 | Epic 状态 |
|------|----------|
| 所有 BR 的 PF 均已完成（全部 CR merged/released） | 已完成 |
| 至少一个 BR 有进行中的 PF（有 developing/verifying/in_review CR） | 进行中 |
| 所有 BR 均 `待开始` 或 Epic 刚创建 | 规划中 |
| 所有 BR 均 `暂停` 或 Epic 被显式搁置 | 已搁置 |

### BR 列表字段说明

| 列 | 说明 |
|----|------|
| BR | BR 编号（如溢出则为链接） |
| 标题 | BR 名称 |
| 优先级 | `P0` / `P1` / `P2` / `—`（未评估） |
| 状态 | `待开始` / `进行中` / `已完成` / `暂停` |
| PF 数 | 关联的 PF 总数 |
| 完成度 | 已完成 PF 数 / PF 总数（无 PF 时显示 `—`） |

## 命名规则

- 文件名：`EPIC-001.md`、`EPIC-002.md`...（三位补零自增）
- ID 自增：扫描 `.devpace/epics/` 中现有 Epic 文件的最大编号 +1
- 目录不存在时自动创建

## project.md 中的引用格式

价值功能树中 Epic 行始终使用 Markdown 链接：

```markdown
OBJ-001（[目标名]）
├── [EPIC-001：专题名](epics/EPIC-001.md)
│   ├── BR-001：需求名 `P0` `进行中` → PF-001 → CR-001 🔄
│   └── [BR-002：需求名](requirements/BR-002.md) `P1` → PF-002, PF-003
└── [EPIC-002：专题名](epics/EPIC-002.md)
    └── BR-003：需求名 `P0` → PF-004 → CR-003 ✅
```

**有 objectives/ 时**：OBJ 行使用链接格式：

```markdown
[OBJ-001：目标名](objectives/OBJ-001.md)
├── [EPIC-001：专题名](epics/EPIC-001.md)
│   ├── BR-001：需求名 `P0` `进行中` → PF-001 → CR-001 🔄
│   └── BR-002：需求名 `P1` → PF-002, PF-003
└── [EPIC-002：专题名](epics/EPIC-002.md)
    └── BR-003：需求名 `P0` → PF-004 → CR-003 ✅
```

**无 Epic 时**：BR 直接挂在 OBJ 下（与当前行为一致，向后兼容）：

```markdown
OBJ-001（[目标名]）
├── BR-001：需求名
│   └── PF-001：功能名 → CR-001 🔄
```

## 更新时机

| 事件 | 更新内容 |
|------|---------|
| BR 创建/删除 | BR 列表表格 |
| BR 状态变更 | BR 列表表格 + Epic 状态重新计算 |
| PF/CR 状态变更 | BR 完成度 + Epic 状态重新计算 |
| /pace-change pause Epic | 状态 → 已搁置 |
| /pace-change resume Epic | 状态恢复 |
| /pace-plan 分配时间框架 | 时间框架字段 |
| /pace-retro 评估 MoS | MoS checkbox |

## 容错

| 异常 | 处理 |
|------|------|
| Epic 文件丢失 | 从 project.md 树视图 + BR 文件中的 Epic 关联字段重建 |
| epics/ 目录不存在 | /pace-biz epic 时自动创建 |
| project.md 链接指向不存在的 Epic 文件 | 按"Epic 文件丢失"处理 |
| Epic 文件与 project.md 树视图状态不一致 | 以 Epic 文件为准（更详细），同步更新树视图 |
| BR 列表与实际 BR 文件不一致 | 以 BR 文件和 project.md 树视图为准重建 |
