# DevPace Hook 体系：用户旅程全景分析

> **日期**：2026-04-07
> **目的**：梳理 devpace 项目中 11 个全局 Hook + 5 个 Skill 级 Hook 在用户旅程各阶段的作用

---

## 一、全景概览

devpace 共注册 **16 个 Hook**（11 全局 + 5 Skill 级），覆盖 **9 种事件类型**，形成五层协作架构：

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: 会话生命周期管理                                │
│  session-start → session-stop → pre-compact → session-end │
├─────────────────────────────────────────────────────────┤
│  Layer 2: 意图路由层                                      │
│  skill-eval (UserPromptSubmit)                            │
├─────────────────────────────────────────────────────────┤
│  Layer 3: 写入守卫层 (PreToolUse)                         │
│  全局: pre-tool-use  |  Skill级: 5 个 scope-check          │
├─────────────────────────────────────────────────────────┤
│  Layer 4: 写入后响应层 (PostToolUse, 异步)                 │
│  post-cr-update | post-schema-check | pulse-counter | sync-push │
├─────────────────────────────────────────────────────────┤
│  Layer 5: 异常处理层                                      │
│  post-tool-failure | subagent-stop                        │
└─────────────────────────────────────────────────────────┘
```

### Exit Code 语义

| Exit Code | 含义 | 效果 |
|-----------|------|------|
| **0** | 建议性 (Advisory) | 输出 ACTION 指令引导 Claude，不阻断操作 |
| **2** | 阻断性 (Blocking) | 直接拒绝工具调用，Claude 无法绕过 |

### 设计原则

- **双层执行模型**：exit 2 仅用于"铁律"级安全保障；其余一律 exit 0 建议性引导
- **消息前缀协议**：所有输出使用 `devpace:<tag>` 前缀，便于日志分类和 Claude 理解来源
- **零依赖架构**：所有 .mjs 仅用 Node.js 内置模块，.sh 仅用 POSIX 标准命令
- **噪音控制**：状态缓存消除重复提醒、时间窗口避免双重提醒、仅关键时机输出

---

## 二、用户旅程各阶段 Hook 作用

### 阶段 1：会话启动

```
用户打开 Claude Code → SessionStart 事件触发
```

#### session-start.sh

| 属性 | 值 |
|------|---|
| 事件 | `SessionStart` |
| Exit Code | 始终 `0` |
| 角色 | **会话入口锚点** |

**逻辑**：检查 `.devpace/state.md` 是否存在

- **存在**：输出 `devpace:session-start Active project detected. ACTION: Read .devpace/state.md to restore project context and identify active CRs; then resume in-progress work.`
- **不存在**：输出 `No active devpace project`

**用户体验**：新会话零手动解释——Hook 自动注入恢复指令，Claude 读 state.md 后用 1 句话报告当前状态。

---

### 阶段 2：用户输入意图路由

```
用户输入自然语言 → UserPromptSubmit 事件触发
```

#### skill-eval.mjs

| 属性 | 值 |
|------|---|
| 事件 | `UserPromptSubmit` |
| Exit Code | 始终 `0` |
| 角色 | **智能意图路由器** |

**前置门控**：
- Gate 1：`.devpace/state.md` 必须存在
- Gate 2：跳过已显式使用 `/pace-*` 的命令
- Gate 3：跳过纯技术命令（git, npm, docker 等）

**双路径路由**：

| 路径 | 条件 | 行为 |
|------|------|------|
| **Path A 精确匹配** | 用户输入命中 19 个 Skill 的高置信度触发模式 | 直接建议调用对应 Skill |
| **Path B 强制评估** | 多匹配或零匹配+项目工作信号词 | 列出候选 Skill，要求 Claude 选择 |

**输出前缀**：`devpace:skill-route`（单匹配）、`devpace:forced-eval`（多匹配/零匹配）

**用户体验**：用户无需记住 19 个 `/pace-*` 命令——自然语言输入自动映射到最合适的 Skill。

---

### 阶段 3：开发执行中的写入守卫

```
Claude 调用 Write/Edit → PreToolUse 事件触发
```

#### 3.1 pre-tool-use.mjs（全局守卫）

| 属性 | 值 |
|------|---|
| 事件 | `PreToolUse`，匹配 `Write\|Edit` |
| Exit Code | `0`（建议）或 `2`（阻断） |
| 角色 | **铁律守卫——整个系统最核心的安全机制** |

**三层检查**：

| 层级 | 检查内容 | 条件 | Exit Code |
|------|---------|------|-----------|
| **ENFORCEMENT 1** | 探索模式保护 | 文件在 `.devpace/` 下 + 非推进模式 → 阻断 state.md 修改和 CR 状态升级 | **2（阻断）** |
| **ENFORCEMENT 2** | Gate 3 铁律 | CR 状态为 `in_review` + 写入内容试图改为 `approved` | **2（阻断）** |
| **ADVISORY** | 质量门提醒 | developing→提醒 Gate 1；verifying→提醒 Gate 2；in_review→提醒需人类批准 | 0（建议） |

**输出消息**：
- 阻断：`devpace:blocked ...`（stderr）
- 建议：`devpace:gate-reminder ...`（stdout）

**关键意义**：Gate 3 不是靠 prompt 约束，而是在工具调用层面物理阻断——即使 Claude 无视规则也无法自动批准 CR。

#### 3.2 Skill 级 scope-check（5 个）

| Hook | 所属 Skill | 允许范围 | Exit Code |
|------|-----------|---------|-----------|
| `pace-init-scope-check.mjs` | /pace-init | `.devpace/`、根 `CLAUDE.md`、`.gitignore` | 0 或 **2** |
| `pace-init-reset-guard.mjs` | /pace-init | 检查 `.reset-confirmed` 标记才允许删除 `.devpace/` | 0 或 **2** |
| `pace-dev-scope-check.mjs` | /pace-dev | Scope Drift 检测——写入目标是否在 CR 声明范围内 | 始终 0（建议） |
| `pace-biz-scope-check.mjs` | /pace-biz | 仅 `.devpace/` 目录 | 0 或 **2** |
| `pace-review-scope-check.mjs` | /pace-review | `.devpace/` 放行，非 `.devpace/` 输出建议 | 始终 0（建议） |

**分层守卫模型**：全局 Hook 执行通用铁律，Skill 级 Hook 执行特定范围约束——两层独立运行，最严格者胜出。

---

### 阶段 4：写入后的自动响应

```
Write/Edit 成功 → PostToolUse 事件触发（4 个 Hook 异步并行）
```

#### 4.1 post-cr-update.mjs

| 属性 | 值 |
|------|---|
| 事件 | `PostToolUse`，异步 |
| Exit Code | 始终 `0` |
| 角色 | **CR 生命周期事件响应器** |

**5 种事件检测与响应**：

| 检测条件 | 输出前缀 | ACTION |
|---------|---------|--------|
| CR 状态变为 `merged` | `devpace:post-merge` | 更新 state.md、同步外部状态、萃取经验 |
| 新 CR 创建 + 有 sync-mapping + 无外部关联 | `devpace:auto-sync` | 建议 auto-link/auto-create 外部 Issue |
| 事件表最新为 `gate1_fail`/`gate2_fail` | `devpace:learn-trigger` | 修复后萃取教训 |
| 事件为 `rejected` | `devpace:learn-trigger` | 分析认知差距 |
| Gate 结果 + 有外部关联 | `devpace:gate-sync` | 推送结果到外部平台 |

#### 4.2 post-schema-check.mjs

| 属性 | 值 |
|------|---|
| 事件 | `PostToolUse`，异步 |
| Exit Code | 始终 `0` |
| 角色 | **数据质量守卫** |

**可校验类型**：`state.md`、`project.md`、`CR-NNN.md`、`PF-NNN.md`、`BR-NNN.md`

**逻辑**：调用 `scripts/validate-schema.mjs` 校验写入文件，不通过时输出具体错误 + 对应 Schema 参考路径。

**输出**：`devpace:schema-check <filename> 校验不通过（N error, M warning）：<issues>. ACTION: 重新读取文件，按错误逐一修复...`

#### 4.3 pulse-counter.mjs

| 属性 | 值 |
|------|---|
| 事件 | `PostToolUse`，异步 |
| Exit Code | 始终 `0` |
| 角色 | **节奏健康哨兵** |

**两个维度的监控**：

| 维度 | 触发条件 | 输出 |
|------|---------|------|
| **写入量提醒** | 每 10 次写入（且 pace-pulse 5 分钟内未运行） | 建议执行 `/pace-status` |
| **卡顿检测** | 同一 CR 被写入 5+ 次但状态未变 | `devpace:stuck-warning`（建议检查阻塞项）+ `devpace:struggle-signal`（标记可能的环境缺陷） |

**持久化文件**：`.devpace/.pulse-counter`、`.devpace/.pulse-cr-writes`、`.devpace/.pulse-last-run`

#### 4.4 sync-push.mjs

| 属性 | 值 |
|------|---|
| 事件 | `PostToolUse`，异步 |
| Exit Code | 始终 `0` |
| 角色 | **外部集成同步器** |

**触发条件**：CR 文件被写入 + sync-mapping 已配置 + CR 有外部关联 + 状态实际发生变化

**噪音控制**：使用 `.devpace/.sync-state-cache` 缓存上次状态，相同状态静默退出

| 状态变化 | ACTION |
|---------|--------|
| → `merged` | 建议执行 `/pace-sync` 关闭外部 Issue |
| → 其他 | 建议同步状态到外部系统 |

---

### 阶段 5：长会话上下文压缩

```
Claude 上下文窗口 ~95% → PreCompact 事件触发
```

#### pre-compact.sh

| 属性 | 值 |
|------|---|
| 事件 | `PreCompact` |
| Exit Code | 始终 `0` |
| 角色 | **长会话连续性保障** |

**输出结构**（以 `=== DEVPACE RECOVERY CONTEXT ===` 包裹）：

1. **铁律提醒** (IR-1 到 IR-5)：state.md 是唯一锚点、先读后写、质量门不可跳过
2. **当前状态摘要**：从 state.md 提取"进行中"和"下一步"
3. **活跃 CR 信息**：扫描 backlog 找到 developing/verifying/in_review 的 CR，提取执行快照恢复建议

**用户体验**：上下文压缩后 Claude 仍能找回工作状态，长会话不中断。

---

### 阶段 6：每轮响应结束

```
Claude 每次响应完成 → Stop 事件触发
```

#### session-stop.sh

| 属性 | 值 |
|------|---|
| 事件 | `Stop` |
| Exit Code | 始终 `0` |
| 角色 | **会话保存提醒器** |

**逻辑**：仅在 `stop_reason === "end_turn"` 时输出；带 `stop_hook_active: true` 防止无限循环。

**输出**：`devpace:stop 检测到 end_turn 事件。ACTION: 若即将结束会话则更新 .devpace/state.md 并输出会话摘要；若仍在继续则忽略此提醒。`

---

### 阶段 7：会话结束

```
用户退出 Claude → SessionEnd 事件触发
```

#### session-end.sh

| 属性 | 值 |
|------|---|
| 事件 | `SessionEnd` |
| Exit Code | 始终 `0` |
| 角色 | **会话出口守门人** |

**逻辑**：扫描 `.devpace/backlog/CR-*.md`，对每个"状态为 developing/verifying 且复杂度为 L/XL"的 CR 输出刷新执行快照的提醒。

**输出**：`devpace:session-end CR-NNN 是 L/XL 级活跃 CR。ACTION: 读取该 CR 文件刷新执行快照的恢复建议；若本次会话已完成该 CR 则忽略。`

---

### 阶段 8：异常处理

#### post-tool-failure.mjs

| 属性 | 值 |
|------|---|
| 事件 | `PostToolUseFailure`，匹配 `Write\|Edit` |
| Exit Code | 始终 `0` |
| 角色 | **失败恢复顾问** |

**触发条件**：Write/Edit 失败 + 项目处于推进模式

| 失败类型 | ACTION |
|---------|--------|
| CR 文件写入失败 | 检查状态字段一致性、补记 write_failed 事件、必要时 git checkout 恢复 |
| 其他 .devpace/ 文件失败 | 检查 state.md 一致性、恢复后重试 |

#### subagent-stop.mjs

| 属性 | 值 |
|------|---|
| 事件 | `SubagentStop` |
| Exit Code | 始终 `0` |
| 角色 | **子代理完整性审计员** |

**触发条件**：devpace 专属子代理（`pace-engineer`、`pace-pm`、`pace-analyst`）停止时

**三项一致性检查**：

| 检查 | 条件 | 含义 |
|------|------|------|
| Gate 记录完整性 | CR 为 verifying 但无 Gate 1 记录 | pace-engineer 可能中途中断 |
| state.md 一致性 | state.md 无"进行中"但 backlog 有 developing CR | state.md 未同步更新 |
| 聚合输出 | — | 一次性输出所有警告 |

---

## 三、用户旅程时间线图

```
会话启动                     用户操作中                                    会话结束
   │                            │                                           │
   ▼                            ▼                                           ▼
