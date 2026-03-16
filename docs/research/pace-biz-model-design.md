# pace-biz 模型设计文档

> **职责**：pace-biz Skill 的模型设计全景——理论锚点 + 实现映射 + 优化路线。
>
> **与 biz-analysis-models.md 的关系**：`biz-analysis-models.md` 定义"抽象模型是什么"，本文档定义"模型如何落地为 pace-biz 的具体实现"。
>
> **读者**：devpace 开发者/维护者。

## §0 速查卡片

### 四模型 × devpace 实现矩阵

| 模型 | 理论定义 | pace-biz 落地 | 主要实现文件 | 差距评估 |
|------|---------|--------------|-------------|---------|
| **Process Model** | 六阶段生命周期 + 三级反馈循环 | 子命令映射 + 空参引导的阶段感知 | SKILL.md 路由表 + 各 procedures | 反馈循环为隐式 |
| **Data Model** | 六层实体 × 四级成熟度 × 五种关系 | .devpace/ 目录结构 + readiness-score.md | project.md, epics/, requirements/ | 成熟度为隐式实现 |
| **Discovery Model** | 三类输入源 × 六阶段统一管道 | discover/import/infer 三子命令 | biz-procedures-{discover,import,infer}.md | Reconcile 实现深度不均 |
| **Quality Model** | 四维度评估（D1-D4） | refine + align + view 协同 | biz-procedures-{refine,align,view}.md | D4 与 metrics.md 弱关联 |

### 文档导航

| 章节 | 内容 |
|------|------|
| §1 Process Model | 六阶段→子命令映射 + Phase 映射 + 反馈循环 |
| §2 Data Model | 实体存储 + 成熟度策略 + 关系实现 |
| §3 Discovery Model | 三源→三命令 + 六阶段管道对比 + Reconcile 差异 |
| §4 Quality Model | 四维度实现 + 维度协同 + 与质量门互补 |
| §5 模型间协同 | 空参引导 + 创建后引导 + 精炼反馈场景 |
| §6 差距与优化 | 三个差距 + 优化方案 + 优先级排序 |

---

## §1 Process Model 落地方案

> 理论定义详见 `biz-analysis-models.md §1`。

### 六阶段 → pace-biz 子命令映射

| 阶段 | 子命令 | 具体步骤 | 补充说明 |
|------|--------|---------|---------|
| **Sense** | `opportunity` | 全流程（Step 1-4） | 捕获外部信号为 OPP 记录 |
| | `discover` | Step 1（目标框定） | 从模糊想法提取意图 |
| **Ideate** | `discover` | Step 2-3（头脑风暴 + 边界定义） | 对话式渐进展开 |
| | `import` | Step 2（实体提取） | 从文档批量提取候选 |
| | `infer` | Step 1-2（代码分析 + 信号挖掘） | 反向推断已有功能 |
| **Structure** | `epic` | 全流程（Step 1-8） | 创建 Epic + OBJ 关联 + MoS |
| | `decompose` | 全流程（Epic→BR 或 BR→PF） | 层级拆解 + 依赖 + 优先级 |
| **Refine** | `refine` | 全流程（Step 1-4） | 交互式补充六维度细节 |
| **Validate** | `align` | 全流程（Step 1-4） | 九维检查 + 趋势追踪 |
| **Ready** | （无专属子命令） | refine Step 4 动态推荐 | 就绪度 >= 80% 时推荐 /pace-dev |

**实现要点**：Sense 和 Ideate 的边界在实现中是模糊的——`discover` 横跨两个阶段（Step 1 = Sense，Step 2-3 = Ideate），这是有意的设计：交互式探索天然跨越"捕获信号"和"展开构思"。

### 六阶段 → Phase 0-5 映射

Process Model 的六阶段主要在 design.md §4 的 Phase 2A（探索模式）中运行：

