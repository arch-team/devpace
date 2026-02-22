# 发布管理执行规程

> **职责**：Release 生命周期的详细执行规则。/pace-release 触发后，Claude 按需读取本文件。

## Create 详细流程

### 候选 CR 收集

1. 扫描 `.devpace/backlog/` 所有 CR 文件
2. 筛选条件：状态为 `merged` 且无"关联 Release"字段（或字段为空）
3. 按类型排序展示：hotfix > defect > feature

### 候选展示格式

```
## Release 候选 CR

| CR | 标题 | 类型 | PF | 合并日期 |
|----|------|------|-----|---------|
| CR-001 | [标题] | feature | PF-001 | 2026-02-20 |
| CR-003 | [标题] | defect | PF-002 | 2026-02-21 |

共 N 个候选 CR。全部纳入还是选择部分？
```

### Release 创建

1. 用户确认纳入范围后，创建 REL-xxx.md
2. ID 自增：扫描 `.devpace/releases/` 最大编号 +1
3. 状态初始化为 `staging`
4. 自动填充验证清单（默认 4 项 + 项目自定义）
5. 更新各 CR 文件的"关联 Release"字段为 REL-xxx
6. 更新 state.md 发布状态段

### 版本号建议

- 全部为 feature → minor 版本递增（如 1.2.0 → 1.3.0）
- 包含 defect/hotfix → patch 版本递增（如 1.2.0 → 1.2.1）
- 用户可自定义版本号

## Deploy 详细流程

### 部署确认

1. 确认 Release 处于 `staging` 状态
2. 询问部署目标环境（如有多环境配置）
3. 用户确认已执行部署操作
4. 在 Release 部署记录表追加：

```markdown
| 日期 | 环境 | 操作 | 结果 | 备注 |
|------|------|------|------|------|
| 2026-02-21 | production | 部署 | 成功 | [用户备注] |
```

5. Release 状态 staging → deployed
6. 更新 state.md 发布状态段

## Verify 详细流程

### 验证清单

1. 展示 Release 的验证清单
2. 逐项引导确认（可批量确认）
3. 用户自定义验证项可动态追加

### 验证通过

全部验证项勾选 → Release 状态 deployed → verified

### 验证发现问题

1. 在 Release "部署后问题"表追加记录
2. 引导用户创建 defect/hotfix CR（调用 /pace-feedback report 逻辑）
3. 新创建的 defect CR 自动关联当前 Release
4. Release 状态保持 deployed（不回退到 staging）

## Close 详细流程

### 前置检查

1. Release 必须处于 `verified` 状态
2. "部署后问题"表中所有问题的"关联 CR"都有值（均已创建修复 CR）
3. 检查未通过 → 提示用户先处理未解决的问题

### 关闭连锁更新

Release verified → closed 时自动执行：

1. **CR 状态批量更新**：Release 包含的所有 CR，状态 merged → released
   - 在各 CR 事件表追加"released via REL-xxx"
2. **project.md 更新**：功能树中 released CR 标记 🚀
3. **iterations/current.md 更新**：产品功能表 Release 列填入 REL-xxx
4. **state.md 更新**：移除已关闭 Release 的发布状态段
5. **dashboard.md 更新**：
   - 部署频率 +1
   - 计算本 Release 各 CR 的变更前置时间（created → released）
   - 如有 defect CR 关联此 Release → 更新变更失败率

### 关闭输出

```
Release REL-xxx 已关闭。
- N 个 CR 状态更新为 released
- 功能树已更新
- 度量数据已更新（部署频率、变更前置时间）
```

## Status 详细流程

### 无活跃 Release

输出："当前没有进行中的 Release。N 个 merged CR 待发布。"

### 有活跃 Release

```
## Release 状态

REL-xxx：[版本号] — [状态]
- 包含 CR：N 个（feature:A, defect:B, hotfix:C）
- 部署后问题：M 个（已处理 K）
- 验证进度：X/Y 项通过
- 建议下一步：[deploy/verify/close/处理问题]
```

## 发布管理规则（从 devpace-rules.md §14 迁入）

### Release 流程

```
/pace-release create → staging → deploy确认 → deployed → verify通过 → verified → close → closed
                                                   │
                                                   └→ 发现问题 → /pace-feedback report → defect CR
```

### Release 规则

- **可选性**：`.devpace/releases/` 不存在或无 Release 文件时，所有 Release 行为静默跳过
- **候选收集**：仅 merged 且未关联 Release 的 CR 可纳入新 Release
- **状态机**：staging → deployed → verified → closed，不可回退
- **人类确认**：deployed 和 verified 状态转换需人类确认
- **自动关闭**：verified → closed 由 Claude 自动执行（含连锁更新）

### Release 关闭连锁更新

Release 关闭时自动执行（补充 §2 merged 后连锁更新）：

1. 关联 CR 状态批量 merged → released
2. project.md 功能树 CR 标记 🚀
3. iterations/current.md Release 列更新
4. state.md 发布状态段更新
5. dashboard.md 度量更新（部署频率、变更前置时间、变更失败率）

### 已纳入 Release 的 CR 变更

当用户对已纳入 Release（staging/deployed）的 CR 发起变更时：

1. **影响分析**：评估变更对 Release 稳定性的影响
2. **高风险变更**：建议从 Release 中移出该 CR，在下个 Release 中包含
3. **低风险变更**：允许原地修改，在 Release 部署记录中注明
4. **已 deployed 的 Release**：不允许修改包含的 CR，发现问题走 /pace-feedback report 创建新 defect CR

## 集成管理规则（从 devpace-rules.md §16 迁入）

### 集成原则

- **手动摄入始终可用**：即使无集成配置，所有功能通过手动输入可用
- **集成是增强不是前置**：集成配置提供自动化便利，但不是必需
- **不自建部署/监控**：devpace 追踪状态，不执行实际部署或监控操作

### 集成配置使用

当 `integrations/config.md` 存在时：
- /pace-release：自动填充目标环境选项
- /pace-feedback：根据告警映射自动建议严重度
- 节奏检测：可检查部署相关信号

### 降级行为

当无集成配置时：
- 所有功能正常工作，仅需手动输入更多信息
- 不提示"请先配置集成"——集成是可选增强
