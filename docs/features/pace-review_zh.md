# 代码审查与质量门禁（`/pace-review`）

`/pace-review` 为处于 `in_review` 状态的变更请求（CR）生成结构化审查摘要。它将自动质量门禁检查（Gate 2）与对抗审查层和累积 Diff 报告相结合，然后移交给人类进行最终审批（Gate 3）。目标是以最低的认知负担，为审查者提供做出知情批准/拒绝决策所需的全部信息。

核心能力：复杂度自适应摘要深度（S 微型 / M 标准 / L-XL 含 TL;DR 的完整摘要）、reject-fix 周期的增量重审（Delta Review）、跨 CR 冲突检测、accept 报告引导的对抗聚焦、审查历史持久化，以及审批过程中的探索模式。

## 快速开始

```
1. CR 到达 in_review 状态（通过 /pace-dev）
2. /pace-review           → Gate 2 + 对抗审查 + 生成摘要
3. 人类审查摘要           → "approved" / 拒绝 / 具体反馈
4. approved → git merge → CR 转换为 merged
```

Gate 3（人类审批）在任何情况下都不可绕过（Iron Law IR-2）。

## 审查流程

### Step 1: 识别待审 CR

扫描 `.devpace/backlog/` 中处于 `in_review` 状态的 CR。可选的关键词参数用于缩小到特定 CR。如果没有符合条件的 CR，**状态感知引导**会介入：建议检查 `verifying` 状态的 CR 或推进 `developing` 状态的 CR——用户无需了解状态机知识。

### Step 1.5: 跨 CR 冲突检测

扫描所有活跃 CR（developing/verifying/in_review），检测与当前 CR 在文件和模块层面的重叠。仅在检测到重叠时显示——无冲突时零噪音。

### Step 2: Gate 2——自动质量检查

Gate 2 是人类审查前的最后一道自动门禁。它遵循**独立验证原则**：不信任 Gate 1 的任何结果——所有证据重新采集（重新读取验收标准、重新获取 git diff）。

**执行顺序（强制）**：

1. 从 CR 文件中重新读取验收标准
2. 获取最新的 `git diff main...<branch>`
3. 首先检查意图一致性——如果意图不匹配，Gate 2 立即失败（不再执行后续检查）

**意图一致性检查**将每条验收标准标记为：满足（pass）、未满足（fail + 缺少什么）、或部分满足（已完成与待完成的详细说明）。同时检测**范围外变更**和**范围内遗漏**。

**失败时**：CR 返回 `developing` 状态。Claude 修复差距、重新运行检查并重新提交——无需手动重启。

### Step 3: 对抗审查

Gate 2 通过后，思维模式从"验证正确性"切换为"发现缺陷"——这是对确认偏误的反制措施。

**核心规则**：零发现不可接受。如果所有维度都没有发现问题，至少输出一条可选优化建议作为下限。

**四个强制维度**（每个至少考虑一次）：

| 维度 | 示例 |
|------|------|
| 边界与错误路径 | 空输入、极端值、并发、超时 |
| 安全风险 | 注入、权限提升、敏感数据泄露 |
| 性能隐患 | N+1 查询、大量内存分配、阻塞操作 |
| 集成风险 | API 契约变更、向后兼容性 |

严重性标签：`🔴 建议修复` / `🟡 建议改进` / `🟢 可选优化`。每条发现都附带误报免责声明。

**Accept 报告集成**：当存在 `/pace-test accept` 报告时，覆盖薄弱和低置信度区域会引导对抗聚焦——在易受攻击的代码路径上检查更多维度。

**可配置维度**：项目可在 `checks.md` 中定义自定义对抗维度（如数据一致性、无障碍访问、向后兼容性）。未配置时使用默认的 4 个维度。

**关键规则**：对抗发现不会阻断 Gate 2——它们是提供给人类审查者的参考信息。简单 CR（复杂度 S）完全跳过对抗审查。

### Step 4: 累积 Diff 报告

对于中等及以上复杂度的 CR，生成按模块分组的 diff 报告，将每个变更文件映射到对应的验收标准：

```
累积 diff 报告：
  模块 A (+N/-M 行)：
    - file1.ts (新增)      → 验收标准 1
    - file2.ts (修改)       → 验收标准 2
  ⚠️ 未覆盖的标准：[列表]
  ⚠️ 范围外变更：[文件 + 理由]
```

这与 Gate 2 互补：Gate 2 检查"是否完成？"，diff 报告展示"如何完成？"。简单 CR 跳过此报告。

### Step 5: 审查摘要

摘要深度根据 CR 复杂度自适应调整（遵循 P2 渐进暴露 + P6 三层透明原则）：

| 复杂度 | 摘要级别 | 内容 |
|--------|---------|------|
| S | 微型（3-5 行） | 变更内容 + 质量状态 + 等待审批 |
| M | 标准 | 意图匹配（含推理后缀）+ 对抗审查 + 累积 diff |
| L/XL | 完整 + TL;DR | 前置 2-3 行执行摘要，后接完整详情 |

每条意图匹配判定附带不超过 15 字符的证据后缀（如 `RetryPolicy.ts:23 exponentialBackoff`）。用户可以追问"为什么？"来展开完整推理链。

**业务可追溯性**：自动追溯 CR → PF → BR 价值链。对不完整的追溯链如实标注，而非编造链接。

**审查历史**：摘要持久化到 CR 的验证证据章节（`### Review Summary (Round N, YYYY-MM-DD)`），支持会话恢复和增量重审基线。

