# devpace UX 审计报告

> 审计版本：v1.4.0 | 审计日期：2026-02-25 | 审计视角：首次使用 devpace 的独立开发者

---

## 1. 执行摘要

devpace 在概念设计层面展现了成熟的 UX 思维——零摩擦启动（P1）、渐进暴露（P2/P6）、副产物非前置（P3）等原则有明确落地。核心路径（init→dev→review→merged）体验流畅，自然语言交互和 ID 隐藏让用户无需学习内部术语。

但审计发现 3 个 Critical 级摩擦点：(1) 17 个 Skill 的认知负荷过高，新用户面对 `/pace-` 命名空间时缺乏分层导航；(2) `/pace-test` 子命令体系过于复杂（10+ 子命令），与 P2 渐进暴露原则冲突；(3) `/pace-guard`、`/pace-trace` 的命名无法从名称猜出功能。跨 Skill 一致性总体良好，但子命令风格（动词 vs 名词）和参数格式存在不一致。总体评价：核心流程体验 4/5，进阶/专项 Skill 的可发现性和渐进暴露 2.5/5。

---

## 2. Skill 发现性评分

### 评分标准

- **5 分**：名称即功能，任何开发者看到名称能直觉猜出用途
- **4 分**：稍加思考可以猜出，或通过上下文暗示理解
- **3 分**：名称有一定关联但需要说明才能确认
- **2 分**：名称容易误解或与功能关联弱
- **1 分**：名称完全无法映射到功能

### 评分表

| Skill | 评分 | 分析 | 改进建议 |
|-------|------|------|---------|
| `/pace-init` | **5** | "init"是通用初始化约定，开发者熟知 | 无需改进 |
| `/pace-dev` | **4** | "dev"暗示开发，但容易理解为"开发环境"而非"推进变更" | 可考虑别名 `/pace-work` |
| `/pace-status` | **5** | "status"直觉映射到查看进度 | 无需改进 |
| `/pace-review` | **5** | "review"即代码审查，开发者直觉理解 | 无需改进 |
| `/pace-next` | **4** | "next"暗示下一步推荐，但可能与"下一个迭代"混淆 | 可补充 description 强化语义 |
| `/pace-change` | **4** | "change"关联需求变更，但可能误解为"修改配置" | 可考虑别名 `/pace-adjust` |
| `/pace-plan` | **5** | "plan"即迭代规划，直觉理解 | 无需改进 |
| `/pace-retro` | **3** | "retro"是敏捷术语，非敏捷背景开发者可能不懂 | 可考虑别名 `/pace-review-iter` 或在 help 中标注"迭代回顾/复盘" |
| `/pace-release` | **5** | "release"即发布，直觉理解 | 无需改进 |
| `/pace-feedback` | **4** | "feedback"可理解为反馈收集，但与"给 devpace 反馈"可能混淆 | 可考虑 `/pace-report` 或 `/pace-incident` |
| `/pace-role` | **3** | "role"可能被理解为角色权限管理，而非视角切换 | 可考虑 `/pace-view` 或 `/pace-lens` |
| `/pace-trace` | **2** | "trace"含义不明确——追踪什么？调用链？日志？ | 改为 `/pace-explain` 或 `/pace-why`，更直觉 |
| `/pace-theory` | **3** | "theory"暗示方法论，但开发者可能疑惑"理论有什么用" | 可考虑 `/pace-concepts` 或 `/pace-guide` |
| `/pace-test` | **4** | "test"直觉映射到测试，但其功能远超"跑测试" | 名称可保留，但需在 description 中突出"验收验证"而非仅"测试" |
| `/pace-guard` | **2** | "guard"可能被理解为安全守卫或权限守卫，而非风险预判 | 改为 `/pace-risk` 更直觉 |
| `pace-learn` | **N/A** | 系统内部 Skill，用户不可见 | 无需用户理解 |
| `pace-pulse` | **N/A** | 系统内部 Skill，用户不可见 | 无需用户理解 |

### 关键发现

