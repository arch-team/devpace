# pace-biz Skill 改进实施方案

> **基准日期**：2026-03-15
> **代码基准**：feature/skill-optimization 分支，128/131 任务完成
> **方法**：完整源码阅读 + 上下游 Skill 衔接分析 + 最新规范对齐

## 一、当前状态基线

### 1.1 文件清单（10 文件，~35K 字符）

| 文件 | 行数 | 职责 |
|------|------|------|
| `skills/pace-biz/SKILL.md` | 111 | 路由入口：8 子命令 + 空参引导 + 执行路由表 |
| `biz-procedures-opportunity.md` | 77 | 创建型：OPP 捕获 |
| `biz-procedures-epic.md` | 118 | 创建型：Epic 创建/转化 |
| `biz-procedures-decompose.md` | 112 | 创建型：Epic->BR 或 BR->PF 分解 |
| `biz-procedures-discover.md` | 165 | 发现型：交互式需求探索 |
| `biz-procedures-import.md` | 155 | 发现型：文档批量导入 |
| `biz-procedures-infer.md` | 170 | 发现型：代码反向推断 |
| `biz-procedures-align.md` | 83 | 分析型：战略对齐检查 |
| `biz-procedures-view.md` | 76 | 分析型：业务全景展示 |
| `biz-procedures-output.md` | 86 | 各子命令输出格式模板 |

### 1.2 已有的平台能力使用

| 能力 | 状态 | 说明 |
|------|------|------|
| `description` CSO 触发词 | 已用 | 中英文关键词覆盖完善 |
| `context: fork` + `agent: pace-pm` | 已用 | PM Agent 上下文 |
| `model: sonnet` | 已用 | 适合业务分析 |
| `allowed-tools` | 已用 | 7 个工具授权 |
| `argument-hint` | 已用 | 复杂但完整 |
| `$ARGUMENTS` | 已用 | 全参数解析 |
| **Skill 级 Hooks** | **未用** | pace-dev/review/init 均已有，pace-biz 无 |
| `preferred-role` 角色感知 | **未用** | pace-next/pace-theory/pace-role 已用 |
| `$0`/`$1` 按位参数 | **未用** | pace-sync 已用 `$1` |

### 1.3 同类 Skill Hook 实现模式对照

| Skill | Hook 脚本 | 行为 |
|-------|----------|------|
| pace-dev | `hooks/skill/pace-dev-scope-check.mjs` | CR 文件/`.devpace/` 允许；非 CR 文件做范围偏移 advisory |
| pace-init | `hooks/skill/pace-init-scope-check.mjs` | 仅 `.devpace/`、CLAUDE.md、.gitignore 允许；其他 exit 2 阻断 |
| pace-review | `hooks/skill/pace-review-scope-check.mjs` | `.devpace/` 允许；非 `.devpace/` advisory |
| **pace-biz** | **无** | 无写入保护 |

### 1.4 关键缺失确认

| 缺失项 | 验证方式 | 结果 |
|--------|---------|------|
| devpace-rules.md §22 | `grep '§22' rules/devpace-rules.md` | 不存在。design.md §12 映射表引用了 §22 但 rules 中无对应章节 |
| epic-format.md 依赖字段 | `grep '依赖' knowledge/_schema/epic-format.md` | 不存在。Schema 无 Dependencies section |
| refine 子命令 | `grep 'refine' skills/pace-biz/` | 不存在。roadmap.md Backlog B1 已记录为候选方向 |
| pace-biz 读取 preferred-role | 审查 SKILL.md 公共前置 | 不存在。仅读 state.md/project.md/mode |

---

## 二、改进项分析

### 依赖关系图

```
3.1 Hooks 写入保护 ──(无依赖，独立)
3.2 refine 子命令 ──(无依赖，独立)
3.3 优先级框架 ──(改 decompose + align，独立)
3.4 体验统一 ──(改 view + align output，独立)
3.5 角色感知 ──(改 SKILL.md 公共前置 + 多个 procedures，依赖 role-procedures-dimensions.md)
3.6 依赖追踪 ──(改 epic-format Schema + decompose + align)
3.7 反馈闭环 ──(改 align，跨 Skill 协作)
3.8 prompt Hook ──(需 3.1 先完成——Hook 基础设施)
3.12 §22 修正 ──(改 design.md，独立)
```

