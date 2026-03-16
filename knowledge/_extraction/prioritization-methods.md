# 优先级评估方法论

> **职责**：定义 BR/PF 优先级评估的标准方法及选择条件。/pace-biz decompose 引用此参考知识。

## 方法 A：Value x Effort 矩阵（默认）

- Value（价值）：高/中/低 -- 对 Epic MoS 的贡献度
- Effort（成本）：高/中/低 -- 预估实现复杂度
- 映射：高价值+低成本=P0 | 高价值+高成本 或 中价值+低成本=P1 | 其他=P2
- 展示评估矩阵让用户确认或覆盖（用户可直接指定优先级跳过矩阵）

## 方法 B：MoSCoW

- Must have -> P0 | Should have -> P1 | Could have -> P2 | Won't have -> 标记"不做"
- 引导问题："这个需求不做的话，Epic 还能交付核心价值吗？"（Must 判定）

## 方法 C：Kano 模型

- 基本型（缺失则不满）-> P0 | 期望型（有则满意）-> P1 | 兴奋型（超预期）-> P2
- 引导问题："如果没有这个功能，用户会觉得产品有问题吗？"（基本型判定）

## 方法选择条件

| 条件 | 选择方法 |
|------|---------|
| 默认（无特殊触发） | Value x Effort |
| 用户指定 `--moscow` | MoSCoW |
| BR 候选 > 8 个 | 建议 MoSCoW（分类效率更高） |
| 用户指定 `--kano` | Kano |
| Epic 目标含"用户体验/产品满意度"关键词 | 建议 Kano（用户感知导向） |

用户可通过参数指定方法（`decompose EPIC-xxx --moscow`），默认行为不变（Value x Effort），确保向后兼容。
