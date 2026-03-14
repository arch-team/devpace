# devpace 项目目录结构

> **职责**：文件放置规则。新建文件时查此文件确定目标位置。

## §0 速查卡片

### 目录-层级映射表

| 目录 | 层级 | 自动加载 | 随 Plugin 分发 | 说明 |
|------|------|---------|---------------|------|
| `.claude-plugin/` | 产品 | — | 是 | 仅 plugin.json + marketplace.json |
| `rules/` | 产品 | 是（Rules） | 是 | Plugin 运行时行为规则 |
| `skills/` | 产品 | 按触发 | 是 | Skill 定义（每 Skill 一个目录） |
| `knowledge/` (含 `_schema/`) | 产品 | 按引用 | 是 | 理论、指标、数据格式契约 |
| `hooks/` | 产品 | 事件驱动 | 是 | Hook 脚本 + hooks.json |
| `agents/` | 产品 | 按调用 | 是 | Agent 定义 |
| `output-styles/` | 产品 | 按选择 | 是 | 输出风格定义 |
| `settings.json` | 产品 | 是 | 是 | Plugin 默认配置 |
| `.claude/rules/` | 开发 | 是（Rules） | 否 | 开发规范（自动加载） |
| `.claude/references/` | 开发 | 按需读取 | 否 | 参考文档（不自动加载） |
| `docs/` | 开发 | 否 | 否 | design/、planning/、features/、research/、plans/、brand/、scratch/ |
| `dev-scripts/` | 开发 | 否 | 否 | 开发工具脚本 |
| `tests/` | 开发 | 否 | 否 | 测试套件 |
| `examples/` | 开发 | 否 | 否 | 示例项目 |
| `.github/` | CI/配置 | — | 否 | GitHub Actions、模板 |
| `.githooks/` | CI/配置 | — | 否 | Git hooks（pre-commit 等） |

### 配置文件速查

**必须**：`.claude-plugin/plugin.json`（manifest）
**可选**：`marketplace.json`、`settings.json`、`hooks/hooks.json`、`Makefile`、`pytest.ini`、`.markdownlint-cli2.jsonc`

### 禁止事项

- 组件放 `.claude-plugin/`（仅 plugin.json + marketplace.json）
- 测试文件散在 `skills/` 中（统一放 `tests/`）
- 分层架构约束（5 条）→ 详见 CLAUDE.md "分层架构"章节

## §1 产品层目录结构

```
devpace/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── rules/
│   └── devpace-rules.md
├── skills/
│   ├── pace-xxx/                       ← SKILL.md + *-procedures*.md
│   └── scripts/
├── knowledge/
│   ├── _schema/*-format.md
│   └── *.md
├── hooks/
│   ├── hooks.json
│   ├── lib/
│   ├── skill/
│   └── *.mjs / *.sh
├── agents/pace-*.md
├── output-styles/
└── settings.json
```

## §2 开发层目录结构

```
devpace/
├── .claude/
│   ├── CLAUDE.md
│   ├── rules/
│   └── references/
├── docs/
│   ├── design/
│   ├── planning/
│   ├── features/
│   ├── research/
│   ├── plans/
│   ├── brand/
│   └── scratch/
├── dev-scripts/
├── tests/
│   ├── static/
│   ├── evaluation/pace-xxx/
│   ├── hooks/
│   ├── integration/
│   └── scenarios/
└── examples/
```

## §3 新文件放置决策树

```
新文件
├─ Plugin 运行时需要？
│  ├─ 行为规则 → rules/
│  ├─ Skill → skills/pace-xxx/
│  ├─ Schema → knowledge/_schema/
│  ├─ 参考知识 → knowledge/
│  ├─ Hook → hooks/（Skill 域 → hooks/skill/）
│  ├─ Agent → agents/
│  └─ 输出风格 → output-styles/
├─ 开发规范？
│  ├─ 自动加载规则 → .claude/rules/
│  └─ 按需参考 → .claude/references/
├─ 文档？（均在 docs/ 下）
│  → design/ | planning/ | features/ | research/ | plans/
├─ 测试？（均在 tests/ 下）
│  → static/ | evaluation/pace-xxx/ | hooks/ | integration/ | scenarios/
├─ 脚本 → dev-scripts/
├─ CI/CD → .github/workflows/
└─ 不确定 → 先问，不要放项目根目录
```

## §4 跨文档引用

| 内容 | 参见 |
|------|------|
| 分层架构 5 条硬性约束 | CLAUDE.md "分层架构"章节（权威源） |
| 组件格式（SKILL.md frontmatter 等） | `plugin-dev-spec.md` |
| 文件命名规范 | `common.md` |
| 信息架构原则（IA-1 至 IA-11） | `info-architecture.md` |
| 新建 Skill 同步清单 | `references/sync-checklists.md` |
