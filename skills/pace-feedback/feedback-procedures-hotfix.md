# 严重度评估与 Hotfix 加速规程

> **职责**：严重度矩阵、Hotfix 加速路径、外部数据摄入。report 紧急通道或 severity ≥ major 时加载。

## 严重度评估

### 影响范围×紧急程度矩阵

| 影响范围 | 紧急程度 | 建议严重度 | CR 类型 |
|---------|---------|----------|--------|
| 全部用户 | 立即修复 | critical | hotfix |
| 全部用户 | 尽快修复 | major | defect |
| 部分用户 | 立即修复 | major | hotfix |
| 部分用户 | 尽快修复 | major | defect |
| 单用户 | 任意 | minor | defect |
| 界面/文案 | 可等待 | trivial | defect |

hotfix + critical → 告知用户可走加速路径。

## Hotfix 加速路径

当 type:hotfix + severity:critical 时：

1. 告知用户："此问题严重度为 critical，建议走 hotfix 加速路径（跳过 in_review）。"
2. 用户确认后，CR 的 workflow.md 加速路径生效
3. 在 CR 事件表记录"加速路径：跳过 in_review，原因 [紧急描述]"
4. merged 后提醒用户补充事后审批记录

### 加速路径规则

- 仅 `type:hotfix` + `severity:critical` 可使用
- 用户必须显式确认（不自动启用）
- `report` 紧急通道自动评估加速资格（但仍需用户确认启用）
- 事后审批不可省略——merged 后在下一个 /pace-retro 或手动审批中补充
- 在 dashboard.md 中记录为"加速合并"（区分正常流程的 merged）

## 外部数据摄入

如 `.devpace/integrations/config.md` 存在：
- 读取告警映射表，根据告警等级自动建议严重度和 CR 类型
- 读取环境列表，自动关联问题发生的环境
