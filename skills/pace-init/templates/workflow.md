# 变更请求工作流

> **职责**：定义本项目变更请求的状态机。可根据项目实际情况裁剪。

## 状态流转

```
created → developing → verifying → in_review → approved → merged → released（可选）
              ↑            │              │
              └────────────┘              │
              └───────────────────────────┘

          任何状态 ⇄ paused（暂停/恢复，工作成果保留）
```

## 阶段规则

### created → developing

- 必须关联一个产品功能
- 必须指定目标应用
- Claude 完成意图检查点（复杂度自适应：简单=记录原话直接开工，标准=补充范围+验收条件，复杂=完整意图+必要时问用户）

### developing → verifying（Claude 自治）

准出条件（具体检查项见 checks.md）：
- [ ] 代码提交到 feature branch
- [ ] 项目质量检查全部通过

### verifying → in_review（Claude 自治）

准出条件（具体检查项见 checks.md）：
- [ ] 集成测试通过
- [ ] 项目质量检查全部通过

### in_review → approved（人类审批）

> ⚠️ Claude 必须停下，生成变更摘要，等待人类 review。

### approved → merged（Claude 执行）

合并后必须执行的连锁更新：
1. 更新 PF 状态：如果该 PF 的所有 CR 均 merged → PF 标记 ✅
2. 更新 project.md 价值功能树中的 CR emoji
3. 更新 state.md：进行中/下一步
4. 更新 iterations/current.md：进度
5. 判断是否纳入 Release：如存在 staging 状态的 Release 且该 CR 在候选列表中 → 更新 Release 文件

### merged → released（Release 流程触发）

> 可选转换——仅当项目使用 Release 管理时生效。

- 触发条件：CR 所在的 Release 完成部署验证并关闭
- 由 Release 关闭流程自动批量标记，不可手动直接设置
- 不使用 Release 流程时，merged 是有效终态（向后兼容）

### Hotfix 加速路径（type:hotfix + severity:critical）

```
created → developing → verifying → merged（跳过 in_review）
```

- 仅 `type:hotfix` 且 `severity:critical` 可使用
- 跳过 in_review 但仍需在事件表记录"加速路径：跳过 in_review，原因 [紧急描述]"
- merged 后必须补充事后审批记录

### 任何状态 ⇄ paused（需求变更触发）

> paused 是一个特殊状态：可从任何状态进入，保留全部工作成果（分支、代码、质量检查进度），恢复时回到暂停前的状态。以下为操作规则。

**进入 paused**：
- 触发：用户要求暂停/砍掉某个功能，或 /pace-change pause
- 保留：分支、代码、已通过的质量检查进度、事件记录
- 动作：
  1. CR 增加 `暂停前状态` 字段，记录当前状态值（用于恢复）
  2. CR 状态改为 paused
  3. 解除依赖此 CR 的其他 CR 的阻塞关系
  4. 更新 project.md 功能树：受影响的功能标记 ⏸️
  5. 更新 state.md：反映暂停

**从 paused 恢复**：
- 触发：用户要求恢复，或 /pace-change resume
- 动作：
  1. CR 状态恢复为 `暂停前状态` 字段的值
  2. 移除 `暂停前状态` 字段
  3. 代码库在暂停期间有变化时，重新验证质量检查
  4. 恢复 project.md 功能树标记（⏸️ → 恢复前的标记）
  5. 更新 state.md：反映恢复
