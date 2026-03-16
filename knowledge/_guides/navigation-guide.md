# 全局导航集成指南

> **职责**：定义 pace-next / pace-pulse / pace-status 共享的导航路由规则。被 `rules/devpace-rules.md` 全局导航集成引用。

## 信号优先级

**权威源**：`knowledge/_signals/signal-priority.md`——pace-next / pace-pulse session-start / pace-status 概览三者共享。修改信号条件时同步检查三个消费方。

## 会话内定位

- **会话开始**（rules §1）= "推送式"快照（session-start 自动触发，<=3 行）。/pace-next = "拉取式"深度导航（用户主动调用，可展开 detail/why）。session-start 末尾已自然引导 /pace-next（通过 pace-status 概览的候选计数），无需额外提示
- **merged 后**：见下方 target skill 完成后路由表 /pace-dev 行

## target skill 完成后路由表

以下 Skill 完成主要操作后，追加下一步引导：

| Skill | 触发时机 | 引导行为 |
|-------|---------|---------|
| /pace-dev（merged 后管道完成） | 7 步管道全部执行后 | 迭代内有未开始 PF -> 确认式"继续做 [PF 名]？"；无 -> 委托 signal-priority.md top-1 信号 |
| /pace-review | 人类审批完成后 | 委托 signal-priority.md top-1 信号 |
| /pace-retro（非 update/mid） | 回顾报告输出后 | 委托 signal-priority.md top-1 信号（通常为 S14 规划新迭代） |
| /pace-release close | 发布关闭确认后 | 委托 signal-priority.md top-1 信号（通常为 S9 回顾/S5 验证） |
| /pace-feedback（defect/hotfix） | CR 创建后 | 确认式"已创建修复任务 [CR 标题]。现在就修？"-> 确认则进入 /pace-dev |
| /pace-change | Step 6 下游引导 | 已有完整引导表（不变） |

## 引导格式

- **确认式**："[完成描述]。[下一步建议]？" -> 等待用户响应
- **委托式**：读取 signal-priority.md top-1 信号 -> 按 `knowledge/_signals/signal-priority.md` 的信号-命令映射输出建议。无信号时追加"-> /pace-next 查看下一步"

## 自主级别感知

- **辅助**：始终确认式（即使委托式信号也转为确认式）
- **标准**（默认）：确认式用于确认式场景，委托式用于委托式场景
- **自主**：同一会话连续 3 次确认后简化为内联提示（不等确认，可被打断）

## 与 session-start 去重

pace-next 在距 session-start < 5 分钟时跳过已通知的最高信号（详见 `skills/pace-next/next-procedures.md` Step 3 去重规则）。

## 会话结束

会话结束总结中，"下一步"行直接写入 state.md "下一步"字段。如有明确下一步信号，格式为"下次建议：[pace-next top-1 建议概要]"。
