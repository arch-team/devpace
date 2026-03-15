# 发现引擎公共规程（Discovery Engine）

> **职责**：定义 discover/import/infer 共享的三层管道架构。各子命令扮演"输入适配器"角色，
> 产出标准格式候选实体，馈入本规程的分析管道和写入管道。
>
> **加载方式**：仅在发现型子命令激活时由对应 procedures 引用加载，不自动注入上下文。

## 架构总览

```
输入适配器                  发现引擎                    输出
├── 对话输入 (discover) ──┐                        ┌── 功能树写入（§5）
├── 文档输入 (import)   ──┼─→ §3 分析管道        ──┼── 候选预览（各子命令 Step 4）
└── 代码输入 (infer)    ──┘                        └── 下游引导（§6）
```

各子命令 = 输入适配器（领域特定提取逻辑）+ 引用本规程（公共管道）

## §1 公共前置检查

1. 检查 `.devpace/` 存在（不存在 → 降级模式，见 §7）
2. 读取 `project.md` 功能树，构建**已有实体基准表**：
   - 列出所有 OPP/Epic/BR/PF 的编号、名称、状态
   - 此基准表传递给 §3 分析管道用于对比
3. 读取 project.md `mode` 字段（lite / 完整）
4. 读取 `metrics/insights.md`（如有，加载经验 pattern）

## §2 候选实体标准格式

所有输入适配器（discover/import/infer）必须将提取结果转换为以下标准格式，再馈入分析管道：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| type | enum | OPP / EPIC / BR / PF | PF |
| name | string | 候选实体名称 | "用户认证" |
| source | object | 来源追溯 | `{ adapter: "import", file: "会议纪要.md", line: 42 }` |
| suggested_parent | string? | 建议归属的父实体编号 | "BR-001" |
| priority | string? | 建议优先级 | "P0" |
| metadata | object | 适配器特定元数据 | import: `{ original_text: "..." }` / infer: `{ module: "auth/", signals: ["route","middleware"] }` / discover: `{ session_stage: "brainstorm" }` |

**lite 模式约束**：type 仅允许 PF，suggested_parent 仅允许 OBJ-xxx。

## §3 分析管道

接收候选实体列表 + §1 的已有实体基准表，按适配器类型路由分析策略：

### 分析策略路由

| 适配器 | 分析策略 | 分类体系 | 说明 |
|--------|---------|---------|------|
| discover | **pass-through** | 全部标记 NEW | 对话式从零构建，无需对比 |
| import | **merge** | NEW / DUPLICATE / ENRICHMENT / CONFLICT / REVIEW | 增量合并到已有树 |
| infer | **gap** | UNTRACKED / UNIMPLEMENTED / TECH_DEBT / DOC_DRIFT | 双向覆盖差距 |

### merge 策略细节（import 专用）

- 逐条对比候选 vs 基准表
- 相似度判断：两层机制（快筛 Jaccard + 精判语义），阈值可配（默认 0.8）
- 分类规则：相似度 >= 阈值 → DUPLICATE | 匹配但有新信息 → ENRICHMENT | 矛盾 → CONFLICT | 阈值 ±5% → REVIEW | 其余 → NEW

### gap 策略细节（infer 专用）

- 双向对比：代码模块 vs 基准表
- 分类规则：代码有+树无 → UNTRACKED | 树有+代码无 → UNIMPLEMENTED | TODO/FIXME 密集 → TECH_DEBT | README↔代码不匹配 → DOC_DRIFT

### pass-through 策略（discover 专用）

- 不做对比，候选直接标记 NEW 进入确认阶段

### 公共分析增强（所有策略共享）

- **编号预分配**：为每个 NEW/UNTRACKED 候选预分配编号（§4）
- **归属推断**：无 suggested_parent 的候选，尝试按名称语义匹配已有 Epic/BR

## §4 实体编号分配

为 OPP/EPIC/BR/PF 分配编号：
1. 扫描 §1 基准表中对应类型的最大编号
2. +1 生成新编号（三位补零：001, 002...）
3. **冲突重试**：写入前再次扫描确认编号未被占用

## §5 写入管道

接收用户确认后的实体列表（经 §3 分析 + 各子命令 Step 4 确认），执行统一写入：

1. **功能树追加**：按实体 type 和 suggested_parent 追加到 project.md
   - OPP → opportunities.md
   - Epic → epics/EPIC-xxx.md + project.md 树
   - BR → project.md 对应 Epic 下（无归属 → 树末尾"待归类"）
   - PF → project.md 对应 BR 下（lite 模式直挂 OBJ）
2. **溯源标记**：`<!-- source: claude, {source.adapter}[ from "{source.file}"] -->`
3. **溢出检查**：按 project-format.md 规则检测 PF/BR 溢出
4. **ENRICHMENT 更新**（merge 策略时）：更新已有实体的描述/验收标准
5. **状态标记**（gap 策略时）：UNIMPLEMENTED 项按用户选择更新 PF 状态
6. **适配器收尾钩子**：各子命令可注入收尾逻辑
   - discover → 删除 scope-discovery.md
   - import → 追加迭代变更记录
   - infer → 无额外操作
7. **git commit**

## §6 下游引导模板

```
[动作]完成（来自 [source.adapter 描述]）：
- 新增：X 个 [实体类型]
- [适配器特定统计行]

→ /pace-biz align 检查战略对齐度
→ /pace-biz decompose [编号] 继续细化
→ /pace-plan next 排入迭代
```

各子命令追加适配器特定统计行：
- discover：OPP/Epic/BR/PF 数量
- import：丰富/跳过/冲突数
- infer：技术债务/未实现确认数

## §7 降级模式

| 场景 | 行为 |
|------|------|
| .devpace/ 不存在 | discover/infer：正常执行适配器阶段，§5 写入输出到控制台，引导 /pace-init。import：直接引导 /pace-init |
| project.md 是桩 | §3 分析管道跳过对比（基准表为空），候选全部标记 NEW |
| 候选列表为空 | 提示"未发现新实体"，建议替代适配器 |

## §8 lite 模式统一适配

| 管道阶段 | 完整模式 | lite 模式 |
|---------|---------|----------|
| §2 候选格式 | OPP/Epic/BR/PF 全类型 | 仅 PF（type=PF, parent=OBJ-xxx） |
| §3 分析管道 | 全层对比 | 仅 PF 层对比 |
| §5 写入管道 | project.md + epics/ + requirements/ | project.md（PF 追加到 OBJ 下） |
