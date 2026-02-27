# 反馈处理通用规程

> **职责**：反馈 ID 分配、草稿恢复、降级模式、后续动作路由、草稿清理。每次 /pace-feedback 触发时加载。状态追踪见 `feedback-procedures-status.md`。

## 反馈 ID 分配

每条进入 pace-feedback 的反馈分配唯一 ID，格式 `FB-NNN`（三位数字，从 001 递增）。

**编号规则**：
- 扫描 `.devpace/feedback-log.md` 获取当前最大编号，+1 为新 ID
- 文件不存在时从 FB-001 开始
- FB-ID 与最终分类无关——无论生产事件、缺陷、改进、新需求还是待定，均分配 ID

## 反馈草稿与中断恢复

### 草稿机制

当收集到第一个有效信息（症状描述）时，在 `.devpace/backlog/FEEDBACK-DRAFT.md` 创建草稿文件：

```markdown
# 反馈草稿

- **FB-ID**：FB-xxx
- **症状**：[已收集的描述]
- **影响范围**：[已收集 或 待收集]
- **紧急程度**：[已收集 或 待收集]
- **复现步骤**：[已收集 或 待收集]
- **首次发现**：[已收集 或 待收集]
- **分类**：[已分类 或 待分诊]
- **收集阶段**：[round-1 | round-2 | classified | traced]
```

### 恢复流程

```
检查 FEEDBACK-DRAFT.md 存在?
├── 是 → "上次反馈（FB-xxx：[症状摘要]）未完成，是否继续？"
│   ├── 继续 → 读取草稿，跳到 收集阶段 对应步骤
│   └── 放弃 → 删除草稿，从头开始
└── 否 → 正常流程
```

## 降级模式

当 `.devpace/` 存在但 `releases/` 不存在时，pace-feedback 以降级模式运行：

| 功能 | 完整模式 | 降级模式 |
|------|---------|---------|
| 反馈分类 / 严重度评估 / CR 创建 | ✅ | ✅ |
| 改进建议池 / 反馈收件箱 / FB-ID 追踪 | ✅ | ✅ |
| Release 追溯 / 部署时间关联 | ✅ | ⏭️ 跳过 |

降级模式下追溯步骤改为：仅基于 backlog/ CR 历史和 Git 日志进行关联分析。

## 后续动作执行

根据分类执行：
- **生产事件** → 自动创建 CR（type:defect 或 type:hotfix），格式遵循 `knowledge/_schema/cr-format.md`：
  1. 填充根因分析 section（已知信息 + 历史根因推荐，详见 `feedback-procedures-analysis.md`）
  2. 关联到 PF 和 Release（如有）
  3. hotfix + critical → 告知用户可走加速路径（详见 `feedback-procedures-hotfix.md`）
- **缺陷** → 自动创建修复 CR（type:defect，关联原 PF），进入推进模式
- **改进** → 记录到 project.md 的 PF 改进建议池（见下方格式），建议纳入下次迭代
- **新需求** → 提示用户使用 /pace-change 走变更管理流程
- **记录待定** → 保存到反馈收件箱（`.devpace/feedback-inbox.md`）

### 改进建议池格式

改进建议写入 project.md 功能规格 section 中对应 PF 下方（未溢出时）或 PF 文件中（已溢出时）：

```markdown
### 改进建议池

| FB-ID | 描述 | 记录日期 | 状态 |
|-------|------|---------|------|
| FB-005 | 登录页加载慢 | 2026-02-27 | 待规划 |
```

状态值：`待规划` | `已纳入 [迭代/CR]` | `已拒绝`。pace-plan 在规划迭代时扫描"待规划"条目。

### 反馈收件箱格式

"记录待定"类型的反馈保存到 `.devpace/feedback-inbox.md`：

```markdown
# 反馈收件箱

> 暂未分类的反馈。pace-plan 规划迭代时提醒处理。

| FB-ID | 原始描述 | 记录日期 | 处理状态 |
|-------|---------|---------|---------|
| FB-003 | 用户提到搜索有时不准确 | 2026-02-27 | 待处理 |
```

## 草稿清理

处理完成后（CR 创建/Inbox 记录/project.md 更新），删除 `.devpace/backlog/FEEDBACK-DRAFT.md`。