### 并行分组

```
Group A（独立，可并行）：3.1 + 3.2 + 3.3 + 3.4 + 3.12
Group B（依赖 Group A 部分）：3.5 + 3.6 + 3.7
Group C（依赖 3.1）：3.8
Group D（低优先级，独立）：3.9 + 3.10 + 3.11 + 3.13
```

---

## 三、P0 改进项详细方案

### 3.1 Skill 级 Hooks 写入保护（修复 IA-7）

**问题**：pace-biz 有 5 个写入子命令（opportunity/epic/decompose/discover/import），写入范围仅靠 procedures 文本约束。pace-dev、pace-init、pace-review 均已实现 Skill 级 Hook。

**方案**：创建 `hooks/skill/pace-biz-scope-check.mjs`，复用 `hooks/lib/utils.mjs` 共享工具。

**允许的写入目标**：
- `.devpace/opportunities.md` — opportunity 子命令
- `.devpace/epics/EPIC-*.md` — epic 子命令
- `.devpace/project.md` — decompose/epic/discover/import/infer 更新功能树
- `.devpace/requirements/BR-*.md` — decompose 溢出
- `.devpace/scope-discovery.md` — discover 中间状态
- `.devpace/state.md` — 状态更新（公共）

**阻断的写入目标**：
- 非 `.devpace/` 目录下的任何文件 → exit 2 阻断
- 原因：pace-biz 是业务规划域，不应修改源代码或其他项目文件

**涉及文件变更**：

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 新建 | `hooks/skill/pace-biz-scope-check.mjs` | ~50 行，参考 pace-init-scope-check.mjs 模式 |
| 修改 | `skills/pace-biz/SKILL.md` | frontmatter 增加 `hooks:` 配置 |

**SKILL.md frontmatter 变更**：

```yaml
---
description: Use when user says "业务机会"... (existing)
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[opportunity|epic|decompose|align|view|discover|import|infer] ..."
model: sonnet
context: fork
agent: pace-pm
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/skill/pace-biz-scope-check.mjs"
          timeout: 5
---
```

**Hook 脚本逻辑**：

```javascript
// 1. 读取 stdin JSON + 提取 file_path
// 2. 空路径 → exit 0（非文件操作）
// 3. isDevpaceFile(filePath) → exit 0（.devpace/ 内全部允许）
// 4. 其他路径 → exit 2 阻断 + 错误消息
```

**验证方法**：模拟 pace-biz 期间写入 `src/` 目录 → 应被阻断。

---

### 3.2 refine 子命令

**问题**：BR/PF 创建后无迭代精炼机制。roadmap.md Backlog B1 已确认此需求。

**方案**：新增 `biz-procedures-refine.md` + 更新路由。

**refine 的行为定义**：

- **输入**：`/pace-biz refine <BR-xxx|PF-xxx>` 或"精炼/细化/补充 BR-001"
- **区分于 pace-change modify**：refine = 深化同一需求（补充验收标准、边界条件、用户故事细节）；modify = 改变需求方向
- **交互式精炼**：Claude 读取现有实体内容，基于已有信息提出 3-5 个补充问题（验收标准？边界条件？异常场景？非功能要求？）
- **写入目标**：更新 `project.md` 功能树中对应条目 + BR 溢出文件（如有）

**涉及文件变更**：

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 新建 | `skills/pace-biz/biz-procedures-refine.md` | ~100 行 |
| 修改 | `skills/pace-biz/SKILL.md` | 路由表 + 子命令列表 + argument-hint 增加 refine |
| 修改 | `skills/pace-biz/biz-procedures-output.md` | 新增 refine 输出格式模板 |

**procedures 结构**：

```
Step 0: 模式检查（lite 模式仅支持 PF 精炼）
Step 1: 定位实体——读取 project.md 树 + 溢出文件，展示当前内容
Step 2: 精炼引导——基于实体类型提问：
  - BR: 验收标准、业务规则、异常场景、用户故事、非功能需求
  - PF: 边界条件、输入输出规格、性能要求、安全约束
Step 3: 用户回答后更新实体内容（操作确认后写入）
Step 4: 输出——展示变更 diff + 下一步建议
```

**输出格式**：

