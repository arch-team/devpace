# 发布管理执行规程——Changelog 生成

> **职责**：从 CR 元数据自动生成 Changelog。
>
> **自包含**：本文件独立执行，不需要加载其他 procedures 文件。

## §0 速查卡片

- **来源**：Release 包含的 CR 元数据（标题、类型、PF 关联）
- **分组**：Features → Bug Fixes → Hotfixes
- **写入**：Release 文件 `## Changelog` section + 用户产品根目录 CHANGELOG.md（追加到顶部）

## 从 CR 元数据生成

1. 读取 Release 包含的 CR 列表
2. 对每个 CR 提取：标题、类型（feature/defect/hotfix）、关联 PF 名称
3. 按类型分组（格式见 `knowledge/_schema/process/release-format.md` §Changelog）：

```markdown
## [版本号] - YYYY-MM-DD

### Features

- [CR-001] 用户认证登录（PF-001 用户认证）
- [CR-004] 数据导出功能（PF-003 数据管理）

### Bug Fixes

- [CR-003] 修复搜索结果排序错误（PF-002 搜索功能）

### Hotfixes

- [CR-005] 紧急修复支付流程崩溃（PF-004 支付系统）
```

4. 写入 Release 文件的 `## Changelog` section
5. 写入用户产品根目录的 CHANGELOG.md（追加到文件顶部，保留历史记录）
   - CHANGELOG.md 不存在 → 创建新文件，包含标准头部
   - 已存在 → 在 `# Changelog` 标题后、第一个版本段之前插入新版本段

> **Release Notes**：生成条件和流程见 `release-procedures-notes.md`（权威源）。close 流程中按条件自动提示。
