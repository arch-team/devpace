# devpace 实施路线

> **职责**：定义实施阶段和里程碑。战略规划的事实来源。
>
> 操作跟踪（当前任务状态、变更记录、会话历史）见 [progress.md](progress.md)。

**定位**：docs/ 体系的**战略规划**——回答"分几个阶段、每阶段做什么"。将 requirements.md 的功能条目编排为分阶段的实施计划。

| 维度 | 说明 |
|------|------|
| 回答的问题 | 分几个阶段？每个阶段做什么？里程碑是什么？ |
| 上游输入 | requirements.md（需求条目排入阶段）、design.md（设计复杂度影响排期） |
| 下游消费 | progress.md（任务定义排入操作跟踪）、日常开发（里程碑完成时更新） |
| 更新时机 | 阶段完成、里程碑完成、新增/砍掉里程碑时 |
| 类别 | 项目管理——战略排期，不进入产品运行时 |
| 主要读者 | 所有参与者——需要理解"项目的全局规划" |

## 阶段总览

| 阶段 | 名称 | 目标 | 状态 |
|------|------|------|------|
| Phase 1 | MVP 核心 | 跑通工作流 + 跨会话 + 质量检查 + 变更管理 | ✅ 完成 |
| Phase 2 | 实战验证 | 在已有项目和新创建项目中完整验证 | ✅ 完成 |
| Phase 3 | 可移植性 | 第 2 个项目验证 + 度量体系 | ✅ 完成 |
| Phase 4 | 社区发布 | 文档完善 + 开源准备 | ✅ 完成 |
| Phase 5 | AI 主导管理 | Claude 从被动执行者转变为主动管理者 | ✅ 完成 |
| Phase 6 | 基础扩展 | CR 类型扩展 + 角色意识 + 缺陷管理 | ✅ 完成 |
| Phase 7 | 发布管理 | Release 实体 + 部署追踪 + DORA 度量 | ✅ 完成 |
| Phase 8 | 运维反馈与集成 | Ops 闭环 + 外部工具集成 + 完整 DORA | ✅ 完成 |
| Phase 9 | 验证与文档 | 文档更新 + 迁移验证 | ✅ 完成 |
| Phase 10 | 开源借鉴与增强 | 状态机增强 + 变更管理增强 + 初始化增强 | ✅ 完成 |
| Phase 11 | Linear AI 深度借鉴 | 溯源标记 + 三层透明 + 渐进自主性 + 反应式调优 | ✅ 完成 |
| Phase 12 | 审查质量与探索增强 | 累积 Diff 审查 + Gate 反思 + 探索关注点引导 | ✅ 完成 |
| Phase 13 | ECC 深度借鉴 | Hook 跨平台 + 检查项依赖 + Model Tiering + 交接协议 + 置信度 + 上下文管理 | ✅ 完成 |
| Phase 14 | BMAD 深度借鉴 | 对抗审查 + 规模自适应 + 步骤隔离 + 技术约定 + Agent 沟通风格 + 智能导航 | ✅ 完成 |
| Phase 15 | 测试策略与验收验证 | /pace-test 三层测试管理（基础执行 + 策略管理 + AI 验收） | ✅ 完成 |
| Phase 16 | 企业级扩展 | DORA 代理指标 + 跨项目经验复用 + CI/CD 自动感知 | ✅ 完成 |
| Phase 17 | Risk Fabric 风险织网 | /pace-guard + risk-format + 嵌入集成 + 分级自主 | ✅ 完成 |
| Phase 18 | 外部同步 MVP | 手动同步 + GitHub MVP（pace-sync setup/link/push/status） | ✅ 完成 |
| Phase 19 | 自动推送与多平台 | 自动推送 + 治理集成 + Linear/Jira 扩展 | 待开始 |
| Phase 20 | 双向同步与 AI 冲突 | 入站事件 + 冲突检测 + AI 解决 | 待开始 |
| Phase 21 | BR 上游业务规划域 | Opportunity/Epic/BR 溢出 + /pace-biz Skill + 端到端追溯 | 🔄 进行中 |

---

## Phase 1：MVP 核心

**目标**：Plugin 骨架完成，核心 Skills 可用，协议规则覆盖正常流程和变更场景。

