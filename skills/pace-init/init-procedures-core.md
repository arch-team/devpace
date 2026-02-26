# 初始化核心规程

> **职责**：初始化和迁移的核心执行规则。覆盖生命周期检测、最小初始化、CLAUDE.md 合并、校验、引导、迁移、质量检查和 Monorepo 感知。

## §0 速查卡片

- **本文件**：核心规程——生命周期检测、Git 策略检测、最小初始化、CLAUDE.md 合并、校验、引导、迁移、质量检查引导、Monorepo
- **init-procedures-checks.md**：工具链检测参考数据——生态系统精准检测表、默认检查项建议、检查项格式
- **init-procedures-full.md**：`full` 模式专用——环境探测、分阶段引导、发布配置收集
- **init-procedures-from.md**：`--from` / `--import-insights` 专用——文档解析、经验导入
- **init-procedures-verify.md**：`--verify` 健康检查
- **init-procedures-reset.md**：`--reset` 重置
- **init-procedures-dryrun.md**：`--dry-run` 预览
- **init-procedures-template.md**：`--export-template` / `--from-template` 模板管理

## §1 项目生命周期检测

### 信号检测

通过以下信号组合判定项目生命周期阶段（无需用户告知）：

| 信号 | 检测方式 | 阶段指向 |
|------|---------|---------|
| git commit 数量 | `git rev-list --count HEAD 2>/dev/null` | 0-5 → 新项目, 5-100 → 开发中, 100+ → 成熟 |
| git tags 存在 | `git tag --list 2>/dev/null` | 有版本标签（vX.Y.Z / X.Y.Z）→ 已发布 |
| CHANGELOG.md | 文件存在性检测 | 存在 → 已发布或接近发布 |
| 未合并分支数 | `git branch --no-merged main 2>/dev/null \| wc -l` | >0 → 有进行中工作 |
| 部署配置 | `fly.toml` / `app.yaml` / `serverless.yml` / `k8s/` / `terraform/` / `Procfile` | 存在 → 已发布或准备发布 |
| 源文件数量 | 按主要语言后缀统计（.js/.ts/.py/.go/.rs/.java） | <10 → 新项目, 10-100 → 开发中, 100+ → 成熟 |

### 阶段判定逻辑

按优先级从高到低判定：

1. **阶段 C（已发布）**：有版本 tags（匹配 `v*` 或 `[0-9]*.[0-9]*` 模式）**或** CHANGELOG.md 存在 **或** 有部署配置文件
2. **阶段 B（开发中）**：不满足阶段 C **且**（commit 数 > 5 **或** 有未合并分支 **或** 源文件数 ≥ 10）
3. **阶段 A（新项目）**：不满足阶段 C 和 B（commit ≤ 5 且无 tags 且源文件 < 10）

**非 git 仓库**：无 `.git/` → 默认阶段 A。

**判定结果输出**：用一句话交代，不暴露阶段标签。示例：
- 阶段 A："这是一个全新项目，采用极简初始化。"
- 阶段 B："检测到已有 47 次提交和 3 条活跃分支，已识别在研工作。"
- 阶段 C："检测到已有 47 次提交和 3 个版本标签的项目，已自动配置版本管理和发布追踪。"

### 阶段 A：新项目策略

**核心原则**：极简启动，零提问优先。

**项目名称自动检测**（按优先级尝试）：

1. `package.json` → `name` 字段
2. `pyproject.toml` → `[project].name`
3. `go.mod` → `module` 路径最后一段
4. `Cargo.toml` → `[package].name`
5. git remote → `git remote get-url origin` 提取仓库名
6. 当前目录名

**项目描述自动检测**（按优先级尝试）：

1. `package.json` → `description` 字段
2. `pyproject.toml` → `[project].description`
3. `README.md` → 第一段非标题、非徽章文本（限 100 字符）

**信息收集决策**：

- 两项均可推断 → **直接生成，仅输出确认摘要**，不提问
- 仅缺一项 → 只问缺失项
- 两项均缺 → 依次询问（先名称后描述）

**state.md 模式**：简单（5-8 行），使用标准模板。

