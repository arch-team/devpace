# 初始化核心规程

> **职责**：初始化核心执行规则。覆盖生命周期检测、最小初始化、CLAUDE.md 合并、校验、引导、质量检查引导。

## §0 速查

本文件为初始化核心规程，覆盖生命周期检测（§1）、最小初始化（§2）、CLAUDE.md 合并（§3）、校验（§4）、引导（§5）、质量检查引导（§9）。子命令规程由 SKILL.md 路由表指定加载。

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

**state.md 模式**：简单，使用标准模板。内容行数目标 ~6 行（HTML 注释和空行不计入）。

**引导语**："试试说'帮我实现 XXX'，devpace 会自动开始追踪。"

### 阶段 B：开发中项目策略

在阶段 A 基础上增加以下检测和预填充：

1. **目录结构推断功能模块**：
   - 扫描 `src/` 一级子目录（如 `auth/`、`billing/`、`api/`）
   - 每个子目录作为一个 PF 候选写入 project.md 价值功能树
   - **PF 候选命名规则**：以目录名为基础生成可读的中文功能名（如 `api/` → "API 路由"、`auth/` → "用户认证"、`utils/` → "工具库"）；通用目录名（utils、common、shared、helpers）保留简短翻译即可
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

5. **state.md 模式**：中等，含当前工作候选。内容行数目标 ~10 行（HTML 注释和空行不计入）

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

8. **state.md 模式**：详细，含版本信息和发布状态。内容行数目标 ~13 行（HTML 注释和空行不计入）

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

> **按需创建原则**：init 不预创建 iterations/、metrics/insights.md、releases/ 目录。这些目录由对应 Skill 在首次使用时自动创建（mkdir -p 语义）。

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

初始化完成后按情况处理：

- **无 .gitignore 文件** → 在确认摘要中建议："建议创建 .gitignore 并添加 `.devpace/`，除非你想版本控制项目状态文件。"（不自动创建）
- **已有 .gitignore 且未包含 `.devpace/`** → 询问是否自动添加 `.devpace/` 条目
- **已有 .gitignore 且已包含 `.devpace/`** → 静默跳过

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
2. **state.md 合规**：校验内容行数（不含 HTML 注释和空行）在阶段对应范围内（A: ~6, B: ~10, C: ~13，允许 ±2 行浮动），包含必需 section（目标、当前工作、下一步、版本标记）
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

## §9 质量检查引导

根据项目工具链生成 checks.md。检测规则和命令映射表见 `init-procedures-checks.md`（权威源）。
最小初始化时自动生成不询问；`--full` 模式时引导用户确认和补充。
生成的 checks.md 须符合 `knowledge/_schema/checks-format.md` 格式契约。
