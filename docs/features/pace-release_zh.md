# 发布管理（`/pace-release`）

devpace 将发布视为一项**主动编排活动**，而非被动的状态追踪。`/pace-release` 驱动完整的发布生命周期——收集已合并的变更、跨环境部署、验证结果、以及通过自动化 changelog、版本号管理和标签完成发布关闭——全程基于 `git` 和 `gh` 等标准工具。它编排你的发布流水线，而非替代你的 CI/CD。

## 前置条件

| 条件 | 用途 | 是否必需？ |
|------|------|:---------:|
| `.devpace/` 已初始化 | 包含已合并 CR 的核心 devpace 项目结构 | 是 |
| `.devpace/releases/` 目录 | 发布文件存储（首次 `create` 时自动创建） | 自动 |
| `integrations/config.md` | Gate 4 检查、部署命令、版本文件配置、环境晋升 | 可选 |
| `gh` CLI | 通过 `tag` 子命令创建 GitHub Release | 可选 |

> **优雅降级**：所有功能在没有 `integrations/config.md` 时都能正常工作——只是需要手动提供更多信息。Changelog 生成始终可用，因为它直接读取 CR 元数据。

## 快速开始

```
1. /pace-release create   --> 收集已合并的 CR，建议版本号，创建 REL-001（staging）
2. /pace-release deploy   --> 记录部署到目标环境（deployed）
3. /pace-release verify   --> 执行验证清单（verified）
4. /pace-release close    --> 生成 changelog + 升级版本号 + 创建标签 + 级联更新（closed）
```

或者直接调用 `/pace-release`（无参数）——引导向导会检测当前状态并引导你执行正确的下一步。

## 命令参考

### 用户层（User Layer）

以下六个命令覆盖标准发布生命周期。大多数团队只需要这些命令。

#### `create`

从已合并的 CR 创建新的 Release。

**语法**：`/pace-release create`

扫描 `.devpace/backlog/` 中处于 `merged` 状态且尚未关联到 Release 的 CR。按类型排序显示候选项（hotfix > defect > feature），询问包含哪些 CR，建议语义化版本号，并创建一个处于 `staging` 状态的 `REL-xxx.md` 文件。如果存在 `integrations/config.md`，可选执行 Gate 4 系统级检查。详见 [release-procedures-create.md](../../skills/pace-release/release-procedures-create.md)。

#### `deploy`

记录一次环境部署。

**语法**：`/pace-release deploy`

支持单环境和多环境晋升。在多环境配置下，遵循定义的晋升路径（`env1 -> env2 -> ... -> envN`），在每个环境执行 deploy + verify 后再晋升到下一个环境。将部署记录追加到 Release 文件，并将状态从 `staging` 转换为 `deployed`。详见 [release-procedures-deploy.md](../../skills/pace-release/release-procedures-deploy.md)。

#### `verify`

执行部署后验证。

**语法**：`/pace-release verify`

展示验证清单（当 `integrations/config.md` 定义了验证命令时，自动验证结果会预填充）。引导你逐项确认。如果发现问题，记录问题并帮助创建与当前 Release 关联的 defect/hotfix CR。全部通过后，将状态转换为 `verified`。详见 [release-procedures-verify.md](../../skills/pace-release/release-procedures-verify.md)。

#### `close`

执行所有关闭操作，完成发布。

**语法**：`/pace-release close`

要求 `verified` 状态。自动执行完整的关闭链：changelog 生成、版本文件升级、Git 标签创建（每一步都会显示简要提示，可跳过），然后进行级联状态更新——CR 状态更新为 `released`、project.md 功能树标记、迭代追踪、state.md 清理和仪表盘指标更新。详见 [release-procedures-close.md](../../skills/pace-release/release-procedures-close.md) 中的 8 步关闭链。

#### `full`

`close` 的推荐别名，语义更清晰（"完成发布"而非"关闭"）。

**语法**：`/pace-release full`

行为与 `close` 完全一致。详见 [release-procedures-close.md](../../skills/pace-release/release-procedures-close.md)。

#### `status`

查看当前 Release 状态和建议的下一步操作。

**语法**：`/pace-release status`

显示活跃 Release 的 CR 按类型分组明细、部署问题计数、验证进度，以及推荐的下一步操作。当不存在活跃 Release 时，显示可供发布的已合并 CR 数量。详见 [release-procedures-status.md](../../skills/pace-release/release-procedures-status.md)。

