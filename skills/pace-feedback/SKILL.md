---
description: Use when user reports issues, shares feedback, or receives production alerts — "用户反馈", "线上问题", "生产问题", "告警", "改进建议", "新需求", "体验问题", "功能请求", "线上bug", "运维".
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash
argument-hint: "[report <问题描述>] 或 [反馈描述]"
model: sonnet
disable-model-invocation: true
---

# /pace-feedback — 反馈收集与事件处理

> **可选功能**：用于系统化收集上线后反馈和处理生产事件。简单场景直接说"用户反馈了 X 问题"或"线上有个 bug"即可。

收集上线后反馈和生产环境问题，关联到价值链（目标→功能→任务），闭合"交付→反馈→改进"循环和"部署→反馈→修复"循环。

## 输入

$ARGUMENTS：
- `report <问题描述>` → 直接进入"生产事件"分支（跳过分诊）
- `<反馈描述>` → 走分诊流程（分类后路由）
- （空）→ 引导式收集（合并反馈和事件的引导问题）

## 流程

详细操作步骤见 `feedback-procedures.md`。

### Step 1：分类反馈

根据反馈内容分类：

| 类型 | 特征 | 后续动作 |
|------|------|---------|
| 生产事件 | 线上故障、报错、告警、影响用户 | → Step 1.5 严重度评估 → Step 4 创建 defect/hotfix CR |
| 缺陷 | 功能不符合预期（非紧急） | → Step 4 创建修复 CR |
| 改进 | 可用但不够好、体验问题 | → 记录到 project.md 待规划 |
| 新需求 | 未覆盖的功能请求 | → 引导用户走 /pace-change 插入流程 |

**report 参数处理**：
- `report <问题描述>` → 直接进入"生产事件"分支（跳过分诊）
- `<反馈描述>` → 走上表分诊流程
- （空）→ 使用 AskUserQuestion 引导：
  1. "发生了什么问题？（如：页面白屏、接口超时、用户反馈体验问题）"
  2. "这是生产环境的紧急问题，还是一般性反馈？"

### Step 1.5：严重度评估（生产事件分支）

根据影响范围和紧急程度自动建议严重度：

| 影响范围 | 紧急程度 | 建议严重度 | CR 类型 |
|---------|---------|----------|--------|
| 全部用户 | 立即修复 | critical | hotfix |
| 全部用户 | 尽快修复 | major | defect |
| 部分用户 | 立即修复 | major | hotfix |
| 部分用户 | 尽快修复 | major | defect |
| 单用户 | 任意 | minor | defect |
| 界面/文案 | 可等待 | trivial | defect |

hotfix + critical → 告知用户可走加速路径。

### Step 1.5b：外部数据摄入（可选）

如 `.devpace/integrations/config.md` 存在：
- 读取告警映射表，根据告警等级自动建议严重度和 CR 类型
- 读取环境列表，自动关联问题发生的环境

### Step 2：关联价值链

1. 读取 `.devpace/project.md` 价值功能树
2. 匹配反馈到最相关的 PF（产品功能）和 BR（业务需求）
3. 读取 `.devpace/releases/` 查找最近的 Release，定位可能引入问题的 CR（生产事件时）
4. 如找到关联 Release → 在 Release "部署后问题"表追加记录
5. 无法匹配 → 记录为"未关联反馈"，建议创建新 BR

### Step 3：更新 MoS

如反馈涉及已定义的成效指标（MoS）：
- 缺陷/生产事件 → 在 project.md 对应 MoS 处追加备注"[日期] 反馈：[问题]"
- 改进 → 建议调整 MoS 指标或新增指标

### Step 4：执行后续动作

根据分类执行：
- **生产事件** → 自动创建 CR（type:defect 或 type:hotfix），格式遵循 `knowledge/_schema/cr-format.md`：
  1. 填充根因分析 section（已知信息）：现象（用户描述）、根因（待调查）、引入点（Step 2 追溯结果，如有）
  2. 关联到 PF 和 Release（如有）
  3. hotfix + critical → 告知用户可走加速路径（跳过 in_review）
- **缺陷** → 自动创建修复 CR（type:defect，关联原 PF），进入推进模式
- **改进** → 追加到 project.md 的 PF 备注区，建议纳入下次迭代
- **新需求** → 提示用户使用 /pace-change 走变更管理流程

### Step 5：更新状态与度量

1. 更新 project.md 功能树（缺陷/生产事件：🐛 或 🔥 标记）
2. 更新 state.md（新增缺陷信息）
3. 在 `.devpace/metrics/dashboard.md` 增量更新缺陷逃逸率（如存在该指标行）

## 输出

反馈处理结果摘要（3-5 行）：分类 + 严重度（如适用）+ 关联 PF + 创建的 CR（如适用）+ 建议下一步。
