# Skill 间依赖关系

> **职责**：记录 devpace 19 个 Skill + 11 个 Hook（8 全局 + 3 Skill 级）之间的耦合关系，便于变更影响评估。
>
> **维护规则**：修改任何 Skill 的 procedures 文件或 Hook 逻辑时，对照本文档评估是否需要同步更新关联方。
>
> **最后更新**：2026-03-14

## §0 速查：四大耦合集群

```
┌─────────────────────────────────────────────────────────┐
│  核心开发管道（紧密耦合）                                   │
│                                                         │
│  pace-dev ──writes──> CR files ──reads──> pace-review   │
│  pace-dev ──triggers──> pace-learn (merged 后管道)        │
│  pace-dev ──delegates──> pace-guard scan (risk-format)   │
│  pace-dev ──delegates──> pace-test strategy/dryrun       │
│  pace-review ──consumes──> pace-test accept (契约)        │
│  pace-review ──feeds──> pace-learn (打回信息)             │
│  pace-test dryrun ──refs──> pace-release procedures      │
│  post-cr-update Hook ──triggers──> pace-learn 管道       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  计划与变更管理（中等耦合）                                 │
│                                                         │
│  pace-change ──delegates──> pace-plan adjust 逻辑        │
│  pace-change ──suggests──> pace-dev / pace-sync          │
│  pace-retro ──delegates──> pace-learn 管道 (7 处引用)     │
│  pace-retro ──writes──> iterations/ ──consumed──> pace-plan│
│  pace-biz ──suggests──> pace-change / pace-plan / pace-dev│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  节奏监测（扇入耦合 + 信号缓存枢纽）                        │
│                                                         │
│  pace-pulse ──writes──> .signal-cache ──reads──> pace-next│
│  pace-pulse ──writes──> .signal-cache ──reads──> pace-status│
│  pace-next ──hardcodes──> 21 个信号→命令映射              │
│  pace-status ──positioned-as──> pace-next 轻量子集        │
│  pulse-counter Hook ──coordinates──> pace-pulse          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  支撑与辅助（松散耦合）                                    │
│                                                         │
│  pace-role ──defines──> 角色维度 ──consumed-by──> 6 Skill │
│  pace-init ──delegates──> pace-sync setup               │
│  pace-release ──delegates──> pace-feedback / pace-test    │
│  pace-feedback ──routes──> pace-change / pace-biz         │
│  pace-trace ──navigates──> pace-theory / pace-learn       │
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
| 共享格式 | `knowledge/_schema/entity/cr-format.md` |
| 触发位置 | `skills/pace-dev/SKILL.md:95`（"到达 in_review → 自动运行 /pace-review 逻辑"） |
| 反向感知 | `skills/pace-review/review-procedures-common.md:30`（简化审批由 pace-dev 直接处理） |

### pace-dev → pace-test（Schema 契约 + 命令委托）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **Schema 契约**（通过 test-strategy-format.md）+ 命令委托 + 数据文件共享 |
| 风险等级 | **低**（已解耦） |
| 契约位置 | `dev-procedures-developing.md:147`（引用 `knowledge/_schema/process/test-strategy-format.md`，或委托 `/pace-test strategy`） |
| 命令建议 | `dev-procedures-developing.md:172`（`/pace-test dryrun 1`）、`dev-procedures-gate.md:23`（`/pace-test generate`）、`dev-procedures-intent.md:181`（`/pace-test generate`） |
| 共享数据 | `.devpace/rules/test-strategy.md`、`.devpace/rules/checks.md` |

### pace-dev → pace-guard（Schema 契约 + 命令委托）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **Schema 契约**（通过 risk-format.md）+ 命令委托 |
| 风险等级 | **低**（已解耦） |
| 位置 | `dev-procedures-intent.md:252`（引用 `knowledge/_schema/auxiliary/risk-format.md`，或委托 `/pace-guard scan`） |
| 影响 | 修改 guard-procedures 内部实现不影响 pace-dev（只要 risk-format.md 契约不变） |
| 反向感知 | `skills/pace-guard/SKILL.md:2`（NOT 声明排除触发混淆） |

### pace-dev → pace-learn（merged 后管道 + Gate 反思）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 管道触发 + 数据共享 |
| 风险等级 | 中 |
| 触发机制 | `hooks/post-cr-update.mjs:46` 输出 `devpace:post-merge` → §11 管道含 pace-learn |
| Gate 反思 | `dev-procedures-gate.md:38`（反思内容在 merged 后纳入 pace-learn 范围） |
| Defect 模式 | `dev-procedures-defect.md:29`（"merged 后自动触发 pace-learn 提取根因 pattern"） |

### pace-dev → pace-sync（命令委托）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令委托 |
| 风险等级 | 低 |
| 位置 | `dev-procedures-common.md:33`（用户同意后执行 `/pace-sync create CR-{id}`） |

### pace-review → pace-test accept（共享契约）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **共享 Schema 契约**（通过 accept-report-contract.md） |
| 风险等级 | **中** |
| 契约文件 | `knowledge/_schema/auxiliary/accept-report-contract.md` |
| 声明位置 | `skills/pace-test/SKILL.md:19`（"pace-review Gate 2：可消费 /pace-test accept 的验收映射报告"） |
| 消费逻辑 | `review-procedures-gate.md:191,220,264`（引用契约提取 accept 验证结果） |

### pace-review → pace-learn（打回信息数据流）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据文件共享（CR 事件表写入供下游消费） |
| 风险等级 | 低 |
| 位置 | `review-procedures-feedback.md:7,35`（打回信息写入事件表供 pace-learn 提取） |
| 位置 | `review-procedures-common.md:112`（"支持 /pace-learn：不仅有打回原因，还有完整审查发现"） |

### pace-review → pace-trace（决策轨迹）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据共享（Review 判断作为决策轨迹） |
| 风险等级 | 低 |
| 位置 | `review-procedures-common.md:113` |

### pace-test → pace-release（跨 Skill 文件路径引用）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **直接文件路径引用** |
| 风险等级 | **中**（非命令委托，直接引用 procedures 文件） |
| 位置 | `test-procedures-dryrun.md:24`（直接引用 `skills/pace-release/release-procedures-create-enhanced.md` 的 Gate 4 检查项） |
| 影响 | pace-release 重命名或重组 procedures 文件会导致 pace-test 引用断裂 |

### pace-test → pace-retro（基准线数据共享）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据共享 |
| 风险等级 | 低 |
| 位置 | `SKILL.md:41`、`test-procedures-baseline.md:13`（"baseline 供 /pace-retro 度量使用"） |

### pace-guard → pace-pulse（monitor 触发）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令触发（pace-pulse 周期性触发 monitor） |
| 风险等级 | 低 |
| 位置 | `SKILL.md:18,28-29`（monitor 由 pace-pulse 第 8 信号触发） |

### pace-guard → pace-retro（trends 数据消费）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据共享 |
| 风险等级 | 低 |
| 位置 | `guard-procedures-trends.md:68`（被 /pace-retro 消费时自动升级详细度） |

### insights.md 写入冲突风险（已修复）

| 属性 | 值 |
|------|-----|
| 风险等级 | ~~中（SSOT 冲突）~~ → **低**（已修复） |
| SSOT 声明方 | pace-learn（`learn-procedures.md:11` 声称唯一写入者） |
| 修复方案 | pace-test flaky Step 6 改为构造学习请求交给 pace-learn 统一管道（与 pace-retro 模式一致） |
| 修复日期 | 2026-03-14 |

## §2 计划与变更管理

### pace-change → pace-plan adjust（命令委托）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **命令委托**（通过 `/pace-plan adjust` + iteration-format.md 契约） |
| 风险等级 | **低**（已解耦） |
| 位置 | `change-procedures-types.md:85`（容量溢出时自动委托 `/pace-plan adjust`） |
| 契约 | `knowledge/_schema/process/iteration-format.md` |

### pace-change → pace-dev / pace-sync（流转建议）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令建议 |
| 风险等级 | 低 |
| 位置 | `change-procedures-types.md:99-103`（5 种变更类型的下一步引导） |
| 位置 | `change-procedures-execution.md:52-53`（建议 `/pace-sync push`） |

### pace-change → pace-test impact（测试影响建议）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令建议 + 数据共享 |
| 风险等级 | 低 |
| 位置 | `change-procedures-types.md:71`（建议 `/pace-test impact`、`/pace-test strategy`） |
| 位置 | `change-procedures-risk.md:7`（引用 pace-test 写入的影响分析 section） |

### pace-retro → pace-learn（学习请求管道）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **数据格式依赖**（最强外部依赖，7 处引用） |
| 风险等级 | **中** |
| 位置 | `retro-procedures.md:190,201,210,215,230,237,253`（pattern 统一写入管道） |
| 共享格式 | `knowledge/_schema/auxiliary/insights-format.md`（retro:195 引用） |

### pace-retro → pace-plan（迭代传递清单）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据文件共享（结构化传递） |
| 风险等级 | 中 |
| 位置 | `retro-procedures.md:560`（传递清单写入 `iterations/current.md`） |
| 消费方 | `SKILL.md:89`（"供 /pace-plan next 消费"） |

### pace-retro → pace-role（角色适配）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 概念对齐（角色适配权威源引用） |
| 风险等级 | 低 |
| 位置 | `retro-procedures.md:74`（引用 `skills/pace-role/role-procedures-dimensions.md`） |
| 位置 | `retro-procedures.md:73`（引用 `devpace-rules.md §13` 读取当前角色） |

### pace-biz → pace-change / pace-plan（命令建议密集）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令建议（最大引用发出者） |
| 风险等级 | 低（纯建议，无数据依赖） |
| 向 pace-change | 6 处引用（SKILL.md、epic、decompose、output 等 procedures 中的 downstream 引导） |
| 向 pace-plan | 8 处引用（SKILL.md、decompose、discover、import、infer 等 procedures 中的引导） |

### pace-change → pace-init（降级引导）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令建议 |
| 风险等级 | 低 |
| 位置 | `change-procedures-degraded.md:38,54-55`（未初始化时引导） |

## §3 节奏监测

### 信号缓存枢纽（.signal-cache）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **数据文件共享**（三 Skill 核心枢纽） |
| 风险等级 | **中** |
| 写入方 | pace-pulse session-start（`pulse-procedures-session-start.md:48`） |
| 读取方 | pace-next（`next-procedures.md:30`）、pace-status overview（`status-procedures-overview.md:21`） |
| TTL | 5 分钟 |
| 共享格式 | `knowledge/_signals/signal-collection.md`（缓存格式定义） |

### pace-next → 21 个信号命令映射（硬编码）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **数据依赖（硬编码命令名表）** |
| 风险等级 | 中 |
| SKILL.md 映射 | `next-procedures-output-default.md:27-41`（S1-S16 共 16 个信号→命令映射） |
| 脚本映射 | `scripts/collect-signals.mjs:354-543`（S1-S25 共 21 个信号→命令映射，含 S16-S19 pace-biz、S21-S25 新增信号） |
| 影响 | 新增/重命名 Skill 命令时须同步更新两处映射表 |

### pace-status ↔ pace-next（双向互斥 + 轻量子集）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 概念对齐（双向互斥边界声明） |
| 风险等级 | 低 |
| pace-status → pace-next | `SKILL.md:2`（"NOT for next-step recommendations"）、`status-procedures-overview.md:23`（定位为"pace-next 轻量子集"）、`:38`（升级导航到 `/pace-next detail`） |
| pace-next → pace-status | `SKILL.md:2`（"NOT for current progress overview"） |

### pace-pulse ↔ pace-status（推/拉去重）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据共享（去重协调） |
| 风险等级 | 低 |
| 位置 | `pulse-procedures-session-start.md:29`（引用 `status-procedures-overview.md` "推/拉去重"节） |
| 机制 | pulse 是"推送式"，status 是"拉取式"，距会话开始 < 5 分钟时省略建议行 |

### pace-next ↔ pace-pulse（session-start 去重）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 概念对齐（无直接文件引用） |
| 风险等级 | 低 |
| 位置 | `next-procedures.md:67-69`（距 session-start < 5 分钟时跳过已通知信号） |

### pulse-counter Hook ↔ pace-pulse（协调互补）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 运行时协调（时间戳文件） |
| 风险等级 | 低 |
| 位置 | `hooks/pulse-counter.mjs:92-98` |
| 协调机制 | pulse-counter 读取 `.devpace/.pulse-last-run`（pace-pulse 写入），5 分钟内不重复提醒 |

### 共享 knowledge 依赖

| knowledge 文件 | pace-next | pace-pulse | pace-status |
|---------------|-----------|------------|-------------|
| `signal-priority.md` | 排序规则权威源 | — | 信号子集权威源 |
| `signal-collection.md` | 缓存规则 | 缓存格式 | 缓存规则 |

## §4 支撑与辅助

### pace-role → 6 个消费方（角色维度权威源）

| 属性 | 值 |
|------|-----|
| 耦合类型 | **概念对齐**（`role-procedures-dimensions.md` 被 6 个 Skill 引用为权威源） |
| 风险等级 | **中**（修改角色定义影响面广） |
| 消费方 | pace-retro(`:74`)、pace-next(`:104`)、pace-pulse(`SKILL.md:60`)、pace-status(`status-procedures-roles.md`)、pace-change(`change-procedures-impact.md:72`)、pace-theory(`theory-procedures-default.md:78`) |
| 影响 | 新增/修改角色维度时须同步 CLAUDE.md "pace-role 角色扩展清单"中列出的 13 个文件 |

### pace-init → pace-sync setup（命令委托）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令委托（8 处引用，含 2 处自动执行） |
| 风险等级 | 低 |
| 自动执行 | `init-procedures-full.md:124,126`、`init-procedures-core.md:198-199`（用户选择后自动执行 `/pace-sync setup`） |
| 命令建议 | `init-procedures-core.md:130-132,203,268,285` 等 |

### pace-release → pace-feedback（命令委托）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令委托 |
| 风险等级 | 低 |
| 位置 | `release-procedures-common.md:74`（deployed 后问题走 `/pace-feedback report`） |
| 位置 | `release-procedures-verify.md:78`（验证失败引导 `/pace-feedback report`） |

### pace-release → pace-test（命令委托）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令委托（可选联动） |
| 风险等级 | 低 |
| 位置 | `release-procedures-create-enhanced.md:55-58,146,149`（测试覆盖联动、Release 测试报告） |

### pace-release ↔ pace-pulse / pace-plan（概念联动）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 概念对齐（无直接数据依赖） |
| 风险等级 | 低 |
| 位置 | `release-procedures-scheduling.md:5,11,36`（发布窗口信号由 pace-pulse 触发） |
| 位置 | `release-procedures-scheduling.md:11,40`（迭代结束提示联动 pace-plan） |

### pace-feedback → pace-change / pace-biz（功能请求路由）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令委托（功能请求分流） |
| 风险等级 | 低 |
| 位置 | `feedback-procedures-intake.md:42,46-47`（有 Epic 结构 → `/pace-biz discover`，无 Epic → `/pace-change add`） |

### pace-trace → pace-theory / pace-learn（导航链接）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 命令建议（导航链接表） |
| 风险等级 | 低 |
| 位置 | `trace-procedures-analysis.md:21-24`（6 个导航链接指向 pace-theory、pace-change、pace-test、pace-guard、pace-learn、pace-role） |
| 位置 | `trace-procedures-gates.md:20-22`（指向 pace-learn、pace-retro、pace-status） |

### pace-theory → knowledge/theory.md（数据源）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 数据共享（运行时数据源） |
| 风险等级 | 低 |
| 位置 | `SKILL.md:44`（按路由表选择性读取）、`theory-procedures-why.md:62`（§11 设计决策权威源）、`theory-procedures-search.md:14`（Grep 搜索） |

### pace-sync → devpace-rules.md §2（状态转换验证）

| 属性 | 值 |
|------|-----|
| 耦合类型 | 概念对齐 |
| 风险等级 | 低 |
| 位置 | `sync-procedures-pull.md:26`（外部状态同步回写时验证状态转换合法性） |

## §5 Hook 系统

### 全局 Hook 事件绑定

| Hook 文件 | 事件 | async | 性质 |
|-----------|------|-------|------|
| `skill-eval.mjs` | UserPromptSubmit | true | Advisory（含变更管理检测，取代 intent-detect.mjs） |
| `pre-tool-use.mjs` | PreToolUse (Write\|Edit) | false | **BLOCKING** (exit 2) + Advisory |
| `post-cr-update.mjs` | PostToolUse (Write\|Edit) | true | Advisory |
| `pulse-counter.mjs` | PostToolUse (Write\|Edit) | true | Advisory |
| `sync-push.mjs` | PostToolUse (Write\|Edit) | true | Advisory |
| `post-schema-check.mjs` | PostToolUse (Write\|Edit) | true | Advisory |
| `post-tool-failure.mjs` | PostToolUseFailure (Write\|Edit) | false | Advisory |
| `subagent-stop.mjs` | SubagentStop | false | Advisory |

Shell Hook：`session-start.sh`(SessionStart)、`pre-compact.sh`(PreCompact)、`session-stop.sh`(Stop)、`session-end.sh`(SessionEnd)。

Skill 级 Hook：`pace-dev-scope-check.mjs`(PreToolUse)、`pace-review-scope-check.mjs`(PreToolUse)、`pace-init-scope-check.mjs`(PreToolUse)。

### Hook → devpace-rules.md 章节引用

| Hook 文件 | 引用章节 | 行号 | 类型 |
|-----------|---------|------|------|
| `skill-eval.mjs` | §9 | — | **运行时输出**（变更管理流程，含 intent-detect 功能） |
| `pre-tool-use.mjs` | §2 | :15 | 注释（Gate 3 人类审批来源） |
| `post-cr-update.mjs` | §11 | :46 | **运行时输出**（post-merge pipeline） |
| `sync-push.mjs` | §11 step 7 | :89-90 | **运行时输出**（close-loop） |
| `sync-push.mjs` | §16 rule 9 | :14 | 注释（噪音抑制设计） |

### Hook → /pace-* 命令引用

| 命令 | Hook 来源 | 行号 | 引用方式 |
|------|----------|------|---------|
| `/pace-dev`（间接） | pre-tool-use.mjs | :48 | 阻断消息建议进入推进模式 |
| `/pace-learn` | post-cr-update.mjs | :53, :58 | 学习触发建议 |
| `/pace-sync push` | sync-push.mjs | :90, :93 | 外部同步建议 |
| `/pace-status` | pulse-counter.mjs | :86, :105 | 进度检查建议 |
| `/pace-status` | subagent-stop.mjs | :106 | 状态修正建议 |

### Hook 间协调关系

| 协调对 | 机制 |
|--------|------|
| `pulse-counter` ↔ `pace-pulse` (Skill) | `.pulse-last-run` 时间戳，5 分钟内不重复提醒 |
| `pre-tool-use` ↔ Skill 级 hooks | 全局 hook 执行 Gate 3 阻断，Skill 级 hook 注释 "delegated to global hook" |
| `pre-tool-use` ↔ `post-tool-failure` | 共用 `isAdvanceMode` 判断（同一 `state.md` 数据源） |
| 4 个 PostToolUse hooks | 并行 async 执行，职责互补不重叠 |

### devpace: 消息前缀汇总

| 前缀 | 来源 | 性质 |
|------|------|------|
| `devpace:change-detected` | skill-eval.mjs | advisory |
| `devpace:blocked` | pre-tool-use.mjs:48,62 | **BLOCKING** |
| `devpace:gate-reminder` | pre-tool-use.mjs:70,73,76 | advisory |
| `devpace:post-merge` | post-cr-update.mjs:46 | advisory |
| `devpace:learn-trigger` | post-cr-update.mjs:53,58 | advisory |
| `devpace:sync-push` | sync-push.mjs:90,93 | advisory |
| `devpace:stuck-warning` | pulse-counter.mjs:86 | advisory |
| `devpace:write-volume` | pulse-counter.mjs:105 | advisory |
| `devpace:tool-failure` | post-tool-failure.mjs:28,30 | advisory |
| `devpace:schema-check` | post-schema-check.mjs:73 | advisory |
| `devpace:subagent-check` | subagent-stop.mjs:102 | advisory |

## §6 变更影响矩阵

修改左侧组件时，需检查右侧关联方：

| 修改对象 | 需检查 |
|---------|--------|
| pace-dev (CR 状态转换逻辑) | pace-review, post-cr-update Hook, sync-push Hook, pace-pulse, subagent-stop Hook |
| pace-dev (Gate 检查逻辑) | pace-test (dryrun 对照表), pre-tool-use Hook |
| pace-guard `guard-procedures-scan.md` | 无直接依赖方（通过 risk-format.md 契约） |
| pace-test `test-procedures-strategy-gen.md` | 无直接依赖方（通过 test-strategy-format.md 契约） |
| pace-test accept (输出格式) | **accept-report-contract.md**（契约文件）→ **pace-review**（消费方） |
| pace-test dryrun (Gate 4 检查项) | 直接引用 `pace-release/release-procedures-create-enhanced.md`（文件路径耦合） |
| pace-plan `adjust-procedures.md` | 无直接依赖方（pace-change 已改为委托 `/pace-plan adjust`） |
| **accept-report-contract.md** | **pace-test accept**（生产方）+ **pace-review**（消费方） |
| pace-learn (写入管道格式) | pace-retro (学习请求格式, 7 处引用), post-cr-update Hook |
| pace-retro (迭代传递清单格式) | pace-plan next (消费传递清单) |
| pace-next 命令映射表 | 新增/重命名任何 Skill 命令时（SKILL.md + collect-signals.mjs 两处） |
| pace-pulse 信号→命令映射 | 新增/重命名任何 Skill 命令时（core + session-start 两个 procedures 文件） |
| **pace-role 角色维度定义** | **6 个消费方**：pace-retro, pace-next, pace-pulse, pace-status, pace-change, pace-theory（+ CLAUDE.md 扩展清单中 13 个文件） |
| pace-release (procedures 文件结构) | pace-test dryrun（直接文件路径引用） |
| pace-feedback (feedback-log 格式) | pace-retro (回顾时可用数据), pace-plan (规划时扫描) |
| CR Schema (`cr-format.md`) | pace-dev, pace-review, pace-change, pace-status, pace-feedback, pace-pulse, 所有 Hook |
| `devpace-rules.md §2` | pre-tool-use Hook（注释）, pace-sync pull（状态转换验证） |
| `devpace-rules.md §9` | skill-eval Hook（**运行时输出**，含变更管理检测） |
| `devpace-rules.md §10` | pace-pulse SKILL.md（脉搏触发时机）, pulse-counter Hook |
| `devpace-rules.md §11` | post-cr-update Hook（**运行时输出** :46）, sync-push Hook（**运行时输出** :90）, pace-feedback（§11 连锁扫描） |
| `devpace-rules.md §13` | pace-retro（角色读取）, pace-next（角色意识）, pace-role inference（权威源） |
| `devpace-rules.md §15` | pace-status roles（教学标记去重） |
| `devpace-rules.md §16` | sync-push Hook（注释，噪音抑制） |
| `knowledge/_signals/signal-priority.md` | pace-next（排序权威源）, pace-status overview（信号子集） |
| `knowledge/_signals/signal-collection.md` | pace-next（缓存规则）, pace-pulse session-start（缓存格式）, pace-status overview（缓存规则） |

## §7 共享数据文件索引

| 数据文件 | 写入方 | 读取方 |
|---------|--------|--------|
| `.devpace/backlog/CR-*.md` | pace-dev, pace-change | pace-review, pace-status, pace-pulse, pace-next, pace-retro, pace-test, pace-guard, pace-feedback, 5 个 Hook (pre-tool-use, post-cr-update, sync-push, pulse-counter, subagent-stop) |
| `.devpace/state.md` | pace-dev, pace-init, pace-plan | pre-tool-use Hook, post-tool-failure Hook, subagent-stop Hook, pulse-counter Hook(间接), skill-eval Hook, pace-pulse, pace-next, pace-status, pace-theory |
| `.devpace/project.md` | pace-init, pace-retro(accept MoS), pace-role(set-default), pace-pulse(自主级别) | pace-plan, pace-retro, pace-change, pace-guard, pace-next, pace-status, pace-biz, pace-theory |
| `.devpace/rules/checks.md` | pace-init, pace-test | pace-dev (Gate 1/2), pace-change, pace-pulse, pace-status, pace-theory |
| `.devpace/rules/test-strategy.md` | pace-dev(自动生成), pace-test(strategy/generate/coverage/flaky) | pace-dev, pace-test(多个子命令), pace-change(陈旧标记) |
| `.devpace/rules/test-baseline.md` | pace-test(core/baseline) | pace-retro(common/focus) |
| `.devpace/context.md` | pace-dev(首次推进) | pace-test(common/verify), pace-guard(scan) |
| `.devpace/metrics/insights.md` | pace-learn(**SSOT**), pace-init(from 导入) | pace-guard(common/scan/trends), pace-retro(retro/focus), pace-plan, pace-next, pace-change, pace-status metrics |
| `.devpace/metrics/dashboard.md` | pace-retro(common), pace-test(report), pace-plan(close), pace-feedback(status) | pace-pulse, pace-next, pace-status, pace-plan, pace-guard(scan), pace-retro(compare/history) |
| `.devpace/iterations/current.md` | pace-plan, pace-retro(传递清单), pace-change(变更记录) | pace-dev(postmerge), pace-pulse, pace-next, pace-status, pace-retro, pace-change, pace-theory |
| `.devpace/risks/RISK-*.md` | pace-guard(scan/common) | pace-guard(monitor/report/trends/resolve), pace-learn, pace-pulse, pace-next, pace-plan, pace-retro(forecast) |
| `.devpace/releases/*.md` | pace-release | pace-test(report), pace-retro(DORA/focus), pace-next, pace-change, pace-feedback, pace-status |
| `.devpace/integrations/sync-mapping.md` | pace-sync(setup) | sync-push Hook, pace-dev(common), pace-pulse, pace-next, pace-status, pace-init(reset) |
| `.devpace/integrations/config.md` | pace-sync(setup), pace-init(full) | pace-test(CI), pace-feedback(hotfix) |
| `.devpace/.signal-cache` | pace-pulse(session-start) | pace-next, pace-status overview |
| `.devpace/.pulse-last-run` | pace-pulse(advance mode) | pulse-counter Hook |
| `.devpace/.pulse-counter` | pulse-counter Hook | pulse-counter Hook |
| `.devpace/.pulse-cr-writes` | pulse-counter Hook | pulse-counter Hook |
| `.devpace/.sync-state-cache` | sync-push Hook | sync-push Hook |
| `.devpace/feedback-log.md` | pace-feedback | pace-feedback(trace/status) |
| `.devpace/feedback-inbox.md` | pace-feedback | pace-plan(规划时扫描) |
| `.devpace/incidents/*.md` | pace-feedback(incident) | pace-feedback(列出) |
| `.devpace/decisions/ADR-*.md` | pace-trace(arch) | pace-trace(列出) |
| `.devpace/epics/EPIC-*.md` | pace-biz(epic) | pace-biz(扫描) |
| `.devpace/opportunities.md` | pace-biz(opportunity) | pace-biz(discover) |
| `.devpace/scope-discovery.md` | pace-biz(discover) | pace-biz(discover) |
| `.devpace/rules/workflow.md` | pace-init(模板复制) | pace-dev |
| `.devpace/rules/change-templates.md` | (pace-learn 建议创建) | pace-change(apply) |
| `.devpace/features/*` | pace-dev(postmerge 溢出) | — |
| `.devpace/requirements/*` | pace-dev(postmerge 溢出) | — |
| `.devpace/reports/test-report-*.md` | pace-test(report) | (人类消费) |

## §8 共享工具函数（lib/utils.mjs）

所有 Hook 共用 `hooks/lib/utils.mjs` 中的工具函数：

| 函数 | 使用该函数的 Hook |
|------|-----------------|
| `readStdinJson` | 全部 8 个 |
| `getProjectDir` | 全部 8 个 |
| `extractFilePath` | pre-tool-use, post-cr-update, sync-push, pulse-counter, post-tool-failure, post-schema-check |
| `isCrFile` | pre-tool-use, post-cr-update, sync-push, pulse-counter, post-tool-failure |
| `readCrState` | pre-tool-use, post-cr-update, sync-push, pulse-counter, subagent-stop |
| `isDevpaceFile` | pre-tool-use, post-schema-check |
| `isAdvanceMode` | pre-tool-use, post-tool-failure, subagent-stop |
| `CR_STATES` | pre-tool-use, post-cr-update, sync-push, subagent-stop |