| 阶段 | Phase 映射 | 说明 |
|------|-----------|------|
| Sense | Phase 2A | 自由探索，不修改状态 |
| Ideate | Phase 2A | 对话/文档/代码发现，产出候选 |
| Structure | Phase 2A → 写入 | 候选确认后写入 .devpace/ |
| Refine | Phase 2A | 深化已有实体 |
| Validate | Phase 2A | align 只读分析（仅写趋势数据到 insights.md） |
| Ready | Phase 2A → Phase 2B | 就绪度达标后，用户可切换到推进模式（/pace-dev） |

Phase 0（/pace-init）为 Process Model 提供运行基础（.devpace/ 结构），Phase 3（/pace-change）可在任何阶段中断并修改已有实体，Phase 4（/pace-plan + /pace-retro）提供迭代级的宏观调度。

### 三级反馈循环的实现

| 级别 | 理论定义 | pace-biz 实现方式 | 实现机制 |
|------|---------|------------------|---------|
| **L1 微循环** | 阶段内迭代 | discover Step 2 多轮追问（2-4 轮） | AskUserQuestion 驱动的多轮对话 |
| | | refine Step 2 按维度逐轮精炼 | 仅提问缺失维度，已完善的跳过 |
| **L2 中循环** | 相邻阶段回退 | refine 后发现分解不合理 → 回退 decompose | 动态推荐（refine Step 4）引导 |
| | | align 发现空 Epic → 回退 decompose | 报告内联引导命令 |
| **L3 宏循环** | 跨阶段调整 | align 发现方向偏差 → 重新评估 opportunity | 报告建议 + 趋势追踪（连续退化警告） |

**实现特征**：三级反馈循环在 pace-biz 中通过**下游引导推荐**隐式实现，而非显式的状态回退机制。每个子命令的输出末尾根据当前状态动态推荐下一步，用户通过执行推荐命令完成循环。这是 UX 原则"零摩擦"的体现——不强制用户理解循环机制，只需跟随推荐即可。

### 空参数引导的阶段感知逻辑

空参数调用 `/pace-biz` 时，SKILL.md 内联逻辑实现了 Process Model 的阶段推断：

```
扫描项目状态
├── 有未评估 Opportunity          → Sense 阶段 → 推荐 opportunity/epic
├── 有规划中 Epic 需分解          → Structure 阶段 → 推荐 decompose
├── BR/PF 平均就绪度 < 60%       → Refine 阶段 → 推荐 refine Top-3
├── 距上次 align > 5 天          → Validate 阶段 → 推荐 align
└── 以上均不满足                  → Sense/Ideate → 上下文发现型推荐
    ├── 检测到 .md/.txt 文档     → 推荐 import
    ├── 检测到 src/lib/ 代码     → 推荐 infer
    └── 其他                     → 推荐 discover
```

这个优先级序列隐含了 Process Model 的阶段顺序：先处理上游未完成项（Sense），再推进中间层（Structure/Refine），最后检查整体质量（Validate）。

---

## §2 Data Model 落地方案

> 理论定义详见 `biz-analysis-models.md §2`。

### 六层实体层级 → devpace 实体存储

| 层级 | 实体 | 存储位置 | 创建者 | 管理者 |
|------|------|---------|--------|--------|
| Vision | 愿景 | project.md 愿景 section | /pace-init | /pace-init |
| OBJ | 业务目标 | project.md 业务目标 section | /pace-init | /pace-change modify |
| Theme (Epic) | 专题 | epics/EPIC-xxx.md（独立文件） | /pace-biz epic | /pace-change |
| BR | 业务需求 | project.md 功能树行 + requirements/BR-xxx.md（溢出） | /pace-biz decompose | /pace-biz refine, /pace-change |
| PF | 产品功能 | project.md 功能树行 | /pace-biz decompose | /pace-biz refine, /pace-change |
| CU (CR) | 变更单元 | backlog/CR-xxx.md（独立文件） | /pace-dev | /pace-dev, /pace-review |

**存储策略设计决策**：

- **Epic 使用独立文件**：因为 Epic 承载 MoS、BR 列表、利益相关者等结构化信息，行内无法容纳。
- **BR 使用行 + 溢出**：大多数 BR 在功能树中一行足够；验收标准/关键流程超过容量时触发溢出到 `requirements/BR-xxx.md`。
- **PF 始终内联**：PF 在功能树中一行包含名称、用户故事和 CR 关联，无需独立文件。
- **CR 使用独立文件**：CR 承载事件表、质量检查清单等大量开发过程数据。

