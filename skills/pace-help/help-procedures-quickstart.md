# help-procedures-quickstart — 快速入门引导

> 由 SKILL.md 路由表加载。`quickstart` 子命令时读取。

## Step 1：检查项目状态

检查项目根目录是否存在 `.devpace/state.md`。

## Step 2a：未初始化

如果 `.devpace/` 不存在，输出 5 步快速入门：

```
devpace 快速入门（约 5 分钟）：

1. /pace-init      初始化项目（对话引导，创建 .devpace/ 目录）
2. /pace-biz       梳理需求（可选——已有明确需求可跳过）
3. /pace-dev       开始第一个任务（直接说"帮我做 XXX"也行）
4. /pace-review    完成后提交审核
5. /pace-status    随时查看进度

第一步：输入 /pace-init 开始。
```

## Step 2b：已初始化

如果 `.devpace/` 已存在，读取 `.devpace/state.md` 和 Glob `.devpace/backlog/*.md`，按项目阶段推荐：

| 条件 | 输出 |
|------|------|
| backlog 为空，无 CR | "项目已初始化。试试直接说'帮我做 XXX'，或用 `/pace-biz` 梳理需求。" |
| 有 status: created 的 CR | "有待开始的任务 [CR 标题]。输入 `/pace-dev` 或直接说'继续做 [标题]'。" |
| 有 status: developing 的 CR | "正在开发 [CR 标题]。输入 `/pace-dev` 继续推进。" |
| 有 status: in_review 的 CR | "[CR 标题] 等待审核。输入 `/pace-review` 查看审核状态。" |
| 其他 | "输入 `/pace-status` 查看当前项目全貌。" |

## Step 3：导航提示

末尾附：`更多帮助：/pace-help commands | 设计理论：/pace-theory | 下一步建议：/pace-next`
