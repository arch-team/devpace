# Project Initialization (`/pace-init`)

`/pace-init` is the entry point for devpace — it creates the `.devpace/` directory that powers all other devpace features. What makes it unique is **lifecycle-aware initialization**: rather than asking the same questions regardless of project maturity, it detects whether a project is brand new, mid-development, or already released, and adapts its behavior accordingly. New projects get zero-question setup; mature projects get automatic version management and release tracking configuration.

## Prerequisites

| Requirement | Purpose | Required? |
|-------------|---------|:---------:|
| Project directory | Working directory for `.devpace/` creation | Yes |
| `git` initialized | Lifecycle detection uses git history signals | Recommended |
| Config files (package.json, pyproject.toml, etc.) | Auto-detect project name, description, and toolchain | Optional |

> **Graceful degradation**: Non-git projects default to Stage A (new project) behavior. Missing config files simply mean more questions during setup.

## Quick Start

```
1. /pace-init                     → Auto-detect lifecycle → generate .devpace/
2. "帮我实现用户登录"              → devpace auto-tracks as CR-001
3. /pace-status                   → See project progress
```

For existing projects with requirements documents:

```
1. /pace-init --from prd.md       → Parse doc → generate BR→PF→CR value tree
2. /pace-status tree              → View the generated feature landscape
```

## Lifecycle Detection

The core differentiator. `/pace-init` inspects the project to determine its maturity stage, then adapts every aspect of initialization.

### Signal Detection

| Signal | Detection method | Stage indicator |
|--------|-----------------|-----------------|
| Git commit count | `git rev-list --count HEAD` | 0-5 → new, 5-100 → mid-dev, 100+ → mature |
| Version tags | `git tag --list` | vX.Y.Z patterns → released |
| CHANGELOG.md | File existence | Present → released or near-release |
| Unmerged branches | `git branch --no-merged main` | >0 → active development |
| Deploy configs | fly.toml, k8s/, terraform/, etc. | Present → production-ready |
| Source file count | Language-specific file count | <10 → new, 10-100 → mid-dev, 100+ → mature |

### Stage Determination (Priority Order)

1. **Stage C (Released)**: Has version tags **or** CHANGELOG.md exists **or** deploy configs present
2. **Stage B (Mid-development)**: Not Stage C **and** (commits > 5 **or** unmerged branches **or** source files >= 10)
3. **Stage A (New project)**: Default when neither C nor B criteria are met

Non-git directories default to Stage A.

### What Each Stage Does

| Capability | Stage A (New) | Stage B (Mid-dev) | Stage C (Released) |
|------------|:---:|:---:|:---:|
| Auto-detect name + description | ✅ | ✅ | ✅ |
| Zero-question setup (when inferrable) | ✅ | ✅ | ✅ |
| Directory structure → PF candidates | — | ✅ | ✅ |
| In-progress work from branches | — | ✅ | ✅ |
| Git strategy detection | — | ✅ | ✅ |
| README feature extraction | — | ✅ | ✅ |
| Version management auto-config | — | — | ✅ |
| Release history (DORA baseline) | — | — | ✅ |
| Environment list inference | — | — | ✅ |
| CHANGELOG parsing → BR/PF seeds | — | — | ✅ |
| pace-sync recommended (not optional) | — | — | ✅ |
| state.md complexity | Simple (5-8 lines) | Medium (10-12 lines) | Full (13-15 lines) |

## Command Reference

### Default: `/pace-init [project-name]`

Lifecycle-aware minimal initialization.

**Syntax**: `/pace-init [project-name]`

Detects project lifecycle stage, collects minimal information (auto-inferred when possible), generates `.devpace/` with stage-appropriate configuration, injects devpace section into CLAUDE.md, runs post-init validation, and outputs contextual guidance. See [init-procedures-core.md](../../skills/pace-init/init-procedures-core.md) for detailed generation rules.

**Output example** (Stage B project):
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

### `full`: `/pace-init [project-name] full`

Phased complete initialization with early exit support.

**Syntax**: `/pace-init [project-name] full`

Executes in 4 phases, each optional after Phase 1. Users can say "够了" at any point to skip remaining phases:

1. **Foundation** (required): Name + description + environment detection → immediately usable `.devpace/`
2. **Business** (optional): "Define business objectives now? Or `/pace-retro` later" → OBJ + MoS + BR
3. **Release** (optional): "Configure release pipeline? Or edit integrations/config.md later" → release config
4. **Sync** (optional): "Configure GitHub sync? Or `/pace-sync setup` later" → external sync

