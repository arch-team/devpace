# Claude Code 生态开源项目深度调研（增量）

> **调研日期**：2026-02-24 | **基准**：ecosystem-benchmarking.md（2026-02-22） | **方法**：Agent Teams 4 Agent 并行调研（Tavily + WebFetch） | **覆盖盲区**：7 个

---

## 一、调研概览

### 本次增量调研背景

上次调研（2026-02-22）覆盖 30+ 项目，确认 devpace 在"价值链追溯 + CR 状态机 + 变更管理 + 质量门禁 + 度量体系"组合上的生态唯一性。本次聚焦 7 个盲区的增量发现。

### 盲区覆盖情况

| # | 盲区 | Agent | 发现数 | 关键发现 |
|---|------|-------|--------|---------|
| 1 | 生态最新动态 | ecosystem-scout | 12+ 新/更新项目 | Superpowers 进入官方 Marketplace；Skill 市场已规模化（63K+ Skills） |
| 2 | Skills 设计模式 | skill-architect | 8 种架构模式 | 官方推荐"pushy" description；Coordinator-Agents 模式；分拆模式获验证 |
| 3 | 可直接使用的优化工具 | toolchain-hunter | 15 个工具 | 官方 plugin-dev 工具包；markdownlint-cli2；5 个生态空白 |
| 4 | Plugin 开发工具链 | toolchain-hunter | 5 层全景 | 模板/测试/验证/发布/CI 完整链路 |
| 5 | MCP Server 研发管理 | integration-researcher | 10+ MCP Server | GitHub MCP（27.2K）覆盖 Issues+Actions+Security；"MCP 可选增强"模式 |
| 6 | Skill 市场模式 | ecosystem-scout | 12+ 平台 | 多层次分发体系成型；安全问题突出（17-20% 恶意 Skill） |
| 7 | Agent Teams | skill-architect | 6 种协作模式 | 官方 Agent Teams 实验性；3-5 人团队最佳；FlowPilot 全自动编排 |

---

## 二、生态动态增量（盲区 #1）

### 2.1 核心数据快照（2026-02-24）

| 指标 | 值 | 来源 |
|------|---|------|
| GitHub "claude-code-plugin" topic 仓库数 | 564 | github.com/topics/claude-code-plugin |
| claude-plugins.dev 索引量 | 11,989 Plugins + 63,065 Skills | blog.brightcoding.dev |
| claudemarketplaces.com 收录 Skills | 751 | claudemarketplaces.com/skills |
| Anthropic Skills 官方仓库 | 74,014 Stars | github.com/anthropics/skills |
| Claude Code 最新版本 | v2.1.45 | releasebot.io |

### 2.2 已知项目 Star 变化（2 天增量）

| 项目 | 上次 | 当前 | 增长 | 主要更新 |
|------|------|------|------|---------|
| Superpowers (obra) | 51,800 | 59,286 | +7,486 | 进入 Anthropic 官方 Marketplace |
| Everything Claude Code | 47,200 | 50,394 | +3,194 | v1.4.0 多语言 Rules + OpenCode 集成 |
| claude-mem | 28,700 | 30,600 | +1,900 | 持续活跃 |
| claude-flow | 11,400 | 14,395 | +2,995 | — |

### 2.3 新发现项目（上次未覆盖）

#### Tier A：密切关注

| 项目 | Stars | 定位 | 对 devpace 的意义 |
|------|-------|------|------------------|
| **wshobson/agents** | 29,200 | 智能自动化 Plugin 生态（72 Plugins, 112 Agents, 146 Skills, 16 Orchestrators） | 最大的 Plugin Marketplace 之一；Conductor Agent 有结构化项目管理 |
| **VoltAgent/awesome-agent-skills** | 7,800 | 跨 8 款 AI 工具的 Skills 聚合（383+ Skills） | 跨平台 Skill 标准参考 |
| **tech-leads-club/agent-skills** | 1,500 | 安全验证的跨 18 款 AI 工具 Skill 注册中心 | 四层安全验证模式可借鉴 |
| **FlowPilot (6BNBN)** | — | 基于 Agent Teams 的全自动工作流调度引擎 | 三层记忆架构，状态持久化+中断恢复 |

#### Tier B：参考价值