1. **核心 5 个 Skill 平均 4.6 分**——命名质量高，新用户基本能猜出功能
2. **进阶 4 个 Skill 平均 3.75 分**——`/pace-retro` 依赖敏捷背景知识是主要扣分点
3. **专项 6 个 Skill 平均 3.2 分**——`/pace-trace`(2 分)和 `/pace-guard`(2 分)是最大问题
4. 整个 `/pace-` 命名空间一致，这是优势。但 17 个命令共享同一前缀增加了补全列表的扫描负担

---

## 3. 新用户上手路径地图

### 模拟场景：独立开发者首次使用 devpace 完成一个 CR 闭环

```
Step 0: 安装 Plugin
  动作: claude --plugin-dir /path/to/devpace
  认知负荷: LOW
  摩擦点: 无——标准 Claude Code 安装流程

        |
        v

Step 1: 初始化 /pace-init
  动作: /pace-init my-project → 回答项目描述
  认知负荷: LOW (仅 2 个问题)
  摩擦点: [Minor] 新用户不知道何时该用 full 参数
  正面: P1 零摩擦启动落地良好——30 秒内完成
  正面: "接下来会发生什么"预览降低了不确定性

        |
        v

Step 2: 首次开发 /pace-dev 或"帮我实现 X"
  动作: 说"帮我实现用户登录"
  认知负荷: LOW->MEDIUM (首次进入确认 + 意图检查点)
  摩擦点: [Major] 首次 opt-in 提问"跟踪还是快速改"可能让新用户困惑
    -> 新用户不理解"跟踪"意味着什么，缺乏上下文做判断
  摩擦点: [Minor] 意图检查点的范围确认可能让用户觉得"问题太多"
  正面: 自动创建 CR + 关联 PF，副产物非前置(P3)
  正面: 渐进教学首次附加解释

        |
        v

Step 3: 自治推进
  动作: Claude 自主编码、测试、Gate 1/2 自动执行
  认知负荷: LOW (用户基本不需要操作)
  摩擦点: [Minor] 用户可能不确定 Claude 在做什么——推进过程缺乏进度感知
  正面: 每个原子步骤 git commit 提供安全网(P4)
  正面: Gate 1/2 自动执行不打扰用户

        |
        v

Step 4: Review /pace-review
  动作: Claude 自动生成 Review 摘要 → 用户说"批准/打回"
  认知负荷: MEDIUM (需要理解摘要内容并做决策)
  摩擦点: [Minor] 简化审批机制的触发条件不直觉——用户不知道
    为什么有时跳过了 review 等待，有时没有
  正面: 摘要结构清晰（改了什么/为什么/影响/质量状态）
  正面: 简单回复即可操作（"批准"/"LGTM"/"打回"）

        |
        v

Step 5: 合并完成
  动作: 自动 merged + 连锁更新
  认知负荷: LOW
  摩擦点: [Minor] 首个 CR 回顾信息可能让用户觉得"说了太多"
  正面: 完成后自动更新功能树、state.md
  正面: 连锁更新全自动，用户无感
```

### 路径评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 总步骤数 | 5 步 | 合理，不过多 |
| 总认知负荷 | LOW->MEDIUM | 主要集中在 Step 2（首次 opt-in）和 Step 4（Review 决策） |
| 最大摩擦点 | Step 2 | 首次 opt-in 对话缺乏上下文，新用户不知道"跟踪"意味着什么 |
| P1 达标 | 是 | init 确实 30 秒内完成 |
| 闭环感知 | 部分 | 用户能感知"创建->开发->审批->完成"，但不一定理解背后的价值链 |

### 新用户最可能卡住的地方

1. **"跟踪还是快速改"决策点**（Step 2）：新用户缺乏足够信息判断应该选哪个。建议默认跟踪，只在用户主动说"快速改"时跳过
2. **不知道有哪些命令**：17 个 Skill 但只展示核心 5 个。如果用户需要变更需求但不知道 `/pace-change` 存在，可能会困惑
3. **从探索模式到推进模式的切换**：双模式概念本身增加了认知负担。用户可能不理解为什么有时候修改代码会触发"要跟踪吗"