### 四级成熟度的隐式实现策略

Data Model 定义了 M0-M3 四级成熟度，但 pace-biz 将其实现为**隐式评估**而非显式字段：

| 成熟度 | 理论特征 | pace-biz 判断方式 | 对应实现 |
|--------|---------|-----------------|---------|
| **M0 Skeleton** | 仅名称和编号 | 就绪度 < 30%——无用户故事/验收标准/关联 | discover/import/infer 初创实体 |
| **M1 Intentional** | 有描述和优先级 | 就绪度 30-59%——有描述但缺验收标准 | decompose 产出（带名称+优先级） |
| **M2 Defined** | 有验收标准和关联 | 就绪度 60-79%——有验收标准但部分维度缺失 | refine 中间产物 |
| **M3 Ready** | 全维度覆盖 | 就绪度 >= 80% | refine 完成产物 |

**实现机制**：`readiness-score.md`（权威源）定义的六维度加权评分（用户故事/验收标准/优先级/上游关联/异常边界/NFR）是成熟度的量化代理。refine Step 1 展示就绪度评分，align Step 2.8 统计就绪度分布——两者共同实现了 Data Model 的成熟度可见性，但用自然语言（"骨架级/基本就绪/就绪"）而非 M0-M3 标签。

**设计决策**：M0-M3 不暴露给用户（biz-analysis-models.md "重要"标注），就绪度百分比是用户侧的等效表达。这避免了引入新概念的认知负担。

### 五种关系类型的实现

| 关系类型 | 理论定义 | pace-biz 实现 | 实现文件 |
|---------|---------|--------------|---------|
| **Decomposition** | 上→下分解 | project.md 功能树缩进层级 + Epic 文件 BR 列表 | decompose-epic.md Step 4-5, decompose-br.md Step 4 |
| **Association** | 同层依赖 | Epic 文件"业务需求"表的"依赖"列 | decompose-epic.md Step 3.4 |
| **Traceability** | 下→上追溯 | `<!-- source: ... -->` 溯源标记 + 功能树层级 | 所有写入操作的溯源标记 |
| **Conflict** | 同层矛盾 | import Step 3 的 CONFLICT 分类 | biz-procedures-import.md Step 3 |
| **Enrichment** | 外→内补充 | import Step 3 的 ENRICHMENT 分类 | biz-procedures-import.md Step 3 |

**实现深度差异**：

- Decomposition 和 Traceability 是完整实现（功能树结构天然承载）。
- Association 仅在 Epic→BR 层有显式依赖记录；BR→PF 层和 PF→PF 层无依赖字段。
- Conflict 和 Enrichment 仅在 import 的 Reconcile 阶段触发，discover 和 infer 不做冲突检测。

---

## §3 Discovery Model 落地方案

> 理论定义详见 `biz-analysis-models.md §3`。

### 三类输入源 → 三个子命令

| 输入源 | 子命令 | 交互模式 | 核心差异 |
|--------|--------|---------|---------|
| **Conversational** | `discover` | 多轮对话，Claude 引导（4-8 轮） | 渐进深入，适合模糊想法 |
| **Document** | `import` | 批量处理，结构化提取 | 高效，适合已有文档 |
| **Artifact** | `infer` | 自动分析，反向推断 | 无需用户输入，适合已有代码 |

### 六阶段管道的逐阶段实现对比