```
已精炼 [BR-xxx|PF-xxx]：[名称]
变更摘要：
  + 新增验收标准 3 条
  + 补充异常场景 2 个
  ~ 更新用户故事描述
→ 下一步：/pace-biz decompose BR-xxx 继续分解 | /pace-dev 开始开发
```

---

### 3.3 优先级决策框架（嵌入 decompose + align）

**问题**：priority 在 decompose 时随意设定（P0/P1/P2），无结构化依据。

**方案**：在现有 decompose 和 align 中嵌入轻量评估，不新增子命令。

**涉及文件变更**：

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 修改 | `biz-procedures-decompose.md` | Step 3E/3P 增加 Value x Effort 评估 |
| 修改 | `biz-procedures-align.md` | Step 2 增加优先级分布检查 |

**decompose 变更（Step 3E 追加）**：

在 Step 3E "引导需求分解"第 2 点之后追加优先级评估：

```
每个 BR 的优先级不再随意标注，通过简化 Value x Effort 矩阵确定：
- Value（价值）：高/中/低 — 对 Epic MoS 的贡献度
- Effort（成本）：高/中/低 — 预估实现复杂度
- 映射规则：高价值低成本=P0 | 高价值高成本或中价值低成本=P1 | 其他=P2
- 展示评估矩阵让用户确认或覆盖
```

Step 3P 同理，针对 PF：

```
每个 PF 的优先级继承 BR 优先级，但可通过 Value x Effort 调整：
- 同一 BR 下多个 PF 时，核心路径 PF 可提升、锦上添花 PF 可降级
```

**align 变更（Step 2 追加 §2.5）**：

```
#### 2.5 优先级分布健康度

- 统计 P0:P1:P2 比例
- P0 占比 > 60% → 警告"优先级通胀——几乎所有需求都是最高优先级，优先级失去区分作用"
- 无 P0 → 警告"缺少明确的核心优先级"
- 建议健康比例：P0 20-30% / P1 40-50% / P2 20-30%
```

---

### 3.4 创建/变更体验统一（内联引导）

**问题**：pace-biz 创建实体后修改要去 pace-change，认知割裂。

**方案**：在 view 和 align 输出中对可操作实体内联引导命令。不新增子命令。

**涉及文件变更**：

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 修改 | `biz-procedures-view.md` | Step 2 输出增加内联操作引导 |
| 修改 | `biz-procedures-align.md` | Step 3 报告增加修复建议命令 |
| 修改 | `biz-procedures-output.md` | view/align 输出模板更新 |

**view 输出增强**：

```
在 Step 2 构建全景视图时，对每个有问题的实体追加操作引导：

├── [EPIC-001]（进行中）← OPP-001
│   MoS：（待定义）→ 补充 MoS：直接描述指标，或 /pace-change modify EPIC-001
│   ├── BR-001 P0 → PF-001 → CR-001 🔄
│   └── BR-002 P1（待分解）→ /pace-biz decompose BR-002
```

**align 报告增强**：

```
在 Step 3 每个问题项后附带修复命令：

孤立实体：
├── 孤立 BR：BR-005 → 建议：/pace-change modify BR-005（关联到 Epic）
├── 空 Epic：EPIC-003 → 建议：/pace-biz decompose EPIC-003
└── 未处理机会：OPP-002 → 建议：/pace-biz epic OPP-002
```

---

### 3.12 §22 悬空引用修正

**问题**：design.md §12 Skill 映射表引用 `§22` 但 devpace-rules.md 中无此章节。

**推荐方案 B**（修正引用，不新增 §22）：

- pace-biz 行为规则已完全由 SKILL.md + procedures 文件承载
- 新增 §22 会导致 rules 文件继续膨胀（已 500+ 行），违反 IA-5 按需加载
- design.md §12 映射表中改为标注 "SKILL.md 自治"

**涉及文件变更**：

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 修改 | `docs/design/design.md` 第 900 行 | `§22` → `SKILL.md` |

**注意**：此为开发层文件变更，应独立于产品层变更批次执行。

---

## 四、P1 改进项详细方案

### 3.5 角色感知集成

**问题**：pace-biz 不读取 `preferred-role`，所有角色看到相同输出。

**方案**：在 SKILL.md 公共前置步骤增加角色读取，在关键 procedures 中增加条件分支。

