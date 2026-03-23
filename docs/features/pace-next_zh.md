🌐 [English](pace-next.md) | 中文版

# 下一步导航（`/pace-next`）

`/pace-next` 是 devpace 的跨域全局导航器。综合 CR、迭代、Release、度量、风险、功能树等多维信号，推荐当前最该做的 1 件事。使用 haiku 模型（轻量快速），仅使用只读工具（Read/Glob/Grep）。

`/pace-status` 回答"在哪"，`/pace-next` 回答"去哪"——这是 devpace 从"被动状态查看"到"主动行动指引"的关键差异化特性。

## 快速上手

```
1. /pace-next              --> 最高优先级 1 条建议（建议 + 原因 + 操作，3 行）
2. /pace-next detail       --> top-3 候选列表（最多 8 行）
3. /pace-next why          --> 展开推理链（2-5 行：信号扫描、优先级对比、备选方案）
4. /pace-next journey      --> 完整工作流旅程：从当前状态到目标的分步引导（自动选择模板）
5. /pace-next journey hotfix --> 指定模板的旅程视图
6. /pace-trace next        --> 查看完整信号采集和遍历过程
```

默认输出 3 秒内可读完。需要备选方案时用 `detail`，想了解推理逻辑时用 `why`，想看完整路径时用 `journey`。

## 核心特性

### 分组优先级矩阵

16 级信号分布在 5 个优先级组中，从高到低遍历，首个命中即为建议。

| 组别 | 优先级 | 信号 | 适用范围 |
|------|--------|------|---------|
| **Blocking** | 最高 | 审批阻塞 (S1)、高风险阻塞 (S2) | 全角色同等优先 |
| **In Progress** | 高 | 继续开发 (S3)、恢复暂停 (S4) | 工作流连续性 |
| **Delivery** | 中高 | Release 待验证 (S5)、风险积压 (S6)、迭代时间紧迫 (S7)、迭代接近完成 (S8) | 价值交付管道 |
| **Strategic** | 中 | 回顾提醒 (S9)、缺陷占比高 (S10)、同步滞后 (S11)、MoS 达成回顾 (S12) | 回顾与优化 |
| **Growth** | 低 | 功能未开始 (S13)、规划新迭代 (S14)、全部完成 (S15) | 新价值开拓 |
| **Idle** | 兜底 | 无信号 (S16) | 自由探索 |

信号定义维护在 `knowledge/_signals/signal-priority.md`（唯一权威源，pace-next / pace-status 概览 / pace-pulse session-start 三方共享）。

### 价值链可见性

建议不仅显示 CR 操作，还体现其在价值链中的位置。每条建议模板嵌入父级 PF（产品功能），对于 Biz/PM 角色还附加父级 BR（业务需求）或 OBJ（业务目标）。让用户看到的不只是"做什么"，还有"为什么重要"。

示例：`继续"OAuth 集成"（登录模块的一部分）——上次停在 token 验证`

### 风险感知

风险信号融入优先级矩阵的两个层级：

- **高严重度风险** (S2)：Blocking 组——全局阻塞级，与审批阻塞同等优先
- **中等风险积压** (S6)：Delivery 组——积累的开放风险，需要在升级前处理

高风险不可绕过人类确认，体现 devpace 安全优先原则。

### 三层渐进透明

每条建议的推理过程通过三个渐进层级可访问：

| 层级 | 触发方式 | 输出内容 | 行数 |
|------|---------|---------|------|
| **表面层** | `/pace-next`（默认） | 建议 + 原因 + 操作，原因行附 ≤15 字推理后缀 | 3 |
| **中间层** | `/pace-next why` | 信号扫描结果、优先级对比、备选方案 | 2-5 |
| **深入层** | `/pace-trace next` | 完整信号采集日志和遍历过程 | 无限制 |

层层引导：原因行以"（...why）"提示结尾，why 输出以"（...trace）"提示结尾。

### 角色适配

5 个角色（Dev / PM / Biz / Tester / Ops）不仅改措辞，还**在组内重排序**：

| 角色 | 提升信号 | 效果 |
|------|---------|------|
| PM | S8（迭代完成）、S13（功能未开始） | 迭代和功能树信号更早浮现 |
| Biz | S12（MoS 达成）、S13（功能未开始） | 业务目标信号更早浮现 |
| Ops | S5（Release 待验证）、S11（同步滞后） | 部署和运维信号更早浮现 |
| Tester | S10（缺陷占比高）、S6（风险积压） | 质量和风险信号更早浮现 |
| Dev（默认） | 无调整 | 默认信号顺序 |

Blocking 组信号（S1-S2）不受角色影响——全角色同等最高优先级。

### 经验增强

当 `.devpace/metrics/insights.md` 存在时，按当前建议类型匹配历史经验 pattern（置信度 > 0.7）。匹配的经验作为 1 行后缀附加在原因行末尾，用"——"连接。

示例：`原因：1 个变更等待审批——上次类似变更曾有权限边界问题`

### 多 CR 并行处理

多个 developing 状态 CR 时，按以下顺序排序：

1. **会话连续性**——state.md 中记录为当前工作的 CR 优先
2. **完成度**——接近完成的 CR 优先
3. **PF 优先级**——更高优先级的产品功能优先

top-1 成为建议，其余在 `detail` 模式中展示。

### 时间维度

时间敏感信号增强紧迫感知：

- **迭代截止压力** (S7)：距结束 < 2 天且完成率 < 50% 时触发
- **开发停滞**：通过会话连续性排名隐含体现——长时间闲置的 CR 被降低优先级
- **回顾提醒** (S9)：最近指标更新超过 7 天时触发

### detail 模式

