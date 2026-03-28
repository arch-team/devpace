# Schema 与 Procedure 职责分工规范

> **职责**：定义 `knowledge/_schema/` 与 `skills/*-procedures*.md` 之间的职责边界。创建或修改 Schema/Procedure 时查阅此文件。本文件是 `product-architecture.md` §2 "Schema 契约协作"和"禁止模式"的详细展开，详则以本文件为权威。

## §0 速查卡片

```
Schema（_schema/）= WHAT — 记录长什么样（结构 + 约束 + 校验）
Procedure（*-procedures*.md）= HOW — 如何生成/操作记录（步骤 + 值来源 + 条件逻辑）
Rules（rules/）= WHEN — 什么时机触发什么行为（触发条件 + 行为规则）
```

**职责判定口诀**：
- "这个字段叫什么、能填什么" → Schema
- "这个值从哪来、怎么填" → Procedure
- "什么时候该填" → Rules 或 Procedure

## §1 Schema 应包含的内容

| 类别 | 示例 | 判定依据 |
|------|------|---------|
| 字段定义 | 字段名、类型、位置、含义 | "这个字段叫什么，在文件的哪个位置" |
| 枚举值 | status: created/developing/... | "这个字段能填什么" |
| 格式约束 | 时间戳格式 YYYY-MM-DDTHH:MM | "值长什么样" |
| 必填/可选标注 | 复杂度：可选 | "是否必须存在" |
| 条件必填约束 | 严重度：仅 defect/hotfix 必填 | "什么条件下必须存在" |
| 字段间依赖 | 阻塞字段引用合法 CR-ID | "字段之间的关系" |
| 最小有效结构 | 最小可用 CR 仅需元信息 | "少到什么程度仍合法" |
| 向后兼容规则 | 无 type 字段视为 feature | "旧格式如何处理" |
| 消费者列表 | pace-dev, pace-change, ... | "谁会读写这个 Schema" |
| 创建时最小结构 | 创建时必填/默认/跳过字段分类 | "刚创建时长什么样"（方案 B 要求） |

## §2 Schema 不应包含的内容

| 类别 | 示例 | 应放在 | 判定依据 |
|------|------|--------|---------|
| 生成算法 | "扫描 backlog/ 最大编号 +1" | Procedure | "如何获取下一个值" |
| 值来源命令 | "从 git diff --stat 获取" | Procedure | "值从哪个命令来" |
| 写入时机矩阵 | "Gate 1 通过时更新 checkbox" | Procedure 或 _guides/ | "谁在什么时候写" |
| 触发条件 | "L/XL 进入 developing 前触发" | Procedure | "什么情况下执行" |
| 恢复操作步骤 | "从 project.md 重建最小 CR" | Procedure 或 _guides/ | "怎么修复" |
| 跨实体协调 | "同步更新 project.md 树视图" | Procedure | "改了 A 还要改 B" |

## §2.5 Procedure 与 _guides/ 的分工

§2 中部分内容标注"应放在 Procedure 或 _guides/"——判定标准如下：

| 判定条件 | 放在 | 理由 |
|---------|------|------|
| 操作步骤仅被一个 Skill 使用 | 该 Skill 的 `*-procedures*.md` | Skill 私有逻辑，随 Skill 演进 |
| 操作步骤被 2+ Skill 共享 | `knowledge/_guides/` | 共享步骤提取为公共指南，各 Skill 引用（product-architecture.md §3 通信模式） |
| 完整生命周期横切多 Skill | `knowledge/_guides/` | 如"CR 从 created 到 merged 各阶段谁做什么"——跨 Skill 的全景视图 |
| 最佳实践/经验指导 | `knowledge/_guides/` | 教学性内容，非强制步骤 |

**速记**：一个 Skill 用 → Procedure；多个 Skill 用 → _guides/。

## §3 边界情况

| 情况 | 判定 | 理由 |
|------|------|------|
| 命名规则 = 格式 + 生成算法 | Schema 保留格式（`CR-xxx 三位补零`），算法移到 Procedure | 格式是契约，算法是操作 |
| 容错 = 兼容性规则 + 恢复操作 | Schema 保留兼容性规则，恢复操作移到 Procedure/_guides/ | 兼容性是契约，恢复是操作 |
| 条件 section 存在性 | Schema 标注"可选——由 [Skill] 产出"，不含触发条件 | Schema 说"可能存在"，Procedure 说"什么时候创建" |
| 字段生命周期 | Schema 可标注精简三态（创建时/延迟填充/按需），详细时机表属 Procedure | 三态是契约预期，详细矩阵是操作指南 |
| 默认值 | Schema 标注默认值（`status: created（默认）`），Procedure 负责填充逻辑 | 默认值是契约（"不填时视为 X"），填充动作是操作 |
| 校验规则 | Schema 定义合法转换（`created→developing 合法`），Hook 独立实现校验逻辑 | Schema 是声明式约束，Hook 是运行时执行——Hook 不引用 Schema（§0 矩阵） |

## §4 Procedure 引用 Schema 的正确方式

```markdown
-- 正确：路径引用 --
"CR 文件格式遵循 knowledge/_schema/entity/cr-format.md"
"验收条件格式见 cr-format.md §验收条件格式"

-- 错误：内联复制 --
"验收条件：S=自由文本、M=编号清单、L/XL=Given/When/Then"
（这些值已在 cr-format.md 中定义，procedures 不应重复）

-- 可接受的操作性引用 --
"根据 cr-format.md §复杂度 评估 CR 复杂度，然后按对应格式填充验收条件"
（引用 Schema 作为决策依据，步骤逻辑由 procedure 定义）
```

**预防合理化**：`"在 procedures 中写一遍格式方便 Claude 执行" → 内联即双源头。Schema 变更时 procedures 必然失同步。路径引用 + 精确 section 指针（§验收条件格式）足够 Claude 定位`

## §5 检测命令

| 检查项 | 命令 | 期望 | 说明 |
|--------|------|------|------|
| Schema 无操作性步骤 | `grep -rn "扫描.*目录\|从.*获取\|执行.*命令\|触发.*时" knowledge/_schema/ --include="*.md" \| grep -v "含义\|说明\|描述\|向后兼容"` | 空 | 排除字段含义说明上下文，减少假阳性 |
| Procedures 无内联格式 | `grep -rn "枚举\|合法值\|格式为" skills/ --include="*procedures*" \| grep -v "_schema/\|format\.md\|见.*§"` | 空 | 排除路径引用和 section 指针 |
| 双源头检测 | 人工检查：Schema 中的"写入条件/更新时机"是否在某个 procedure 有重复定义 | 无重复 | 自动化困难，保持人工审查 |

## §6 审计记录索引

基于本规范对具体 Schema 文件的审计结果，按时间归档在 `docs/research/`：

| 文件 | 审计报告 | 日期 |
|------|---------|------|
| cr-format.md | `docs/research/cr-format-audit-2026-03-27.md` | 2026-03-27 |