---

## 4. P1-P7 原则审计表

> 注意：以 design.md §2 的权威定义为准。

### design.md 原则编号对照

| design.md # | 原则名 | team-lead 描述中的对应 |
|-------------|--------|----------------------|
| P1 | 零摩擦接入 | P1 零摩擦启动 |
| P2 | 渐进式暴露 | P3 渐进暴露 |
| P3 | 副产物非前置 | P2 副产物非前置 |
| P4 | 容错恢复 | P4 容错恢复 |
| P5 | 自由探索 | （描述为"节奏可感知"，实际 design.md 为"自由探索"） |
| P6 | 分级输出 | （描述为"单入口原则"，实际 design.md 为"分级输出"） |
| P7 | Git 为源 | （描述为"反馈即时性"，实际 design.md 为"Git 为源"） |

### 逐条审计

#### P1 零摩擦接入 — 评分：4.5/5

**设计承诺**：用户说自然语言就能工作，不要求先创建结构化数据。

**落地情况**：
- `/pace-init` 最小模式仅问 2 个问题（项目名+描述），30 秒内完成 -- 达标
- 自然语言触发推进模式（"帮我实现 X"）-- 达标
- CR 自动创建，用户不需要知道 CR 存在 -- 达标
- `--from` 参数支持从已有文档快速导入 -- 超预期

**扣分点**：
- 首次进入推进模式时的 opt-in 确认增加了一个决策点（-0.3）
- `/pace-init full` 的 6 步引导在某些场景下信息收集过多（-0.2）

#### P2 渐进式暴露 — 评分：3.5/5

**设计承诺**：日常只看 1 行摘要，按需展开。

**落地情况**：
- `/pace-status` 默认 3 行概览，`detail`/`tree` 按需展开 -- 达标
- 命令分层（核心/进阶/专项）-- 达标
- 渐进教学（首次触发时 1 句解释，终身只教 1 次）-- 良好
- 三层渐进透明（表面/中间/深入）-- 设计完善

**扣分点**：
- `/pace-test` 有 10+ 子命令，新用户看到完整列表认知负荷过高（-0.8）——严重违反 P2
- `/pace-release` 有 12 个子命令（6 日常+6 单独），虽然标记"可选"但子命令数量仍然吓人（-0.4）
- `/pace-status` 有 11 种参数（含 5 种角色视角），选择困难（-0.3）

#### P3 副产物非前置 — 评分：4.5/5

**设计承诺**：结构化数据是工作的自动产出，不要求先填写。

**落地情况**：
- BR->PF->CR 价值树在工作过程中自动生长 -- 达标
- 度量数据（dashboard.md）在 retro 时自动生成 -- 达标
- project.md 功能树在首个 CR 创建时自动生成 -- 达标
- 迭代计划、发布记录等目录按需创建 -- 达标

**扣分点**：
- `/pace-init full` 模式要求预先填写业务目标和 MoS，这与"副产物非前置"存在张力 -- 但作为可选项，影响较小（-0.5）

#### P4 容错恢复 — 评分：4/5

**设计承诺**：任何时刻中断无缝继续。

**落地情况**：
- 每个原子步骤 git commit + 更新 state.md -- 达标
- 质量检查幂等（重跑无副作用）-- 达标
- 会话结束自动保存 checkpoint -- 达标
- state.md 格式损坏自愈 -- 达标
- paused 状态保留全部工作成果 -- 达标

**扣分点**：
- inline 回退（fork 不可用时）丢失 Agent Memory，跨会话经验不持久化（-0.5）
- 新会话恢复时，如果 state.md 内容不够详细，恢复精度可能降低（-0.5）

#### P5 自由探索 — 评分：4.5/5

**设计承诺**：默认自由，正式推进时才走流程。

