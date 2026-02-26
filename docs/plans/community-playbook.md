# devpace Community Engagement Playbook

> Practical, copy-paste-ready templates for community promotion. Each section is designed to be used directly on its target platform.
>
> **Product**: devpace -- AI-native BizDevOps pace manager for Claude Code
> **GitHub**: https://github.com/arch-team/devpace
> **Key value prop**: "Never re-explain your project to Claude again"
> **Core data point**: 0 corrections (devpace) vs 8 corrections (manual) across 3 session interruptions

---

## 1. Show HN Draft

**Title**: `Show HN: devpace – BizDevOps pace manager for Claude Code`

**Body**:

```text
I've been using Claude Code daily for product development — not one-off scripts,
but multi-week projects with real business requirements, changing specs, and
quality standards. The biggest pain wasn't Claude's code quality. It was this:
every time I started a new session, I had to re-explain where I was, what I was
building, and what the acceptance criteria were. Across 3 session interruptions,
that added up to 8 manual corrections before Claude was back on track.

So I built devpace, a Claude Code plugin that gives projects a persistent
development rhythm. You run /pace-init once, then just talk naturally — "help
me implement user auth." Claude auto-creates a tracked change request, writes
code, runs quality checks, and asks for your approval before merging. Next
session, it picks up exactly where you left off. Zero corrections needed.

The core idea is a goal-to-code traceability chain: business goals → product
features → code changes. When requirements change (and they always do),
/pace-change runs impact analysis across the whole chain so you know the blast
radius before anything moves. Quality gates run automatically — Claude can't
skip tests or bypass review just because it "feels confident."

It's open source (MIT), written entirely as a Claude Code Plugin (Rules + Skills
+ Hooks — no external servers, no API keys, everything local in .devpace/ as
plain Markdown). The honest limitations: the full value takes 2-3 sessions to
feel (cross-session context is the killer feature, but you need to close and
reopen to experience it), and the 17 Skills can feel like a lot upfront even
though day-to-day you only use 3-4.

GitHub: https://github.com/arch-team/devpace

Feedback welcome — especially what sucks.
```

**Posting checklist**:

- [ ] Post between 8-10am ET on a weekday (peak HN traffic)
- [ ] Monitor for the first 2 hours and respond to every comment
- [ ] Prepare answers for likely questions: "How is this different from CLAUDE.md?" / "Why not just use TodoWrite?" / "Does this work with Cursor/Windsurf?"
- [ ] Have the GitHub repo public and README polished before posting

---

## 2. Reddit r/ClaudeAI Strategy

### Template A: "Claude forgets my project every session" threads

> **Use when**: Someone posts about losing context between sessions, having to re-explain their project, or Claude "forgetting" what they were working on.

```text
Had the same problem. I was spending the first 5 minutes of every session
re-explaining my project structure, what I'd already done, and what was next.
Tried putting everything in CLAUDE.md but it got stale fast and I still had
to manually update it.

What actually fixed it for me was structuring my project state as machine-
readable Markdown that Claude maintains automatically. I built a plugin
called devpace that does this — it keeps a .devpace/ directory with project
state, and Claude updates it as you work. Next session, it reads the state
and picks up where you left off.

The real test: I interrupted the same project 3 times and compared devpace
(0 corrections needed) vs manual approach (8 corrections). The difference
was biggest for things like acceptance criteria and quality gate status —
stuff that's hard to put in a CLAUDE.md.

Open source, no API keys needed: https://github.com/arch-team/devpace
```

### Template B: "How do you manage long projects with Claude?" threads

> **Use when**: Someone asks about workflows, project organization, or keeping Claude on track over multiple sessions/features.

```text
After a lot of trial and error, what worked for me was separating the "what
to build" from the "how to track it." I have Claude maintain a lightweight
traceability chain: business goals → features → code changes. Each code
change links back to a feature, so when requirements shift (which happens
constantly), I can see what's affected.

I packaged this into a Claude Code plugin (devpace) but the core ideas work
even without it: keep your project state in a structured .devpace/ directory,
define quality checks that run automatically, and make Claude update its own
context files as it works instead of relying on you to maintain them.

The plugin adds quality gates (Claude can't skip tests or merge without
approval), change impact analysis, and auto-recovery across sessions. The
repo has a full walkthrough if you want to see the flow:
https://github.com/arch-team/devpace/blob/main/examples/todo-app-walkthrough.md
```