详细规则见审查流程文件：[common](../../skills/pace-review/review-procedures-common.md)（始终加载）、[gate](../../skills/pace-review/review-procedures-gate.md)（M+ 审查）、[delta](../../skills/pace-review/review-procedures-delta.md)（增量审查）、[feedback](../../skills/pace-review/review-procedures-feedback.md)（决策后处理）。

### Step 6: 人类决定（Gate 3）

| 人类响应 | 动作 |
|---------|------|
| "approved" / "lgtm" | CR → `approved` → `git merge` → CR → `merged` → 级联更新 |
| 拒绝 + 原因 | CR → `developing`；原因记录在事件表中（scope / quality / design） |
| 具体反馈 | Claude 修改代码 → 重新运行受影响的检查 → 更新摘要 |
| 探索性问题 | 暂停审批，进入探索模式（CR 保持 `in_review`），做出决定后恢复 |

## 核心特性

### 反表演性意见处理

收到审查反馈时，Claude 遵循：**理解**真实意图（澄清歧义）→ **评估**与 CR 范围的对齐度 → **执行 + 验证**。禁止行为：回复"您说得对！"、接受违反 YAGNI 原则的建议、在理解意图之前修改代码。

### 独立验证原则

Gate 2 从零开始采集所有证据。不信任 Gate 1 的快照——上下文窗口会漂移，且代码可能在 `verifying` 阶段发生变更。这是一条硬性要求。

### 增量重审（Delta Review）

当 CR 存在近期的 reject-fix 历史时，`/pace-review` 仅针对被拒绝时涉及的维度进行检查，而非重新运行完整审查。未变更的验收标准标记为"与上一轮相同"。用户可通过"完整审查"或"重新审查全部"强制执行完整审查。

### 简化审批集成

满足所有快速通道条件的简单 CR（S 复杂度、Gate 1/2 一次通过、0% 偏移）由 `/pace-dev` 内联审批处理。当用户在简化审批中选择"让我看看"时，`/pace-review` 以 S 级微型摘要激活——对于已通过验证的 CR 无需完整审查。

### 结构化拒绝记录

当人类拒绝 CR 时，Claude 提示输入分类原因（最多一次追问）。类别：**scope**（验收差距或范围蔓延）、**quality**（代码或测试覆盖率）、**design**（架构或 API）。记录存储在 CR 事件表中，供 `/pace-learn` 提取模式。

## 使用场景

### 场景 1：标准审查流程

```
用户：  /pace-review
Claude：找到 CR-007（in_review）

        ## 为支付网关添加重试逻辑
        **变更内容**：src/payment/ 下 3 个文件，新增 RetryPolicy 类
        **意图匹配**：
          ✅ AC-1：指数退避 — 满足
          ✅ AC-2：最多重试 3 次 — 满足
        **对抗审查**（2 条发现）：
          🟡 maxDelay 缺少上限校验
          🟢 建议添加重试指标日志
        **质量**：✅ lint、types、tests | ⏳ 等待人类审批

用户：  approved
Claude：✅ CR-007 → approved → 已合并到 main
```

### 场景 2：审查中的反馈修改

```
用户：  /pace-review CR-012
Claude：[生成摘要]

用户：  parser.ts 的错误处理太宽泛了——请使用具体的 catch 块。

Claude：理解：按错误类型使用细粒度 catch 块。与 AC-2 对齐。
        修改 parser.ts ... 重新运行检查 ... ✅ 全部通过。
        更新摘要：✅ 所有标准满足 | ⏳ 等待人类审批

用户：  lgtm
Claude：✅ CR-012 → approved → 已合并到 main
```

### 场景 3：拒绝后的增量重审

```
用户：  错误处理太宽泛了——请使用具体的 catch 块。
Claude：理解。CR-012 → developing。原因：quality: 宽泛的错误处理。

        ...（修复完成，Gate 1/2 重新运行）...

用户：  /pace-review
Claude：找到 CR-012（in_review）—— 检测到之前的拒绝记录，执行增量重审。

        ## 改进 parser 的错误处理（Delta Review · 第 2 轮）
        **上次拒绝原因**：quality: 宽泛的错误处理
        **修复状态**：
          ✅ 针对 ParseError、ValidationError、IOError 使用具体 catch 块
        **未变更**：AC-1（通过）、AC-3（通过）—— 未重新检查
        **质量**：✅ 全部通过 | ⏳ 等待人类审批

用户：  lgtm
Claude：✅ CR-012 → approved → 已合并到 main
```

## 与其他 Skill 的集成

| Skill | 关系 |
|-------|------|
| `/pace-dev` | Gate 1 通过后将 CR 转换为 `in_review` 状态，移交给 `/pace-review` |
| `/pace-test` | 提供 `accept` 验证证据，在审查摘要中展示 |
| `/pace-change` | CR 状态转换（拒绝 → `developing`）遵循状态机 |
| `/pace-learn` | 结构化拒绝记录为模式提取提供数据，用于未来改进 |

## 相关资源

- [SKILL.md](../../skills/pace-review/SKILL.md) -- Skill 入口点和触发描述
- [review-procedures-common.md](../../skills/pace-review/review-procedures-common.md) -- 通用审查规则（始终加载）
- [review-procedures-gate.md](../../skills/pace-review/review-procedures-gate.md) -- M+ 审查流水线（意图、对抗、diff）
- [review-procedures-delta.md](../../skills/pace-review/review-procedures-delta.md) -- 增量审查流程
- [review-procedures-feedback.md](../../skills/pace-review/review-procedures-feedback.md) -- 决策后处理
- [设计文档](../design/design.md) -- 质量门禁定义和 CR 状态机
- [devpace-rules.md](../../rules/devpace-rules.md) -- 运行时行为规则
