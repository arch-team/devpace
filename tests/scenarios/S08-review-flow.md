# 场景 S08: Code Review

**对应需求**: S8, F1.7
**验证目标**: 审批→merged 自动更新；打回→developing + 原因

## 前置条件

- 至少有 1 个 in_review 状态的 CR

## 执行步骤

### 审批流程

| # | 人类动作 | 期望 Claude 行为 |
|---|---------|-----------------|
| 1 | CR 到达 in_review | 自动生成变更摘要（改了什么、为什么、影响） |
| 2 | 说"通过"或"lgtm" | CR → approved → merged，触发连锁更新 |
| 3 | 验证连锁更新 | PF 状态更新、功能树 emoji 更新、state.md 更新 |

### 打回流程

| # | 人类动作 | 期望 Claude 行为 |
|---|---------|-----------------|
| 1 | CR 到达 in_review | 自动生成变更摘要 |
| 2 | 说"打回，[原因]" | CR → developing，事件表记录打回原因 |
| 3 | 继续推进 | 基于打回反馈修复，重新提交 review |

## 验收标准

- [ ] 自动生成变更摘要（含改了什么、为什么、影响范围）
- [ ] 审批后自动合并和状态更新
- [ ] merged 后触发连锁更新（PF 状态、功能树、state.md、iterations）
- [ ] 打回后回到 developing 并记录原因

## 评分维度

| 维度 | Pass | Partial | Fail |
|------|------|---------|------|
| 变更摘要 | 完整清晰 | 有但信息不全 | 无摘要 |
| 审批流程 | 一步完成 merged + 连锁 | merged 但遗漏连锁 | 流程断裂 |
| 打回流程 | 回到 developing + 记录 | 回到但无记录 | 未处理 |
| 意图一致性 | 对比 diff 与意图 | 部分对比 | 无对比 |

## 检查产物

- `.devpace/backlog/CR-*.md` — 状态 merged 或 developing（打回）
- `.devpace/project.md` — 功能树 emoji 更新
- `.devpace/state.md` — 反映审批结果
- `.devpace/iterations/current.md` — 进度更新