**角色适配维度**（引用 `skills/pace-role/role-procedures-dimensions.md`）：

| 角色 | view 关注 | decompose 追加考量 | discover 追问方向 |
|------|----------|-------------------|------------------|
| Biz Owner | MoS 达成率、业务价值 | 市场影响、ROI | 用户价值、竞争定位 |
| PM | 迭代进度、功能依赖 | 交付节奏、资源约束 | 功能优先级、用户场景 |
| Dev | 技术可行性、实现复杂度 | NFR、架构约束 | 技术方案、接口定义 |
| Tester | 验收标准完整度、测试覆盖 | 可测试性、边界条件 | 异常场景、数据边界 |
| Ops | 部署影响、监控需求 | 运维成本、SLA 约束 | 部署方式、回滚方案 |

**涉及文件变更**：

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 修改 | `skills/pace-biz/SKILL.md` | 公共前置增加 Step 2.5：读 project.md `preferred-role` |
| 修改 | `biz-procedures-view.md` | Step 2 增加角色条件分支 |
| 修改 | `biz-procedures-decompose.md` | Step 3E/3P 增加角色追加考量 |
| 修改 | `biz-procedures-discover.md` | Step 2 追问策略增加角色方向 |

**SKILL.md 公共前置变更**：

```markdown
### 所有子命令的公共前置

1. 读取 state.md 和 project.md 确认项目上下文
2. 确认 .devpace/ 已初始化
3. 读取 project.md 配置 section 的 `mode` 字段
4. **读取 project.md 配置 section 的 `preferred-role` 字段（缺省 = Dev）**
5. 按子命令路由到对应 procedures 文件
```

**实现原则**（引用 role-procedures-dimensions.md）：角色适配仅调整输出措辞和关注维度排序，不改变底层数据采集、分析逻辑或阈值。Dev 角色使用现有格式（零改变）。无数据支撑时回退到 Dev 默认。

---

### 3.6 依赖关系追踪

**问题**：Epic 间、BR 间无依赖记录，影响 pace-plan 排期准确性。

**涉及文件变更**：

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 修改 | `knowledge/_schema/epic-format.md` | 业务需求表增加"依赖"列 |
| 修改 | `biz-procedures-decompose.md` | Step 3 增加依赖询问 |
| 修改 | `biz-procedures-align.md` | 新增 §2.6 依赖检查维度 |

**epic-format.md 变更**：

业务需求表格增加可选"依赖"列：

```markdown
| BR | 标题 | 优先级 | 状态 | PF 数 | 完成度 | 依赖 |
|----|------|:------:|------|:-----:|:------:|------|
| BR-001 | [需求名] | P0 | 进行中 | 2 | 1/2 | — |
| BR-002 | [需求名] | P1 | 待开始 | 0 | — | BR-001 |
```

**decompose Step 3 追加**：

```
4. 对每个新 BR，追问：是否依赖已有的 BR？（列出同 Epic 下其他 BR 供选择）
   - 无依赖 → "—"
   - 有依赖 → 记录 BR-xxx（可多个，逗号分隔）
```

**align §2.6 新增**：

```
#### 2.6 依赖健康度

- 检测循环依赖：BR-A → BR-B → BR-A
- 检测关键路径：找出被最多 BR 依赖的"瓶颈" BR
- 检测就绪度：依赖项未完成但自身已排入迭代 → 风险提示
```

---

### 3.7 反馈闭环回溯

**问题**：价值链只有正向（OPP→CR），无反向验证。

**涉及文件变更**：

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 修改 | `biz-procedures-align.md` | 新增 §2.7 MoS 达成度检查 |

**align §2.7 新增**：

```
#### 2.7 MoS 达成度（反向回溯）

对每个已有 MoS 的 Epic，计算达成进度：
- 读取 Epic MoS checkbox 列表
- 统计 [x] vs [ ] 比例
- 对照 BR 完成度：所有 BR 完成 → Epic MoS 应有进展
- 发现异常：BR 全部完成但 MoS 无一勾选 → 提醒："EPIC-001 的 BR 已全部完成，但 MoS 尚未评估。建议 /pace-retro 评估达成度"
```

---

### 3.8 prompt Hook 试点

**问题**：创建 Epic/BR 时可能与 OBJ 语义不对齐，目前只能事后 align 发现。