┌──────────┐  ┌──────────┐  ┌──────────────────────────────────┐  ┌──────────┐
│ session-  │  │ skill-   │  │        开发循环（可重复多次）        │  │ session- │
│ start.sh │→│ eval.mjs │→│                                    │→│ end.sh  │
│ 恢复上下文 │  │ 意图路由  │  │  Write/Edit 触发:                  │  │ L/XL CR │
└──────────┘  └──────────┘  │                                    │  │ 快照刷新 │
                             │  ┌─ pre-tool-use.mjs (守卫)        │  └──────────┘
                             │  │  + Skill scope-check (范围)     │       ▲
                             │  ▼                                 │       │
                             │  [写入执行]                          │  ┌──────────┐
                             │  │                                 │  │ session- │
                             │  ▼ (成功)          ▼ (失败)         │  │ stop.sh │
                             │  ┌─────────┐  ┌─────────────┐     │  │ 保存提醒 │
                             │  │4 个异步  │  │post-tool-   │     │  │(每轮触发)│
                             │  │PostTool  │  │failure.mjs  │     │  └──────────┘
                             │  │响应 Hook │  │失败恢复      │     │       ▲
                             │  └─────────┘  └─────────────┘     │       │
                             │                                    │  ┌──────────┐
                             │  上下文压缩时:                       │  │ pre-     │
                             │  ┌─ pre-compact.sh (注入恢复上下文)  │  │compact.sh│
                             │                                    │  │压缩前保护│
                             │  子代理结束时:                       │  └──────────┘
                             │  ┌─ subagent-stop.mjs (一致性审计) │
                             └──────────────────────────────────┘
