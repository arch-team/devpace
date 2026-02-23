# 发布管理执行规程

> **职责**：Release 生命周期的详细执行规则。/pace-release 触发后，Claude 按需读取本文件。

## 引导式向导流程（空参数）

当用户调用 `/pace-release` 不带参数时，执行引导式向导：

### 状态检测与引导

1. 扫描 `.devpace/releases/` 查找活跃 Release（状态非 closed/rolled_back）
2. 扫描 `.devpace/backlog/` 查找 merged 且未关联 Release 的 CR
3. 根据以下优先级引导：

| 检测到的状态 | 引导行为 | 自动执行 |
|-------------|---------|---------|
| 有 verified Release | "Release v{version} 验证通过。完成发布？（将自动生成 Changelog、更新版本号、创建 Git Tag）" | → close 流程 |
| 有 deployed Release | "Release v{version} 已部署。要开始验证吗？" + 附加选项"出了问题？" | → verify 或 rollback 流程 |
| 有 staging Release | "Release v{version} 已准备好，包含 N 个变更。下一步：部署到 [环境]？" | → deploy 流程 |
| 无活跃 Release + 有 merged CR | "有 N 个已完成的任务可以发布。要创建新发布吗？" | → create 流程 |
| 无活跃 Release + 无 merged CR | "当前没有待发布的变更。" | 无操作 |

### 引导交互规则

- 每个引导问题使用 AskUserQuestion 工具，提供明确选项
- 用户确认后直接执行对应子命令的完整流程
- 用户拒绝或选择其他操作 → 展示可用选项
- 引导过程中向用户说明正在做什么，但不暴露子命令名称（对齐 §3 自然语言映射）

## Create 详细流程

### 候选 CR 收集

1. 扫描 `.devpace/backlog/` 所有 CR 文件
2. 筛选条件：状态为 `merged` 且无"关联 Release"字段（或字段为空）
3. 按类型排序展示：hotfix > defect > feature

### 候选展示格式

```
## Release 候选 CR

| CR | 标题 | 类型 | PF | 合并日期 |
|----|------|------|-----|---------|
| CR-001 | [标题] | feature | PF-001 | 2026-02-20 |
| CR-003 | [标题] | defect | PF-002 | 2026-02-21 |

共 N 个候选 CR。全部纳入还是选择部分？
```

### Release 创建

1. 用户确认纳入范围后，创建 REL-xxx.md
2. ID 自增：扫描 `.devpace/releases/` 最大编号 +1
3. 状态初始化为 `staging`
4. 自动填充验证清单（默认 4 项 + 项目自定义）
5. 更新各 CR 文件的"关联 Release"字段为 REL-xxx
6. 更新 state.md 发布状态段
7. 可选：如果 integrations/config.md 配置了发布分支模式，创建 `release/v{version}` 分支

### 版本号建议

- 包含 feature → minor 版本递增（如 1.2.0 → 1.3.0）
- 仅 defect/hotfix（无 feature）→ patch 版本递增（如 1.2.0 → 1.2.1）
- 用户可自定义版本号

### Gate 4 系统级发布门禁

Release create 完成后、deploy 之前执行（可选，依赖 integrations/config.md，格式见 `knowledge/_schema/integrations-format.md`）：

1. **构建验证**：读取 `integrations/config.md` 的 CI/CD 构建命令 → 执行（如 `npm run build`）
   - 命令成功 → ✅ 构建通过
   - 命令失败 → ❌ 提示修复后重试
   - 未配置构建命令 → 跳过
2. **CI 状态检查**：读取检查命令（如 `gh run list --branch main --limit 1`）→ 执行
   - 最近一次运行成功 → ✅ CI 绿色
   - 运行失败或进行中 → ⚠️ 提示用户确认是否继续
   - 未配置检查命令 → 跳过
3. **候选完整性检查**：遍历 Release 包含的 CR，确认全部 Gate 1/2/3 已通过
   - 检查 CR 状态为 merged（已经过全部 Gate）
   - 任何 CR 状态异常 → ❌ 提示修复

Gate 4 不通过时不阻断 Release 创建（Release 已经创建为 staging），但提示用户在 deploy 前修复问题。

4. **自动生成 Release 测试报告**：Gate 4 检查完成后（不论通过与否），自动执行 `/pace-test report REL-xxx`，将 Release 级测试质量报告附加到 Release 文件
   - 报告内容：CR 质量汇总 + 功能覆盖 + 风险评估 + 发布建议（详见 `skills/pace-test/test-procedures.md` §6.2）
   - 如报告返回"数据不足"信息（部分 CR 缺少 accept 或 coverage 数据），在 Release 文件备注"部分 CR 缺少测试数据，建议补全"并附补全建议清单
   - 无 `/pace-test` Skill 可用时静默跳过（不阻断 Release 创建）

## Deploy 详细流程

### 环境晋升模式

读取 `integrations/config.md` 的环境表（格式见 `knowledge/_schema/integrations-format.md`）：

1. **单环境或无配置**：直接部署确认（当前行为不变）
2. **多环境**：按环境表行序逐环境部署
   - 展示晋升路径：`[env1] → [env2] → [env3]`
   - 从首环境开始，每个环境独立 deploy + verify
   - 当前环境验证通过后，提示晋升到下一环境
   - 最终环境部署后 Release 状态 staging → deployed

