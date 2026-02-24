# 发布管理执行规程——专家功能

> **职责**：Release 专家功能（Changelog、版本管理、Tag、回滚、Release Notes、分支管理）和发布/集成规则。/pace-release 触发后，Claude 按需读取本文件。

## Changelog 生成流程

### 从 CR 元数据生成

1. 读取 Release 包含的 CR 列表
2. 对每个 CR 提取：标题、类型（feature/defect/hotfix）、关联 PF 名称
3. 按类型分组：

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

### 可选：Release Notes（用户级）

如果用户请求或 Release 包含多个 PF 的变更，可生成按 BR/PF 组织的高层 Release Notes：

```markdown
## Release Notes - v{version}

### [BR-001] 用户体验提升
- **[PF-001] 用户认证**：新增登录功能（CR-001）
- **[PF-002] 搜索功能**：修复排序错误（CR-003）

### [BR-002] 系统稳定性
- **[PF-004] 支付系统**：紧急修复崩溃问题（CR-005）
```

## Version Bump 流程

### 读取版本配置

1. 读取 `integrations/config.md` 的"版本管理"段
2. 提取：版本文件路径、版本格式、版本字段路径、Tag 前缀
3. 无版本管理配置 → 提示用户手动更新版本文件，跳过后续步骤

### 推断版本号

1. 读取当前版本号：
   - json 格式：`Read` 文件 → 解析 JSON → 提取字段值
   - toml 格式：`Read` 文件 → 正则提取 `字段 = "x.y.z"`
   - yaml 格式：`Read` 文件 → 正则提取 `字段: x.y.z`
   - text 格式：`Read` 文件 → 正则提取语义化版本号
2. 根据 Release 包含的 CR 类型推断：
   - 包含 feature → minor 递增（1.2.0 → 1.3.0）
   - 仅 defect/hotfix（无 feature）→ patch 递增（1.2.0 → 1.2.1）
   - 用户可覆盖为任意版本号
3. 用户确认版本号

### 更新版本文件

1. 使用 `Edit` 工具替换版本文件中的版本号
   - json：替换 `"version": "旧版本"` → `"version": "新版本"`
   - toml：替换 `version = "旧版本"` → `version = "新版本"`
   - yaml：替换 `version: 旧版本` → `version: 新版本`
   - text：替换旧版本号字符串
2. 更新 Release 文件的版本号字段

## Git Tag 流程

### 创建 Tag

1. 读取 Release 版本号和 integrations/config.md 的 Tag 前缀（默认 `v`）
2. Tag 名称：`{前缀}{版本号}`（如 `v1.3.0`）
3. 执行 `git tag {tag名称}`
4. 提示用户是否 push tag（`git push origin {tag名称}`）

### 可选：GitHub Release

1. 检查 `gh` CLI 是否可用
2. 可用 → 询问用户是否创建 GitHub Release
3. 用户确认 → 执行：
   ```
   gh release create {tag名称} --title "Release {版本号}" --notes "{changelog内容}"
   ```
4. `gh` 不可用或用户拒绝 → 跳过

## Rollback 流程

### 前置检查

1. Release 必须处于 `deployed` 状态
2. 如不处于 deployed → 提示当前状态，不允许操作

### 回滚记录

1. 询问回滚原因
2. 在 Release 部署记录表追加回滚记录：

```markdown
| 日期 | 环境 | 操作 | 结果 | 备注 |
|------|------|------|------|------|
| 2026-02-22 | production | 回滚 | 成功 | [回滚原因] |
```

3. Release 状态 deployed → rolled_back
4. 更新 state.md 发布状态段

### 后续处理

1. 引导用户创建 defect/hotfix CR 关联本次回滚原因
2. 新 CR 的"关联 Release"指向当前 Release
3. 提示：修复后需创建新 Release（rolled_back 是终态）

## Release Notes 生成流程

### 与 Changelog 的区别

| 维度 | Changelog | Release Notes |
|------|-----------|---------------|
| 受众 | 开发者 | 产品用户 |
| 组织方式 | 按 CR 类型（Features/Bug Fixes/Hotfixes） | 按 BR→PF（业务需求→产品功能） |
| 粒度 | CR 级别（每个变更一行） | PF 级别（每个功能一段描述） |
| 语言 | 技术语言（含 CR/PF 编号） | 产品语言（无技术编号） |
| 生成时机 | close 时自动 | 用户请求或 close 时提示 |

### 生成流程

1. 读取 Release 包含的 CR 列表
2. 对每个 CR 提取关联的 PF 和 BR
3. 按 BR 分组，BR 下按 PF 聚合 CR：
   - BR 标题作为分组标题
   - PF 标题作为功能描述
   - 同一 PF 下的多个 CR 合并为一段描述
4. 用产品语言重写（去除 CR/PF 编号，改为用户可读的描述）

### Release Notes 格式

