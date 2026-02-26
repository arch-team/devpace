# 项目初始化（`/pace-init`）

`/pace-init` 是 devpace 的入口——它创建 `.devpace/` 目录，驱动所有其他 devpace 功能。其核心差异是**生命周期感知初始化**：不是对所有项目千篇一律地提问，而是自动检测项目处于全新、开发中还是已发布阶段，据此适配初始化行为。新项目零提问启动；成熟项目自动配置版本管理和发布追踪。

## 前置条件

| 条件 | 用途 | 是否必须 |
|------|------|:--------:|
| 项目目录 | `.devpace/` 的创建位置 | 是 |
| `git` 已初始化 | 生命周期检测依赖 git 历史信号 | 推荐 |
| 配置文件（package.json、pyproject.toml 等） | 自动检测项目名称、描述和工具链 | 可选 |

> **优雅降级**：非 git 项目默认按阶段 A（新项目）处理。缺少配置文件只意味着需要手动回答更多问题。

## 快速上手

```
1. /pace-init                     → 自动检测生命周期 → 生成 .devpace/
2. "帮我实现用户登录"              → devpace 自动追踪为 CR-001
3. /pace-status                   → 查看项目进度
```

已有需求文档的项目：

```
1. /pace-init --from prd.md       → 解析文档 → 生成 BR→PF→CR 价值功能树
2. /pace-status tree              → 查看生成的功能全景
```

## 生命周期检测

核心差异化能力。`/pace-init` 检测项目成熟度阶段，据此适配初始化的方方面面。

### 信号检测

| 信号 | 检测方式 | 阶段指向 |
|------|---------|---------|
| Git commit 数量 | `git rev-list --count HEAD` | 0-5 → 新项目，5-100 → 开发中，100+ → 成熟 |
| 版本标签 | `git tag --list` | 匹配 vX.Y.Z 模式 → 已发布 |
| CHANGELOG.md | 文件存在性 | 存在 → 已发布或接近发布 |
| 未合并分支 | `git branch --no-merged main` | >0 → 有进行中工作 |
| 部署配置 | fly.toml、k8s/、terraform/ 等 | 存在 → 已上线 |
| 源文件数量 | 按语言统计源文件 | <10 → 新项目，10-100 → 开发中，100+ → 成熟 |

### 阶段判定（按优先级）

1. **阶段 C（已发布）**：有版本标签 **或** CHANGELOG.md 存在 **或** 有部署配置
2. **阶段 B（开发中）**：不满足阶段 C **且**（commit 数 > 5 **或** 有未合并分支 **或** 源文件数 >= 10）
3. **阶段 A（新项目）**：不满足 C 和 B 条件时的默认值

非 git 目录默认为阶段 A。

### 各阶段行为对比

| 能力 | 阶段 A（新项目） | 阶段 B（开发中） | 阶段 C（已发布） |
|------|:---:|:---:|:---:|
| 自动检测名称 + 描述 | ✅ | ✅ | ✅ |
| 零提问启动（可推断时） | ✅ | ✅ | ✅ |
| 目录结构 → PF 候选 | — | ✅ | ✅ |
| 未合并分支 → 在研工作 | — | ✅ | ✅ |
| Git 分支策略检测 | — | ✅ | ✅ |
| README 功能提取 | — | ✅ | ✅ |
| 版本管理自动配置 | — | — | ✅ |
| 发布历史（DORA 基线） | — | — | ✅ |
| 环境列表推断 | — | — | ✅ |
| CHANGELOG 解析 → BR/PF 种子 | — | — | ✅ |
| pace-sync 推荐（非可选） | — | — | ✅ |
| state.md 复杂度 | 简单（5-8 行） | 中等（10-12 行） | 完整（13-15 行） |

## 命令参考

### 默认模式：`/pace-init [项目名称]`

生命周期感知的最小初始化。

**语法**：`/pace-init [项目名称]`

