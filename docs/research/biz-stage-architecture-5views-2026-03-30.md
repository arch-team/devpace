# devpace 业务需求阶段——架构 5 视图

> 分析日期：2026-03-30
> 方法论：Kruchten 4+1 视图模型
> 范围：Vision / OBJ / Opportunity / Epic / BR / PF 六实体全生命周期

## 导航指南

| 你是谁 | 先看哪里 | 关注什么 |
|--------|---------|---------|
| **产品经理** | 视图 1 场景 + 视图 2 逻辑 | 用户旅程、实体关系、MoS 双维度、就绪度 |
| **开发者** | 视图 4 开发 + 视图 5 物理 | 文件依赖、procedures 规范、.devpace/ 布局 |
| **架构师** | 视图 3 过程 + 附录一致性矩阵 | 事件驱动、Hook 守护、跨会话、数据流 |

## Fig-0 五视图关系总览

```mermaid
flowchart TD
    classDef view fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1

    S["1 场景视图\n用户如何使用"]
    L["2 逻辑视图\n实体与数据如何组织"]
    P["3 过程视图\n运行时如何工作"]
    D["4 开发视图\n代码如何组织"]
    PH["5 物理视图\n文件如何布局"]

    S -- "用例驱动实体设计" --> L
    L -- "状态机驱动工作流" --> P
    L -- "实体映射到代码组件" --> D
    P -- "运行时映射到存储" --> PH
    D -- "代码操作物理文件" --> PH
    PH -. "文件变化反馈到用户" .-> S

    class S,L,P,D,PH view
```

---

## 视图 1：场景视图 (Scenario View)

> 回答：**用户如何使用业务需求阶段的各种能力？**

### 1.1 角色与用例矩阵

devpace 通过 `project.md` 的 `preferred-role` 字段识别角色（缺省 Dev），角色仅影响**追问方向、展示维度、措辞风格**，不改变核心流程。

| 角色 | 典型用例 | 追问侧重 | 展示侧重 |
|------|---------|---------|---------|
| **Biz Owner** | 定义 OBJ、评估 OPP、检查 MoS 达成 | 商业价值、ROI | MoS 进度、营收指标 |
| **PM** | 分解 Epic/BR、精炼需求、规划迭代 | 用户场景、优先级、竞品 | PF 完成度、依赖 |
| **Dev** | 推断代码功能、快速创建 CR | （默认，零改变） | CR 状态、技术复杂度 |
| **Tester** | 补充验收标准、边界条件 | 可测试性、边界 | 验收标准数、Gate 2 |
| **Ops** | 评估运维影响、部署需求 | 运维影响、基础设施 | Release 状态 |

**权威源**：`knowledge/role-adaptations.md`

### 1.2 核心用户旅程

```mermaid
journey
    title 旅程 A：从零到一（完整正向路径）
    section 初始化
      pace-init full: 5: 用户
      定义 Vision + OBJ: 4: 用户
    section 业务机会
      pace-biz opportunity: 5: 用户, Claude
      捕获 OPP: 5: Claude
    section 专题创建
      pace-biz epic OPP-xxx: 4: 用户, Claude
      创建 EPIC + 关联 OBJ: 5: Claude
    section 需求分解
      pace-biz decompose EPIC: 4: 用户, Claude
      生成 BR 列表: 5: Claude
      pace-biz decompose BR: 4: 用户, Claude
      生成 PF 列表: 5: Claude
    section 精炼与检查
      pace-biz refine BR/PF: 3: 用户
      就绪度提升到 80%+: 5: Claude
      pace-biz align: 4: Claude
    section 移交开发
      pace-plan next: 5: 用户, Claude
      pace-dev: 5: 用户, Claude
```

**五条用户旅程速查**：

| 旅程 | 路径 | 适用场景 |
|------|------|---------|
| **A 从零到一** | `init full -> opportunity -> epic -> decompose -> refine -> align -> /pace-plan` | 全新项目，从战略到执行 |
| **B 探索发现** | `discover（多轮对话）-> decompose -> /pace-plan` | 模糊想法，需要头脑风暴 |
| **C 文档导入** | `import <文档> -> align -> /pace-plan` | 已有 PRD/会议纪要 |
| **D 代码反推** | `infer -> align -> /pace-dev` | 已有代码库，补充追踪 |
| **E 快速注入** | `/pace-change add`（跳过 OPP/Epic） | 日常零散需求 |

### 1.3 空参数智能引导

当用户无参数调用 `/pace-biz` 时，系统基于项目状态自动推荐（阶段名不输出给用户）：

