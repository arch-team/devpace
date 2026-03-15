# discover 子命令 procedures

> **职责**：交互式探索需求发现——从模糊想法出发，通过多轮对话引导产出 OPP→Epic→BR→PF 候选树。
> **角色**：发现引擎的"对话输入适配器"——领域特定的对话逻辑 + 引用 `biz-procedures-discovery-engine.md` 的公共管道。

## 触发

`/pace-biz discover <描述>` 或用户表达模糊需求想法（"我想做一个..."、"有没有可能..."、"头脑风暴一下"）。

## 与 decompose 的区别

- **discover**：从零开始的全链路探索，输入是模糊想法，输出是 OPP→Epic→BR→PF 候选树
- **decompose**：已有实体的单层精确拆解，输入是 EPIC-xxx 或 BR-xxx，输出是下一层子实体

## 步骤

### Step 0：上下文加载与智能路由

1. 按 `biz-procedures-discovery-engine.md` §1 执行公共前置检查（.devpace/ 检查、基准表构建、mode 读取、insights 加载）
2. **智能路由检测**（当用户输入可能更适合其他子命令时，提前引导）：
   - 用户提供了文件路径（如 `discover meeting-notes.md`）→ 提示："检测到文件路径，建议使用 `/pace-biz import meeting-notes.md` 从文档导入。继续 discover 对话式探索？"
   - 用户输入含代码相关关键词（"看看代码"、"代码里有什么"、"技术债"）→ 提示："建议使用 `/pace-biz infer` 从代码库推断。继续 discover 对话式探索？"
   - 用户确认继续 discover → 正常进入 Step 1
   - 用户接受建议 → 路由到对应子命令
4. **空项目检测**：若 project.md 不存在或仅为桩文件（无 OBJ 定义），引导先初始化：
   > 项目尚未初始化业务目标。建议先运行 `/pace-init full` 一站式建立项目结构，再通过 discover 探索新需求。
   - 用户坚持继续 → 正常进入 Step 1（discover 降级模式会在 Step 5 输出到控制台）
5. 检查是否有进行中的发现会话：`.devpace/scope-discovery.md`
   - 存在 → 读取并提示用户："上次探索到 [阶段]，继续还是重新开始？"
   - 不存在 → 开始新会话

**lite 模式适配**：按 `biz-procedures-discovery-engine.md` §8，discover 特定调整：
- Step 1：OBJ 候选照常映射，不创建 OPP
- Step 2：功能头脑风暴直接产出 PF 候选（跳过 BR 分组）
- Step 4：候选树展示为 `OBJ→PF` 结构（无 OPP/Epic/BR 层）
- Step 5：写入管道仅处理 PF（不创建 OPP/Epic/BR 文件）

### Step 1：目标框定（1-2 轮 AskUserQuestion）

从用户输入中提取核心意图，通过追问补充关键信息：

**第 1 轮**（若用户已给出描述则跳过）：
- "要解决什么问题？目标用户是谁？"

**第 2 轮**（基于第 1 轮回答）：
- "这个对用户来说有多紧迫？是锦上添花还是痛点？"
- "有没有现有的替代方案？"
- "除了目标用户，还有哪些人会受影响或关心这件事？"（可选——引导利益相关者识别）

**产出**：
- OBJ 候选（映射到 project.md 已有 OBJ 或建议新 OBJ）
- 目标用户画像（1-2 句话）
- 利益相关者候选（如用户提供了第 2 轮可选追问的回答）

**中间状态持久化**：写入 `.devpace/scope-discovery.md`：

```markdown
# 需求发现会话

## 阶段：目标框定
## 开始时间：[YYYY-MM-DD HH:mm]

## 目标
[用户描述的核心问题]

## 用户画像
[目标用户描述]

## OBJ 候选
- [OBJ 映射或新建议]
```

### Step 2：功能头脑风暴（2-4 轮）

基于 Step 1 的目标，引导用户展开功能想象：

**追问策略**（按轮次渐进深入，根据当前角色调整侧重）：

| 轮次 | 问题方向 | 示例 |
|------|---------|------|
| 1 | 核心能力 | "用户必须能做什么？最基本的操作是什么？" |
| 2 | 场景延伸 | "当 [场景] 发生时怎么办？有没有异常情况？" |
| 3 | 边界探索 | "需要支持多少用户/数据量？有性能要求吗？" |
| 4 | 差异化 | "和现有方案相比，最大的不同是什么？" |