### Template C: "Claude Code plugin recommendations" threads

> **Use when**: Someone specifically asks about useful plugins, extensions, or tooling for Claude Code.

```text
If you're doing multi-session product development (not one-off scripts),
check out devpace. It's a BizDevOps plugin that gives your project a
persistent development rhythm.

The pitch: you run /pace-init once, then just say "help me implement X."
Claude creates a tracked change request, codes it, runs quality checks,
and asks for approval. Next session it auto-resumes — no re-explaining.

What I actually use most:
- Cross-session context (never re-explain your project)
- Quality gates (Claude can't skip tests or bypass review)
- /pace-change for impact analysis when requirements shift

MIT licensed, everything stored locally as Markdown:
https://github.com/arch-team/devpace
```

### Engagement rules for Reddit

| Situation | Action |
|-----------|--------|
| Thread directly mentions the problem devpace solves | Reply with the matching template, adapted to the specific context |
| Thread is about Claude Code but not about the problem | Contribute useful advice. Do NOT mention devpace |
| Someone asks a follow-up question about devpace | Answer thoroughly and honestly, including limitations |
| Thread has fewer than 3 comments | Skip it. Low-traffic threads look like self-promotion |
| Someone already recommended devpace | Upvote and add color if useful. Do not pile on |

---

## 3. Twitter/X Content Templates

### Single Tweets

**1. Pain point hook**

```text
Every Claude Code session starts the same way:
"So we're building a task manager, the auth module is half done, tests are in pytest, and..."

What if Claude just... remembered?

Built a plugin for that: github.com/arch-team/devpace
```

**2. Data-driven comparison**

```text
Tested: 3 session interruptions, same project.

Manual approach: 8 corrections to get Claude back on track
With devpace: 0 corrections

The difference? Claude maintains its own context. You just talk.

github.com/arch-team/devpace
```

**3. Quick demo description**

```text
/pace-init → set up your project once
"help me implement auth" → Claude tracks, codes, tests, asks for approval
close session, reopen → Claude picks up exactly where it stopped

That's devpace. Open source Claude Code plugin.
github.com/arch-team/devpace
```

**4. Developer empathy**

```text
The hardest part of using Claude Code for real projects isn't the code quality.

It's re-explaining your project every single session.

devpace fixes this. Also adds quality gates so Claude can't skip tests.
github.com/arch-team/devpace
```

**5. Open source invitation**

```text
Just open-sourced devpace — a Claude Code plugin for managing development pace across sessions.

17 skills, quality gates, change impact analysis, cross-session context. All local Markdown, no API keys.

Looking for feedback from anyone doing multi-session Claude Code projects.
github.com/arch-team/devpace
```

### Thread Starter A: The Problem Story (4 tweets)

```text
[1/4] I've been using Claude Code for real product dev for months. The code quality
is great. But there's a workflow problem nobody talks about:

Claude forgets everything between sessions.

Every. Single. Time. You re-explain your project from scratch.

[2/4] I tested it systematically: interrupted a project 3 times and tracked how
many corrections I needed to get Claude back on track.

Manual approach: 8 corrections
- 3 for project context
- 2 for acceptance criteria (completely lost)
- 3 for quality gate status (completely lost)

[3/4] So I built devpace — a Claude Code plugin that maintains project state
automatically. Claude updates .devpace/ as it works, and reads it when a new
session starts.

The same 3-interruption test: 0 corrections needed.

But context recovery is just the start.

[4/4] devpace also adds:
- Quality gates Claude can't bypass
- Change impact analysis when requirements shift
- Goal-to-code traceability

Open source, MIT, no API keys. Everything is local Markdown.

If you do multi-session projects with Claude Code, try it:
github.com/arch-team/devpace
```

### Thread Starter B: The Meta-Narrative (3 tweets)