**落地情况**：
- 探索模式默认，不受状态机/阻塞关系约束 -- 达标
- 探索模式不修改 .devpace/（硬约束）-- 达标
- 推进模式需显式 opt-in -- 达标
- 关注点引导（架构/调试/评估）自动推断，不需声明 -- 超预期

**扣分点**：
- 探索模式下如果用户编辑了代码，可能触发推进模式提醒，略显打断（-0.5）

#### P6 分级输出 — 评分：4/5

**设计承诺**：默认简洁，按需展开。

**落地情况**：
- 步骤完成 1 句话，会话结束 3-5 行，追问展开 -- 达标
- 推理后缀 <=15 字 -- 达标
- 自适应会话结束（无修改=不执行，简单=1 行，标准=3 行，复杂=5 行）-- 达标
- 三层透明模型（表面/中间/深入）-- 良好

**扣分点**：
- `/pace-retro` 完整回顾报告可能信息量过大（四维度报告+改进建议+经验沉淀）（-0.5）
- 节奏健康度检测信号虽有上限（每会话 3 条），但与渐进教学叠加可能导致信息过载（-0.5）

#### P7 Git 为源 — 评分：5/5

**设计承诺**：不重复记录 Git 已有信息。

**落地情况**：
- CR 只记分支名，不记 commit hash -- 达标
- 需要 commit 详情时通过 git log 查询 -- 达标
- 质量检查只记 pass/fail，不记完整输出 -- 达标
- 度量从事件表+Git 历史聚合 -- 达标

无扣分点。

### 原则审计汇总

| 原则 | 评分 | 主要问题 |
|------|------|---------|
| P1 零摩擦接入 | 4.5/5 | 首次 opt-in 增加决策成本 |
| P2 渐进式暴露 | 3.5/5 | /pace-test 和 /pace-release 子命令过多 |
| P3 副产物非前置 | 4.5/5 | full 模式与原则有张力 |
| P4 容错恢复 | 4/5 | inline 回退丢失 Agent Memory |
| P5 自由探索 | 4.5/5 | 代码编辑可能误触推进提醒 |
| P6 分级输出 | 4/5 | retro 报告信息量偏大 |
| P7 Git 为源 | 5/5 | 完美落地 |
| **平均** | **4.14/5** | |

---

## 5. 摩擦点清单

### Critical（阻碍用户完成核心流程或严重损害体验）

| # | 摩擦点 | 位置 | 影响 | 建议 |
|---|--------|------|------|------|
| C1 | **17 个 Skill 的认知过载** | 全局 | 新用户面对 `/pace-` 补全列表时被淹没，无法快速定位需要的功能 | (1) 在 init 完成后的"接下来"预览中只提核心 3 命令；(2) 自动补全按层级分组（核心->进阶->专项）；(3) 考虑合并功能边界模糊的 Skill |
| C2 | **/pace-test 子命令体系过度复杂** | `skills/pace-test/SKILL.md` | 10+ 子命令（accept/strategy/coverage/impact/report/generate/flaky/dryrun/baseline + 旧名兼容），严重违反 P2 渐进暴露 | (1) 默认只暴露核心 3 个（空参/accept/coverage）；(2) 其余子命令合并或隐藏到 `advanced` 子组；(3) 向后兼容名称不在 help 中展示 |
| C3 | **/pace-guard 和 /pace-trace 命名不直觉** | `skills/pace-guard/SKILL.md`, `skills/pace-trace/SKILL.md` | 用户想做风险分析时找不到命令（"guard"不映射"风险"），想知道 Claude 决策原因时找不到命令（"trace"不映射"为什么"） | `/pace-guard` 改名 `/pace-risk`；`/pace-trace` 改名 `/pace-why` 或 `/pace-explain` |

### Major（显著增加认知负荷或降低效率）