```
## What's New in v{version}

### 用户体验提升
- **用户认证**：新增登录功能，支持邮箱和手机号两种方式
- **搜索功能**：修复了搜索结果排序不正确的问题

### 系统稳定性
- **支付系统**：修复了在高并发场景下的崩溃问题
```

### 输出位置

1. 写入 Release 文件的 `## Release Notes` section
2. 可选：输出到用户产品根目录的 RELEASE_NOTES.md（用户确认）

## 发布分支管理流程

### 分支模式

发布分支是可选功能——不使用时所有发布操作在 main 分支完成。

三种模式（通过 integrations/config.md 的"发布分支"配置选择）：

| 模式 | 流程 | 适用场景 |
|------|------|---------|
| 直接发布（默认） | main 分支直接 tag + release | 小型项目、持续部署 |
| Release 分支 | main → release/v{version} → 验证修复 → merge 回 main | 需要最终验证的正式发布 |
| Release PR | 创建包含 changelog + version bump 的 PR，用户 merge PR = 确认发布 | 借鉴 Release Please，PR 驱动发布 |

### branch create 流程

1. 确认 Release 处于 `staging` 状态
2. 确认当前在 main 分支且工作区干净（`git status`）
3. 创建分支：`git checkout -b release/v{version}`
4. 在 Release 文件中记录分支名称
5. 提示用户：在 release 分支上完成最终修复和验证

### branch pr 流程（Release PR 模式）

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

### branch merge 流程

1. 确认 Release 分支存在
2. 切换到 main：`git checkout main`
3. 合并 release 分支：`git merge release/v{version} --no-ff`
4. 删除 release 分支：`git branch -d release/v{version}`
5. 提示用户是否 push：`git push origin main`

### close 时自动检测

Release close（详见 `release-procedures-lifecycle.md`「Close 详细流程」）时检查是否存在 release 分支：
- 存在 → 提示用户先 merge 回 main（或自动执行 branch merge）
- 不存在 → 正常关闭

## 发布管理规则（从 devpace-rules.md §14 迁入）

### Release 流程

```
/pace-release create → Gate 4 → staging → deploy确认 → deployed → verify通过 → verified → close → closed
                                              │                                      │
                                              └→ rolled_back                         └→ changelog + version + tag
```

### Release 规则

- **可选性**：`.devpace/releases/` 不存在或无 Release 文件时，所有 Release 行为静默跳过
- **候选收集**：仅 merged 且未关联 Release 的 CR 可纳入新 Release
- **状态机**：staging → deployed → verified → closed + deployed → rolled_back
- **人类确认**：deployed 和 verified 状态转换需人类确认
- **自动关闭**：verified → closed 由 Claude 自动执行（含连锁更新）
- **主动编排**：通过 git/gh 等标准工具执行发布动作，不替代 CI/CD

### Release 关闭连锁更新

Release 关闭时自动执行（补充 §2 merged 后连锁更新）：

1. Changelog 生成（写入 Release + 用户 CHANGELOG.md）
2. 版本文件更新（按 integrations/config.md 配置，无配置跳过）
3. Git Tag 创建（+ 可选 GitHub Release）
4. 关联 CR 状态批量 merged → released
5. project.md 功能树 CR 标记 🚀
6. iterations/current.md Release 列更新
7. state.md 发布状态段更新
8. dashboard.md 度量更新（部署频率、变更前置时间、变更失败率）

### 已纳入 Release 的 CR 变更

当用户对已纳入 Release（staging/deployed）的 CR 发起变更时：

1. **影响分析**：评估变更对 Release 稳定性的影响
2. **高风险变更**：建议从 Release 中移出该 CR，在下个 Release 中包含
3. **低风险变更**：允许原地修改，在 Release 部署记录中注明
4. **已 deployed 的 Release**：不允许修改包含的 CR，发现问题走 /pace-feedback report 创建新 defect CR

## 集成管理规则（从 devpace-rules.md §16 迁入）

### 集成原则

- **手动摄入始终可用**：即使无集成配置，所有功能通过手动输入可用
- **集成是增强不是前置**：集成配置提供自动化便利，但不是必需
- **编排不替代**：devpace 编排和调用用户的工具（git/gh/npm），不替代 GitHub Actions/Jenkins

### 集成配置使用

当 `integrations/config.md` 存在时：
- /pace-release create：Gate 4 系统级检查（构建/CI/完整性）
- /pace-release deploy：可选执行部署命令
- /pace-release verify：自动执行验证命令
- /pace-release version：读取版本文件配置进行 bump
- /pace-release tag：读取 Tag 前缀配置
- /pace-feedback：根据告警映射自动建议严重度
- 节奏检测：可检查部署相关信号

### 降级行为

当无集成配置时：
- 所有功能正常工作，仅需手动输入更多信息
- 不提示"请先配置集成"——集成是可选增强
- changelog 始终可用（从 CR 元数据生成，不依赖集成配置）
- version/tag 提示用户手动操作
