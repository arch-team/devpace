# devpace — 开发节奏管理器

> **职责**：给 Claude Code 项目一个稳定的研发节奏——需求在变，节奏不乱。

## 项目定位

一个 Claude Code Plugin，通过 Rules 注入行为协议 + Skills 提供交互入口 + Markdown 模板管理项目状态，让 Claude Code 具备跨会话的研发流程感知能力。理论基础见 `docs/reference/theory.md`。

**目标用户**：使用 Claude Code 持续迭代产品的开发者——在多个会话中推进有业务目标的项目。

## 注意事项

- **概念模型始终完整**：BR→PF→CR 价值链从第一天就存在，不可省略任何环节。内容可为空但结构必须完整
- **Markdown 是唯一格式**：消费者是 LLM + 人类，不使用 YAML/JSON 作为状态文件格式
- **Schema 是契约**：`knowledge/_schema/` 中的格式定义是强约束。Skill 输出必须符合 Schema
- **plugin.json 必须与文件系统同步**：新增/删除 Skill 后立即更新 `.claude-plugin/plugin.json`
- **Rules 是分发规范，不是开发规范**：`rules/devpace-rules.md` 面向 Plugin 用户，开发规范在 `.claude/rules/`

## 核心设计

- **概念模型始终完整**：BR→PF→CR 从第一天就存在，内容随迭代自然丰富，文件结构按信息量扩展
- **Claude 自治为主**：技术闭环（developing→verifying）自主推进，human_review 质量检查等待人类
- **Markdown 格式**：消费者是 LLM + 人类，不是传统解析器
- **UX 优先**：零摩擦、渐进暴露、副产物非前置、容错恢复
- **变更韧性**：变更是一等公民，核心差异化能力

## 理论基础

devpace 的设计基于 BizDevOps 方法论。在新增功能、调整设计、做架构决策时，需对照 `docs/reference/theory.md` 中的概念模型确保一致性。关键概念：
- **概念模型三要素**：作业对象 × 作业空间 × 作业规则
- **价值交付链路**：BR → PF → CR → 发布（双向追溯，始终完整，内容渐进丰富）
- **三个闭环**：业务闭环(人类) → 产品闭环(人机) → 技术闭环(Claude 自治)
- **专题模式**：变更是常态，用 MoS 衡量成效而非固定范围
- **渐进丰富**：概念模型始终完整，文件结构按信息量自然扩展（见 `docs/design/design.md`）

## 目录结构

- `rules/` — 自动注入的行为协议（随 Plugin 分发）
- `skills/` — 7 个 Slash Commands（pace-init/status/advance/review/retro/change/guide）
- `knowledge/_schema/` — 状态文件格式契约（cr-format.md、project-format.md、state-format.md）
- `docs/` — 项目文档
  - `reference/` — 方法论知识库：theory.md
  - `design/` — 产品设计：vision.md → design.md → model-panorama.md
  - `planning/` — 项目规划：requirements.md → roadmap.md

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

### 参考文档索引

| 文档 | 何时读取 |
|------|---------|
| `docs/planning/roadmap.md` | **每次会话开始**（必读） |
| `docs/reference/theory.md` | 新增功能或调整概念模型时（BizDevOps 理论基础） |
| `docs/design/design.md` | 修改 UX 行为、状态机、质量门时（产品设计规范） |
| `docs/design/model-panorama.md` | 需要理解概念模型间关系时（10 模型全景） |
| `docs/planning/requirements.md` | 确认需求范围或优先级时（场景 S1-S9、功能需求 F1-F3） |
| `docs/design/vision.md` | 需要理解项目北极星和 OBJ 时 |

### 开发规范索引（.claude/rules/，自动加载）

| 规范文件 | 职责 |
|---------|------|
| `common.md` | 响应语言、Git 提交规范、文档命名 |

## 质量检查

- plugin.json 与文件系统同步（新增/删除 Skill 后立即更新）
- 每个 rules/ 和 _schema/ 文件有 §0 速查卡片
- 模板文件用 `{{PLACEHOLDER}}` 标记需填充的内容
- Skill 的 SKILL.md 遵循 claude-code-forge 的 frontmatter 规范