**引导语**："试试说'帮我实现 XXX'，devpace 会自动开始追踪。"

### 阶段 B：开发中项目策略

在阶段 A 基础上增加以下检测和预填充：

1. **目录结构推断功能模块**：
   - 扫描 `src/` 一级子目录（如 `auth/`、`billing/`、`api/`）
   - 每个子目录作为一个 PF 候选写入 project.md 价值功能树
   - 标注 `<!-- source: claude, dir-structure -->`
   - 无 `src/` 目录 → 跳过此步

2. **在研工作识别**：
   - `git branch --no-merged main 2>/dev/null | head -5` 获取未合并分支列表
   - 输出候选列表供用户确认
   - 用户确认后为每个分支在 state.md "当前工作" section 添加条目
   - 不自动创建 CR 文件（用户可通过 /pace-dev 逐一处理）

3. **README 信息提取**：
   - Features / 功能 section → PF 候选
   - Non-Goals / 不做 / Out of Scope section → project.md "范围: 不做"
   - 仅在 README.md 存在且有结构化内容时执行

4. **Git 策略检测**：
   - 从 `--full` 专属提升为阶段 B 默认行为
   - 按上方"Git 策略检测"规则执行
   - 结果写入 context.md "开发流程" section

5. **state.md 模式**：中等（10-12 行），含当前工作候选

### 阶段 C：已发布项目策略

在阶段 B 基础上增加以下自动配置：

1. **版本管理自动配置**：
   - 从 git tags 推断 tag 格式（`vX.Y.Z` 或 `X.Y.Z`）+ 当前版本号（最新 tag）
   - 从 `package.json` / `pyproject.toml` / `Cargo.toml` 推断版本文件路径
   - 直接写入 `integrations/config.md` 版本管理 section，不提问

2. **发布分支自动识别**：
   - `git branch -a | grep -E 'release/|hotfix/'` 检测分支模式
   - 存在 → 自动配置 integrations/config.md + 标注 workflow.md hotfix 路径可用

3. **环境列表推断**：
   - 从 `.env.staging`、`.env.production` 等文件名 → 推断环境列表
   - 从部署配置文件内容（fly.toml 的 `[env]`、k8s manifest 的 namespace 等）→ 补充
   - 写入 integrations/config.md 环境 section

4. **发布历史种子数据**：
   - `git tag --sort=-version:refname | head -5` 获取最近 5 个版本 tag
   - 配合 `git log --format="%ai" <tag> -1` 获取每个 tag 的日期
   - 写入 metrics/dashboard.md DORA 基线（标注 `<!-- source: claude, git-history -->`）
   - 目录不存在则自动创建

5. **CHANGELOG 解析**（CHANGELOG.md 存在时）：
   - 提取最近版本的功能/修复条目
   - 作为 BR/PF 种子展示给用户确认
   - 用户确认后写入 project.md

6. **健康检查端点探测**：
   - 搜索源代码中的 `/health`、`/ping`、`/readyz` 路由定义
   - 找到 → 建议作为发布验证命令写入 checks.md

7. **pace-sync 推荐引导**：
   - 阶段 C 将同步提议从"可选"提升为"推荐"
   - 措辞调整："已发布项目通常需要外部同步，建议运行 `/pace-sync setup` 配置。"

8. **state.md 模式**：复杂（13-15 行），含版本信息和发布状态

### 通用增强

- `--interactive` 标志：强制对话模式，逐项确认所有自动推断的信息（覆盖零提问行为）
- 判定结果在输出中用一句话交代（不暴露阶段标签）
- 用户可在输出后说"调整一下"进入交互修改

### Git 策略检测

阶段 B/C 默认执行。从 Git 分支模式推断分支策略：

```
git branch -a --list | head -20
```

| 分支模式 | 推断策略 |
|---------|---------|
| 仅 `main`（或 `master`）+ 特性分支 | trunk-based |
| `main` + `develop` + `release/*` + `feature/*` | gitflow |
| `main` + `staging` + `production` | 环境分支 |
| 无法判断 | 询问用户或标注"待定" |

**写入位置**：context.md 的"开发流程"section。

## §2 最小初始化（默认）

