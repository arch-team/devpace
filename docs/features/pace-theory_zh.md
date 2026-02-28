🌐 [English](pace-theory.md) | 中文版

# pace-theory — 设计理论指南

查阅 devpace 背后的 BizDevOps 方法论和设计理论的参考 Skill。只读。

## 核心特性

- **15 个子命令分 3 层**：入门（概览、model、why）→ 概念（objects、spaces、rules、trace、loops、change、metrics、topic）→ 参考（mapping、decisions、vs-devops、sdd、all）
- **精确章节路由**：每个子命令仅加载 theory.md 对应章节，不全量加载 550 行文件
- **`why` 深度解释**：三层输出——近期行为 → 设计决策（§11，16 条）→ 理论原文摘录；支持关键词精准查询（`why gate`、`why paused`）
- **上下文感知输出**：`.devpace/` 存在时，用项目实际数据（CR、度量、迭代）作为实例
- **角色适配框架**：输出视角根据当前角色（biz/pm/dev/tester/ops）自动调整

## 关键增强（v1.6）

### 三层命令结构
子命令组织为入门/概念/参考三层。空参数调用仅显示入门层，渐进暴露高级选项以降低认知负荷。

### 显式路由表
每个子命令映射到 theory.md 的具体章节（§0-§14）。定向查询不再全量加载文件——haiku 模型仅接收相关章节。

### `why` 作为差异化特性
实现 devpace 的四层可解释性链路：推理后缀（15 字）→ 中间层展开（2-5 行）→ `/pace-theory why`（方法论）→ `/pace-trace`（完整决策轨迹）。每层自然引导到下一层。

### `why` 关联设计决策
`why` 现在交叉引用 §11（16 条设计决策）解释每个行为。支持聚焦查询如 `why gate`、`why cr`、`why paused` 进行定向解释。

### 渐进披露
默认输出摘要优先（1-2 句话 + 核心表格 5-8 行），末尾附展开提示指向相关子命令。完整章节内容按需获取。

### 关键词搜索带上下文
自由文本关键词搜索返回匹配段落 + 位置上下文（"此概念属于 [章节名]，相关：[子命令]"）+ 零匹配时的智能 fallback。

### 项目上下文集成
objects/trace/metrics 子命令使用项目实际 BR/PF/CR 数据替代通用理论示例。未初始化项目收到温和引导。

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| `/pace-trace` | pace-theory 解释"devpace 为什么这样设计"（通用理论）；pace-trace 重建"某个具体 CR 的完整决策轨迹"（实例级别） |
| `/pace-status` | status 展示当前状态；theory 解释这些状态背后的概念 |
| `/pace-retro` | retro 生成度量数据；theory 解释背后的 DIKW 模型 |
| `/pace-learn` | learn 记录经验；theory 提供连接经验与方法论的框架 |

## 相关资源

- **权威源**：`skills/pace-theory/SKILL.md`（路由表、流程）
- **默认输出规则**：`skills/pace-theory/theory-procedures-default.md`（摘要分层、导航推荐、角色适配）
- **Why 输出规则**：`skills/pace-theory/theory-procedures-why.md`（三层模板、关键词映射）
- **搜索输出规则**：`skills/pace-theory/theory-procedures-search.md`（搜索流程、上下文定位）
- **数据源**：`knowledge/theory.md`（550 行 BizDevOps 知识库，14 个章节）
- **设计决策**：`knowledge/theory.md` §11（16 条关键设计决策）