`/pace-next detail` 遍历全部 16 级信号，收集所有命中项，输出 top-3 候选（最多 8 行）。

```
💡 建议：继续"OAuth 集成"（登录模块）
   原因：上次停在 token 验证，完成度 70%
   操作：/pace-dev 或说"继续"

📋 候选（按优先级）：
  2. 1 个变更等待审批 —— /pace-review
  3. 功能"MFA 支持"还没开始 —— 说"帮我实现 MFA 支持"
```

仅 1 条命中时不展示候选段。

### 旅程模式

`/pace-next journey` 从"下一步做什么"升级为"从当前到目标的完整路径"。渲染分步旅程视图，标记已完成步骤、当前位置和待做步骤——纯建议性，不自动执行任何操作。

**旅程模板**：

| 模板 | 编排路径 | 适用场景 |
|------|---------|---------|
| `new-feature` | biz discover → decompose → plan next → dev → review → merged | 从零开始交付一个功能 |
| `iteration` | plan next → [dev → review → merged]* → plan close → retro | 完整迭代循环 |
| `hotfix` | feedback report → dev → review → release deploy | 紧急修复 |
| `release` | release create → deploy → verify → close | 标准发布 |
| `onboarding` | init → dev(第一个功能) → review → merged | 新用户首次体验 |

不指定模板名时，根据项目状态自动选择（例如：无 CR 的新项目 → `onboarding`；有活跃迭代 → `iteration`）。

**输出示例**：

```
旅程：iteration — 完成当前迭代循环

✅ 规划迭代 — 纳入 3 个功能点
✅ 开发 PF-001 — "OAuth 集成"已合并
👉 开发 PF-002 — 说"帮我实现 [功能名]"或 /pace-dev
⏳ 审批 — /pace-review
⏳ 迭代回顾 — /pace-retro

进度：2/5 步完成
```

**核心规则**：
- **只展示不执行**——展示路径，不自动触发任何 Skill
- **无状态文件**——不持久化旅程状态，每次调用从 `.devpace/` 动态推断
- **与默认模式互补**——journey 展示全局路径，默认模式推荐单步行动

## 使用场景

### 场景 1：开始新会话——先做什么？

```
You:    /pace-next
Claude: 💡 建议：继续"OAuth 集成"（登录模块）
           原因：上次停在 token 验证，接近完成
           操作：/pace-dev 或说"继续"
```

### 场景 2：多个选项——哪个最重要？

```
You:    /pace-next detail
Claude: 💡 建议：2 个变更等待审批——审批后才能推进
           原因：审批已等待超 24 小时，阻塞下游工作
           操作：/pace-review

        📋 候选（按优先级）：
          2. 继续"数据导出" —— 完成度 60%
          3. 功能"报表生成"还没开始（属于数据分析）
```

### 场景 3：想了解推理过程

```
You:    /pace-next why
Claude: 信号扫描：S1（审批阻塞）= 0，S2（高风险）= 0，S3（开发中）= 1 CR
        优先级命中：S3——"OAuth 集成"处于 developing 状态
        备选方案：S8（迭代 80% 完成）、S13（1 个功能未开始）
        决策：S3 优先——工作流连续性高于迭代接近完成
        完整追踪：/pace-trace next
```

### 场景 4：角色适配——业务视角

```
You:    /pace-role biz
You:    /pace-next
Claude: 💡 建议：MoS 达成率 82%——回顾业务成效指标
           原因："用户认证"目标 4/5 指标已达成
           操作：/pace-retro
```

## 与其他命令的关系

| 命令 | 关系 |
|------|------|
| `/pace-status` | status 回答"在哪"（快照）；next 回答"去哪"（导航）。status 概览附带轻量 top-1 建议（pace-next 子集，无推理） |
| `/pace-pulse` session-start | session-start 是"推送式"自动快照；next 是"拉取式"深度导航。去重：< 5 分钟内 next 跳过已通知的最高信号 |
| `/pace-dev` | next 经常推荐继续开发；操作行引导至 `/pace-dev` |
| `/pace-review` | 有审批积压 (S1) 时，next 将其置顶推荐 |
| `/pace-role` | 角色设置驱动 pace-next 的组内信号重排序；角色切换立即生效 |
| `/pace-retro` | 战略组信号（S9、S12）引导至 `/pace-retro` |
| `/pace-trace` | `why` 提供中间层推理；`/pace-trace next` 提供完整信号遍历追踪 |

## 信号优先级源

所有信号定义、分组和角色重排序规则维护在 `knowledge/_signals/signal-priority.md`——三个消费方共享的唯一权威源：

| 消费方 | 可见子集 | 用途 |
|--------|---------|------|
| pace-next | 全部 S1-S16 | 完整遍历，取 top-1 或 top-3 |
| pace-status 概览 | S1/S3/S5/S8/S9/S13/S15 | 轻量 top-1 建议 |
| pace-pulse session-start | 全部（独立阈值版本） | 分层摘要 |

## 相关资源

- [SKILL.md](../../skills/pace-next/SKILL.md) — Skill 定义、输入/输出和高层流程
- [next-procedures.md](../../skills/pace-next/next-procedures.md) — 详细决策算法、输出格式和角色适配规则
- [next-procedures-journey.md](../../skills/pace-next/next-procedures-journey.md) — 旅程编排模板、自动选择逻辑和输出格式
- [signal-priority.md](../../knowledge/_signals/signal-priority.md) — 信号定义和优先级分组（SSOT）
- [signal-collection.md](../../knowledge/_signals/signal-collection.md) — 共享信号采集规程
- [User Guide](../user-guide_zh.md) — 所有命令的快速参考
