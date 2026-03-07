# Skill Creator 详细设计文档

> **源码**：[anthropics/skills/skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
> **版本基准**：2026-03 main 分支
> **文档目的**：为团队提供 Anthropic 官方 skill-creator 的完整中文设计解读，支撑 devpace 的 Skill 开发与评估体系建设

---

## 目录

1. [概述与定位](#1-概述与定位)
2. [目录结构](#2-目录结构)
3. [核心架构](#3-核心架构)
4. [SKILL.md 主工作流详解](#4-skillmd-主工作流详解)
5. [Agent 子系统](#5-agent-子系统)
6. [Python 脚本工具链](#6-python-脚本工具链)
7. [Eval Viewer 可视化系统](#7-eval-viewer-可视化系统)
8. [数据 Schema 规范](#8-数据-schema-规范)
9. [关键设计模式](#9-关键设计模式)
10. [Description 优化系统](#10-description-优化系统)
11. [打包与分发](#11-打包与分发)
12. [环境适配](#12-环境适配)
13. [与 devpace 的集成要点](#13-与-devpace-的集成要点)

---

## 1. 概述与定位

### 1.1 核心使命

Skill Creator 是 Anthropic 官方提供的 **Skill 全生命周期管理工具**，覆盖从意图捕获到打包分发的完整流程。其核心理念是：

> **Skill 不是写出来的，是迭代测出来的。**

它将 Skill 开发从"写完即用"的线性模式，升级为 **"编写→测试→评估→改进→再测试"** 的闭环迭代模式。

### 1.2 解决的问题

| 问题 | 解决方案 |
|------|---------|
| Skill 写出来不知道好不好 | 自动生成测试用例（evals），量化评估 |
| 有 Skill 和没 Skill 差别多大 | 并行对比实验（with-skill vs baseline） |
| description 触发不准（误触发/漏触发） | Description 自动优化循环 |
| 改进方向不明确 | 盲比较 + 后验分析，给出具体改进建议 |
| 人工评审效率低 | 自包含 HTML Viewer，离线可用 |

### 1.3 适用场景

- 新建 Skill 并验证其有效性
- 优化已有 Skill 的触发精度（description）
- A/B 对比两个 Skill 版本的优劣
- Skill 打包分发前的质量门禁

---

## 2. 目录结构

```
skill-creator/
├── SKILL.md                          # 主工作流定义（~480 行）
├── LICENSE.txt                       # Apache 2.0
├── agents/                           # 3 个专用评估 Agent
│   ├── grader.md                     # 断言评分器
│   ├── comparator.md                 # 盲比较器
│   └── analyzer.md                   # 后验分析器
├── assets/
│   └── eval_review.html              # Description 优化评估集编辑器
├── eval-viewer/
│   ├── generate_review.py            # 从运行数据生成 Viewer HTML
│   └── viewer.html                   # 交互式评审界面（~43.9KB，自包含）
├── references/
│   └── schemas.md                    # 全部 JSON Schema 定义
└── scripts/                          # Python 自动化工具链
    ├── __init__.py
    ├── run_eval.py                   # Description 触发测试
    ├── run_loop.py                   # 优化主循环
    ├── improve_description.py        # Description 改进（Claude API + 扩展思考）
    ├── aggregate_benchmark.py        # 基准数据聚合与统计
    ├── generate_report.py            # HTML 报告生成
    ├── package_skill.py              # Skill 打包（.skill 格式）
    ├── quick_validate.py             # 快速结构验证
    └── utils.py                      # 共享工具（frontmatter 解析等）
```

### 2.1 关键分层

| 层次 | 内容 | 消费者 |
|------|------|--------|
| **工作流层** | SKILL.md | Claude（作为执行引擎） |
| **评估层** | agents/ + scripts/ | Claude（子 Agent）+ Python 运行时 |
| **可视化层** | eval-viewer/ + assets/ | 人类（浏览器）|
| **契约层** | references/schemas.md | 全部组件（数据交换格式） |

---

## 3. 核心架构

### 3.1 整体工作流

```
                    ┌─────────────────────────────────────────────┐
                    │              SKILL CREATOR 主循环            │
                    └─────────────────────────────────────────────┘
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          ▼                             ▼                             ▼
   ┌─────────────┐            ┌──────────────────┐          ┌──────────────┐
   │  Phase 1    │            │    Phase 2       │          │   Phase 3    │
   │  意图→草稿  │──────────▶│  测试→评估→改进  │────────▶│  优化→分发   │
   │             │            │   (可多轮迭代)    │          │              │
   └─────────────┘            └──────────────────┘          └──────────────┘
   │ 捕获意图     │            │ 生成运行          │          │ Description  │
   │ 访谈研究     │            │ 评分断言          │          │   优化循环    │
   │ 编写 SKILL.md│            │ 聚合基准          │          │ 打包分发      │
   │ 创建 evals   │            │ 启动 Viewer       │          │              │
   └─────────────┘            │ 读取反馈          │          └──────────────┘
                              │ 盲比较(可选)      │
                              │ 后验分析(可选)    │
                              └──────────────────┘
```

### 3.2 数据流

```
用户意图
    │
    ▼
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ SKILL.md│────▶│ evals.json│────▶│ 并行运行 │────▶│grading/  │
│ (草稿)  │     │ (测试集) │     │ (子Agent) │     │timing.json│
└─────────┘     └──────────┘     └──────────┘     └──────────┘
                                                        │
                                                        ▼
                                                  ┌──────────┐
                                                  │benchmark │
                                                  │.json/.md │
                                                  └──────────┘
                                                        │
                                                        ▼
                                                  ┌──────────┐
                                     ┌───────────▶│ viewer   │◀──── 人类反馈
                                     │            │ .html    │────▶ feedback.json
                                     │            └──────────┘
                                     │                  │
                                     │                  ▼
                                ┌──────────┐     ┌──────────┐
                                │comparison│     │ analysis │
                                │.json     │     │.json     │
                                └──────────┘     └──────────┘
                                (盲比较结果)      (改进建议)
```

### 3.3 执行模型

Skill Creator 有两种执行模式：

| 模式 | 执行方式 | 适用场景 |
|------|---------|---------|
| **内嵌模式** | Claude 直接执行 SKILL.md 中的步骤 | 完整 Skill 创建与迭代 |
| **脚本模式** | Python 脚本自动化执行 | Description 优化、批量测试 |

两者通过共享的 JSON Schema（§8）实现数据互通。

---

## 4. SKILL.md 主工作流详解

### 4.1 Phase 1：意图捕获与草稿

#### Step 1：捕获意图

- 用户描述想要的 Skill 行为
- Claude 提炼核心目的和使用场景
- 确定 Skill 应何时被触发（description 候选）

#### Step 2：访谈与研究

- 通过问答深入理解需求
- 研究已有类似 Skill 或模式
- 确定 Skill 的边界（做什么 / 不做什么）

#### Step 3：编写 SKILL.md

遵循 **渐进披露三层架构**：

```
Layer 1：元数据（frontmatter）
    ├── name：显示名称
    ├── description：触发条件（CSO 规则：只写"何时触发"，不写"做什么"）
    ├── allowed-tools：免确认工具
    └── 其他可选字段

Layer 2：SKILL.md 正文
    ├── 控制在 500 行以内
    ├── 包含完整工作流指令
    └── 可引用外部参考文件

Layer 3：捆绑资源
    ├── references/：大型参考文档（需 TOC）
    ├── scripts/：自动化脚本
    └── agents/：专用子 Agent
```

**CSO（Conditional Skill Observation）规则**——这是 description 编写的核心原则：

| 规则 | 正确示例 | 错误示例 |
|------|---------|---------|
| 只写"何时触发" | `Use when creating or modifying skills` | `Creates skills with eval loops and optimization` |
| 开头用 "Use when" | `Use when user wants to test skill quality` | `Skill testing and optimization tool` |
| 包含具体触发词 | `Use when user says "create skill", "test skill", "skill-creator"` | `Handles skill development tasks` |
| 不描述内部步骤 | `Use when skill needs quality evaluation` | `Runs evals, grades assertions, launches viewer` |

**原因**：如果 description 包含了工作流步骤摘要，Claude 可能根据摘要直接行动而不加载完整 SKILL.md 内容，导致执行不完整。

#### Step 4：创建测试用例（evals）

evals 是 Skill Creator 评估体系的基石：

```json
{
  "evals": [
    {
      "name": "唯一标识名",
      "description": "测试场景描述",
      "prompt": "模拟用户输入",
      "expectations": [
        {
          "text": "断言描述（期望行为）",
          "critical": true
        }
      ]
    }
  ]
}
```

**设计要点**：

- 每个 eval 是一个独立的用户场景
- `prompt` 模拟真实用户输入（自然语言，不含指令）
- `expectations` 是可验证的行为断言，不是实现细节
- `critical: true` 表示此断言为必须通过项
- 建议覆盖：正常路径、边界情况、不应触发的负面案例

### 4.2 Phase 2：测试与评估（核心循环）

这是 Skill Creator 最精密的部分，分为 5 个步骤：

#### Step 1：并行生成运行

对每个 eval，**同时**启动两个子 Agent：

```
┌─────────────────────────────────────────────────────┐
│  eval_case_1                                        │
│  ┌──────────────────┐  ┌──────────────────────────┐│
│  │ Agent A (with)   │  │ Agent B (baseline)       ││
│  │ skill 已加载     │  │ 无 skill（Claude 默认）  ││
│  │ → output_with/   │  │ → output_without/        ││
│  └──────────────────┘  └──────────────────────────┘│
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  eval_case_2 （并行启动）                            │
│  ┌──────────────────┐  ┌──────────────────────────┐│
│  │ Agent A (with)   │  │ Agent B (baseline)       ││
│  └──────────────────┘  └──────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

**关键约束**：
- 每个 eval 的 with 和 without 必须在同一轮并行生成，不可串行
- 所有 eval case 也尽量并行启动
- 运行结果写入工作区的独立子目录

#### Step 2：起草断言

- 读取运行输出
- 根据 eval 的 expectations 生成具体的通过/失败断言
- 断言必须基于"真实完成"而非"表面合规"
  - 正确：`文件 X 已创建且包含函数 Y`
  - 错误：`Claude 说它创建了文件 X`（可能只是声称但未实际执行）

#### Step 3：捕获时间数据

- 从任务通知中提取执行时长和 token 用量
- 写入 `timing.json`
- **⚠️ 仅一次机会**：timing 数据来自运行时通知，错过无法恢复

```json
{
  "total_duration_ms": 15234,
  "total_tokens": 8500,
  "input_tokens": 2100,
  "output_tokens": 6400,
  "captured_at": "2026-03-05T10:30:00Z"
}
```

#### Step 4：评分与聚合

调用 **grader Agent**（§5.1）对每个运行评分，然后通过 `aggregate_benchmark.py`（§6.4）聚合为基准数据：

```
各 eval 的 grading.json
        │
        ▼
aggregate_benchmark.py
        │
        ▼
benchmark.json（统计摘要）
+ benchmark.md（可读报告）
```

聚合统计包含：
- 通过率（pass_rate）：均值、标准差、最小/最大值
- 时间指标：均值、标准差
- Token 用量：均值、标准差
- 配置间差异（Δ）：with_skill vs without_skill

#### Step 5：启动 Viewer

生成自包含 HTML 文件并打开浏览器供人工审查（§7 详述）。

### 4.3 Phase 2 续：改进循环

读取 Viewer 中人类写入的 `feedback.json`，根据反馈修改 SKILL.md，然后重复 Phase 2。

**可选增强**——盲比较：

1. 调用 **comparator Agent**（§5.2），对两个版本做盲 A/B 评估
2. 调用 **analyzer Agent**（§5.3），分析获胜版本的优势和失败版本的问题
3. 根据分析结果指导下一轮改进

### 4.4 Phase 3：Description 优化与分发

见 §10（Description 优化系统）和 §11（打包与分发）。

---

## 5. Agent 子系统

### 5.1 Grader（评分 Agent）

**文件**：`agents/grader.md`
**职责**：评估单次运行是否满足 eval 断言

**8 步流程**：

```
1. 读取运行转录文件
2. 检查运行生成的输出文件（实际验证，不信"口头声明"）
3. 逐条评估断言
   ├── passed: true/false
   ├── evidence: 具体证据引用
   └── 强调"真实完成" vs "表面合规"
4. 提取运行中的关键声明（claims）
5. 验证每个声明是否有证据支撑
6. 读取用户笔记（若有）
7. 批评评估本身（自审环节）
   └── "这些断言是否真的验证了 Skill 质量？"
8. 写入 grading.json
```

**输出格式**（grading.json）：

```json
{
  "eval_name": "test-case-1",
  "configuration": "with_skill",
  "expectations": [
    {
      "text": "断言描述",
      "passed": true,
      "evidence": "来自转录第 N 行的证据引用"
    }
  ],
  "overall_assessment": "通过/失败原因总述",
  "eval_critique": "对评估方法本身的反思",
  "claims": ["声明1", "声明2"],
  "metrics": {
    "total_duration_ms": 15000,
    "total_tokens": 8500
  }
}
```

**设计亮点**：
- 自审机制（eval_critique）：不仅评分，还反思"评分方式本身是否合理"
- 证据链：每个 passed/failed 判断必须附带 evidence
- 声明验证：防止 Claude "说了做了但实际没做"的幻觉问题

### 5.2 Comparator（盲比较 Agent）

**文件**：`agents/comparator.md`
**职责**：不知道哪个是新版、哪个是旧版的情况下，比较两个运行输出的质量

**7 步流程**：

```
1. 读取两个输出（随机标记为 A/B，不暴露版本信息）
2. 理解任务要求（eval 的 prompt 和 expectations）
3. 生成评分标准
   ├── 内容维度：完整性、准确性、相关性
   └── 结构维度：组织性、可读性、规范遵循
4. 按标准评分
5. 检查断言通过情况
6. 做出获胜决定
   └── 优先输出质量 > 断言分数
7. 写入 comparison.json
```

**关键原则**：
- **保持盲性**：不知道哪个版本是"改进版"，防止偏见
- **果断决策**：必须选出胜者，不允许"差不多"
- **质量优先**：输出的实际质量比断言分数更重要

**输出格式**（comparison.json）：

```json
{
  "eval_name": "test-case-1",
  "winner": "A",
  "confidence": "high",
  "reasoning": "获胜原因详述",
  "rubric": {
    "content": { "A": 8, "B": 6, "notes": "A 的内容更完整..." },
    "structure": { "A": 7, "B": 7, "notes": "结构相当..." }
  },
  "assertion_check": {
    "A_passed": 4,
    "B_passed": 3
  }
}
```

### 5.3 Analyzer（后验分析 Agent）

**文件**：`agents/analyzer.md`
**职责**：理解为什么一个版本比另一个好，并给出改进建议

**两种模式**：

#### 模式 A：后验分析（比较后调用）

```
1. 读取比较结果（comparison.json）
2. 读取两份 SKILL.md（获胜版 + 落败版）
3. 读取运行转录
4. 分析指令遵循情况
   └── 哪些 Skill 指令被遵循了？哪些被忽略了？
5. 识别获胜者优势
   └── 具体哪些指令/模式导致了更好的输出？
6. 识别失败者弱点
   └── 哪些指令不够清晰或被误解？
7. 生成改进建议
   └── 具体的、可操作的修改建议
8. 写入 analysis.json
```

#### 模式 B：基准分析（聚合后调用）

```
1. 读取基准数据（benchmark.json）
2. 分析每个断言的通过/失败模式
3. 识别跨 eval 的共性模式
4. 分析指标模式（时间、token）
5. 生成笔记和建议
6. 写入分析笔记
```

**输出格式**（analysis.json）：

```json
{
  "eval_name": "test-case-1",
  "winner_advantages": [
    { "pattern": "优势模式描述", "evidence": "证据" }
  ],
  "loser_weaknesses": [
    { "pattern": "弱点描述", "suggestion": "改进建议" }
  ],
  "instruction_adherence": {
    "followed": ["指令1", "指令2"],
    "ignored": ["指令3"],
    "misinterpreted": ["指令4"]
  },
  "improvements": [
    {
      "priority": "high",
      "change": "具体修改描述",
      "rationale": "原因"
    }
  ]
}
```

---

## 6. Python 脚本工具链

### 6.1 run_eval.py —— Description 触发测试

**用途**：测试 Skill 的 description 是否能正确触发（Claude 是否会读取该 Skill）。

**工作原理**：

```
1. 构建临时 command 文件（包含 Skill 的 description）
2. 对每个查询运行 claude -p --stream-json
3. 分析 JSON 流输出，检测是否出现 Skill 读取事件
4. 返回触发率（trigger_rate）
```

**核心参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--skill-path` | Skill 目录路径 | 必填 |
| `--evals` | evals.json 路径 | 必填 |
| `--workers` | 并行数 | 4 |
| `--output` | 结果输出目录 | 必填 |

**输出**：每个查询的 pass/fail 状态 + 整体触发率。

### 6.2 run_loop.py —— 优化主循环

**用途**：自动化 "测试→改进→再测试" 循环，直到 description 达到目标精度。

**工作流**：

```
┌──────────────────────┐
│   初始 description   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐     失败
│   run_eval.py 测试   │────────┐
└──────────┬───────────┘        │
           │ 全部通过            ▼
           │              ┌───────────────────┐
           │              │ improve_description │
           │              │ .py 改进            │
           │              └─────────┬─────────┘
           │                        │
           │              ┌─────────▼─────────┐
           │              │ 更新 SKILL.md      │
           │              │ description        │
           │              └─────────┬─────────┘
           │                        │
           │                        ▼
           │              ┌───────────────────┐
           │              │ 再次 run_eval.py  │──── 循环
           │              └───────────────────┘
           ▼
   ┌──────────────┐
   │ 输出最优结果  │
   └──────────────┘
```

**关键特性**：
- **训练/测试分割**：60/40 比例，防止 description 过拟合训练集
- **历史追踪**：每轮迭代的 description 和分数都被记录
- **实时报告**：生成带自动刷新的 HTML 报告
- **最优选择**：循环结束后选择整体表现最好的 description（不一定是最后一轮）

### 6.3 improve_description.py —— Description 改进

**用途**：利用 Claude API（带扩展思考模式）智能改进 description。

**核心逻辑**：

```python
# 分析失败类型
false_positives = []  # 不应触发但触发了
false_negatives = []  # 应触发但没触发

# 构建改进 prompt
prompt = f"""
当前 description: {current}
误触发案例: {false_positives}
漏触发案例: {false_negatives}
历史尝试: {history}  # 避免重复

请改进 description，使其在不超过 1024 字符的前提下：
1. 修正误触发（更精确的条件限定）
2. 修正漏触发（补充缺失的触发关键词）
3. 不重复历史尝试
"""

# 使用扩展思考模式调用 Claude
response = claude_api(
    prompt=prompt,
    extended_thinking=True  # 关键：让 Claude 深入推理
)
```

**设计要点**：
- 使用扩展思考（extended thinking）模式，让 Claude 在修改前充分推理
- 传入历史尝试记录，避免在同一方向重复尝试
- 自动检测并截断超过 1024 字符的 description
- 完整记录推理过程（thinking + prompt + response）到日志

### 6.4 aggregate_benchmark.py —— 基准数据聚合

**用途**：将多个 eval 的评分结果聚合为统计摘要。

**聚合逻辑**：

```
输入：各 eval 的 grading.json + timing.json
输出：benchmark.json + benchmark.md

统计维度：
├── pass_rate（通过率）
│   ├── mean / stddev / min / max
│   └── 按 critical vs non-critical 分组
├── timing（执行时间）
│   ├── mean / stddev / min / max
│   └── with_skill vs without_skill
├── tokens（token 用量）
│   ├── mean / stddev / min / max
│   └── with_skill vs without_skill
└── deltas（配置间差异）
    ├── Δ pass_rate
    ├── Δ time
    └── Δ tokens
```

**⚠️ 字段命名强约束**：`configuration` 字段必须严格为 `"with_skill"` 或 `"without_skill"`——Viewer 硬编码了这两个值，名称不匹配会导致显示为零。

### 6.5 generate_report.py —— HTML 报告生成

**用途**：从 `run_loop.py` 的输出生成可视化的迭代报告。

**功能**：
- 交互式表格展示每轮迭代的结果
- 颜色区分训练集 / 测试集查询
- 显示每个查询的触发状态和通过/失败
- 支持自动刷新（供 `run_loop.py` 实时监控）

### 6.6 package_skill.py —— Skill 打包

**用途**：将 Skill 目录打包为可分发的 `.skill` 文件。

**流程**：

```
1. 调用 quick_validate.py 验证结构
2. 排除构建产物：__pycache__、node_modules、evals、workspace
3. 创建 zip 压缩包（.skill 扩展名）
4. 保持内部目录结构
```

### 6.7 quick_validate.py —— 快速验证

**用途**：最小化的 Skill 结构验证。

**验证项**：

| 检查项 | 规则 |
|--------|------|
| SKILL.md 存在 | 必须存在 |
| YAML frontmatter 有效 | 语法正确 |
| name 字段 | 存在、≤64 字符、kebab-case |
| description 字段 | 存在、≤1024 字符、无尖括号 |

### 6.8 utils.py —— 共享工具

**用途**：解析 SKILL.md 的 frontmatter，提取 name、description、正文内容。

**特性**：
- 支持 YAML 多行字符串格式：`>`、`|`、`>-`、`|-`
- 被 run_eval.py、improve_description.py 等多个脚本共享

---

## 7. Eval Viewer 可视化系统

### 7.1 架构

Viewer 是一个 **自包含 HTML 文件**（~43.9KB），所有数据内嵌，无外部依赖，可离线使用。

### 7.2 双标签页设计

```
┌──────────────────────────────────────────────────────┐
│  [📝 Outputs]  [📊 Benchmark]                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Outputs 标签页：                                    │
│  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │ With Skill      │  │ Without Skill            │  │
│  │                 │  │                          │  │
│  │ [运行输出]      │  │ [运行输出]               │  │
│  │                 │  │                          │  │
│  │ [断言评分]      │  │ [断言评分]               │  │
│  │  ✅ 断言1       │  │  ❌ 断言1                │  │
│  │  ✅ 断言2       │  │  ✅ 断言2                │  │
│  └─────────────────┘  └──────────────────────────┘  │
│                                                      │
│  💬 反馈区：                                         │
│  ┌──────────────────────────────────────────────┐   │
│  │ [文本框：输入你的反馈...]                     │   │
│  │ [自动保存到 feedback.json]                    │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  Benchmark 标签页：                                  │
│  ┌──────────────────────────────────────────────┐   │
│  │ 配置        | 通过率  | 时间    | Tokens     │   │
│  │ with_skill  | 85%    | 12.3s  | 8,500      │   │
│  │ without     | 60%    | 15.1s  | 10,200     │   │
│  │ Δ          | +25%   | -2.8s  | -1,700     │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  📈 历次迭代对比（若有多轮）                         │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 7.3 反馈机制

- 用户在 Viewer 中输入的反馈自动保存到 `feedback.json`
- Claude 在改进循环中读取 `feedback.json` 获取人类洞察
- 反馈与 eval name 关联，支持逐 eval 的精确反馈

### 7.4 生成方式

```python
# generate_review.py
def generate_viewer(workspace_path, output_path):
    """
    读取工作区中的所有运行数据，内嵌到 viewer.html 模板中。

    数据来源：
    - grading.json（评分）
    - timing.json（时间）
    - benchmark.json（聚合统计）
    - comparison.json（盲比较，可选）

    输出：自包含 HTML 文件
    """
```

### 7.5 `--static` 模式

在无浏览器的环境（如 Cowork）中，使用 `--static` 参数生成静态 HTML 文件，写入指定路径而非自动打开浏览器。

---

## 8. 数据 Schema 规范

所有数据交换通过 `references/schemas.md` 定义的 JSON Schema 约束。

### 8.1 Schema 清单

| Schema | 文件 | 生产者 | 消费者 |
|--------|------|--------|--------|
| evals.json | 用户/Claude 创建 | SKILL.md Step 4 | 所有评估步骤 |
| history.json | 自动生成 | 改进循环 | improve_description |
| grading.json | grader Agent | Step 4（评分） | aggregate_benchmark、Viewer |
| timing.json | 主工作流 | Step 3（捕获） | aggregate_benchmark、Viewer |
| benchmark.json | aggregate_benchmark | Step 4（聚合） | Viewer、analyzer Agent |
| comparison.json | comparator Agent | 盲比较 | analyzer Agent |
| analysis.json | analyzer Agent | 后验分析 | 改进循环 |

### 8.2 关键约束

1. **字段名硬编码依赖**：
   - `grading.json` 的 `expectations` 数组必须包含 `text`、`passed`、`evidence` 字段
   - `benchmark.json` 的 `configuration` 值必须是 `"with_skill"` / `"without_skill"`
   - Viewer 直接按这些名称渲染，不匹配则显示异常

2. **向后兼容**：
   - `aggregate_benchmark.py` 同时支持工作区目录布局和旧版目录布局
   - Schema 新增字段应设为可选，保持向后兼容

---

## 9. 关键设计模式

### 9.1 渐进披露（Progressive Disclosure）

```
用户感知层：description（数十字符）
    ↓ 触发后
工作流层：SKILL.md 正文（<500 行）
    ↓ 需要时
深度层：references/、scripts/、agents/（无限制）
```

这个三层架构确保：
- **首次加载成本低**：Claude 只需读 description 决定是否触发
- **工作流完整**：SKILL.md 包含完整指令
- **资源按需加载**：大型参考文档只在需要时读取

### 9.2 并行对比实验

```
同一 eval prompt
    ├── with-skill Agent ──→ 输出 A
    └── baseline Agent ────→ 输出 B

评估不是"A 好不好"，而是"A 比 B 好多少"。
```

**为什么不只测有 Skill 的？**
- 基线对比证明 Skill 的增量价值
- 防止"Skill 做的事情 Claude 本来就会做"的假阳性
- 量化 Skill 的 ROI（时间、token、质量三维对比）

### 9.3 盲评消除偏见

Comparator Agent 不知道哪个输出来自"改进版"，只看到 A 和 B。这消除了：
- 确认偏见（偏向认为新版更好）
- 锚定效应（知道版本后下意识找支持证据）
- 顺序效应（先看的影响判断）

### 9.4 自审机制（Eval Critique）

Grader Agent 不仅评分，还反思评估方法本身：

> "这些断言真的能验证 Skill 质量吗？有没有遗漏的维度？评分标准是否过于宽松/严格？"

这是一个元认知层，帮助在迭代中不断改进评估方法本身。

### 9.5 Train/Test 分割防过拟合

```
全部 eval queries
    ├── 60% 训练集 ──→ 用于 improve_description.py 分析失败模式
    └── 40% 测试集 ──→ 仅用于验证，不参与优化
```

最终选择的 description 必须在测试集上也表现良好，防止：
- description 过于针对特定查询措辞
- 优化结果在新场景下失效

### 9.6 证据链完整性

从断言到判断，每一步都要求证据：

```
expectation.text（断言）
    → grading.evidence（判断证据）
        → comparison.reasoning（比较推理）
            → analysis.improvements（改进建议+原因）
```

没有"凭感觉"的空间——所有结论必须有可追溯的证据支撑。

---

## 10. Description 优化系统

### 10.1 完整优化流程

```
┌──────────────────────────────────────────────────────┐
│ Step 1：生成触发查询集                                │
│   ├── 正面查询（应触发，~12 条）                      │
│   ├── 负面查询（不应触发，~8 条）                     │
│   └── 用户审查并确认                                  │
├──────────────────────────────────────────────────────┤
│ Step 2：建立基线                                     │
│   └── 用当前 description 运行 run_eval.py            │
├──────────────────────────────────────────────────────┤
│ Step 3：优化循环（run_loop.py）                      │
│   ├── 评估当前 description                           │
│   ├── 分析失败模式（FP/FN）                          │
│   ├── 调用 improve_description.py（扩展思考模式）     │
│   ├── 应用新 description                             │
│   ├── 重新评估                                       │
│   └── 循环直到全部通过或达到最大迭代                   │
├──────────────────────────────────────────────────────┤
│ Step 4：应用最优结果                                  │
│   ├── 从历史中选出测试集得分最高的 description        │
│   ├── 更新 SKILL.md frontmatter                      │
│   └── 生成优化报告                                    │
└──────────────────────────────────────────────────────┘
```

### 10.2 查询集设计指南

| 类型 | 数量 | 设计原则 | 示例 |
|------|------|---------|------|
| 正面-精确 | ~4 | 直接使用 Skill 名称或命令 | `"帮我创建一个 skill"` |
| 正面-语义 | ~4 | 用自然语言描述意图 | `"我想让 Claude 自动格式化代码"` |
| 正面-边界 | ~4 | 触发条件的边界情况 | `"skill 效果不好怎么改进"` |
| 负面-相似 | ~4 | 表面相似但不应触发 | `"explain what a skill is"` |
| 负面-无关 | ~4 | 完全不相关的请求 | `"帮我写一个排序算法"` |

### 10.3 误触发与漏触发分析

```
误触发（False Positive）：
    查询本不应触发 Skill，但 description 过于宽泛导致触发
    → 修正：添加排除条件，收窄触发范围

漏触发（False Negative）：
    查询应该触发 Skill，但 description 不够精确导致未触发
    → 修正：补充触发关键词，扩展语义覆盖

两者的平衡是 description 优化的核心挑战。
```

---

## 11. 打包与分发

### 11.1 打包流程

```
1. quick_validate.py 验证结构
2. 排除列表：
   ├── __pycache__/
   ├── node_modules/
   ├── *.pyc
   ├── evals/（测试数据不分发）
   ├── *-workspace/（工作区不分发）
   └── .git/
3. 创建 .skill 文件（zip 格式）
4. 保持内部目录结构
```

### 11.2 .skill 文件格式

```
my-skill.skill（实际为 zip）
├── SKILL.md
├── agents/
│   └── *.md
├── references/
│   └── *.md
└── scripts/
    └── *.py
```

---

## 12. 环境适配

### 12.1 Claude Code（CLI）

默认执行环境。Viewer 自动打开浏览器，反馈实时写入文件系统。

### 12.2 Claude.ai（Web）

受限环境，无文件系统访问。Skill Creator 在此环境下：
- 省略文件写入步骤
- 直接在对话中展示结果
- 无法使用 Python 脚本

### 12.3 Cowork（协作环境）

- 使用 `--static` 模式生成 Viewer HTML
- 输出路径写入工作区内（不使用 /tmp/）
- 无法自动打开浏览器

---

## 13. 与 devpace 的集成要点

### 13.1 已有集成

devpace 已在 `plugin-dev-spec.md` 中定义了 skill-creator 集成约定：

| 产物 | 位置 | 入库 |
|------|------|------|
| 评估工作区 | `skills/<name>-workspace/` | 否（.gitignore） |
| eval 定义 | `tests/evaluation/<name>-evals.json` | 是（权威源） |
| `--static` HTML | `skills/<name>-workspace/iteration-N/review.html` | 否 |

### 13.2 可借鉴的设计理念

| Skill Creator 设计 | devpace 借鉴点 |
|-------------------|---------------|
| 渐进披露三层架构 | Skill 分拆模式（SKILL.md + *-procedures.md） |
| CSO 规则 | description 编写规则已融入 plugin-dev-spec.md |
| 证据链完整性 | 可融入 /pace-review 的 Gate 2 质量检查 |
| 盲比较消除偏见 | 可用于 Skill 版本对比评估 |
| Train/Test 分割 | 可用于 eval 设计防止过拟合 |
| 自审机制 | 可融入 /pace-retro 的复盘分析 |

### 13.3 推荐使用流程

在 devpace 开发 Skill 时的推荐集成步骤：

```
1. /pace-dev 开发 Skill 初稿
2. /skill-creator 创建 evals（测试集写入 tests/evaluation/）
3. /skill-creator 运行评估循环
4. /skill-creator 优化 description
5. /pace-review Gate 2 审查
6. /pace-test 验收测试
```

---

## 附录 A：关键文件大小参考

| 文件 | 大小 | 说明 |
|------|------|------|
| SKILL.md | ~16KB / ~480 行 | 主工作流，接近 500 行上限 |
| viewer.html | ~43.9KB / ~1300 行 | 自包含 HTML，无外部依赖 |
| schemas.md | ~5KB | 7 种 JSON Schema 定义 |
| 各 Agent | ~2-3KB 每个 | 流程化指令 |
| Python 脚本 | ~200-500 行每个 | 自动化工具 |

## 附录 B：术语表

| 英文术语 | 中文 | 含义 |
|----------|------|------|
| eval | 评估用例 | 单个测试场景（prompt + expectations） |
| assertion / expectation | 断言 | 期望行为的可验证描述 |
| grading | 评分 | 对断言的通过/失败判定 |
| benchmark | 基准 | 跨 eval 的聚合统计数据 |
| blind comparison | 盲比较 | 不知版本信息的 A/B 对比 |
| post-hoc analysis | 后验分析 | 比较后的深度原因分析 |
| progressive disclosure | 渐进披露 | 分层加载，按需暴露复杂度 |
| CSO | 条件式 Skill 观察 | description 只写触发条件的原则 |
| train/test split | 训练/测试分割 | 防止 description 过拟合的数据分组 |
| false positive (FP) | 误触发 | 不应触发但触发了 |
| false negative (FN) | 漏触发 | 应触发但没触发 |
| extended thinking | 扩展思考 | Claude API 的深度推理模式 |