### 生成规则

1. **state.md**：使用模板，替换占位符：
   - `{{OBJECTIVE}}` → 用户提供或自动检测的一句话描述
   - `{{MOS_SUMMARY}}` → `（待定义）`
   - `{{NEXT_ACTION}}` → 按生命周期阶段选择引导语
2. **project.md**：使用模板，替换 `{{PROJECT_NAME}}` 和 `{{PROJECT_DESCRIPTION}}`
   - 阶段 B/C：在价值功能树 section 预填充检测到的 PF 候选
3. **backlog/**：创建空目录
4. **rules/workflow.md**：从 Plugin 模板复制
5. **rules/checks.md**：从项目工具链精准检测生成（见 §9 质量检查引导）
6. **context.md**（按阈值生成）：扫描项目代码库检测技术栈和编码约定：
   - 检测 package.json / pyproject.toml / go.mod / Cargo.toml 确定技术栈
   - 检测 .eslintrc / .prettierrc / biome.json / ruff.toml / .editorconfig 提取编码规范
   - 检测 tsconfig.json / Dockerfile / docker-compose.yml 推断架构约束
   - 检测 Makefile / justfile / pnpm-workspace.yaml 识别构建工具和 monorepo
   - 从代码文件采样（3-5 个主要文件）提取命名风格和代码模式
   - 仅记录已确认的约定（检测到的），不猜测未发现的
   - 按 context-format.md "50% 猜错"规则，只记录 Claude 可能猜错的约定
   - **阈值**：检测到 ≥ 1 条非显而易见的约定即创建（有一个约定就值得记录）
   - **阶段 B/C**：Git 策略检测结果也写入 context.md
7. **CI/CD 自动检测**（静默，无需用户确认）：
   - 按 `integrations-format.md` 的"CI 自动检测映射表"扫描项目根目录
   - 检测到 CI 配置文件 → 自动创建 `integrations/config.md`（仅 CI/CD section），来源标记 `auto-detect`
   - 检测到的检查命令写入"检查命令"字段
   - 未检测到 CI 配置 → 不创建 integrations/，不提示
8. **阶段 C 额外生成**：integrations/config.md（版本管理 + 环境）、metrics/dashboard.md（DORA 基线）

### 同步配置提议

检测到 git remote 时，按生命周期阶段调整提议强度：

1. 检查 `git remote get-url origin` 是否可用
2. 可用时：
   - **阶段 A/B**（可选）：自然语言提议："检测到 GitHub 仓库 {owner}/{repo}，是否要配置外部同步？"
   - **阶段 C**（推荐）：措辞调整："已发布项目通常需要外部同步，建议运行 `/pace-sync setup` 配置 CR 与 GitHub Issue 的同步。"
   - 用户同意 → 自动执行 `/pace-sync setup` 流程（复用 sync-procedures §2）
   - 用户拒绝或忽略 → 静默跳过
3. 不可用 → 静默跳过

**规则**：仅提议，不阻断初始化流程。提议不超过 2 句话。后续可随时通过 `/pace-sync setup` 手动配置。

### 跨项目经验导入

跨项目经验导入（`--import-insights`）的处理规则见 `init-procedures-from.md` §2。已有 `.devpace/` 的项目也可独立使用此参数（不重新初始化，仅导入经验）。

### .gitignore 建议

初始化完成后提示：
> "建议在 .gitignore 中添加 `.devpace/`，除非你想版本控制项目状态文件。"

如果项目根目录已有 `.gitignore` 且未包含 `.devpace/`，询问是否自动添加。

## §3 CLAUDE.md 智能合并

### 合并策略

使用 `<!-- devpace-start -->` / `<!-- devpace-end -->` 标记实现幂等注入：

1. **检测现有 CLAUDE.md**：读取项目根目录 `CLAUDE.md`
2. **搜索标记**：查找 `<!-- devpace-start -->` 和 `<!-- devpace-end -->`
3. **按情况处理**：
   - **已有标记** → 替换标记区间内的内容（保留标记本身），实现幂等更新
   - **文件存在但无标记** → 在文件末尾追加空行 + `<!-- devpace-start -->` + devpace section + `<!-- devpace-end -->`
   - **文件不存在** → 创建新文件，内容为 `<!-- devpace-start -->` + devpace section + `<!-- devpace-end -->`

### 模板内容

使用 `templates/claude-md-devpace.md` 模板，模板内容已包含 `<!-- devpace-start -->` 和 `<!-- devpace-end -->` 标记。替换模板中的占位符（`{{PROJECT_NAME}}`、`{{PROJECT_POSITIONING}}` 等）后注入。

### 安全规则

- 不修改标记区间外的 CLAUDE.md 内容
- 标记区间内的内容视为 devpace 管理区域，可覆盖
- 用户手动编辑标记区间内的内容会在下次 init 时被覆盖（设计如此，CLAUDE.md devpace section 由 devpace 管理）

## §4 初始化后自动校验

初始化完成后自动执行轻量校验：

1. **文件存在性**：校验所有生成文件存在且非空
2. **state.md 合规**：校验行数在阶段对应范围内（A: 5-8, B: 10-12, C: 13-15），包含必需 section（目标、当前工作、下一步、版本标记）
3. **project.md 合规**：校验包含项目名和描述，价值功能树 section 存在（可为空桩）
4. **CLAUDE.md 注入**：校验 `<!-- devpace-start -->` 和 `<!-- devpace-end -->` 标记存在
5. **checks.md 最低标准**：至少含 2 条检查项（1 条命令检查 + 1 条意图检查）

**结果处理**：
- 全部通过 → 输出一行确认："✅ 所有文件校验通过"
- 有问题 → 尝试自动修复（补缺失 section、修复格式），修复后重新校验；无法自动修复则提示用户

## §5 情境化引导规则

### 按生命周期阶段

| 阶段 | 引导语 | 具体 prompt 示例 |
|------|--------|-----------------|
| 阶段 A | "试试说'帮我实现 XXX'，我会自动创建第一个 CR 开始工作" | "帮我实现用户登录功能" |
| 阶段 B | "试试说'帮我修复 XXX'或'帮我添加 XXX'，devpace 会自动追踪变更" | "帮我修复首页加载慢的问题" |
| 阶段 C | "试试说'准备发布 vX.Y.Z'或'线上有个紧急 bug'" | "准备发布 v2.1.0" |

### 按初始化模式

| 模式 | 额外引导 |
|------|---------|
| `--from` | "已从文档生成 N 个产品功能，试试 `/pace-status tree` 查看全景" |
| `full` 业务阶段跳过 | "随时可以 `/pace-retro` 回顾并定义业务目标" |

### 通用速查

初始化完成后始终附加常用命令速查（3-5 条）：

```
常用命令：
- 开始工作："帮我实现/修复/添加 XXX"
- 查看进度：/pace-status
- 管理变更：/pace-change
- 回顾总结：/pace-retro
```

### git remote 检测

检测到 `git remote get-url origin` 返回 GitHub URL → 追加："运行 `/pace-sync setup` 可将 CR 同步到 GitHub Issues。"

## §6 按需目录创建

以下目录和文件在首次使用对应功能时由 Claude 自动创建，不在 init 时预创建：

| 目录/文件 | 创建时机 | 创建者 |
|-----------|---------|--------|
| `iterations/current.md` | 首次 `/pace-plan` | pace-plan Skill |
| `metrics/dashboard.md` | 首次 `/pace-retro`（阶段 A/B）或 init（阶段 C） | pace-retro Skill / pace-init |
| `metrics/insights.md` | 首次 CR merged 后 pace-learn 执行 | pace-learn（自动） |
| `releases/` | 首次 `/pace-release create` | pace-release Skill |
| `integrations/config.md` | CI 自动检测（最小 init）或 init 阶段 C 或首次配置集成 | pace-init / 手动 |
| `.devpace/context.md` | `/pace-init` 或首次技术约定讨论 | init-procedures / Claude 自动 |

Claude 在需要写入上述路径时，先检查目录是否存在，不存在则自动创建（mkdir -p 语义），不报错、不提示。

## §7 延后收集时机

最小初始化时 project.md 为桩状态。以下时机触发内容填充：

1. **首个 CR 创建时**：Claude 根据用户描述自动推断关联的 PF，在 project.md 的价值功能树中创建初始结构（一个推断的 BR + PF + CR 关联），同时为 PF 行追加括号内用户故事（从用户描述提炼）
2. **首次 `/pace-retro`**：如果 project.md 仍无业务目标，引导用户定义 OBJ 和 MoS
3. **用户主动讨论业务目标时**：Claude 引导定义 OBJ 和 MoS 并回填 project.md
4. **首次 `/pace-change` 时**：如果 project.md 的"范围"section 仍为桩状态，引导用户定义"做什么/不做什么"并回填
5. **用户主动讨论项目范围时**：Claude 引导定义范围边界并回填 project.md 的"范围"section
6. **技术/产品讨论中明确偏好时**：Claude 将确认的技术或产品决策追加到 project.md 的"项目原则"section（标注来源和日期）
7. **技术约定讨论时**：用户讨论编码规范、技术选型或架构约束时，Claude 将确认的约定追加到 context.md 对应 section

## §8 迁移框架

### 版本检测

检查 `state.md` 末尾的 `<!-- devpace-version: X.Y.Z -->` 标记：

- 无标记 → 视为 v1.2.0（标记引入前的版本），触发迁移
- 标记版本 < 当前版本 → 触发增量迁移
- 标记版本 = 当前版本 → 不迁移

### 增量迁移规范

每次版本升级在本章节追加 `vOLD → vNEW` 增量迁移段。迁移前提示用户确认，完成后输出变更摘要。

**通用迁移安全规则**：

- **只添加不删除**：迁移不删除任何现有文件或字段
- **默认值兼容**：新字段全部可选，不填写时使用默认值
- **回滚方案**：迁移前自动 `git commit`（如有未提交变更），迁移后可通过 `git revert` 回滚
- **幂等性**：同一迁移重复执行不产生副作用

### v1.2.0 → v1.5.0 迁移

**触发条件**：`devpace-version` 为 1.2.0（或缺失标记）。

**迁移步骤**：

1. 通知用户："检测到 v1.2.0 项目，建议升级到 v1.5.0 以支持外部同步、增强的质量门和生命周期感知。"
2. 更新版本标记：`<!-- devpace-version: 1.5.0 -->`
3. 更新 rules/workflow.md（从 Plugin 模板覆盖，新增同步相关状态）
4. 输出摘要："升级完成 v1.2.0 → v1.5.0。变更：版本标记更新、工作流规则更新。现有数据无损。"

<!-- GROWTH-TRIGGER: 当本章节超过 80 行时，提取为 init-procedures-migration.md -->

## §9 质量检查引导

根据项目工具链生成 checks.md。检测规则和命令映射表见 `init-procedures-checks.md`（权威源）。
最小初始化时自动生成不询问；`--full` 模式时引导用户确认和补充。
生成的 checks.md 须符合 `knowledge/_schema/checks-format.md` 格式契约。

## §10 Monorepo 感知初始化

### 信号检测

| 文件 | Monorepo 工具 |
|------|-------------|
| `pnpm-workspace.yaml` | pnpm workspace |
| `nx.json` | Nx |
| `turbo.json` | Turborepo |
| `lerna.json` | Lerna |
| `rush.json` | Rush |

### 组织方式选择

检测到 monorepo 信号时，使用 AskUserQuestion 询问组织方式：

**A) 根目录单一 .devpace/（推荐小型 monorepo，<5 个子包）**：
- 标准初始化流程
- context.md 记录 monorepo 结构和子包列表
- PF 树按子包组织

**B) 根共享 + 子包独立追踪（大型 monorepo，≥5 个子包）**：
- 根 `.devpace/`：rules/（共享规则）+ context.md（全局约定）
- 子包 `.devpace/`：state.md + project.md + backlog/（独立追踪）
- 子包的 rules/ 继承根目录（不重复创建）

### 子包发现

- 从 monorepo 配置文件读取 workspace 列表
- 验证子包目录存在
- 为每个子包生成独立的 state.md 和 project.md
