---
description: Initialize project development tracking. Use when user says "初始化研发管理", "pace-init", or wants to set up development workflow tracking.
allowed-tools: AskUserQuestion, Write, Read, Glob, Bash
argument-hint: "[项目名称]"
disable-model-invocation: true
---

# /pace-init — 初始化项目开发节奏管理

从模板初始化当前项目的 `.devpace/` 目录。行为规则通过 Plugin 机制自动注入，不修改项目已有文件。

## 输入

$ARGUMENTS：可选，项目名称。未提供时询问。

## 流程

### Step 1：检查前置条件

- 如果 `.devpace/state.md` 已存在 → 提示用户已初始化，询问是否重置
- 确认当前目录是项目根目录（有 .git/ 或其他项目标志）

### Step 2：收集信息

使用 AskUserQuestion 逐步获取：

1. **项目名称和一句话定位**（如果 $ARGUMENTS 未提供）
2. **代码结构分析**（自动执行，不需用户输入）：
   - 扫描项目目录结构和主要文件
   - 推断功能分组和模块划分
   - 在后续引导中基于分析结果主动建议
3. **当前阶段的业务目标**（1-2 个，用一句话描述）
4. **每个目标的成效指标（MoS）**（每个目标 2-4 个可衡量的指标）
   - 基于代码结构分析主动建议 MoS（"根据项目结构，建议关注 [指标]"）
   - 用户可接受建议或自定义
5. **实施路径**（分几个阶段，每阶段名称）
6. **第一批要做的产品功能**（3-8 个，归属到业务需求分组）
   - 基于代码结构分析主动建议功能分组（"检测到 [模块]，建议归入 [BR]"）

### Step 3：生成 .devpace/ 目录和文件

在项目根目录创建 `.devpace/` 结构：

```
.devpace/
├── state.md              ← 填入初始状态
├── project.md            ← 填入愿景、目标、MoS、价值功能树
├── backlog/              ← 空目录
├── iterations/
│   └── current.md        ← 填入第一个迭代
├── rules/
│   ├── workflow.md       ← 从 Plugin 模板复制标准工作流
│   └── checks.md         ← 引导用户定义项目特有质量检查
└── metrics/
    └── dashboard.md      ← 空仪表盘模板
```

内容从 Plugin 的 `skills/pace-init/templates/` 读取模板，替换 `{{PLACEHOLDER}}` 为用户提供的信息。

### Step 4：引导定义质量检查

询问用户本项目特有的质量检查项：
- "你的项目在代码提交前需要检查什么？比如测试、lint、类型检查……"
- "有没有项目特有的质量要求？"

填入 `.devpace/rules/checks.md`。

### Step 5：确认

展示生成的 `project.md` 价值功能树，确认结构合理。

## 输出

初始化完成的 `.devpace/` 目录 + 确认摘要。
