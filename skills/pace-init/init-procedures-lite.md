# 轻量模式初始化规程

> **职责**：`--lite` 参数时的初始化行为覆盖。在 core 流程之后执行。

## 行为覆盖

### project.md 结构简化

轻量模式下 project.md 的价值功能树使用简化结构（跳过 OPP/Epic/BR 层）：

```
## 价值功能树

OBJ-1：[目标名称]
├── PF-001：[功能名]（[用户故事]）→ (待创建 CR)
├── PF-002：[功能名]（[用户故事]）→ (待创建 CR)
└── PF-003：[功能名]（[用户故事]）→ (待创建 CR)
```

### 跳过的组件

轻量模式下**不创建**以下内容：
- `opportunities.md`（Opportunity 看板）
- `epics/` 目录（Epic 文件）
- `requirements/` 目录（BR 溢出文件）
- project.md 中的 Epic/BR 层级

### project.md 标记

在 project.md 顶部元数据中添加标记：
```
mode: lite
```

### 与完整模式的兼容

- 轻量模式项目可随时升级为完整模式：`/pace-init --upgrade`（将 PF 归组到自动创建的 BR 下）
- `/pace-biz` 在 lite 模式项目中仍可使用——首次创建 Epic/BR 时自动升级为完整模式
- `/pace-dev`、`/pace-change`、`/pace-plan` 等核心命令在 lite 模式下正常工作（跳过 Epic/BR 相关逻辑）

### 初始化引导调整

轻量模式的初始化对话简化为：
1. 项目名称确认
2. "这个项目要做什么？"（1-2 句话 → Claude 推断 OBJ + PF）
3. 确认功能列表 → 完成

不询问 Vision、Strategy、MoS 等高级概念（这些在 full 模式中引导）。
