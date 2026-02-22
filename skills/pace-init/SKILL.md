---
description: Use when user says "初始化", "pace-init", "开始追踪", "初始化研发管理", or wants to set up project development tracking.
allowed-tools: AskUserQuestion, Write, Read, Glob, Bash
argument-hint: "[项目名称] [full] [--from <文档路径>]"
disable-model-invocation: true
---

# /pace-init — 初始化项目开发节奏管理

从模板初始化当前项目的 `.devpace/` 目录。默认执行最小初始化（仅需项目名 + 描述），`full` 参数执行完整流程，`--from` 参数从需求文档自动生成功能树。详细迁移和配置流程见 `init-procedures.md`。

## 输入

$ARGUMENTS：可选。格式为 `[项目名称]`、`[项目名称] full` 或 `[项目名称] --from <文档路径>`。未提供名称时询问。

## 流程

### Step 0：版本迁移检测

- 无 `.devpace/state.md` → 全新初始化（Step 1）
- 有 state.md + version=0.9.0 → 提示已初始化，询问重置
- 有 state.md + version=0.2.0~0.8.0 → 提示已初始化，询问重置（兼容，无迁移）
- 有 state.md + version=0.1.0/缺失 → v0.1→v0.9 迁移（详见 `init-procedures.md`）

### Step 1：信息收集（最小）

确认项目根目录。收集：
- **项目名称**（$ARGUMENTS 提供或询问）
- **一句话描述**（询问："用一句话描述这个项目做什么？"）

仅此两项。业务目标、MoS、功能树等后续自然生长。

### Step 2：生成 .devpace/（最小）

```
.devpace/
├── state.md          # 仅 "目标: [描述], 无进行中工作"
├── project.md        # 桩: 项目名 + 描述, 空价值树
├── backlog/
└── rules/
    ├── workflow.md    # 标准模板
    └── checks.md     # 从项目类型自动检测（package.json→npm test 等）
```

**不创建**：`iterations/`、`metrics/`、`releases/`、`integrations/`——这些在首次使用对应功能时按需创建。

### Step 3：确认

输出初始化摘要，然后展示"接下来会发生什么"预览：

```
初始化完成。接下来你可以：
- 说"帮我实现 X" → 我会自动跟踪这个任务
- 说"加一个 Y" → 我会分析影响再调整
- 说"做到哪了" → 我报告进度
```

建议在 `.gitignore` 中添加 `.devpace/`（如果用户不想版本控制状态文件）。

## `/pace-init full` 完整流程

当参数含 `full` 时，执行完整信息收集（兼容 v0.3.0 行为）：

1. 项目名称 + 描述
2. 业务目标 + MoS
3. 实施路径
4. 产品功能
5. 发布配置（可选，详见 `init-procedures.md`）
6. 质量检查引导

生成完整目录结构：

```
.devpace/
├── state.md · project.md · backlog/ · releases/ · integrations/
├── iterations/current.md · rules/{workflow,checks}.md
└── metrics/dashboard.md
```

## `/pace-init --from <文档路径>` 文档驱动初始化

当参数含 `--from` 时，从需求文档（PRD/README/设计文档）自动解析并生成 BR→PF→CR 功能树：

### 流程

1. **读取文档**：读取指定路径的文档文件（支持 .md/.txt/.pdf 等）
2. **提取需求**：AI 解析文档，识别业务目标、功能模块、用户场景
3. **生成功能树**：将提取的需求映射为 devpace 概念模型：
   - 业务目标/核心价值 → BR（业务需求）
   - 功能模块/特性描述 → PF（产品功能）
   - 具体任务/实现项 → CR（变更请求）初始列表
4. **用户确认**：展示生成的功能树结构，等待用户确认或调整
5. **写入 project.md**：确认后写入 `.devpace/project.md` 的价值功能树

### 差异化

与扁平任务列表不同，`--from` 生成的是 BR→PF→CR 价值链：
- 每个 CR 可追溯到所属的 PF 和 BR
- 功能之间的依赖关系被识别和记录
- 变更管理可追踪影响到业务目标级别

### 注意事项

- 文档内容越结构化，解析结果越准确
- 模糊的描述会被标记为"需澄清"，生成后用户可调整
- 生成的 CR 初始列表仅为建议，不自动创建 CR 文件（用户 /pace-dev 时才创建）
- 可与 `full` 参数组合使用：`/pace-init myproject full --from prd.md`

## 输出

初始化完成的 `.devpace/` 目录 + 确认摘要。
