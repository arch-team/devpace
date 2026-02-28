# 下一步导航核心规程

> **职责**：/pace-next 的信号采集策略、优先级决策算法、经验增强和角色适配规则。所有输出模式共享。
>
> 信号编号和分组定义见 `knowledge/signal-priority.md`（权威源）。

## 未初始化项目输出

当 `.devpace/state.md` 不存在时，直接输出：

```
💡 建议：初始化项目研发管理 → /pace-init
   原因：启用追踪后可获得上下文恢复、质量门禁、变更管理等能力
```

不做进一步信号采集，直接结束。

## Step 2：信号采集

**读取策略**：
- 使用 Glob 扫描 `backlog/*.md`、`releases/*.md`、`risks/*.md`，再用 Grep 提取状态字段
- 文件不存在或目录为空时，相关信号视为"未命中"
- 不全量读取文件内容，只提取决策所需字段
- 额外采集价值链上下文（CR→PF→BR 映射），用于建议模板

## Step 3：优先级决策

按 Blocking → In Progress → Delivery → Strategic → Growth → Idle 顺序遍历，取**首个命中**。

### 信号条件详述

以下补充 SKILL.md 信号摘要表中各信号的 pace-next 特有判断逻辑：

**S3 多 CR 并行选择**：当多个 developing CR 同时存在时，按以下维度排序取 top-1：
1. `state.md` "进行中"指向的 CR 优先（会话连续性）
2. checkpoint 计数较多的优先（接近完成）
3. 关联 PF 在 project.md 中优先级较高的优先
- detail 模式下，多个 developing CR 作为独立候选条目（每个 CR 一条，含 PF 上下文）

**S4 判断规则**：读取 paused CR 的暂停原因（事件表最后一条 paused 事件备注），判断阻塞是否已解除：
- 原因为等待某 CR → 检查该 CR 是否已 merged
- 原因为外部阻塞 → 无法自动判断，跳过此条
- 无法判断 → 跳过此条

**S7 时间判断**：读取 `current.md` 的周期字段（开始/结束日期），计算剩余天数。无日期字段时跳过。

**S9 日期判断**：读取 `dashboard.md` 首行或 blockquote 中的"最近更新"日期字段。字段缺失时跳过此条。

**S13 判断规则**：遍历 `project.md` 功能树中的 PF 行，如果 PF 下没有关联任何 CR（无 CR 缩进行），视为"未开始的功能"。

### 角色重排序

应用 `knowledge/signal-priority.md` 角色重排序规则。角色读取方式：从 `project.md` 的角色字段或当前会话推断。无法推断时默认 Dev。

### 与 session-start 去重

距 session-start < 5 分钟时（从 state.md 会话开始时间推算），pace-next 跳过已通知的最高信号，直接给出下一条命中的信号。避免用户刚看到 session-start 提醒后立即调用 pace-next 收到重复建议。

## Step 4：经验增强

如果 `.devpace/metrics/insights.md` 存在，按当前命中信号类型匹配经验 pattern：

| 命中信号 | 匹配策略 | 增强方式 |
|:-------:|---------|---------|
| S1（审批阻塞） | 匹配 review 相关 pattern（标签 `type: review`） | 附加"上次审批常见问题：[pattern 摘要]" |
| S3（继续开发） | 按 CR 类型或涉及模块匹配（标签 `type: developing`） | 附加"上次类似变更 [经验摘要]" |
| S5（Release 待验证） | 匹配部署相关 pattern（标签 `type: release`） | 附加"上次部署教训：[pattern 摘要]" |
| S8（迭代接近完成） | 匹配迭代相关 pattern（标签 `type: iteration`） | 附加"上次迭代经验：[pattern 摘要]" |
| S10（缺陷占比高） | 匹配防御型 pattern（标签 `type: defense`） | 附加具体改进建议 |
| S12（MoS 达成） | 匹配目标相关 pattern（标签 `type: objective`） | 附加"目标调整经验：[pattern 摘要]" |
| S13（功能未开始） | 匹配同类 PF 实施 pattern | 附加"同类功能实施经验：[pattern 摘要]" |
| 其他 | 匹配任何相关 pattern | 附加"经验参考：[pattern 摘要]" |

**规则**：
- 只读引用，不写入 insights.md
- 置信度 > 0.7 的 pattern 才引用；insights.md 中有结构化标签（`type: xxx`）时优先用标签匹配（haiku 高效），无标签时用关键词匹配
- 无匹配时不附加，保持简洁
- 增强内容 ≤ 1 行

## Step 5：角色适配

根据 §13 角色意识调整建议**措辞和信息维度**（分组内重排序由 Step 3 角色重排序执行）：

| 角色 | 措辞风格 | 信息维度 |
|------|---------|---------|
| Dev（默认） | 技术行动为主："继续实现 [功能]""修复 [问题]" | CR + PF 层（"[CR 标题]，属于 [PF 名]"） |
| PM | 功能交付为主："[功能] 交付进度需关注""迭代目标完成 N%" | PF + 迭代层（"[PF 名] 进度 N%，当前迭代目标 M 项功能"） |
| Biz | 业务目标为主："[MoS 指标] 接近达标""业务价值交付 N 项" | PF + BR + OBJ 层（"[PF 名] 支撑 [BR 名]，对齐 [OBJ 名]"） |
| Tester | 质量指标为主："N 个缺陷待修复""质量门通过率 N%" | CR + 质量维度（缺陷数、通过率） |
| Ops | 部署发布为主："[Release] 待验证""部署健康度需确认" | Release + 部署维度 |

角色读取方式：从 `project.md` 的 `preferred-role` 字段或当前会话推断。角色适配通用原则见 `skills/pace-role/role-procedures-dimensions.md`（权威源）。

## 输出约束

- 自然语言为主，不暴露 CR ID、状态机术语（遵循 §3）
- "操作"行引导到对应 Skill 或自然语言操作，不引导到具体子命令（如引导到 /pace-release 而非 /pace-release verify）
- 经验增强内容附加在"原因"行末尾，用"——"连接
- 价值链上下文嵌入建议行（不独立成行）：Dev 层附 PF | PM 层附 PF+迭代 | Biz 层附 BR+OBJ
