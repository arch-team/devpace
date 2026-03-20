# import 子命令 procedures

> **职责**：从外部文档（会议纪要、用户反馈、竞品分析等）批量提取需求实体，合并到现有功能树。

## 触发

`/pace-biz import <路径>...` 或用户要从文档中导入需求（"把这份会议纪要的需求导入"、"从 PRD 里提取需求"）。

## 与 init --from 的区别

- **init --from**：项目初始化时使用，从零创建 project.md 功能树
- **import**：项目已有功能树，增量追加新实体并执行合并分析（去重、冲突检测）

## 步骤

### Step 0：前置检查与模式检查

1. 检查 `.devpace/` 存在（不存在 → 引导 `/pace-init`）
2. 读取 `project.md` 现有功能树（获取已有实体列表用于合并分析）
3. 读取 `metrics/insights.md`（如有，加载导入相关经验 pattern）

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
| Issue 导出 | CSV/JSON 格式（含 title/label/status 字段） | Issues → PF 候选 |
| PRD / 功能规格 | 用户故事、功能列表、Features section | 同 init --from §1 解析规则 |
| API 规格 | OpenAPI/Swagger 关键词 | 同 init --from §1 API 特殊处理 |

### Step 2：实体提取

对每个源文件，按检测到的源类型执行提取：

**通用提取规则**（映射表见 `knowledge/_extraction/entity-extraction-rules.md`）：按该映射表的文档元素→实体映射关系执行提取。

**扩展提取规则**（import 特有）：

| 文档元素 | 映射目标 | 解析方法 |
|---------|---------|---------|
| Action Items（会议纪要） | BR/PF 候选 | "决定"、"需要"、"TODO" 关键词 |
| 用户痛点描述（反馈） | BR 候选 | 负面情感 + 功能关联 |
| 功能请求（反馈） | PF 候选 | "希望"、"建议"、"能不能" |
| 竞品差距功能（竞品分析） | PF 候选 | 对比表中我方缺失项 |
| TODO/FIXME 注释 | PF 候选（技术债务） | 注释模式匹配 |

每个提取的实体记录来源文件和行号，用于溯源。

**角色适配**（通用维度见 `knowledge/role-adaptations.md`，读取公共前置传入的 preferred-role）：
- Biz Owner → 提取时优先标注商业价值相关实体
- Tester → 提取时额外标注验收条件和测试数据需求
- Dev/PM/Ops（默认）→ 无追加（零改变）

### Step 3：合并分析

对比提取实体 vs 现有功能树，逐条分类：

| 分类 | 条件 | 处理 |
|------|------|------|
| NEW | 相似度 < 阈值 | 建议添加到功能树 |
| DUPLICATE | 相似度 >= 阈值 | 跳过并注明已有对应实体（附相似度百分比） |
| ENRICHMENT | 匹配已有但补充了新信息（验收标准/用户故事） | 建议更新已有实体 |
| CONFLICT | 与现有定义矛盾 | 标记待决，需用户裁定 |

合并分类框架、阈值范围和两层判断机制见 `knowledge/_schema/auxiliary/merge-strategy.md`。

**相似度快筛说明**：快筛基于标题关键词重叠率判断——大部分关键词相同视为高重叠，少量关键词相同视为低重叠。快筛通过但处于阈值边界的项，由 Claude 进行语义分析精判：
- 示例："用户登录" vs "用户注册"——关键词重叠高但语义不同 -> NEW
- 示例："登录认证" vs "用户登录"——关键词重叠中等但语义相同 -> DUPLICATE

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

1. NEW 项：追加到 `project.md` 功能树对应位置
   - BR 追加到对应 OBJ/Epic 下（内联格式遵循 `knowledge/_schema/entity/br-format.md` §内联格式；无明确归属时追加到树末尾，标记"待归类"）
   - PF 追加到对应 BR 下（内联格式遵循 `knowledge/_schema/entity/pf-format.md` §内联格式）
2. ENRICHMENT 项：更新 `project.md` 中对应 PF/BR 的描述或验收标准
3. 编号自增（扫描现有最大编号 +1）
4. 触发 PF/BR 溢出检查（按 project-format.md 溢出规则）
5. 所有内容标记溯源：`<!-- source: claude, imported from "[filename]" -->`
6. 若有迭代文件（`iterations/current.md`），追加变更记录
7. git commit

**不创建 CR**——import 只丰富功能树（OPP/Epic/BR/PF 级别），不涉及开发层。

### Step 6：下游引导

```
导入完成（来自 [N 个文件]）：
- 新增：X 个 BR + Y 个 PF
- 丰富：Z 个已有实体
- 跳过：W 个重复项
  成熟度分布：骨架级 K 个 / 基本级 M 个 — 建议优先精炼骨架级实体

→ /pace-biz refine [最需精炼的 ID] 优先精炼骨架级实体
→ /pace-biz align 检查新增内容的战略对齐度
→ /pace-biz decompose [BR-xxx] 继续细化新增需求
→ /pace-plan next 排入迭代
```

## 降级模式

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
