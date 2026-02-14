---
description: Show BizDevOps theory and concept reference. Use when user says "理论", "概念", "为什么这样设计", "pace-guide", or needs to understand BizDevOps principles behind the plugin design.
---

# /pace-guide — BizDevOps 理论指南

查阅 BizDevOps 方法论提炼的理论知识，理解 devpace 的设计依据。

## 输入

$ARGUMENTS：
- （空）→ 输出核心概念速览（§0 速查卡片）
- `model` → 概念模型三要素详解（作业对象、作业空间、作业规则）
- `objects` → 作业对象详解（BR→PF→CR→发布→缺陷）
- `spaces` → 作业空间详解（产品线、交付团队、应用、发布单元）
- `rules` → 作业规则详解（工作流、门禁、配置化）
- `trace` → 价值交付链路与双向追溯
- `topic` → 专题模式与成效指标（MoS）
- `metrics` → 度量体系（DIKW 模型 + 三维度量）
- `loops` → 三个反馈闭环（业务、产品、技术）
- `change` → 变更管理的理论依据
- `mapping` → BizDevOps 概念 → devpace 实现的完整映射表
- `decisions` → 关键设计决策及其理论依据
- `vs-devops` → BizDevOps 与 DevOps 的区别
- `all` → 输出完整理论知识库
- `<关键词>` → 在理论知识库中搜索匹配内容

## 流程

### Step 1：加载知识库

读取 Plugin 的 `knowledge/bizdevops-theory.md`。

### Step 2：按参数输出

- 无参数 → 输出 §0 速查卡片，列出可查询的主题
- 有具体主题 → 输出对应章节内容
- 有关键词 → 在知识库中搜索，输出匹配段落
- `all` → 输出完整内容（提醒用户内容较长）

### Step 3：关联当前项目

如果当前项目已初始化 `bizdevops/`：
1. 读取 `bizdevops/product-line.md`
2. 根据查询主题，指出当前项目中该概念的具体体现
3. 如有偏离 BizDevOps 方法论建议的地方，给出改进建议

如果未初始化：仅输出理论内容，不做项目关联。

## 输出

按请求粒度展示的 BizDevOps 理论知识，辅以 devpace 中的具体映射。
