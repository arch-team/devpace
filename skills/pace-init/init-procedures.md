# 初始化执行规程

> **职责**：初始化和迁移的详细执行规则。/pace-init 触发后，Claude 按需读取本文件对应章节。

## §0 速查卡片

- **项目生命周期检测**：信号组合判定阶段 A（新项目）/ B（开发中）/ C（已发布），按阶段适配初始化策略
- **最小初始化（默认）**：生命周期感知生成 state.md/project.md/backlog/rules + CI/CD 自动检测
- **CLAUDE.md 智能合并**：devpace-start/end 标记实现幂等注入
- **按需目录创建**：iterations/releases/insights 等目录在首次使用时创建
- **延后收集时机**：功能规格/架构约束等在具体工作阶段按需采集
- **迁移框架**：版本标记检测 + 增量迁移段（v1.5.0 起生效）
- **环境探测（--full 模式）**：完整项目扫描——技术栈/架构/CI/CD/发布配置
- **质量检查引导**：按项目工具链精准检测生成 checks.md
- **子命令**：--verify 健康检查 / --reset 重置 / --dry-run 预览 / --export-template 模板管理

## 项目生命周期检测

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
   - 按"环境探测"章节的 Git 策略检测规则执行
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
   - 阶段 C 将 Step 8 的同步提议从"可选"提升为"推荐"
   - 措辞调整："已发布项目通常需要外部同步，建议运行 `/pace-sync setup` 配置。"

8. **state.md 模式**：复杂（13-15 行），含版本信息和发布状态

### 通用增强

- `--interactive` 标志：强制对话模式，逐项确认所有自动推断的信息（覆盖零提问行为）
- 判定结果在输出中用一句话交代（不暴露阶段标签）
- 用户可在输出后说"调整一下"进入交互修改

## 最小初始化（默认）

### 生成规则

1. **state.md**：使用模板，替换占位符：
   - `{{OBJECTIVE}}` → 用户提供或自动检测的一句话描述
   - `{{MOS_SUMMARY}}` → `（待定义）`
   - `{{NEXT_ACTION}}` → 按生命周期阶段选择引导语
2. **project.md**：使用模板，替换 `{{PROJECT_NAME}}` 和 `{{PROJECT_DESCRIPTION}}`
   - 阶段 B/C：在价值功能树 section 预填充检测到的 PF 候选