### 专家层（Expert Layer）

以下命令可单独使用，供需要精细控制特定发布步骤的团队使用。在正常的 `close` 流程中，步骤 1-3 会自动执行。

#### `changelog`

从 CR 元数据自动生成 CHANGELOG.md。

**语法**：`/pace-release changelog`

读取活跃 Release 中包含的 CR，按类型分组（Features / Bug Fixes / Hotfixes）并关联 PF，将条目写入 Release 文件和项目根目录的 `CHANGELOG.md`。详见 [release-procedures-changelog.md](../../skills/pace-release/release-procedures-changelog.md)。

#### `version`

升级语义化版本号。

**语法**：`/pace-release version`

从 `integrations/config.md` 读取版本文件配置（支持 JSON、TOML、YAML、纯文本）。根据 CR 类型推断升级级别：包含 feature = minor，仅 defect/hotfix = patch。用户可覆盖。就地更新版本文件。详见 [release-procedures-version.md](../../skills/pace-release/release-procedures-version.md)。

#### `tag`

创建 Git 标签，可选创建 GitHub Release。

**语法**：`/pace-release tag`

使用 Release 版本号和配置的前缀（默认 `v`）创建带注释的 Git 标签。当 `gh` CLI 可用时，提供创建 GitHub Release 的选项，以 changelog 内容作为 Release Notes。详见 [release-procedures-tag.md](../../skills/pace-release/release-procedures-tag.md)。

#### `notes`

生成面向用户的 Release Notes，按业务影响组织。

**语法**：`/pace-release notes [--role biz|ops|pm]`

与面向开发者的 changelog（按 CR 类型分组）不同，Release Notes 按 BR（业务需求）和 PF（产品功能）组织，使用产品语言，不包含技术标识符。包含"业务影响"章节，向上追溯到 OBJ 级别的目标和 MoS 进度。

通过 `--role` 参数生成特定角色视角的通知：`biz`（面向管理层的业务影响报告）、`ops`（面向运维的部署手册）、`pm`（面向产品经理的功能交付清单）。详见 [release-procedures-notes.md](../../skills/pace-release/release-procedures-notes.md)。

#### `branch`

管理发布分支。

**语法**：`/pace-release branch [create|pr|merge]`

支持 `integrations/config.md` 中配置的三种分支模式：直接发布（默认，在 main 上打标签）、发布分支（`release/v{version}` 用于最终修复）、Release PR（PR 驱动的发布流程，灵感来自 Release Please）。未配置分支模式时，所有操作在 main 分支上进行。详见 [release-procedures-branch.md](../../skills/pace-release/release-procedures-branch.md)。

#### `rollback`

当已部署的 Release 出现严重问题时记录回滚。

**语法**：`/pace-release rollback`

仅在 Release 处于 `deployed` 状态时可用。记录回滚原因，将回滚条目追加到部署日志，将状态转换为 `rolled_back`（终态），并引导创建根因追踪的 defect/hotfix CR。在回滚后创建新 Release 时，已回滚 Release 中无问题的 CR 会自动预填充为候选项，减少重复选择。详见 [release-procedures-rollback.md](../../skills/pace-release/release-procedures-rollback.md)。

#### `status history`

查看发布历史时间线及 DORA 趋势。

**语法**：`/pace-release status history`

扫描所有 Release 文件生成跨发布纵向视图：版本演进、每个 Release 的 CR 数量/类型、回滚标记、平均发布周期时长，以及 DORA 指标趋势（部署频率、前置时间、变更失败率）。默认显示最近 10 个 Release。详见 [release-procedures-status.md](../../skills/pace-release/release-procedures-status.md)。

## 发布状态机

```
                create          deploy          verify          close
  (merged CRs) -----> staging -----> deployed -----> verified -----> closed
                                        |
                                        | rollback
                                        v
                                   rolled_back
```

| 状态 | 含义 | 允许的转换 |
|------|------|-----------|
| `staging` | Release 已创建，CR 已收集，准备部署 | `deployed` |
| `deployed` | 已部署到目标环境 | `verified`、`rolled_back` |
| `verified` | 部署后验证通过 | `closed` |
| `closed` | 发布完成，所有关闭操作已执行（终态） | -- |
| `rolled_back` | 因严重问题回退部署（终态） | -- |