```mermaid
stateDiagram-v2
    direction LR

    [*] --> Sense : 无 OPP 且无 Epic/BR
    [*] --> Ideate : 有未转化 OPP
    [*] --> Structure : 有 Epic 未分解
    [*] --> Refine : 平均就绪度 < 60%
    [*] --> Validate : 距上次 align > 5天
    [*] --> Ready : 就绪度 >= 80%

    Sense --> Ideate : OPP 已捕获
    Ideate --> Structure : Epic 已创建
    Structure --> Refine : BR/PF 已分解
    Refine --> Validate : 就绪度提升
    Validate --> Ready : 对齐通过
    Ready --> [*] : 移交 pace-plan/pace-dev

    Validate --> Sense : 发现 OBJ 未覆盖
    Validate --> Structure : 发现空 Epic
    Validate --> Refine : P0 就绪度不足

    note right of Sense : 推荐 discover/import/infer
    note right of Ideate : 推荐 epic/opportunity
    note right of Structure : 推荐 decompose
    note right of Refine : 推荐 refine Top-3
    note right of Validate : 推荐 align
    note right of Ready : 推荐 pace-plan/pace-dev
```

**信号驱动**：S16（Epic 需分解）、S17（未评估 OPP）、S18（功能树稀疏）、S19（范围未定义）——定义在 `knowledge/_signals/signal-priority.md`。

### 1.4 关键设计决策

| 决策 | 选择 | WHY |
|------|------|-----|
| 10 子命令统一入口 | 单 Skill 多子命令 | 降低认知负担（一个命令），利用空参数引导自动推荐 |
| 空参数不报错 | 生命周期感知推荐 | P1 零摩擦——用户不需要知道"应该做什么" |
| 5 角色正交适配 | 角色仅影响输出层 | 单一代码路径 + 输出层适配，避免 5 倍维护成本 |

---

## 视图 2：逻辑视图 (Logical View)

> 回答：**实体、关系、状态机、数据流如何组织？**

### 2.1 实体关系模型

```mermaid
erDiagram
    Vision ||--o{ OBJ : "一对多"
    OBJ ||--o{ Epic : "主/副关联"
    OBJ ||--o{ BR : "直挂(无Epic时)"
    Epic ||--o{ BR : "一对多"
    BR ||--o{ PF : "一对多"
    PF ||--o{ CR : "一对多"
    OPP |o--o| Epic : "评估转化"

    Vision {
        string blockquote "一句话愿景摘要"
        string target_user "目标用户"
        string core_problem "核心问题"
        string differentiation "差异化(渐进)"
        string north_star "北极星指标(渐进)"
    }
    OBJ {
        string id "OBJ-xxx"
        enum type "business|product|tech|growth|efficiency|compliance"
        enum status "活跃|已达成|已废弃"
        list mos_customer "客户价值 MoS"
        list mos_business "企业价值 MoS"
    }
    Epic {
        string id "EPIC-xxx"
        enum status "规划中|进行中|已完成|已搁置"
        string background "背景(2-3句)"
        list mos "双维度 MoS"
        table stakeholders "利益相关者(可选)"
    }
    OPP {
        string id "OPP-xxx"
        enum source "用户反馈|竞品观察|技术发现|市场趋势|内部洞察"
        enum status "评估中|已采纳|已搁置|已拒绝"
    }
    BR {
        string id "BR-xxx"
        enum priority "P0|P1|P2"
        enum status "待开始|进行中|已完成|暂停"
        list mos "双维度 MoS"
        list key_flow "关键流程(可选)"
    }
    PF {
        string id "PF-xxx"
        string user_story "用户故事"
        list acceptance "验收标准"
        list boundary "边界"
    }
    CR {
        string id "CR-xxx"
        enum status "created|developing|verifying|in_review|approved|merged|released"
    }
```

### 2.2 三种文件存在模式

```mermaid
flowchart LR
    classDef always fill:#C8E6C9,stroke:#388E3C,color:#1B5E20
    classDef overflow fill:#FFF9C4,stroke:#F9A825,color:#333
    classDef single fill:#BBDEFB,stroke:#1976D2,color:#0D47A1

    subgraph A["始终独立文件"]
        direction TB
        V["vision.md"] --> V1["创建即独立"]
        O["OBJ-xxx.md"] --> O1["创建即独立"]
        E["EPIC-xxx.md"] --> E1["创建即独立"]
    end

    subgraph B["溢出模式(内联->独立)"]
        direction TB
        BR_I["BR 内联\nproject.md 树一行"] -->|"3+PF / >5行 / modify"| BR_O["BR-xxx.md\nrequirements/"]
        PF_I["PF 内联\nproject.md 树一行"] -->|">15行 / 3+CR / modify"| PF_O["PF-xxx.md\nfeatures/"]
    end

    subgraph C["单文件集中"]
        direction TB
        OPP["opportunities.md\n所有 OPP 集中管理"]
    end

    class V,O,E,V1,O1,E1 always
    class BR_I,BR_O,PF_I,PF_O overflow
    class OPP single
```

**溢出是单向不可逆的**——一旦溢出不回退。`project.md` 价值功能树始终是统一入口。

### 2.3 状态机集合