**对应 OBJ**：OBJ-1, OBJ-2, OBJ-3, OBJ-4

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M1.1 | 项目骨架 + 核心规则 | ✅ 完成 | plugin.json, CLAUDE.md, protocol, schema, templates |
| M1.2 | 基础 Skills | ✅ 完成 | pace-init, pace-status, pace-dev, pace-review, pace-retro |
| M1.3 | 变更管理能力 | ✅ 完成 | protocol §9 + pace-change skill + paused 状态 + 变更记录 |
| M1.4 | 项目文档体系 | ✅ 完成 | vision, requirements, roadmap, design 更新 |

### 任务定义

> 实时状态见 [progress.md](progress.md) "当前任务"表。

| 任务 | 关联里程碑 | 关联条目 |
|------|----------|---------|
| 更新 protocol §9 变更管理 | M1.3 | OBJ-4, S4-S7, F2.1-F2.3 |
| 创建 pace-change skill | M1.3 | OBJ-4, S4-S7, F2.7 |
| 更新 workflow 模板增加 paused | M1.3 | OBJ-4, S5, F2.4 |
| 更新 iteration 模板增加变更记录 | M1.3 | OBJ-4, S4-S7, F2.1-F2.3 |
| 更新 design.md 补充变更管理方案 | M1.4 | OBJ-4, design.md §7 |
| 补强 rules 会话结束协议（A.1） | M1.4 | OBJ-2, S10, F1.2 |
| 补强 rules merged 连锁更新（A.2） | M1.4 | OBJ-1, S2, F1.3 |

---

## Phase 2：实战验证

**目标**：在已有项目（diagnostic-agent-framework）和新创建项目中验证全部 MVP 能力。

**对应 OBJ**：OBJ-1, OBJ-2, OBJ-3, OBJ-4, OBJ-5, OBJ-6, OBJ-7

### 验证计划

| # | 验证项 | 方法 | 通过标准 |
|---|--------|------|---------|
| V2.1 | /pace-init 初始化 | 在 diagnostic-agent-framework 运行 | .devpace/ 结构完整 |
| V2.2 | 完整 CR 工作流 | 用 analyzer 提取任务走 created→merged | 全流程自动化 |
| V2.3 | 跨会话恢复 | 中断 3 次，每次验证自动恢复 | 零手动解释 |
| V2.4 | 质量检查自动执行 | 故意引入不符合质量检查的代码 | 质量检查拦截，不跳过 |
| V2.5 | 需求插入 | 中途加入新 PF | 影响分析准确，功能树更新 |
| V2.6 | 需求暂停 | 暂停进行中的 CR | 工作保留，依赖调整 |
| V2.7 | 优先级调整 | 重排迭代优先级 | state.md 和迭代计划更新 |
| V2.8 | Code Review 流程 | CR 进入 in_review 后验证审批/打回流程 | 审批→merged 自动更新；打回→developing 并记录原因 |
| V2.9 | 优于手动方案（OBJ-5） | 同一项目 3 次会话中断，对比 devpace vs 手动 CLAUDE.md 方案 | devpace 恢复上下文所需用户纠正次数更少 |
| V2.10 | 渐进丰富自然（OBJ-6） | 观察从 1 个 CR 增长到 3+ CR 的过程 | 用户未主动查询或修改 devpace 生成的结构文件 |
| V2.11 | 会话结束保存 | 工作到一半说"结束"，下次会话验证自动恢复 | state.md 已更新、CR 文件最新、输出 3-5 行总结 |
| V2.12 | 理论参考（/pace-theory） | 在不同项目阶段调用 /pace-theory | 返回与当前阶段相关的理论指导，不修改状态文件 |
| V2.13 | 状态分级输出（/pace-status） | 分别测试默认/detail/tree 三级输出 | 每级输出粒度正确，默认 ≤3 行 |
| V2.14 | 新项目初始化 | 创建空项目目录，运行 /pace-init | .devpace/ 结构完整，对话引导正常，价值功能树合理 |
| V2.15 | 新项目完整 CR 生命周期 | 在新初始化的项目中走完 created→merged | BR→PF→CR 全链路走通，state.md 记录准确 |
| V2.16 | 新项目跨会话连续性 | 新项目中中断后新会话恢复 | 自动读取 .devpace/ 状态，零手动解释恢复 |

---

## Phase 3：可移植性 + 加固

**目标**：缓解战略风险，建立用户入口，第 2 个项目验证可移植性，度量体系可用。

**对应 OBJ**：OBJ-7, OBJ-8, OBJ-11