晋升流程：
```
staging → deploy(env1) → verify(env1) → deploy(env2) → verify(env2) → ... → deploy(envN) → deployed
```

每次 deploy 在部署记录表追加一行（含环境名称），更新 Release 的"当前环境"字段。

### 部署确认

1. 确认 Release 处于 `staging` 状态
2. 询问部署目标环境（如有多环境配置）
   - 多环境模式：自动选择晋升路径的下一个环境
   - 单环境模式：手动选择或使用默认环境
3. 如果 integrations/config.md 配置了部署命令 → 询问用户是否让 devpace 执行
   - 用户确认 → 执行部署命令并报告结果
   - 用户拒绝或无配置 → 用户自行部署，确认已完成
4. 在 Release 部署记录表追加：

```markdown
| 日期 | 环境 | 操作 | 结果 | 备注 |
|------|------|------|------|------|
| 2026-02-21 | production | 部署 | 成功 | [用户备注] |
```

5. Release 状态 staging → deployed
6. 更新 state.md 发布状态段

## Verify 详细流程

### 自动验证（如有配置）

读取 `integrations/config.md` 的"发布验证"段：

1. 执行验证命令（如 `curl -sf https://api.example.com/health`）
   - 在配置的超时时间内成功 → ✅ 预填到验证清单
   - 超时或失败 → ❌ 标记失败，提示人工确认
2. 执行额外验证命令（如有）
3. 自动验证结果展示在验证清单中

无验证命令配置时，跳过自动验证，完全手动。

### 验证清单

1. 展示 Release 的验证清单（自动验证结果预填）
2. 逐项引导确认（可批量确认）
3. 用户自定义验证项可动态追加

### 验证通过

全部验证项勾选：
- 单环境模式 → Release 状态 deployed → verified
- 多环境模式 → 如果不是最终环境 → 提示 `/pace-release deploy` 晋升到下一环境
- 多环境模式 → 最终环境 → Release 状态 deployed → verified

### 验证发现问题

1. 在 Release "部署后问题"表追加记录
2. 引导用户创建 defect/hotfix CR（调用 /pace-feedback report 逻辑）
3. 新创建的 defect CR 自动关联当前 Release
4. Release 状态保持 deployed（不回退到 staging）

## Close 详细流程

> close 和 full 行为完全相同——full 是 close 的推荐别名。close 默认自动包含 changelog + version + tag 工具操作，用户不再需要单独调用。

### 前置检查

1. Release 必须处于 `verified` 状态
2. "部署后问题"表中所有问题的"关联 CR"都有值（均已创建修复 CR）
3. 检查未通过 → 提示用户先处理未解决的问题

### 关闭连锁更新（自动包含工具操作）

Release verified → closed 时**自动按顺序执行**以下全部步骤：

**工具操作（每步前简短提示，任一步可跳过）**：
1. **Changelog 生成**（详见 Changelog 流程）：简短提示 "正在生成 Changelog..." → 执行 → 展示预览
2. **版本文件更新**（详见 Version Bump 流程）：简短提示 "建议版本号 v{version}，确认？" → 执行（无配置则自动跳过）
3. **Git Tag 创建**（详见 Git Tag 流程）：简短提示 "创建 Tag v{version}？" → 执行

**连锁状态更新（自动执行，无需逐步确认）**：
4. **CR 状态批量更新**：Release 包含的所有 CR，状态 merged → released
   - 在各 CR 事件表追加"released via REL-xxx"
5. **project.md 更新**：功能树中 released CR 标记 🚀
6. **iterations/current.md 更新**：产品功能表 Release 列填入 REL-xxx
7. **state.md 更新**：移除已关闭 Release 的发布状态段
8. **dashboard.md 更新**：
   - 部署频率 +1
   - 计算本 Release 各 CR 的变更前置时间（created → released）
   - 如有 defect CR 关联此 Release → 更新变更失败率

**与旧版行为的区别**：旧版 close 需要用户先手动调用 changelog/version/tag 子命令，新版 close 自动包含这些步骤。工具操作步骤 1-3 每步前有简短提示，用户可跳过任一步（优雅降级）。

### 关闭输出

```
Release REL-xxx 已关闭（v{version}）。
- Changelog 已生成 → CHANGELOG.md
- 版本号已更新 → {版本文件}
- Git Tag 已创建 → v{version}
- N 个 CR 状态更新为 released
- 功能树已更新
- 度量数据已更新（部署频率、变更前置时间）
```

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

## Full 流程（close 的推荐别名）

`full` 与 `close` 行为完全相同——推荐使用 `full` 因为语义更明确（"完成发布"而非"关闭"）。

执行流程和输出格式见上方"Close 详细流程"章节。

### Close/Full 输出

```
Release REL-xxx 发布完成（v{version}）。
✅ Changelog → CHANGELOG.md
✅ 版本号 → {版本文件} ({旧版本} → {新版本})
✅ Git Tag → v{version}
✅ N 个 CR → released
✅ 度量数据已更新
```

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

Release close 时检查是否存在 release 分支：
- 存在 → 提示用户先 merge 回 main（或自动执行 branch merge）
- 不存在 → 正常关闭

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
- 建议下一步：[deploy/verify/close/处理问题/changelog/rollback]
```

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