| # | 摩擦点 | 位置 | 影响 | 建议 |
|---|--------|------|------|------|
| M1 | **首次 opt-in "跟踪还是快速改"缺乏上下文** | `rules/devpace-rules.md §2` | 新用户不理解"跟踪"意味着什么（创建 CR？状态机？质量门？），无法做有效决策 | (1) 重写提问为："我来管理这次开发的进度和代码质量检查。要这样做，还是你只想快速改个东西？"——将"跟踪"具象化；(2) 或直接默认跟踪，仅在用户说"快速"时跳过 |
| M2 | **/pace-release 子命令数量过多** | `skills/pace-release/SKILL.md` | 12 个子命令（6 日常+6 单独），新用户看到列表会被吓退 | (1) 空参引导式向导已是最佳入口，应更突出推荐；(2) changelog/version/tag/notes/branch 合并到 `close --step` 或 `advanced` 子组 |
| M3 | **/pace-status 参数过多** | `skills/pace-status/SKILL.md` | 11 种参数（含 5 种角色视角），选择困难 | (1) 角色视角参数与 /pace-role 功能重叠——用户设置了 role 后 status 应自动适配，不需要 status 再接受角色参数；(2) 去掉 biz/pm/dev/tester/ops 参数，改为依赖 /pace-role 的状态 |
| M4 | **/pace-change 与自然语言变更检测的边界模糊** | `skills/pace-change/SKILL.md`, `rules/devpace-rules.md §9` | rules §9 定义了自动检测变更意图，/pace-change 是显式调用。两者关系不清晰——用户说"加一个功能"时是自动触发还是需要 /pace-change？ | 在 user-guide 中明确说明：自然语言触发 = 自动走 /pace-change 流程，/pace-change 是显式调用的等价物 |
| M5 | **推进模式中用户缺乏进度感知** | `skills/pace-dev/SKILL.md` Step 3 | Claude 自治推进时，用户不知道当前在做什么、进展到哪里。仅依赖 checkpoint 的 git commit 不够直觉 | (1) 每个主要阶段输出 1 句话进度（如"代码完成，正在跑测试..."）；(2) 长时间操作时用简短进度指示器 |
| M6 | **/pace-retro 与"回顾"概念的认知距离** | `skills/pace-retro/SKILL.md` | "retro"是敏捷术语，独立开发者可能不熟悉 | 在 /pace-next 的推荐中使用"回顾一下最近的工作"而非"运行 retro" |

### Minor（轻微不便或美化建议）

| # | 摩擦点 | 位置 | 影响 | 建议 |
|---|--------|------|------|------|
| m1 | **/pace-theory 子命令过多** | `skills/pace-theory/SKILL.md` | 14 个子命令（model/objects/spaces/rules/trace/topic/metrics/loops/change/mapping/decisions/vs-devops/why/all），作为教学工具信息过载 | 默认无参数的速查卡片已足够；其余子命令在速查卡片中以链接形式暴露 |
| m2 | **简化审批的触发条件对用户不透明** | `rules/devpace-rules.md §2` | 用户不知道为什么有时跳过 review 等待，有时没有。4 个条件（复杂度/Gate/漂移/文件数）用户看不见 | 简化审批时附加 1 句原因："变更很小且质量门一次通过，自动合并还是要看看？" |
| m3 | **/pace-test accept 与 /pace-review 的关系不清晰** | `skills/pace-test/SKILL.md`, `skills/pace-review/SKILL.md` | accept 提供验收证据辅助 Gate 2/3，但用户不知道什么时候该用 accept，什么时候直接 review 就够 | 在 /pace-review 输出中，如果 CR 没有 accept 证据，附加建议："运行 /pace-test accept 可以获得更详细的验收证据" |
| m4 | **`pace-learn` 和 `pace-pulse` 的存在让系统 Skill 数量膨胀** | `skills/pace-learn/SKILL.md`, `skills/pace-pulse/SKILL.md` | 虽然对用户不可见，但在内部增加了系统复杂度；如果 /pace- 补全列表意外展示了它们，会造成困惑 | 确认 `user-invocable: false` 能完全阻止补全列表展示 |
| m5 | **降级模式的引导时机可能打扰用户** | `skills/pace-change/SKILL.md` Step 5 | 无 .devpace/ 时执行后额外输出初始化引导，对已决定不用 devpace 的用户是噪声 | 初始化引导只在首次降级时输出，重复降级不再提醒 |
| m6 | **/pace-init full 与 /pace-init --from 的关系不清晰** | `skills/pace-init/SKILL.md` | 两者可以组合使用（`/pace-init myproject full --from prd.md`），但用户不知道可以这样 | 在 init 完成后的预览中提示 full 和 --from 的存在 |
| m7 | **风险管理的渐进暴露不够** | `skills/pace-guard/SKILL.md` | /pace-guard 有 5 个子命令（scan/monitor/trends/report/resolve），但 scan 是默认且最常用的，其余应按需暴露 | scan 结果中智能推荐已有实现，保持即可 |