**前置条件**：Phase 2 全部验证通过

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M3.1 | 战略风险缓解 | ✅ 完成 | 变更管理独立入口验证 + 质量门 Hook 完整实现 |
| M3.2 | 用户入口 | ✅ 完成 | README.md（面向用户）+ Quickstart 路径 |
| M3.3 | 可移植性验证 | ✅ 完成 | 第 2 个项目完整验证 + 度量数据 + 规模验证 |

### 任务定义

> 实时状态在 Phase 3 启动时排入 [progress.md](progress.md)。

**M3.1 战略风险缓解**

| 任务 | 关联条目 | 说明 |
|------|---------|------|
| 变更管理独立入口验证 | OBJ-11, S14, F2.8 | 无 .devpace/ 初始化场景下 /pace-change 的降级模式测试（design.md §7 渐进降级） |
| 质量门 Hook 完整实现 | OBJ-3, design.md §6 | Gate 1/2 自动拦截的 Hook 层实现，补齐 session hook 之外的质量自动化 |
| 异常中断容错测试 | NF3 | 写入中断、网络断连等异常场景的恢复验证 |

**M3.2 用户入口**

| 任务 | 关联条目 | 说明 |
|------|---------|------|
| 用户 README.md | OBJ-9, S13, F4.1 | 面向新用户：是什么、为什么、怎么开始。应引用 T13 对比数据 |
| Quickstart 路径设计 | OBJ-9, S13, F4.2, NF1 | "5 分钟跑通 /pace-init"的完整引导路径 |

**M3.3 可移植性验证**

| 任务 | 关联条目 | 说明 |
|------|---------|------|
| 选择第 2 个验证项目 | OBJ-7 | 应与 DAF 差异大（不同语言/规模/迭代节奏） |
| 第 2 个项目 /pace-init + CR 全流程 | OBJ-7, NF4 | 收集初始化耗时、适配工作量、首个 CR 完成时间 |
| pace-retro 端到端验证 | OBJ-8, S9, F3.4 | 明确数据提取逻辑，建立度量基准线，生成含基准对比的回顾报告 |
| state.md 规模验证 | NF2 | 10+ CR 场景下 state.md 是否仍 ≤15 行 |

---

## Phase 4：社区发布

**目标**：开源合规，社区引导完善，正式分发。

**对应 OBJ**：OBJ-9, OBJ-10

**前置条件**：Phase 3 可移植性验证通过

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M4.1 | 开源合规 | ✅ 完成 | LICENSE + CONTRIBUTING.md + CHANGELOG.md |
| M4.2 | 社区引导 | ✅ 完成 | 示例项目 + 用户指南 |
| M4.3 | 分发准备 | ✅ 完成 | Marketplace 配置增强 + 跨平台验证 + README 更新 |

### 任务定义

> 实时状态在 Phase 4 启动时排入 [progress.md](progress.md)。

**M4.1 开源合规**

| 任务 | 关联条目 | 说明 |
|------|---------|------|
| 添加 LICENSE | OBJ-9 | MIT（已在 plugin.json 声明） |
| 创建 CONTRIBUTING.md | OBJ-9 | 贡献指南：开发环境搭建、测试方法、PR 规范 |
| 创建 CHANGELOG.md | OBJ-9 | 版本变更记录，从 0.1.0 开始 |

**M4.2 社区引导**

| 任务 | 关联条目 | 说明 |
|------|---------|------|
| 示例项目 | OBJ-9 | 新用户学习的最快路径，包含从 init 到 merged 的完整示例 |
| 用户指南 | OBJ-9, OBJ-10 | 超越 README 的完整使用文档，覆盖全部 7 个 Skill |

**M4.3 分发准备**

| 任务 | 关联条目 | 说明 |
|------|---------|------|
| Marketplace 正式提交 | OBJ-9 | 从本地开发配置切换到正式发布配置 |
| 跨平台验证 | NF3 | Hook 脚本在 Linux/WSL 下的兼容性测试 |

---

## Phase 5：AI 主导管理

**目标**：Claude 从被动执行者转变为主动管理者，人类从指挥者转变为审批者。实现主动节奏管理、经验驱动决策、角色分离和生命周期扩展。

**对应 OBJ**：OBJ-1, OBJ-2, OBJ-3, OBJ-8

