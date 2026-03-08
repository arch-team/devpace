# Skill 间依赖关系

> **职责**：记录 devpace 18 个 Skill + 6 个 Hook 之间的耦合关系，便于变更影响评估。
>
> **维护规则**：修改任何 Skill 的 procedures 文件或 Hook 逻辑时，对照本文档评估是否需要同步更新关联方。

## §0 速查：三大耦合集群

```
┌─────────────────────────────────────────────────────────┐
│  核心开发管道（紧密耦合）                                   │
│                                                         │
│  pace-dev ──writes──> CR files ──reads──> pace-review   │
│  pace-dev ──triggers──> pace-learn (merged 后管道)        │
│  pace-dev ──triggers──> pace-guard (L/XL pre-flight)     │
│  pace-dev ──triggers──> pace-test (dryrun 建议)           │
│  pace-review ──reads──> pace-test accept 证据             │
│  post-cr-update Hook ──triggers──> pace-learn 管道       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  计划与变更管理（中等耦合）                                 │
│                                                         │
│  pace-change ──inlines──> pace-plan adjust 逻辑          │
│  pace-change ──suggests──> pace-dev / pace-sync          │
│  pace-retro ──produces──> 学习请求 ──consumed──> pace-learn│
│  pace-retro ──writes──> iterations/ ──consumed──> pace-plan│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  节奏监测（扇入耦合）                                      │
│                                                         │
│  pace-pulse ──reads──> 多 Skill 的数据文件（13 信号源）     │
│  pace-next ──hardcodes──> 14 个 Skill 命令名映射          │
│  pulse-counter Hook ──coordinates──> pace-pulse          │
└─────────────────────────────────────────────────────────┘
```

## §1 核心开发管道

### pace-dev → pace-review（CR 文件共享 + 自动触发）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据文件共享 + 命令触发 + 状态机共享 |
| 风险等级 | **高** |
| 写入方 | pace-dev（创建 CR、更新状态/事件记录） |
| 读取方 | pace-review（读取 CR 状态、验收条件、事件记录、复杂度、分支名） |
| 共享格式 | `knowledge/_schema/cr-format.md` |
| 触发位置 | `skills/pace-dev/SKILL.md:96`（"到达 in_review → 自动运行 /pace-review 逻辑"） |
| 反向感知 | `skills/pace-review/review-procedures-common.md:30`（简化审批由 pace-dev 直接处理） |

### pace-dev → pace-learn（merged 后管道）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 管道触发（CR 进入 merged 状态后自动执行） |
| 风险等级 | 中 |
| 触发机制 | `post-cr-update.mjs:43` 输出 `pace-learn knowledge extraction` 步骤 |
| 位置 | `hooks/post-cr-update.mjs:42-43` |

### pace-dev → pace-guard（L/XL 预检 + Schema 契约）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **Schema 契约**（通过 risk-format.md 接口）+ 命令委托 |
| 风险等级 | **低**（已解耦） |
| 位置 | `skills/pace-dev/dev-procedures-intent.md:206`（引用 `knowledge/_schema/risk-format.md` 风险预评估章节，或委托 `/pace-guard scan`） |
| 描述 | pace-dev 通过共享 Schema 定义输出格式，不再直接引用 pace-guard 内部 procedures 文件 |
| 影响 | 修改 guard-procedures 内部实现不影响 pace-dev（只要 risk-format.md 契约不变） |
| 反向感知 | `skills/pace-guard/SKILL.md:2`（NOT 声明排除触发混淆） |

### pace-dev → pace-test（Schema 契约 + 命令委托）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **Schema 契约**（通过 test-strategy-format.md 接口）+ 命令委托 + 数据文件共享 |
| 风险等级 | **低**（已解耦） |
| 契约位置 | `skills/pace-dev/dev-procedures-developing.md:146`（引用 `knowledge/_schema/test-strategy-format.md`，或委托 `/pace-test strategy`） |
| 命令建议 | `dev-procedures-developing.md:135`（`/pace-test generate`）、`:171`（`/pace-test dryrun 1`）、`dev-procedures-gate.md:17`（`/pace-test generate`） |
| 共享数据 | `.devpace/rules/test-strategy.md`、`.devpace/rules/checks.md` |
| 影响 | 修改 test-procedures 内部实现不影响 pace-dev（只要 test-strategy-format.md 契约不变） |