```mermaid
stateDiagram-v2
    state "OPP 状态机" as OPP_SM {
        [*] --> 评估中
        评估中 --> 已采纳 : epic 转化
        评估中 --> 已搁置 : 用户延后
        评估中 --> 已拒绝 : 用户拒绝
        已搁置 --> 评估中 : 恢复评估
    }

    state "Epic 状态机(聚合自BR)" as EPIC_SM {
        [*] --> E_规划中
        E_规划中 --> E_进行中 : 有活跃CR
        E_进行中 --> E_已完成 : 全BR完成
        E_进行中 --> E_已搁置 : 显式搁置
        E_已搁置 --> E_进行中 : resume
    }

    state "BR 状态机(聚合自PF)" as BR_SM {
        [*] --> B_待开始
        B_待开始 --> B_进行中 : 有活跃CR
        B_进行中 --> B_已完成 : 全PF完成
        B_进行中 --> B_暂停 : 显式暂停
        B_暂停 --> B_进行中 : resume
    }

    state "OBJ 状态机(人类确认)" as OBJ_SM {
        [*] --> 活跃
        活跃 --> 已达成 : retro确认
        活跃 --> 已废弃 : 战略调整
    }
```

**自底向上聚合链**：

```
CR 状态 (Gate/手动)
  |  全merged→完成; 有developing→进行中; 全paused→暂停
  v
PF 状态 = f(关联 CR)
  |  同规则
  v
BR 状态 = f(关联 PF)
  |  同规则
  v
Epic 状态 = f(关联 BR)
  |  人类确认
  v
OBJ 状态 (/pace-retro 建议 + 人类确认)
```

### 2.4 渐进丰富模型

```mermaid
flowchart TD
    classDef trigger fill:#E8F5E9,stroke:#4CAF50,color:#1B5E20
    classDef entity fill:#FFF9C4,stroke:#F9A825,color:#333

    INIT["pace-init\n创建桩"] --> PM["project.md\n(桩状态)"]
    INIT --> VM["vision.md\n(桩状态)"]

    FULL["pace-init full\n阶段2"] --> VM2["vision.md\n核心四要素"]
    FULL --> OBJ["OBJ-xxx.md\n类型+MoS"]
    FULL --> OPP_E["opportunities.md\n空文件"]

    BIZ_OPP["pace-biz\nopportunity"] --> OPP_F["opportunities.md\n+OPP条目"]
    BIZ_EPIC["pace-biz\nepic"] --> EPIC_F["EPIC-xxx.md\n背景+MoS"]
    BIZ_EPIC --> PM2["project.md\n+Epic链接"]

    DEC_E["pace-biz\ndecompose EPIC"] --> PM3["project.md\n+BR行"]
    DEC_B["pace-biz\ndecompose BR"] --> PM4["project.md\n+PF行"]

    REF["pace-biz\nrefine"] --> PM5["project.md/BR/PF\n验收标准+边界+故事"]

    RETRO["pace-retro"] --> VM3["vision.md\n北极星当前值"]
    RETRO --> OBJ2["OBJ-xxx.md\nMoS进度"]

    class INIT,FULL,BIZ_OPP,BIZ_EPIC,DEC_E,DEC_B,REF,RETRO trigger
    class PM,VM,VM2,OBJ,OPP_E,OPP_F,EPIC_F,PM2,PM3,PM4,PM5,VM3,OBJ2 entity
```

**MoS 双维度贯穿三层**：

| 层级 | MoS 粒度 | 示例 | 评估时机 |
|------|---------|------|---------|
| OBJ | 战略级 | 月活 MAU、订阅收入 | /pace-retro |
| Epic | 专题级 | 注册转化率、支持成本 | /pace-retro |
| BR | 业务结果 | 登录成功率 > 95% | /pace-retro |
| PF | **非 MoS**，是验收标准 | 邮箱+密码，>=8位 | Gate 2 |

### 2.5 就绪度评分模型

6 维度加权评分（权威源：`knowledge/_schema/auxiliary/readiness-score.md`）：

| 维度 | BR 权重 | PF 权重 | 达标条件 |
|------|:-------:|:-------:|---------|
| 用户故事/描述 | 20% | 25% | 非空且 >10 字 |
| 验收标准 | 25% | 30% | >= 2 条 |
| 优先级 | 15% | 15% | 已评估（非"--"） |
| 上游关联 | 15% | 10% | 有 Epic/OBJ 关联 |
| 异常/边界 | 15% | 10% | 有异常或边界描述 |
| NFR 考量 | 10% | 10% | 有非功能需求 |

**四档成熟度标签**：骨架级(0-20%) / 基本级(21-59%) / 详细级(60-79%) / 就绪级(>=80%)

### 2.6 关键设计决策

