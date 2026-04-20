# Entity Schema 质量优化方案

> **日期**：2026-03-26
> **来源**：`docs/research/entity-schema-evaluation-2026-03-25.md`（评估报告）
> **性质**：结构性加固，非新功能。遵循 D11"深度优于广度"原则
> **状态**：已完成

---

## 执行摘要

评估报告原始识别 12 项改进（1 P0 + 5 P1 + 6 P2）。经逐项必要性分析后 **7 项执行、5 项取消**。取消的共同原因是"信息已有替代覆盖，新增为冗余"。

| 批次 | 原计划 | 实际 | 变更文件 | 提交 |
|------|:------:|:----:|:-------:|------|
| Batch 1 | 5 项 | 5 项执行 + 2 项调整 + 1 既有修复 | 8 文件 | `8049081` |
| Batch 2 | 3 项 | 全部取消 | — | — |
| Batch 3 | 4 项 | 2 项执行、2 项取消 | 1 文件 | `0e9649a` |

验证：631 passed / 0 failed / 0 lint errors / 20/20 eval / plugin 加载正常。

---

## Batch 1：结构补全 — ✅ 已完成

**提交**：`8049081` fix(knowledge): Entity Schema Batch 1 质量加固 + 引用修复

| # | 优先级 | 改进项 | 结果 | 说明 |
|---|:------:|--------|:----:|------|
| 1 | ~~P0~~ | ~~补充 4 个 schema 的 Consumers section~~ | **取消** | 分析结论：`_schema/README.md` 已是 Consumers SSOT，在 schema 中重复违反 IA-6。开发流程（product-architecture.md §0）已引导到 README |
| 2 | P2 | pf-format 标注风格对齐 | ✅ | `必填/否` → `核心/渐进`，对齐其余 6 个 schema |
| 3 | ~~P2~~ | ~~project-format Consumers 完善~~ | **调整** | 不扩充 project-format 的 Consumers（同 #1 理由），改为完善 README.md 消费者数据 |
| 4 | P2 | OBJ "已达成"阈值量化 | ✅ | "大部分 MoS 达成" → "客户价值和企业价值两个维度均有达成记录" |
| 5 | P2 | vision 北极星值类型约束 | ✅ | 当前值/目标值补充推荐格式：`数字 + 单位`（如 `1200 MAU`、`95%`） |
| 新 | — | README.md 消费者数据补全 | ✅ | br-format fan-in 1→2（+pace-biz）、pf-format fan-in 1→2（+pace-biz） |
| 新 | — | 反向清理 vision/obj 的 Consumers section | ✅ | 统一 SSOT：删除 schema 内 Consumers，README.md 为唯一权威源 |
| 新 | — | 既有问题修复：cr_07 引用断裂 | ✅ | 4 个 pace-biz procedures 的 `role-adaptations.md` 补全路径前缀 `knowledge/` |

### 关键决策：Consumers SSOT

**决策**：不在 schema 文件中维护 Consumers section，`_schema/README.md` 为唯一权威源。

**依据**：
- `_schema/README.md` 已维护 fan-in 和消费者列表
- `product-architecture.md §0` 合规检查已引导开发者查 README
- 在 schema 和 README 两处维护消费者违反 IA-6 单一权威
- 运行时 Claude 不消费 Consumers section，最终用户不阅读 schema 文件

---

## Batch 2：一致性治理 — ❌ 全部取消

| # | 优先级 | 改进项 | 结果 | 取消理由 |
|---|:------:|--------|:----:|---------|
| 6 | P1 | 跨实体状态映射表 | **取消** | 聚合规则始终锚定 CR 英文状态名（穿透引用），不经过中间层中文/emoji 状态。每层计算规则已显式写明，映射表是冗余文档 |
| 7 | P1 | 4 个 schema 渐进阶段定义 | **取消** | vision/obj 的渐进阶段表在 skills/ 中零运行时引用（"桩/成长/成熟"零命中）。Procedures 已明确"何时填什么"，阶段表是纯设计文档，不影响 Agent 行为 |
| 8 | P2 | project-format 字段标注表 | **取消** | project-format 是多 section 聚合容器（非单一实体），各 section 已有内联格式说明。统一字段表需把异构 section 强行拉平，语义不匹配 |

---

## Batch 3：复杂 Schema 加固 — 部分完成

**提交**：`0e9649a` fix(knowledge): cr-format 更新时机表 + 容错表——Schema 质量 Batch 3

| # | 优先级 | 改进项 | 结果 | 说明 |
|---|:------:|--------|:----:|------|
| 9 | P1 | cr-format 容错章节 | ✅ | 集中已有 7 条向后兼容规则 + 补充 4 条恢复场景（CR 丢失/状态不一致/意图缺失/事件表损坏），共 11 条 |
| 10 | P1 | cr-format 更新时机表 | ✅ | 从散落 ~10 处提取整合为 13 条结构化表格，覆盖 CR 全生命周期更新规则 |
| 11 | P1 | project-format 容错章节 | **取消** | project-format 的容错主要是"字段缺失→默认值"（~18 处），就近定义已清晰。与 cr-format 的"异常恢复"性质不同，集中化收益有限 |
| 12 | P2 | MoS 聚合路径形式化 | **取消** | 不同层 MoS 度量不同事物（BR=业务结果、Epic=专题价值、OBJ=战略达成），跨层聚合是人类判断非算法。design.md 承诺的"贡献分析"是 Skill 实现 Gap（pace-retro），不是 Schema Gap |

---

## 变更文件汇总

| 文件 | 批次 | 变更内容 |
|------|:----:|---------|
| `knowledge/_schema/entity/pf-format.md` | B1 | 字段表列名 `必填/否` → `核心/渐进` |
| `knowledge/_schema/entity/obj-format.md` | B1 | "已达成"阈值量化 + 删除 Consumers section |
| `knowledge/_schema/entity/vision-format.md` | B1 | 北极星值推荐格式 + 删除 Consumers section |
| `knowledge/_schema/README.md` | B1 | br/pf-format fan-in 补全（+pace-biz） |
| `skills/pace-biz/biz-procedures-decompose-br.md` | B1 | `role-adaptations.md` → `knowledge/role-adaptations.md` |
| `skills/pace-biz/biz-procedures-refine.md` | B1 | 同上 |
| `skills/pace-biz/biz-procedures-infer.md` | B1 | 同上 |
| `skills/pace-biz/biz-procedures-view.md` | B1 | 同上 |
| `knowledge/_schema/entity/cr-format.md` | B3 | 新增更新时机表（13 条）+ 容错表（11 条） |

## 参考文件

| 文件 | 用途 |
|------|------|
| `docs/research/entity-schema-evaluation-2026-03-25.md` | 评估报告（改进项来源） |
| `knowledge/_schema/entity/*.md` (8 个) | 优化对象 |
| `knowledge/_schema/README.md` | Consumers SSOT（Batch 1 决策） |
