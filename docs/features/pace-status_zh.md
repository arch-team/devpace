🌐 [English](pace-status.md) | 中文版

# 项目状态查询（`/pace-status`）

`/pace-status` 是只读查询命令，按不同粒度展示项目研发进度。遵循 **三级信息分层** 和正交维度：

- **L1 概览**：回答"整体怎样"（≤3 行精简摘要）
- **L2 detail / L2 trace**：同层级的两种正交视角——detail 展开广度（当前迭代每个功能），trace 下钻深度（某个需求的完整交付状态，可跨迭代）
- **L3 tree**：回答"从业务到代码的全貌"（完整价值链）

所有输出使用自然语言，不暴露内部 ID。角色视图和 `since` 时间修饰符提供额外过滤维度。

## 快速上手

```
1. /pace-status            --> 3 行概览 + 进度条 + 建议下一步
2. /pace-status detail     --> 功能树 + 各功能完成状态
3. /pace-status trace 认证  --> 从业务需求/目标出发的反向追溯
4. /pace-status tree       --> 完整价值链（目标→需求→功能→变更）
5. /pace-status metrics    --> 核心指标快照 + 趋势箭头
6. /pace-status since 3d   --> 最近 3 天变更摘要
```

## 子命令参考

### 核心层

| 子命令 | 说明 |
|--------|------|
| （空） | 快速概览——≤3 行 + 建议（/pace-next 轻量子集，仅 top-1 信号） |
| `detail` | 功能树广度展开——当前迭代每个功能的状态 |
| `tree` | 完整价值链——从业务目标到变更请求 |
| `trace <名称>` | 反向深度追溯——某个需求/功能的完整交付状态（可跨迭代） |
| `metrics [quality\|delivery\|risk]` | 核心指标快照 + 趋势箭头；可按类别聚焦 |
| `since <时间>` | 时间段变更摘要（`3d`、`1w`、`last-session`），可与其他子命令组合 |
| `<关键词>` | 按标题搜索匹配的变更详情；无匹配时自动 fallback 到功能树搜索 |

### 视角层（角色过滤）

由 `/pace-role` 管理，也可直接作为子命令使用。设置角色后概览和 detail 自动适配。

| 子命令 | 视角 | 关注点 |
|--------|------|--------|
| `biz` | 业务负责人 | MoS 达成率、价值交付 |
| `pm` | 产品经理 | 迭代进度、功能完成度 |
| `dev` | 开发者 | CR 状态、质量门 |
| `tester` | 测试者 | 缺陷分布、质量指标 |
| `ops` | 运维 | Release 状态、部署健康 |
| `chain` | 价值链定位 | 当前工作在价值链中的位置 |

**优先级**：显式角色子命令 > `/pace-role` 自动适配。

## 核心特性

### 三级信息分层

概览（L1）回答"整体怎样"，detail 和 trace（L2）是同层级的正交视角（广度 vs 深度），tree（L3）展示全貌。detail 和 trace 不是包含关系——trace 可能展示 detail 中没有的跨迭代 CR，也可能缺少与目标节点无关的功能。

### 导航衔接

每个非概览子命令输出末尾追加 1 行上下文导航提示，消除子命令间的信息孤岛：

- detail → "深入某功能：/pace-status trace [功能名]"
- tree → "当前迭代聚焦：/pace-status detail"
- metrics → "完整回顾：/pace-retro"
- trace → "全景价值链：/pace-status tree"
- chain → "追溯其他功能：/pace-status trace [名称]"

### 概览附加行控制

概览主体 ≤3 行（硬约束），附加行（建议 + 同步）≤2 行，总输出 ≤5 行。建议行是 /pace-next 的轻量子集——仅 top-1 信号，不含推理过程。

### 推/拉去重

距会话开始 <5 分钟时省略建议行（session-start 刚给过节奏提醒），超过后正常输出。

### metrics 深度

默认输出 4 项核心指标（一次通过率、MoS 达成率、CR 周期、迭代速度）+ 趋势箭头。可按 `quality`/`delivery`/`risk` 类别聚焦。区分 pace-retro：metrics = 实时快照，pace-retro = 时间段回顾。

### 关键词搜索 fallback

`<关键词>` 无匹配时自动尝试功能树匹配，命中提示使用 trace 追溯。

## 使用场景

### 场景 1：早会快速检查

```
You:    /pace-status
Claude: 认证系统 ████████░░ 80% (4/5 CR)，下一步：权限控制
        阻塞：用户管理等待认证模块完成
        建议：继续"OAuth 集成" → /pace-dev
```

### 场景 2：业务方询问进度

```
You:    /pace-status trace 认证
Claude: 目标: 用户认证系统 (OBJ-1)
        ├── 需求: 安全登录 (BR-001)
        │   ├── 登录模块 → 3/3 CR ✅
        │   └── 权限控制 → 1/2 CR 🔄
        └── 需求: OAuth 支持 (BR-002)
            └── OAuth 模块 → 2/2 CR ✅
        MoS: 3/5 达成
        → 全景价值链：/pace-status tree
```

### 场景 3：本周做了什么

```
You:    /pace-status since 1w
Claude: 最近 7 天变更摘要
        完成：OAuth 集成（merged）
        进行中：会话管理（创建 → 开发中）
        新增：MFA 支持（创建）
        → 查看当前全貌：/pace-status detail
```

## 与其他命令的关系

| 命令 | 关系 |
|------|------|
| `/pace-next` | status 回答"在哪"+ 轻量 top-1 建议；pace-next 回答"该做什么"+ 完整推理 |
| `/pace-retro` | metrics = 实时快照；pace-retro = 时间段回顾报告 |
| `/pace-role` | 设置角色后 status 自动适配；显式角色子命令覆盖 |
| `/pace-pulse` | session-start 是"推送"；status 是"拉取"。< 5 分钟去重 |

## 相关资源

- [SKILL.md](../../skills/pace-status/SKILL.md) — Skill 定义和子命令列表
- [status-procedures-*.md](../../skills/pace-status/) — 详细输出格式（按子命令拆分，按需加载）
- [User Guide](../user-guide_zh.md) — 所有命令的快速参考
- [metrics.md](../../knowledge/metrics.md) — metrics 子命令使用的指标定义
