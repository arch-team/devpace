---
description: Use when user says "初始化", "pace-init", "开始追踪", "初始化研发管理", "新项目", "项目管理", "set up devpace", "健康检查 devpace", "重置 devpace", "预览初始化", or wants to set up, verify, or reset project development tracking.
allowed-tools: AskUserQuestion, Write, Read, Glob, Bash
argument-hint: "[项目名称] [full] [--from <路径>...] [--import-insights <路径>] [--verify [--fix]] [--dry-run] [--reset [--keep-insights]] [--export-template] [--from-template <路径>] [--interactive]"
model: sonnet
disable-model-invocation: true
---

# /pace-init — 初始化项目开发节奏管理

从模板初始化当前项目的 `.devpace/` 目录。默认执行最小初始化（自动检测项目生命周期阶段，按阶段适配行为），`full` 执行分阶段完整流程，`--from` 从文档自动生成功能树。支持 `--verify`（健康检查）、`--reset`（重置）、`--dry-run`（预览）等子命令。详细执行规则见 `init-procedures.md`。

## 输入

$ARGUMENTS：可选。格式：

- `[项目名称]` — 最小初始化（默认，生命周期感知）
- `[项目名称] full` — 分阶段完整流程
- `[项目名称] --from <路径>...` — 从文档生成功能树（支持目录和多文件）
- `--verify [--fix]` — 健康检查（可选自动修复）
- `--dry-run` — 预览初始化结果，不写入文件
- `--reset [--keep-insights]` — 重置 .devpace/
- `--export-template` — 导出当前配置为可复用模板
- `--from-template <路径>` — 从模板初始化
- `--import-insights <路径>` — 导入跨项目经验
- `--interactive` — 强制对话模式（覆盖自动检测行为）

## 流程

### Step 0：前置检查与路由

**子命令路由**（优先级高于初始化流程）：

- `--verify` → 健康检查流程（见"健康检查"章节）
- `--reset` → 重置流程（见"重置"章节）
- `--export-template` / `--from-template` → 模板管理流程（见"模板管理"章节）

**标志处理**：

- `--dry-run` → 设置 dry-run 标志，继续正常流程但不写入任何文件

**版本检测**：

- 无 `.devpace/state.md` → 全新初始化（Step 1）
- 有 state.md + 版本标记 `<!-- devpace-version: X.Y.Z -->` 低于当前版本 → 提示增量迁移（详见 `init-procedures.md`"迁移框架"章节）
- 有 state.md + 版本为当前版本 → 提示已初始化，询问是否重置

### Step 1：项目生命周期检测 + 信息收集

**生命周期自动判定**（详见 `init-procedures.md`"项目生命周期检测"章节）：通过 git commit 数量、tags、部署配置、源文件数等信号组合判定项目阶段：

- **阶段 A（新项目）**：commit ≤ 5 且无 tags 且源文件 < 10
- **阶段 B（开发中）**：有 commit 历史但无版本 tags，或有未合并分支
- **阶段 C（已发布）**：有版本 tags 或 CHANGELOG 存在或有部署配置

判定结果用一句话交代，如："检测到这是一个已有 47 次提交和 3 个版本标签的项目，已自动配置版本管理和发布追踪。"用户可在输出后说"调整一下"进入交互修改。

**信息收集**（按阶段适配）：

- **阶段 A**：自动推断项目名（package.json → pyproject.toml → go.mod → Cargo.toml → git remote → 目录名）和描述（package.json#description → pyproject.toml#description → README.md 首段）。若两项均可推断 → 直接生成不提问；仅缺一项 → 只问缺失项
- **阶段 B**：阶段 A + 目录结构推断功能模块（扫描 src/ 一级子目录）+ 在研工作识别（未合并分支，限前 5 条）+ Git 策略检测（提升为默认行为）+ README 信息提取
- **阶段 C**：阶段 B + 版本管理自动配置（从 git tags 推断格式和版本号）+ 发布历史种子数据（最近 5 次发布）+ 环境列表推断 + CHANGELOG 解析

`--interactive` 标志：强制对话模式，逐项确认所有自动推断的信息。

### Step 2：生成 .devpace/（按生命周期阶段适配）

**阶段 A（新项目）**：

```
.devpace/
├── state.md          # 简单模式（5-8 行）
├── project.md        # 桩: 项目名 + 描述, 空价值树
├── backlog/
└── rules/
    ├── workflow.md    # 标准模板
    └── checks.md     # 从项目工具链精准检测（vitest/jest/mocha, ruff/flake8 等）
```

**阶段 B（开发中）**——在阶段 A 基础上增加：

- project.md 价值功能树预填充（从 src/ 目录结构推断 PF 候选，标注 `<!-- source: claude, dir-structure -->`）
- state.md 中等模式（10-12 行），当前工作从未合并分支候选
- context.md 自动生成（Git 策略检测 + 编码约定检测）

**阶段 C（已发布）**——在阶段 B 基础上增加：

- integrations/config.md 自动配置（版本管理 + 环境列表 + 发布分支）
- metrics/dashboard.md DORA 基线（从 git tags 提取最近 5 次发布，标注 `<!-- source: claude, git-history -->`）
- state.md 复杂模式（13-15 行）
- pace-sync 推荐引导（从"可选"提升为"推荐"）

**不创建**（所有阶段）：按需目录创建策略不变（iterations/releases/insights 等首次使用时创建）。

**Monorepo 检测**：检测到 monorepo 信号（pnpm-workspace.yaml/nx.json/turbo.json/lerna.json）时询问组织方式（详见 `init-procedures.md`）。

