🌐 中文 | [English](README.md)

# devpace

给 Claude Code 项目一个稳定的研发节奏——需求在变，节奏不乱。

![version](https://img.shields.io/github/v/release/arch-team/devpace?label=version) ![license](https://img.shields.io/badge/license-MIT-green) ![type](https://img.shields.io/badge/Claude%20Code-Plugin-purple)

## 为什么需要 devpace

使用 Claude Code 做产品开发时：

| 问题 | 没有 devpace | 有 devpace |
|------|------------|-----------|
| <nobr>需求一变就乱</nobr> | "加个功能"导致连锁混乱，没人知道影响范围 | 影响分析 + 有序调整，Claude 不会自作主张改计划 |
| <nobr>质量时好时坏</nobr> | Claude 有时跳过测试、忘了检查 | 自动检查 + 人类审批，质量关卡不可跳过 |
| <nobr>做着做着偏离目标</nobr> | 技术工作和业务目标脱节，做了很多但价值不清 | 从业务目标到代码变更，始终可追溯 |
| <nobr>每次开会话都要重新解释</nobr> | 手动方案需 **8 次**用户纠正（3 次中断实测） | 自动恢复上下文，**0 次**纠正 |

→ [看完整演示：从初始化到完成](examples/todo-app-walkthrough.md)

## 30 秒体验

```
/pace-init               ← 初始化（只需一次）
"帮我实现用户认证"         ← Claude 自动跟踪任务、写代码、跑测试、检查质量
"审批" 或 "打回"           ← 你决定是否合并
"加一个导出功能"           ← Claude 分析影响、调整计划、等你确认
"认证先不做了"             ← 影响分析 → 暂停（保留工作）→ 调整计划
```

下次开会话，Claude 自动报告："上次停在认证模块，继续？"——零手动解释。

## 覆盖完整研发生命周期

```
  目标         功能         代码变更          质量          发布
你来定义 ──→ 一起规划 ──→ Claude 写代码 ──→ 自动+你审批 ──→ 可选自动
               │                │               │              │
           pace-plan        pace-dev       pace-review    pace-release
           pace-change                                    pace-feedback
```

需求随时可变——`/pace-change` 自动分析影响、调整计划、等你确认。

每轮结束后，`/pace-retro` 展示质量指标和改进趋势。

## 工作原理

devpace 在你的项目中构建一条**从目标到代码的追溯链**：

1. **目标对齐** —— 每个代码变更都关联到业务目标。没有目的的工作不会发生。
2. **自动质量门禁** —— Claude 自动检查代码质量和需求一致性，失败自动修复。人类审批不可跳过。
3. **变更是常态** —— 需求变了？自动影响分析，有序调整，已有工作保留。
4. **中断无忧** —— 会话断了？下次自动恢复。所有状态在 `.devpace/` 中，纯 Markdown。

底层机制：一个 Claude Code Plugin，通过 Rules（行为准则）+ Skills（`/pace-*` 命令）+ Hooks（关键时刻自动触发）实现。

## 安装

> **前置条件**：需先安装 [Claude Code CLI](https://claude.ai/code)。

### Marketplace 安装（推荐）

```bash
# 第一步：注册 marketplace（仅需一次）
/plugin marketplace add arch-team/devpace

# 第二步：安装
/plugin install devpace@devpace
```

### 从源码安装

```bash
git clone https://github.com/arch-team/devpace.git
claude --plugin-dir /path/to/devpace
```

### 验证安装

安装后在 Claude Code 中输入 `/pace-`，如果 devpace 加载成功，会看到 `/pace-init`、`/pace-dev`、`/pace-status` 等自动补全建议。

## 命令

### 日常使用

| 命令 | 作用 |
|------|------|
| <nobr>`/pace-init`</nobr> | 首次初始化（只需一次，支持 `--from PRD` 自动分解功能树） |
| <nobr>`/pace-dev`</nobr> | 开始写代码 |
| <nobr>`/pace-status`</nobr> | 看进度 |
| <nobr>`/pace-review`</nobr> | 审批变更 |
| <nobr>`/pace-next`</nobr> | 不确定做什么时，看 AI 推荐的下一步 |

### 需求变了或一轮做完时

| 命令 | 什么时候用 |
|------|----------|
| <nobr>`/pace-change`</nobr> | 加需求、暂停、改范围、调优先级 |
| <nobr>`/pace-plan`</nobr> | 一轮做完了，规划下一轮 |
| <nobr>`/pace-retro`</nobr> | 复盘做得怎么样 |

### 专项功能（可选，不使用时不受影响）

| 命令 | 场景 |
|------|------|
| <nobr>`/pace-test`</nobr> | 需求追溯驱动的测试管理 |
| <nobr>`/pace-guard`</nobr> | 风险织网：Pre-flight 扫描 + Runtime 监控 + 趋势分析 + 分级响应 |
| <nobr>`/pace-release`</nobr> | 发布编排：Changelog + 版本 bump + Git Tag + GitHub Release |
| <nobr>`/pace-sync`</nobr> | 外部工具桥接：任务状态 ↔ GitHub Issues 同步（标签 + 评论） |
| <nobr>`/pace-role`</nobr> | 切换视角（产品经理/测试/运维等） |
| <nobr>`/pace-theory`</nobr> | 了解背后的方法论 |
| <nobr>`/pace-feedback`</nobr> | 收集上线后反馈 |
| <nobr>`/pace-trace`</nobr> | 查看 AI 决策的完整推理轨迹 |

大多数时候不需要敲命令——说"帮我实现 X"等于 `/pace-dev`，说"做到哪了"等于 `/pace-status`。

## 核心能力

### 变更管理（核心差异化）

| 能力 | 说明 |
|------|------|
| <nobr>需求变更</nobr> | 加功能、暂停、改范围——自动分析影响，有序调整，Claude 不擅自改计划 |
| <nobr>复杂度感知</nobr> | 自动评估任务复杂度，小变更快速通过、大变更完整流程，复杂度漂移自动检测 |

### 质量与追溯

| 能力 | 说明 |
|------|------|
| <nobr>质量门禁</nobr> | 代码质量 + 需求一致性自动检查 + 对抗审查，人类审批不可跳过 |
| <nobr>目标追溯</nobr> | 从业务目标到代码变更，始终可追溯 |
| <nobr>测试验证</nobr> | 需求追溯驱动——策略生成、覆盖率分析、AI 验收验证、变更影响回归 |

### 研发节奏

| 能力 | 说明 |
|------|------|
| <nobr>跨会话恢复</nobr> | 会话断了自动续上，零手动解释，经验跨会话持久化 |
| <nobr>迭代管理</nobr> | 规划 → 执行 → 回顾完整循环，自动推荐下一步 |
| <nobr>渐进自主性</nobr> | 辅助/标准/自主三级——新用户多引导，熟练用户少干预 |
| <nobr>DORA 代理度量</nobr> | 部署频率/前置时间/失败率/MTTR 代理值，Elite~Low 基准分级 + 趋势对比 |
| <nobr>CI/CD 感知</nobr> | 自动检测 CI 工具类型，Gate 4 自动查询 CI 状态，零配置即用 |
| <nobr>风险织网</nobr> | Pre-flight 5 维风险扫描 + Runtime 实时监控 + 分级自主响应（High 必须人类确认） |
| <nobr>跨项目经验</nobr> | 高置信度经验可导出/导入到其他项目，减少重复学习 |

## 工作流程

### 两种模式

- **探索模式**（默认）：自由读代码、分析问题、讨论方案。不触发任何流程。
- **推进模式**（改代码时）：自动创建任务，跟踪进度，检查质量。小变更快速通过、大变更完整流程。

不确定时 Claude 会问："要开始改代码，还是先看看？"

### 工作流程

```
常规流程：
开始做 ──→ 在做 ──→ 待审批 ──→ 完成
            │         │
       质量自动检查  你来审批      自动合并 + 状态更新
      （Claude 处理）（你决定）

随时：
  需求变了 ──→ 影响分析 ──→ 调整计划 ──→ 继续
  会话中断 ──→ 下次自动从断点恢复

完整循环（可选）：
  规划 (pace-plan) → 开发 (pace-dev) → 回顾 (pace-retro) → 下一轮
```

## 设计原则

| 原则 | 含义 |
|------|------|
| <nobr>零摩擦</nobr> | 说自然语言就能工作，不需要学术语 |
| <nobr>渐进暴露</nobr> | 默认输出 1 行，详情按需展开 |
| <nobr>副产物非前置</nobr> | 结构化数据是工作的自动产出，不是前置要求 |
| <nobr>中断容错</nobr> | 任意时刻中断，下次无缝恢复 |

## 与替代方案的对比

| 维度 | GitHub Issues / 手动管理 | devpace |
|------|------------------------|---------|
| 核心模型 | 任务列表 | 目标 → 功能 → 代码变更追溯链 |
| 需求变更 | 人工评估影响 | 自动影响分析 + 有序调整 |
| Claude 的角色 | 执行者（你指挥每一步） | 自主协作者（自动推进、自检、等你决策） |
| 追溯性 | 任务 → 代码 | 业务目标 → 功能 → 变更 → 代码 |
| 度量 | 完成数量 | 质量通过率 + 价值对齐 + DORA 代理值 |

## devpace 不是什么

- **不是 CI/CD 流水线** —— 它与你现有的工具（GitHub Actions、Jenkins 等）并行工作
- **不是项目管理平台** —— 没有 Web 界面、没有团队功能，纯 CLI
- **不是 git 的替代品** —— 它在 `.devpace/` 中创建 Markdown 状态文件，你的代码仍在 git 中管理

## 了解更多

- [用户指南](docs/user-guide_zh.md) — 完整命令参考、工作模式、状态机细节（[English](docs/user-guide.md)）
- [端到端演示](examples/todo-app-walkthrough_zh.md) — 从初始化到完成的完整示例（[English](examples/todo-app-walkthrough.md)）
- [贡献指南](CONTRIBUTING_zh.md) — 开发环境、测试、PR 规范
- [更新日志](CHANGELOG.md) — 版本历史（[英文摘要见 GitHub Releases](https://github.com/arch-team/devpace/releases)）
- [问题排查](https://github.com/arch-team/devpace/issues?q=label%3Abug) — 搜索已知问题或提交新 Issue

---
MIT
