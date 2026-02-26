# I Built a Claude Code Plugin Using Claude Code — 18 Phases, 114 Tasks, 0 Regrets

> **Chinese version / 中文版将发布于掘金和少数派** — see below the separator for the full Chinese translation.

*What happens when your AI coding assistant builds its own project management tool?*

---

I spent two weeks building **devpace**, a Claude Code plugin that gives AI-assisted development a proper BizDevOps rhythm. 18 phases. 114 tasks completed. 18 skills shipped. And here's the part that still feels slightly surreal: **the plugin managed its own development from day one.**

Not as a gimmick. Not as a demo. As the actual project management system that tracked every change request, enforced every quality gate, and recovered context across every session. The dog food was real, and it tasted... surprisingly good.

## The Pain That Started This

If you've used Claude Code for anything beyond a one-off script, you know the drill:

**Session amnesia.** You close the terminal. You come back the next day. Claude has no idea what you were working on. You spend the first 10 minutes re-explaining where you left off.

**Quality drift.** Claude skips tests on the third file. Forgets to run the linter. Approves its own work without checking acceptance criteria. You catch it — sometimes. Not always.

**Feature creep, invisible.** You asked for a login page. You got a login page, a registration flow, password reset, and a half-built 2FA system. Nothing tracked. Nothing planned. Just code appearing.

**Requirement changes break everything.** Mid-project you say "actually, let's change this feature." Claude says "sure" and starts coding. But nobody assessed the impact. Nobody updated the plan. Three sessions later, half your codebase is inconsistent and you can't figure out why.

I tried the usual fixes. A detailed `CLAUDE.md`. Manual TODO lists. Explicit instructions like "please remember to check tests." They worked for about one session.

The problem isn't that Claude is bad at coding. It's that **Claude has no concept of a development process**. No state machine. No quality gates. No notion that a "change request" should flow through stages, not just get committed.

## The Hypothesis

What if we gave Claude a proper development rhythm — not just rules to follow, but a full value chain from business objectives to code changes?

Not a task list. Not a Kanban board. A **BizDevOps system** where every code change traces back to a product feature, every product feature traces back to a business requirement, and every state transition goes through explicit quality gates.

The hypothesis was: Claude doesn't need more capabilities. It needs **guardrails**. Structure. A process that makes it harder to skip the important parts than to follow them.

## How It Evolved

### Phase 1-4: Can This Even Work?

The first four phases were pure validation. Can Claude Code's plugin system (Rules + Skills + Hooks) actually enforce a development process?

The answer was yes, with caveats. The core concept — a CR (Change Request) state machine with 7 states (`created -> developing -> verifying -> in_review -> approved -> merged -> released`) and 4 quality gates — worked immediately. Claude would create a CR when you started coding, run gate checks before state transitions, and block merges until a human approved.

What surprised me was the **cross-session continuity**. A 15-line `state.md` file, auto-updated at session end, gave Claude perfect context recovery the next day. No re-explaining. No "where were we?" Just "continuing CR-003, left off at the verifying stage" and back to work.

By Phase 4, I had a working proof of concept, open-source infrastructure (MIT license, README, contributing guide), and the confidence that this wasn't a toy.

### Phase 5-8: Claude Becomes the Manager

Phase 5 was the turning point. Until then, Claude was a diligent follower of rules. Phase 5 made it a **proactive participant**.

I added 6 automatic detection signals — Claude would notice when a CR had been stuck in `developing` for too long, when reviews were piling up, when the iteration was drifting from plan. Not loud alerts. Quiet, one-line nudges: *"CR-005 has been in developing for 3 sessions. Consider reviewing scope or splitting."*

Then came the Hooks. A `PostToolUse` hook that triggered knowledge extraction whenever a CR merged. A `UserPromptSubmit` hook that detected change intent before Claude started coding — if you said "actually, let's add a new feature," the hook would whisper to Claude: "this sounds like a scope change, suggest using /pace-change for impact analysis."

By Phase 8, the system had 3 specialized agents (PM, Engineer, Analyst), release management, DORA metric proxies, and an operational feedback loop. Claude wasn't just writing code. It was managing a development process.

### Phase 10-14: Benchmarking Against the Ecosystem

This is where I got humble.

