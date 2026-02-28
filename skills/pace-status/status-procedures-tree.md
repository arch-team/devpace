# tree：完整价值链路

> 由 SKILL.md 路由表加载。仅在 `tree` 子命令时读取。

## 步骤

1. 读取 `.devpace/project.md` 的价值功能树部分
2. 对每个 PF 节点，通过 Grep 快速统计 backlog/ 中 CR 状态分布
3. 展示完整价值链路，每个节点附带状态 emoji 和进度

## 导航

输出末尾追加 1 行：`→ 当前迭代聚焦：/pace-status detail`