**前置条件**：Phase 4 社区发布完成

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M5.1 | 主动管理基础 | ✅ 完成 | Rules §10-§12 + pace-pulse + pace-learn + PostToolUse/UserPromptSubmit Hooks |
| M5.2 | 角色意识与智能增强 | ✅ 完成 | Agent 定义 + Skill→Agent 路由 + CR 拆分 + 范围估算 |
| M5.3 | 生命周期扩展 | ✅ 完成 | Release Note 自动生成 + pace-feedback + 业务引导增强 |

### 任务定义

> 实时状态见 [progress.md](progress.md) "当前任务"表。

**M5.1 主动管理基础（P0 + P1）**

| 任务 | 关联条目 | 说明 |
|------|---------|------|
| Rules §10 主动节奏管理 + §11 迭代自动节奏 | OBJ-1, OBJ-2 | 6 个信号检测 + merged 后自动管道 + 迭代节奏信号 |
| pace-pulse Skill | OBJ-2 | Claude 自动健康检查（user-invocable: false） |
| PostToolUse Hook + post-cr-update.sh | OBJ-1 | merged 状态检测 → 触发知识积累和度量更新 |
| pace-learn Skill | OBJ-8 | 即时知识积累（CR merged / 质量门修复 / 人类打回） |
| UserPromptSubmit Hook (intent-detect.sh) | OBJ-1 | 变更意图预检测，提醒走变更管理流程 |
| Rules §12 经验驱动决策 | OBJ-8 | insights.md 驱动推进模式决策 |

**M5.2 角色意识与智能增强（P2）**

| 任务 | 关联条目 | 说明 |
|------|---------|------|
| Agent 定义：pace-pm / pace-engineer / pace-analyst | OBJ-1 | 产品经理/工程师/分析师三角色分离 |
| Skill→Agent 路由 | OBJ-1 | pace-plan→pm、pace-dev→engineer、pace-retro→analyst |
| 智能 CR 拆分建议 | OBJ-3 | 意图检查点中自动评估 CR 拆分 |
| 迭代范围估算 | OBJ-2 | pace-plan 基于历史数据的工作量估算 |

**M5.3 生命周期扩展（P3）**

| 任务 | 关联条目 | 说明 |
|------|---------|------|
| Release Note 自动生成 | OBJ-1 | PF 所有 CR merged 后生成变更摘要 |
| pace-feedback Skill | OBJ-1 | 上线后反馈收集，闭合交付→反馈→改进循环 |
| 业务规划引导增强 | OBJ-1 | pace-init 代码结构推断 + MoS 建议 |

---

## Phase 6：基础扩展

**目标**：CR 类型扩展（feature/defect/hotfix）、角色意识（5 角色自动推断）、缺陷管理基础。

**对应 OBJ**：OBJ-12, OBJ-13, OBJ-14

**前置条件**：Phase 5 完成

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M6.1 | CR Schema 扩展 + 迁移 | ✅ 完成 | cr-format type/severity/released + workflow released + hotfix 路径 + v0.1→v0.2 迁移 |
| M6.2 | 角色模型 | ✅ 完成 | Rules §13 角色意识 + pace-role Skill + pace-status 角色视图 |
| M6.3 | 缺陷管理 | ✅ 完成 | pace-ops Skill + defect CR 创建 + 缺陷度量 + theory 映射更新 |

---

## Phase 7：发布管理

**目标**：Release 实体、部署追踪、DORA 度量基础。

**对应 OBJ**：OBJ-12

**前置条件**：M6.1 完成

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M7.1 | Release Schema + Skill | ✅ 完成 | release-format.md + pace-release Skill + release 模板 |
| M7.2 | 规则 + 连锁更新 | ✅ 完成 | §14 发布管理 + §2 Release 纳入 + §9 Release 变更场景 |
| M7.3 | DORA 度量（部分） | ✅ 完成 | 部署频率 + 变更前置时间 |

---

## Phase 8：运维反馈与集成

**目标**：运维闭环完整版、外部工具集成框架、完整 DORA 四指标。

**对应 OBJ**：OBJ-13

**前置条件**：M7.1 完成

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M8.1 | 集成框架 | ✅ 完成 | integrations-format.md + integrations 模板 + post-merge Hook + §16 集成管理 |
| M8.2 | /pace-ops 完整版 | ✅ 完成 | 外部数据摄入 + Release 追溯 + §15 运维反馈 |
| M8.3 | 反馈闭环主动化 | ✅ 完成 | §1 Release/defect/MoS 提醒 + retro MoS 进展 |
| M8.4 | 完整 DORA 度量 | ✅ 完成 | 变更失败率 + MTTR + 完整 DORA 报告 + 缺陷根因报告 |