`deployed` 和 `verified` 转换需要人工确认。`verified` 到 `closed` 的转换由 Claude 自动执行（包括关闭链）。

## 核心特性

### Gate 4：系统级发布检查

在 `create` 之后运行的可选预部署门禁：

1. **构建验证**——执行 `integrations/config.md` 中的构建命令；失败时显示最后 10 行错误输出及建议修复步骤
2. **CI 状态检查**——查询 CI 流水线状态（无显式配置时自动检测 CI 配置）；失败时通过 `gh run view --web` 提供 CI 运行 URL
3. **候选项完整性**——确认所有包含的 CR 已通过 Gate 1/2/3（`merged` 状态）；失败时列出具体 CR 及其未通过的 Gate
4. **测试报告**——通过 `/pace-test report` 自动生成 Release 级质量报告

Gate 4 不会阻断 Release 创建——它在部署前暴露问题。检查结果持久化到 Release 文件中用于审计追溯。

### CR 依赖检测

在 `create` 过程中自动检测候选 CR 之间的依赖关系：
- **功能依赖**：关联到同一 PF 的 CR 被标记为功能相关
- **代码级依赖**：修改相同文件的 CR 被标记为代码交叉风险
- 显示包含/排除建议的依赖关系图

### 发布就绪检查

`create` 过程中的可选预验证，扫描候选 CR 的代码变更：
- 临时代码标记（`TODO`、`FIXME`、`console.log`、`debugger`）
- 缺失的测试覆盖（没有 accept 记录的 CR）
- 生成就绪度评分（A/B/C）——仅作参考，不会阻断流程

### 发布影响预览

在 `create` 之后自动生成，提供发布级别的全景视图：
- 代码变更统计（新增/删除行数、影响文件数）
- 模块级变更热力图
- 风险区域高亮（多个 CR 修改同一文件）
- 业务影响追溯（本次 Release 对 OBJ/BR 进度的贡献）

### Changelog 自动生成

Changelog 条目完全从 CR 元数据（标题、类型、PF 关联）生成，无需手动编写。输出同时写入 Release 文件和项目根目录的 `CHANGELOG.md`（在顶部追加，保留历史记录）。

### 带业务影响的 Release Notes

与 changelog 不同的独立输出：按 BR/PF 组织，使用产品语言，包含"业务影响"章节，向上追溯到 OBJ 级别的目标和 MoS 里程碑。通过 `--role` 参数支持角色视角：
- `--role biz`：面向业务（OBJ 进度、MoS 达成情况）
- `--role ops`：面向运维（部署详情、风险评估、回滚方案）
- `--role pm`：面向产品（功能交付清单、完成百分比）

Release Notes 生成门槛已降低：当 Release 包含至少 1 个 feature CR 时即可生成（之前要求 2+ 个 CR）。

### 带全景视图的环境晋升

当 `integrations/config.md` 定义了多个环境时，`deploy` 按顺序晋升路径执行，每个环境进行 deploy + verify。每次 deploy/verify 操作都会显示完整的晋升全景图及当前位置：`[staging ✅] → [canary ✅] → [production 👈 current] → [done]`。

### 关闭进度追踪

8 步关闭链逐步显示进度（`[N/8] ✅ Step name`），并支持中断恢复——如果任何步骤失败，之前的步骤会被保留，流程可以从失败步骤恢复。

### 带候选项预填充的回滚路径

当已部署的 Release 出现严重问题时，`rollback` 提供结构化的应对方案：记录事件、回退到已知状态、创建 CR 追踪修复。在回滚后创建新 Release 时，已回滚 Release 中无问题的 CR 会自动预填充为候选项，减少重复选择。

### 带回滚追踪的引导向导

无参数向导现在会追踪已回滚的 Release，并在引导下一步操作前显示修复 CR 的状态。防止用户遗忘未解决的回滚后续事项。

### 发布历史时间线

`status history` 提供跨发布纵向视图：版本演进、每个 Release 的 CR 数量/类型、回滚标记，以及 DORA 趋势摘要。

### 发布调度

可选的发布节奏配置（`integrations/config.md`）支持在向导和 pace-pulse 中显示窗口提醒，以迭代结束作为自然发布窗口。

## 使用场景

### 场景 1：标准发布