检测项目生命周期阶段，收集最少信息（可推断时自动获取），生成按阶段适配的 `.devpace/`，向 CLAUDE.md 注入 devpace section，运行初始化后校验，输出情境化引导。详细生成规则见 [init-procedures-core.md](../../skills/pace-init/init-procedures-core.md)。

**输出示例**（阶段 B 项目）：
```
检测到已有 47 次提交和 3 条活跃分支，已识别在研工作。

初始化完成：
.devpace/
├── state.md          — 项目状态（当前工作已预填）
├── project.md        — 项目定义（PF 候选已从 src/ 推断）
├── backlog/          — CR 存放目录
├── context.md        — 技术约定（Git flow 检测）
└── rules/
    ├── workflow.md   — 工作流规则
    └── checks.md     — 质量检查（vitest + biome 已检测）

✅ 所有文件校验通过
CLAUDE.md — devpace section 已注入

试试说"帮我修复 XXX"或"帮我添加 XXX"，devpace 会自动追踪变更。

常用命令：
- 开始工作："帮我实现/修复/添加 XXX"
- 查看进度：/pace-status
- 管理变更：/pace-change
- 回顾总结：/pace-retro
```

### `full` 模式：`/pace-init [项目名称] full`

分阶段完整初始化，支持提前退出。

**语法**：`/pace-init [项目名称] full`

按 4 个阶段引导，第 1 阶段后每个阶段均可选。用户可随时说"够了"跳过剩余阶段：

1. **基础阶段**（必须）：项目名 + 描述 + 环境检测 → 立即生成可用 .devpace/
2. **业务阶段**（可选）："要现在定义业务目标和成效指标吗？可稍后 /pace-retro 补充" → OBJ + MoS + BR
3. **发布阶段**（可选）："检测到 [CI 工具]，要配置发布流程吗？可稍后编辑 integrations/config.md" → 发布配置
4. **同步阶段**（可选）："检测到 GitHub 仓库，要配置外部同步吗？可稍后 /pace-sync setup" → 同步配置

详细阶段规则见 [init-procedures-full.md](../../skills/pace-init/init-procedures-full.md)。

### `--from` 模式：`/pace-init --from <路径>...`

文档驱动初始化——从需求文档自动生成 BR→PF→CR 价值功能树。

**语法**：`/pace-init [项目名称] --from <路径> [--from <路径2>...]`

支持单文件、目录（扫描所有 .md/.txt 文件）和多文件。增强解析：用户故事 → BR、功能列表 → PF 树、OpenAPI/Swagger 规格 → 按资源分组的 PF。解析结果先展示确认再写入 project.md。详细解析规则见 [init-procedures-from.md](../../skills/pace-init/init-procedures-from.md)。

**输出示例**：
```
从 prd.md 提取到以下功能树：

BR-1: 用户管理（"让用户能安全地注册和登录系统"）
├── PF-1: 用户注册（邮箱+密码+验证）
│   ├── CR候选: 注册表单实现
│   └── CR候选: 邮箱验证流程
├── PF-2: 用户登录（JWT + 刷新令牌）
│   └── CR候选: 登录接口 + Token 管理

BR-2: 订单系统（"支持完整的购买流程"）
├── PF-3: 购物车
└── PF-4: 支付集成

确认写入 project.md？[Y/n]
```

### `--verify` 健康检查：`/pace-init --verify [--fix]`

校验已有 `.devpace/` 目录的完整性。

**语法**：`/pace-init --verify [--fix]`

遍历 `.devpace/` 所有文件，按对应 Schema 逐一校验，输出健康报告。加 `--fix` 自动修复结构问题（缺失 section、格式不一致、版本标记），不修改语义内容。详细校验清单见 [init-procedures-verify.md](../../skills/pace-init/init-procedures-verify.md)。

**输出示例**：
```
.devpace/ 健康检查报告：
✅ state.md — 正常
✅ project.md — 正常
⚠️ rules/checks.md — 缺少 Gate 2 section（可自动修复）
❌ backlog/CR-001.md — 缺少"意图"字段（需人工处理）
✅ CLAUDE.md — devpace section 存在

总计：5 个文件，3 正常，1 可修复，1 需人工
```