| 决策 | 选择 | WHY |
|------|------|-----|
| 溢出模式 | BR/PF 内联→阈值触发→独立文件 | 小项目避免过度文件化，大项目自然成长 |
| 状态自底向上聚合 | 上层状态由下层推算 | 消除状态不一致，减轻人工维护 |
| OBJ 仅 3 态 | 活跃/已达成/已废弃 | 战略级无"暂停"——等价于优先级调整 |
| MoS 双维度贯穿三层 | 客户价值+企业价值 | 从战略到执行保持价值视角一致 |
| OPP 段落式非表格 | 二级标题+列表字段 | 来源详情变长，表格无法承载 |

---

## 视图 3：过程视图 (Process View)

> 回答：**运行时工作流、事件驱动、跨会话恢复如何工作？**

### 3.1 子命令执行流水线

以 `decompose EPIC` 为例展示完整时序（其他子命令结构类似）：

```mermaid
sequenceDiagram
    actor U as 用户
    participant S as pace-biz SKILL.md
    participant H as Hook 层
    participant A as pace-pm Agent
    participant F as .devpace/ 文件

    U->>S: /pace-biz decompose EPIC-001
    S->>S: 公共前置：读 state.md + project.md + role

    S->>A: fork 到 pace-pm（context: fork）
    A->>F: Step 1: 读取 epics/EPIC-001.md
    A->>F: Step 2: 确认状态为规划中/进行中

    A->>U: Step 3: 展示 Epic 背景，建议 2-5 个 BR
    U->>A: 确认/调整分解方案

    A->>H: Step 4: Write project.md（追加 BR 行）
    H->>H: pace-biz-scope-check：目标在 .devpace/ ？
    H-->>A: exit 0 放行
    A->>F: 写入 project.md 价值功能树

    A->>H: Step 5: Write epics/EPIC-001.md（更新 BR 表）
    H-->>A: exit 0 放行
    A->>F: 更新 Epic 文件 BR 表格

    A->>U: Step 6: 输出分解结果 + 依赖可视化
    A->>U: 下游引导：decompose BR / pace-plan
```

**子命令读写矩阵**（摘要）：

| 子命令 | 读取 | 写入 |
|--------|------|------|
| opportunity | project.md, opportunities.md | opportunities.md |
| epic | opportunities.md, project.md | epics/, project.md, opportunities.md |
| decompose EPIC | epics/, project.md | project.md, epics/ |
| decompose BR | requirements/, project.md | project.md, requirements/ |
| refine | project.md, requirements/ | project.md, requirements/ |
| discover | state.md, project.md, opportunities.md | 全链路 + scope-discovery.md |
| import | project.md, insights.md | project.md, epics/, requirements/ |
| infer | project.md, src/ | project.md |
| align | project.md, epics/, requirements/, opportunities.md | metrics/insights.md |
| view | project.md, epics/, requirements/, opportunities.md | **无（只读）** |

### 3.2 事件驱动守护机制

```mermaid
sequenceDiagram
    actor U as 用户
    participant SE as skill-eval.mjs<br/>(UserPromptSubmit)
    participant SK as pace-biz SKILL
    participant PT as pre-tool-use.mjs<br/>(全局 Hook)
    participant SC as pace-biz-scope-check<br/>(Skill Hook)
    participant EP as Epic Prompt Hook<br/>(Skill Hook)
    participant F as .devpace/

    U->>SE: "帮我创建一个登录专题"
    SE->>SE: 关键词匹配：专题/Epic -> pace-biz
    SE->>SK: 路由到 /pace-biz

    SK->>SK: 解析为 epic 子命令
    SK->>F: Write epics/EPIC-002.md

    Note over PT,SC: 两层 PreToolUse Hook 依次触发

    F->>PT: PreToolUse 事件
    PT->>PT: 探索模式检查：pace-biz 是管理类 Skill，允许写 .devpace/
    PT-->>F: 放行

    F->>SC: PreToolUse 事件（Skill 级）
    SC->>SC: 目标路径 .devpace/epics/EPIC-002.md -> 在范围内
    SC-->>F: exit 0 放行

    F->>EP: PreToolUse 事件（path: epics/EPIC-*.md）
    EP->>EP: Prompt 检查：OBJ 关联存在？MoS 可度量？
    EP-->>F: PASS 放行

    F->>F: 写入成功
```

**四层 Hook 守护总览**：

| 层级 | Hook | 触发事件 | 守护内容 |
|------|------|---------|---------|
| 全局路由 | skill-eval.mjs | UserPromptSubmit | 关键词 -> Skill 映射 |
| 全局守护 | pre-tool-use.mjs | PreToolUse | 探索模式 IR-1 保护 |
| Skill 范围 | pace-biz-scope-check.mjs | PreToolUse(Write/Edit) | 仅允许写 .devpace/ |
| Skill 质量 | Epic Prompt Hook | PreToolUse(Write EPIC-*.md) | OBJ 关联 + MoS 可度量 |

### 3.3 跨会话恢复机制

discover 子命令是唯一有跨会话中间态的子命令：

