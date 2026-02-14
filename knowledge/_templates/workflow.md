# 变更请求工作流

> **职责**：定义本项目变更请求的状态机。可根据项目实际情况裁剪。

## 状态流转

```
created → developing → verifying → review_ready → approved → merged
              ↑            │              │
              └────────────┘              │
              └───────────────────────────┘

          任何状态 ⇄ paused（暂停/恢复，工作成果保留）
```

## 阶段规则

### created → developing

- 必须关联一个产品功能
- 必须指定目标应用

### developing → verifying（Claude 自治）

准出条件（具体检查项见 gates.md）：
- [ ] 代码提交到 feature branch
- [ ] 项目门禁全部通过

### verifying → review_ready（Claude 自治）

准出条件（具体检查项见 gates.md）：
- [ ] 集成测试通过
- [ ] 项目门禁全部通过

### review_ready → approved（人类审批）

> ⚠️ Claude 必须停下，生成变更摘要，等待人类 review。

### approved → merged（Claude 执行）

合并后自动动作：
1. 更新关联产品功能状态
2. 更新 state.md
3. 更新 product-line.md 追溯树

### 任何状态 ⇄ paused（需求变更触发）

**进入 paused**：
- 触发：用户要求暂停/砍掉某个功能，或 /pace-change pause
- 保留：分支、代码、已通过的门禁进度、事件记录
- 动作：解除依赖此 CR 的其他 CR 的阻塞关系

**从 paused 恢复**：
- 触发：用户要求恢复，或 /pace-change resume
- 恢复到暂停前的状态
- 门禁可能需要重新验证（如果代码库在暂停期间有变化）