See [init-procedures-full.md](../../skills/pace-init/init-procedures-full.md) for detailed phase rules.

### `--from`: `/pace-init --from <path>...`

Document-driven initialization — auto-generates BR→PF→CR value tree from requirement documents.

**Syntax**: `/pace-init [project-name] --from <path> [--from <path2>...]`

Supports single files, directories (scans all .md/.txt files), and multiple files. Enhanced parsing handles user stories → BR, feature lists → PF tree, and OpenAPI/Swagger specs → PF grouped by resource. Results are shown for confirmation before writing to project.md. See [init-procedures-from.md](../../skills/pace-init/init-procedures-from.md) for parsing rules.

**Output example**:
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

### `--verify`: `/pace-init --verify [--fix]`

Health check for existing `.devpace/` directories.

**Syntax**: `/pace-init --verify [--fix]`

Iterates all `.devpace/` files, validates each against its corresponding schema, and outputs a health report. With `--fix`, auto-repairs structural issues (missing sections, format inconsistencies, version markers) without modifying semantic content. See [init-procedures-verify.md](../../skills/pace-init/init-procedures-verify.md) for the full validation checklist.

**Output example**:
```
.devpace/ 健康检查报告：
✅ state.md — 正常
✅ project.md — 正常
⚠️ rules/checks.md — 缺少 Gate 2 section（可自动修复）
❌ backlog/CR-001.md — 缺少"意图"字段（需人工处理）
✅ CLAUDE.md — devpace section 存在

总计：5 个文件，3 正常，1 可修复，1 需人工
```

### `--reset`: `/pace-init --reset [--keep-insights]`

Complete removal of `.devpace/` with safety checks.

**Syntax**: `/pace-init --reset [--keep-insights]`

Requires explicit confirmation before deletion. Removes `.devpace/` directory and cleans up the devpace section in CLAUDE.md (between `<!-- devpace-start -->` and `<!-- devpace-end -->` markers). Warns about external associations (GitHub Issues linked via sync-mapping). With `--keep-insights`, preserves `metrics/insights.md` as a cross-project asset. See [init-procedures-reset.md](../../skills/pace-init/init-procedures-reset.md) for detailed steps.

### `--dry-run`: `/pace-init --dry-run [other-args]`

Preview mode — runs all detection logic without writing any files.

**Syntax**: `/pace-init [project-name] --dry-run`

Executes the full lifecycle detection, toolchain analysis, and information gathering pipeline, then outputs a preview of what would be created. Particularly useful for Stage B/C projects to review auto-configuration results before committing. See [init-procedures-dryrun.md](../../skills/pace-init/init-procedures-dryrun.md) for output format.

**Output example**:
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

### `--export-template` / `--from-template`

Template management for team-wide standardization.

**Export syntax**: `/pace-init --export-template`

Exports the current `.devpace/` configuration into a reusable `.devpace-template/` directory. Includes workflow.md, checks.md (with project-specific commands removed), context.md (with project-specific paths removed), and integrations/config.md. Designed for sharing quality standards across an organization's projects.

**Apply syntax**: `/pace-init --from-template <path>`

Initializes using a template as the base, overriding default templates with the team's configuration. Lifecycle detection and information collection still run normally; the template only provides workflow/checks/context/integrations defaults.

Complementary to `--import-insights`: templates standardize *rules*, insights share *experience*.

### `--import-insights`

Import cross-project experience from another devpace project.

**Syntax**: `/pace-init --import-insights <path>`

Reads an exported insights file, downgrades confidence scores (×0.8), resets verification counts, skips preference-type entries, and deduplicates against existing insights. Can be used both during initial setup and on already-initialized projects. See [init-procedures-from.md](../../skills/pace-init/init-procedures-from.md) for processing rules.

### `--interactive`

Force interactive mode, overriding zero-question auto-detection.

**Syntax**: `/pace-init [project-name] --interactive`

Every auto-inferred value (project name, description, detected PF candidates, toolchain choices) is presented for confirmation before use. Useful when auto-detection might make incorrect assumptions or when you want full control over the initialization.

## Usage Scenarios

### Scenario 1: Brand New Project

Starting fresh — no code yet, just an empty directory with `git init`.