```

---

## 四、Hook 统计汇总

### 按阻断/建议分类

| 类型 | 数量 | Hook |
|------|------|------|
| **可阻断（exit 2）** | 4 个 | pre-tool-use.mjs、pace-init-scope-check、pace-init-reset-guard、pace-biz-scope-check |
| **纯建议（exit 0）** | 12 个 | 其余全部 |

### 按同步/异步分类

| 类型 | 数量 | Hook |
|------|------|------|
| **同步（阻塞 Claude 等待结果）** | 8 个 | session-start、pre-tool-use、skill-eval、post-tool-failure、subagent-stop、pre-compact、session-stop、session-end |
| **异步（不阻塞 Claude）** | 4 个 | post-cr-update、post-schema-check、pulse-counter、sync-push |
| **Skill 级（随 Skill 执行）** | 5 个 | 5 个 scope-check |

### 按守护职责分类

| 职责域 | Hook | 保障目标 |
|--------|------|---------|
| **跨会话连续性** | session-start、session-stop、session-end、pre-compact | 上下文零丢失 |
| **质量门禁** | pre-tool-use（Gate 3 铁律 + 模式隔离） | 质量不可绕过 |
| **范围约束** | 5 个 Skill scope-check、pace-dev-scope-check（漂移检测） | 防止越界操作 |
| **数据完整性** | post-schema-check、post-tool-failure、subagent-stop | 状态文件格式正确、失败恢复、子代理一致性 |
| **流水线自动化** | post-cr-update | CR 生命周期关键节点自动触发下游管线 |
| **外部集成** | sync-push | BizDevOps 闭环同步 |
| **节奏健康** | pulse-counter | 卡顿/空转预警 |
| **意图路由** | skill-eval | 自然语言→Skill 自动映射 |

---

## 五、核心价值总结

devpace 的 Hook 体系本质上构建了一个 **"Agent 行为的操作系统"**：

| 层次 | 类比 | devpace Hook |
|------|------|-------------|
| 内核保护 | 操作系统内核态保护 | pre-tool-use.mjs（铁律，exit 2 阻断） |
| 系统调用拦截 | syscall hook | Skill scope-check（写入范围约束） |
| 进程调度 | 进程调度器 | skill-eval.mjs（意图→Skill 路由） |
| 文件系统校验 | fsck | post-schema-check.mjs（Schema 校验） |
| 事件总线 | 事件驱动中间件 | post-cr-update.mjs（状态变化→管线触发） |
| 会话管理 | 进程挂起/恢复 | session-start/stop/end + pre-compact |
| 健康监控 | watchdog | pulse-counter.mjs（卡顿检测） |
| IPC 同步 | 进程间通信 | sync-push.mjs（外部系统同步） |

**核心公式**：`Agent 产出质量 = 模型能力 × 环境质量`——Hook 是环境质量的执行层，将规则从"文本建议"升级为"机制保障"。