---

## Phase 9：验证与文档

**目标**：文档体系更新、迁移验证。

**前置条件**：Phase 6-8 完成

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M9.1 | 文档更新 | ✅ 完成 | roadmap + progress + README + CHANGELOG + 用户指南 + 贡献指南 + 示例 中文化 |
| M9.2 | 迁移验证 | ✅ 完成 | v0.1.0→v0.9.0 迁移机制修复 + DAF 项目模拟验证 9/9 通过 |

---

## Phase 10：开源借鉴与增强

**目标**：借鉴开源社区优秀设计模式，增强状态机、变更管理和初始化能力。

**前置条件**：Phase 9 M9.1 完成

**对应 OBJ**：OBJ-1, OBJ-3, OBJ-4, OBJ-12

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M10.1 | 状态机增强 | ✅ 完成 | P1 角色约束转换 + P2 Checkpoint + P5 复杂度量化 + P6 关联关系丰富化 |
| M10.2 | 变更管理增强 | ✅ 完成 | P3 Triage 结构化分流（Accept/Decline/Snooze） |
| M10.3 | 初始化增强 | ✅ 完成 | P4 PRD→功能树自动分解（--from 参数） |

### 任务定义

| # | 任务 | 里程碑 | 关联条目 |
|---|------|--------|---------|
| T56 | P1 角色约束的状态转换 | M10.1 | OBJ-3, design.md §5 |
| T57 | P2 CR 状态转换 Checkpoint | M10.1 | OBJ-4, design.md §5/§7 |
| T58 | P3 变更 Triage 结构化分流 | M10.2 | OBJ-4, design.md §7, S4-S7 |
| T59 | P4 PRD→功能树自动分解 | M10.3 | OBJ-1, S23 |
| T60 | P5 CR 复杂度量化评估 | M10.1 | OBJ-3, design.md §5, F5.7 |
| T61 | P6 CR 间关系丰富化 | M10.1 | OBJ-4, design.md §5 |

---

## Phase 11：Linear AI 深度借鉴

**目标**：借鉴 Linear AI 的核心创新（三层透明、渐进自主性、反应式调优、视觉溯源），增强 devpace 的信任建设、自主性分层和智能进化能力。

**前置条件**：Phase 10 完成

**对应 OBJ**：OBJ-1, OBJ-3, OBJ-5, OBJ-6

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M11.1 | 溯源标记 + 三层透明 | ✅ 完成 | 方向 4（source 标记）+ 方向 1（表面/中间/深入层 + /pace-trace） |
| M11.2 | 反应式调优 + 渐进自主性 | ✅ 完成 | 方向 3（§12.5 纠正即学习 + insights-format 偏好类型）+ 方向 2（辅助/标准/自主三级） |

### 任务定义

| # | 任务 | 里程碑 | 关联条目 |
|---|------|--------|---------|
| T63 | 方向 4：溯源标记系统 | M11.1 | OBJ-6, F7.1, S24 |
| T64 | 方向 1：三层渐进透明 | M11.1 | OBJ-5, F7.2, F7.3, S24, NF11 |
| T65 | 方向 3：反应式调优 | M11.2 | OBJ-1, F7.5, F7.6, S26 |
| T66 | 方向 2：渐进自主性 | M11.2 | OBJ-3, F7.4, S25 |

---

## Phase 12：审查质量与探索增强

**目标**：借鉴 Plandex（累积 Diff）、Shrimp（Gate 反思）、Roo Code（关注点引导）的优秀设计，提升审查质量和探索模式的结构化输出。

**前置条件**：Phase 11 完成

**对应 OBJ**：OBJ-3, OBJ-5

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M12.1 | 审查质量增强 | ✅ 完成 | 累积 Diff 审查视图 + Gate 间反思步骤 |
| M12.2 | 探索模式增强 | ✅ 完成 | 关注点引导（架构/调试/评估） |

### 任务定义

| # | 任务 | 里程碑 | 关联条目 |
|---|------|--------|---------|
| T67 | 累积 Diff 审查视图 | M12.1 | OBJ-3, design.md §6 |
| T68 | Gate 间反思步骤 | M12.1 | OBJ-3, design.md §6 |
| T69 | 探索模式关注点引导 | M12.2 | OBJ-5, design.md §2 |

---

## Phase 13：ECC 深度借鉴

