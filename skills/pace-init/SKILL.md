---
description: Initialize project development tracking. Use when user says "初始化研发管理", "pace-init", or wants to set up development workflow tracking.
allowed-tools: AskUserQuestion, Write, Read, Glob, Bash
---

# /pace-init — 初始化项目开发节奏管理

从模板初始化当前项目的 `.devpace/` 目录，并将方法论写入项目 CLAUDE.md。

## 输入

$ARGUMENTS：可选，项目名称。未提供时询问。

## 流程

### Step 1：检查前置条件

- 如果 `.devpace/state.md` 已存在 → 提示用户已初始化，询问是否重置
- 确认当前目录是项目根目录（有 .git/ 或其他项目标志）

### Step 2：收集信息

使用 AskUserQuestion 逐步获取：

1. **项目名称和一句话定位**（如果 $ARGUMENTS 未提供）
2. **当前阶段的业务目标**（1-2 个，用一句话描述）
3. **每个目标的成效指标（MoS）**（每个目标 2-4 个可衡量的指标）
4. **实施路径**（分几个阶段，每阶段名称）
5. **第一批要做的产品功能**（3-8 个，归属到业务需求分组）

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

### Step 3.5：写入项目 CLAUDE.md（方法论 DNA 植入）

将 devpace 方法论写入项目的 CLAUDE.md，使项目自身携带研发协作上下文：

1. 读取 Plugin 的 `skills/pace-init/templates/claude-md-devpace.md` 模板
2. 用 Step 2 收集的信息替换 `{{PLACEHOLDER}}`：
   - `{{PROJECT_NAME}}`：项目名称
   - `{{PROJECT_POSITIONING}}`：一句话定位
   - `{{OBJECTIVES_AND_MOS}}`：业务目标和成效指标列表
3. 检查项目根目录是否已有 `CLAUDE.md`：
   - **已存在** → 读取现有内容，检查是否已有"研发协作规程"区块
     - 已有 → 跳过，告知用户已存在
     - 没有 → 在文件末尾追加模板内容（保留原有内容不变）
   - **不存在** → 用模板创建新的 CLAUDE.md
4. 对用户只说"项目上下文已配置"，不展开细节

### Step 4：引导定义质量检查

询问用户本项目特有的质量检查项：
- "你的项目在代码提交前需要检查什么？比如测试、lint、类型检查……"
- "有没有项目特有的质量要求？"

填入 `.devpace/rules/checks.md`。

### Step 5：确认

展示生成的 `project.md` 价值功能树，确认结构合理。

## 输出

初始化完成的 `.devpace/` 目录 + 项目 CLAUDE.md + 确认摘要。
