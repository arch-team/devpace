# 发布管理执行规程——Git Tag

> **职责**：创建 Git Tag 和可选的 GitHub Release。
>
> **自包含**：本文件独立执行，不需要加载其他 procedures 文件。

## §0 速查卡片

- **Tag 格式**：`{前缀}{版本号}`（默认前缀 `v`，如 `v1.3.0`）
- **GitHub Release**：检测 `gh` CLI → 用户确认 → 以 changelog 为 release notes

## 创建 Tag

1. 读取 Release 版本号和 integrations/config.md 的 Tag 前缀（默认 `v`）
2. Tag 名称：`{前缀}{版本号}`（如 `v1.3.0`）
3. 执行 `git tag {tag名称}`
4. 提示用户是否 push tag（`git push origin {tag名称}`）

## 可选：GitHub Release

1. 检查 `gh` CLI 是否可用
2. 可用 → 询问用户是否创建 GitHub Release
3. 用户确认 → 执行：
   ```
   gh release create {tag名称} --title "Release {版本号}" --notes "{changelog内容}"
   ```
4. `gh` 不可用或用户拒绝 → 跳过
