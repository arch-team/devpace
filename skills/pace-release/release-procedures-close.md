# 发布管理执行规程——Close

> **职责**：Release 关闭流程，8 步链进度指示器 + 中断恢复。
>
> **加载 common.md**：本文件与 `release-procedures-common.md` 配合使用。
>
> **步进式加载**：步骤 1-3 按执行进度加载对应独立文件——`release-procedures-changelog.md`（步骤 1）、`release-procedures-version.md`（步骤 2）、`release-procedures-tag.md`（步骤 3）。用户跳过某步则不加载对应文件。

## §0 速查卡片

- **前置检查**：Release 必须 verified · 部署后问题均有关联 CR
- **8 步链**：changelog→version→tag→CR 状态→project.md→iterations→state.md→dashboard
- **进度格式**：`[N/8] ✅ 步骤名称（结果）` · 失败时 `[N/8] ❌ 步骤名称：{原因}`
- **中断恢复**：`close_progress: N` → 下次从 N+1 继续 · 每步独立幂等
- **full 别名**：`full` 与 `close` 行为完全相同

## 前置检查

1. Release 必须处于 `verified` 状态
2. "部署后问题"表中所有问题的"关联 CR"都有值（均已创建修复 CR）
3. 检查未通过 → 提示用户先处理未解决的问题

## 关闭连锁更新（自动包含工具操作）

Release verified → closed 时**自动按顺序执行**以下全部步骤。每步完成后输出进度行，便于用户追踪和中断恢复。

**进度指示器格式**：每步执行时输出 `[N/8] 步骤名称...`，完成后输出 `[N/8] ✅ 步骤名称（简短结果）`。

**工具操作（每步前简短提示，任一步可跳过）**：
1. **Changelog 生成**（详见 `release-procedures-changelog.md`）：`[1/8] 生成 Changelog...` → 执行 → `[1/8] ✅ Changelog 已生成（N 条变更记录）`
2. **版本文件更新**（详见 `release-procedures-version.md`）：`[2/8] 版本号 v{old} → v{new}，确认？` → 执行 → `[2/8] ✅ 版本号已更新`（无配置则 `[2/8] ⏭️ 跳过（无版本文件配置）`）
3. **Git Tag 创建**（详见 `release-procedures-tag.md`）：`[3/8] 创建 Tag v{version}？` → 执行 → `[3/8] ✅ Tag v{version} 已创建`

**连锁状态更新（自动执行，每步输出确认行）**：
4. **CR 状态批量更新**：Release 包含的所有 CR，状态 merged → released
   - 在各 CR 事件表追加"released via REL-xxx"
   - `[4/8] ✅ CR 状态已更新（N 个 CR → released）`
5. **project.md 更新**：功能树中 released CR 标记 🚀
   - `[5/8] ✅ 功能树已标记`
6. **iterations/current.md 更新**：产品功能表 Release 列填入 REL-xxx
   - `[6/8] ✅ 迭代记录已更新`
7. **state.md 更新**：移除已关闭 Release 的发布状态段
   - `[7/8] ✅ 状态文件已更新`
8. **dashboard.md 更新**：
   - 部署频率 +1
   - 计算本 Release 各 CR 的变更前置时间（created → released）
   - 如有 defect CR 关联此 Release → 更新变更失败率
   - `[8/8] ✅ 度量数据已更新（部署频率、变更前置时间）`

## 中断恢复

如果任一步失败（文件冲突、权限错误等），Claude 应：
1. 明确报告哪一步失败及原因：`[N/8] ❌ 步骤名称失败：{原因}`
2. 已完成的步骤不回滚（每步是独立幂等的）
3. 提示用户修复后可从失败步继续：`"修复后，运行 /pace-release close 将从第 N 步继续（前 N-1 步已完成）。"`
4. 在 Release 文件中记录 `close_progress: N`（N = 已完成的最大步骤号），下次 close 时从 N+1 继续

## 关闭输出

```
Release REL-xxx 发布完成（v{version}）。
✅ Changelog → CHANGELOG.md
✅ 版本号 → {版本文件} ({旧版本} → {新版本})
✅ Git Tag → v{version}
✅ N 个 CR → released
✅ 度量数据已更新
```

## Full 流程

`full` 与 `close` 行为完全相同——推荐使用 `full` 因为语义更明确（"完成发布"而非"关闭"）。执行流程和输出格式见上方章节。