```text
[1/3] I used Claude Code to build a Claude Code plugin.

The plugin (devpace) manages development pace — cross-session context, quality
gates, change management.

The irony: I needed this plugin while building it. Every new session, I'd lose
track of which of the 118 tasks I was on.

[2/3] Some numbers from the build:
- 18 phases, 118 tasks
- 17 skills (commands Claude can use)
- 34 user scenarios verified
- 68 functional requirements
- Built entirely through Claude Code sessions

The plugin literally managed its own development by Phase 3.

[3/3] The deepest lesson: the hard part of AI-assisted development isn't
generating code. It's maintaining rhythm across sessions, keeping quality
consistent, and not losing track of why you're building what you're building.

That's what devpace solves: github.com/arch-team/devpace
```

---

## 4. Chinese Community Templates

### V2EX 帖子模板

> **板块建议**: /t/programmer 或 /t/ai

**标题**: `用 Claude Code 做项目开发，最烦的不是代码质量，是每次都要重新解释项目`

```text
用 Claude Code 做了几个月的产品开发，代码质量没什么问题，但有个工作流上的痛点
一直困扰我：

**每次开新会话，都要从头解释项目背景。**

"我们在做一个任务管理器，auth 模块做到一半，测试用的 pytest，验收标准是……"

做了个量化测试：同一个项目中断 3 次，手动方式需要 8 次纠正才能让 Claude
回到正轨，其中验收标准和质量门状态完全丢失。

所以做了 devpace，一个 Claude Code 插件。核心思路很简单：让 Claude 自己
维护项目状态（放在 .devpace/ 目录，纯 Markdown），下次开会话自动读取恢复。

同样的 3 次中断测试：0 次纠正。

除了跨会话恢复，还加了：
- 质量门：Claude 不能跳过测试、不能跳过审批
- 变更影响分析：需求变了，自动分析影响范围再调整
- 业务目标→功能→代码变更的全链路追溯

MIT 开源，纯本地运行，不需要 API Key：
https://github.com/arch-team/devpace

如果你也在用 Claude Code 做多会话的项目开发，欢迎试试给反馈。
尤其想听听哪里不好用。
```

### 即刻 (Jike) 短帖模板

> **圈子建议**: "AI 探索" 或 "独立开发者"

**模板 1：痛点切入**

```text
用 Claude Code 做项目开发的一个反直觉发现：最浪费时间的不是让 Claude 写代码，
而是每次开新会话都要重新解释"我们在哪、在做什么"。

做了个插件 devpace 解决这个问题。Claude 自己维护项目状态，下次打开自动恢复。
实测：3 次中断，手动要纠正 8 次，用 devpace 是 0 次。

还顺手加了质量门（Claude 不能跳过测试）和变更影响分析（需求变了自动评估波及范围）。

开源的：github.com/arch-team/devpace
```

**模板 2：Meta 叙事**

```text
用 Claude Code 开发了一个 Claude Code 插件。

这个插件（devpace）管理开发节奏——跨会话恢复、质量门、变更管理。有意思的是，
开发它的过程中自己就需要它：118 个任务，每次开新会话都忘了做到哪。

从第 3 阶段开始，这个插件就开始管理它自己的开发了。某种程度上算是自举？

18 个阶段、17 个 Skill、34 个用户场景，全程用 Claude Code 会话完成。

MIT 开源：github.com/arch-team/devpace
```

---

## 5. Engagement Rules

### When to Engage vs. When to Stay Silent

| Signal | Action | Reason |
|--------|--------|--------|
| Someone describes a problem devpace directly solves | Engage with the matching template | Genuine value add |
| Someone asks for Claude Code plugin recommendations | Mention devpace alongside other tools | Relevant and requested |
| Thread discusses AI dev workflows in general | Contribute workflow advice; mention devpace only if directly relevant | Value first, product second |
| Thread is about Claude Code but not about the problem | Contribute useful advice. Do NOT mention devpace | Forcing it is spam |
| Thread has heated debate or negative sentiment | Stay silent | Bad timing for promotion |
| Someone criticizes AI coding tools broadly | Stay silent unless you can add genuine nuance | Do not be defensive |
| You already commented about devpace in the same sub this week | Stay silent | Frequency control |

