---
title: "Claude Code Keeps Forgetting Your Project? Here's a Fix"
published: false
tags: claudecode, ai, developer-tools, productivity
canonical_url: https://github.com/arch-team/devpace
---

# Claude Code Keeps Forgetting Your Project? Here's a Fix

> **Chinese version**: 中文版将发布于掘金和少数派
>
> **Target platforms**: Dev.to, Medium (English); juejin.cn, sspai.com (Chinese)

---

You close your Claude Code session at 6 PM. You open it back up the next morning. And the first thing you type is a three-paragraph explanation of what you were doing yesterday.

Sound familiar?

## The Problem Nobody Talks About

Claude Code is one of the most capable AI coding assistants available. It can write whole modules, refactor complex systems, and reason through architecture decisions. But it has a blind spot that costs developers real time every single day: **it forgets everything between sessions**.

This isn't a bug. It's how the tool works. Claude Code operates in isolated sessions. There is no persistent project memory. No state carried over. When you start a new session, Claude sees your codebase, your `CLAUDE.md` if you have one, and nothing else. It doesn't know what you were working on, what state your feature is in, which tests were passing, what your acceptance criteria are, or what you decided in the last three sessions.

For a one-off script, this is fine. For sustained product development across days or weeks, it's a serious friction point. You end up repeating yourself. You correct Claude when it makes wrong assumptions. You re-explain decisions you already made. And every interruption — lunch break, meeting, end of day — resets the clock.

## What Manual Solutions Look Like (and Where They Break)

The most common workaround is a well-crafted `CLAUDE.md` file. You write down your project structure, conventions, current goals, maybe a list of TODOs. Some developers keep a separate notes file that they paste into the conversation at the start of each session. Others manually update a "project status" section after each work block.

These approaches help — up to a point. They cover the static parts: "this is a TypeScript project, we use Vitest, here are the coding conventions." But they fail at the dynamic parts:

- **What's in progress right now?** A `CLAUDE.md` doesn't update itself. By your third session, the "current work" section is stale.
- **What are the acceptance criteria for this feature?** You wrote them down somewhere, but did you paste them into the context? Probably not.
- **What's the quality gate status?** Did the last session's tests pass? Were there lint issues? What about the intent check — does the code match what you originally planned? Manual notes don't capture this.
- **What changed since last time?** If you or someone else pushed commits between sessions, your manual context is now out of sync with reality.

The fundamental issue is maintenance. Keeping manual context accurate requires effort proportional to your project's complexity. And the whole point of using an AI coding assistant is to reduce effort, not create new bookkeeping tasks.

## What Happens When Context Is Actually Maintained

