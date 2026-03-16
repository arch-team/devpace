# devpace 信息分层架构

> **职责**：devpace Plugin 的六层信息架构和资产类型定义。

## 六层架构

```
Layer 6: knowledge/theory     (Why  — 概念知识，被动加载，极少变更)
Layer 5: rules/               (Must — 行为约束，会话启动时自动加载)
Layer 4: knowledge/_schema/*/  (Shape — 数据格式契约，按需加载；分 entity/process/integration/auxiliary)
Layer 3: skills/*/SKILL.md    (What — 路由层，description 触发加载)
Layer 2: skills/*/*-procedures.md (How — 操作步骤，按状态/子命令条件加载)
Layer 1: knowledge/_templates/ (Instance — 具体实例，实例化时加载)
```

依赖方向：**仅允许下层引用上层**。Layer 2 引用 Layer 4 的格式定义；Layer 4 不引用 Layer 2 的实现细节。

## 信息类型 → 资产映射

| 信息类型 | Plugin 资产 | 特征 |
|---------|------------|------|
| 步骤（Procedure） | `*-procedures.md` | 按步操作指令 |
| 约束（Principle） | `rules/*.md` | 行为规范 |
| 概念（Concept） | `knowledge/*.md` | 背景知识 |
| 结构（Structure） | `knowledge/_schema/*/*.md` | 数据格式定义（四子目录分组） |
| 路由（Process） | `SKILL.md` | 工作流分发 |
| 实例（Fact） | `knowledge/_templates/*.md` | 具体模板 |