### How to Mention devpace Without Being Spammy

1. **Lead with the problem, not the product.** The first paragraph should describe the pain point or share useful advice. devpace appears in the second half, naturally.
2. **Always include the limitation.** Mention that the full value takes 2-3 sessions to feel. Honesty builds trust.
3. **Use "I built" not "we launched."** Personal framing reads as genuine. Corporate framing reads as marketing.
4. **Adapt the template.** Never copy-paste the same text twice on the same platform. Match the tone and specific question of the thread.
5. **Ratio: 3:1 value-to-promotion.** For every post that mentions devpace, make 3 posts/comments that contribute value without mentioning it at all.

### How to Handle Negative Feedback or Criticism

| Criticism type | Response approach |
|----------------|-------------------|
| "This is too complex / too many features" | Agree it can feel overwhelming. Explain that day-to-day you only use 3-4 commands (/pace-init, natural language dev, /pace-change). Ask what would make it simpler. |
| "Anthropic will just build this natively" | Acknowledge the risk honestly (it's in the vision doc). Explain that cross-session persistence might get native support, but the concept-model-driven workflow engine (BR -> PF -> CR traceability) is a different category. |
| "I tried it and it didn't work" | Thank them, ask for specifics (Claude version, what they tried, error messages). Fix it publicly if possible. Every bug report is a gift at this stage. |
| "This is just a fancy CLAUDE.md" | Explain the difference: CLAUDE.md is static instructions you maintain. devpace is dynamic state that Claude maintains. Show the 0 vs 8 corrections data. |
| "Nobody needs BizDevOps for side projects" | Agree that the full BizDevOps framing is for larger projects. For side projects, the value is simpler: context recovery + quality gates. The rest is opt-in. |
| Trolling or bad-faith criticism | Do not respond. Move on. |

### Weekly Time Budget

| Activity | Time | Frequency |
|----------|------|-----------|
| Scan Reddit r/ClaudeAI, r/ChatGPTPro, r/LocalLLaMA for relevant threads | 20 min | 2x/week |
| Write 1-2 comments on relevant threads | 15 min | 2x/week |
| Post 1 tweet or thread | 10 min | 1x/week |
| Post to Chinese communities (V2EX / Jike) | 15 min | 1x/week |
| Respond to comments on your own posts | 10 min | as needed |
| **Total** | **~1.5 hours/week** | |

### Platform Priority

| Platform | Priority | Reason |
|----------|----------|--------|
| Hacker News | P0 (one-time) | High-signal developer audience, one strong Show HN post |
| Reddit r/ClaudeAI | P0 (ongoing) | Exact target audience, high thread volume about the problem |
| Twitter/X | P1 | AI dev community active here, good for building presence over time |
| V2EX | P1 | Chinese developer community, good technical discussion culture |
| Jike | P2 | Lower effort, good for casual reach in Chinese AI community |
| Reddit r/ChatGPTPro | P2 | Adjacent audience, occasional Claude Code threads |

### Content Calendar (First 4 Weeks)

| Week | Monday | Wednesday | Friday |
|------|--------|-----------|--------|
| 1 | Post Show HN | Respond to HN comments; scan Reddit | 1 Reddit comment + 1 Tweet |
| 2 | V2EX post | 1-2 Reddit comments | Tweet thread (Problem Story) |
| 3 | Jike post | 1-2 Reddit comments | 1 Tweet |
| 4 | Review metrics; adjust strategy | 1-2 Reddit comments | Tweet thread (Meta-Narrative) |

### Success Metrics (After 4 Weeks)

| Metric | Target | How to measure |
|--------|--------|----------------|
| Show HN upvotes | 10+ | HN post score |
| Reddit comments that generate replies | 3+ | Count reply threads |
| GitHub stars from community posts | 10-20 | Track referral sources via GitHub traffic |
| Negative feedback handled well | 100% responded to constructively | Self-audit |
| Time budget maintained | Under 2 hours/week | Time tracking |
