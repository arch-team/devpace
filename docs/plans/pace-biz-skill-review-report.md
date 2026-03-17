# pace-biz Skill 深度评审报告

> 评审日期：2026-03-18 | 评审方法：skill-reviewer 三层分批 + devpace 专项

## 评审范围

- SKILL.md (177 行) + 10 个 procedures 文件 (1293 行)，共 1470 行
- 45 trigger evals + 18 behavioral evals

## 发现汇总

| 严重度 | 数量 | 本次修复 |
|--------|------|---------|
| Critical | 0 | — |
| Major | 10 | 8（M9/M2 暂缓） |
| Minor | 17 | 5（高价值项） |

---

## Major 问题

### M1: opportunity/epic 缺写入前确认步骤
- **来源**: L2a 创建型深审
- **文件**: `biz-procedures-opportunity.md`, `biz-procedures-epic.md`
- **问题**: SKILL.md §输出明确要求"写入操作前展示变更预览，用户确认后执行"，但 opportunity（Step 2→3 直接写入）和 epic（Step 5-7 三次写入无确认门）均跳过确认
- **decompose-epic/br 已正确实现**：Step 3.7/3.5 包含"用户确认/调整分解方案"
- **修复**: 在 opportunity Step 2-3 间、epic Step 4-5 间插入确认步骤

### M2: discover 中间持久化格式不完整 (暂缓)
- **来源**: L2b 发现型深审
- **文件**: `biz-procedures-discover.md`
- **问题**: Step 1 有 scope-discovery.md 模板，但 Step 2/3 的"追加到 scope-discovery.md"缺少格式模板。会话中断后恢复时 LLM 需推断阶段
- **暂缓原因**: 需要设计完整的多阶段持久化方案，与当前修复批次范围不一致

### M3-M7: 6 个 procedures 缺少实体格式 Schema 引用
- **来源**: L3 Schema 引用完整性检查
- **文件与缺失引用**:

| procedures | 操作实体 | 缺失 Schema |
|------------|---------|-------------|
| decompose-epic | 创建 BR | `_schema/entity/br-format.md` |
| decompose-br | 创建 PF | `_schema/entity/pf-format.md` |
| import | 创建 BR/PF | `_schema/entity/br-format.md`, `_schema/entity/pf-format.md` |
| infer | 创建 PF | `_schema/entity/pf-format.md` |
| refine | 修改 BR/PF | `_schema/entity/br-format.md`, `_schema/entity/pf-format.md` |

- **风险**: 无 Schema 引用时 LLM 可能生成不合规格式，与其他 Skill 产出不一致

### M8: align 缺 insights-format.md 引用 + 内联趋势格式
- **来源**: L3 + L2c
- **文件**: `biz-procedures-align.md`
- **问题**: Step 4 写入 insights.md 趋势数据但未引用 `_schema/auxiliary/insights-format.md`；趋势表格式内联定义（line 162），应委托给 Schema

### M9: SKILL.md 空参数引导混入实现细节 (暂缓)
- **来源**: L1 综合评审
- **文件**: `SKILL.md` lines 127-154
- **问题**: 空参数引导的阶段检测逻辑（Sense/Ideate/Structure/Refine/Validate/Ready）约 28 行实现细节内联在 SKILL.md 中，按 IA-3 稳定性原则应提取到 procedures
- **暂缓原因**: L1 分析指出当前放置有合理性（路由表标记为"内联智能引导"，且逻辑不被其他文件复用）。提取需新建 procedures 文件，变更较大

### M10: import 源类型矩阵内部矛盾
- **来源**: L2b 发现型深审
- **文件**: `biz-procedures-import.md`
- **问题**: 源类型矩阵 CSV/JSON 行的提取映射提到"PF/CR 候选"，但 Step 5 明确声明"不创建 CR — import 只丰富功能树（OPP/Epic/BR/PF 级别）"

---

## Minor 问题

| # | 问题 | 来源 | 文件 | 本次修复 |
|---|------|------|------|---------|
| m1 | description 544 字符超 300 预算 | L3+L1 | SKILL.md | 是 |
| m2 | 缺 trigger 词：OPP/decompose/align/view/全景图 | L1 | SKILL.md | 是 |
| m3 | 缺 /pace-init 排除条件 | L1 | SKILL.md | 是 |
| m4 | "执行路由表"非标准章节名 | L3 | SKILL.md | 否（L1 认为合规） |
| m5 | decompose-br 缺 PF 间依赖追踪 | L2a | decompose-br | 否 |
| m6 | decompose-br 缺 BR 状态不变说明 | L2a | decompose-br | 是 |
| m7 | decompose-br 缺"BR 无 Epic 关联"容错 | L2a | decompose-br | 是 |
| m8 | decompose 类 Step 0 升级提示不一致 | L2a | decompose-* | 否（各有理由） |
| m9 | import 无中间状态持久化 | L2b | import | 否 |
| m10 | import Step 0 insights "经验模式"悬空 | L2b | import | 否 |
| m11 | import REVIEW 分类未在输出模板体现 | L2b | import | 否 |
| m12 | discover 追问策略过于刚性 | L2b | discover | 否 |
| m13 | align "分析型（只读）"分类标签误导 | L2c | SKILL.md | 是 |
| m14 | view 统计区缺就绪度汇总行 | L2c | view | 否 |
| m15 | view 内联格式单行过密 | L2c | view | 否 |
| m16 | Eval 缺 lite mode 场景 | L3 | evals.json | 否 |
| m17 | 协同场景与推荐使用流程重叠 | L1 | SKILL.md | 否 |

---

## 修复计划

### 批次 1：产品层（skills/、knowledge/）

| 修复 | 文件 | 变更 |
|------|------|------|
| M1 | opportunity.md | 在 Step 2-3 间插入确认步骤 |
| M1 | epic.md | 在 Step 4-5 间插入确认步骤 |
| M3 | decompose-epic.md | 添加 br-format.md 引用 |
| M4 | decompose-br.md | 添加 pf-format.md 引用 + m6/m7 |
| M5 | import.md | 添加 br-format.md/pf-format.md 引用 + M10 修复 |
| M6 | infer.md | 添加 pf-format.md 引用 |
| M7 | refine.md | 添加 br-format.md/pf-format.md 引用 |
| M8 | align.md | 添加 insights-format.md 引用 + 趋势格式委托 |
| m1-m3 | SKILL.md | description 优化 + m13 分类标签 |

### 批次 2：开发层（tests/、docs/）
- 评审报告已写入（本文件）
- Eval 覆盖度记录（不在本次修复范围）

---

## 合规状态

| 检查项 | 状态 |
|--------|------|
| 跨 Skill procedures 引用 | ✅ 通过 |
| Schema 无反向引用 | ✅ 通过 |
| 分层完整性（无 docs/.claude/ 引用） | ✅ 通过 |
| knowledge 子目录隔离 | ✅ 通过 |
| _extraction 隔离 | ✅ 通过 |
| _signals 隔离 | ✅ 通过 |
| IA-5 SKILL.md 行数预算 | ✅ 177 < 500 |
| IA-5 单次加载预算 | ✅ max 375 < 800 |