### Step 3：CLAUDE.md 注入

使用智能合并策略（详见 `init-procedures.md`"CLAUDE.md 智能合并"章节）：

- 已有 `<!-- devpace-start -->`/`<!-- devpace-end -->` 标记 → 原地替换区间内容（幂等更新）
- 文件存在但无标记 → 末尾追加带标记的 devpace section
- 文件不存在 → 创建新文件

### Step 4：自动校验 + 情境化引导

**自动校验**（详见 `init-procedures.md`"初始化后自动校验"章节）：校验所有生成文件存在且非空、state.md/project.md 符合 Schema、CLAUDE.md section 已注入、checks.md 至少含 2 条检查项。全部通过 → 一行确认；有问题 → 直接修复。

**情境化引导**（按项目状态输出下一步）：

- 阶段 A → "试试说'帮我实现 XXX'，我会自动创建第一个 CR 开始工作"
- 阶段 B → "试试说'帮我修复 XXX'或'帮我添加 XXX'，devpace 会自动追踪变更"
- `--from` 模式 → "已从文档生成 N 个产品功能，试试 `/pace-status tree` 查看全景"
- 检测到 git remote → 追加 "运行 `/pace-sync setup` 可将 CR 同步到 GitHub Issues"

提供一个具体 prompt 示例 + 3-5 个常用命令速查。建议 `.gitignore` 添加 `.devpace/`。

**dry-run 模式**：输出将创建的目录树 + 每文件一句话说明，末尾提示去掉 `--dry-run` 的命令。

## `/pace-init full` 分阶段完整流程

当参数含 `full` 时，执行分阶段引导（兼容生命周期检测），每阶段完成后可说"够了"提前退出：

1. **基础阶段**：项目名 + 描述 + 环境检测（自动）→ 立即生成可用 .devpace/
2. **业务阶段**（可选）："要现在定义业务目标和成效指标吗？可稍后 /pace-retro 补充" → OBJ + MoS + BR
3. **发布阶段**（可选）："检测到 [CI 工具]，要配置发布流程吗？可稍后编辑 integrations/config.md" → 发布配置
4. **同步阶段**（可选）："检测到 GitHub 仓库，要配置外部同步吗？可稍后 /pace-sync setup" → 同步配置

用 AskUserQuestion 多选让用户勾选想配置的维度。生成完整目录结构（含所有子目录和文件）。

## `/pace-init --from <路径>...` 文档驱动初始化

从需求文档自动解析并生成 BR→PF→CR 功能树。

### 增强能力

- **目录路径**：`/pace-init --from requirements/` → 扫描目录下所有 .md 文件综合提取
- **多文件**：`/pace-init --from prd.md --from api-spec.md`
- **增强解析**：用户故事 → BR、功能列表 → PF 树、API 规格（OpenAPI/Swagger YAML/JSON）→ PF
- 解析结果先展示确认，再写入 project.md

### 流程

1. **读取文档**：读取指定路径的文件/目录/多文件（支持 .md/.txt/.pdf/.yaml/.json）
2. **提取需求**：AI 解析文档，识别业务目标、功能模块、用户场景、API 规格
3. **生成功能树**：映射为 BR→PF→CR 价值链（非扁平任务列表）
4. **用户确认**：展示生成的功能树结构，等待确认或调整
5. **写入 project.md**：确认后写入 `.devpace/project.md` 的价值功能树

### 注意事项

- 文档内容越结构化，解析结果越准确
- 模糊描述标记为"需澄清"
- 生成的 CR 初始列表仅为建议，不自动创建 CR 文件（用户 /pace-dev 时才创建）
- 可与 `full` 组合：`/pace-init myproject full --from prd.md`

## `/pace-init --verify` 健康检查

遍历 `.devpace/` 所有文件，按对应 Schema 逐一校验（详见 `init-procedures.md`"健康检查规程"章节）：

- ✅ 正常
- ⚠️ 可自动修复（缺失字段补默认值、格式修正、版本标记更新）
- ❌ 需人工处理

加 `--fix` 自动修复结构问题（不修改语义内容）。

## `/pace-init --reset` 重置

重置 `.devpace/` 目录（详见 `init-procedures.md`"重置规程"章节）：

1. 二次确认："即将删除 .devpace/ 及所有追踪数据，此操作不可逆"
2. 删除 .devpace/
3. 清理 CLAUDE.md 中的 devpace section（`<!-- devpace-start -->`…`<!-- devpace-end -->` 区间）
4. 提示外部关联清理（sync-mapping 关联的 GitHub Issues 需手动处理）
5. `--keep-insights` 保留 insights.md（经验是跨项目资产）
6. 完成后提示："已清除。可运行 /pace-init 重新初始化"

## `/pace-init --dry-run` 预览

执行全部检测逻辑，不写入任何文件。输出将创建的目录树 + 每文件一句话说明，特别适合阶段 B/C 项目预览自动配置结果。末尾提示确认或给出去掉 `--dry-run` 的命令。

## `/pace-init --export-template` / `--from-template` 模板管理

**导出**（`--export-template`）：导出当前 `.devpace/` 配置为可复用模板（`.devpace-template/`）：workflow.md、checks.md（去项目特定命令）、context.md（通用约定）、integrations/config.md。

**应用**（`--from-template <路径>`）：从模板初始化，模板中的配置覆盖默认模板。与 `--import-insights` 互补：insights 是经验层面，template 是规范层面。

## 输出

初始化完成的 `.devpace/` 目录 + 确认摘要。`--dry-run` 时仅输出预览。`--verify` 时输出健康报告。`--reset` 时输出清理确认。