| 管道阶段 | discover 实现 | import 实现 | infer 实现 |
|---------|--------------|------------|------------|
| **Ingest** | Step 1 目标框定（AskUserQuestion 1-2 轮） | Step 1 源文件摄入（读取 .md/.txt + 类型自动检测） | Step 1 代码结构分析（目录扫描 + 框架检测） |
| **Extract** | Step 2 功能头脑风暴（2-4 轮对话 + 模式识别辅助） | Step 2 实体提取（通用映射表 + 扩展提取规则） | Step 2 信号挖掘（注释信号 + 配置信号 + Git 增强） |
| **Reconcile** | Step 4a 轻量合并检查（标题关键词快筛，重叠 > 70% 标注提醒） | Step 3 完整合并分析（NEW/DUPLICATE/ENRICHMENT/CONFLICT 四分类） | Step 3 差距分析（未追踪/未实现/技术债务/文档漂移 四分类） |
| **Confirm** | Step 4b 候选树展示（用户可调整层级/优先级/名称） | Step 4 合并计划展示（accept all / reject all / 逐条选择） | Step 4 报告与确认（逐项 accept/skip） |
| **Persist** | Step 5 写入 .devpace/（复用 opportunity/epic 创建逻辑） | Step 5 执行写入（追加功能树 + 溯源标记） | Step 5 写入 .devpace/（追加功能树 + 溯源标记） |
| **Guide** | Step 6 下游引导（骨架级实体数 + refine/decompose/align/plan 推荐） | Step 6 下游引导（新增/丰富/跳过统计 + 推荐） | Step 6 下游引导（追踪/债务/未实现统计 + 推荐） |

### Reconcile 差异化策略

三个子命令的 Reconcile 深度不同，这是有意的设计决策：

| 子命令 | Reconcile 深度 | 设计理由 |
|--------|---------------|---------|
| **import** | 完整四分类 + 两层判断（快筛 + 语义精判） + 阈值控制 | 文档导入量大，重复/冲突概率高，需要精确合并 |
| **discover** | 轻量快筛（标题关键词重叠 > 70% 标注提醒，不阻断） | 对话式探索中打断用户思路的代价高于漏过少量重复 |
| **infer** | 差距分析（四分类：未追踪/未实现/技术债务/文档漂移） | 代码推断的实体形态与功能树不同（模块 vs PF），需要专属分类框架 |

**合并策略契约**：import 的完整合并逻辑定义在 `knowledge/_schema/auxiliary/merge-strategy.md`（权威源）。

### 智能路由逻辑

路由发生在两个层次：

**第一层：空参数引导**（SKILL.md 空参逻辑）
```
.md/.txt 文档存在   → 推荐 import
src/lib/ 代码存在   → 推荐 infer
活跃 Epic 待分解    → 推荐 decompose
其他               → 推荐 discover
```

**第二层：discover 内部路由**（biz-procedures-discover.md Step 0）
```
用户输入含文件路径   → 建议转向 import（用户可拒绝）
用户输入含代码关键词  → 建议转向 infer（用户可拒绝）
用户确认继续        → 正常进入 discover 对话
```

两层路由形成"推荐 → 确认"的容错机制：第一层基于项目状态推荐最可能的入口，第二层在用户已选 discover 后仍可根据输入内容二次引导。

---

## §4 Quality Model 落地方案

> 理论定义详见 `biz-analysis-models.md §4`。

### 四维度实现映射

| 维度 | 名称 | 实现子命令 | 实现细节 | 权威源 |
|------|------|-----------|---------|--------|
| **D1** | Readiness（就绪度） | `refine` Step 1 + `align` Step 2.8 | 六维度加权评分：用户故事(20-25%)/验收标准(25-30%)/优先级(15%)/上游关联(10-15%)/异常边界(10-15%)/NFR(10%) | `_schema/auxiliary/readiness-score.md` |
| **D2** | Alignment（对齐度） | `align` Step 2.1-2.9 | 九维检查：OBJ 覆盖率/孤立实体/MoS 完整性/价值链完整性/优先级分布/依赖健康/MoS 达成度/就绪度分布/利益相关者覆盖 | biz-procedures-align.md |
| **D3** | Completeness（完整度） | `view` Step 2 覆盖率摘要 + `align` Step 2.4 | 四层覆盖率：OBJ→Epic/Epic→BR/BR→PF/PF→CR | biz-procedures-view.md Step 2 |
| **D4** | Health（健康度） | `align` Step 4 趋势追踪 | 历史快照对比 + 连续退化警告（3 次恶化触发） | biz-procedures-align.md Step 4 |

