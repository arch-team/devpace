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

| 文件 | 用途 |
|------|------|
| `.claude-plugin/plugin.json` | **必须** — Plugin manifest |
| `.claude-plugin/marketplace.json` | Marketplace 元数据 |
| `settings.json` | Plugin 默认设置 |
| `hooks/hooks.json` | Hook 事件配置 |
| `Makefile` / `pytest.ini` / `.markdownlint-cli2.jsonc` | 构建、测试、lint 配置 |

### 禁止事项

- 组件放 `.claude-plugin/`（仅 plugin.json + marketplace.json）
- 产品层文件放 `docs/` 或 `.claude/`（运行时资产必须在产品层目录）
- 测试文件散在 `skills/` 中（统一放 `tests/`）
- 产品层引用 `docs/` 或 `.claude/`（分层硬性约束，详见 CLAUDE.md）

## §1 产品层目录结构

```
devpace/                          # Plugin 根目录
├── .claude-plugin/
│   ├── plugin.json               # manifest（name = 命名空间前缀）
│   └── marketplace.json
├── rules/
│   └── devpace-rules.md          # 运行时行为规则（自动加载）
├── skills/
│   ├── pace-xxx/                 # 每 Skill 一个目录
│   │   ├── SKILL.md              # 路由（"做什么"）
│   │   └── *-procedures*.md      # 步骤（"怎么做"，可多个）
│   └── scripts/                  # Skill 共享脚本
├── knowledge/
│   ├── _schema/*-format.md       # 数据格式契约
│   └── *.md                      # theory、metrics、signal-* 等
├── hooks/
│   ├── hooks.json                # 事件注册
│   ├── lib/                      # 共享工具库
│   ├── skill/                    # Skill 作用域 Hook
│   └── *.mjs / *.sh
├── agents/pace-*.md              # Agent 定义
├── output-styles/                # 输出风格定义
└── settings.json                 # Plugin 默认配置
```

## §2 开发层目录结构

```
devpace/
├── .claude/
│   ├── CLAUDE.md                 # 项目入口（分层约束权威源）
│   ├── rules/                    # 开发规范（自动加载）
│   └── references/               # 按需参考文档
├── docs/
│   ├── design/                   # vision.md、design.md
│   ├── planning/                 # roadmap、progress、requirements
│   ├── features/                 # 特性文档
│   ├── research/ | plans/        # 调研记录 | 实施计划
│   ├── brand/                    # 品牌资产
│   └── scratch/                  # 临时草稿
├── dev-scripts/                  # validate-all.sh 等
├── tests/
│   ├── static/                   # 静态检查
│   ├── evaluation/pace-xxx/      # Skill 评估（每 Skill 一子目录）
│   ├── hooks/                    # Hook 测试
│   └── integration/ | scenarios/ # 集成 | 场景测试
└── examples/                     # 示例项目
```

## §3 新文件放置决策树

```
新文件
├─ Plugin 运行时需要？
│  ├─ 行为规则 → rules/          ├─ Hook → hooks/（Skill 域 → hooks/skill/）
│  ├─ Skill → skills/pace-xxx/   ├─ Agent → agents/
│  ├─ Schema → knowledge/_schema/ └─ 输出风格 → output-styles/
│  └─ 参考知识 → knowledge/
├─ 开发规范？ → 自动加载 .claude/rules/ | 按需 .claude/references/
├─ 文档？ → design/ | planning/ | features/ | research/ | plans/（均在 docs/ 下）
├─ 测试？ → static/ | evaluation/pace-xxx/ | hooks/ | integration/ | scenarios/（均在 tests/ 下）
├─ 脚本 → dev-scripts/  |  CI/CD → .github/workflows/
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