```
You:    /pace-release
Claude: Found 3 merged CRs ready for release.
        CR-001 (feature), CR-003 (defect), CR-005 (hotfix).
        Create a new release? [Y/n]

You:    Y
Claude: Suggested version: 1.3.0 (contains features).
        Confirm version? [1.3.0]

You:    1.3.0
Claude: REL-002 created (v1.3.0, staging).
        Gate 4: Build OK, CI green, all CRs passed.
        Next: /pace-release deploy

You:    /pace-release deploy
Claude: Deploy REL-002 (v1.3.0) to production? [Y/n]

You:    Y
Claude: Deployment recorded. Status: deployed.
        Next: /pace-release verify

You:    /pace-release verify
Claude: Verification checklist (3/3 passed).
        All items confirmed. Status: verified.
        Next: /pace-release close

You:    /pace-release close
Claude: Generating changelog... done.
        Version bump 1.2.0 -> 1.3.0? [Y] ... done.
        Create tag v1.3.0? [Y] ... done.

        Release REL-002 complete (v1.3.0).
        - Changelog written to CHANGELOG.md
        - Version updated in package.json
        - Tag v1.3.0 created
        - 3 CRs marked as released
        - Metrics updated (deploy frequency, lead time)
```

### 场景 2：部署后回滚

```
You:    /pace-release
Claude: REL-002 (v1.3.0) is deployed. Start verification? [Y/n/problem]

You:    problem
Claude: What happened?

You:    Payment processing is failing for international orders
Claude: Recording rollback for REL-002.
        Reason: Payment processing failure (international orders).
        Status: rolled_back.

        Create a hotfix CR for this issue? [Y/n]

You:    Y
Claude: CR-006 created (hotfix, linked to REL-002).
        After fixing, create a new release with /pace-release create.
```

## 与其他命令的集成

| 命令 | 集成点 |
|------|--------|
| `/pace-dev` | CR 通过开发流水线达到 `merged` 状态，成为发布候选项 |
| `/pace-test` | `create` 通过 `/pace-test report` 自动生成 Release 级测试报告 |
| `/pace-feedback` | `verify` 中的问题触发通过反馈流创建 defect CR |
| `/pace-retro` | `close` 更新 dashboard.md 的 DORA 指标（部署频率、前置时间、变更失败率） |
| `/pace-sync` | 未来集成（Phase 19），用于外部平台发布状态同步 |

## 相关资源

- [SKILL.md](../../skills/pace-release/SKILL.md) -- Skill 入口点和路由表
- [release-procedures-common.md](../../skills/pace-release/release-procedures-common.md) -- 共享规则（版本推断 SSOT、发布规则、集成规则）
- [release-procedures-wizard.md](../../skills/pace-release/release-procedures-wizard.md) -- 引导向导（无参数流程）
- [release-procedures-create.md](../../skills/pace-release/release-procedures-create.md) -- 创建流程（CR 收集、版本建议）
- [release-procedures-create-enhanced.md](../../skills/pace-release/release-procedures-create-enhanced.md) -- 创建增强（依赖检测、就绪检查、Gate 4）
- [release-procedures-deploy.md](../../skills/pace-release/release-procedures-deploy.md) -- 部署流程（环境晋升）
- [release-procedures-verify.md](../../skills/pace-release/release-procedures-verify.md) -- 验证流程（健康检查）
- [release-procedures-close.md](../../skills/pace-release/release-procedures-close.md) -- 关闭/完成流程（8 步链）
- [release-procedures-changelog.md](../../skills/pace-release/release-procedures-changelog.md) -- Changelog 生成
- [release-procedures-version.md](../../skills/pace-release/release-procedures-version.md) -- 版本号升级
- [release-procedures-tag.md](../../skills/pace-release/release-procedures-tag.md) -- Git 标签和 GitHub Release
- [release-procedures-rollback.md](../../skills/pace-release/release-procedures-rollback.md) -- 回滚流程（候选项预填充）
- [release-procedures-notes.md](../../skills/pace-release/release-procedures-notes.md) -- Release Notes（角色视角）
- [release-procedures-branch.md](../../skills/pace-release/release-procedures-branch.md) -- 分支管理
- [release-procedures-scheduling.md](../../skills/pace-release/release-procedures-scheduling.md) -- 发布调度
- [release-procedures-status.md](../../skills/pace-release/release-procedures-status.md) -- 状态和历史
- [integrations-format.md](../../knowledge/_schema/integration/integrations-format.md) -- 集成配置 Schema
- [devpace-rules.md](../../rules/devpace-rules.md) -- 运行时行为规则
