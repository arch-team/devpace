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
| Phase 1 | MVP 核心 | 跑通工作流 + 跨会话 + 质量检查 + 变更管理 | 🔄 进行中 |
| Phase 2 | 实战验证 | 在 diagnostic-agent-framework 中完整验证 | ⏳ 待开始 |
| Phase 3 | 可移植性 | 第 2 个项目验证 + 度量体系 | ⏳ 待开始 |
| Phase 4 | 社区发布 | 文档完善 + 开源准备 | ⏳ 待开始 |

---

## Phase 1：MVP 核心

**目标**：Plugin 骨架完成，核心 Skills 可用，协议规则覆盖正常流程和变更场景。

**对应 OBJ**：OBJ-1, OBJ-2, OBJ-3, OBJ-4

### 里程碑

| # | 里程碑 | 状态 | 产出 |
|---|--------|------|------|
| M1.1 | 项目骨架 + 核心规则 | ✅ 完成 | plugin.json, CLAUDE.md, protocol, schema, templates |
| M1.2 | 基础 Skills | ✅ 完成 | pace-init, pace-status, pace-advance, pace-review, pace-retro |
| M1.3 | 变更管理能力 | 🔄 进行中 | protocol §9 + pace-change skill + paused 状态 + 变更记录 |
| M1.4 | 项目文档体系 | 🔄 进行中 | vision, requirements, roadmap, design 更新 |

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

**目标**：在 diagnostic-agent-framework 中验证全部 MVP 能力。

**对应 OBJ**：OBJ-1, OBJ-2, OBJ-3, OBJ-4, OBJ-5, OBJ-6

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
| V2.12 | 理论参考（/pace-guide） | 在不同项目阶段调用 /pace-guide | 返回与当前阶段相关的理论指导，不修改状态文件 |
| V2.13 | 状态分级输出（/pace-status） | 分别测试默认/detail/tree 三级输出 | 每级输出粒度正确，默认 ≤3 行 |

---

## Phase 3：可移植性

**目标**：第 2 个项目验证，度量体系可用。

**对应 OBJ**：OBJ-7, OBJ-8

### 任务（待 Phase 2 完成后细化）

- 选择第 2 个验证项目
- /pace-init 从零开始
- /pace-retro 端到端验证（对应 S9 验收标准）
- /pace-retro 生成有意义的回顾报告
- 收集可移植性数据（初始化耗时、适配工作量）

---

## Phase 4：社区发布

**目标**：文档完善，社区可用。

**对应 OBJ**：OBJ-9, OBJ-10

### 任务（待 Phase 3 完成后细化）

- README 重写（面向社区）
- 用户指南（docs/user-guide.md）
- 示例项目
- 开源准备（LICENSE、CONTRIBUTING）

---

## 变更记录

> 操作级变更记录已移至 [progress.md](progress.md)。此处仅保留战略级变更。

| 日期 | 变更 | 原因 |
|------|------|------|
| 2025-02-15 | 拆分 progress.md 为操作锚点，roadmap.md 回归战略规划 | 战略规划与操作跟踪职责分离 |
| 2025-02-15 | 目录结构与职责分离重构 | P1-P7 问题累积 |
| 2025-02-14 | 增加 OBJ-4 为 MVP 目标 | 用户反馈"需求变更导致失序"是核心痛点 |
| 2025-02-14 | 初始版本 | 项目创建 |