---

## 6. 跨 Skill 一致性报告

### 6.1 输出格式一致性

| 维度 | 一致性评级 | 说明 |
|------|-----------|------|
| 摘要行数 | 良好 | 多数 Skill 输出 3-5 行摘要，/pace-next 限制 3 行/8 行 |
| ID 隐藏 | 良好 | 全局 NF6 约束统一执行，不暴露 CR-001 等 ID |
| 自然语言 | 良好 | 状态用"在做""等你审批"而非"developing""in_review" |
| 进度条/emoji | 部分一致 | /pace-status 有进度条和 emoji，其余 Skill 未统一 |

### 6.2 术语一致性

| 术语 | 使用情况 | 问题 |
|------|---------|------|
| CR/变更请求/任务 | 对用户统一为"任务"或"变更" | 一致 |
| PF/产品功能/功能 | 对用户统一为"功能" | 一致 |
| BR/业务需求/目标 | 对用户统一为"目标" | 一致 |
| Gate/质量门/质量检查 | SKILL.md 中混用 "Gate 1/2/3" 和 "质量检查" | **不一致**：用户指南用"质量门禁"，SKILL.md 部分用"Gate"，部分用"质量检查" |
| checkpoint | 内部概念，用户不直接接触 | 可接受 |
| 推进模式/advance mode | devpace-rules.md 中混用 "推进模式" 和 "advance mode" | **不一致**：应统一为中文"推进模式" |

### 6.3 子命令风格一致性

| Skill | 子命令风格 | 说明 |
|-------|-----------|------|
| `/pace-init` | 参数+flag（`full`、`--from`） | 混合风格 |
| `/pace-dev` | 自然语言参数 | 无子命令 |
| `/pace-status` | 名词参数（`detail`/`metrics`/`tree`/`chain`/角色） | 名词为主 |
| `/pace-change` | 动词参数（`add`/`pause`/`resume`/`reprioritize`/`modify`） | **动词为主** |
| `/pace-plan` | 名词/动词混合（`next`/`close`） | 混合 |
| `/pace-retro` | 动词参数（`update`） | 动词 |
| `/pace-release` | 动词参数（`create`/`deploy`/`verify`/`close`/`rollback`） | **动词为主** |
| `/pace-test` | 混合（`accept`/`strategy`/`coverage`/`impact`/`report`/`generate`/`flaky`/`dryrun`/`baseline`） | **严重不一致**：动词(accept/generate)、名词(strategy/coverage/report/baseline)、形容词(flaky)混合 |
| `/pace-guard` | 动词/名词混合（`scan`/`monitor`/`trends`/`report`/`resolve`） | 混合 |
| `/pace-next` | 名词参数（`detail`） | 简洁 |
| `/pace-role` | 角色标识 | 特殊 |
| `/pace-theory` | 名词参数（主题列表） | 名词为主 |
| `/pace-trace` | 名词参数（决策类型） | 名词为主 |

**发现**：子命令整体倾向"动词 = 操作型 Skill"（change/release/guard）和"名词 = 查询型 Skill"（status/theory/trace），这种区分是合理的。但 `/pace-test` 的子命令风格混乱是最大一致性问题。

### 6.4 model 选择一致性

