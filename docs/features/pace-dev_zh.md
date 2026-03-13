# 开发工作流（`/pace-dev`）

`/pace-dev` 是 devpace 的核心开发 Skill。它驱动变更请求（CR）走完完整生命周期——从意图澄清到代码实现再到质量门禁——在一个自主工作流中完成。Claude 进入"推进模式"，编写代码、运行测试、遇到失败时自修正，并在每个有意义的步骤进行 commit。该 Skill 根据变更的复杂度自适应调整严格程度：单文件拼写修复走最小化流程，多模块功能则生成完整的执行计划并征求用户确认。

## 快速开始

```
1. /pace-dev "add user login"   --> 定位或创建 CR，澄清意图，开始编码
2. (Claude 自主工作)             --> 实现、测试、提交，运行 Gate 1 和 Gate 2
3. "LGTM"                       --> 人工审批（Gate 3）--> CR 合并
```

发出初始命令后，Claude 自主驱动工作流，无需额外 prompt，直到需要你做决策或到达人工审批门禁。

## CR 生命周期概览

每项变更都经历六状态生命周期。`/pace-dev` 自动管理状态转换；你只需在 Gate 3（人工审批）介入。

```
created --> developing --> verifying --> in_review --> approved --> merged
   |            |              |             |            |          |
   |  意图      |  代码 &      |  Gate 1     |  Gate 2    | Gate 3   | 合并后
   |  检查点    |  测试        |  (代码      |  (需求     | (人工)   | 更新
   |            |              |   质量)     |   质量)    |          |
```

| 状态 | 发生什么 | 谁执行 |
|------|---------|--------|
| `created` | CR 已创建，包含标题和意图；完成复杂度评估 | Claude |
| `developing` | 代码实现、测试编写、每步 git commit | Claude |
| `verifying` | Gate 1——自动化代码质量检查；失败时自修正 | Claude |
| `in_review` | Gate 2——与验收标准对比；生成审查摘要 | Claude |
| `approved` | Gate 3——人工审查 diff 摘要并批准 | 你 |
| `merged` | 分支合并，state.md 更新，关联 PF 刷新 | Claude |

## 核心特性

### 意图检查点

CR 首次进入 `developing` 时，Claude 执行一个自准备步骤来锁定范围和验收标准。这不是需要你填写的表单——Claude 在内部完成并告知你"范围已确认，开始工作"。

- **简单（S）**：记录你的原始请求及一条自由文本验收条件。
- **标准（M）**：增加编号验收标准列表，用 `[TBD]` 标签标注歧义项。
- **复杂（L/XL）**：生成完整的 Given/When/Then 验收标准、执行计划，并向你提最多 2 个澄清问题（每个附带推荐答案）。

如果你问"计划是什么？"，Claude 会展示完整的意图部分，包括执行计划。

### 复杂度评估

Claude 从四个维度评估每个 CR 并分配大小：S、M、L 或 XL。

| 维度 | S | M | L | XL |
|------|---|---|---|-----|
| 涉及文件数 | 1-3 | 4-7 | 8-15 | >15 |
| 涉及目录数 | 1 | 2-3 | 4-5 | >5 |
| 验收标准数 | 1 | 2-3 | 4+ | 多组 |
| 跨模块依赖 | 无 | 单向 | 双向 | 架构级 |

最高维度决定最终评级。L/XL 级 CR 自动进入拆分评估流程，Claude 会建议将工作拆成更小的 CR。

### 自适应路径

复杂度决定工作流的仪式化程度：

| 路径 | 复杂度 | 行为 |
|------|--------|------|
| **Quick** | S，单文件 | 最小意图记录，无执行计划，直接编码 |
| **Standard** | S 多文件，M | 标准意图 + 编号标准；可选执行计划 |
| **Full** | L，XL | 完整意图 + 强制执行计划 + 计划反思 + 编码前用户确认门禁 |

**升级守卫**在意图检查点期间监视范围蔓延。如果一个 S 级 CR 实际涉及多个模块，Claude 会建议升级到 M 或 L。该建议不会阻断流程——你可以选择继续使用原级别。

