# help-procedures-overview — 空参数帮助概览

> 由 SKILL.md 路由表加载。空参数时读取。

## Step 1：检查项目状态

检查项目根目录是否存在 `.devpace/state.md`。

## Step 2a：未初始化

如果 `.devpace/` 不存在：

```
devpace 是研发节奏管理器，帮你从需求到交付保持有序。

快速开始：`/pace-help quickstart`
查看所有命令：`/pace-help commands`
了解设计理论：`/pace-theory`
```

结束。

## Step 2b：已初始化

读取 `.devpace/state.md` 提取当前工作摘要。然后 Glob `.devpace/backlog/*.md` 检查 CR 状态。

按以下优先级输出第一个匹配的引导：

| 条件 | 输出 |
|------|------|
| 有 status: developing 的 CR | "正在开发 [CR 标题]。需要了解推进命令？`/pace-help dev`" |
| 有 status: in_review 的 CR | "有变更等待审核。需要了解审核流程？`/pace-help review`" |
| 有 status: created 但无 developing 的 CR | "有待开始的任务。需要了解如何启动？`/pace-help dev`" |
| backlog 为空 | "项目已初始化但还没有任务。试试 `/pace-help quickstart`" |
| 其他 | "输入 `/pace-help commands` 查看所有可用命令" |

## Step 3：附命令速查

无论 Step 2a 还是 Step 2b，末尾附：

```
还可以：
  /pace-help commands — 查看所有命令（HOW）
  /pace-theory <概念> — 了解设计理论（WHY）
  /pace-next — 获取下一步建议（WHAT）
```