### `--reset` 重置：`/pace-init --reset [--keep-insights]`

完全删除 `.devpace/`，含安全确认。

**语法**：`/pace-init --reset [--keep-insights]`

删除前需明确确认。删除 `.devpace/` 目录并清理 CLAUDE.md 中的 devpace section（`<!-- devpace-start -->` 到 `<!-- devpace-end -->` 区间）。若存在外部关联（sync-mapping 关联的 GitHub Issues），会提示需手动处理。`--keep-insights` 保留 `metrics/insights.md`（经验是跨项目资产）。详细步骤见 [init-procedures-reset.md](../../skills/pace-init/init-procedures-reset.md)。

### `--dry-run` 预览：`/pace-init --dry-run [其他参数]`

预览模式——执行全部检测逻辑，不写入任何文件。

**语法**：`/pace-init [项目名称] --dry-run`

运行完整的生命周期检测、工具链分析和信息收集流程，然后输出将创建的文件预览。特别适合阶段 B/C 项目在确认前查看自动配置结果。详细输出格式见 [init-procedures-dryrun.md](../../skills/pace-init/init-procedures-dryrun.md)。

**输出示例**：
```
/pace-init 预览（dry-run 模式，不写入文件）：

检测结果：
- 项目阶段：已有 120 次提交 + 5 个版本标签
- 项目名称：my-api（来源：package.json）
- 技术栈：TypeScript + Express
- 工具链：vitest + biome + tsc

将创建的文件：
.devpace/
├── state.md          — 项目状态（13 行，含版本信息）
├── project.md        — 项目定义（PF 候选从 src/ 推断）
├── backlog/          — CR 存放目录
├── context.md        — 技术约定（5 条约定）
├── rules/
│   ├── workflow.md   — 工作流规则
│   └── checks.md     — 质量检查（4 条命令检查 + 2 条意图检查）
├── integrations/
│   └── config.md     — 版本管理 + 环境 + CI/CD
└── metrics/
    └── dashboard.md  — DORA 基线（最近 5 次发布）

CLAUDE.md — 将注入 devpace section

确认初始化？运行 /pace-init my-api 开始。
```

### `--export-template` / `--from-template` 模板管理

团队级标准化的模板管理。

**导出语法**：`/pace-init --export-template`

将当前 `.devpace/` 配置导出为可复用的 `.devpace-template/` 目录。包含 workflow.md、checks.md（移除项目特定命令）、context.md（移除项目特定路径）和 integrations/config.md。用于在组织内多个项目间共享质量标准。

**应用语法**：`/pace-init --from-template <路径>`

使用模板作为基础进行初始化，模板中的配置覆盖默认模板。生命周期检测和信息收集照常运行；模板仅提供 workflow/checks/context/integrations 的默认值。

与 `--import-insights` 互补：模板标准化**规范**，insights 共享**经验**。

### `--import-insights` 跨项目经验导入

从另一个 devpace 项目导入经验。

**语法**：`/pace-init --import-insights <路径>`

读取导出的 insights 文件，置信度降级（×0.8），验证次数重置，跳过偏好类型条目，与现有 insights 去重。可在初始化时使用，也可在已初始化的项目上独立使用。详细处理规则见 [init-procedures-from.md](../../skills/pace-init/init-procedures-from.md)。

### `--interactive` 交互模式

强制交互模式，覆盖零提问的自动检测行为。

**语法**：`/pace-init [项目名称] --interactive`

所有自动推断的值（项目名称、描述、PF 候选、工具链选择）都会逐项展示确认后再使用。适用于自动检测可能不准确或你希望完全控制初始化过程的场景。

## 使用场景

### 场景 1：全新项目

从零开始——一个空目录，刚执行 `git init`。

