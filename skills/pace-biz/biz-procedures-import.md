# import 子命令 procedures

> **职责**：从外部文档（会议纪要、用户反馈、竞品分析等）批量提取需求实体，合并到现有功能树。
> **角色**：发现引擎的"文档输入适配器"——领域特定的摄入和提取逻辑 + 引用 `biz-procedures-discovery-engine.md` 的公共管道。

## 触发

`/pace-biz import <路径>...` 或用户要从文档中导入需求（"把这份会议纪要的需求导入"、"从 PRD 里提取需求"）。

## 与 init --from 的区别

- **init --from**：项目初始化时使用，从零创建 project.md 功能树
- **import**：项目已有功能树，增量追加新实体并执行合并分析（去重、冲突检测）

## 步骤

### Step 0：前置检查与模式检查

1. 按 `biz-procedures-discovery-engine.md` §1 执行公共前置检查（.devpace/ 检查、基准表构建、mode 读取、insights 加载）

**lite 模式适配**：按 `biz-procedures-discovery-engine.md` §8，import 特定调整：
- Step 2 实体提取：映射目标仅为 PF（跳过 OPP/Epic/BR 映射），用户故事和功能列表直接提取为 PF 候选
- Step 3 合并分析：仅对比已有 PF 列表
- Step 5 写入：PF 直接追加到 project.md 对应 OBJ 下，不创建 Epic/BR

### Step 1：源文件摄入

- **单文件**：`/pace-biz import meeting-notes.md` → 直接读取
- **目录路径**：`/pace-biz import requirements/` → 扫描目录下所有 `.md`/`.txt` 文件
- **多文件**：`/pace-biz import doc1.md doc2.md` → 依次读取，合并提取结果
- 文件过多（>10）时先输出文件列表让用户筛选

**源类型自动检测**：

| 源类型 | 检测特征 | 提取映射 |
|--------|---------|---------|
| 会议纪要 | "会议"、"minutes"、"纪要"、日期标题格式 | Action Items → BR/PF 候选 |
| 用户反馈 | "反馈"、"feedback"、评分模式、用户引用 | 痛点 → BR，功能请求 → PF |
| 竞品分析 | "竞品"、"competitor"、"对比"、对比表格 | 差距功能 → PF 候选 |
| 技术债务 | "TODO"、"FIXME"、"tech-debt"、"技术债" | 债务项 → PF 候选（标记技术债务） |
| Issue 导出 | CSV/JSON 格式（含 title/label/status 字段） | Issues → PF/CR 候选 |
| PRD / 功能规格 | 用户故事、功能列表、Features section | 同 init --from §1 解析规则 |
| API 规格 | OpenAPI/Swagger 关键词 | 同 init --from §1 API 特殊处理 |

### Step 2：实体提取

对每个源文件，按检测到的源类型执行提取：

**通用提取规则**（复用 init-procedures-from.md §1 映射表）：

| 文档元素 | 映射目标 | 解析方法 |
|---------|---------|---------|
| 用户故事（As a... I want...） | BR（业务需求） | 模式匹配 + 语义分析 |
| 功能列表 / Features | PF（产品功能）树 | 层级提取 |
| API 端点列表 | PF（按资源分组） | 结构化解析 |
| 优先级标记（P0/P1/Must/Should） | 优先级候选 | 标签提取 |

**扩展提取规则**（import 特有）：

| 文档元素 | 映射目标 | 解析方法 |
|---------|---------|---------|
| Action Items（会议纪要） | BR/PF 候选 | "决定"、"需要"、"TODO" 关键词 |
| 用户痛点描述（反馈） | BR 候选 | 负面情感 + 功能关联 |
| 功能请求（反馈） | PF 候选 | "希望"、"建议"、"能不能" |
| 竞品差距功能（竞品分析） | PF 候选 | 对比表中我方缺失项 |
| TODO/FIXME 注释 | PF 候选（技术债务） | 注释模式匹配 |

每个提取的实体记录来源文件和行号，用于溯源。

### Step 2.5：转换为标准候选格式

将 Step 2 提取结果转换为 `biz-procedures-discovery-engine.md` §2 标准格式：

- source: `{ adapter: "import", file: "[filename]", line: N }`
- metadata: `{ original_text: "...", source_type: "meeting|feedback|competitor|debt|issue|prd" }`

