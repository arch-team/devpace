---
description: Use when user asks "为什么", "怎么理解", "概念", "理论", "方法论", "BizDevOps", "原理", "pace-theory", or wants to understand devpace concepts, behavior rationale, or methodology.
allowed-tools: Read, Glob, Grep
argument-hint: "[model|objects|spaces|rules|trace|topic|metrics|loops|change|mapping|decisions|vs-devops|why|all]"
model: haiku
---

# /pace-theory — 设计理论指南

查阅 devpace 背后的方法论和设计理论，理解 devpace 的设计依据。

## 输入

$ARGUMENTS：
- （空）→ 输出核心概念速览（§0 速查卡片）
- `model` → 概念模型三要素详解（作业对象、作业空间、作业规则）
- `objects` → 作业对象详解（BR→PF→CR→发布→缺陷）
- `spaces` → 作业空间详解（产品线、交付团队、应用、发布单元）
- `rules` → 作业规则详解（工作流、质量检查、配置化）
- `trace` → 价值交付链路与双向追溯
- `topic` → 专题模式与成效指标（MoS）
- `metrics` → 度量体系（DIKW 模型 + 三维度量）
- `loops` → 三个反馈闭环（业务、产品、技术）
- `change` → 变更管理的理论依据
- `mapping` → 方法论概念 → devpace 实现的完整映射表
- `decisions` → 关键设计决策及其理论依据
- `vs-devops` → devpace 方法论与 DevOps 的区别
- `why` → 解释 devpace 最近做了什么以及为什么
- `all` → 输出完整理论知识库
- `<关键词>` → 在理论知识库中搜索匹配内容

## 流程

### Step 1：加载知识库

按 $ARGUMENTS 对应的 § 章节选择性读取 Plugin 的 `knowledge/theory.md`；`all` 或无参数时全量读取。

### Step 2：按参数输出

- 无参数 → 输出 §0 速查卡片，列出可查询的主题
- 有具体主题 → 输出对应章节内容
- 有关键词 → 在知识库中搜索，输出匹配段落
- `why` → 读取 `.devpace/state.md` + 最近 CR 事件表，解释 devpace 近期的行为及其设计理由（如为什么创建 CR、为什么执行质量检查、为什么等待 review 等）
- `all` → 输出完整内容（提醒用户内容较长）

### Step 3：关联当前项目

如果当前项目已初始化 `.devpace/`：
1. 读取 `.devpace/project.md`
2. 根据查询主题，指出当前项目中该概念的具体体现
3. 如有偏离 方法论设计建议的地方，给出改进建议

如果未初始化：仅输出理论内容，不做项目关联。

## 输出

按请求粒度展示的 设计理论知识，辅以 devpace 中的具体映射。