### pace-review → pace-test accept（共享契约）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **共享 Schema 契约**（通过 accept-report-contract.md 接口） |
| 风险等级 | **中**（已从"很高"降级——格式变更通过契约文件协调） |
| 契约文件 | `knowledge/_schema/accept-report-contract.md`（生产方和消费方的共享接口） |
| 声明位置 | `skills/pace-test/SKILL.md:19`（"pace-review Gate 2：可消费 /pace-test accept 的验收映射报告"） |
| 消费逻辑 | `skills/pace-review/review-procedures-gate.md`（引用 accept-report-contract.md 提取规则） |
| 模板嵌入 | `review-procedures-gate.md` 摘要模板的 accept 字段按契约定义的格式填充 |
| 影响 | 变更 accept 输出格式时修改 accept-report-contract.md，双方同步适配 |

### pace-review → pace-learn（打回信息数据流）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据文件共享（CR 事件表写入供下游消费） |
| 风险等级 | 低 |
| 位置 | `skills/pace-review/review-procedures-feedback.md:7,35`（结构化打回信息写入事件表供 pace-learn 提取） |
| 位置 | `skills/pace-review/review-procedures-common.md:112`（"支持 /pace-learn：不仅有打回原因，还有完整审查发现"） |

### pace-test → pace-dev（Gate 检查互认）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 概念对齐 |
| 风险等级 | 低 |
| 位置 | `skills/pace-test/SKILL.md:18`（"/pace-dev Gate 1/2：消费 checks.md 中的测试命令"） |
| 位置 | `skills/pace-test/test-procedures-dryrun.md:8`（"与 /pace-dev Gate 的区别"对照表） |

## §2 计划与变更管理

### pace-change → pace-plan adjust（命令委托）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **命令委托**（通过 `/pace-plan adjust` 委托 + iteration-format.md 契约） |
| 风险等级 | **低**（已解耦） |
| 位置 | `skills/pace-change/change-procedures-types.md:85` |
| 描述 | "用户确认 → 委托 `/pace-plan adjust` 执行，迭代写入规则见 iteration-format.md" |
| 影响 | 修改 adjust-procedures.md 内部实现不影响 pace-change（只要 iteration-format.md 契约不变） |

### pace-change → pace-dev / pace-sync（流转建议）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令建议（变更执行后的下一步引导） |
| 风险等级 | 低 |
| 位置 | `skills/pace-change/change-procedures-types.md:99-103`（5 种变更类型各有对应的下一步命令） |
| 位置 | `skills/pace-change/change-procedures-execution.md:52-53`（建议 `/pace-sync push`） |

### pace-change → pace-test impact（测试影响建议）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令建议 |
| 风险等级 | 低 |
| 位置 | `skills/pace-change/change-procedures-types.md:71`（建议 `/pace-test impact`） |

### pace-retro → pace-learn（学习请求管道）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **数据格式依赖** |
| 风险等级 | 中 |
| 位置 | `skills/pace-retro/retro-procedures.md:159-206` |
| 描述 | pace-retro Step 5 构造"学习请求"，交给 pace-learn 统一写入管道处理 |
| 共享格式 | 学习请求结构（pace-learn 定义，pace-retro 生产） |

### pace-retro → pace-plan（迭代传递清单）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据文件共享 |
| 风险等级 | 中 |
| 位置 | `skills/pace-retro/retro-procedures.md:529`（写入 `iterations/current.md` 的回顾 section） |
| 消费方 | `skills/pace-retro/SKILL.md:86`（"供 /pace-plan next 消费"） |

### pace-change → pace-init（降级引导）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令建议（未初始化时引导） |
| 风险等级 | 低 |
| 位置 | `skills/pace-change/change-procedures-degraded.md:38,54-55` |

## §3 节奏监测

### pace-next → 14 个 Skill 命令映射（硬编码）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **数据依赖（硬编码命令名表）** |
| 风险等级 | 中 |
| 位置 | `skills/pace-next/next-procedures-output-default.md:27-40` |
| 映射表 | S1→pace-review, S2→pace-guard report, S3→pace-dev, S4→pace-change resume, S5→pace-release, S6→pace-guard report, S7→pace-plan adjust, S8→pace-retro+pace-plan, S9→pace-retro, S10→pace-guard report, S11→pace-sync push, S12→pace-retro, S14→pace-plan |
| 影响 | 新增/重命名 Skill 命令时须同步更新此映射表 |

