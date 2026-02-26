# 迭代规划（`/pace-plan`）

`/pace-plan` 是 devpace 的迭代规划 Skill。它管理迭代的完整生命周期——从关闭当前迭代到规划下一个迭代——补齐产品闭环中的"规划→执行→回顾"循环。与处理产品功能（PF）级需求变更的 `/pace-change` 不同，`/pace-plan` 在迭代范围层级操作，决定每个迭代纳入哪些 PF 并管理容量约束。

## 快速上手

```
1. /pace-plan              --> 评估当前迭代状态,建议下一步操作
2. /pace-plan next         --> 规划新迭代(含 Plan Proposal)
3. /pace-plan close        --> 关闭当前迭代(自动回顾)
4. /pace-plan adjust       --> 迭代中途范围调整
5. /pace-plan health       --> 展示迭代健康度指标
```

## 子命令

| 子命令 | 使用场景 | 功能 |
|--------|---------|------|
| `(空)` | 检查迭代状态 | 评估完成率并建议下一步(关闭或继续) |
| `next` | 启动新迭代 | 规划下个迭代,含引导流程和 Plan Proposal |
| `close` | 结束当前迭代 | 关闭迭代,自动轻量回顾并归档 |
| `adjust` | 迭代中途 | 增删 PF 或调整当前迭代优先级 |
| `health` | 监控进展 | 展示健康度指标(完成率 vs 时间,范围稳定性) |

## 核心特性

### 空功能树引导式规划

当 `project.md` 无活跃或待做 PF 时，`/pace-plan next` 进入引导规划模式——询问用户用 1-2 句话描述迭代目标，从描述推断 PF 并填充 `project.md`（附溯源标记）。消除冷启动问题。

### Plan Proposal（智能规划建议）

Claude 自动生成完整的迭代规划建议方案，包含目标归纳、基于优先级的 PF 选择（延后 PF 优先→依赖已满足→project.md 排序）、工作量估算和容量评估。用户用自然语言确认或调整。详细生成逻辑和格式见 [plan-procedures.md](../../skills/pace-plan/plan-procedures.md) Step 3.7。

### 估算（启发式与历史数据）

估算根据可用数据自适应：有 `dashboard.md` 历史数据时使用实际速度和 CR 周期（指标定义见 `knowledge/metrics.md`）；无历史数据时回退到基于验收标准数量的 S/M/L 启发式分级。首次迭代默认 3-5 个 PF 容量上限。详细规则见 [plan-procedures.md](../../skills/pace-plan/plan-procedures.md) Step 3.3。

### 规划增强

- **BR 分组**：候选 PF ≥5 个时按父级业务需求分组，降低认知负荷。
- **依赖校验**：检查 PF 依赖字段，未满足前置条件时提醒。
- **风险集成**：`.devpace/risks/` 存在时展示高/中风险标记，高风险 PF 估算增加 30% buffer。
- **回顾建议直联**：展示上一迭代的"下迭代建议"，闭合反馈循环。

### 关闭时自动轻量回顾

`/pace-plan close` 将 `current.md` 归档为 `iter-N.md`，自动采集 3 项基线指标（PF 完成率、平均 CR 周期、迭代速度——定义见 `knowledge/metrics.md`）并更新 `dashboard.md`。完整回顾通过 `/pace-retro` 仍为可选。详细流程见 [close-procedures.md](../../skills/pace-plan/close-procedures.md)。

### 迭代中途范围调整（adjust）

在当前迭代中增删 PF 或调整优先级，每次操作后重算容量。与 `/pace-change` 的边界：change 管 PF 级需求变更，adjust 管迭代范围。详细流程见 [adjust-procedures.md](../../skills/pace-plan/adjust-procedures.md)。

### 迭代健康度指标（health）

展示完成率 vs 时间进度、范围变更次数、PF 状态分布和速度趋势。评估为正常/有风险/范围不稳定，与 pulse 信号检测集成。详细流程见 [health-procedures.md](../../skills/pace-plan/health-procedures.md)。

## 使用场景

### 场景 1：首次迭代规划（空功能树）

```
你：    /pace-plan next
Claude：未找到活跃或待做 PF。让我们从你的目标开始。
        这个迭代想做什么？用 1-2 句话描述目标。

你：    构建用户认证,包括登录和注册
Claude：基于你的描述,我推断了以下功能：
        - PF-001：邮箱密码登录
        - PF-002：邮箱验证注册
        - PF-003：密码重置流程
        确认还是需要调整？

你：    看起来不错
Claude：PF 已添加到 project.md。

        建议方案：
          目标：完成用户认证功能
          纳入 PF（共 3 个）：
            [P0] PF-001 用户登录 — 预估 M（2-4 CR）
            [P0] PF-002 用户注册 — 预估 M（2-4 CR）
            [P1] PF-003 密码重置 — 预估 S（1-2 CR）
          总预估工作量：约 7-10 会话
          周期：[接下来 2 周,如已指定]

        确认这个方案？

你：    好
Claude：迭代已规划并保存到 .devpace/iterations/current.md。
        最高优先级：PF-001 用户登录。现在就开始？

你：    开始吧
Claude：建议运行：/pace-dev "实现 PF-001"
```

### 场景 2：基于历史数据规划