```
你：    /pace-init my-app
Claude: 这是一个全新项目，采用极简初始化。

        初始化完成：
        .devpace/
        ├── state.md · project.md · backlog/ · rules/

        ✅ 所有文件校验通过

        试试说"帮我实现 XXX"，我会自动创建第一个 CR 开始工作。

你：    帮我实现用户注册功能
Claude: [创建 CR-001，自动开始追踪开发进度]
```

### 场景 2：开发中项目

已有 50+ 次提交和活跃分支的项目，但尚未正式发布。

```
你：    /pace-init
Claude: 检测到已有 52 次提交和 2 条活跃分支，已识别在研工作。
        项目名称：payment-service（来源：package.json）
        项目描述：A microservice for payment processing（来源：package.json）

        识别到以下功能模块（从 src/ 目录结构）：
        - auth/    → PF 候选: 认证模块
        - billing/ → PF 候选: 计费模块
        - webhook/ → PF 候选: Webhook 处理

        识别到 2 条未合并分支：
        - feature/refund-api
        - fix/timeout-handling

        初始化完成 [...]

你：    调整一下，webhook 不是独立功能，属于 billing 的一部分
Claude: [更新 project.md，将 webhook 归入 billing 模块]
```

### 场景 3：已发布项目（含 CI/CD）

成熟项目，有版本标签、GitHub Actions 和部署配置。

```
你：    /pace-init
Claude: 检测到已有 230 次提交和 8 个版本标签的项目，已自动配置版本管理和发布追踪。
        当前版本：v2.3.1（tag 格式：vX.Y.Z）
        最近发布：v2.3.1 (02-20), v2.3.0 (02-15), v2.2.0 (01-28)
        环境：staging, production（来源：.env.staging, .env.production）
        CI：GitHub Actions（push + PR trigger）

        初始化完成：
        .devpace/
        ├── state.md · project.md · backlog/ · context.md
        ├── rules/ · integrations/config.md · metrics/dashboard.md

        已发布项目通常需要外部同步，建议运行 /pace-sync setup 配置。
```

### 场景 4：初始化前预览

不确定 `/pace-init` 会创建什么？先预览。

```
你：    /pace-init --dry-run
Claude: [完整检测输出 + 文件树预览，不写入文件]

你：    看起来没问题，执行吧
你：    /pace-init
```

### 场景 5：手动编辑后健康检查

手动编辑了 `.devpace/` 文件，想验证一切是否仍然有效。

```
你：    /pace-init --verify
Claude: ⚠️ rules/checks.md — 缺少 Gate 2 section

你：    /pace-init --verify --fix
Claude: ✅ rules/checks.md — Gate 2 section 已补充
        ✅ 所有文件校验通过
```

## 生成文件参考

| 文件 | 说明 | 创建时机 |
|------|------|:--------:|
| `state.md` | 项目状态追踪（目标、当前工作、下一步） | 始终创建 |
| `project.md` | 项目定义，含 BR→PF→CR 价值功能树 | 始终创建 |
| `backlog/` | CR 文件存放目录 | 始终创建 |
| `rules/workflow.md` | CR 状态机和工作流规则 | 始终创建 |
| `rules/checks.md` | 质量门检查（工具链精准检测） | 始终创建 |
| `context.md` | 技术约定和编码规范 | 阶段 B/C 或检测到 ≥1 条约定时 |
| `integrations/config.md` | CI/CD、版本管理、环境配置 | 阶段 C 或检测到 CI 时 |
| `metrics/dashboard.md` | DORA 度量基线（从 git 历史提取） | 仅阶段 C |
| `CLAUDE.md`（注入） | devpace section，含 `.devpace/` 文件参考表 | 始终注入 |

初始化时**不创建**的文件（按需创建）：`iterations/`、`releases/`、`metrics/insights.md` — 在首次被其他命令使用时自动创建。

## 工具链检测

`/pace-init` 生成的 `checks.md` 包含精准匹配项目实际工具的命令，而非笼统的通用建议。

### 检测矩阵