```mermaid
stateDiagram-v2
    [*] --> 检查恢复 : /pace-biz discover

    state 检查恢复 {
        [*] --> 有文件 : scope-discovery.md 存在
        [*] --> 无文件 : 不存在
        有文件 --> 过期 : 创建 > 7 天
        有文件 --> 可恢复 : 未过期
        过期 --> 提示用户 : "过期，建议重新开始"
        提示用户 --> 新会话 : 用户选择 new
        提示用户 --> 恢复 : 用户选择 continue
        可恢复 --> 恢复 : 自动续接
    }

    无文件 --> 新会话

    state 新会话 {
        [*] --> 目标框定 : Step 1 (1-2轮)
        目标框定 --> 功能头脑风暴 : Step 2 (2-4轮)
        功能头脑风暴 --> 边界定义 : Step 3 (1-2轮)
    }

    恢复 --> 目标框定 : 阶段=目标框定
    恢复 --> 功能头脑风暴 : 阶段=功能头脑风暴
    恢复 --> 边界定义 : 阶段=边界定义

    边界定义 --> 验证确认 : Step 4 (合并检查+展示)
    验证确认 --> 写入 : Step 5 (全链路创建)
    写入 --> 删除文件 : 删除 scope-discovery.md
    删除文件 --> [*]

    验证确认 --> 用户放弃 : 拒绝所有候选
    用户放弃 --> 删除文件2 : 删除 scope-discovery.md
    删除文件2 --> [*]
```

**恢复机制**：`scope-discovery.md` 的 `## 阶段：xxx` 标记是唯一恢复标识。格式定义见 `knowledge/_schema/process/scope-discovery-format.md`。

### 3.4 子命令间协作模式

```mermaid
flowchart TD
    classDef cmd fill:#E3F2FD,stroke:#1976D2,color:#0D47A1
    classDef file fill:#FFF9C4,stroke:#F9A825,color:#333
    classDef readonly fill:#E8F5E9,stroke:#4CAF50,color:#1B5E20

    OPP_CMD["opportunity"] -->|写入| OPP_F["opportunities.md"]
    OPP_F -->|读取| EPIC_CMD["epic"]
    EPIC_CMD -->|写入| EPIC_F["epics/EPIC-xxx.md"]
    EPIC_CMD -->|更新| PM_F["project.md\n价值功能树"]
    EPIC_CMD -->|更新状态| OPP_F

    EPIC_F -->|读取| DEC_E["decompose EPIC"]
    DEC_E -->|追加 BR| PM_F
    DEC_E -->|更新表格| EPIC_F

    PM_F -->|读取| DEC_B["decompose BR"]
    DEC_B -->|追加 PF| PM_F

    PM_F -->|读取| REF["refine"]
    REF -->|更新内容| PM_F
    REF -->|溢出触发| BR_F["requirements/BR-xxx.md"]

    PM_F -->|读取| ALIGN["align"]
    EPIC_F -->|读取| ALIGN
    OPP_F -->|读取| ALIGN
    ALIGN -->|写入趋势| INS["metrics/insights.md"]

    PM_F -->|读取| VIEW["view"]

    DISC["discover"] -->|全链路写入| PM_F
    DISC -->|写入| OPP_F
    DISC -->|写入| EPIC_F
    IMP["import"] -->|增量追加| PM_F
    INF["infer"] -->|追加| PM_F

    class OPP_CMD,EPIC_CMD,DEC_E,DEC_B,REF,DISC,IMP,INF cmd
    class OPP_F,EPIC_F,PM_F,BR_F,INS file
    class ALIGN,VIEW readonly
```

**核心协作原则**：子命令间**不直接调用**对方 procedures——通过 Schema 约束的 `.devpace/` 文件间接协作（IA-10 契约隔离）。

### 3.5 fork Agent 执行模型

pace-biz 通过 `context: fork` + `agent: pace-pm` 路由到产品经理 Agent：

| 属性 | 值 |
|------|-----|
| Agent | pace-pm |
| Model | sonnet（Agent 定义）/ opus（SKILL.md 覆盖） |
| 工具 | Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion |
| 记忆 | project 级跨会话记忆 |
| 决策模式 | 分析+建议+确认后执行（不自主决策） |
| 沟通风格 | 业务语言，"建议 [行动] 因为 [原因]" 收尾 |
| 降级 | fork 不可用时 inline 静默回退（rules 13.5） |

### 3.6 关键设计决策

| 决策 | 选择 | WHY |
|------|------|-----|
| Skill 专属 Hook | scope-check 仅 pace-biz 上下文触发 | pace-biz 不应改源码，pace-dev 需要。Skill 级避免误拦截 |
| discover 中间态文件 | scope-discovery.md 持久化 | 多轮对话跨会话恢复；7 天过期防僵尸 |
| Epic Prompt Hook | 让 Claude 自行检查修复 | Command Hook 只能阻断；Prompt Hook 可给修复建议 |
| 子命令不直接调用 | Schema 中介 + 信号推荐 | IA-10 契约隔离——独立演进 |