| model | Skill |
|-------|-------|
| haiku | pace-status, pace-next, pace-role, pace-theory, pace-trace, pace-pulse |
| sonnet | pace-init, pace-release, pace-feedback, pace-test, pace-learn, pace-guard |
| opus | pace-review |
| 未指定（fork） | pace-dev, pace-change, pace-plan, pace-retro |

**评估**：model 选择与 Skill 复杂度匹配合理。只读查询用 haiku（成本低），操作型用 sonnet，关键审批用 opus。

### 6.5 降级模式一致性

| Skill | 降级处理 | 说明 |
|-------|---------|------|
| `/pace-change` | 有完整降级模式（无 .devpace/ 时基于代码库分析） | 最佳实践 |
| `/pace-guard` | 有降级模式（scan/monitor 可用，trends/report/resolve 不可用） | 良好 |
| `/pace-test` | 有降级模式（无 .devpace/ 时仅 Layer 1 可用） | 良好 |
| `/pace-next` | 检测后输出未初始化引导 | 良好 |
| `/pace-dev` | 自动创建 CR | 非降级——功能完整 |
| 其他 Skill | 大多数假定 .devpace/ 存在 | 需要评估是否需要降级支持 |

**发现**：降级模式仅在部分 Skill 中实现，一致性中等。核心路径（dev/change/test/guard/next）已覆盖，进阶 Skill 未覆盖可以接受。

---

## 7. Top 10 改进建议

按用户影响排序（1 = 最高影响）：

### 1. 简化 /pace-test 子命令体系（Critical）

**影响**：所有使用测试功能的用户。

**现状**：10+ 子命令，向后兼容旧名增加混乱。SKILL.md 的推荐流程（`strategy -> generate -> coverage -> 无参数 -> accept -> report`）本身就是认知负担。

**建议**：
- 默认暴露 3 个：无参数（跑测试）、`accept`（验收验证）、`coverage`（覆盖分析）
- 其余合并为 `advanced`（`generate`/`flaky`/`dryrun`/`baseline`）和 `report`
- `strategy` 合并到 `coverage` 中（先看覆盖再建议策略是自然流）
- `impact` 合并到无参数运行中（变更后运行测试时自动分析影响）
- 移除 help 中的向后兼容名称展示

### 2. /pace-guard 改名为 /pace-risk（Critical）

**影响**：风险管理功能的可发现性。

**现状**："guard"不映射"风险"，用户说"分析一下风险"时不会想到 `/pace-guard`。

**建议**：直接改名为 `/pace-risk`。保留 `/pace-guard` 作为内部别名兼容。

### 3. /pace-trace 改名为 /pace-why（Critical）

**影响**：透明度功能的可发现性。

**现状**："trace"对开发者暗示"调用链追踪"而非"决策解释"。

**建议**：改名为 `/pace-why`，完美对应用户自然语言"为什么这样做"。

### 4. 重写首次 opt-in 提问（Major）

**影响**：所有新用户的首次体验。

**现状**："我来跟踪这个变更，还是只是快速改个东西？"——"跟踪"语义不明。

**建议**：改为"我来管理这次开发的进度和代码质量检查。要这样做，还是你只想快速改个东西？"将抽象的"跟踪"替换为具体的"进度管理+质量检查"。

### 5. /pace-status 去掉角色视角参数（Major）

**影响**：减少 /pace-status 参数膨胀，强化 /pace-role 角色。

**现状**：/pace-status 接受 `biz/pm/dev/tester/ops` 参数，与 `/pace-role` 功能重叠。

**建议**：
- 去掉 /pace-status 的 5 个角色参数
- 当 /pace-role 设置了角色时，/pace-status 自动适配视角
- 减少用户的选择成本，同时强化 /pace-role 的存在感

### 6. /pace-release 子命令分组（Major）

**影响**：减少 /pace-release 认知负荷。

**现状**：12 个子命令平铺展示。

**建议**：
- 空参引导向导作为唯一推荐入口（已实现，但需更突出）
- `changelog`/`version`/`tag`/`notes`/`branch` 合并为 `close` 的 `--step` 选项
- `rollback` 保持独立（紧急操作需要快速可达）
- help 中只展示：create/deploy/verify/close/status/rollback + "空参引导"

