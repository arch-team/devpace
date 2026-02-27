# 执行规程

> **职责**：Step 4-6——方案提出、执行记录、下游引导与外部同步。按 SKILL.md 路由表按需加载。

## Step 4：提出调整方案

按变更类型提出具体方案（各类型的分析逻辑和执行细节见 `change-procedures-types.md`）。

**变更影响预览**（OPT-08）：

Step 4 追加"预览变更清单"——列出将修改的文件和关键变更内容：
- **默认折叠**：低风险时只展示文件清单（如"将修改 3 个文件：project.md, CR-005.md, current.md"）
- **追问或高风险时展开**：展示每个文件的具体变更内容
- `--dry-run` 标志：只输出预览清单，不继续执行

**必须等待用户确认**后再执行。不自作主张调整计划。

## Step 5：执行并记录

确认后执行（各类型的 CR 更新细节见 `change-procedures-types.md`）：

1. 更新相关 CR 文件（状态、意图、质量检查、事件表）
2. 更新 `project.md` 功能树（新增/暂停/恢复/状态变更）
   - 无 project.md → 更新 state.md 功能概览行
3. 更新 PF 文件（modify 且 PF 已溢出时，细节见 types）
4. 更新 `iterations/current.md` 计划和变更记录表（格式参考 Plugin `knowledge/_schema/iteration-format.md`）
   - 无迭代文件 → 跳过此步
5. 更新 `state.md` 快照（当前工作 + 下一步）
6. **变更管理指标更新**（OPT-15）：dashboard.md 存在时增量更新变更管理 section

变更事件记录到迭代文件的"变更记录"表：

```markdown
## 变更记录

| 日期 | 类型 | 描述 | 影响 |
|------|------|------|------|
```

无迭代文件时，变更事件记录到 CR 文件的事件表。

## Step 6：下游引导 + 外部同步

### 外部同步检查

> OPT-20：执行后自动生成同步摘要（不只是提醒）。

变更操作（pause/resume/priority change 等）执行完成后：

1. 检查受影响 CR 是否有外部关联（读取 CR 文件的"外部关联"字段）
2. 有关联 → 生成同步摘要 + 提醒：
   - 格式："[CR 标题] 状态变更为 [新状态]。建议运行 `/pace-sync push CR-{id}` 同步。"
   - 批量变更时合并："N 个已关联 CR 的状态已变更，建议运行 `/pace-sync push` 同步。"
3. 无关联 → 静默跳过

**规则**：
- 仅提醒，不自动执行 push（Phase 18 MVP 行为）
- sync-mapping.md 不存在时跳过整个步骤

### 下游引导

按变更类型精确引导后续操作（各类型的引导详情见 `change-procedures-types.md` 下游引导表）。