---

## 视图 4：开发视图 (Development View)

> 回答：**代码如何组织？模块间依赖关系？**

### 4.1 组件分层图

```mermaid
flowchart TB
    classDef l6 fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    classDef l5 fill:#FCE4EC,stroke:#C62828,color:#B71C1C
    classDef l4 fill:#FFF3E0,stroke:#F57C00,color:#E65100
    classDef l3 fill:#E3F2FD,stroke:#1976D2,color:#0D47A1
    classDef l2 fill:#E8F5E9,stroke:#388E3C,color:#1B5E20
    classDef l1 fill:#FFFDE7,stroke:#F9A825,color:#333

    subgraph L6["L6 Why — 概念知识（被动加载）"]
        T6["theory.md\nmetrics.md\nrole-adaptations.md"]
    end

    subgraph L5["L5 Must — 行为约束（始终加载）"]
        T5["devpace-rules.md\n双模式 / 铁律 / 角色意识"]
    end

    subgraph L4["L4 Shape — 数据契约（按需加载）"]
        T4A["entity/: vision, obj, epic,\nopp, br, pf, project (8个)"]
        T4B["process/: scope-discovery,\nchecks, iteration (3个)"]
        T4C["auxiliary/: readiness-score,\nmerge-strategy (2个)"]
    end

    subgraph L3["L3 What — 路由层（触发加载）"]
        T3["pace-biz/SKILL.md\n9子命令 + 空参数引导"]
    end

    subgraph L2["L2 How — 操作步骤（条件加载）"]
        T2["10 个 procedures 文件\nopportunity / epic / decompose-epic\ndecompose-br / refine / discover\nimport / infer / align / view"]
    end

    subgraph L1["L1 Instance — 运行时数据"]
        T1[".devpace/ 文件\nproject.md / vision.md / epics/\nrequirements/ / opportunities.md"]
    end

    L6 -.->|"理论依据"| L5
    L5 -->|"约束"| L3
    L4 -->|"格式契约"| L2
    L3 -->|"路由到"| L2
    L2 -->|"操作"| L1

    class T6 l6
    class T5 l5
    class T4A,T4B,T4C l4
    class T3 l3
    class T2 l2
    class T1 l1
```

**依赖方向严格从下层指向上层**：L2 引用 L4 合法；L4 引用 L2 禁止。

### 4.2 文件依赖矩阵

```mermaid
flowchart LR
    classDef skill fill:#E3F2FD,stroke:#1976D2
    classDef proc fill:#E8F5E9,stroke:#388E3C
    classDef schema fill:#FFF3E0,stroke:#F57C00
    classDef know fill:#F3E5F5,stroke:#7B1FA2

    SKILL["SKILL.md\n(路由层)"]

    SKILL --> P1["biz-procedures-\nopportunity"]
    SKILL --> P2["biz-procedures-\nepic"]
    SKILL --> P3["biz-procedures-\ndecompose-epic"]
    SKILL --> P4["biz-procedures-\ndecompose-br"]
    SKILL --> P5["biz-procedures-\nrefine"]
    SKILL --> P6["biz-procedures-\ndiscover"]
    SKILL --> P7["biz-procedures-\nimport"]
    SKILL --> P8["biz-procedures-\ninfer"]
    SKILL --> P9["biz-procedures-\nalign"]
    SKILL --> P10["biz-procedures-\nview"]

    P1 --> S_OPP["opp-format"]
    P2 --> S_EPIC["epic-format"]
    P2 --> S_OPP
    P3 --> S_EPIC
    P3 --> S_BR["br-format"]
    P4 --> S_BR
    P4 --> S_PF["pf-format"]
    P5 --> S_BR
    P5 --> S_PF
    P5 --> S_RS["readiness-score"]
    P6 --> S_SD["scope-discovery\n-format"]
    P7 --> S_BR
    P7 --> S_MS["merge-strategy"]
    P9 --> S_RS

    P3 --> K_PM["prioritization\n-methods"]
    P7 --> K_EE["entity-extraction\n-rules"]
    P6 --> K_EE

    class SKILL skill
    class P1,P2,P3,P4,P5,P6,P7,P8,P9,P10 proc
    class S_OPP,S_EPIC,S_BR,S_PF,S_RS,S_SD,S_MS schema
    class K_PM,K_EE know
```

**禁止依赖方向**：
- Schema 不引用 Skill/Rules（`grep -r "skills/\|rules/" knowledge/_schema/` 应为空）
- 跨 Skill procedures 不互相引用（`grep -rn "skills/pace-" skills/ --include="*-procedures*.md"` 应为空）

### 4.3 procedures 结构规范

标准章节顺序（源：`plugin-spec.md` 分拆模式）：

