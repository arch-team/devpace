# 发布管理执行规程——发布分支管理

> **职责**：Release 分支的创建、PR 和合并操作。
>
> **自包含**：本文件独立执行，不需要加载其他 procedures 文件。

## §0 速查卡片

- **三种模式**：直接发布（默认）· Release 分支 · Release PR
- **操作**：`branch create` → `branch pr`（PR 模式）→ `branch merge`
- **close 联动**：close 时自动检测 release 分支 → 提示先 merge

## 分支模式

发布分支是可选功能——不使用时所有发布操作在 main 分支完成。

三种模式（通过 integrations/config.md 的"发布分支"配置选择）：

| 模式 | 流程 | 适用场景 |
|------|------|---------|
| 直接发布（默认） | main 分支直接 tag + release | 小型项目、持续部署 |
| Release 分支 | main → release/v{version} → 验证修复 → merge 回 main | 需要最终验证的正式发布 |
| Release PR | 创建包含 changelog + version bump 的 PR，用户 merge PR = 确认发布 | 借鉴 Release Please，PR 驱动发布 |

## branch create 流程

1. 确认 Release 处于 `staging` 状态
2. 确认当前在 main 分支且工作区干净（`git status`）
3. 创建分支：`git checkout -b release/v{version}`
4. 在 Release 文件中记录分支名称
5. 提示用户：在 release 分支上完成最终修复和验证

## branch pr 流程（Release PR 模式）

借鉴 Release Please 的 PR 驱动发布模式：

1. 确认 Release 处于 `staging` 或 `verified` 状态
2. 在 release 分支（或 main）上提交 changelog + version bump 变更
3. 创建 PR：
   ```
   gh pr create --title "Release v{version}" --body "{changelog + CR 列表}"
   ```
4. PR 内容包含：
   - Changelog 预览
   - 包含的 CR 列表（类型、标题、PF）
   - Gate 4 检查结果摘要
5. 用户 merge PR → 可视为 deploy 确认
6. 更新 Release 状态

## branch merge 流程

1. 确认 Release 分支存在
2. 切换到 main：`git checkout main`
3. 合并 release 分支：`git merge release/v{version} --no-ff`
4. 删除 release 分支：`git branch -d release/v{version}`
5. 提示用户是否 push：`git push origin main`

## close 时自动检测

Release close 时检查是否存在 release 分支：
- 存在 → 提示用户先 merge 回 main（或自动执行 branch merge）
- 不存在 → 正常关闭