### 7. 增加推进模式的进度感知（Major）

**影响**：改善所有使用推进模式的用户体验。

**现状**：Claude 自治推进时用户不知道进展到哪里。

**建议**：
- 每个主要状态转换（created->developing->verifying->in_review）输出 1 句话
- Gate 1/2 执行时附加简短信号："质量检查通过，进入验证阶段..."
- 长时间操作（>30s）输出进度指示

### 8. 统一术语：Gate vs 质量门 vs 质量检查（Minor）

**影响**：提升专业感和一致性。

**现状**：用户指南用"质量门禁"，SKILL.md 用"Gate"，rules 用"质量检查"。

**建议**：
- 面向用户：统一为"质量检查"（日常交互中）和"质量门禁"（正式文档中）
- 面向开发者/内部：继续使用 "Gate 1/2/3"
- 在 user-guide 中添加术语对照表

### 9. /pace-retro 增加自然语言触发的可发现性（Minor）

**影响**：提升非敏捷用户的可发现性。

**现状**："retro"是敏捷术语，独立开发者可能不熟悉。

**建议**：
- /pace-next 推荐时使用自然语言"回顾最近的工作"而非"运行 retro"
- description 中增加更多中文触发词如"总结""分析进展"

### 10. 首次初始化后的"下一步"预览优化（Minor）

**影响**：提升新用户留存。

**现状**：init 完成后展示"接下来你可以：说'帮我实现 X' / 说'加一个 Y' / 说'做到哪了'"。

**建议**：
- 将预览缩减为 1 个最佳下一步："现在就说你想做什么，我来帮你推进。"
- 移除命令暗示，强化自然语言交互
- 如果项目已有代码，自动分析并建议："项目看起来是 [类型]，需要我帮忙 [改进/新增/修复] 什么吗？"

---

## 附录 A：审计方法

本审计基于以下文件的逐行阅读：

1. 全部 17 个 `skills/*/SKILL.md`
2. `docs/design/design.md` §2 UX 原则
3. `docs/user-guide.md` 完整内容
4. `rules/devpace-rules.md` 完整内容

审计视角：首次使用 devpace 的独立开发者（有 2-3 年开发经验，使用过 Git 和基本的项目管理工具，但没有敏捷/Scrum 背景，对 BizDevOps 方法论不了解）。

## 附录 B：信息密度评估

### 高密度 Skill（可能信息过载）

| Skill | 子命令数 | 信息量评级 | 新用户友好度 |
|-------|---------|-----------|-------------|
| `/pace-test` | 10+ | 过高 | 低 |
| `/pace-release` | 12 | 过高 | 低（空参引导弥补） |
| `/pace-theory` | 14 | 过高 | 中（速查卡片弥补） |
| `/pace-status` | 11 | 偏高 | 中（默认概览弥补） |

### 低密度 Skill（信息量合适）

| Skill | 子命令数 | 信息量评级 | 新用户友好度 |
|-------|---------|-----------|-------------|
| `/pace-init` | 3 | 合适 | 高 |
| `/pace-dev` | 1 | 合适 | 高 |
| `/pace-review` | 1 | 合适 | 高 |
| `/pace-next` | 2 | 合适 | 高 |
| `/pace-role` | 6 | 合适 | 高 |

### 新用户 vs 老用户信息需求差异

| 维度 | 新用户需要 | 老用户需要 | 当前满足 |
|------|-----------|-----------|---------|
| 命令发现 | 核心 3-5 个命令 | 全部命令+子命令 | 部分（分层但不够渐进） |
| 概念理解 | "做什么"而非"为什么" | "为什么"和定制 | 良好（渐进教学） |
| 输出详细度 | 极简 | 可配置 | 良好（分级输出） |
| 术语 | 自然语言 | 可接受缩写/ID | 良好（NF6） |
| 错误恢复 | 引导式 | 自行解决 | 中等（自愈但反馈不够） |