| 序号 | 章节 | 必须 | 说明 |
|------|------|:----:|------|
| 1 | 职责 | 是 | 一句话 blockquote |
| 2 | 触发 | 是 | 命令格式+自然语言触发条件 |
| 3 | 与其他子命令的区别 | 否 | 仅易混淆的子命令需要 |
| 4 | 步骤（Step 0-N） | 是 | Step 0=前置检查，最后=下游引导 |
| 5 | 降级模式 | 否 | .devpace/不存在等场景 |
| 6 | 容错 | 是 | 异常-处理 表格 |

**步骤编写规范**（HE-3 Agent Legibility）：
- 每步可直接执行（"读取 epics/EPIC-xxx.md" 而非"检查 Epic 状态"）
- 条件分支完整（"若 status=developing → A；若 paused → B；其他 → 报错"）
- 引用 Schema 不内联（"格式遵循 `br-format.md` §内联格式"）

### 4.4 Hook 工程结构

| 注册位置 | 生效范围 | pace-biz 相关 Hook |
|---------|---------|-------------------|
| `hooks/hooks.json` | 全局所有 Skill | pre-tool-use.mjs（探索模式保护）、skill-eval.mjs（关键词路由） |
| `SKILL.md` frontmatter `hooks:` | 仅 pace-biz 激活时 | pace-biz-scope-check.mjs（写入范围）、Epic Prompt Hook（质量检查） |

**Hook 输出格式标准**（HE-4）：`devpace:<标签> <状态>。ACTION: <步骤1>；<步骤2>。`

### 4.5 辅助知识层

| 子目录 | 文件 | pace-biz 消费方 |
|--------|------|----------------|
| `_extraction/` | entity-extraction-rules.md | import Step 2、discover Step 2 |
| `_extraction/` | prioritization-methods.md | decompose-epic Step 3 |
| `_signals/` | signal-priority.md (S16-S19) | 空参数引导、pace-next |
| root | role-adaptations.md | 所有子命令公共前置 |
| `_schema/auxiliary/` | readiness-score.md | refine Step 1、align Step 2.8 |
| `_schema/auxiliary/` | merge-strategy.md | import Step 3 |

### 4.6 关键设计决策

| 决策 | 选择 | WHY |
|------|------|-----|
| 10 文件分拆 | SKILL.md 路由 + procedures 执行 | IA-2 路由与步骤分离；SKILL.md <200 行保持可扫描 |
| project-format 549 行 | 价值功能树+溢出+渐进丰富 | 高 fan-in 枢纽（10 Skill 引用），承载统一入口契约 |
| 优先级方法论独立 | `_extraction/prioritization-methods.md` | decompose Epic 和 BR 共用；IA-6 单一权威 |
| 提取规则独立 | `_extraction/entity-extraction-rules.md` | init --from 和 import 共用；避免双源头 |

---

## 视图 5：物理视图 (Physical View)

> 回答：**.devpace/ 文件如何布局？加载策略？存储格式？**

### 5.1 .devpace/ 文件系统布局

```mermaid
flowchart TD
    classDef persistent fill:#E8F5E9,stroke:#388E3C,color:#1B5E20
    classDef temp fill:#FFCDD2,stroke:#C62828,color:#B71C1C
    classDef ondemand fill:#FFF9C4,stroke:#F9A825,color:#333

    ROOT[".devpace/"]

    ROOT --> STATE["state.md\n会话状态"]
    ROOT --> PROJ["project.md\n价值功能树枢纽"]
    ROOT --> VIS["vision.md\n产品愿景"]
    ROOT --> OPP["opportunities.md\n业务机会看板"]
    ROOT --> SCOPE["scope-discovery.md\ndiscover 中间态"]

    ROOT --> OBJECTIVES["objectives/"]
    OBJECTIVES --> OBJ1["OBJ-001.md"]
    OBJECTIVES --> OBJ2["OBJ-002.md ..."]

    ROOT --> EPICS["epics/"]
    EPICS --> EP1["EPIC-001.md"]
    EPICS --> EP2["EPIC-002.md ..."]

    ROOT --> REQS["requirements/\n(BR 溢出时创建)"]
    REQS --> BR1["BR-001.md"]

    ROOT --> FEATS["features/\n(PF 溢出时创建)"]
    FEATS --> PF1["PF-001.md"]

    ROOT --> METRICS["metrics/"]
    METRICS --> INS["insights.md\nalign 趋势数据"]

    class STATE,PROJ,VIS,OPP persistent
    class SCOPE temp
    class OBJECTIVES,OBJ1,OBJ2,EPICS,EP1,EP2 persistent
    class REQS,BR1,FEATS,PF1 ondemand
    class METRICS,INS persistent
```

**图例**：绿色=持久文件 | 红色=临时文件（完成后删除） | 黄色=按需创建（溢出触发）

### 5.2 文件加载策略

