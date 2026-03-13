---
description: Use when user reports issues, shares feedback, or receives production alerts — "用户反馈", "线上问题", "生产问题", "告警", "改进建议", "新需求", "体验问题", "功能请求", "线上bug", "运维", "事件", "incident", "故障", "P0", "P1", "严重故障", "postmortem", "事后复盘". NOT for code implementation or development (use /pace-dev). NOT for requirement changes (use /pace-change).
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Bash
argument-hint: "[report <问题描述>] 或 [incident open/close/timeline/list] 或 [反馈描述]"
model: sonnet
disable-model-invocation: true
context: fork
agent: pace-engineer
---

# /pace-feedback — 反馈收集与事件处理

> **可选功能**：用于系统化收集上线后反馈和处理生产事件。简单场景直接说"用户反馈了 X 问题"或"线上有个 bug"即可。

收集上线后反馈和生产环境问题，关联到价值链（目标→Epic→功能→任务），闭合"交付→反馈→改进"循环和"部署→反馈→修复"循环。反馈可关联到 Epic 和 Opportunity（如来源为已有客户反馈）。每条反馈分配唯一 FB-ID，全生命周期可追踪。

## 输入

$ARGUMENTS：
- `report <问题描述>` → **紧急通道**：跳过分诊，自动进入"生产事件"分支并启用加速路径评估（仅 hotfix/critical 场景自动建议加速）
- `incident open <描述>` → 创建事件记录（严重度评估 + 时间线初始化）
- `incident close <INCIDENT-xxx>` → 关闭事件 + 生成 postmortem 模板
- `incident timeline <INCIDENT-xxx>` → 查看事件时间线
- `incident list` → 列出所有事件（支持 `--open` 筛选）
- `<反馈描述>` → 走分诊流程（分类后路由）
- （空）→ 引导式收集（渐进式两轮收集）

## 流程

通用规则见 `feedback-procedures-common.md`（每次加载）。按场景按需加载：

| 条件 | 加载文件 |
|------|---------|
| 空参数 / 信息不完整 | `feedback-procedures-intake.md` |
| 分类为生产事件 / 缺陷 | `feedback-procedures-trace.md` |
| severity ≥ major 或 report 参数 | `feedback-procedures-hotfix.md` |
| 创建 defect/hotfix CR | `feedback-procedures-analysis.md` |
| Step 5 状态更新 | `feedback-procedures-status.md` |
| incident open / close / timeline / list | `feedback-procedures-incident.md` |

### incident 子命令执行路由

| 子命令 | 读取 | 写入 | 规程文件 |
|--------|------|------|---------|
| incident open | state.md, backlog/, releases/ | incidents/INCIDENT-xxx.md | feedback-procedures-incident.md |
| incident close | incidents/INCIDENT-xxx.md, backlog/ | incidents/INCIDENT-xxx.md | feedback-procedures-incident.md |
| incident timeline | incidents/INCIDENT-xxx.md | （只读） | feedback-procedures-incident.md |
| incident list | incidents/ | （只读） | feedback-procedures-incident.md |

### Step 0：草稿恢复检查

检查 `.devpace/backlog/FEEDBACK-DRAFT.md` 是否存在（详见 common）：
- 存在 → 提示恢复 / 放弃
- 不存在 → 继续 Step 1

### Step 1：分类反馈

| 类型 | 特征 |
|------|------|
| 生产事件 | 线上故障、报错、告警、影响用户 |
| 缺陷 | 功能不符合预期（非紧急） |
| 改进 | 可用但不够好、体验问题 |
| 新需求 | 未覆盖的功能请求 |
| 记录待定 | 信息模糊、分类不确定、暂不处理 |

### Step 2-6：执行处理

按分类路由到对应 procedures 文件执行。详细步骤见各 procedures 文件。

## 输出

反馈处理结果摘要（3-5 行）：FB-ID + 分类 + 严重度（如适用）+ 关联 PF + 创建的 CR（如适用）+ 建议下一步。