```
You:    /pace-init my-app
Claude: 这是一个全新项目，采用极简初始化。

        初始化完成：
        .devpace/
        ├── state.md · project.md · backlog/ · rules/

        ✅ 所有文件校验通过

        试试说"帮我实现 XXX"，我会自动创建第一个 CR 开始工作。

You:    帮我实现用户注册功能
Claude: [Creates CR-001, begins development tracking automatically]
```

### Scenario 2: Mid-Development Project

An existing project with 50+ commits and active branches, but no formal release yet.

```
You:    /pace-init
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

You:    调整一下，webhook 不是独立功能，属于 billing 的一部分
Claude: [Updates project.md accordingly]
```

### Scenario 3: Released Project with CI/CD

A mature project with version tags, GitHub Actions, and deployment config.

```
You:    /pace-init
Claude: 检测到已有 230 次提交和 8 个版本标签的项目，已自动配置版本管理和发布追踪。
        当前版本：v2.3.1（tag 格式：vX.Y.Z）
        最近发布：v2.3.1 (02-20), v2.3.0 (02-15), v2.2.0 (01-28)
        环境：staging, production（来源：.env.staging, .env.production）
        CI：GitHub Actions（push + PR trigger）

        初始化完成：
        .devpace/
        ├── state.md · project.md · backlog/ · context.md
        ├── rules/ · integrations/config.md · metrics/dashboard.md

        已发布项目通常需要外部同步，建议运行 /pace-sync setup 配置 CR 与 GitHub Issue 的同步。
```

### Scenario 4: Preview Before Committing

Unsure what `/pace-init` will create for your project? Preview first.

```
You:    /pace-init --dry-run
Claude: [Full detection output + file tree preview, no files written]

You:    Looks good, go ahead
You:    /pace-init
```

### Scenario 5: Health Check After Manual Edits

You've been manually editing `.devpace/` files and want to verify everything is still valid.

```
You:    /pace-init --verify
Claude: ⚠️ rules/checks.md — 缺少 Gate 2 section

You:    /pace-init --verify --fix
Claude: ✅ rules/checks.md — Gate 2 section 已补充
        ✅ 所有文件校验通过
```

## Generated Files Reference

| File | Description | When created |
|------|-------------|:------------:|
| `state.md` | Project status tracking (objective, current work, next step) | Always |
| `project.md` | Project definition with BR→PF→CR value tree | Always |
| `backlog/` | Directory for CR files | Always |
| `rules/workflow.md` | CR state machine and workflow rules | Always |
| `rules/checks.md` | Quality gate checks (toolchain-detected) | Always |
| `context.md` | Technical conventions and coding standards | Stage B/C or when ≥1 convention detected |
| `integrations/config.md` | CI/CD, version management, environment config | Stage C or when CI detected |
| `metrics/dashboard.md` | DORA metrics baseline from git history | Stage C only |
| `CLAUDE.md` (injection) | devpace section with `.devpace/` file reference table | Always |

Files not created at init (on-demand): `iterations/`, `releases/`, `metrics/insights.md` — created when first needed by other commands.

## Toolchain Detection

`/pace-init` generates `checks.md` with precise commands matching the actual tools in your project, not generic suggestions.

### Detection Matrix

| Ecosystem | Signal | Detected tool | Generated command |
|-----------|--------|---------------|-------------------|
| Node.js | `vitest` in devDependencies | Vitest | `npx vitest run` |
| Node.js | `jest` in devDependencies | Jest | `npx jest` |
| Node.js | `@biomejs/biome` in devDependencies | Biome | `npx biome check .` |
| Node.js | `.eslintrc*` or `eslint.config.*` exists | ESLint | `npx eslint .` |
| Node.js | `typescript` in devDependencies | TypeScript | `npx tsc --noEmit` |
| Python | `[tool.pytest]` in pyproject.toml | pytest | `pytest` |
| Python | `[tool.ruff]` in pyproject.toml | Ruff | `ruff check .` |
| Python | `[tool.mypy]` in pyproject.toml | mypy | `mypy .` |
| Go | go.mod exists | Go test | `go test ./...` |
| Go | `.golangci.yml` exists | golangci-lint | `golangci-lint run` |
| Rust | Cargo.toml exists | Cargo | `cargo test` + `cargo clippy -- -D warnings` |

