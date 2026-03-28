# Schema 与 Procedure 职责分工规范

> **职责**：定义 `knowledge/_schema/` 与 `skills/*-procedures*.md` 之间的职责边界。创建或修改 Schema/Procedure 时查阅此文件。

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

## §3 边界情况

| 情况 | 判定 | 理由 |
|------|------|------|
| 命名规则 = 格式 + 生成算法 | Schema 保留格式（`CR-xxx 三位补零`），算法移到 Procedure | 格式是契约，算法是操作 |
| 容错 = 兼容性规则 + 恢复操作 | Schema 保留兼容性规则，恢复操作移到 Procedure/_guides/ | 兼容性是契约，恢复是操作 |
| 条件 section 存在性 | Schema 标注"可选——由 [Skill] 产出"，不含触发条件 | Schema 说"可能存在"，Procedure 说"什么时候创建" |
| 字段生命周期 | Schema 可标注精简三态（创建时/延迟填充/按需），详细时机表属 Procedure | 三态是契约预期，详细矩阵是操作指南 |

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

| 检查项 | 命令 | 期望 |
|--------|------|------|
| Schema 无操作性步骤 | `grep -rn "扫描.*目录\|从.*获取\|执行.*命令\|触发.*时" knowledge/_schema/ --include="*.md"` | 无匹配或仅限"字段含义说明"上下文 |
| Procedures 无内联格式 | `grep -rn "枚举\|合法值\|格式为" skills/ --include="*procedures*" \| grep -v "_schema/"` | 无匹配或仅限路径引用上下文 |
| 双源头检测 | 人工检查：Schema 中的"写入条件/更新时机"是否在某个 procedure 有重复定义 | 无重复 |

## §6 cr-format.md 现状评估

基于本规范对 cr-format.md 的检验结果（2026-03-27）：

### 合规项
- 字段定义、枚举值、格式约束、兼容性规则 ✅
- 消费者列表 ✅
- Procedures 全部使用路径引用 ✅

### 越界项（待重构）

| Section | 行号 | 越界内容 | 严重度 | 处理方向 |
|---------|------|---------|--------|---------|
| §更新时机 | 431-448 | 跨 Skill 写入矩阵 | 高 | 迁到 _guides/cr-lifecycle.md |
| §执行快照规则 | 379-385 | 值来源命令 + 更新时机 + 生成条件 | 高 | Schema 保留结构；操作性内容迁到 procedures |
| §风险预评估写入条件 | 405-408 | 触发条件（与 procedures 双源头） | 中 | 删除 Schema 侧，由 procedures 权威定义 |
| §运行时风险写入条件 | 426-429 | 触发条件和持久化操作 | 中 | 同上 |
| §容错前 2 条 | 449-454 | 恢复操作步骤 | 中 | 保留兼容性规则，恢复步骤迁到 _guides/ |
| §命名规则算法 | 312-313 | ID 生成算法 | 低 | Schema 保留格式约束，算法迁到 procedure |

### 其他优化项（非职责越界）

| 编号 | 问题 | 说明 |
|------|------|------|
| O1 | §0 类型枚举遗漏 tech-debt | §0 列 3 种，详细枚举有 4 种 |
| O2 | 缺"创建时最小结构" | 方案 B（删除 cr.md template）的前提 |
| O3 | 复杂度自适应规则分散 | 5 处各自定义复杂度行为，需统一映射表 |
| O4 | Epic 省略规则不明确 | §文件结构产品功能链缺"无 Epic 时省略"标注 |
| O5 | §文件结构缺事件表格式 | 缺少列名和时间戳格式示例 |
| O7 | 缺"创建算法" | 作为生成源需明确步骤（属 procedure 职责，应放在对应 procedure 而非 Schema 中） |
