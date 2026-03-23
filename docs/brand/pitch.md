# devpace — AI-native BizDevOps 研发节奏管理器

> **需求永远在变，但从规划到交付的研发节奏，不应该因此失控。**

devpace 是一个 [Claude Code](https://claude.ai/code) 插件，让 AI 从"写代码的工具"进化为**理解业务意图的研发协作者**。它将 **业务目标 → 产品功能 → 代码变更** 串成一条可追溯的价值链，用规则、Schema、质量门禁和反馈循环约束 Agent 行为——把 vibe coding 变成可度量的工程实践。

## 解决什么问题

用 Claude Code 做产品迭代时，你大概率遇到过这些：

| 痛点 | 表现 | devpace 怎么解 |
|------|------|---------------|
| **跨会话失忆** | 每次开 Claude 都要重新解释"上次做到哪了" | 自动恢复上下文，零手动解释 |
| **质量靠自觉** | Claude 有时跳过测试、忘记检查 | 三级质量门禁（Gate 1-3）自动执行，不可跳过 |
| **需求变更失序** | 需求变了不知道影响多大，进度瞬间混乱 | 变更影响即时分析，有序调整而非推倒重来 |
| **业务机会散落** | 灵感和需求散在对话、文档、脑子里 | 结构化引导梳理，对齐战略目标 |
| **交付过程黑盒** | 做了什么、为什么这么做，回头全忘了 | 全链路追溯 + 决策记录 + DORA 度量 |

## 核心特性

- **双模式协作**：探索模式自由分析不改状态，推进模式绑定 CR + 状态机 + 质量门——一键切换
- **变更是一等公民**：不是"计划被打断了"，而是"变更来了，先分类再处理"
- **零摩擦入门**：说句"帮我做 X"就自动进入研发节奏，不需要学任何命令
- **渐进暴露**：从 5 个核心命令起步，进阶和专项能力在需要时自然浮现
- **多角色适配**：Biz / PM / Dev / Tester / Ops 五角色自动推断，同一数据不同视角
- **经验驱动**：每次交付自动提炼 pattern，后续决策引用历史经验，越用越聪明

## 快速开始

> **前置条件**：已安装 [Claude Code CLI](https://claude.ai/code)

**Marketplace 安装（推荐）**

```bash
# 注册 marketplace（一次性）
/plugin marketplace add arch-team/devpace-marketplace

# 安装
/plugin install devpace@devpace
```

**从源码安装**

```bash
git clone https://github.com/arch-team/devpace.git
claude --plugin-dir /path/to/devpace
```

安装后在 Claude Code 中输入 `/pace-`，看到自动补全即安装成功。

```
/pace-init                    ← 初始化项目（一次性）
"帮我实现用户登录功能"          ← Claude 自动跟踪进度、写代码、检查质量
"approve" 或 "reject"         ← 你决定是否合并
"加个导出功能"                 ← 自动分析影响、调整计划、等你确认
```

下次打开，Claude 报告："上次停在认证模块，继续？"——零手动解释。

## 能力全景

```
Biz 域    /pace-biz         业务机会 · Epic · 需求发现/导入/推断/分解/精炼
Dev 域    /pace-dev          CR 推进 · 质量门 · 自适应路径
          /pace-change       变更管理（5 种场景 · 影响分析 · 有序调整）
          /pace-review       代码审核 · Gate 2/3
          /pace-test         测试策略 · 覆盖分析 · AI 验收
          /pace-guard        风险预检 · 运行时监控
Ops 域    /pace-release      发布编排 · changelog · 环境晋升
          /pace-sync         GitHub/Linear/Jira 双向同步
          /pace-feedback     生产反馈 · 缺陷追溯闭环
横切      /pace-status       状态总览 · /pace-next 智能导航
          /pace-plan         迭代规划 · /pace-retro 回顾度量（DORA）
          /pace-trace        决策追溯 · ADR · /pace-role 角色切换
```

## 设计哲学

devpace 是 **Harness Engineering** 在 AI 研发场景的实践——不是限制 AI 的能力，而是用工程化的方式**引导** AI 行为：

- **规则约束行为**：5 条铁律确保关键操作不可绕过（如人类审批、状态机完整性）
- **Schema 约束数据**：统一的格式契约让多个 Skill 安全协作
- **门禁约束质量**：Gate 1（代码质量）→ Gate 2（需求一致性）→ Gate 3（人类审批）
- **反馈驱动改进**：每次交付自动学习，经验在后续开发中被引用

> 从 Harness Engineering 视角看，devpace 是 Claude Code 的研发节奏 harness——让 AI 辅助产品交付从随意变为有序。

## 适合谁

**使用 Claude Code 持续迭代产品的人**——不是写一次性脚本，而是在多个会话中推进有业务目标的项目。独立开发者一人戴多顶帽子，团队各司其职，devpace 都能适配。

## 支持项目

devpace 是 **Harness Engineering AI 研发实践**的开源项目，由社区驱动持续演进。

如果你觉得 devpace 的方向有价值——**让 AI 辅助研发从 vibe coding 走向工程化**——欢迎：

- [![Give a Star](https://img.shields.io/badge/Star_devpace-⭐_让更多人看到-yellow?style=for-the-badge&logo=github)](https://github.com/arch-team/devpace)
- **试用**后在 [Discussions](https://github.com/arch-team/devpace/discussions) 分享你的体验
- **提 Issue** 告诉我们哪里不好用，或者你希望 devpace 还能做什么
- **贡献代码**——从修一个文档到加一个 Skill，所有 PR 都欢迎

[![Star History Chart](https://api.star-history.com/svg?repos=arch-team/devpace&type=Date)](https://star-history.com/#arch-team/devpace&Date)

> devpace 还很年轻，但方向明确：**需求在变是常态，失序不应该是。** 如果你认同这个理念，一个 Star 就是最好的支持。

## License

MIT