### 维度间协同的实现

理论模型定义了 D1→D2←D3→D4 的协同关系，pace-biz 的实现路径如下：

```
refine（D1 就绪度提升）
  ↓ 就绪度变化触发动态推荐
align（D2 对齐度检查）
  ├── 调用 readiness-score.md 计算 D1 → 汇聚为 D2 的"需求就绪度分布"检查项
  ├── 调用 view 的覆盖率逻辑 → D3 的"价值链完整性"检查项
  └── 写入 insights.md 趋势数据 → D4 的"历史对比"
view（D3 完整度展示）
  └── 覆盖率摘要段：OBJ→Epic/Epic→BR/BR→PF/PF→CR 四层统计
```

**关键实现**：`align` 是 Quality Model 的集成点——它在单次执行中覆盖 D1（就绪度分布统计）、D2（九维对齐检查）、D3（价值链完整性）、D4（趋势对比），并将结果写入 `metrics/insights.md` 供后续追踪。

### Quality Model vs 质量门体系

Quality Model 和 design.md §6 的质量门（Gate 1/2/3）是互补关系，覆盖不同层面：

| 体系 | 覆盖层面 | 评估对象 | 触发时机 | 实现方式 |
|------|---------|---------|---------|---------|
| **Quality Model** | 业务规划层（OPP→Epic→BR→PF） | 需求质量 | /pace-biz 子命令执行时 | 评分 + 报告 + 推荐 |
| **Gate 1** | 开发层（CR） | 代码质量 | /pace-dev developing→verifying | 自动化检查（测试/lint） |
| **Gate 2** | 审核层（CR） | 交付质量 | /pace-review verifying→in_review | 对比意图一致性 |
| **Gate 3** | 人类决策层 | 最终确认 | /pace-review in_review→approved | 人类审批 |

**衔接点**：Quality Model 的 D1 就绪度（>= 80%）是进入 /pace-dev 的软前提——不阻断，但推荐先精炼。Gate 1/2/3 是 CR 状态机的硬门禁——必须通过。两者形成从"需求足够好"到"代码足够好"的质量链。

---

## §5 模型间协同

> 理论定义详见 `biz-analysis-models.md §5`。

以下是三个典型场景中多模型如何协同驱动 pace-biz 行为：

### 场景 1：空参数引导

用户无参数调用 `/pace-biz` 时，三个模型协同推断最优推荐：

| 模型 | 贡献 | 实现位置 |
|------|------|---------|
| Process Model | 判断当前所处阶段（Sense/Structure/Refine/Validate） | SKILL.md 空参逻辑：扫描 OPP/Epic/就绪度/align 时间 |
| Data Model | 扫描实体成熟度分布，发现骨架级实体 | SKILL.md 空参逻辑：BR/PF 就绪度 < 60% → refine |
| Quality Model | 检查各维度得分，识别最薄弱环节 | SKILL.md 空参逻辑：距上次 align > 5 天 → align |

**协同逻辑**：优先级序列（OPP → decompose → refine → align → discover）本质上是 Process Model 阶段顺序 × Data Model 成熟度检测 × Quality Model 维度检查的综合排序。

### 场景 2：创建后引导

discover/import/infer 完成实体创建后的引导推荐：

| 模型 | 贡献 | 实现位置 |
|------|------|---------|
| Discovery Model | Persist 完成 → 进入 Guide 阶段 | 各 procedures Step 6 |
| Data Model | 统计新创建实体的骨架级数量（M0） | Step 6："其中 K 个为骨架级" |
| Process Model | 推荐下一阶段（Structure 或 Refine） | Step 6：推荐 decompose/refine/align |

### 场景 3：精炼反馈

refine 完成后的动态推荐：

