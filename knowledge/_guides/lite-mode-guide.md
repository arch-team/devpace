# /pace-biz lite 模式子命令可用性

> **职责**：定义 /pace-biz 各子命令在 lite 模式下的行为。被 SKILL.md 路由表和各 procedures Step 0 引用。

## 可用性表

| 子命令 | lite 模式行为 |
|--------|-------------|
| opportunity / epic | 不可用 — 提示升级到完整模式或 /pace-change add |
| decompose EPIC-xxx | 不可用 — lite 无 Epic/BR 层 |
| decompose BR-xxx | 不可用 — lite 无 BR 层 |
| refine | 仅支持 PF — BR-xxx 参数终止 |
| align | 简化为 OBJ→PF→CR 链路检查 |
| view | 简化为 OBJ→PF→CR 树视图 |
| discover / import / infer | 可用 — 映射目标简化为 PF |

## 不可用时的标准提示模板

```
lite 模式不支持 [子命令]。[原因]。
替代：`/pace-change add` 快速添加需求。
升级：`/pace-init --upgrade-mode` 启用完整 OPP/Epic/BR 能力。
```

## Consumers

SKILL.md (路由), biz-procedures-opportunity, biz-procedures-epic, biz-procedures-decompose-epic, biz-procedures-decompose-br, biz-procedures-refine, biz-procedures-align, biz-procedures-view