| 策略 | 文件 | 加载时机 |
|------|------|---------|
| **始终加载** | state.md | 每次会话开始 |
| **公共前置** | state.md + project.md | 所有子命令 Step 0 |
| **按子命令** | 见 3.1 读写矩阵 | 路由后按需读取 |
| **按引用** | Schema 文件 | procedures 引用时读取 |
| **延迟** | epics/*、requirements/* | 仅操作特定实体时 |

**上下文预算**：description < 300 字符，SKILL.md < 500 行，单次执行加载 < 800 行

### 5.3 文件写入权限矩阵

| 文件 | 主写入者 | 辅助写入者 | 只读消费者 |
|------|---------|-----------|-----------|
| opportunities.md | opportunity | discover, epic(状态更新) | view, align |
| epics/EPIC-xxx.md | epic | decompose-epic, discover | view, align |
| project.md 树 | decompose, import, infer | epic, discover | view, align, refine |
| requirements/BR-xxx.md | refine(溢出) | import | align |
| features/PF-xxx.md | — (pace-dev 溢出) | — | view |
| scope-discovery.md | **discover(唯一)** | — | — |
| metrics/insights.md | **align(唯一)** | — | pace-retro |

**Single Writer 原则**：scope-discovery.md 和 insights.md align 趋势段各有唯一写入者，防止并发冲突。

### 5.4 数据格式与向后兼容

**格式约束**：Markdown 是唯一格式。消费者是 LLM + 人类，不使用 YAML/JSON。

**溯源标记**：`<!-- source: claude, [operation-name] -->` / `<!-- source: user -->`。日常不可见，/pace-trace 时展示。

**向后兼容矩阵**：

| 场景 | 行为 |
|------|------|
| 无 objectives/ | project.md 保持原有内联 `### OBJ-N` 格式 |
| 无 epics/ | BR 直挂 OBJ |
| MoS 无维度标签 | 简单 checkbox 列表仍合法 |
| 旧格式"成功标准"章节名 | 仍可识别（br-format） |

**容错统一模式**：文件丢失→重建 | 目录不存在→自动创建 | 不一致→以独立文件为准 | 字段缺失→渐进填充

### 5.5 关键设计决策

| 决策 | 选择 | WHY |
|------|------|-----|
| Markdown 唯一 | 不用 YAML/JSON | LLM + 人类双可读；渲染即文档 |
| project.md 枢纽 | 价值功能树集中 | 一文件纵览全局，避免 20+ 文件散落 |
| HTML 注释溯源 | `<!-- source: ... -->` | P2 渐进暴露——日常不可见，深查时才展示 |
| scope-discovery 完成即删 | 不归档中间态 | 最终产出已写入正式文件；保留只增噪声 |

---

## 附录 A：跨视图一致性追踪矩阵

| 场景视图(用户旅程) | 逻辑视图(实体变化) | 过程视图(触发步骤) | 开发视图(代码文件) | 物理视图(存储文件) |
|-------------------|-------------------|-------------------|-------------------|-------------------|
| 旅程A: opportunity | OPP 创建(评估中) | opportunity Step 3 | biz-procedures-opportunity.md | opportunities.md |
| 旅程A: epic | Epic 创建(规划中), OPP→已采纳 | epic Step 5-7 | biz-procedures-epic.md | epics/EPIC-xxx.md, project.md |
| 旅程A: decompose EPIC | BR 创建(待开始) | decompose-epic Step 4-5 | biz-procedures-decompose-epic.md | project.md 树, epics/ |
| 旅程A: decompose BR | PF 创建(待开始) | decompose-br Step 4 | biz-procedures-decompose-br.md | project.md 树 |
| 旅程A: refine | BR/PF 就绪度提升 | refine Step 2-3 | biz-procedures-refine.md | project.md, requirements/ |
| 旅程A: align | 无实体变化(分析) | align Step 2(9维度) | biz-procedures-align.md | metrics/insights.md |
| 旅程B: discover | OPP+Epic+BR+PF 批量创建 | discover Step 1-5 | biz-procedures-discover.md | 全链路 + scope-discovery.md(临时) |
| 旅程C: import | BR+PF 增量追加 | import Step 2-5 | biz-procedures-import.md | project.md, epics/, requirements/ |
| 旅程D: infer | PF+技术债务追加 | infer Step 1-5 | biz-procedures-infer.md | project.md |

## 附录 B：与现有分析报告的关系

| 报告 | 定位 | 本文档增量价值 |
|------|------|---------------|
| `biz-schema-analysis-2026-03-28.md` | Schema 层设计模式分析 | 本文档将 Schema 放入逻辑视图和物理视图的更大架构上下文中 |
| `biz-stage-full-analysis-2026-03-28.md` | 执行流程线性描述 | 本文档增加事件驱动、跨会话恢复、Hook 守护、分层架构等维度 |
| **本文档** | 架构设计文档（5视图） | 提供多角色可导航的结构化视角；14 张 Mermaid 图飞书可渲染 |
