# <关键词>：搜索匹配

> 由 SKILL.md 路由表加载。仅在 `<关键词>` 子命令时读取。

## 步骤

1. 在 `.devpace/backlog/` 中按标题关键词搜索匹配的 CR
2. 有匹配 → 展示该 CR 的质量检查 checkbox 状态和事件记录

## 无匹配时 fallback

自动尝试在 `.devpace/project.md` 功能树中匹配 PF/BR/OBJ 名称：

- **功能树命中** → 提示："未找到变更记录，但在功能树中找到匹配——尝试 `/pace-status trace [匹配名称]`"
- **均无匹配** → "未找到匹配结果。尝试 `/pace-status detail` 查看全貌，或 `/pace-status trace <名称>` 追溯特定需求。"

## 导航

跟随匹配结果上下文：CR 匹配 → `/pace-dev`，PF 匹配 → `/pace-status trace`。