| 项目 | Stars | 定位 | URL |
|------|-------|------|-----|
| ComposioHQ/awesome-claude-plugins | 1,200 | Plugin 精选列表 + 500+ App 连接器 | github.com/ComposioHQ/awesome-claude-plugins |
| kenryu42/claude-code-safety-net | 1,100 | 破坏性命令拦截 | github.com/kenryu42/claude-code-safety-net |
| zscole/adversarial-spec | 496 | 多 LLM 对抗式需求精炼 | github.com/zscole/adversarial-spec |
| gmickel/flow-next | 525 | 计划优先工作流 + 多模型审查门 | github.com/gmickel/gmickel-claude-marketplace |
| agenticnotetaking/arscontexta | 1,700 | 对话→个性化知识系统 | github.com/agenticnotetaking/arscontexta |

### 2.4 生态重大事件

1. **Superpowers 进入官方 Marketplace**：通过 `/plugin marketplace add obra/superpowers-marketplace` 安装，标志着社区项目与官方生态的融合
2. **Claude Cowork 发布**：与 Claude Code 共享 Skill 格式，Skill 正式成为 Anthropic 生态通用标准
3. **OpenClaw 安全问题**：17-20% Skills 含恶意内容（AIMLAPI 报告），凸显安全验证分发的价值
4. **AgentShield 安全审计工具**：912 测试、98% 覆盖率，扫描 CLAUDE.md/settings/MCP/Hooks/Agent/Skills

---

## 三、Skills 设计模式横向对比（盲区 #2）

### 3.1 设计模式对比矩阵

| 维度 | devpace | feature-dev (官方) | skill-creator (官方) | flow-next | plan-and-execute |
|------|---------|-------------------|---------------------|-----------|------------------|
| 结构 | **分拆模式** (SKILL.md + procedures) | Commands 模式 (单文件) | 超大单文件 (~760行) + agents/ + references/ | 分拆模式 (SKILL.md + steps/phases) | 单文件 SKILL.md |
| description | CSO (只写触发条件) | 简短一行 | 长 description + 场景列举 | 长 description + 排除声明 | "Use when..." + 排除 |
| Agent 路由 | context:fork (3 Agent) | Task 工具手动调用 (3 Agent) | coordinator 手动 spawn | 无 | user-invocable:false + dispatch |
| Skill 间协作 | 价值链串联 | Phase 内串联 (7 Phase) | Mode 切换 | CLI 串联 | 链式调用 |
| Model 指定 | tiering (opus/sonnet/haiku) | 全部 sonnet | 无 | 无 | 无 |
| allowed-tools | 按角色限制 | Agent 级限制 | 无 | 无 | 无 |
| 状态管理 | Markdown 直接读写 | 无持久状态 | Workspace 目录 | CLI (flowctl) 封装 | 无 |

### 3.2 8 种可借鉴的架构模式

| # | 模式 | 来源 | 描述 | devpace 适配建议 |
|---|------|------|------|-----------------|
| 1 | **Coordinator-Agents** | skill-creator (官方) | SKILL.md 作指挥中心，定义 Building Blocks (Input→Output→Agent 映射) | 为 pace-test 等复杂 Skill 引入 Building Block 概念 |
| 2 | **Phase-Gate-Agent** | feature-dev (官方) | 7-Phase 工作流 + 用户审批门禁 + Agent 颜色标识 + Confidence Scoring | Agent 颜色标识 + 可信度评分 |
| 3 | **CLI-Mediated Workflow** | flow-next | 用 CLI 封装状态操作，SKILL.md 引用 CLI 命令 | 评估 CLI 封装 devpace 状态操作 |
| 4 | **Exclusion Declaration** | flow-next | description 中显式声明"不要用此 Skill"的场景 | 易混淆 Skill 对加入排除声明 |
| 5 | **Pushy Description** | skill-creator (官方) | 官方建议 description "a little bit pushy"，穷举触发场景 | 适度增加 description 触发覆盖面 |
| 6 | **Delegated Reading** | cartographer | "Opus orchestrates, Sonnet reads"，主 Agent 不直接读文件 | 大型分析场景减少主 agent token 消耗 |
| 7 | **Progressive Disclosure** | 官方文档 | 三层加载：Metadata(100 words) → SKILL.md(<500 lines) → Bundled Resources | devpace 分拆模式已对齐，明确 procedures.md = bundled references |
| 8 | **Human Transparency** | plan-and-execute | 子 agent 返回必须完整展示给用户，不得总结压缩 | pace-dev Engineer 执行后关键变更透明呈现 |

### 3.3 关键发现

