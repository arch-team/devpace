# devpace — 开发节奏管理器

> 一个 Claude Code Plugin，详见 [vision.md](../docs/design/vision.md)。

## 开发守则

1. **概念模型始终完整**：BR→PF→CR 价值链从第一天就存在，不可省略任何环节。内容可为空但结构必须完整
2. **Markdown 是唯一格式**：消费者是 LLM + 人类，不使用 YAML/JSON 作为状态文件格式
3. **Schema 是契约**：`knowledge/_schema/` 中的格式定义是强约束，Skill 输出必须符合 Schema
4. **plugin.json 必须与文件系统同步**：新增/删除 Skill 后立即更新 `.claude-plugin/plugin.json`
5. **Rules 是分发规范，不是开发规范**：`rules/devpace-rules.md` 面向 Plugin 用户，开发规范在 `.claude/rules/`
6. **UX 优先**：零摩擦、渐进暴露、副产物非前置、容错恢复（设计原则见 `design.md §二`）
7. **理论对齐**：新增功能或调整概念模型时，对照 `docs/reference/theory.md` 确保一致性

## 目录结构

```
devpace/
├── .claude/                    # 开发层：开发 devpace 本身的规范
│   ├── CLAUDE.md               # 本文件
│   └── rules/common.md         # 语言、Git、命名规范
├── .claude-plugin/plugin.json  # Plugin 入口声明
├── docs/                       # 开发层：项目文档
│   ├── design/
│   │   ├── vision.md           # 北极星、OBJ、MoS
│   │   ├── design.md           # 设计规范：UX、概念模型、格式决策、变更管理设计
│   │   └── workflow-spec.md    # 工作流规范：Phase 0-5、CR 状态机、质量门
│   ├── planning/
│   │   ├── requirements.md     # 需求场景 S1-S9、功能需求 F1-F3
│   │   └── roadmap.md          # 里程碑追踪
│   └── reference/
│       └── theory.md           # BizDevOps 理论（双重角色：开发参考 + /pace-guide 运行时）
├── knowledge/_schema/          # 状态文件格式契约
├── rules/devpace-rules.md      # 运行时行为协议（随 Plugin 分发）
└── skills/                     # 产品层：7 个 Slash Commands
    ├── pace-init/              # 含 templates/（含 claude-md-devpace.md）
    ├── pace-advance/
    ├── pace-change/
    ├── pace-guide/
    ├── pace-retro/
    ├── pace-review/
    └── pace-status/
```

## 开发验证

```bash
# 加载 Plugin 测试
claude --plugin-dir ./

# 在 diagnostic-agent-framework 中测试
cd /Users/jinhuasu/Project_Workspace/Anker-Projects/diagnostic-agent-framework
claude --plugin-dir ../ml-platform-research/llm-platform-solution/claude-code-forge/devpace
```

## 会话协议

1. **开始**：读取 `docs/planning/roadmap.md` → 识别当前 Milestone 和待做任务
2. **执行**：加载参考 → 实现 → 质量检查
3. **结束**：更新 `docs/planning/roadmap.md`（Milestone 状态 + 变更记录）

## 权威文件索引

| 概念 | 权威文件 | 权威范围 |
|------|---------|---------|
| 北极星、OBJ、MoS | `vision.md` | 为什么做、做什么 |
| UX 原则（P1-P7） | `design.md §二` | 设计约束 |
| 概念模型映射 | `design.md §三` | BR/PF/CR 如何对应到实现 |
| CR 状态机 | `workflow-spec.md §3` | 状态、转换、门禁完整定义 |
| 端到端工作流（Phase 0-5） | `workflow-spec.md` | 完整流程、Skill 映射 |
| 质量门系统 | `workflow-spec.md §5` | Gate 1/2/3 定义 |
| 变更管理设计 | `design.md §六` | 为什么和四个场景 |
| 变更管理操作流程 | `workflow-spec.md §4.3` | Phase 3 何时、怎么做 |
| BizDevOps 理论 | `theory.md` | 方法论参考（双重角色：开发参考 + /pace-guide 运行时） |
| 需求场景 S1-S9 | `requirements.md` | 验收标准 |
| 功能需求 F1-F3 | `requirements.md` | 特性规格 |
| 项目进度 | `roadmap.md` | 里程碑和当前任务 |
| 运行时行为规则 | `devpace-rules.md` | 插件加载后 Claude 的行为 |
| 文件格式契约 | `_schema/*.md` | state/project/CR 的字段定义 |

### 开发规范索引（.claude/rules/，自动加载）

| 规范文件 | 职责 |
|---------|------|
| `common.md` | 响应语言、Git 提交规范、文档命名 |

## 质量检查

- plugin.json 与文件系统同步（新增/删除 Skill 后立即更新）
- 每个 rules/ 和 _schema/ 文件有 §0 速查卡片
- 模板文件用 `{{PLACEHOLDER}}` 标记需填充的内容
- Skill 的 SKILL.md 遵循 claude-code-forge 的 frontmatter 规范