When no specific tool is detected, generic placeholders are preserved for manual configuration.

## CLAUDE.md Smart Merge

`/pace-init` injects a devpace section into your project's `CLAUDE.md` using HTML comment markers for idempotent updates:

```markdown
<!-- devpace-start -->
# Project Name
> Project description
## 研发协作
[...devpace file reference table...]
<!-- devpace-end -->
```

**Merge behavior**:
- Markers present → replace content between markers (idempotent update)
- File exists, no markers → append marked section at end
- File doesn't exist → create new file with marked section

Re-running `/pace-init` or upgrading devpace safely updates the section without affecting other CLAUDE.md content.

## Integration with Other Commands

| Command | Integration point |
|---------|-------------------|
| `/pace-dev` | Uses `rules/checks.md` generated by init for quality gates |
| `/pace-status` | Reads `state.md` and `project.md` created by init |
| `/pace-change` | Uses value tree in `project.md` for impact analysis |
| `/pace-retro` | Fills business objectives in `project.md` if still stub |
| `/pace-sync setup` | Proposed during init for Stage C projects and when git remote detected |
| `/pace-release` | Uses version management config in `integrations/config.md` |
| `/pace-plan` | Creates `iterations/current.md` (on-demand, not at init) |

## Architecture (for Developers)

### Skill File Architecture

`/pace-init` uses a routing + procedure split pattern for token efficiency:

| File | Lines | Purpose |
|------|------:|---------|
| `SKILL.md` | 62 | Routing layer — input/output/dispatch, loaded on every invocation |
| `init-procedures-core.md` | 349 | Shared core — lifecycle detection, Git strategy, minimal init, CLAUDE.md merge, validation, guidance, quality check guidance, monorepo |
| `init-procedures-migration.md` | 58 | Migration framework — version detection, safety rules, incremental migration segments |
| `init-procedures-checks.md` | 84 | Toolchain detection reference — ecosystem-specific detection tables, default check suggestions, check format |
| `init-procedures-full.md` | 154 | `full` mode — environment probing, phased guidance, release config |
| `init-procedures-from.md` | 53 | `--from` / `--import-insights` — document parsing, experience import |
| `init-procedures-verify.md` | 54 | `--verify` — health check |
| `init-procedures-reset.md` | 31 | `--reset` — reset procedure |
| `init-procedures-dryrun.md` | 40 | `--dry-run` — preview mode |
| `init-procedures-template.md` | 25 | `--export-template` / `--from-template` — template management |

Claude loads only the procedure files relevant to the invoked sub-command, reducing context window consumption compared to the previous monolithic design.

### Lifecycle Detection Algorithm

The detection uses a priority-based evaluation of 6 signals. Stage C takes highest priority (any release indicator triggers it), followed by Stage B (development activity), with Stage A as the default fallback. This ensures mature projects always get the richest auto-configuration even if some signals are ambiguous.

```
Signals collected (parallel):
  commits ← git rev-list --count HEAD
  tags    ← git tag --list (filtered for version patterns)
  deploy  ← glob(fly.toml, app.yaml, serverless.yml, k8s/, terraform/)
  branches← git branch --no-merged main | wc -l
  sources ← count(*.js, *.ts, *.py, *.go, *.rs, *.java)
  changelog ← exists(CHANGELOG.md)

Stage determination:
  if tags.match(version) OR changelog OR deploy.any → Stage C
  elif commits > 5 OR branches > 0 OR sources >= 10 → Stage B
  else → Stage A
```

### File Generation Pipeline

```
┌─────────────────────────┐
│    Step 0: Routing       │
│  --verify/--reset/       │
│  --dry-run flag          │
├─────────────────────────┤
│    Step 1: Detection     │
│  Lifecycle + Info gather │
│  (stage-adaptive)        │
├─────────────────────────┤
│    Step 2: Generation    │
│  Templates + pre-fill    │
│  (stage-adaptive)        │
├─────────────────────────┤
│    Step 3: CLAUDE.md     │
│  Smart merge (idempotent)│
├─────────────────────────┤
│    Step 4: Validation    │
│  Schema check + guidance │
└─────────────────────────┘
```

### Template System

Templates live in `skills/pace-init/templates/` (12 files). Each template uses `{{PLACEHOLDER}}` syntax for dynamic content replacement. The generation rules in [init-procedures-core.md](../../skills/pace-init/init-procedures-core.md) define exactly which placeholders are replaced and with what values for each lifecycle stage.