1. **devpace 的分拆模式获生态验证**：官方 Progressive Disclosure 三层加载与 devpace 的 SKILL.md + procedures.md 模式一致
2. **CSO 策略偏保守**：官方 skill-creator 建议 description "a little bit pushy"，devpace 的 CSO 可适度放宽
3. **context:fork 是先进实践**：生态中仅 devpace 使用 context:fork 做 Skill→Agent 路由，多数项目用 Task 手动调用
4. **Model Tiering 是差异化**：生态中仅 devpace 有系统化的 opus/sonnet/haiku 任务分配策略

---

## 四、Agent Teams / Multi-agent 实践（盲区 #7）

### 4.1 官方 Agent Teams 状态

- **状态**：实验性功能（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`）
- **最佳实践**：3-5 人团队 / 每人 5-6 tasks / 避免同文件冲突 / 先研究后实现
- **质量门 Hook**：`TeammateIdle`（exit 2 可反馈继续）、`TaskCompleted`（exit 2 可阻止完成）
- **Plan Approval 模式**：可要求 teammate 先提交计划，lead 审批后再实现

### 4.2 Multi-Agent 协作模式

| 模式 | 典型项目 | devpace 现状 | 启发 |
|------|---------|-------------|------|
| Leader-Worker | Agent Teams 官方 | PM→Engineer 已类似 | 验证现有模式 |
| Peer-to-Peer | Agent Teams | 未使用 | Engineer ↔ Analyst 互通 |
| Coordinator-Agents | skill-creator | 部分使用 | Building Block 概念 |
| Competing Hypotheses | Agent Teams debug | 未使用 | pace-retro 多假设并行 |
| CLI-Mediated | flow-next | 未使用 | 状态操作 CLI 封装 |
| Delegated Reading | cartographer | 未使用 | 大型分析 token 优化 |

### 4.3 外部编排工具

| 工具 | 定位 | 与 Agent Teams 关系 |
|------|------|-------------------|
| **Claude Squad** (~10K Stars) | 终端级多实例管理器 | 外部编排器，独立 git workspace |
| **FlowPilot** | 全自动工作流调度引擎 | 基于 Agent Teams，三层记忆架构 |
| **AgentSpeak** | Agent 间 token-efficient 通讯协议 | 减少 60-70% 消息 token |
| **AgentSpec** | 结构化 Agent 角色/规则/门禁模板 | JSON 模板定义验证流+防漂移 |

---

## 五、可直接使用的优化工具（盲区 #3）

### 5.1 P0 工具（强烈推荐，立即集成）

| 工具 | 用途 | Stars | devpace 集成点 | URL |
|------|------|-------|--------------|-----|
| **plugin-dev** (官方) | Plugin 验证/脚手架/审查（7 Skill + 3 Agent + 6 脚本） | 官方 | 开发 + Gate 1 | github.com/anthropics/claude-code/plugins/plugin-dev |
| **markdownlint-cli2** | Markdown 格式校验（50+ 规则 + auto-fix + CI 输出） | 701 | Gate 1 / CI | github.com/DavidAnson/markdownlint-cli2 |
| **gray-matter** | YAML frontmatter 解析验证 | 4,400 | Gate 1 / Hook | github.com/jonschlinkert/gray-matter |
| **ajv** | JSON Schema 验证引擎 | 14,600 | Gate 1 | github.com/ajv-validator/ajv |

### 5.2 P1 工具（推荐，近期集成）

| 工具 | 用途 | Stars | devpace 集成点 | URL |
|------|------|-------|--------------|-----|
| remark-lint-frontmatter-schema | frontmatter JSON Schema 校验 | 72 | Gate 1 | github.com/JulianCataldo/remark-lint-frontmatter-schema |
| claude-code-plugin-template | Plugin Marketplace 模板 + CI workflow | 40 | 发布流程 | github.com/ivan-magda/claude-code-plugin-template |
| OrchestKit (SkillForge) | 综合质量门禁 Hook 系统（86 Hook） | 87 | Hook 参考 | github.com/yonatangross/skillforge-claude-plugin |

### 5.3 生态空白（devpace 潜在差异化方向）

当前生态中**无人提供**的工具：

1. **SKILL.md 语义验证器**——验证 description 是否符合 CSO/pushy 编写规则
2. **Plugin 依赖分析器**——分析 Skill 之间的依赖关系和冲突
3. **Plugin 性能 Profiler**——衡量 Skill 的 token 消耗和响应质量
4. **自动化回归测试**——检测 Skill 行为变化（input → output 对比）
5. **Marketplace 版本对比**——不同版本 Plugin 差异分析

---

## 六、Plugin 开发工具链（盲区 #4）

### 6.1 全景图

| 层次 | 当前 devpace | 推荐增强 |
|------|-------------|---------|
| **模板/脚手架** | 无 | 官方 plugin-dev + claude-code-plugin-template |
| **静态测试** | pytest 204 测试 | 保留 + 增加 markdownlint-cli2 |
| **frontmatter 验证** | test_frontmatter.py | 增加 gray-matter + ajv Schema 验证 |
| **Plugin 结构验证** | test_plugin_json_sync.py | 增加 `claude plugin validate .` |
| **Hook 测试** | 无 | Vitest（原生 ESM 支持） |
| **E2E 验证** | 手动 --plugin-dir | Shell 脚本自动化 |
| **CI/CD** | 无 | GitHub Actions（markdownlint + pytest + plugin validate） |
| **发布** | marketplace.json 手动 | `claude plugin validate .` 预发布验证 |

### 6.2 推荐 CI Workflow 骨架

```yaml
name: devpace CI
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: DavidAnson/markdownlint-cli2-action@v22
        with:
          globs: "rules/**/*.md\nskills/**/SKILL.md\nknowledge/**/*.md"
      - run: pip install pytest && pytest tests/static/ -v
      - run: npx claude plugin validate .