**目标**：借鉴 Everything Claude Code 1.4.1 的最佳实践，增强 Hook 可靠性、检查项智能化、模型分配和上下文管理。

**前置条件**：Phase 12 完成

**对应 OBJ**：OBJ-1, OBJ-2, OBJ-3, OBJ-4, OBJ-8

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M13.1 | 工程基础增强 | ✅ 完成 | Hook Bash→Node.js 迁移 + 检查项依赖/阈值 + Model Tiering |
| M13.2 | 协作与智能增强 | ✅ 完成 | Agent 交接协议 + 置信度模型 + 上下文窗口管理 |

### 任务定义

| # | 任务 | 里程碑 | 关联条目 |
|---|------|--------|---------|
| T70 | Hook 跨平台可靠性 — Bash→Node.js 迁移 | M13.1 | OBJ-3, NF3 |
| T71 | 检查项依赖与安全推荐 | M13.1 | OBJ-3, design.md §6 |
| T72 | Model Tiering — 按任务复杂度分配模型 | M13.1 | OBJ-1 |
| T73 | Agent 交接协议增强 | M13.2 | OBJ-4, design.md §5 |
| T74 | 学习管道置信度模型 | M13.2 | OBJ-8 |
| T75 | 上下文窗口管理建议 | M13.2 | OBJ-2 |

---

## Phase 14：BMAD 深度借鉴

**目标**：借鉴 BMAD-METHOD（36,900+ Stars）的核心创新——对抗式审查、工作流自适应、步骤隔离、技术约定宪法，增强 devpace 的质量审查深度、复杂度感知和技术一致性。

**前置条件**：Phase 13 完成

**对应 OBJ**：OBJ-1, OBJ-3, OBJ-4, OBJ-5

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M14.1 | 质量审查增强 | ✅ 完成 | P1 对抗审查（checks-format + review-procedures + rules） |
| M14.2 | 复杂度感知增强 | ✅ 完成 | P2 规模自适应路径 + P3 步骤隔离铁律 |
| M14.3 | 上下文与体验增强 | ✅ 完成 | P4 context.md 技术约定 + P5 Agent 沟通风格 + P6 智能导航 |

### 任务定义

| # | 任务 | 里程碑 | 关联条目 |
|---|------|--------|---------|
| T76 | P1 对抗审查（Adversarial Review） | M14.1 | OBJ-3, design.md §6 |
| T77 | P2 Quick Flow 规模自适应 + 升级守卫 | M14.2 | OBJ-1, design.md §6 |
| T78 | P3 Micro-File 步骤隔离规则 | M14.2 | OBJ-3, design.md §6 |
| T79 | P4 project-context.md 全局技术约定 | M14.3 | OBJ-4, design.md §6 |
| T80 | P5 Agent 沟通风格增强 | M14.3 | OBJ-5 |
| T81 | P6 智能导航/建议下一步 | M14.3 | OBJ-5 |

---

## Phase 15：测试策略与验收验证

**目标**：为 /pace-test 实现完整的三层测试管理——Layer 1 基础执行、Layer 2 策略管理（PF 验收→测试映射）、Layer 3 AI 验收验证，使测试从"跑命令"提升为"基于需求验收标准的系统化验证"。

**对应 OBJ**：OBJ-3, OBJ-12

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M15.1 | Layer 1 + Layer 3 + 基础能力 | ✅ 完成 | SKILL.md 入口 + 基础测试执行 + AI 验收验证（accept） + generate 用例生成 + CR Schema test 字段 + 规则注册 |
| M15.2 | Layer 2 策略管理 | ✅ 完成 | strategy/coverage/impact/report 四子命令 + test-strategy Schema + 测试效能指标 |
| M15.3 | 高级分析能力 | ✅ 完成 | flaky 不稳定测试分析 + dryrun 模拟门禁 + baseline 测试基准线 |

### 任务定义

| # | 任务 | 里程碑 | 关联条目 |
|---|------|--------|---------|
| T90 | SKILL.md + Layer 1/3 + gen + CR Schema + 规则注册 | M15.1 | OBJ-3, design.md §6 |
| T91 | strategy/coverage/regress/report + test-strategy Schema + metrics | M15.2 | OBJ-3, OBJ-12 |
| T92 | flaky/gate/baseline 三子命令 | M15.3 | OBJ-3 |

---

## Phase 16：企业级扩展

**目标**：面向企业开发者扩展 DORA 度量代理指标、跨项目经验复用和 CI/CD 自动感知能力，兑现 vision.md"完整 BizDevOps"承诺的 Ops 感知层深化。

