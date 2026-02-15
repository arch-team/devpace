# devpace 文档级联影响分析规程

> **职责**：上游文档变更时的影响分析与级联更新流程。`dev-workflow.md §8` 触发后，Claude 按需读取本文件。

## §0 速查卡片

```
权威链     → vision.md (WHY) → design.md (HOW) → requirements.md (WHAT) → roadmap.md (WHEN)
级联方向   → 只能沿权威链向下（上游 → 下游），不可反向
多文件变更 → 按权威链从上游到下游依次处理（vision → design → requirements）
vision 变  → 定位受影响 OBJ → 检查 design/requirements/roadmap → 更新或标记待审
design 变  → 定位受影响 Skill → 检查 requirements/已实现代码 → 更新或新增任务
reqs 变    → 定位受影响 F 条目 → 检查 roadmap 任务/已实现 Skill → 更新任务列表
自触发级联 → Claude 改上游文档后 → 直接评估下游影响 → 备注受影响任务 → 记入变更记录
反向反馈   → 实现中发现上游缺陷 → 报告用户 → 确认后修正上游 → 触发正向级联（不违反单向原则）
执行清单   → 识别范围 → 沿链追踪 → 逐文档评估更新 → 记入变更记录 → 备注进行中任务
陈旧标记   → <!-- REVIEW: [source] changed [date], may affect this section -->
```

## 权威链定义

```
vision.md (WHY) → design.md (HOW) → requirements.md (WHAT) → roadmap.md (WHEN)
```

变更只能沿此方向级联（上游 → 下游），不可反向。

**多文件同时变更**：当多个上游文件在同一时段被修改时，按权威链从上游到下游依次处理：先 vision.md → 再 design.md → 最后 requirements.md。上游文件的级联结果可能覆盖下游文件的独立变更，因此必须按此顺序，避免重复或矛盾的级联更新。

## 场景 A：vision.md 变更

**触发**：OBJ 增删改、北极星调整、护城河策略变化。

**影响分析**：

1. 识别受影响的 OBJ → 通过 roadmap.md "对应 OBJ" 定位受影响的 Phase
2. 检查 design.md 哪些章节基于该 OBJ 设计（参考 CLAUDE.md 权威文件索引）
3. 检查 requirements.md 哪些 S/F 条目源自该 OBJ
4. 评估 roadmap.md 当前任务是否受影响

**动作**：更新受影响的下游文档，或标记 `<!-- REVIEW: vision.md [OBJ-X] changed [date] -->`。

## 场景 B：design.md 变更

**触发**：UX 原则变化、状态机修改、工作流重设计、新增/删除章节。

**影响分析**：

1. 通过 design.md Skill 映射定位受影响的 Skill
2. 检查 requirements.md 哪些 F 条目基于变更的设计章节
3. 检查已实现的 Skill 是否需要适配
4. 评估 roadmap.md 是否需要新增任务

**动作**：更新 requirements.md 受影响条目 + 必要时新增 roadmap 任务。

## 场景 C：requirements.md 变更

**触发**：新增场景、验收标准修改、功能需求变更、优先级调整。

**影响分析**：

1. 识别受影响的 F 条目 → 定位对应的 roadmap 任务
2. 检查已实现的 Skill 是否需要返工
3. 评估是否需要新增 roadmap 任务

**动作**：更新 roadmap.md 任务列表 + 必要时调整里程碑。

## 场景 D：自触发级联（Claude 修改上游文档）

**触发**：当前任务本身要求修改 vision.md / design.md / requirements.md（如"更新 design.md 补充变更管理方案"）。由 `dev-workflow.md §3` 第 5 条触发。

**与场景 A/B/C 的区别**：
- 不需要"提示用户建议评估"——Claude 自己就是修改者，直接评估
- 变更内容已知——不需要 diff，直接从修改内容出发分析影响

**处理步骤**：

1. 完成上游文档修改并 git commit
2. 明确记录本次修改了什么（哪个文档、哪些章节、变更性质）
3. 根据修改的文档级别，按场景 A/B/C 对应的影响分析维度，评估对下游的影响
4. 检查 roadmap.md "当前任务"表中其他"进行中"或"待做"任务是否受影响
   - 受影响的任务：在"说明"列添加备注 `[design.md §X 已更新，需适配]`
   - 需要新增任务：立即添加到 roadmap（遵循 §5 关联条目填写要求）
5. 在 roadmap.md "变更记录"添加条目，原因列标注"自触发：任务 [任务名]"

## 级联执行清单（通用）

1. 识别变更范围（哪个文档、哪个章节/条目）
2. 沿权威链向下追踪影响
3. 对每个受影响的下游文档：读取、评估、更新或标记待审
4. 在 roadmap.md "变更记录"添加条目：`| 日期 | 变更描述 | 原因 |`
5. 若有进行中的任务受影响，在"说明"列添加备注

## 陈旧标记

使用 HTML 注释标记在下游文档的受影响位置：

```
<!-- REVIEW: [source] changed [date], may affect this section -->
```

解决后移除标记。

## 反向反馈协议

实现过程中发现上游文档有缺陷，不是"反向级联"，而是"修正上游 → 正向级联"的闭环。单向级联原则不被违反——下游实现永远不能直接改变上游的设计意图，只能报告问题、等待确认、修正上游后再正向级联。

**触发条件**（满足任一）：
- design.md 的设计规格在实现中发现不可行或有矛盾
- requirements.md 的验收标准存在歧义或无法按当前设计满足
- vision.md 的 OBJ/MoS 定义与实际实现不匹配

**处理流程**：见 `dev-workflow.md §3` 第 3 条。

**记录格式**：roadmap.md 变更记录中，原因列使用 `反向反馈：实现 [任务名] 时发现 [问题简述]`。

## 变更决策记录

所有级联处理的结果记入 roadmap.md "变更记录"表。

格式：`| 日期 | [源文档] 变更：[内容] → [下游影响] | [原因] |`
