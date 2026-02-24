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
| 生产事件 | 线上故障、报错、告警、影响用户 | → 严重度评估 → 创建 defect/hotfix CR |
| 缺陷 | 功能不符合预期（非紧急） | → 创建修复 CR |
| 改进 | 可用但不够好、体验问题 | → 记录到 project.md 待规划 |
| 新需求 | 未覆盖的功能请求 | → 引导用户走 /pace-change 插入流程 |

**report 参数处理**：
- `report <问题描述>` → 直接进入"生产事件"分支（跳过分诊）
- `<反馈描述>` → 走上表分诊流程
- （空）→ 引导式收集

### Step 2-5：执行处理

详见 `feedback-procedures.md`：严重度评估（Step 1.5）→ 关联价值链（Step 2）→ 更新 MoS（Step 3）→ 执行后续动作（Step 4）→ 更新状态与度量（Step 5）。

## 输出

反馈处理结果摘要（3-5 行）：分类 + 严重度（如适用）+ 关联 PF + 创建的 CR（如适用）+ 建议下一步。