### 执行计划（L/XL）

对于复杂变更，Claude 在编写任何代码之前生成分步计划：

- 每步是一个原子操作，对应一次有意义的 commit。
- 步骤包含确切的文件路径、要执行的操作和可验证的预期结果。
- 步骤间的依赖关系被显式标注。
- 当测试策略存在时，测试骨架步骤排在实现步骤之前。

生成计划后，Claude 从四个维度执行**计划反思**（需求覆盖度、过度工程风险、拆分必要性、技术假设），记录 1-3 行观察。然后将计划呈现给你确认后再开始编码。

### 门禁反思

每个质量门通过后，Claude 在 CR 事件日志中追加简短的自评：

- **Gate 1 反思**：技术债观察、测试覆盖评估、测试先行遵从度审查。
- **Gate 2 反思**：边界场景覆盖和验收完整度观察。

这些反思不会阻断工作流。它们积累质量信号，在 CR 合并时馈入经验提取。

### 漂移检测

两个互补的监控在每个检查点（git commit + CR 更新）运行：

- **意图漂移**：将变更文件与声明的范围对比。如果超过 30% 的文件落在意图边界之外，Claude 会标记："这些文件超出声明范围——是有意扩展还是范围蔓延？"
- **复杂度漂移**：将实际文件/目录数量与初始复杂度阈值对比。如果一个 S 级 CR 已触及 4+ 个文件，Claude 会建议升级。每个 CR 最多标记一次。

两种检测均为建议性质——它们不会阻断你的工作流。

### PF 溢出检查

当 CR 被创建或合并时，Claude 检查关联的产品功能（PF）是否已超出 `project.md` 中的内联容量：

- **触发条件**：功能规格超过 15 行、3+ 个关联 CR，或之前对该 PF 执行过 `/pace-change modify`。
- **动作**：自动将 PF 提取为 `.devpace/features/PF-xxx.md` 下的独立文件，并在 `project.md` 中更新为链接。
- **零摩擦**：无需确认。提取会在执行摘要中报告。

### 快速 CR 切换

有多个进行中的 CR？快速切换：

- `/pace-dev #3`——按编号直接跳转到 CR-003。
- `/pace-dev --last`——恢复最近工作过的 CR。
- `/pace-dev "login"`——按关键词匹配（已有行为）。

### 简化审批

简化审批路径（跳过 `in_review` 等待）现在区分外观性修复和结构性修复：

- **外观性修复**（lint、格式化、import 排序）不计为"非首次通过"。这意味着更多 S 级 CR 有资格走简化审批。
- **结构性修复**（逻辑错误、类型错误、缺少 return）仍然取消简化审批资格。
- **批量审批**：当 2+ 个 CR 同时处于 `in_review` 且均符合简化审批条件时，Claude 提供批量确认提示。

### L/XL 步级进度

对于有执行计划的 L/XL 级 CR，每完成一步会产出：

1. CR 事件日志中的步骤检查点标记（`[checkpoint: step-3-done]`）。
2. state.md 中的步级定位器（`→ Step 3/5: middleware implementation`）。
3. 给用户的一行进度通知：`[Step 3/5] middleware implementation complete`。

这实现了精确的跨会话恢复——下次会话从准确的步骤处继续。

### 执行计划编辑

在 L/XL 级 CR 的确认门禁期间，你可以用自然语言调整计划：

- "删除步骤 3" / "合并步骤 4 和 5" / "在步骤 2 后添加一步：..." / "交换步骤 3 和 4"
- Claude 应用变更并重新呈现更新后的计划供确认。
- 你还可以设置**暂停点**："在步骤 3 后暂停"——Claude 会在那里停下并输出进度摘要，等待确认后再继续。

### 探索到推进的上下文继承

在同一会话中从探索模式切换到推进模式时，Claude 自动从先前讨论中提取相关上下文：

- 方案选择及其理由
- 发现的约束和依赖
- 探索中达成的结论

该上下文会带来源标注预填到 CR 意图部分，无需重新解释已做出的决策。

### 开发中压缩建议

