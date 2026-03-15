# theory-procedures-default — 默认输出规则

> 由 SKILL.md 路由表加载。空参数及 12 个具体主题子命令（model/objects/.../sdd）和 `all` 时读取。

## §0 速查卡片

```
输出规则：摘要优先（首段+表格 5-8 行），末尾附展开提示和导航推荐。
```

## §1 无参数输出

1. 输出 theory.md §0 速查卡片内容
2. 追加分层导航入口：

```
📖 入门：`model`（概念模型） | `why`（设计理由）
📚 深入：`objects` `spaces` `rules` `trace` `loops` `change` `metrics` `topic`
📋 参考：`mapping` `decisions` `vs-devops` `sdd` `all`
```

3. 不逐一列出所有子命令说明——导航入口足够引导

## §2 具体主题输出（摘要优先）

1. **首段摘要**：1-2 句话概括该章节核心观点
2. **核心表格**：提取章节中最重要的表格或列表（5-8 行）
3. **末尾展开**："深入了解：/pace-theory [相关子命令列表]"
4. 不直接输出 theory.md 原文全文——摘要是默认粒度

## §3 `all` 输出

1. 前置提醒："以下是完整理论知识库（~550 行），如果只想了解特定主题，建议用具体子命令查询。"
2. 输出 theory.md 全文

## §4 导航推荐

每个子命令输出末尾附 1 行导航推荐。模式：**当前主题 → 相邻/深入主题**。

| 当前子命令 | 推荐下一步 |
|-----------|-----------|
| （空） | `model`（了解核心框架）或 `why`（理解设计理由） |
| `model` | `objects`（深入作业对象）或 `trace`（看价值链） |
| `objects` | `trace`（看追溯链路）或 `rules`（看流转规则） |
| `spaces` | `objects`（看在空间中流转的对象）或 `mapping`（看完整映射） |
| `rules` | `decisions`（了解规则设计理由）或 `change`（看变更管理） |
| `trace` | `loops`（看反馈闭环）或 `mapping`（看完整映射） |
| `topic` | `metrics`（看度量体系）或 `loops`（看闭环如何运作） |
| `metrics` | `loops`（看闭环关联）或 `decisions`（看度量决策） |
| `loops` | `trace`（看价值链）或 `topic`（看专题模式） |
| `change` | `decisions`（看设计理由）或 `rules`（看作业规则） |
| `decisions` | `mapping`（看实现映射）或 `why`（看行为解释） |
| `mapping` | `vs-devops`（看方法论对比）或 `decisions`（看设计决策） |
| `vs-devops` | `model`（了解 BizDevOps 核心）或 `mapping`（看完整映射） |
| `sdd` | `rules`（看作业规则）或 `decisions`（看设计决策 #16） |
| `all` | 无需导航 |

**5 分钟入门路径**（速查卡片中嵌入）：`model` → `objects` → `trace` → `loops`

## §5 角色适配（条件执行）

**前置条件**：仅当 `.devpace/` 存在时执行本节。

检查 `.devpace/state.md` 中的 preferred-role 字段，调整"关联当前项目"部分的措辞框架：

| 角色 | 输出框架 | 侧重内容 |
|------|---------|---------|
| biz | "从业务看技术" | 价值链、MoS、业务闭环、业务目标映射 |
| pm | "迭代与交付" | 迭代节奏、交付进度、产品闭环、优先级 |
| dev | "从技术看业务"（默认） | 实现映射、状态机、门禁逻辑、代码关联 |
| tester | "质量保障" | 门禁机制、度量指标、缺陷追溯 |
| ops | "发布与运维" | 发布流程、运维闭环、部署追踪 |

- 理论内容不变，只调整关联部分的措辞
- Dev 角色不改变默认措辞（向下兼容）
- 首次角色适配追加教学提示："（当前按 [角色] 视角关联，切换：/pace-role [角色]）"

角色定义权威源：`knowledge/role-adaptations.md`。本表仅定义 theory 输出的角色适配框架。

## §6 未初始化引导

如果未初始化 `.devpace/`：仅输出理论内容，末尾追加引导："想看这些概念在你的项目中如何运作？试试 `/pace-init`"
