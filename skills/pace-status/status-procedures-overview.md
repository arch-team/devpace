# 快速概览

> 由 SKILL.md 路由表加载。$ARGUMENTS 为空或无法匹配任何子命令时执行。

## 步骤

1. 读取 `.devpace/state.md`
2. 以 **≤ 3 行** 自然语言 + 进度条输出，不暴露 ID（NF6 硬约束）
3. 如果有阻塞项，高亮提醒
4. 角色适配：pace-role 已设角色时，概览侧重角色关注维度

## 进度条规则

- `█` = 已完成，`░` = 未完成，总长 10 字符
- 括号内 CR merged/total
- 仅当前迭代主要功能组
- **降级**：终端不支持 Unicode 块字符时用 `[====----] 50%` 或纯百分比

## 建议下一步（概览末尾附加）

**缓存优先**：概览信号采集前先检查 `.devpace/.signal-cache`（规则见 `knowledge/signal-collection.md`）。缓存命中（< 5 分钟）→ 使用缓存的 `top_signal` 字段作为建议行信号源。缓存过期 → 执行完整采集。

**定位**：/pace-next 的**轻量子集**——仅 top-1 信号 + 命令指引，不含推理。多信号竞争取最高优先级 1 条并追加候选计数。

**权威源**：`knowledge/signal-priority.md`。本表仅暴露 `status-subset = ✅` 的信号子集，编号和条件与权威源一致。

| 信号 ID | 条件 | 建议 |
|:-------:|------|------|
| S1 | backlog/ 有 `in_review` CR | "有 N 个变更等待审批 → /pace-review" |
| S3 | 有 developing CR | "继续 [CR 标题] → /pace-dev" |
| S5 | deployed 未 verified Release | "验证最近部署 → /pace-release" |
| S8 | 迭代完成率 > 80% | "迭代接近完成 → /pace-retro 后 /pace-plan" |
| S9 | 距 retro > 7 天 + merged CR | "建议回顾 → /pace-retro" |
| S13 | PF 无对应 CR | "开始新功能 → 说'帮我实现 X'" |
| S15 | backlog 全部 merged/released | "所有任务完成——开始新功能或回顾" |
| — | 其他 | 不附加建议 |

**候选计数**：当有 2+ 信号命中时，top-1 建议行末尾追加 `（还有 N 个候选 → /pace-next detail）`，引导用户获取深度导航。

## 推/拉去重

距会话开始 < 5 分钟时省略建议行（session-start 刚给过节奏提醒）。

## 同步摘要（sync-mapping.md 存在时）

`sync-mapping.md` 存在 → 概览末尾追加 1 行同步摘要：`🔗 同步：{N} 已同步，{M} 待推送`。不存在时静默跳过。

规则：全部已同步省略待推送数 | 无关联 CR 不显示 | gh 不可用显示"状态未检查"。

## 附加行上限

概览主体 ≤ 3 行，附加行（建议 + 同步）≤ 2 行。超出按优先级：建议 > 同步。**总输出 ≤ 5 行**。
