# 功能发现与 PF 溢出规程

> **职责**：CR 创建时的 PF 溢出检查和 merged 后的功能发现、PF 溢出检查规则。

## 功能发现（嵌入式触发，从 devpace-rules.md §11 迁入）

根据用户使用进度，在自然时机**直接执行**进阶功能的核心价值输出（而非推荐命令名称）。每条仅出现一次（使用 §15 教学标记去重）。

**"隐形 AI"原则**：用户感受到的是"devpace 自动帮我做了 X"，而非"devpace 教我用一个命令"。

| 条件 | 嵌入式行为（直接执行） | 标记值 |
|------|----------------------|--------|
| 第 3 个 CR merged | 直接输出迷你回顾——"3 个变更完成：Gate 一次通过率 N%，平均 M 个 checkpoint。" | `discover_retro` |
| 首次变更管理成功完成 | 直接输出影响摘要——"本次变更涉及 N 个模块，已同步更新关联状态。" | `discover_change` |
| 第 5 个 CR merged | 直接输出迭代进度——"已完成 N/M 个功能点，迭代完成率 X%。" | `discover_plan` |
| 首个 CR merged 且 releases/ 目录已存在 | 直接检查 Release 纳入——"此变更可纳入当前 Release。是否纳入？" | `discover_release` |
| 首个 defect/hotfix CR 创建 | 直接输出追溯——"追溯到引入点：[CR/commit]，影响范围：[模块]。" | `discover_feedback_report` |

**执行规则**：检查 state.md 教学标记 → 未出现过 → 在自然时机直接执行功能的核心价值输出 → 更新标记。用户如果问"怎么手动触发"，再说明对应命令名称。

## PF 溢出检查（Overflow Check）

CR 创建或状态变更（尤其是 merged）时，检查关联 PF 是否满足溢出条件，满足时自动创建独立文件。

### 检查时机

| 事件 | 检查行为 |
|------|---------|
| CR 创建（新关联 PF） | 计算该 PF 关联的 CR 数（含本次），≥3 则触发 |
| CR merged（§11 连锁更新时） | 综合检查三个条件 |
| `/pace-change modify` 涉及 PF | 由 change-procedures-types.md 负责检查并触发 |

### 溢出条件（满足任一）

溢出条件定义见 `knowledge/_schema/pf-format.md` "溢出触发条件"章节（功能规格 >15 行 | 关联 3+ CR | 经历 modify）。

### 溢出执行步骤

检测到溢出条件后，按 `knowledge/_schema/pf-format.md` 定义的步骤执行：

1. 创建 `.devpace/features/` 目录（如不存在）
2. 从 project.md 功能规格 section 提取该 PF 的验收标准、边界等内容
3. 从 project.md 价值功能树提取 BR/OBJ 关联和 CR 列表
4. 从 backlog/ CR 文件提取各 CR 状态和类型
5. 聚合信息创建 `features/PF-xxx.md`
6. 更新 project.md：
   - 功能规格 section 中移除该 PF 段落
   - 价值功能树中该 PF 行追加 `→ [详情](features/PF-xxx.md)`
7. 在执行透明摘要中报告溢出："PF-xxx 信息已迁移到独立文件 features/PF-xxx.md"

### 规则

- **零摩擦**：溢出自动发生，不询问用户确认（对齐 P1 原则）
- **幂等性**：已存在 `features/PF-xxx.md` 时不重复溢出，仅更新已有文件
- **向后兼容**：无 `features/` 目录的项目不触发任何溢出逻辑
- **容错**：溢出失败（如文件写入异常）不阻断主流程，在摘要中标注失败原因
