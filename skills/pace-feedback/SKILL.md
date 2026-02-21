---
description: Collect post-merge feedback and link to value chain. Use when user reports issues after deployment, user feedback, or discovered bugs — "上线后", "用户反馈", "发现 bug", "线上问题".
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob
argument-hint: "[反馈描述]"
---

# /pace-feedback — 反馈收集与关联

收集上线后反馈，关联到 BizDevOps 价值链（BR→PF→CR），闭合"交付→反馈→改进"循环。

## 输入

$ARGUMENTS：
- `<反馈描述>` → 用户反馈或问题描述

## 流程

### Step 1：分类反馈

根据反馈内容分类：

| 类型 | 特征 | 后续动作 |
|------|------|---------|
| 缺陷 | 功能不符合预期、报错、崩溃 | 创建修复 CR |
| 改进 | 可用但不够好、体验问题 | 记录到 project.md 待规划 |
| 新需求 | 未覆盖的功能请求 | 引导用户走 /pace-change 插入流程 |

### Step 2：关联价值链

1. 读取 `.devpace/project.md` 价值功能树
2. 匹配反馈到最相关的 PF（产品功能）和 BR（业务需求）
3. 无法匹配 → 记录为"未关联反馈"，建议创建新 BR

### Step 3：更新 MoS

如反馈涉及已定义的成效指标（MoS）：
- 缺陷 → 在 project.md 对应 MoS 处追加备注"[日期] 反馈：[问题]"
- 改进 → 建议调整 MoS 指标或新增指标

### Step 4：执行后续动作

根据分类执行：
- **缺陷** → 自动创建修复 CR（关联原 PF），进入推进模式
- **改进** → 追加到 project.md 的 PF 备注区，建议纳入下次迭代
- **新需求** → 提示用户使用 /pace-change 走变更管理流程

### Step 5：更新度量

在 `.devpace/metrics/dashboard.md` 增量更新缺陷逃逸率（如存在该指标行）。

## 输出

反馈处理结果摘要（2-3 行）：分类 + 关联 PF + 后续动作。
