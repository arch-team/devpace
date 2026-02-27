# 发布管理执行规程——引导式向导

> **职责**：空参数调用 `/pace-release` 时的引导式向导流程。
>
> **自包含**：本文件独立执行，不需要加载其他 procedures 文件。

## §0 速查卡片

- **状态检测**：扫描活跃 Release + rolled_back Release + merged CR → 按优先级引导下一步
- **Rolled_back 追踪**：检查回滚后修复 CR 状态，信息性提醒（不阻断）
- **交互规则**：AskUserQuestion 提供选项 → 用户确认后执行对应流程 → 不暴露子命令名称

## 状态检测与引导

1. 扫描 `.devpace/releases/` 查找活跃 Release（状态非 closed/rolled_back）
2. 扫描 `.devpace/releases/` 查找 rolled_back Release，检查其后续修复状态
3. 扫描 `.devpace/backlog/` 查找 merged 且未关联 Release 的 CR
4. 根据以下优先级引导：

| 检测到的状态 | 引导行为 | 自动执行 |
|-------------|---------|---------|
| 有 verified Release | "Release v{version} 验证通过。完成发布？（将自动生成 Changelog、更新版本号、创建 Git Tag）" | → close 流程 |
| 有 deployed Release | "Release v{version} 已部署。要开始验证吗？" + 附加选项"出了问题？" | → verify 或 rollback 流程 |
| 有 staging Release | "Release v{version} 已准备好，包含 N 个变更。下一步：部署到 [环境]？" | → deploy 流程 |
| 无活跃 Release + 有 merged CR | "有 N 个已完成的任务可以发布。要创建新发布吗？" | → create 流程 |
| 无活跃 Release + 无 merged CR | "当前没有待发布的变更。" | 无操作 |

## Rolled_back Release 后续追踪

在引导结果输出**之前**，如果步骤 2 发现 rolled_back Release，附加追踪提醒：

1. 读取 rolled_back Release 的"部署后问题"表和关联的 defect/hotfix CR
2. 检查这些 CR 的当前状态（developing/verifying/merged/released）
3. 输出提醒（插入到主引导行为之前）：

```
⚠️ Release REL-{xxx} (v{version}) 已回滚，后续修复状态：
- CR-{yyy}（{类型}）：{状态}
- CR-{zzz}（{类型}）：{状态}
{所有 CR 均 merged/released → "修复 CR 已就绪，可纳入新 Release。"}
{部分 CR 未完成 → "建议处理修复 CR 后再推进新 Release。"}
```

4. 提醒是信息性的，不阻断后续引导流程——用户可以选择继续创建新 Release 或先处理修复 CR
5. 多个 rolled_back Release 时，仅展示最近一个（按 ID 降序）

## 引导交互规则

- 每个引导问题使用 AskUserQuestion 工具，提供明确选项
- 用户确认后直接执行对应子命令的完整流程
- 用户拒绝或选择其他操作 → 展示可用选项
- 引导过程中向用户说明正在做什么，但不暴露子命令名称（对齐 §3 自然语言映射）
