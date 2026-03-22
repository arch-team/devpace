---
description: Use when user says "帮助", "help", "怎么用", "使用说明", "用法", "有哪些命令", "能做什么", "命令列表", "怎么入门", "quickstart", "FAQ", "常见问题", "pace-help", or wants help with how to use devpace commands and features. NOT for concept deep dive or methodology (use /pace-theory). NOT for next-step recommendation (use /pace-next). NOT for code implementation (use /pace-dev).
allowed-tools: Read, Glob, Grep
argument-hint: "[commands|<command-name>|quickstart|faq]"
model: haiku
---

# /pace-help — 使用帮助

devpace 使用帮助的统一入口。回答"怎么用"（HOW）——命令列表、命令用法、入门引导、常见问题。

## 与现有机制的关系

| 维度 | Skill | 核心问题 |
|------|-------|---------|
| **HOW** 怎么用 | /pace-help（本 Skill） | "有哪些命令" "pace-dev 怎么用" "怎么入门" |
| **WHY** 为什么 | /pace-theory | "CR 是什么" "为什么要门禁" "BizDevOps 理论" |
| **WHAT** 做什么 | /pace-next | "下一步做什么" "该先做哪个" |

## 输入

$ARGUMENTS 支持 4 类子命令：

- `commands` → 所有命令的分层列表
- `<command-name>` (如 `dev`、`review`、`biz`) → 特定命令用法详解
- `quickstart` → 快速入门引导
- `faq` → 常见操作问题
- （空） → 上下文感知帮助概览

## 执行路由

**重要**：根据 $ARGUMENTS 匹配子命令，仅读取对应行指定的文件，**不加载其他 procedures**。

| 子命令 | 加载 procedure | 数据源 |
|--------|---------------|--------|
| （空） | help-procedures-overview.md | .devpace/state.md（如存在） |
| `commands` | help-procedures-commands.md | 动态读 skills/pace-*/SKILL.md |
| `<command-name>` | help-procedures-detail.md | 动态读 skills/pace-\<cmd\>/SKILL.md |
| `quickstart` | help-procedures-quickstart.md | .devpace/（如存在） |
| `faq` | help-procedures-faq.md | knowledge/_guides/help-faq.md |

**子命令识别规则**：`commands`/`quickstart`/`faq` 精确匹配优先；其余参数视为命令名，进入 detail 路由。

## 流程

### Step 1：识别子命令

按上方路由表匹配 $ARGUMENTS，加载对应 procedures 文件。

### Step 2：执行

按 procedures 中的步骤执行。所有子命令均为只读操作。

## 输出

自然语言为主，简洁实用。每个子命令输出末尾附 1 行导航提示，引导到相关 Skill 或子命令。