### Step 3：合并分析

将候选实体列表 + §1 基准表馈入 `biz-procedures-discovery-engine.md` §3（策略 = merge）。

**merge 策略参数**（import 特有配置）：

- **相似度阈值**：默认 0.8，可通过参数调整：`import doc.md --threshold 0.7`

| 阈值范围 | 效果 | 适用场景 |
|---------|------|---------|
| 0.9+ | 严格匹配，仅近乎相同的标题判为重复 | 功能命名高度规范化的项目 |
| 0.7-0.9（默认 0.8） | 平衡去重与新增 | 大多数场景 |
| 0.5-0.7 | 宽松匹配，相似功能更易判为重复 | 功能命名不规范、同义词多的项目 |

- **两层判断机制**（对应 §3 merge 策略的快筛+精判）：
  - 示例："用户登录" vs "用户注册"——关键词重叠高但语义不同 → NEW
  - 示例："登录认证" vs "用户登录"——关键词重叠中等但语义相同 → DUPLICATE

- **模糊边界处理**：相似度在阈值 ±5% 范围内的项，标记为 `REVIEW`（需用户裁定），而非自动判定。

输出：按 NEW / DUPLICATE / ENRICHMENT / CONFLICT / REVIEW 分类后的候选列表。

### Step 4：用户确认

展示合并计划（diff 格式），对每项标注来源交叉引用：

```
导入分析（来自 [文件名]）：

NEW（新增 N 项）：
  + BR-xxx：[名称]
    来源：[文件名] L42 | 相关已有：PF-001（同领域）
  + PF-xxx：[名称]
    来源：[文件名] L58 | 相关已有：无

DUPLICATE（已有 M 项）：
  = [提取名称] ≈ PF-003（相似度 [N]%，已存在，跳过）
    来源：[文件名] L75 | 已有定义：project.md L120

ENRICHMENT（丰富 K 项）：
  ~ PF-002：追加验收标准 "[新标准]"
    来源：[文件名] L88 | 现有验收标准：N 条 → N+1 条

CONFLICT（冲突 J 项）：
  ! BR-001 现有定义 "[现有]" vs 导入 "[新]"
    来源：[文件名] L95 | 现有定义：requirements/BR-001.md

逐条确认：accept all / reject all / 逐条选择
```

**交叉引用规则**：
- 每项标注"来源"（源文件 + 行号）和"相关已有"（功能树中同领域实体）
- DUPLICATE 项展示相似度百分比和已有定义位置
- ENRICHMENT 项展示前后对比（如验收标准条数变化）
- 帮助用户在 accept/reject 时做出知情决策

CONFLICT 项使用 AskUserQuestion 交互决定保留哪个版本。

### Step 5：执行写入

将确认的候选实体列表馈入 `biz-procedures-discovery-engine.md` §5 写入管道，附加 import 特定逻辑：

1. **收尾钩子**：若有迭代文件（`iterations/current.md`），追加变更记录

其余步骤（功能树追加、编号分配、溯源标记、溢出检查、ENRICHMENT 更新、git commit）由写入管道 §5 统一执行。

**不创建 CR**——import 只丰富功能树（OPP/Epic/BR/PF 级别），不涉及开发层。

### Step 6：下游引导

按 `biz-procedures-discovery-engine.md` §6 模板输出，追加 import 统计行：丰富/跳过/冲突数。

## 降级模式

按 `biz-procedures-discovery-engine.md` §7，import 附加：

| 场景 | 行为 |
|------|------|
| .devpace/ 不存在 | 提示"项目未初始化"，引导 `/pace-init` 或 `/pace-init --from <路径>`（推荐） |
| project.md 是桩 | 正常运行，跳过合并分析（无现有功能树可对比），直接写入 |
| 源文件不存在 | 提示路径无效，列出当前目录文件供选择 |
| 源文件为空 | 提示文件为空，跳过 |

## 容错

| 异常 | 处理 |
|------|------|
| 无法识别源类型 | 按通用文本处理，提取关键短语为 PF 候选 |
| 提取结果为空 | 提示"未从文档中提取到明确的需求实体"，建议手动梳理 |
| 大文件（>500 行） | 分段处理，每段提取后合并结果 |
| 二进制文件 | 跳过并提示"不支持二进制文件" |
| 编号冲突 | 重新扫描确认最大编号后分配 |