I ran a systematic benchmark against 50+ open-source projects in the Claude Code ecosystem. The top 15 by stars: Superpowers (51.8K), Everything Claude Code (47.2K), claude-mem (28.7K), Claude Task Master (25.5K), and on down. Plus broader AI-assisted development tools: Linear's AI features, Plandex, Shrimp Task Manager, BMAD-METHOD, Roo Code, Claude Pilot.

Each one taught me something. From Linear AI: a three-layer progressive transparency model (surface -> detailed -> full audit trail). From BMAD-METHOD (36K+ stars): adversarial review patterns where Claude argues against its own code. From Everything Claude Code: model tiering — using haiku for routine checks, sonnet for analysis, opus for critical decisions.

Four phases of deep study. Each phase produced concrete features:

- **Phase 11 (Linear AI)**: Source tracing tags (`<!-- source: user -->` vs `<!-- source: claude -->`), progressive autonomy levels (assisted/standard/autonomous), correction-as-learning
- **Phase 12 (Plandex/Shrimp/Roo)**: Cumulative diff review, gate reflection steps, exploration focus guidance
- **Phase 13 (ECC)**: Hooks migrated from Bash to Node.js for cross-platform reliability, check dependencies, confidence scoring
- **Phase 14 (BMAD)**: Adversarial review where Claude challenges its own implementation, complexity-adaptive paths, step isolation

None of these existed in Phase 4. The competitive analysis didn't just fill gaps — it fundamentally changed how the plugin thinks about quality.

### Phase 15-18: Hardening and Reach

The final stretch was about depth and integration. Phase 15 added a three-layer test management system (`/pace-test`) that maps test strategies to product feature acceptance criteria — not just "run tests" but "verify this test validates that business requirement." Phase 16 brought DORA proxy metrics, cross-project experience reuse, and CI/CD auto-detection. Phase 17 introduced Risk Fabric — pre-flight risk scanning before development starts, with graduated autonomous response (low risk: silent log, medium: warning + suggested mitigation, high: hard stop, wait for human).

Phase 18, the most recent, bridges devpace to GitHub Issues. Not a mechanical field mapping, but a semantic bridge — Claude understands the *meaning* of a state change and generates appropriate issue labels and comments.

## What I Actually Learned

### 1. LLMs Need Guardrails More Than Capabilities

This is the single biggest takeaway. Claude Code is already remarkably capable. What it lacks is **structure**. The quality gates alone — automatic checks before every state transition — caught more issues than any amount of "please remember to test" in a system prompt.

Gate 3, the human approval gate, is the most important feature in devpace. It's an unconditional hard stop. No autonomy level bypasses it. No urgency overrides it. Claude must wait for a human to approve before merging. This one rule prevents more problems than everything else combined.

### 2. "Byproducts Not Prerequisites" Is the UX Principle

I almost killed the project early by requiring too much structure upfront. The original design asked users to define Business Requirements, then Product Features, then Change Requests before writing a single line of code. Nobody wants that.

The breakthrough was UX principle P3: **structured data should be a byproduct of natural work, not a prerequisite.** You just start talking to Claude. It creates the CR automatically. The PF is inferred. The BR connection builds over time. By the third iteration, you have a full value chain without ever having explicitly built one.

### 3. Change Management Is the Killer Feature Nobody Talks About

Every project management tool assumes plans are stable. They're not. Requirements change mid-sprint, priorities shift, features get paused. devpace treats **change as a first-class citizen**: 5 types of change scenarios (insert, pause, reprioritize, modify, drop), automatic impact analysis, and structured triage (accept/decline/snooze).

When you tell Claude "actually, let's not do this feature for now," devpace doesn't just mark it as paused. It analyzes which other CRs depend on it, adjusts the iteration plan, preserves all work done so far, and records the change reason. When you resume it three weeks later, everything picks up exactly where it stopped.

### 4. The Meta-Recursion Is Not a Gimmick

devpace managing its own development is not just a cute story. It's the most honest validation possible. Every feature was stress-tested in real conditions. The cross-session continuity was verified across 100+ sessions. The quality gates caught real issues in devpace's own code. The change management handled real scope changes — the project went from 7 skills to 18, from 12 scenarios to 34, from 28 functional requirements to 68.