```

---

## 七、MCP Server 研发管理集成（盲区 #5）

### 7.1 MCP Server 全景图

| 类别 | MCP Server | Stars | 成熟度 | devpace 集成点 |
|------|-----------|-------|--------|--------------|
| **项目管理** | GitHub MCP (官方) | 27,200 | Stable | BR/PF/CR 同步 Issues + Gate 4 Actions |
| | Atlassian Remote MCP (官方) | 闭源 | Stable | CR 同步 Jira Issues |
| | Azure DevOps MCP (微软) | 1,300 | Stable | CR 同步 + Pipeline 状态 |
| | GitLab MCP (zereight) | 1,100 | Beta | CR 同步 MR + Pipeline 状态 |
| **CI/CD** | GitHub MCP (含 Actions) | 同上 | Stable | Gate 4 CI 状态查询 |
| | GitLab MCP (含 Pipelines) | 同上 | Beta | Gate 4 Pipeline 状态 |
| | Jenkins MCP (kud) | 1 | Alpha | Gate 4 Jenkins 查询 |
| **代码质量** | SonarQube MCP (官方) | 393 | Stable | Gate 1/2 质量报告 |
| | Sentry MCP (官方) | 564 | Stable | 错误监控 + Gate 1 |
| **安全扫描** | Snyk Studio MCP (官方) | — | Stable | Gate 1 安全扫描 |
| | GitHub MCP (Code Security) | 同上 | Stable | Gate 1 安全检查 |

### 7.2 推荐集成策略："MCP 可选增强"模式

| 层次 | 无 MCP | 有 MCP |
|------|--------|--------|
| CI 工具检测 | Glob 扫描配置文件 | 同左（不需要 MCP） |
| CI 状态查询 | shell 命令（`gh run list`） | MCP 工具（更丰富数据） |
| Issue 同步 | 手动 | MCP 自动同步 |
| 质量报告 | 本地 checks.md | SonarQube MCP 增强报告 |
| 安全扫描 | 无 | Snyk MCP 扫描 |

### 7.3 T97 支持方案

**Tier 1（P0，不依赖 MCP）**：Glob 检测 CI 配置文件 + shell 命令检查状态

| 检测文件 | CI 工具 | 检查命令 |
|---------|---------|---------|
| `.github/workflows/` | GitHub Actions | `gh run list --limit 1` |
| `.gitlab-ci.yml` | GitLab CI | `glab ci status` |
| `Jenkinsfile` | Jenkins | CLI |
| `azure-pipelines.yml` | Azure Pipelines | MCP |

**Tier 2（P1，MCP 增强）**：GitHub MCP 一个 Server 覆盖 Issues + Actions + Security

### 7.4 integrations-format.md 扩展建议

新增 section：Issue Tracker / 代码质量 / 安全扫描 / 错误监控 / MCP Server 配置

---

## 八、Skill 市场模式（盲区 #6）

### 8.1 多层次分发体系

| 层次 | 平台 | 规模 | 模式 |
|------|------|------|------|
| **官方** | Anthropic Skills 仓库 | 74K Stars | 高质量官方维护 |
| **大型索引** | claude-plugins.dev | 11,989 Plugins + 63,065 Skills | 自动爬取 GitHub |
| **大型索引** | skillsmp.com | 200K+ Skills | GitHub 索引 |
| **评级市场** | skillhub.club | 7,000+ Skills | AI 评分 + 桌面应用 |
| **精选列表** | VoltAgent/awesome-agent-skills | 7,800 Stars, 383+ Skills | 跨 8 款 AI 工具 |
| **安全注册** | tech-leads-club/agent-skills | 1,500 Stars | 四层安全验证 |

### 8.2 Skill 组合模式

| 模式 | 代表项目 | 描述 |
|------|---------|------|
| **Team Routing** | catlog22/Claude-Code-Workflow | 统一入口 + --role 参数路由 |
| **Pipeline** | obra/superpowers | brainstorm → plan → execute → verify |
| **Agent Teams + Skill Matrix** | wshobson/agents | 预定义团队 + Orchestrator 协调 |
| **Meta-Skill** | 多项目 | 基础 Skills 组合 = 完整能力 |
| **Progressive Disclosure** | wshobson/agents | 三层加载（Metadata → 指令 → 资源） |

### 8.3 安全与信任

| 风险 | 应对 |
|------|------|
| 恶意 Skill（17-20%） | tech-leads-club 四层验证；AgentShield 静态分析 |
| 提示注入 | 人工审核 + 静态分析 |
| 供应链攻击 | 锁文件 + 内容哈希；SHA pinning（v2.1.14+） |

---

## 九、可操作建议清单（按优先级）

### P0（强烈推荐，下一迭代）

| # | 建议 | 来源 | devpace 模块 | Phase 16 关联 |
|---|------|------|-------------|-------------|
| P0-1 | **description 策略微调**：适度增加触发覆盖面；易混淆 Skill 对加排除声明 | skill-creator 官方 | skills/*/SKILL.md | — |
| P0-2 | **集成官方 plugin-dev 工具**：Plugin 验证 + Skill 审查 | Anthropic 官方 | 开发工具链 | — |
| P0-3 | **添加 markdownlint-cli2**：Gate 1 + CI 的 Markdown 格式校验 | DavidAnson/markdownlint-cli2 | Gate 1 / CI | — |
| P0-4 | **T97 Tier 1 实现**：Glob 检测 CI 配置 + shell 命令检查 | integration-researcher | T97 | T97 |
| P0-5 | **注册到聚合平台**：claudemarketplaces.com + VoltAgent + GitHub Topics | ecosystem-scout | 分发策略 | — |

### P1（推荐，2-3 个迭代内）

| # | 建议 | 来源 | devpace 模块 | Phase 16 关联 |
|---|------|------|-------------|-------------|
| P1-1 | **Agent 颜色标识**：PM(蓝)/Engineer(绿)/Analyst(黄) | feature-dev 官方 | agents/ | — |
| P1-2 | **GitHub MCP 集成**：Issues + Actions + Security | GitHub MCP (27.2K) | T97 MCP 增强 | T97 |
| P1-3 | **Confidence Scoring**：pace-test accept 可信度评分 | feature-dev | skills/pace-test/ | — |
| P1-4 | **Vitest Hook 测试**：Node.js ESM Hook 单元测试 | toolchain-hunter | hooks/ | — |
| P1-5 | **GitHub Actions CI**：markdownlint + pytest + plugin validate | plugin-template | CI/CD | T97 |
| P1-6 | **integrations-format 扩展**：Issue Tracker/质量/安全/监控 section | integration-researcher | knowledge/_schema/ | T97 |
| P1-7 | **Graceful Degradation**：context:fork 不可用时 inline 执行 | skill-creator | skills/ | — |
| P1-8 | **SonarQube MCP 集成**：Gate 1/2 质量报告增强 | SonarQube MCP (393) | Gate 1/2 | — |

### P2（可选，长期方向）

| # | 建议 | 来源 | devpace 模块 | Phase 16 关联 |
|---|------|------|-------------|-------------|
| P2-1 | **Building Block 概念**：pace-test Input→Output→Agent 映射表 | skill-creator | skills/pace-test/ | — |
| P2-2 | **Delegated Reading**：大型分析 Opus 编排 + Sonnet 读取 | cartographer | agents/ | — |
| P2-3 | **CLI 状态管理封装**：参考 flow-next flowctl | flow-next | 架构方向 | — |
| P2-4 | **Human Transparency**：子 agent 关键变更完整展示 | plan-and-execute | skills/pace-dev/ | — |
| P2-5 | **Agent Teams 评估**：正式发布后评估迁移 | Agent Teams 官方 | 架构方向 | — |
| P2-6 | **SKILL.md 语义验证器**：description 合规验证（生态空白） | toolchain-hunter | 差异化工具 | — |
| P2-7 | **安全验证分发**：锁文件 + 内容哈希 | tech-leads-club | 分发策略 | — |
| P2-8 | **跨平台 Skill 兼容**：agentskills.io 开放标准 | VoltAgent | Skill 格式 | — |
| P2-9 | **Snyk MCP 安全增强**：Gate 1 全面扫描 | Snyk MCP | Gate 1 | — |

---

## 十、与已有调研的增量对比

### 新增发现 vs 2026-02-22 基线

| 维度 | 上次已覆盖 | 本次新增 |
|------|----------|---------|
| 项目数 | 30+ | +12 新项目 |
| Skill 设计模式 | 功能借鉴为主 | +8 种架构模式深度对比 |
| 工具推荐 | 无 | +15 个可直接使用的工具 |
| MCP Server | 无 | +10 个研发管理 MCP Server |
| Skill 市场 | 无 | +12 个分发平台 + 5 种组合模式 |
| Agent Teams | 未覆盖 | +6 种协作模式 + 外部编排工具 |
| 安全问题 | 未覆盖 | 17-20% 恶意 Skill + 应对方案 |

### devpace 生态定位确认

**无需调整**。本次调研进一步确认：

1. **BizDevOps 完整价值链**（OBJ→BR→PF→CR→Release）在生态中仍是唯一
2. **需求变更管理作为一等公民**（5 场景 + Triage）仍是空白
3. **多级质量门禁**（Gate 1/2/3/4）仍无对标
4. **分拆模式**（SKILL.md + procedures.md）与官方 Progressive Disclosure 一致，获生态验证
5. **context:fork + Model Tiering** 是先进实践，生态中仅 devpace 有系统化方案

---

## 十一、Phase 16 关联分析

| 待做任务 | 本次调研支持 |
|---------|------------|
| **T95 DORA 代理指标** | SonarQube MCP 可提供覆盖率数据增强 DORA 代理值 |
| **T96 跨项目经验导入** | tech-leads-club 安全验证模式可参考用于 insights 导入安全校验 |
| **T97 CI/CD 自动感知** | **直接支持**：Tier 1 Glob 检测（P0-4）+ Tier 2 GitHub MCP 集成（P1-2） |

---

## 附录：数据来源

| 来源 | URL |
|------|-----|
| GitHub Topic: claude-code-plugin | https://github.com/topics/claude-code-plugin |
| quemsah/awesome-claude-plugins | https://github.com/quemsah/awesome-claude-plugins |
| Claude Code Changelog | https://releasebot.io/updates/anthropic/claude-code |
| claudemarketplaces.com | https://claudemarketplaces.com/skills |
| VoltAgent/awesome-agent-skills | https://github.com/VoltAgent/awesome-agent-skills |
| tech-leads-club/agent-skills | https://github.com/tech-leads-club/agent-skills |
| wshobson/agents | https://github.com/wshobson/agents |
| GitHub MCP Server | https://github.com/github/github-mcp-server |
| Azure DevOps MCP | https://github.com/microsoft/azure-devops-mcp |
| GitLab MCP | https://github.com/zereight/gitlab-mcp |
| SonarQube MCP | https://github.com/SonarSource/sonarqube-mcp-server |
| Sentry MCP | https://github.com/getsentry/sentry-mcp |
| Snyk Studio MCP | https://github.com/snyk/studio-mcp |
| Anthropic 官方 Plugins | https://github.com/anthropics/claude-code/tree/main/plugins |
| flow-next | https://github.com/gmickel/gmickel-claude-marketplace |
| FlowPilot | https://github.com/6BNBN/FlowPilot |
| cartographer | https://github.com/kingbootoshi/cartographer |
| Agent Teams 文档 | https://code.claude.com/docs/en/agent-teams |
| claude-code-plugin-template | https://github.com/ivan-magda/claude-code-plugin-template |
| claude-plugins.dev 报道 | https://www.blog.brightcoding.dev/2026/02/22/claude-plugins-the-revolutionary-ai-agent-skill-manager |
| OpenClaw 安全报告 | https://aimlapi.com/blog/from-conversation-to-execution-a-comprehensive-guide-to-openclaw-claude-code-and-claude-cowork |
