# 发布管理执行规程——Status 与 Status History

> **职责**：展示当前 Release 状态和跨 Release 历史时间线。
>
> **自包含**：本文件独立执行，不需要加载其他 procedures 文件。

## §0 速查卡片

- **Status**：活跃 Release → CR 分布 + 问题数 + 验证进度 + 环境进度 + 建议下一步
- **Status History**：跨 Release 时间线 + 回滚标记 + DORA 趋势联动

## Status 详细流程

### 无活跃 Release

输出："当前没有进行中的 Release。N 个 merged CR 待发布。"

### 有活跃 Release

```
## Release 状态

REL-xxx：v{版本号} — [状态]
- 包含 CR：N 个（feature:A, defect:B, hotfix:C）
- 部署后问题：M 个（已处理 K）
- 验证进度：X/Y 项通过
- 环境进度：[staging ✅] → [production 👈 当前] → [完成]  （多环境时展示）
- 建议下一步：[deploy/verify/close/处理问题/changelog/rollback]
```

## Status History 详细流程（发布时间线）

扫描 `.devpace/releases/` 所有 Release 文件，生成跨 Release 纵向视图。

### 时间线生成

1. 读取所有 Release 文件，提取：版本号、状态、包含 CR 数、CR 类型分布、创建日期、关闭日期
2. 按创建日期排序（最新在前）
3. 生成可视化时间线：

```
## Release 历史时间线

v1.3.0 (REL-003) — closed — 2026-02-25
  3 CR (2 feature, 1 defect) · 周期 5 天

v1.2.1 (REL-002) — 🔴 rolled_back — 2026-02-20
  1 CR (1 hotfix) · 原因：支付流程崩溃

v1.2.0 (REL-001) — closed — 2026-02-15
  4 CR (3 feature, 1 defect) · 周期 3 天

───────────────────────────────
总计：3 个 Release · 回滚率 33% · 平均周期 4 天
```

### DORA 趋势联动

如果 `dashboard.md` 存在且包含 DORA 数据，追加趋势摘要：

```
### 交付节奏趋势（最近 5 个 Release）
- 部署频率：1.5 次/周（↑ 上升趋势）
- 平均变更前置时间：4.2 天（↓ 改善中）
- 变更失败率：33%（⚠️ 需关注）
```

### 输出规则

- 默认展示最近 10 个 Release（超过时折叠旧记录）
- Rolled_back Release 用 🔴 标记并展示回滚原因
- 无 Release 历史时输出"尚无发布历史记录。"
