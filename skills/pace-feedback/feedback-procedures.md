# 反馈处理执行规程

> **职责**：反馈收集与生产事件处理的详细流程。/pace-feedback 触发后，Claude 按需读取本文件。

## 问题摄入详情

### 引导式问题收集

当用户未提供完整描述时，使用以下引导模板：

1. **现象描述**："出现了什么问题？（如：页面白屏、接口超时、数据丢失、体验不佳）"
2. **影响范围**："影响多少用户？"
   - 全部用户 / 部分用户（某地区/某版本）/ 单个用户 / 未知
3. **紧急程度**："需要多快修复？"
   - 立即修复（生产不可用）/ 尽快修复（功能受损）/ 可等待（下个迭代修复）
4. **复现步骤**（可选）："能否描述如何复现？"
5. **首次发现时间**（可选）："什么时候发现的？最近有部署吗？"

### 自动信息补充

Claude 自动从项目上下文补充：
- 读取最近的 Release（`.devpace/releases/`）确定最近部署时间
- 扫描 backlog/ 中最近 merged 的 CR，列出潜在引入源
- 读取 checks.md 确认是否有相关质量检查覆盖

## 影响追溯详情

### 追溯路径

```
问题描述 → 匹配 PF（关键词/模块）→ 查找该 PF 的 CR 历史 → 定位最近 Release → 缩小引入范围
```

### 追溯数据源

1. **project.md 价值功能树**：问题关键词 → 匹配 PF 标题或 BR 描述
2. **backlog/ CR 文件**：匹配 PF 下所有 CR，按 merged 时间倒排，聚焦最近 merged 的 CR
3. **releases/ Release 文件**：查找包含该 CR 的 Release，确认部署时间线
4. **CR 事件表**：检查是否有质量检查跳过或加速路径的记录

### 追溯报告格式

```
## 影响追溯

**问题**：[问题描述]
**关联功能**：[PF 标题]（[PF-ID]）→ [BR 标题]
**可疑 CR**：[CR 标题]（merged [日期]，Release [REL-xxx]）
**置信度**：高/中/低
**依据**：[追溯逻辑说明]
```

置信度说明：
- **高**：问题明确指向某个 PF，且该 PF 最近有 CR merged
- **中**：问题可能涉及多个 PF，或 CR 未在最近 Release 中
- **低**：无法明确匹配 PF，需人工确认

## 外部数据摄入

如 `.devpace/integrations/config.md` 存在：
- 读取告警映射表，根据告警等级自动建议严重度和 CR 类型
- 读取环境列表，自动关联问题发生的环境

## Hotfix 加速路径

当 type:hotfix + severity:critical 时：

1. 告知用户："此问题严重度为 critical，建议走 hotfix 加速路径（跳过 in_review）。"
2. 用户确认后，CR 的 workflow.md 加速路径生效
3. 在 CR 事件表记录"加速路径：跳过 in_review，原因 [紧急描述]"
4. merged 后提醒用户补充事后审批记录

### 加速路径规则

- 仅 `type:hotfix` + `severity:critical` 可使用
- 用户必须显式确认（不自动启用）
- 事后审批不可省略——merged 后在下一个 /pace-retro 或手动审批中补充
- 在 dashboard.md 中记录为"加速合并"（区分正常流程的 merged）

## 根因分析记录

### 创建时填充

```markdown
## 根因分析

- **现象**：[用户报告的问题描述]
- **根因**：待调查
- **引入点**：[追溯结果，如 CR-xxx] 或 待确认
- **预防措施**：待修复后填写
```

### 修复后填充

defect CR merged 后，pace-learn 自动提取根因分析：
- 更新"根因"为实际原因
- 更新"引入点"为确认的 CR
- 填充"预防措施"
- 提取为 insights.md 的防御 pattern（如该类问题可泛化）

## 度量更新

### 缺陷逃逸率增量更新

每创建一个 defect/hotfix CR，自动在 dashboard.md 更新：
- 缺陷逃逸计数 +1
- 重新计算缺陷逃逸率

### 缺陷修复周期

defect CR merged 后，计算从创建到 merged 的天数，更新到 dashboard.md。

## 运维反馈规则（从 devpace-rules.md §15 迁入）

### 主动识别触发

**触发词**："线上问题""生产报错""用户反馈 bug""告警""监控异常""部署后""上线后发现"

识别到运维场景时：
1. 自动推断角色为 Ops（§13）
2. 引导用户使用 /pace-feedback report 报告问题
3. 如有活跃 Release → 自动关联追溯

### 反馈闭环

会话开始时节奏检测（§1）额外关注：
- 存在 deployed 但未 verified 的 Release → 附加"Release [REL-xxx] 已部署但未验证，建议执行 /pace-release verify"
- 存在 defect CR 占比 > 30% → 附加"缺陷比例较高，建议关注质量改进"
- 距上次 /pace-retro > 7 天且有 defect CR → 附加"建议执行 /pace-retro 分析缺陷趋势"

### Hotfix 紧急通道

当用户报告 critical 级问题时：
1. 立即建议使用 /pace-feedback report 创建 hotfix CR
2. 提示可走加速路径（跳过 in_review）
3. 修复完成后提醒补充事后审批和根因分析