**角色适配**（读取公共前置传入的 preferred-role，调整追问侧重）：

| 角色 | 追加侧重 | 追问示例 |
|------|---------|---------|
| Biz Owner | 商业价值、市场影响 | "这对营收/用户增长有什么预期影响？" |
| PM | 用户场景、优先级 | "这个功能的目标用户群有多大？是否有竞品已实现？" |
| Dev | 技术可行性、架构约束 | "实现这个功能的技术难点是什么？有现成组件可复用吗？" |
| Tester | 可测试性、验收条件 | "怎么验证这个功能正常工作？边界情况有哪些？" |
| Ops | 运维影响、部署需求 | "这会影响系统的哪些部分？需要新的基础设施吗？" |

角色适配仅调整追问方向和措辞，不改变 discover 的核心流程和产出结构。Dev 角色使用默认策略（零改变）。

每轮回答后 Claude 实时整理为 BR→PF 候选分组，展示给用户确认方向。

**产出**：BR→PF 候选列表（层级分组），追加到 `scope-discovery.md`。

### Step 3：边界定义（1-2 轮）

明确范围边界，防止后续范围蔓延：

- "这个版本明确不做什么？"
- "有什么技术约束或时间约束？"

**产出**：范围"做/不做"清单，追加到 `scope-discovery.md`。

### Step 4：验证与确认（1 轮）

展示结构化摘要：

```
需求发现摘要：

目标：[核心问题]
用户：[目标用户]

候选价值链：
OBJ-x（[目标]）
└── OPP-xxx：[机会描述]
    └── EPIC-xxx：[专题名称]
        ├── BR-xxx：[需求 1] P0
        │   ├── PF-xxx：[功能 1a]
        │   └── PF-xxx：[功能 1b]
        └── BR-xxx：[需求 2] P1
            └── PF-xxx：[功能 2a]

范围：
  做：[清单]
  不做：[清单]

确认后将写入 .devpace/，请检查并调整。
```

用户可以：调整层级关系、重新排优先级、删除不需要的候选、修改名称。

### Step 4.5：转换为标准候选格式

将 Step 4 验证确认后的候选树转换为 `biz-procedures-discovery-engine.md` §2 标准格式：

- source: `{ adapter: "discover", session: "scope-discovery.md" }`
- metadata: `{ session_stage: "[当前阶段]" }`
- 对话式候选全部标记为 NEW（分析策略 = pass-through，见 §3）

### Step 5：写入 .devpace/

将确认的候选实体列表馈入 `biz-procedures-discovery-engine.md` §5 写入管道，附加 discover 特定逻辑：

1. **OPP/Epic 创建**：OPP 按 biz-procedures-opportunity.md 格式写入 opportunities.md，Epic 按 biz-procedures-epic.md 格式创建 epics/EPIC-xxx.md
2. **范围**：写入 `project.md` "范围" section（做/不做清单）
3. **收尾钩子**：删除 `scope-discovery.md`（发现会话完成）

其余步骤（BR/PF 追加、编号分配、溯源标记、溢出检查、git commit）由写入管道 §5 统一执行。

### Step 6：下游引导

按 `biz-procedures-discovery-engine.md` §6 模板输出，追加 discover 统计行：OPP/Epic/BR/PF 各自数量。

## 降级模式

按 `biz-procedures-discovery-engine.md` §7，discover 附加：

| 场景 | 行为 |
|------|------|
| .devpace/ 不存在 | 正常执行 Step 0-4（对话探索），Step 5 输出到控制台不写文件，引导 /pace-init |
| project.md 是桩 | 正常运行，Step 5 填充桩内容（愿景、范围等） |
| 用户中途放弃 | scope-discovery.md 保留中间状态，下次可继续 |

## 容错

| 异常 | 处理 |
|------|------|
| 用户描述过于模糊（< 5 字） | 追加引导问题："能再详细说说吗？比如要解决什么问题？" |
| scope-discovery.md 格式损坏 | 忽略已有内容，重新开始 |
| OBJ 映射无匹配 | 建议创建新 OBJ 或跳过 OBJ 映射 |
| 用户拒绝所有候选 | 尊重决定，删除 scope-discovery.md，不写入任何文件 |