When I added Phase 10 (competitive analysis), it meant modifying the project's own design documents, which triggered devpace's cascade system to evaluate downstream impacts. The tool managing the tool that manages the tool. And it worked.

## The Numbers

| Metric | Value |
|--------|-------|
| Development phases | 18 completed, 2 planned |
| Tasks completed | 114 of 118 |
| Skills (user-facing commands) | 18 |
| Agents (specialized roles) | 3 (PM, Engineer, Analyst) |
| Hooks (automated triggers) | 13 |
| Schema definitions | 14 |
| User scenarios validated | 34 |
| Functional requirements | 68 |
| Non-functional requirements | 11 |
| Git commits | 191 |
| Versions released | 14 (v0.1.0 to v1.5.0) |
| Projects benchmarked | 50+ analyzed, 15+ deep-studied |
| Lines of rules (runtime) | 467 |
| Static test assertions | 148+ |

### Feature Comparison

| Capability | Manual CLAUDE.md | Task Tools (TodoWrite, CCPM) | devpace |
|------------|-----------------|------|---------|
| Cross-session continuity | Fragile, manual | Basic | Automatic, structured |
| Quality gates | None | None | 4-level, auto-enforced |
| Change management | None | None | 5 scenarios, impact analysis |
| Value chain traceability | None | None | OBJ -> BR -> PF -> CR |
| Human approval gate | None | None | Unconditional Gate 3 |
| DORA metrics | None | None | Proxy metrics with trending |
| Risk management | None | None | Pre-flight scan, graduated response |
| CI/CD integration | None | None | Auto-detect + Gate 4 query |
| External tool sync | None | None | GitHub Issues semantic bridge |
| Dual mode (explore/advance) | None | None | Default explore, opt-in advance |
| Progressive teaching | None | None | First-time behavior explanations |
| Role awareness | None | None | 5 roles, auto-inferred |

## What's Not Great

I'm going to be honest because that's more useful than a pitch.

**It's opinionated.** devpace assumes a specific development model (BizDevOps value chain, CR state machine, quality gates). If your workflow is "just vibe and ship," devpace will feel like bureaucracy. That's by design, but it's not for everyone.

**It's Markdown-heavy.** The state files are readable and LLM-friendly, but they're also verbose. A `project.md` with 20 product features is long. There's no database, no search index — just files.

**The competitive moat for Layer 1 is thin.** Cross-session continuity is devpace's entry point, but tools like claude-mem (28.7K stars) with vector search and AI-compressed memories do the "remembering" part arguably better. devpace's real value is in Layers 2-3 (change management, value chain), but users need to get past Layer 1 first.

**Testing is structural, not behavioral.** The 148+ static tests validate file structure, schema compliance, and cross-references. They don't test whether Claude actually follows the rules correctly in a live session. Behavioral validation is still manual.

**Enterprise claims are unproven.** I say "enterprise-ready" because the architecture supports audit trails and DORA metrics. But devpace has exactly zero enterprise users. The compliance features are designed, not battle-tested.

## Try It

devpace is MIT licensed and open source.

```bash
# Install from Claude Code marketplace
/install devpace

# Or clone and load locally
git clone https://github.com/arch-team/devpace
claude --plugin-dir ./devpace
```

Run `/pace-init` in your project. Answer a few questions. Start coding. devpace handles the rest — or at least, it tries to.

If something sucks, open an issue. If you have a workflow that devpace can't handle, I want to hear about it. If you think the whole concept is overengineered, you might be right — tell me why.