| 生态系统 | 检测信号 | 识别工具 | 生成命令 |
|---------|---------|---------|---------|
| Node.js | devDependencies 含 `vitest` | Vitest | `npx vitest run` |
| Node.js | devDependencies 含 `jest` | Jest | `npx jest` |
| Node.js | devDependencies 含 `@biomejs/biome` | Biome | `npx biome check .` |
| Node.js | `.eslintrc*` 或 `eslint.config.*` 存在 | ESLint | `npx eslint .` |
| Node.js | devDependencies 含 `typescript` | TypeScript | `npx tsc --noEmit` |
| Python | pyproject.toml 含 `[tool.pytest]` | pytest | `pytest` |
| Python | pyproject.toml 含 `[tool.ruff]` | Ruff | `ruff check .` |
| Python | pyproject.toml 含 `[tool.mypy]` | mypy | `mypy .` |
| Go | go.mod 存在 | Go test | `go test ./...` |
| Go | `.golangci.yml` 存在 | golangci-lint | `golangci-lint run` |
| Rust | Cargo.toml 存在 | Cargo | `cargo test` + `cargo clippy -- -D warnings` |

未检测到具体工具时，保留通用占位符供手动配置。

## CLAUDE.md 智能合并

`/pace-init` 使用 HTML 注释标记向项目 `CLAUDE.md` 注入 devpace section，实现幂等更新：

```markdown
<!-- devpace-start -->
# 项目名称
> 项目定位
## 研发协作
[...devpace 文件参考表...]
<!-- devpace-end -->
```

**合并行为**：
- 已有标记 → 替换标记区间内的内容（幂等更新）
- 文件存在但无标记 → 末尾追加带标记的 section
- 文件不存在 → 创建新文件，包含标记 section

重新运行 `/pace-init` 或升级 devpace 版本时，会安全更新该 section，不影响 CLAUDE.md 的其他内容。

## 与其他命令的集成

| 命令 | 集成点 |
|------|--------|
| `/pace-dev` | 使用 init 生成的 `rules/checks.md` 执行质量门 |
| `/pace-status` | 读取 init 创建的 `state.md` 和 `project.md` |
| `/pace-change` | 使用 `project.md` 中的价值功能树进行影响分析 |
| `/pace-retro` | project.md 仍为桩状态时引导填充业务目标 |
| `/pace-sync setup` | 阶段 C 项目或检测到 git remote 时在 init 中推荐 |
| `/pace-release` | 使用 `integrations/config.md` 中的版本管理配置 |
| `/pace-plan` | 创建 `iterations/current.md`（按需创建，不在 init 时） |

## 架构说明（开发者向）

### 生命周期检测算法

检测使用 6 个信号的基于优先级的评估。阶段 C 拥有最高优先级（任何发布指标都触发），其次是阶段 B（开发活动），阶段 A 是默认兜底。这确保成熟项目始终获得最丰富的自动配置，即使某些信号模糊。

```
信号收集（并行）：
  commits  ← git rev-list --count HEAD
  tags     ← git tag --list（筛选版本模式）
  deploy   ← glob(fly.toml, app.yaml, serverless.yml, k8s/, terraform/)
  branches ← git branch --no-merged main | wc -l
  sources  ← count(*.js, *.ts, *.py, *.go, *.rs, *.java)
  changelog← exists(CHANGELOG.md)

阶段判定：
  if tags.match(version) OR changelog OR deploy.any → 阶段 C
  elif commits > 5 OR branches > 0 OR sources >= 10 → 阶段 B
  else → 阶段 A
```

### 文件生成管道

```
┌─────────────────────────┐
│    Step 0：路由           │
│  --verify/--reset/       │
│  --dry-run 标志          │
├─────────────────────────┤
│    Step 1：检测           │
│  生命周期 + 信息收集      │
│  （按阶段适配）           │
├─────────────────────────┤
│    Step 2：生成           │
│  模板 + 预填充            │
│  （按阶段适配）           │
├─────────────────────────┤
│    Step 3：CLAUDE.md      │
│  智能合并（幂等）         │
├─────────────────────────┤
│    Step 4：校验           │
│  Schema 检查 + 情境引导   │
└─────────────────────────┘
```