### Monorepo Support

When monorepo signals are detected (`pnpm-workspace.yaml`, `nx.json`, `turbo.json`, `lerna.json`), the user chooses between:

- **Single root `.devpace/`** (recommended for <5 packages): Standard init, `context.md` records monorepo structure
- **Root shared + per-package tracking** (for >=5 packages): Root gets `rules/` + `context.md`, each sub-package gets independent `state.md` + `project.md` + `backlog/`

### Migration Framework

Version detection via `<!-- devpace-version: X.Y.Z -->` marker in `state.md`. When a lower version is detected, incremental migration segments execute (only-add, never-delete policy). Migration rules live in [init-procedures-migration.md](../../skills/pace-init/init-procedures-migration.md), with new segments appended as versions ship. Each migration prompts user confirmation and provides rollback via `git revert`.

## Degradation & Troubleshooting

### Degradation Behavior

| Condition | Behavior |
|-----------|----------|
| No `.git/` directory | Default to Stage A; skip all git-based detection |
| No config files (package.json, etc.) | Ask for project name and description manually |
| No CI/CD configuration detected | Skip `integrations/config.md` creation |
| Fewer than 1 convention detected | Skip `context.md` creation |
| Non-git project with `--from` | Full `--from` parsing works; lifecycle defaults to Stage A |
| `--verify` on missing `.devpace/` | Prompt to run `/pace-init` first |
| `--reset` with sync-mapping | Warn about external associations before deletion |

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Wrong lifecycle stage detected | Unusual git history pattern | Use `--interactive` to override auto-detection |
| checks.md has wrong test command | Tool detection mismatch | Edit `.devpace/rules/checks.md` directly |
| CLAUDE.md section duplicated | Markers were accidentally removed | Run `/pace-init` again (re-creates markers) |
| `--verify` reports many errors | Manual edits broke schema compliance | Run `--verify --fix` for auto-repair |
| Monorepo not detected | Non-standard workspace config | Use `--interactive` and configure manually |

## Roadmap

| Version | Features | Status |
|---------|----------|--------|
| v1.0.0 | Minimal init + full mode + environment detection | ✅ Released |
| v1.2.0 | Cross-project insights import (`--import-insights`) | ✅ Released |
| v1.5.0 | Lifecycle-aware init + `--verify`/`--reset`/`--dry-run` + `--from` enhanced + `--export-template` + Monorepo + CLAUDE.md smart merge + toolchain precision + contextual guidance | ✅ Released |
| v1.6.0 | Migration framework extraction + v1.5→v1.6 migration segment + Skill-level write scope Hook + description NOT-for clause | ✅ Current |

## Related Resources

- [User Guide — /pace-init section](../user-guide.md) — Quick reference for end users
- [SKILL.md](../../skills/pace-init/SKILL.md) — Skill definition (routing layer)
- [init-procedures-core.md](../../skills/pace-init/init-procedures-core.md) — Core execution rules (lifecycle, init, quality check, monorepo)
- [init-procedures-migration.md](../../skills/pace-init/init-procedures-migration.md) — Migration framework (version detection, incremental migration)
- [init-procedures-checks.md](../../skills/pace-init/init-procedures-checks.md) — Toolchain detection reference data
- [init-procedures-full.md](../../skills/pace-init/init-procedures-full.md) — Full mode execution rules
- [init-procedures-from.md](../../skills/pace-init/init-procedures-from.md) — Document-driven init and insights import
- [init-procedures-verify.md](../../skills/pace-init/init-procedures-verify.md) — Health check rules
- [init-procedures-reset.md](../../skills/pace-init/init-procedures-reset.md) — Reset procedure
- [init-procedures-dryrun.md](../../skills/pace-init/init-procedures-dryrun.md) — Preview mode rules
- [init-procedures-template.md](../../skills/pace-init/init-procedures-template.md) — Template management rules
- [state-format.md](../../knowledge/_schema/state-format.md) — State file schema
- [project-format.md](../../knowledge/_schema/project-format.md) — Project file schema
- [checks-format.md](../../knowledge/_schema/checks-format.md) — Quality checks schema
- [context-format.md](../../knowledge/_schema/context-format.md) — Technical conventions schema
- [devpace-rules.md](../../rules/devpace-rules.md) — Runtime behavior rules
