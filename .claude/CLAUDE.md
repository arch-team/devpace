# devpace — 开发节奏管理器

> **devpace** 是一个 Claude Code 插件，为 AI 辅助开发带来完整的 BizDevOps 研发节奏管理。它将"业务目标→产品功能→代码变更"串成一条可追溯的价值链，让 Claude 不只是写代码的工具，而是理解业务意图的研发协作者。会话中断？自动恢复上下文，无需重复解释。需求变更？即时评估影响范围，有序调整而非推倒重来。质量跑偏？内置门禁自动拦截，未就绪的变更无法流入下游。**需求永远在变，但从规划到交付的研发节奏，不应该因此失控。**

详见 [vision.md](../docs/design/vision.md)。

## 分层架构（硬性要求）

devpace 分为两个独立层次，**产品层不得依赖开发层**：

| 层次 | 目录 | 职责 | 分发 |
|------|------|------|------|
| **开发层** | `.claude/`、`docs/` | 开发 devpace 本身的规范和设计文档 | 不分发 |
| **产品层** | `rules/`、`skills/`、`knowledge/`、`.claude-plugin/` | Plugin 运行时资产，分发给用户 | 随 Plugin 分发 |

**硬性约束**：

1. **产品层独立可分发**：`rules/`、`skills/`、`knowledge/`、`.claude-plugin/` 必须作为独立整体分发，不依赖 `.claude/` 和 `docs/` 中的任何文件
2. **禁止产品→开发引用**：产品层文件（rules/、skills/、knowledge/）中不得出现指向 `docs/` 或 `.claude/` 的路径引用
3. **开发→产品引用允许**：开发层文件（.claude/CLAUDE.md、docs/design.md 等）可以引用产品层文件
4. **共享知识归产品层**：如果一份内容同时被开发和产品使用（如 theory.md），它必须放在产品层（knowledge/），开发层引用它

**检查方法**：`grep -r "docs/\|\.claude/" rules/ skills/ knowledge/` 应返回空结果。

## 开发守则

1. **概念模型始终完整**：BR→PF→CR 价值链从第一天就存在，不可省略任何环节。内容可为空但结构必须完整
2. **Markdown 是唯一格式**：消费者是 LLM + 人类，不使用 YAML/JSON 作为状态文件格式
3. **Schema 是契约**：`knowledge/_schema/` 中的格式定义是强约束，Skill 输出必须符合 Schema
4. **plugin.json 必须与文件系统同步**：新增/删除 Skill 后立即更新 `.claude-plugin/plugin.json`
5. **Rules 是分发规范，不是开发规范**：`rules/devpace-rules.md` 面向 Plugin 用户，开发规范在 `.claude/rules/`
6. **UX 优先**：零摩擦、渐进暴露、副产物非前置、容错恢复（设计原则见 `design.md §2`）
7. **理论对齐**：新增功能或调整概念模型时，对照 `knowledge/theory.md` 确保一致性

## 目录结构

```
devpace/
├── .claude/                    # 开发层：开发 devpace 本身的规范
│   ├── CLAUDE.md               # 本文件
│   └── rules/common.md         # 语言、Git、命名规范
├── .claude-plugin/plugin.json  # Plugin 入口声明
├── docs/                       # 开发层：项目文档（不随 Plugin 分发）
│   ├── design/
│   │   ├── vision.md           # 北极星、OBJ、MoS
│   │   └── design.md           # 完整设计方案
│   └── planning/
│       ├── requirements.md     # 需求场景 S1-S9、功能需求 F1-F3
│       └── roadmap.md          # 里程碑追踪
├── knowledge/                  # 产品层：运行时知识
│   ├── _schema/                #   格式契约
│   ├── metrics.md              #   度量指标定义
│   └── theory.md               #   BizDevOps 理论（/pace-guide 运行时数据源）
├── rules/devpace-rules.md      # 产品层：运行时行为协议
└── skills/                     # 产品层：7 个 Slash Commands
    ├── pace-init/              #   含 templates/（含 claude-md-devpace.md）
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

# 分层完整性检查（产品层不得引用开发层）
grep -r "docs/\|\.claude/" rules/ skills/ knowledge/
# 期望：无输出
```

## 会话协议

1. **开始**：读取 `docs/planning/roadmap.md` → 识别当前 Milestone 和待做任务
2. **执行**：加载参考 → 实现 → 质量检查
3. **结束**：更新 `docs/planning/roadmap.md`（Milestone 状态 + 变更记录）

## 权威文件索引

| 概念 | 权威文件 | 权威范围 |
|------|---------|---------|
| 北极星、OBJ、MoS | `docs/design/vision.md` | 为什么做、做什么 |
| UX 原则（P1-P7） | `docs/design/design.md §2` | 设计约束 |
| 概念模型映射 | `docs/design/design.md §3` | 价值交付链路、闭环、渐进丰富 |
| 端到端工作流（Phase 0-5） | `docs/design/design.md §4` | 完整流程、Skill 映射 |
| CR 状态机 | `docs/design/design.md §5` | 状态、转换、门禁完整定义 |
| 质量门系统 | `docs/design/design.md §6` | Gate 1/2/3 定义 |
| 变更管理 | `docs/design/design.md §7` | 设计原则、四种场景、操作流程 |
| BizDevOps 理论 | `knowledge/theory.md` | 方法论参考（/pace-guide 运行时数据源） |
| 需求场景 S1-S9 | `docs/planning/requirements.md` | 验收标准 |
| 功能需求 F1-F3 | `docs/planning/requirements.md` | 特性规格 |
| 项目进度 | `docs/planning/roadmap.md` | 里程碑和当前任务 |
| 运行时行为规则 | `rules/devpace-rules.md` | 插件加载后 Claude 的行为 |
| 文件格式契约 | `knowledge/_schema/*.md` | state/project/CR 的字段定义 |
| 度量指标定义 | `knowledge/metrics.md` | 指标名称、计算方式、用途 |

### 开发规范索引（.claude/rules/，自动加载）

| 规范文件 | 职责 |
|---------|------|
| `common.md` | 响应语言、Git 提交规范、文档命名 |

## 质量检查

- plugin.json 与文件系统同步（新增/删除 Skill 后立即更新）
- 每个 rules/ 和 _schema/ 文件有 §0 速查卡片
- 模板文件用 `{{PLACEHOLDER}}` 标记需填充的内容
- Skill 的 SKILL.md 遵循 claude-code-forge 的 frontmatter 规范
- Skill 分拆模式：SKILL.md 放输入/输出/高层步骤（"做什么"），当详细规则超过 ~50 行时拆出 `*-procedures.md`（"怎么做"）。参考 pace-advance 和 pace-change
- **分层完整性**：产品层文件不得引用 `docs/` 或 `.claude/`（见分层架构章节）