We built [devpace](https://github.com/arch-team/devpace), a Claude Code plugin, partly to solve this problem. The core idea is simple: maintain project state as plain Markdown files in a `.devpace/` directory, and have Claude read them automatically at every session start.

But instead of just claiming it works, let me show you numbers from an actual comparison test.

### The Test Setup

We took the same project and ran it through three deliberate interruption points — simulating a developer closing their laptop, taking a call, switching projects, and coming back. We ran this twice: once with devpace managing the state, once with a manually maintained `CLAUDE.md`.

At each interruption recovery, we counted how many times the user had to correct Claude's understanding of the project state. A "correction" means Claude either assumed something wrong, forgot something important, or started working in the wrong direction.

### The Results

**devpace: 0 user corrections across 3 interruption points.**

**Manual approach: 8 user corrections across 3 interruption points.**

Eight times the user had to stop Claude and say "no, that's not where we were" or "we already decided against that approach" or "the acceptance criteria require X, not Y."

But the raw correction count only tells part of the story. We also ran a 7-dimension analysis comparing what each approach actually preserved across sessions:

| Dimension | devpace (auto) | Manual CLAUDE.md |
|-----------|:-:|:-:|
| D1: Current work status | Pass | Pass |
| D2: Feature context (what and why) | Pass | Pass |
| D3: Acceptance criteria state | Pass | **Fail** |
| D4: Quality gate status | Pass | **Fail** |
| D5: Decision history | Pass | Partial |
| D6: Dependency/blocker state | Pass | Partial |
| D7: Next step recommendation | Pass | **Fail** |

<!-- GIF: session-restore-demo.gif — show: new session → auto-report → "continue" → picks up where left off -->

**devpace scored 21/21. Manual scored 7/21.** ([Full test methodology](https://github.com/arch-team/devpace/blob/main/docs/research/cross-session-test.md))

The critical gap is D3 and D4. Acceptance criteria and quality gate state are completely uncovered by manual approaches. No developer is going to manually write "Gate 1 passed, Gate 2 pending, lint passed on 14 files, type check failed on auth.ts line 42" in their `CLAUDE.md` after every session. It's too granular, too tedious, and too easy to forget. But that's exactly the information Claude needs to resume work without false starts.

## How devpace Does It

devpace is a Claude Code Plugin — it uses Rules (behavioral guidelines), Skills (`/pace-*` commands), and Hooks (auto-triggers) to maintain project state. Here's what matters for cross-session continuity:

**A `.devpace/` directory** gets created in your project with plain Markdown files:

```
.devpace/
├── state.md          ← Session anchor: current phase, active work, next steps (5-15 lines)
├── project.md        ← Value-feature tree: goals → features → tasks
├── backlog/CR-NNN.md ← One file per task: status, linked feature, quality checks, event log
├── rules/
│   ├── workflow.md   ← Your project's workflow rules
│   └── checks.md     ← Quality checks (auto-detected from your toolchain)
└── context.md        ← Technical conventions
```

**On session end**, devpace updates `state.md` with what's in progress and what comes next. Not a brain dump — a structured 5-15 line checkpoint.

**On session start**, a Hook reads `state.md` and injects the context. Claude reports one sentence describing the current situation. You say "continue" and you're back where you left off.

The key design choice: **devpace preserves project state, not conversation state.** It doesn't try to replay your chat history. It captures the things that matter — what feature you're building, what's done, what's not, what quality checks look like, what the acceptance criteria say — as structured data that Claude can parse instantly.

Everything is Markdown. You can read it, edit it, commit it to git, diff it. No proprietary formats. No external services. No database.

## The 30-Second Experience

```
# First time (once per project)
/pace-init my-app

# Claude auto-detects your toolchain, creates .devpace/, injects into CLAUDE.md
# Done. Start working:

"Help me implement user authentication"
# Claude auto-creates a task, writes code, runs tests, checks quality

# --- session break ---

# Next session, Claude reports:
# "Last session stopped at auth module, JWT refresh token pending. Continue?"

"continue"
# Picks up exactly where it left off. No re-explanation.
```

For existing projects with a PRD or requirements doc:

```
/pace-init --from prd.md
# Parses your doc → generates a goal-feature-task tree → you confirm → start working
```

## What This Isn't

devpace is not a CI/CD platform. It's not a replacement for GitHub Issues or Jira. It doesn't have a web dashboard or team collaboration features. It's a plugin that runs inside Claude Code and maintains the project state that Claude needs to work autonomously across sessions.

It also does more than just cross-session continuity — there's change management (`/pace-change`), quality gates, iteration planning, DORA metrics, and a full traceability chain from business goals to code. But the cross-session problem is the entry point. It's the pain you feel every morning.

## Try It

```bash
# In Claude Code:
/plugin marketplace add arch-team/devpace
/plugin install devpace@devpace
```

Or from source:

```bash
git clone https://github.com/arch-team/devpace.git
claude --plugin-dir /path/to/devpace
```

Then:

```
/pace-init
```

You'll see a `.devpace/` directory appear with your project's state files. Work for a while, close the session, open a new one. See if Claude remembers.

The repo is MIT licensed and open source: [github.com/arch-team/devpace](https://github.com/arch-team/devpace)

For the full feature set: [User Guide](https://github.com/arch-team/devpace/blob/main/docs/user-guide.md) | [End-to-end walkthrough](https://github.com/arch-team/devpace/blob/main/examples/todo-app-walkthrough.md)

---

*Built by a developer tired of saying "no, we already decided that" to Claude for the third time in one morning.*

---
---

# Claude Code 总是忘记你的项目？这里有个解决方案

> **English version**: 英文版发布于 Dev.to 和 Medium
>
> **发布平台**: 掘金 (juejin.cn)、少数派 (sspai.com)

---

下午 6 点关掉 Claude Code，第二天早上打开，你输入的第一句话是一段三行的解释——告诉 Claude 你昨天在做什么。

这事是不是经常发生？

## 没人谈论的真实痛点

Claude Code 是目前最强大的 AI 编程助手之一。它能写整个模块、重构复杂系统、推演架构方案。但它有一个每天实实在在吃掉开发者时间的盲区：**它在会话之间忘记一切。**

这不是 Bug，这是工具的工作方式。Claude Code 以隔离会话运行，没有持久化的项目记忆，没有跨会话状态。当你开启新会话时，Claude 看到的只有你的代码库和 `CLAUDE.md`（如果有的话）。它不知道你在做什么功能、功能处于什么状态、哪些测试通过了、验收标准是什么、也不知道你过去三次会话做了什么决定。

如果只是写一次性脚本，这无所谓。但如果你在跨越数天或数周做持续的产品研发，这是一个严重的摩擦点。你不断重复自己的话，你在 Claude 做出错误假设时纠正它，你重新解释已经做过的决策。每一次中断——午休、开会、下班——都把时钟归零。

## 手动方案长什么样（以及它们在哪里失败）

最常见的解决方法是精心编写一份 `CLAUDE.md` 文件。写下项目结构、编码约定、当前目标，可能再来一个 TODO 列表。有些开发者会维护单独的笔记文件，每次新会话时粘贴到对话中。还有人在每次工作结束后手动更新一个"项目状态"小节。

这些方法有帮助——在一定范围内。它们覆盖了静态部分："这是一个 TypeScript 项目，我们用 Vitest，编码约定如下。"但它们在动态部分失败了：

- **现在正在做什么？** `CLAUDE.md` 不会自己更新。到第三次会话时，"当前工作"部分已经过时了。
- **这个功能的验收标准是什么？** 你确实在某处写过，但你粘贴进上下文了吗？大概率没有。
- **质量门状态是什么？** 上次会话的测试通过了吗？有 lint 问题吗？意图一致性检查呢——代码和最初的计划匹配吗？手动笔记不会记录这些。
- **上次之后有什么变化？** 如果你或其他人在两次会话之间推了提交，你的手动上下文就和现实脱节了。

根本问题是维护成本。让手动上下文保持准确，需要的精力与项目复杂度成正比。而使用 AI 编程助手的初衷，本来就是减少精力消耗，而不是制造新的记账任务。

## 当上下文被真正维护时会发生什么

我们做了 [devpace](https://github.com/arch-team/devpace)——一个 Claude Code 插件——部分就是为了解决这个问题。核心思路很简单：以纯 Markdown 文件在 `.devpace/` 目录中维护项目状态，让 Claude 在每次会话开始时自动读取。

但与其只是声称它有效，不如让我展示一组实际对比测试的数据。

### 测试设置

我们拿同一个项目，人为设置了 3 个中断点——模拟开发者合上笔记本、接电话、切换项目，然后回来继续。这个过程跑了两遍：一次用 devpace 管理状态，一次用手动维护的 `CLAUDE.md`。

在每次中断恢复时，我们记录用户需要纠正 Claude 理解的次数。一次"纠正"意味着 Claude 假设错了、忘记了重要的事情、或者朝错误的方向开始工作。

### 结果

**devpace：3 个中断点，0 次用户纠正。**

**手动方案：3 个中断点，8 次用户纠正。**

八次——用户不得不打断 Claude 说"不是的，我们不在那个位置"、"我们已经否决了那个方案"或者"验收标准要求的是 X 不是 Y"。

但原始纠正次数只说明了一部分。我们还做了一个 7 维度分析，比较两种方案在跨会话时实际保留了什么：

| 维度 | devpace（自动） | 手动 CLAUDE.md |
|------|:-:|:-:|
| D1：当前工作状态 | 通过 | 通过 |
| D2：功能上下文（做什么、为什么） | 通过 | 通过 |
| D3：验收标准状态 | 通过 | **失败** |
| D4：质量门状态 | 通过 | **失败** |
| D5：决策历史 | 通过 | 部分 |
| D6：依赖/阻塞状态 | 通过 | 部分 |
| D7：下一步建议 | 通过 | **失败** |

<!-- GIF: session-restore-demo.gif — 展示：新会话 → 自动报告 → "继续" → 精确恢复 -->

**devpace 得分 21/21。手动方案得分 7/21。**（[完整测试方法论](https://github.com/arch-team/devpace/blob/main/docs/research/cross-session-test.md)）

关键差距在 D3 和 D4。验收标准和质量门状态被手动方案完全遗漏。没有哪个开发者会在每次会话结束后手动写下"Gate 1 已通过，Gate 2 待验证，lint 在 14 个文件上通过，type check 在 auth.ts 第 42 行失败"。这太细碎、太繁琐、太容易忘记。但这恰恰是 Claude 恢复工作而不走弯路所需要的信息。

## devpace 怎么做到的

devpace 是一个 Claude Code 插件——它通过 Rules（行为规范）、Skills（`/pace-*` 命令）和 Hooks（关键时刻自动触发）来维护项目状态。以下是跨会话连续性的关键机制：

在你的项目中创建一个 **`.devpace/` 目录**，里面全是纯 Markdown 文件：

```
.devpace/
├── state.md          ← 会话锚点：当前阶段、进行中的工作、下一步（5-15 行）
├── project.md        ← 价值-功能树：目标 → 功能 → 任务
├── backlog/CR-NNN.md ← 每个任务一个文件：状态、关联功能、质量检查、事件日志
├── rules/
│   ├── workflow.md   ← 你项目的工作流规则
│   └── checks.md     ← 质量检查（从你的工具链自动检测）
└── context.md        ← 技术约定
```

**会话结束时**，devpace 更新 `state.md`——记录正在做什么、下一步做什么。不是无结构的脑倾倒，而是结构化的 5-15 行检查点。

**会话开始时**，Hook 读取 `state.md` 并注入上下文。Claude 用一句话报告当前状况。你说"继续"，就回到上次的位置。

关键设计选择：**devpace 保存的是项目状态，而不是对话状态。** 它不试图回放聊天历史。它捕捉的是真正重要的东西——你在做什么功能、什么完成了什么没完成、质量检查长什么样、验收标准怎么说——以 Claude 能瞬间解析的结构化数据形式存在。

所有东西都是 Markdown。你可以阅读、编辑、提交到 git、做 diff。没有私有格式，没有外部服务，没有数据库。

## 30 秒体验

```
# 第一次使用（每个项目一次）
/pace-init my-app

# Claude 自动检测工具链、创建 .devpace/、注入 CLAUDE.md
# 完成。开始工作：

"帮我实现用户认证"
# Claude 自动创建任务、写代码、跑测试、检查质量

# --- 会话中断 ---

# 下次会话，Claude 报告：
# "上次停在认证模块，JWT 刷新令牌待完成。继续？"

"继续"
# 精确地从上次的位置接上。不需要重新解释。
```

如果你已经有 PRD 或需求文档：

```
/pace-init --from prd.md
# 解析文档 → 生成目标-功能-任务树 → 你确认 → 开始工作
```

## 这不是什么

devpace 不是 CI/CD 平台。不是 GitHub Issues 或 Jira 的替代品。没有 Web 控制台，没有团队协作功能。它是一个运行在 Claude Code 内部的插件，维护 Claude 跨会话自主工作所需要的项目状态。

它做的也不止是跨会话连续性——还有变更管理（`/pace-change`）、质量门、迭代规划、DORA 度量以及从业务目标到代码的完整可追溯链。但跨会话问题是入口。这是你每天早上切实感受到的痛。

## 试一下

```bash
# 在 Claude Code 中：
/plugin marketplace add arch-team/devpace
/plugin install devpace@devpace
```

或者从源码安装：

```bash
git clone https://github.com/arch-team/devpace.git
claude --plugin-dir /path/to/devpace
```

然后：

```
/pace-init
```

你会看到一个 `.devpace/` 目录出现，里面是你项目的状态文件。工作一段时间，关掉会话，再开一个新的。看看 Claude 是否还记得。

仓库是 MIT 许可的开源项目：[github.com/arch-team/devpace](https://github.com/arch-team/devpace)

完整功能参考：[用户指南](https://github.com/arch-team/devpace/blob/main/docs/user-guide_zh.md) | [端到端演示](https://github.com/arch-team/devpace/blob/main/examples/todo-app-walkthrough_zh.md)

---

*一个受够了每天早上对 Claude 说三遍"不对，我们已经决定过了"的开发者做的。*