The code is at [github.com/arch-team/devpace](https://github.com/arch-team/devpace). The full design document, every decision record, and the 18-phase roadmap are in the repo. Nothing is hidden.

---

*Built with Claude Code. Managed by the thing it built. Reviewed by the human who started it all.*

---
---

# 我用 Claude Code 开发了一个 Claude Code 插件 —— 18 个阶段、114 项任务、0 个遗憾

> **English version / 英文版已发布于 Dev.to 和 Medium** — 见上方分隔线以上内容。

*如果你的 AI 编程助手自己给自己造一个项目管理工具，会发生什么？*

---

我花了两周时间开发了 **devpace**，一个为 AI 辅助开发带来完整 BizDevOps 研发节奏管理的 Claude Code 插件。18 个阶段。114 项任务完成。18 个 Skill 上线。而让我至今仍觉得微妙的是：**这个插件从第一天起就在管理自己的开发过程。**

不是噱头。不是演示。而是实际追踪每一个变更请求、执行每一个质量门禁、在每次会话中恢复上下文的真正的项目管理系统。这碗"自产狗粮"吃得……出乎意料地好。

## 让一切开始的痛点

如果你用 Claude Code 做过任何超出一次性脚本的事情，你一定知道这些场景：

**会话失忆。** 关掉终端，第二天回来，Claude 对你在做什么一无所知。你要花头 10 分钟重新解释上次做到哪了。

**质量漂移。** Claude 到第三个文件就跳过测试了。忘了跑 linter。自己审批自己的代码而不检查验收标准。你能抓到——有时候。不是每次。

**隐性的功能蔓延。** 你要了一个登录页面。你得到了一个登录页面、注册流程、密码重置和一个写了一半的双因素认证系统。没有跟踪。没有计划。只有凭空出现的代码。

**需求变更把一切搞乱。** 项目进行到一半你说"其实，这个功能改一下"。Claude 说"好的"然后开始写代码。但没人评估影响。没人更新计划。三个会话之后，一半的代码库不一致了，你根本找不出原因。

我试过常见的解决办法。详细的 `CLAUDE.md`。手动 TODO 列表。明确的指令比如"请记得检查测试"。大概管用一个会话。

问题不在于 Claude 不会写代码。而是 **Claude 没有开发流程的概念**。没有状态机。没有质量门禁。没有"变更请求应该经过阶段流转而不是直接提交"的认知。

## 假设

如果我们给 Claude 一个正式的开发节奏——不只是要遵守的规则，而是一条从业务目标到代码变更的完整价值链？

不是任务列表。不是看板。而是一个**BizDevOps 系统**，其中每个代码变更都能追溯到产品功能，每个产品功能都能追溯到业务需求，每个状态转换都要经过明确的质量门禁。

假设是：Claude 不需要更多能力。它需要的是**护栏**。结构。一个让跳过重要步骤比遵守它们更难的流程。

## 演进过程

### 阶段 1-4：这东西能跑起来吗？

前四个阶段是纯验证。Claude Code 的插件系统（Rules + Skills + Hooks）真的能执行一套开发流程吗？

答案是可以，有一些注意事项。核心概念——一个有 7 个状态（`created -> developing -> verifying -> in_review -> approved -> merged -> released`）和 4 个质量门禁的 CR（变更请求）状态机——立刻就跑通了。Claude 会在你开始写代码时创建 CR，在状态转换前执行门禁检查，在人类批准之前阻止合并。

让我惊喜的是**跨会话连续性**。一个 15 行的 `state.md` 文件，会话结束时自动更新，第二天就给 Claude 完美的上下文恢复。不需要重新解释。没有"上次到哪了？"只有"继续 CR-003，上次停在 verifying 阶段"然后直接工作。

到阶段 4，我有了一个能用的概念验证、开源基础设施（MIT 许可、README、贡献指南），以及"这不是玩具"的信心。

### 阶段 5-8：Claude 变成了管理者

阶段 5 是转折点。在此之前，Claude 是一个勤恳的规则执行者。阶段 5 让它成为**主动的参与者**。

我加了 6 个自动检测信号——Claude 会注意到一个 CR 在 `developing` 状态卡了太久、Review 在堆积、迭代偏离计划。不是大声警报。而是安静的一行提醒：*"CR-005 已在 developing 状态 3 个会话。考虑审查范围或拆分。"*

然后是 Hook。一个 `PostToolUse` hook 在 CR 合并时触发知识提取。一个 `UserPromptSubmit` hook 在 Claude 开始写代码之前检测变更意图——如果你说"其实，加一个新功能吧"，hook 会提醒 Claude："这听起来像范围变更，建议用 /pace-change 做影响分析。"

到阶段 8，系统有了 3 个专业化 Agent（PM、工程师、分析师）、发布管理、DORA 指标代理值、运维反馈闭环。Claude 不只是在写代码。它在管理一个开发流程。

### 阶段 10-14：与生态对标

这是我变谦虚的阶段。

我对 Claude Code 生态中 50+ 个开源项目做了系统性对标。Star 数前 15 名：Superpowers（51.8K）、Everything Claude Code（47.2K）、claude-mem（28.7K）、Claude Task Master（25.5K），等等。再加上更广泛的 AI 辅助开发工具：Linear 的 AI 功能、Plandex、Shrimp 任务管理器、BMAD-METHOD、Roo Code、Claude Pilot。

每个都教了我一些东西。从 Linear AI：三层渐进透明模型（表面 -> 详细 -> 完整审计轨迹）。从 BMAD-METHOD（36K+ stars）：对抗审查模式，让 Claude 质疑自己的代码。从 Everything Claude Code：模型分层——用 haiku 做例行检查，sonnet 做分析，opus 做关键决策。

四个阶段的深度研究。每个阶段产出了具体功能：

- **阶段 11（Linear AI）**：溯源标记（`<!-- source: user -->` vs `<!-- source: claude -->`）、渐进自主性三级（辅助/标准/自主）、纠正即学习
- **阶段 12（Plandex/Shrimp/Roo）**：累积 Diff 审查、Gate 间反思步骤、探索模式关注点引导
- **阶段 13（ECC）**：Hook 从 Bash 迁移到 Node.js 以确保跨平台可靠性、检查项依赖、置信度评分
- **阶段 14（BMAD）**：对抗审查让 Claude 挑战自己的实现、复杂度自适应路径、步骤隔离

这些在阶段 4 都不存在。竞品分析不只是填补了空白——它从根本上改变了插件对质量的思考方式。

### 阶段 15-18：加固与延伸

最后的冲刺关于深度和集成。阶段 15 加了三层测试管理系统（`/pace-test`），把测试策略映射到产品功能验收标准——不只是"跑测试"而是"验证这个测试覆盖了那个业务需求"。阶段 16 带来了 DORA 代理指标、跨项目经验复用和 CI/CD 自动检测。阶段 17 引入了 Risk Fabric——开发前的预飞行风险扫描，带分级自主响应（低风险：静默记录，中等：警告+缓解方案，高：硬停，等待人类确认）。

阶段 18，最近完成的，将 devpace 桥接到 GitHub Issues。不是机械的字段映射，而是语义桥接——Claude 理解状态变化的*含义*，然后生成适当的 Issue 标签和评论。

## 我真正学到了什么

### 1. LLM 需要护栏而不是更多能力

这是最大的收获。Claude Code 已经非常强大了。它缺的是**结构**。单是质量门禁——每次状态转换前的自动检查——就比任何数量的"请记得测试"的系统提示抓到了更多问题。

Gate 3，人类审批门禁，是 devpace 最重要的功能。它是无条件硬停。任何自主级别都绕不过。任何紧急程度都不能覆盖。Claude 必须等人类批准才能合并。这一条规则预防的问题比其他所有东西加起来都多。

### 2. "副产物而非前置条件"是核心 UX 原则

我差点因为要求太多前期结构而杀死这个项目。最初的设计要求用户先定义业务需求，然后产品功能，然后变更请求，然后才能写一行代码。没有人想要这样。

突破是 UX 原则 P3：**结构化数据应该是自然工作的副产物，而不是前置条件。** 你只需要开始跟 Claude 对话。它自动创建 CR。PF 被推断出来。BR 的关联随时间建立。到第三个迭代，你就拥有了一条完整的价值链，而你从来没有显式地构建过它。

### 3. 变更管理是没人谈论的杀手功能

每个项目管理工具都假设计划是稳定的。但计划不是。需求在 Sprint 中途变化，优先级调整，功能被暂停。devpace 把**变更当作一等公民**：5 种变更场景（插入、暂停、重排优先级、修改、砍掉），自动影响分析，结构化分流（接受/拒绝/延后）。

当你告诉 Claude "这个功能先不做了"，devpace 不只是标记为暂停。它分析哪些其他 CR 依赖它，调整迭代计划，保留所有已完成的工作，记录变更原因。三周后你恢复它时，一切从暂停的地方精确地继续。

### 4. 元递归不是噱头

devpace 管理自己的开发不只是一个好故事。它是最诚实的验证方式。每个功能都在真实条件下经过了压力测试。跨会话连续性在 100+ 个会话中得到验证。质量门禁在 devpace 自己的代码中捕获了真实问题。变更管理处理了真实的范围变更——项目从 7 个 Skill 增长到 18 个，从 12 个场景到 34 个，从 28 个功能需求到 68 个。

当我添加阶段 10（竞品分析）时，意味着修改项目自己的设计文档，这触发了 devpace 的级联系统去评估下游影响。管理工具的工具在管理自己。而且它跑通了。

## 数字

| 指标 | 数值 |
|------|------|
| 开发阶段 | 18 个完成，2 个计划中 |
| 完成任务 | 114 / 118 |
| Skills（用户命令） | 18 |
| Agents（专业角色） | 3（PM、工程师、分析师） |
| Hooks（自动触发器） | 13 |
| Schema 定义 | 14 |
| 验证的用户场景 | 34 |
| 功能需求 | 68 |
| 非功能需求 | 11 |
| Git 提交 | 191 |
| 发布版本 | 14（v0.1.0 至 v1.5.0） |
| 对标项目 | 50+ 分析，15+ 深度研究 |
| 运行时规则行数 | 467 |
| 静态测试断言 | 148+ |

### 功能对比

| 能力 | 手动 CLAUDE.md | 任务工具 (TodoWrite, CCPM) | devpace |
|------|---------------|------|---------|
| 跨会话连续性 | 脆弱，手动 | 基础 | 自动、结构化 |
| 质量门禁 | 无 | 无 | 4 级，自动执行 |
| 变更管理 | 无 | 无 | 5 种场景，影响分析 |
| 价值链追溯 | 无 | 无 | OBJ -> BR -> PF -> CR |
| 人类审批门禁 | 无 | 无 | 无条件 Gate 3 |
| DORA 指标 | 无 | 无 | 代理指标 + 趋势对比 |
| 风险管理 | 无 | 无 | 预飞行扫描，分级响应 |
| CI/CD 集成 | 无 | 无 | 自动检测 + Gate 4 查询 |
| 外部工具同步 | 无 | 无 | GitHub Issues 语义桥接 |
| 双模式（探索/推进） | 无 | 无 | 默认探索，主动推进 |
| 渐进教学 | 无 | 无 | 首次行为解释 |
| 角色感知 | 无 | 无 | 5 角色，自动推断 |

## 不够好的地方

说实话，因为这比一篇推广文更有用。

**它很固执。** devpace 假设了一个特定的开发模型（BizDevOps 价值链、CR 状态机、质量门禁）。如果你的工作流是"随心所欲然后发布"，devpace 会让你觉得是官僚主义。这是设计决策，但它不适合所有人。

**Markdown 很重。** 状态文件可读且对 LLM 友好，但也很冗长。一个有 20 个产品功能的 `project.md` 很长。没有数据库，没有搜索索引——只有文件。

**第一层的护城河很薄。** 跨会话连续性是 devpace 的入口，但像 claude-mem（28.7K stars）带向量搜索和 AI 压缩记忆的工具在"记忆"这件事上可能做得更好。devpace 的真正价值在第 2-3 层（变更管理、价值链），但用户需要先跨过第 1 层。

**测试是结构性的，不是行为性的。** 148+ 静态测试验证文件结构、Schema 合规和交叉引用。它们不测试 Claude 在实际会话中是否正确遵守了规则。行为验证仍然是手动的。

**企业级的说法未经验证。** 我说"企业级就绪"因为架构支持审计追踪和 DORA 指标。但 devpace 的企业用户数量是零。合规功能是设计出来的，不是战斗中验证的。

## 来试试

devpace 采用 MIT 许可，完全开源。

```bash
# 从 Claude Code marketplace 安装
/install devpace

# 或克隆后本地加载
git clone https://github.com/arch-team/devpace
claude --plugin-dir ./devpace
```

在你的项目中运行 `/pace-init`。回答几个问题。开始写代码。devpace 处理剩下的——或者至少，它会尝试。

如果有什么问题，开个 issue。如果你有 devpace 处理不了的工作流，我想听。如果你觉得整个概念过度工程了，你可能是对的——告诉我为什么。

代码在 [github.com/arch-team/devpace](https://github.com/arch-team/devpace)。完整的设计文档、每一条决策记录和 18 个阶段的路线图都在仓库里。没有藏着掖着。

---

*用 Claude Code 构建。由它自己构建的东西管理。由发起一切的人类审查。*
