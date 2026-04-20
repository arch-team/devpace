---
description: Use when user asks "为什么", "怎么理解", "概念", "理论", "方法论", "BizDevOps", "原理", "什么是 BR", "什么是 PF", "CR 是什么意思", "价值链", "状态机原理", "追溯", "闭环", "度量", "MoS", "成效指标", "设计决策", "pace-theory", or wants to understand devpace concepts, behavior rationale, or methodology. NOT for specific CR decision audit trail (use /pace-trace). NOT for code implementation (use /pace-dev).
allowed-tools: Read, Glob, Grep
argument-hint: "[model|objects|spaces|rules|trace|topic|metrics|loops|change|mapping|decisions|vs-devops|sdd|why|all|<关键词>]"
model: haiku
---

# /pace-theory — 设计理论指南

查阅 devpace 背后的 BizDevOps 方法论和设计理论。why 解释通用理论，trace 重建实例轨迹。

## 输入

$ARGUMENTS 支持 15 个子命令（入门/概念/参考三层）和自由关键词搜索。完整列表见下方路由表。

## 执行路由

**重要**：根据 $ARGUMENTS 匹配子命令，仅读取对应行指定的文件，**不加载其他 procedures**。

| 子命令 | 读取 theory.md | 加载 procedure | 补充数据源 |
|--------|---------------|---------------|-----------|
| （空） | §0 | skills/pace-theory/theory-procedures-default.md | — |
| `model` | §2 | skills/pace-theory/theory-procedures-default.md | — |
| `objects` | §3 | skills/pace-theory/theory-procedures-default.md | 已初始化：backlog/ 最近 CR |
| `spaces` | §4 | skills/pace-theory/theory-procedures-default.md | — |
| `rules` | §5 | skills/pace-theory/theory-procedures-default.md | — |
| `trace` | §6 | skills/pace-theory/theory-procedures-default.md | 已初始化：backlog/ 最近 CR |
| `topic` | §7 | skills/pace-theory/theory-procedures-default.md | — |
| `metrics` | §8 | skills/pace-theory/theory-procedures-default.md | 已初始化：metrics/dashboard.md |
| `loops` | §9 | skills/pace-theory/theory-procedures-default.md | 已初始化：iterations/current.md |
| `change` | §10 | skills/pace-theory/theory-procedures-default.md | 已初始化：state.md |
| `decisions` | §11 | skills/pace-theory/theory-procedures-default.md | — |
| `mapping` | §12 | skills/pace-theory/theory-procedures-default.md | — |
| `vs-devops` | §1 | skills/pace-theory/theory-procedures-default.md | — |
| `sdd` | §14 | skills/pace-theory/theory-procedures-default.md | — |
| `why` | §11 | skills/pace-theory/theory-procedures-why.md | state.md + CR 事件表 + Gate 结果 + rules/checks.md + iterations/current.md |
| `all` | theory.md 全文 | skills/pace-theory/theory-procedures-default.md | — |
| `<关键词>` | Grep theory.md | skills/pace-theory/theory-procedures-search.md | — |

## 流程

### Step 1：加载知识库

按执行路由表选择性读取 Plugin 的 `knowledge/theory.md` 对应章节。

### Step 2：按参数输出

加载路由表中对应的 procedure 文件获取输出规则，按子命令类型执行输出。

### Step 3：关联当前项目

如果 `.devpace/` 存在：读取 `project.md`，按路由表"补充数据源"列选择性读取，应用角色适配框架并用项目实际数据做实例教学。如果未初始化：仅输出理论，末尾引导 `/pace-init`。

## 输出

按请求粒度展示的设计理论知识，辅以 devpace 中的具体映射。自然语言为主，渐进暴露细节。