**前置条件**：3.1 完成（Hooks 基础设施已建立）。

**方案**：在 3.1 的 Hook 配置中追加一个 prompt 类型检查，仅对 `epics/EPIC-*.md` 写入生效。

**注意**：component-reference.md 确认 prompt Hook 具有语义理解能力，适合替代正则匹配做复杂判断。整个项目中 pace-dev 已使用 command Hook，但 prompt 类型尚无 Skill 级使用先例（全局 hooks.json 也未使用）。建议作为试点但标记为实验性。

**涉及文件变更**：

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 修改 | `skills/pace-biz/SKILL.md` | hooks 配置追加 prompt 类型 |

**Hook 配置追加**：

```yaml
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/skill/pace-biz-scope-check.mjs"
          timeout: 5
    - matcher:
        tool_name: "Write"
        path_pattern: "**/.devpace/epics/EPIC-*.md"
      hooks:
        - type: prompt
          prompt: "检查即将写入的 Epic 文件：1) OBJ 关联是否存在于 project.md？2) MoS 是否使用了可度量的表述？如有问题输出改进建议并阻断（exit 2）。"
          timeout: 15
```

**风险**：prompt Hook 每次调用消耗 LLM 推理时间（~10-15s），对 pace-biz 写入频率（每次会话 1-5 次）可接受。

---

## 五、P2 改进项概要

| # | 改进 | 涉及文件 | 工作量 | 说明 |
|---|------|---------|--------|------|
| 3.9 | `$0`/`$1` 按位参数 | 各 procedures 参数引用 | 小 | 提升路由确定性，非紧急 |
| 3.10 | discover 渐进产出 | `biz-procedures-discover.md` | 中 | `--depth opp\|epic\|pf` 控制产出深度 |
| 3.11 | 搜索与过滤 | `biz-procedures-view.md` | 中 | `view --status/--obj/--keyword` 参数 |
| 3.13 | 领域模板 | 新建 `knowledge/domain-templates/` | 大 | SaaS/移动/API 预定义模板 |

P2 项不在本轮实施范围，记录为后续候选。

---

## 六、实施计划

### 批次 1：产品层 P0（并行执行）

**范围**：3.1 + 3.2 + 3.3 + 3.4（全部为产品层文件）

```
Task A: 3.1 Hooks 写入保护
  - 新建 hooks/skill/pace-biz-scope-check.mjs
  - 修改 skills/pace-biz/SKILL.md（hooks frontmatter）
  验证：尝试写入非 .devpace/ → 阻断

Task B: 3.2 refine 子命令
  - 新建 skills/pace-biz/biz-procedures-refine.md
  - 修改 skills/pace-biz/SKILL.md（路由表 + 子命令列表）
  - 修改 skills/pace-biz/biz-procedures-output.md（新增格式）
  验证：/pace-biz refine BR-001 → 进入交互精炼

Task C: 3.3 优先级框架 + 3.4 体验统一
  - 修改 biz-procedures-decompose.md（Value x Effort）
  - 修改 biz-procedures-align.md（优先级分布 + 内联引导）
  - 修改 biz-procedures-view.md（内联操作引导）
  - 修改 biz-procedures-output.md（align/view 格式更新）
  验证：decompose 时出现评估矩阵；view/align 有内联命令
```

### 批次 2：产品层 P1

**范围**：3.5 + 3.6 + 3.7 + 3.8

```
Task D: 3.5 角色感知
  - 修改 SKILL.md 公共前置
  - 修改 view/decompose/discover procedures

Task E: 3.6 依赖追踪
  - 修改 knowledge/_schema/epic-format.md
  - 修改 decompose/align procedures

Task F: 3.7 反馈闭环 + 3.8 prompt Hook
  - 修改 align procedures
  - 修改 SKILL.md hooks（追加 prompt）
```

### 批次 3：开发层（独立执行）

**范围**：3.12（产品层变更完成后，独立批次更新开发层）

```
Task G: §22 修正
  - 修改 docs/design/design.md §12 映射表
```

### 质量门

每批次完成后：
1. `bash dev-scripts/validate-all.sh` 全部通过
2. `grep -r "docs/\|\.claude/" rules/ skills/ knowledge/` 返回空（分层完整性）
3. SKILL.md 行数检查（路由表 + hooks 不超 ~150 行）
4. 手动验证：`claude --plugin-dir ./` 加载无报错