### 模板系统

模板存放在 `skills/pace-init/templates/`（12 个文件）。每个模板使用 `{{PLACEHOLDER}}` 语法进行动态内容替换。[init-procedures-core.md](../../skills/pace-init/init-procedures-core.md) 中的生成规则定义了每个生命周期阶段替换哪些占位符及其值。

### Monorepo 支持

检测到 monorepo 信号（`pnpm-workspace.yaml`、`nx.json`、`turbo.json`、`lerna.json`）时，用户选择：

- **根目录单一 `.devpace/`**（推荐 <5 个子包）：标准初始化，`context.md` 记录 monorepo 结构
- **根共享 + 子包独立追踪**（≥5 个子包）：根目录放 `rules/` + `context.md`，每个子包独立 `state.md` + `project.md` + `backlog/`

### 迁移框架

通过 `state.md` 末尾的 `<!-- devpace-version: X.Y.Z -->` 标记检测版本。检测到低版本时执行增量迁移段（只添加不删除策略）。新版本发布时在 init-procedures-core.md 中追加迁移段。每次迁移提示用户确认，支持通过 `git revert` 回滚。

## 降级行为与故障排除

### 降级行为

| 条件 | 行为 |
|------|------|
| 无 `.git/` 目录 | 默认阶段 A；跳过所有 git 相关检测 |
| 无配置文件（package.json 等） | 手动询问项目名称和描述 |
| 未检测到 CI/CD 配置 | 跳过 `integrations/config.md` 创建 |
| 检测到的约定不足 1 条 | 跳过 `context.md` 创建 |
| 非 git 项目使用 `--from` | `--from` 解析正常工作；生命周期默认阶段 A |
| `--verify` 但 `.devpace/` 不存在 | 提示先运行 `/pace-init` |
| `--reset` 时存在 sync-mapping | 删除前警告外部关联 |

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 生命周期阶段判定不准 | 异常的 git 历史模式 | 使用 `--interactive` 覆盖自动检测 |
| checks.md 测试命令有误 | 工具检测不匹配 | 直接编辑 `.devpace/rules/checks.md` |
| CLAUDE.md section 重复 | 标记被意外删除 | 重新运行 `/pace-init`（重新创建标记） |
| `--verify` 报大量错误 | 手动编辑破坏了 Schema 合规性 | 运行 `--verify --fix` 自动修复 |
| Monorepo 未被识别 | 非标准的 workspace 配置 | 使用 `--interactive` 手动配置 |

## 路线图

| 版本 | 功能 | 状态 |
|------|------|------|
| v1.0.0 | 最小初始化 + full 模式 + 环境探测 | ✅ 已发布 |
| v1.2.0 | 跨项目经验导入（`--import-insights`） | ✅ 已发布 |
| v1.5.0 | 生命周期感知 + `--verify`/`--reset`/`--dry-run` + `--from` 增强 + `--export-template` + Monorepo + CLAUDE.md 智能合并 + 工具链精准检测 + 情境化引导 | ✅ 当前 |

## 相关资源

- [用户指南 — /pace-init 章节](../user-guide.md) — 快速参考
- [SKILL.md](../../skills/pace-init/SKILL.md) — Skill 定义（做什么，步骤流程）
- [init-procedures-core.md](../../skills/pace-init/init-procedures-core.md) — 核心执行规程（怎么做）
- [state-format.md](../../knowledge/_schema/state-format.md) — 状态文件 Schema
- [project-format.md](../../knowledge/_schema/project-format.md) — 项目文件 Schema
- [checks-format.md](../../knowledge/_schema/checks-format.md) — 质量检查 Schema
- [context-format.md](../../knowledge/_schema/context-format.md) — 技术约定 Schema
- [devpace-rules.md](../../rules/devpace-rules.md) — 运行时行为规则