对于已完成执行计划 60% 以上的 L/XL 级 CR，当当前步骤与之前步骤无关时，Claude 可能建议 `/compact`——为剩余工作释放上下文空间。

### 推进中内联探索

如果你在实现过程中需要思考或讨论替代方案（"让我想想..." / "有没有更好的方法？"），Claude 暂停推进工作流进行自由讨论，然后在你说"继续"时无缝恢复。讨论成果自动更新到 CR 意图中。

## 使用场景

### 场景 1：快速修复 Bug

```
你：    /pace-dev "fix null check in auth middleware"
Claude: 未找到现有 CR。创建 CR-012（类型: defect，严重度: medium）。
        范围已确认，开始工作。

        ...（实现修复、添加测试、提交）...

        变更摘要
        - 文件: 修改 1 / 新增 1
        - CR 状态: created --> developing --> verifying --> in_review
        - Gate 1: 通过。Gate 2: 通过。
        准备好供你审查。批准合并？
```

### 场景 2：多模块功能（L）

```
你：    /pace-dev "add role-based access control"
Claude: CR-013 已创建。复杂度: L（8 文件、4 目录、双向依赖）。
        建议拆分为 2 个 CR：
        - CR-013a: 角色模型 + 权限中间件
        - CR-013b: 角色分配的管理界面
        依赖关系: CR-013a 先于 CR-013b。
        拆分还是作为一个 CR 继续？

你：    拆分。
Claude: 已创建 CR-013a 和 CR-013b。开始 CR-013a。
        以下是执行计划（5 步）：
        1. 在 models/role.ts 中定义 Role schema ...
        ...
        确认开始，还是调整？

你：    开始吧。
Claude: ...（自主实现，带检查点）...
```

### 场景 3：恢复中断的工作

```
你：    /pace-dev
Claude: 恢复 CR-010（状态: developing，执行计划步骤 3/5）。
        上次检查点: "已完成 API 路由，下一步: 编写集成测试。"
        从步骤 4 继续。
```

## 与其他命令的集成

| 命令 | 与 `/pace-dev` 的关系 |
|------|----------------------|
| `/pace-init` | 初始化 `/pace-dev` 运行所在的 `.devpace/` 项目结构 |
| `/pace-review` | CR 到达 `in_review` 时自动调用；生成 Gate 2 的 diff 摘要 |
| `/pace-test` | 开发期间可调用，生成与验收标准对齐的测试骨架 |
| `/pace-change` | 处理需求变更（增删改 PF）；`/pace-dev` 负责实现 |
| `/pace-sync` | CR 状态转换后，sync-push hook 提醒你推送状态到 GitHub |
| `/pace-status` | 随时查看当前 CR 状态和项目进度 |
| `/pace-guard` | 在 L/XL 级 CR 的意图检查点期间调用风险预扫描 |
| `/pace-next` | CR 合并后或无进行中工作时建议下一步操作 |

## 相关资源

- [dev-procedures-common.md](../../skills/pace-dev/dev-procedures-common.md) -- 通用规则（context.md 生成、同步建议、决策日志、透明度摘要）
- [dev-procedures-intent.md](../../skills/pace-dev/dev-procedures-intent.md) -- 意图检查点、复杂度评估、执行计划、方案确认
- [dev-procedures-developing.md](../../skills/pace-dev/dev-procedures-developing.md) -- 步骤隔离、漂移检测、L/XL 检查点
- [dev-procedures-gate.md](../../skills/pace-dev/dev-procedures-gate.md) -- Gate 1/2 通过后反思
- [dev-procedures-postmerge.md](../../skills/pace-dev/dev-procedures-postmerge.md) -- 功能发现、PF 溢出检查
- [dev-procedures-defect.md](../../skills/pace-dev/dev-procedures-defect.md) -- 缺陷/热修复 CR 创建及修复后处理
- [cr-format.md](../../knowledge/_schema/cr-format.md) -- CR 文件 schema（字段、状态、事件日志格式）
- [devpace-rules.md](../../rules/devpace-rules.md) -- 运行时行为规则（推进模式约束、双模式系统）
- [用户指南](../user-guide.md) -- 所有命令快速参考