### pace-pulse → 多 Skill 数据文件（只读扇入）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 只读数据消费（13 信号源） |
| 风险等级 | 低（只读不影响源 Skill） |
| 位置 | `skills/pace-pulse/pulse-procedures-core.md:10-20` |
| 信号源 | `current.md` PF 完成率、CR 滞留时间、checks.md 失败率、current.md 变更记录、`.devpace/risks/` 风险文件、`sync-mapping.md` 同步状态、`dashboard.md` 度量更新日期、`state.md` 会话时间 |

### pulse-counter Hook ↔ pace-pulse（协调互补）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 运行时协调（时间戳文件） |
| 风险等级 | 低 |
| 位置 | `hooks/pulse-counter.mjs:7-16` |
| 协调机制 | pulse-counter 检查 `.devpace/.pulse-last-run`（pace-pulse 写入），若 pace-pulse 近 5 分钟内运行过则跳过提醒 |

## §4 Hook ↔ Rules 章节引用

| Hook 文件 | 引用的 Rules 章节 | 位置 |
|-----------|-------------------|------|
| `intent-detect.mjs` | `devpace-rules.md §9` | :48 |
| `sync-push.mjs` | `§16 rule 9`（噪声控制）、`§11 step 7`（close-loop） | :14, :84-85 |
| `pre-tool-use.mjs` | `devpace-rules.md §2`（双模式、Gate 3） | :12-13 |
| `post-cr-update.mjs` | `§11`（合并后管道步骤） | :6, :40 |

## §5 变更影响矩阵

修改左侧 Skill/Hook 时，需检查右侧关联方：

| 修改对象 | 需检查 |
|---------|--------|
| pace-dev (CR 状态转换逻辑) | pace-review, post-cr-update Hook, sync-push Hook, pace-pulse |
| pace-dev (Gate 检查逻辑) | pace-test (dryrun 对照表), pre-tool-use Hook |
| pace-guard `guard-procedures-scan.md` | 无直接依赖方（pace-dev 已改引用 risk-format.md 契约） |
| pace-test `test-procedures-strategy-gen.md` | 无直接依赖方（pace-dev 已改引用 test-strategy-format.md 契约） |
| pace-test accept (输出格式) | **accept-report-contract.md**（变更格式时需同步更新契约文件） |
| pace-plan `adjust-procedures.md` | 无直接依赖方（pace-change 已改为委托 `/pace-plan adjust`） |
| **accept-report-contract.md** | **pace-test accept**（生产方）+ **pace-review**（消费方） |
| pace-learn (写入管道格式) | pace-retro (学习请求格式), post-cr-update Hook |
| pace-retro (迭代传递清单格式) | pace-plan next (消费传递清单) |
| pace-next 命令映射表 | 新增/重命名任何 Skill 命令时 |
| pace-pulse 信号→命令映射 | 新增/重命名任何 Skill 命令时（4 个 procedures 文件） |
| CR Schema (`cr-format.md`) | pace-dev, pace-review, pace-change, pace-status, pace-pulse, 所有 Hook |
| `devpace-rules.md §2` | pre-tool-use Hook（注释） |
| `devpace-rules.md §9` | intent-detect Hook（**运行时输出** :48） |
| `devpace-rules.md §11` | post-cr-update Hook（注释）, sync-push Hook（**运行时输出** :85） |
| `devpace-rules.md §16` | sync-push Hook（注释） |

## §6 共享数据文件索引

| 数据文件 | 写入方 | 读取方 |
|---------|--------|--------|
| `.devpace/backlog/CR-*.md` | pace-dev, pace-change | pace-review, pace-status, pace-pulse, pace-next, 4 个 Hook |
| `.devpace/state.md` | pace-dev, pace-init | pre-tool-use Hook, pace-dev-scope-check Hook, post-tool-failure Hook, pace-pulse |
| `.devpace/rules/checks.md` | pace-dev, pace-test | pace-dev (Gate 1/2), pace-pulse |
| `.devpace/rules/test-strategy.md` | pace-test strategy | pace-dev (测试先行引导) |
| `.devpace/dashboard.md` | pace-retro | pace-pulse, pace-status |
| `.devpace/iterations/current.md` | pace-plan, pace-retro | pace-pulse, pace-plan next |
| `.devpace/risks/` | pace-guard | pace-pulse |
| `.devpace/integrations/sync-mapping.md` | pace-sync | sync-push Hook, post-cr-update Hook, pace-pulse |
| `.devpace/.sync-state-cache` | sync-push Hook | sync-push Hook |
| `.devpace/.pulse-last-run` | pace-pulse (advance mode) | pulse-counter Hook |
| `.devpace/insights.md` | pace-learn | pace-retro (引用), pace-feedback |