| 模型 | 贡献 | 实现位置 |
|------|------|---------|
| Quality Model D1 | 就绪度前后对比 | refine Step 4："就绪度 X% → Y%" |
| Process Model | 就绪度达标 → Ready → /pace-dev | refine Step 4：>= 80% 推荐开发 |
| Process Model | 就绪度不达标 → 继续 Refine 或回退 Structure | refine Step 4：60-79% 建议继续精炼 |
| Quality Model D2 | 距上次 align 过久 → 建议 Validate | refine Step 4："距上次 align 超 5 次精炼操作 → align" |

---

## §6 当前差距与优化方案

### 差距 1：模型文件的"悬空"问题

**问题描述**：`biz-analysis-models.md` 定义了四个理论模型，但它目前仅被两个消费者引用（/pace-theory 运行时读取、本文档开发参考）。pace-biz 的 procedures 文件没有引用它——模型智能分散在各 procedures 的具体步骤中，与理论定义之间缺少显式关联。

**风险**：模型定义与实现逐步漂移。例如，未来修改 Process Model 的阶段定义时，开发者可能遗漏对空参引导逻辑的同步更新。

**优化方案（P1 推荐）**：✅ 已完成
- 在本文档的映射表中标注具体行号/步骤引用，作为变更时的检查清单
- 在同步检查清单中新增"模型定义变更"同步链路 → `.claude/references/sync-checklists.md`
- 预期收益：模型变更时有明确的影响追踪路径
- 实施复杂度：低（文档层面工作，不涉及 Skill 逻辑修改）

### 差距 2：隐式实现的漂移风险

**问题描述**：成熟度（M0-M3）和反馈循环（L1-L3）都是隐式实现——通过就绪度评分和动态推荐间接体现。没有代码或配置层面的显式引用来锚定这些概念。

**风险**：开发者修改 refine 或 align 时，可能无意中破坏成熟度判断逻辑或反馈循环的推荐链路。

**优化方案（P2 可选）**：降级——上轮已内联阶段名和成熟度标签，sync-checklists 补全同步链路，隐式漂移风险已大幅降低
- 在 procedures 文件的关键步骤旁添加模型注释（如 `<!-- Data Model: M1→M2 transition -->`），作为实现意图标记
- 预期收益：开发者修改时能看到模型层面的设计意图
- 实施复杂度：低（注释层面，不影响 LLM 执行行为）
- 权衡：增加了文件内容量，需评估对上下文预算的影响

### 差距 3：metrics.md 与 Quality Model 的弱关联

**问题描述**：`knowledge/metrics.md` 定义了 8 类度量指标（质量保障/缺陷管理/业务价值对齐/DORA 等），Quality Model 的 D4 健康度通过 `align` 趋势追踪实现并写入 `metrics/insights.md`。但两者之间的关联是隐式的：
- metrics.md 的"业务价值对齐指标"（MoS 达成率/价值链完整率）与 Quality Model D2/D3 高度重叠，但没有显式声明对应关系
- align 写入 insights.md 的趋势数据格式与 metrics.md 的指标定义不直接对应

**风险**：/pace-retro（metrics.md 的主要消费者）和 /pace-biz align（Quality Model D4 的实现者）可能产出不一致的度量视图。

**优化方案（P1 推荐）**：✅ 已完成
- 在 metrics.md 的"业务价值对齐指标"section 添加 Quality Model 维度映射注释 + QM 维度列
- 统一 align 趋势数据与 metrics.md 指标定义的术语（"MoS 完整性"→"MoS 定义率"消歧 + 新增"MoS 达成度"/"价值链完整率"列）
- 预期收益：度量体系内聚性提升，/pace-retro 可直接消费 align 的趋势数据
- 实施复杂度：中（需要同时调整 metrics.md 和 biz-procedures-align.md Step 4）

### 优先级排序

| 优先级 | 差距 | 方案 | 收益 | 复杂度 |
|--------|------|------|------|--------|
| **P1** | 差距 1（悬空问题） | sync-checklists 新增模型同步链路 | 防止模型-实现漂移 | 低 |
| **P1** | 差距 3（弱关联） | metrics.md + align 术语统一 | 度量体系内聚 | 中 |
| **P2** | 差距 2（隐式实现） | procedures 文件添加模型意图注释 | 开发者可见性 | 低 |