**对应 OBJ**：OBJ-15, OBJ-16, OBJ-17

**前置条件**：Phase 15 完成

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M16.1 | DORA 代理指标 | ✅ 完成 | /pace-retro DORA 四指标代理值 + 趋势对比 + 基准分级 + metrics.md 映射规则 |
| M16.2 | 跨项目经验复用 MVP | ✅ 完成 | insights 导出/导入机制 + 置信度降级 + 偏好过滤 |
| M16.3 | CI/CD 感知 Tier 1+2 | ✅ 完成 | CI 工具类型自动检测 + Gate 4 CI 状态查询 + integrations 持久化 |

### 任务定义

| # | 任务 | 里程碑 | 关联条目 |
|---|------|--------|---------|
| T95 | DORA 代理指标实现 | M16.1 | OBJ-15, S28, F9.1, design.md §8 |
| T96 | 跨项目经验导入 MVP | M16.2 | OBJ-16, S29, F9.2 |
| T97 | CI/CD 自动感知 | M16.3 | OBJ-17, S30, F9.3, design.md §8 |

---

## Phase 17：Risk Fabric 风险织网

**目标**：为 devpace 引入独立风险实体和全生命周期风险管理——Pre-flight 预判、Runtime 监控、Retrospective 趋势分析，让风险可见、可追踪、可解决。

**对应 OBJ**：OBJ-1, OBJ-3

**前置条件**：Phase 16 完成

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M17.1 | Risk Fabric 核心 | ✅ 完成 | /pace-guard Skill（scan/monitor/trends/report/resolve）+ risk-format Schema + 意图检查点嵌入 + pace-pulse 第 8 信号 + 分级自主响应矩阵 |

### 任务定义

| # | 任务 | 里程碑 | 关联条目 |
|---|------|--------|---------|
| T98 | Risk Fabric 核心实现 | M17.1 | OBJ-1, OBJ-3, S31, F10.1-F10.6, design.md §18 |

---

## Phase 18：外部同步 MVP

**目标**：pace-sync Skill 核心子命令 + GitHub（gh CLI）+ 手动推送 + 语义 Comment + MVP 闭环。让用户能通过 `/pace-sync` 将 CR 状态推送到 GitHub Issue，merged 时自动同步关闭。

**对应 OBJ**：OBJ-1, OBJ-12

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M18.1 | Schema + 配置基础 | ✅ 完成 | sync-mapping-format.md + integrations/cr Schema 扩展 |
| M18.2 | Skill 基础 + 运行时修复 | ✅ 完成 | SKILL.md + sync-procedures-*.md（setup/link/push/status）+ 标签预创建 + unlink + dry-run |
| M18.3 | Hook + Rules + 语义同步 | ✅ 完成 | sync-push.mjs 缓存比对 + post-cr-update.mjs 7 步管道 + §16 精炼 + feature docs 双层保障 |

### 任务定义

> 实时状态见 [progress.md](progress.md) "当前任务"表。

---

## Phase 19：智能推送与 Issue 生命周期

**目标**：自动推送（副产物非前置）+ Issue 创建能力 + Gate 结果同步 + 教学增强 + 健康信号。

**对应 OBJ**：OBJ-1, OBJ-12, OBJ-17

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M19.1 | 智能推送 + Gate 同步 | 待开始 | auto-create + auto-link + Gate Comment/Label + 教学触发 + pulse 信号 |
| M19.2 | Issue 生命周期 | 待开始 | create 子命令 + PR 关联能力 + 治理集成 |
| M19.3 | 多平台预研 | 待开始 | Linear 原型适配器 |

---

## Phase 20：轮询入站与冲突解决

**目标**：轮询式入站感知（CLI Plugin 无 webhook 约束）+ 冲突检测与 AI 解决 + 多平台正式支持。

**对应 OBJ**：OBJ-1, OBJ-12, OBJ-17

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M20.1 | 轮询式入站感知 | 待开始 | /pace-sync pull + 会话开始检查外部变更 |
| M20.2 | AI 冲突解决 | 待开始 | /pace-sync resolve + 语义冲突检测 |
| M20.3 | 多平台正式 + CI 回流 | 待开始 | Linear/Jira 正式适配器 + CI 结果回流 |

---

## Phase 21：BR 上游业务规划域

**目标**：补齐 BR 上游的业务规划域——从业务机会到专题（Epic）到业务需求的完整价值流建模，实现端到端追溯。