---

## 七、SKILL.md 变更预览（批次 1 完成后）

```yaml
---
description: Use when user says "业务机会", "专题", "Epic", "分解需求", "精炼", "细化", "战略对齐", "业务全景", "业务规划", "需求发现", "头脑风暴", "brainstorm", "导入需求", "从文档导入", "代码分析需求", "技术债务盘点", "discover", "import", "infer", "refine", "pace-biz", or wants to create opportunities/Epics, decompose/refine requirements, discover/import/infer features. NOT for implementation (/pace-dev), existing item changes (/pace-change), or iteration planning (/pace-plan).
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[opportunity|epic|decompose|refine|align|view|discover|import|infer] [EPIC-xxx|BR-xxx|PF-xxx] <描述|路径>"
model: sonnet
context: fork
agent: pace-pm
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/skill/pace-biz-scope-check.mjs"
          timeout: 5
---
```

路由表新增行：

```markdown
| refine | project.md, requirements/BR-xxx.md | project.md, requirements/ | biz-procedures-refine.md |
```

子命令列表新增：

```markdown
**精炼型**（深化已有实体）：
- `refine <BR-xxx|PF-xxx>` → 交互式补充验收标准、边界条件、用户故事
```

---

## 八、风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| Hook 脚本阻断合法写入 | 低 | 高 | pace-biz 仅写 .devpace/，判断逻辑简单；参考 pace-init 成熟模式 |
| refine 与 pace-change modify 边界模糊 | 中 | 中 | SKILL.md 明确区分：refine=深化（同方向），modify=改变（新方向）|
| prompt Hook 延迟影响体验 | 中 | 低 | 仅对 Epic 写入触发（频率低），timeout 15s |
| 角色适配增加 procedures 复杂度 | 中 | 中 | 遵循"仅调整输出措辞，不改底层逻辑"原则 |
| 优先级矩阵用户觉得繁琐 | 低 | 低 | 用户可直接覆盖，矩阵仅为建议 |

---

## 九、与 roadmap/progress 的关系

| 改进项 | roadmap 关联 | 新增任务? |
|--------|-------------|----------|
| 3.1 Hooks | 无现有任务 | 需新增 |
| 3.2 refine | Backlog B1 | B1 升级为正式任务 |
| 3.3 优先级 | 无 | 需新增 |
| 3.4 体验统一 | 无 | 需新增 |
| 3.5 角色感知 | 无 | 需新增 |
| 3.6 依赖追踪 | 无 | 需新增 |
| 3.7 闭环回溯 | 无 | 需新增 |
| 3.8 prompt Hook | 无 | 需新增 |
| 3.12 §22 修正 | 无 | 需新增 |

---

## 十、文件变更索引

### 新建文件（2 个）

| 文件 | 层级 | 批次 |
|------|------|------|
| `hooks/skill/pace-biz-scope-check.mjs` | 产品 | 1 |
| `skills/pace-biz/biz-procedures-refine.md` | 产品 | 1 |

### 修改文件（产品层，8 个）

| 文件 | 批次 | 涉及改进项 |
|------|------|-----------|
| `skills/pace-biz/SKILL.md` | 1+2 | 3.1, 3.2, 3.5, 3.8 |
| `skills/pace-biz/biz-procedures-output.md` | 1+2 | 3.2, 3.4 |
| `skills/pace-biz/biz-procedures-decompose.md` | 1+2 | 3.3, 3.5, 3.6 |
| `skills/pace-biz/biz-procedures-align.md` | 1+2 | 3.3, 3.4, 3.6, 3.7 |
| `skills/pace-biz/biz-procedures-view.md` | 1 | 3.4, 3.5 |
| `skills/pace-biz/biz-procedures-discover.md` | 2 | 3.5 |
| `knowledge/_schema/epic-format.md` | 2 | 3.6 |
| 无需修改 plugin.json | — | pace-biz 已注册，子命令变更不影响 |

### 修改文件（开发层，1 个，独立批次）

| 文件 | 批次 | 涉及改进项 |
|------|------|-----------|
| `docs/design/design.md` | 3 | 3.12 |