```
你：    /pace-plan next
Claude：上一迭代完成 4/5 个 PF（80% 速度）。
        2 个 PF 从上迭代延后。
        上迭代回顾建议："聚焦小型 PF 以提高完成率"。

        建议方案：
          目标：完成延后功能 + 结算流程
          纳入 PF（共 4 个）：
            [P0] PF-005 用户资料(延后) — 预估：2.5 会话(历史均值)
            [P0] PF-008 邮件通知(延后) — 预估：1.8 会话
            [P1] PF-012 购物车 — 预估：3.2 会话
            [P2] PF-014 支付集成 — 预估：4.5 会话 ⚠️ 高风险(+30%)
          总计：~12 会话 vs 容量 15 会话

        确认还是调整？

你：    去掉 PF-014,风险太高
Claude：已调整。移除 PF-014。

        更新方案：
          纳入 PF（共 3 个）：
            [P0] PF-005 用户资料 — 2.5 会话
            [P0] PF-008 邮件通知 — 1.8 会话
            [P1] PF-012 购物车 — 3.2 会话
          总计：~7.5 会话(远低于容量)

        确认？

你：    好
Claude：迭代已保存。从 PF-005 开始？
```

### 场景 3：迭代中途调整

```
你：    /pace-plan adjust
Claude：当前迭代状态：
          目标：完成用户认证
          进度：2/4 个 PF 完成（50%）
          剩余：PF-003(进行中), PF-004(待做)
          容量：已用约 5 会话,剩余约 3 会话

        需要什么调整？

你：    去掉 PF-004,换成 PF-007
Claude：检查容量...
        - 移除 PF-004 释放 ~2 会话
        - 增加 PF-007 需要 ~3 会话
        - 新总计：剩余约 6 会话

        调整可行。确认？

你：    确认
Claude：已更新 current.md。
        变更记录："迭代中途调整：PF-004 → PF-007(优先级调整)"
```

### 场景 4：迭代健康检查

```
你：    /pace-plan health
Claude：迭代健康度报告：
          时间进度：60%（10 天迭代中已过 6 天）
          PF 完成率：40%（5 个中完成 2 个）
          状态分布：✅2 🔄1 ⏳2
          范围变更：0 次(稳定)

        ⚠️ 有风险：完成率(40%)落后于时间进度(60%)。
        需要 1.5 倍当前速度才能按时完成。

        建议：
        1. 运行 /pace-plan adjust 缩减范围
        2. 检查进行中的 CR 是否受阻
        3. 考虑延长迭代周期
```

### 场景 5：迭代关闭

```
你：    /pace-plan close
Claude：正在关闭当前迭代...

        最终状态：
          计划：5 个 PF
          完成：4 个 PF（80%）
          延后：1 个 PF（PF-015）

        自动回顾指标：
          - PF 完成率：80%
          - 平均 CR 周期：2.3 天
          - 迭代速度：0.8

        指标已更新到 dashboard.md。
        迭代已归档到 iter-03.md。

        建议运行 /pace-retro 做完整回顾分析。

        准备好规划下一个迭代了吗？
```

## 与其他命令的集成

| 命令 | 与 `/pace-plan` 的关系 |
|------|----------------------|
| `/pace-init` | 初始化迭代运行所在的 `.devpace/` 结构 |
| `/pace-change` | 处理 PF 级需求变更；容量超出时可能触发 `/pace-plan adjust` 建议 |
| `/pace-dev` | 执行阶段；`/pace-plan` 规划后引导到 `/pace-dev` |
| `/pace-retro` | 完整回顾；`/pace-plan close` 执行轻量自动回顾，建议 `/pace-retro` 深度分析 |
| `/pace-status` | 展示当前迭代进度及整体项目状态 |
| `/pace-guard` | 风险扫描集成到规划；高风险 PF 获得估算 buffer |
| `/pace-pulse` | 健康度指标反馈 pulse 信号；低健康度触发 pulse 检测 |
| `/pace-next` | 迭代结束或无活跃工作时可能建议 `/pace-plan next` |

## 降级行为

当某些数据缺失时，`/pace-plan` 优雅降级：

| 缺失数据 | 降级处理 |
|---------|---------|
| `project.md` 空 | 引导规划模式：获取用户目标→推断 PF→填充功能树 |
| 无历史数据 | 启发式估算（基于验收标准数量 S/M/L 分级） |
| 无迭代周期 | 容量检查跳过时间基准警告，仅展示 PF 数量限制 |
| 无 `dashboard.md` | 跳过速度基准限制，用启发式上限（首次迭代 3-5 个 PF） |
| 无上迭代回顾 | 跳过建议展示，继续正常规划 |
| 无 `.devpace/risks/` | 跳过风险集成，无高风险标记 |
| `current.md` 空 | `/pace-plan adjust` / `health` 提示"无活跃迭代，请先运行 `/pace-plan next`" |

## 相关资源

- [plan-procedures.md](../../skills/pace-plan/plan-procedures.md) -- Step 3+4：新迭代规划（候选 PF、估算、Plan Proposal、文件生成）
- [close-procedures.md](../../skills/pace-plan/close-procedures.md) -- Step 2：迭代关闭（归档、自动轻量回顾、dashboard 更新）
- [adjust-procedures.md](../../skills/pace-plan/adjust-procedures.md) -- Step 2.5：迭代中途范围调整（增删 PF、调整优先级、容量重算）
- [health-procedures.md](../../skills/pace-plan/health-procedures.md) -- Step 5：迭代健康度指标（完成率 vs 时间、范围稳定性、速度趋势）
- [iteration-format.md](../../knowledge/_schema/iteration-format.md) -- 迭代文件 schema（字段、PF 列表格式、变更记录）
- [devpace-rules.md](../../rules/devpace-rules.md) -- 运行时行为规则（迭代生命周期集成）
- [用户指南](../user-guide.md) -- 所有命令快速参考