3. **backlog/**：创建空目录
4. **rules/workflow.md**：从 Plugin 模板复制
5. **rules/checks.md**：从项目工具链精准检测生成（见"质量检查引导"章节）
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

### Step 8：同步配置提议

检测到 git remote 时，按生命周期阶段调整提议强度：

1. 检查 `git remote get-url origin` 是否可用
2. 可用时：
   - **阶段 A/B**（可选）：自然语言提议："检测到 GitHub 仓库 {owner}/{repo}，是否要配置外部同步？"
   - **阶段 C**（推荐）：措辞调整："已发布项目通常需要外部同步，建议运行 `/pace-sync setup` 配置 CR 与 GitHub Issue 的同步。"
   - 用户同意 → 自动执行 `/pace-sync setup` 流程（复用 sync-procedures §2）
   - 用户拒绝或忽略 → 静默跳过
3. 不可用 → 静默跳过

**规则**：仅提议，不阻断初始化流程。提议不超过 2 句话。后续可随时通过 `/pace-sync setup` 手动配置。

### 跨项目经验导入（--import-insights）

当用户执行 `/pace-init --import-insights <路径>` 时，在初始化完成后执行经验导入：

1. 读取指定路径的导出文件
2. 校验格式（应符合 insights-format.md 导出文件格式）
3. 按导入规则处理每个条目：
   - 跳过偏好（preference）类型条目
   - 置信度 × 0.8 降级
   - 验证次数重置为 0
   - 追加"导入日期"字段
4. 与已有 insights.md 去重（同标题保留高置信度版本）
5. 写入 `.devpace/metrics/insights.md`（目录不存在则创建）
6. 输出摘要：`"已导入 N 条经验（来自 [项目名]），置信度已降级（×0.8），需在本项目中重新验证。跳过 M 条偏好类型条目。"`

已有 .devpace/ 的项目也可独立使用此参数（不重新初始化，仅导入经验）。

### .gitignore 建议

初始化完成后提示：
> "建议在 .gitignore 中添加 `.devpace/`，除非你想版本控制项目状态文件。"

如果项目根目录已有 `.gitignore` 且未包含 `.devpace/`，询问是否自动添加。

## CLAUDE.md 智能合并

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

## 初始化后自动校验

初始化完成后（Step 4 的一部分），自动执行轻量校验：

1. **文件存在性**：校验所有生成文件存在且非空
2. **state.md 合规**：校验行数在阶段对应范围内（A: 5-8, B: 10-12, C: 13-15），包含必需 section（目标、当前工作、下一步、版本标记）
3. **project.md 合规**：校验包含项目名和描述，价值功能树 section 存在（可为空桩）
4. **CLAUDE.md 注入**：校验 `<!-- devpace-start -->` 和 `<!-- devpace-end -->` 标记存在
5. **checks.md 最低标准**：至少含 2 条检查项（1 条命令检查 + 1 条意图检查）

**结果处理**：
- 全部通过 → 输出一行确认："✅ 所有文件校验通过"
- 有问题 → 尝试自动修复（补缺失 section、修复格式），修复后重新校验；无法自动修复则提示用户

## 情境化引导规则

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

## 按需目录创建

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

## 延后收集时机

最小初始化时 project.md 为桩状态。以下时机触发内容填充：

1. **首个 CR 创建时**：Claude 根据用户描述自动推断关联的 PF，在 project.md 的价值功能树中创建初始结构（一个推断的 BR + PF + CR 关联），同时为 PF 行追加括号内用户故事（从用户描述提炼）
2. **首次 `/pace-retro`**：如果 project.md 仍无业务目标，引导用户定义 OBJ 和 MoS
3. **用户主动讨论业务目标时**：Claude 引导定义 OBJ 和 MoS 并回填 project.md
4. **首次 `/pace-change` 时**：如果 project.md 的"范围"section 仍为桩状态，引导用户定义"做什么/不做什么"并回填
5. **用户主动讨论项目范围时**：Claude 引导定义范围边界并回填 project.md 的"范围"section
6. **技术/产品讨论中明确偏好时**：Claude 将确认的技术或产品决策追加到 project.md 的"项目原则"section（标注来源和日期）
7. **技术约定讨论时**：用户讨论编码规范、技术选型或架构约束时，Claude 将确认的约定追加到 context.md 对应 section

## 迁移框架

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

## 环境探测（`--full` 模式增强）

当 `/pace-init full` 执行时，在信息收集（Step 1）和生成目录（Step 2）之间，自动执行环境探测。探测结果用于预填 `context.md` 和 `integrations/config.md`，减少用户手动配置。

### 探测步骤

#### 1. 项目类型检测

扫描项目根目录的配置文件，识别技术栈和项目架构：

| 探测文件 | 推断信息 | 写入位置 |
|---------|---------|---------|
| `package.json` | 语言=JS/TS + 框架（react/vue/angular/next/express 从 dependencies 推断） | context.md 技术栈 |
| `pyproject.toml` / `setup.py` | 语言=Python + 框架（django/flask/fastapi 从依赖推断） | context.md 技术栈 |
| `go.mod` | 语言=Go + module 名 | context.md 技术栈 |
| `Cargo.toml` | 语言=Rust | context.md 技术栈 |
| `tsconfig.json` | TypeScript 启用 + strict 模式等配置 | context.md 技术栈 |
| `Dockerfile` / `docker-compose.yml` | 容器化部署 | context.md 架构约束 |
| `Makefile` / `justfile` | 构建系统 | context.md 构建工具 |

多技术栈项目（monorepo 等）→ 全部记录。无可识别配置文件 → 标注"待定"。

#### 2. MCP 感知

检查 Claude Code 环境中已可用的 MCP Server，预填集成建议：

| 检查路径 | 推断信息 | 写入位置 |
|---------|---------|---------|
| `.mcp.json`（项目级） | 已配置的 MCP Server 列表 | integrations/config.md MCP section |
| 全局 MCP 配置（Claude Code 用户设置） | 全局可用的 MCP Server | integrations/config.md MCP section |

**预填逻辑**：
- 检测到 Playwright MCP → 标注"可用于 E2E 测试和浏览器验收"
- 检测到 Tavily MCP → 标注"可用于研究和文档查询"
- 无 MCP 配置 → 跳过此 section

#### 3. CI/CD 检测

扫描项目中的 CI/CD 配置文件，自动识别部署流水线：

| 探测文件/目录 | CI/CD 工具 | 推断信息 |
|-------------|-----------|---------|
| `.github/workflows/*.yml` | GitHub Actions | 工作流名称、触发事件（push/PR/tag） |
| `.gitlab-ci.yml` | GitLab CI | 阶段定义 |
| `Jenkinsfile` | Jenkins | Pipeline 存在 |
| `.circleci/config.yml` | CircleCI | 配置存在 |
| `bitbucket-pipelines.yml` | Bitbucket Pipelines | 配置存在 |
| `vercel.json` / `.vercel/` | Vercel | 部署平台=Vercel |
| `netlify.toml` | Netlify | 部署平台=Netlify |

**预填逻辑**：提取工具名称和触发方式 → 写入 `integrations/config.md` CI/CD section。无 CI/CD 配置 → 跳过。

#### 4. Git 策略检测

从 Git 分支模式推断分支策略：

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

### 探测输出

探测完成后，输出探测摘要给用户确认：

```
环境探测完成：
- 技术栈：[语言] + [框架]（从 [配置文件] 检测）
- CI/CD：[工具名]（[触发方式]）
- 分支策略：[策略名]
- MCP：[N] 个可用 Server
以上信息已预填到 context.md 和 integrations/config.md，你可以修改或补充。
```

### 探测安全规则

- **只检测不猜测**：仅记录从配置文件中确认的信息，不推测缺失的配置
- **不执行命令**：除 `git branch` 外不执行项目的构建/测试命令
- **用户确认**：探测结果在完整初始化流程中展示给用户确认，不自动写入
- **最小初始化不触发**：环境探测仅在 `--full` 模式中执行（但 Git 策略检测在阶段 B/C 默认执行）

## full 模式分阶段引导

### 阶段 1：基础（必须）

执行生命周期检测 + 信息收集 + 生成 .devpace/（同最小初始化 + 环境探测）。完成后立即可用。

### 阶段 2：业务（可选）

使用 AskUserQuestion 询问："要现在定义业务目标和成效指标吗？可稍后 /pace-retro 补充。"

用户选择"现在定义"→ 引导收集：
1. 业务目标（OBJ）：项目的核心价值和成功标准
2. 成效指标（MoS）：可衡量的指标列表
3. 业务需求（BR）：高层需求分解

用户选择"稍后再说"→ 跳过，project.md 保持桩状态。

### 阶段 3：发布配置（可选）

使用 AskUserQuestion 询问："检测到 [CI 工具]，要配置发布流程吗？可稍后编辑 integrations/config.md。"

用户选择"现在配置"→ 引导收集发布配置（见"发布配置收集"章节）。
用户选择"稍后再说"→ 跳过。

### 阶段 4：外部同步（可选）

使用 AskUserQuestion 询问："检测到 GitHub 仓库，要配置外部同步吗？可稍后 /pace-sync setup。"

用户选择"现在配置"→ 执行 `/pace-sync setup`。
用户选择"稍后再说"→ 跳过。

### 提前退出

用户在任何阶段可说"够了"→ 跳过剩余阶段，使用已收集的信息完成初始化。

## 发布配置收集

### 有发布流程时

额外收集信息：
1. **环境列表**：如 staging、production（写入 `integrations/config.md`）
2. **CI/CD 工具**（可选）：如 GitHub Actions、Jenkins、GitLab CI
3. **发布审批**：自动（CI 通过即部署）/ 手动确认（需人类审批）

生成 `.devpace/integrations/config.md`：

```markdown
# 集成配置

## 环境

| 环境 | 用途 | URL |
|------|------|-----|
| staging | 预发布验证 | [URL] |
| production | 正式环境 | [URL] |

## CI/CD

- **工具**：[工具名称]
- **触发方式**：[push/manual/tag]

## 发布审批

- **模式**：[auto/manual]
```

### 无发布流程时

- 跳过发布配置
- `releases/` 和 `integrations/` 目录不创建（按需创建策略）
- 相关功能（/pace-release、/pace-feedback 的 Release 追溯）降级

## 质量检查引导

### 工具链精准检测

根据项目实际使用的工具链生成 checks.md，而非按大类建议：

#### Node.js 精准检测

| 检测源 | 检测字段 | 生成命令 |
|--------|---------|---------|
| package.json devDependencies | `vitest` | `npx vitest run` |
| package.json devDependencies | `jest` | `npx jest` |
| package.json devDependencies | `mocha` | `npx mocha` |
| package.json scripts | `test` 脚本 | `npm test`（兜底，仅当无上述工具时） |
| package.json devDependencies | `@biomejs/biome` | `npx biome check .` |
| `.eslintrc*` 或 `eslint.config.*` | 文件存在 | `npx eslint .` |
| `.prettierrc*` | 文件存在 | `npx prettier --check .` |
| package.json devDependencies | `typescript` | `npx tsc --noEmit` |

#### Python 精准检测

| 检测源 | 检测字段 | 生成命令 |
|--------|---------|---------|
| pyproject.toml `[tool.pytest]` | section 存在 | `pytest` |
| pyproject.toml `[tool.ruff]` | section 存在 | `ruff check .` |
| pyproject.toml `[tool.mypy]` | section 存在 | `mypy .` |
| pyproject.toml `[tool.pyright]` | section 存在 | `pyright` |
| setup.cfg `[flake8]` | section 存在 | `flake8` |
| pyproject.toml dependencies | `bandit` | `bandit -r src/` |

#### Go 精准检测

| 检测源 | 检测字段 | 生成命令 |
|--------|---------|---------|
| go.mod | 文件存在 | `go test ./...` |
| .golangci.yml | 文件存在 | `golangci-lint run` |
| go.mod | 文件存在 | `go vet ./...` |

#### Rust 精准检测

| 检测源 | 检测字段 | 生成命令 |
|--------|---------|---------|
| Cargo.toml | 文件存在 | `cargo test` |
| Cargo.toml | 文件存在 | `cargo clippy -- -D warnings` |
| Cargo.toml | 文件存在 | `cargo audit`（如 cargo-audit 可检测） |

#### 通用规则

- 未检测到具体工具 → 保留通用占位符 `{{CHECK_COMMAND}}`
- 生成的命令必须直接可执行（不需要额外安装）
- 安全检查建议作为注释包含（`<!-- 推荐：... -->`），用户可取消注释启用
- 最小初始化时自动生成不询问；`--full` 模式时引导用户确认和补充

### 默认检查项建议

| 项目类型 | 意图检查建议 | 安全检查建议 |
|---------|-------------|-------------|
| Node.js | "所有导出函数有 JSDoc" | `npm audit --audit-level=high` |
| Python | "所有公共函数有 docstring" | `bandit -r src/` |
| Go | "所有导出函数有注释" | `gosec ./...` |
| Rust | "所有 pub 函数有文档注释" | `cargo audit` |
| 通用 | "单个函数不超过 50 行" | Claude 检查"代码中不含硬编码密钥" |

### 检查项格式

checks.md 支持两种检查类型（格式定义见 `knowledge/_schema/checks-format.md`）：

- **命令检查**：`检查方式：[bash 命令]`——exit code 判定（0=通过）
- **意图检查**：`检查方式：Claude 检查 [自然语言规则]`——Claude 阅读变更代码对照规则判定

```markdown
## 质量检查

### Gate 1：代码质量（developing → verifying）
- [ ] [检查名称]：`[命令]`
- [ ] [检查名称]：Claude 检查 [自然语言规则]

### Gate 2：集成验证（verifying → in_review）
- [ ] [检查名称]：`[命令]`
- [ ] [检查名称]：Claude 检查 [自然语言规则]

### Gate 3：人类审批（in_review → approved）
- [ ] 人类审批：Code Review 通过
```

## --from 模式增强解析

### 路径处理

- **单文件**：`/pace-init --from prd.md` → 直接读取
- **目录路径**：`/pace-init --from requirements/` → 扫描目录下所有 .md/.txt 文件，综合提取
- **多文件**：`/pace-init --from prd.md --from api-spec.md` → 依次读取，合并提取结果

### 解析规则

| 文档元素 | 映射目标 | 解析方法 |
|---------|---------|---------|
| 用户故事（As a... I want... So that...） | BR（业务需求） | 模式匹配 + 语义分析 |
| 功能列表 / Features section | PF（产品功能）树 | 层级提取 |
| API 端点列表 / OpenAPI paths | PF（按资源分组） | 结构化解析（YAML/JSON） |
| 技术需求 / Non-functional requirements | project.md "项目原则" | 语义分类 |
| 优先级标记（P0/P1/Must/Should） | CR 优先级候选 | 标签提取 |
| 时间线 / Milestones | 迭代规划候选 | 时间点提取 |

### 确认流程

1. 解析完成后展示提取结果的结构化摘要
2. 用 AskUserQuestion 让用户确认或调整
3. 确认后写入 project.md
4. 目录路径解析时，若文件过多（>10），先输出文件列表让用户筛选

### API 规格特殊处理

检测到 OpenAPI/Swagger 文件（.yaml/.json 含 `openapi` 或 `swagger` 关键词）：
- 提取 paths → 按资源（/users、/orders 等）分组为 PF
- 提取 tags → 作为 PF 分组名称
- 提取 descriptions → 作为 PF 描述

## 健康检查规程

### 触发

`/pace-init --verify [--fix]`

### 前置条件

检查 `.devpace/` 目录存在，不存在则提示"未找到 .devpace/ 目录，请先运行 /pace-init"。

### 校验清单

遍历 `.devpace/` 所有文件，按对应 Schema 逐一校验：

| 文件 | Schema | 校验内容 |
|------|--------|---------|
| state.md | state-format.md | 必需 section、版本标记 |
| project.md | project-format.md | 项目名、价值功能树 section |
| rules/workflow.md | — | 文件存在且非空 |
| rules/checks.md | checks-format.md | Gate section 存在、至少 2 条检查 |
| context.md | context-format.md | section 结构合规 |
| backlog/CR-*.md | cr-format.md | 必填字段存在 |
| iterations/*.md | iteration-format.md | section 结构合规 |
| releases/*.md | release-format.md | section 结构合规 |
| integrations/config.md | integrations-format.md | section 结构合规 |
| metrics/dashboard.md | — | 文件存在且非空 |
| metrics/insights.md | insights-format.md | 条目格式合规 |
| CLAUDE.md | — | devpace section 标记存在 |

### 输出格式

```
.devpace/ 健康检查报告：
✅ state.md — 正常
✅ project.md — 正常
⚠️ rules/checks.md — 缺少 Gate 2 section（可自动修复）
❌ backlog/CR-001.md — 缺少"意图"字段（需人工处理）
✅ CLAUDE.md — devpace section 存在

总计：N 个文件，M 正常，X 可修复，Y 需人工
```

### --fix 行为

当指定 `--fix` 时，自动修复可修复项：

- 缺失的 section → 补充空 section 模板
- 缺失的版本标记 → 补充当前版本标记
- 格式问题（多余空行、缺失分隔符）→ 规范化
- **不修改语义内容**（不改用户写的文本、不删除用户数据）

修复后重新输出报告。

## 重置规程

### 触发

`/pace-init --reset [--keep-insights]`

### 流程

1. **前置检查**：确认 `.devpace/` 存在
2. **外部关联检测**：
   - 检查 `.devpace/integrations/sync-mapping.md` 是否存在
   - 存在 → 提示："发现外部同步映射，关联的 GitHub Issues 需手动处理。"
3. **二次确认**：使用 AskUserQuestion 确认："即将删除 .devpace/ 及所有追踪数据（N 个 CR、M 个迭代记录），此操作不可逆。确认删除？"
4. **保留 insights**（如 `--keep-insights`）：
   - 备份 `.devpace/metrics/insights.md` 到临时位置
5. **删除 .devpace/**：删除整个目录
6. **清理 CLAUDE.md**：
   - 读取 CLAUDE.md，删除 `<!-- devpace-start -->` 到 `<!-- devpace-end -->` 之间的内容（含标记本身）
   - 清理可能遗留的多余空行
7. **恢复 insights**（如 `--keep-insights`）：
   - 创建 `.devpace/metrics/` 目录
   - 将备份的 insights.md 恢复
8. **完成提示**："已清除 .devpace/。可运行 /pace-init 重新初始化。"

### 安全规则

- 必须二次确认，不可静默删除
- 不删除 .devpace/ 以外的文件（除 CLAUDE.md devpace section 外）
- `--keep-insights` 保留经验数据（经验是跨项目资产）

## dry-run 规程

### 触发

`/pace-init --dry-run [其他参数]`

### 行为

执行完整的检测和规划逻辑（生命周期检测、工具链检测、信息收集等），但不写入任何文件。

### 输出格式

```
/pace-init 预览（dry-run 模式，不写入文件）：

检测结果：
- 项目阶段：[阶段描述]
- 项目名称：[名称]（来源：[package.json/目录名/...]）
- 项目描述：[描述]（来源：[...]）
- 技术栈：[语言] + [框架]
- 工具链：[测试/lint/typecheck 工具]

将创建的文件：
.devpace/
├── state.md          — 项目状态追踪（[N] 行）
├── project.md        — 项目定义和价值功能树
├── backlog/          — CR 存放目录
├── rules/
│   ├── workflow.md   — 工作流规则
│   └── checks.md     — 质量检查（[M] 条检查项）
├── context.md        — 技术约定（[K] 条约定）
└── integrations/
    └── config.md     — 集成配置（CI/CD + 版本管理）

CLAUDE.md — 将注入 devpace 研发协作 section

确认初始化？运行 `/pace-init [项目名称]` 开始。
```

## 模板导出与应用规程

### 导出（--export-template）

**前置条件**：`.devpace/` 目录存在。

**导出内容**（创建 `.devpace-template/` 目录）：

| 源文件 | 导出处理 |
|--------|---------|
| rules/workflow.md | 直接复制 |
| rules/checks.md | 移除项目特定的 bash 命令路径，保留结构和意图检查 |
| context.md | 移除项目特定的路径和名称，保留通用约定 |
| integrations/config.md | 移除项目特定的 URL 和密钥，保留结构 |

**输出**：`".devpace-template/ 已创建，包含 N 个模板文件。新项目可使用 /pace-init --from-template .devpace-template/ 应用。"`

### 应用（--from-template）

1. 读取模板目录中的文件
2. 执行正常初始化流程（生命周期检测 + 信息收集）
3. 用模板文件覆盖默认模板（workflow.md、checks.md、context.md、integrations/config.md）
4. 继续正常流程（替换占位符、生成 state.md/project.md）

## Monorepo 感知初始化

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
