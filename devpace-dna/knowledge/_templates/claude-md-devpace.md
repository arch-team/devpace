# {{PROJECT_NAME}}

> {{PROJECT_POSITIONING}}

## 研发协作规程

本项目使用 `.devpace/` 管理迭代研发。以下规程始终生效。

### 会话开始

1. 读 `.devpace/state.md`（≤15 行）
2. 用 **1 句自然语言** 报告状态和建议（不输出 ID、状态机术语、表格）
3. 等待用户指令，不自作主张开始工作

### 两种工作模式

**探索**（默认）——看代码、分析、讨论时：
- 自由操作，不修改 `.devpace/` 下的文件
- 不受工作流约束

**推进**——用户要改代码时（"开始做""帮我改""实现""修复"）：
- 绑定 `.devpace/backlog/CR-*.md`（已有的匹配，或自动创建）
- 每完成一个原子步骤：git commit + 更新 CR 事件 + 更新 state.md
- 质量检查不过 → 自行修复，不问用户
- 人工审阅 → 生成摘要，**停下等待**用户决策
- 不确定用户意图时问："要正式开始改代码，还是先看看？"

### 需求变更

用户说"不做了""加一个""先做那个""改一下"时：
1. 读 `.devpace/project.md` → 识别受影响的功能和变更 → 自然语言报告影响
2. 提出调整方案 → **等用户确认**
3. 确认后更新 CR + project.md + iterations/current.md + state.md

### 输出量控制

- 完成一步：1 句话
- 会话结束：3-5 行（做了什么 + 质量状态 + 下一步）
- 用户问详情：按需展开

### .devpace/ 文件

| 文件 | 何时读 |
|------|--------|
| `state.md` | 每次会话开始（必读） |
| `backlog/CR-*.md` | 推进模式 |
| `project.md` | 变更分析 或 用户要求看全景 |
| `rules/workflow.md` | 推进模式（状态机定义） |
| `rules/checks.md` | 推进模式（质量检查定义） |
| `iterations/current.md` | 查进度 或 变更分析 |
| `metrics/dashboard.md` | 仅 /pace-retro |

## 业务目标

{{OBJECTIVES_AND_MOS}}