**对应 OBJ**：OBJ-1, OBJ-4, OBJ-6

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M21.1 | 概念模型和 Schema 基础 | ✅ 完成 | epic-format.md + br-format.md + opportunity-format.md + project-format.md 增强 + theory.md/design.md §3 更新 |
| M21.2 | 核心 Skill 和增强 | ✅ 完成 | /pace-biz（5 子命令）+ pace-init/change/status/plan 增强 |
| M21.3 | 追溯和信号 | ✅ 完成 | pace-trace/retro/next/dev/release 增强 + S16/S17 信号 |
| M21.4 | 文档和测试 | 🔄 进行中 | 特性文档 + requirements + roadmap + eval 覆盖 |

---

## 变更记录

> 操作级变更记录已移至 [progress.md](progress.md)。此处仅保留战略级变更。

| 日期 | 变更 | 原因 |
|------|------|------|
| 2026-03-07 | 新增 Phase 21：BR 上游业务规划域（M21.1-M21.4）。Opportunity/Epic/BR 溢出概念模型 + /pace-biz Skill + 全价值链增强 | BR 上游空白导致无法兑现端到端追溯承诺 |
| 2026-02-26 | pace-plan UX 优化 11 项增强（E1-E11）：P0 空树引导+智能建议、P1 adjust+auto-retro+启发式+衔接+速度、P2 分组+风险+回顾直联+health。不新增 Phase，产品层优化模式 | UX 原则 P1-P7 对齐审计，11 个用户旅程断点修复 |
| 2026-02-25 | Phase 18 里程碑扩展（M18.2+M18.3 新增 C1/B1/B2/A1/D2/D1 内容）；Phase 19 重组为智能推送+Issue 生命周期+多平台预研；Phase 20 重组为轮询入站+冲突解决+多平台正式（pull 从 Phase 19 移入，webhook 约束明确） | pace-sync 产品优化分析 |
| 2026-02-25 | 新增 Phase 18-20：外部工具同步（M18.1-M18.3, M19.1-M19.3, M20.1-M20.3） | v1.5.0 External Tool Semantic Bridge，语义级双向桥接 |
| 2026-02-25 | 新增 Phase 17：Risk Fabric 风险织网（M17.1） | OBJ-1/OBJ-3 能力延伸，独立风险实体 + 全生命周期风险管理 |
| 2026-02-23 | 新增 Phase 16：企业级扩展（M16.1-M16.3） | vision.md 定位调整（企业开发者 + Ops 分阶段覆盖），新增 OBJ-15/16/17 |
| 2026-02-23 | 新增 Phase 15：测试策略与验收验证（M15.1-M15.3） | /pace-test BizDevOps 感知的测试策略命令，三层测试管理体系 |
| 2026-02-22 | 新增 Phase 14：BMAD 深度借鉴（M14.1-M14.3） | BMAD-METHOD 深度调研，6 方向借鉴落地 |
| 2026-02-22 | 新增 Phase 13：ECC 深度借鉴（M13.1-M13.2） | Everything Claude Code 深度调研，6 方向增强 |
| 2026-02-22 | 新增 Phase 12：审查质量与探索增强（M12.1-M12.2） | 开源生态深度调研（Plandex/Shrimp/Roo Code）3 方向借鉴 |
| 2026-02-22 | 新增 Phase 11：Linear AI 深度借鉴（M11.1-M11.2） | Linear AI 深度调研，4 个方向借鉴落地 |
| 2026-02-21 | 新增 Phase 10：开源借鉴与增强（M10.1-M10.3） | 16 项目对标分析，6 项借鉴落地 |
| 2026-02-21 | 新增 Phase 6-9：完整 BizDevOps 生命周期扩展 | 覆盖发布/运维/角色/缺陷管理 |
| 2026-02-21 | 新增 Phase 5：AI 主导管理（M5.1-M5.3） | AI 主动性差距分析 → 七维度优化方案 |
| 2025-02-15 | 拆分 progress.md 为操作锚点，roadmap.md 回归战略规划 | 战略规划与操作跟踪职责分离 |
| 2025-02-15 | 目录结构与职责分离重构 | P1-P7 问题累积 |
| 2025-02-14 | 增加 OBJ-4 为 MVP 目标 | 用户反馈"需求变更导致失序"是核心痛点 |
| 2025-02-14 | 初始版本 | 项目创建 |
