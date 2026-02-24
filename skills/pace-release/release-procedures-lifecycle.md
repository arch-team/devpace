# 发布管理执行规程——生命周期

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

Release create 完成后、deploy 之前执行（可选，格式见 `knowledge/_schema/integrations-format.md`）：

**CI 自动感知**：如果 `integrations/config.md` 不存在或无 CI/CD section，Gate 4 先按"CI 自动检测映射表"（integrations-format.md）扫描项目根目录。检测到 CI 配置时，使用默认检查命令执行状态检查（不持久化到 config.md，仅本次使用）。建议用户运行 `/pace-init` 持久化检测结果。

1. **构建验证**：读取 `integrations/config.md` 的 CI/CD 构建命令 → 执行（如 `npm run build`）
   - 命令成功 → ✅ 构建通过
   - 命令失败 → ❌ 提示修复后重试
   - 未配置构建命令 → 跳过
2. **CI 状态检查**：读取检查命令 → 执行。命令来源优先级：① integrations/config.md 配置 → ② CI 自动检测默认命令 → ③ 均无则跳过
   - 最近一次运行成功 → ✅ CI 绿色
   - 运行失败或进行中 → ⚠️ 提示用户确认是否继续
   - 检查命令对应 CLI 不可用（command not found）→ 跳过并提示安装
3. **候选完整性检查**：遍历 Release 包含的 CR，确认全部 Gate 1/2/3 已通过
   - 检查 CR 状态为 merged（已经过全部 Gate）
   - 任何 CR 状态异常 → ❌ 提示修复

Gate 4 不通过时不阻断 Release 创建（Release 已经创建为 staging），但提示用户在 deploy 前修复问题。

4. **自动生成 Release 测试报告**：Gate 4 检查完成后（不论通过与否），自动执行 `/pace-test report REL-xxx`，将 Release 级测试质量报告附加到 Release 文件
   - 报告内容：CR 质量汇总 + 功能覆盖 + 风险评估 + 发布建议（详见 `skills/pace-test/test-procedures-strategy.md` §6.2）
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
1. **Changelog 生成**（详见 `release-procedures-expert.md`「Changelog 生成流程」）：简短提示 "正在生成 Changelog..." → 执行 → 展示预览
2. **版本文件更新**（详见 `release-procedures-expert.md`「Version Bump 流程」）：简短提示 "建议版本号 v{version}，确认？" → 执行（无配置则自动跳过）
3. **Git Tag 创建**（详见 `release-procedures-expert.md`「Git Tag 流程」）：简短提示 "创建 Tag v{version}？" → 执行

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
