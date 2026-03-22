# devpace eval/ 优化方案：超越 skill-creator 的评估体系

> **版本**：v1.1 | **日期**：2026-03-22 | **状态**：Draft
> **前置研究**：[skill-eval-ecosystem-2026-03-21.md](../research/skill-eval-ecosystem-2026-03-21.md) | [harness-engineering-practices-2026-03-14.md](../research/harness-engineering-practices-2026-03-14.md)

---

## 0 Executive Summary

devpace eval/ 在**触发精度评估**和**回归防护**方面已领先 skill-creator（Wilson 置信区间、多维回归阈值、19-Skill 竞争检测、CI 零成本离线回归）。但在**行为评估**（107 条 assertions 定义了但无法自动执行）和**评估可视化**（结果只有 JSON 无仪表盘）两个维度存在结构性短板。

本方案补齐短板的同时，在四个维度建立 skill-creator 不具备的差异化能力：

| 差异化维度 | skill-creator 上限 | devpace 目标 |
|-----------|-------------------|-------------|
| 多 Skill 竞争评估 | 单 Skill 隔离测试 | 19 Skill 同时在场，测选择正确性 |
| CI + 人工双轨 | 纯人工驱动的浏览器交互 | CI 自动管线 + 交互式 viewer + 结构化反馈闭环 |
| 评估经济学 | 每次评估必须调用 Claude | 三层成本梯度（零成本/低成本/标准成本） |
| 反馈驱动改进 | 浏览器表单 → feedback.json → 人工消费 | 结构化 notes → 自动关联 assertion → 改进追踪 |

---

## 1 现状评估

### 1.1 devpace eval/ 资产盘点

| 组件 | 文件 | 状态 | 成熟度 |
|------|------|------|--------|
| 触发检测引擎 | `trigger.py` | 生产可用 | Agent SDK + Wilson CI + async 并发 |
| Description 优化 | `loop.py` + `improve.py` | 生产可用 | train/test split + 过拟合检测 + extended thinking |
| 回归检测 | `regress.py` + `baseline.py` | 生产可用 | 4 维阈值 + sibling 联动 + git diff 变更发现 |
| 结果持久化 | `results.py` | 生产可用 | 结构化 JSON + 历史归档 + 元数据 |
| CLI 入口 | `cli.py` + `__main__.py` | 生产可用 | 5 个子命令 |
| 行为 eval 数据 | `tests/evaluation/*/evals.json` | 数据就绪 | pace-dev 15 场景 107 assertions，框架完整 |
| 行为 eval 执行 | — | **缺失** | 无自动执行管线 |
| 评分引擎 | — | **缺失** | 无 grader |
| 可视化报告 | — | **缺失** | 仅 CLI 文本输出 |
| with/without 基线对照 | — | **缺失** | 无 Skill 价值度量 |

### 1.2 skill-creator 对标

| 能力 | devpace 现状 | skill-creator | 差距 |
|------|-------------|---------------|------|
| 触发检测 | Agent SDK (plugin 级) | `claude -p` (command 级) | **devpace 领先**：真实 plugin 加载，19 Skill 竞争 |
| 触发统计 | Wilson 置信区间 | 纯触发率 | **devpace 领先** |
| Description 优化 | 自动循环 + API | 自动循环 + CLI | 持平，devpace 有 extended thinking |
| 行为执行 | 无 | subagent 并行 spawn | **skill-creator 领先** |
| 行为评分 | 无 | grader agent + evidence | **skill-creator 领先** |
| 基线对照 | 无 | with/without 并行对比 | **skill-creator 领先** |
| 盲比较 | 无 | comparator + analyzer agent | **skill-creator 领先** |
| 可视化 | 无 | HTML viewer (Outputs + Benchmark) | **skill-creator 领先** |
| 回归检测 | 4 维阈值 + sibling | iteration 间线性对比 | **devpace 领先** |
| CI 集成 | GitHub Actions + 离线回归 | 无 | **devpace 领先** |
| 跨 Skill 防护 | 共享断言 + 交叉污染对 | 无 | **devpace 独有** |

---

## 2 目标架构

### 2.1 五层评估栈

```
Layer 6: Viewer         交互式 eval viewer server + 人工反馈闭环 (新建)
Layer 5: Report         静态 HTML 仪表盘 + CI 集成报告 (新建)
Layer 4: Regression     多维回归 + sibling 联动 + 离线 (已有)
Layer 3: Behavioral     行为执行 → 评分 → 基线对照 (新建)
Layer 2: Trigger        触发精度 + Wilson CI + Description 优化 (已有)
Layer 1: Static         pytest 结构检查 + validate-all.sh (已有)
```

skill-creator 覆盖 Layer 2-3 + 交互 viewer，但无 CI 管线和回归框架。devpace 目标是六层全覆盖——CI 自动管线（Layer 1-5）和人工迭代通道（Layer 6）双轨并行。

### 2.2 数据流

```
                          ┌─────────────────────────┐
 trigger-evals.json ──────► Layer 2: Trigger Eval   ├──► latest.json
                          └───────────┬─────────────┘       │
                                      │                     ▼
                          ┌───────────▼─────────────┐  ┌─────────┐
 evals.json ──────────────► Layer 3: Behavioral Eval├──► grading/ │
                          │   ┌──────────────┐      │  └────┬────┘
                          │   │ env fixture  │      │       │
                          │   │ spawn agent  │      │       ▼
                          │   │ collect output│      │  ┌─────────┐
                          │   │ grade assert │      │  │benchmark│
                          │   │ (opt) blind  │      │  └────┬────┘
                          │   └──────────────┘      │       │
                          └─────────────────────────┘       │
                                                            ▼
                          ┌─────────────────────────┐  ┌─────────┐
 baseline.json ───────────► Layer 4: Regression     ├──► report/  │
 latest.json ─────────────►   multi-dim + sibling   │  └────┬────┘
                          └─────────────────────────┘       │
                                                            ▼
                          ┌─────────────────────────┐
                          │ Layer 5: Report          │
                          │   static HTML dashboard  │
                          │   CI annotation          │
                          └────────────┬────────────┘
                                       │
                                       ▼
                          ┌─────────────────────────┐
                          │ Layer 6: Viewer          │
                          │   interactive server     │
                          │   feedback collection    │──► notes.jsonl
                          │   iteration comparison   │
                          └─────────────────────────┘
```

### 2.3 目录结构设计

#### 设计原则

1. **功能内聚**：同一评估域的文件放同一子目录
2. **依赖单向**：`core/` ← `trigger/`/`behavior/`/`regression/` ← `review/` ← `cli.py`，不反向
3. **入口在根**：`cli.py`、`__main__.py` 保持包根级，是唯一跨子目录的路由层
4. **向后兼容**：`shim.py` 保留，维持现有 Makefile 调用路径

#### 目录结构

```
eval/
│
├── core/                    # 共享基础设施（无域逻辑）
│   ├── __init__.py          #   re-export: results, skill_io
│   ├── skill_io.py          #   SKILL.md frontmatter 读写
│   └── results.py           #   结果持久化、路径常量、元数据
│
├── trigger/                 # 触发精度评估 + description 优化
│   ├── __init__.py          #   re-export: detect, loop, improve, apply
│   ├── detect.py            #   Agent SDK 触发检测引擎 (原 trigger.py)
│   ├── improve.py           #   Anthropic API description 生成 (原 improve.py)
│   ├── loop.py              #   优化循环 + train/test split (原 loop.py)
│   └── apply.py             #   description diff/apply (原 apply.py，消除重复)
│
├── behavior/                # 行为评估：执行 + 评分 + 对照 (Phase 1-2 新建)
│   ├── __init__.py          #   re-export: execute, grader, benchmark, comparator
│   ├── execute.py           #   env fixture + Agent SDK 行为执行
│   ├── grader.py            #   混合三级评分 (G1 程序化 / G2 正则 / G3 LLM)
│   ├── benchmark.py         #   with/without 基线对照 + 统计聚合
│   └── comparator.py        #   盲 A/B 比较 (Phase 3)
│
├── regression/              # 回归检测 + 基线管理
│   ├── __init__.py          #   re-export: detect, baseline
│   ├── detect.py            #   多维回归检测 + sibling 联动 (原 regress.py)
│   └── baseline.py          #   基线 save/diff (原 baseline.py)
│
├── review/                  # 人工审查：可视化 + 反馈 + 质量分析
│   ├── __init__.py          #   re-export: report, viewer, feedback, analyzer
│   ├── report.py            #   静态 HTML 仪表盘生成
│   ├── viewer.py            #   交互式 eval viewer server
│   ├── feedback.py          #   结构化反馈收集 + notes.jsonl 管理
│   └── analyzer.py          #   断言区分度分析 + 评估质量检测
│
├── __init__.py              # 包入口 (版本号 + 子包 re-export)
├── __main__.py              # python3 -m eval 入口
├── cli.py                   # 统一 CLI 路由（唯一跨子目录导入点）
├── shim.py                  # 向后兼容层（Makefile/旧脚本）
├── _gate_sdk.py             # 独立脚本：快速门禁检查
└── eval-runner.sh           # 独立脚本：行为 eval shell 路由
```

#### 依赖关系图

```
                    ┌──────────────────────────────────────┐
                    │           cli.py (路由层)              │
                    │  唯一允许跨子目录导入的模块             │
                    └──┬──────┬──────────┬──────────┬──────┘
                       │      │          │          │
                       ▼      ▼          ▼          ▼
                  trigger/ behavior/ regression/ review/
                       │      │          │          │
                       │      │          │          │
                       └──┬───┴────┬─────┘          │
                          │        │                │
                          ▼        │                │
                       core/  ◄────┘                │
                       │                            │
                       └────────────────────────────┘

依赖规则：
  core/       → 无内部依赖（仅标准库 + anthropic SDK）
  trigger/    → core/
  behavior/   → core/
  regression/ → core/
  review/     → core/ + 读取 trigger/behavior/regression 的结果文件（JSON I/O，非代码导入）
  cli.py      → 所有子包（路由分发）
  shim.py     → 所有子包（兼容 re-export）
```

**关键约束**：`review/` 不 import `trigger/`、`behavior/`、`regression/` 的 Python 模块——它通过读取 `tests/evaluation/*/results/` 下的 JSON 文件消费结果。这保证子目录间零代码耦合。

#### 数据目录

```
tests/evaluation/
├── pace-dev/
│   ├── trigger-evals.json     # 触发评估查询集
│   ├── evals.json             # 行为评估场景 + assertions
│   └── results/
│       ├── latest.json        # 最近触发 eval 结果
│       ├── baseline.json      # 基线快照
│       ├── history/           # 按时间戳归档
│       ├── loop/              # description 优化结果
│       ├── grading/           # 行为 eval 评分结果 (P1 新增)
│       └── benchmark/         # with/without 对照结果 (P2 新增)
├── _fixtures/                 # 行为 eval 环境 fixture (P1 新增)
│   ├── ENV-DEV-A/
│   ├── ENV-DEV-B/
│   └── setup-fixtures.sh
├── _results/                  # 全局聚合报告 (P2 新增)
│   ├── dashboard.html         # 静态快照（CI artifact）
│   └── notes.jsonl            # 人工反馈日志
└── regress/
    └── latest-report.json
```

#### 迁移映射（现有文件 → 新位置）

| 现有文件 | 新位置 | 变更说明 |
|---------|--------|---------|
| `skill_io.py` | `core/skill_io.py` | 移动 |
| `results.py` | `core/results.py` | 移动 |
| `trigger.py` | `trigger/detect.py` | 移动 + 重命名 |
| `improve.py` | `trigger/improve.py` | 移动 |
| `loop.py` | `trigger/loop.py` | 移动 |
| `apply.py` | `trigger/apply.py` | 移动 + 重构（消除与 skill_io 的重复逻辑） |
| `regress.py` | `regression/detect.py` | 移动 + 重命名 |
| `baseline.py` | `regression/baseline.py` | 移动 |
| `cli.py` | `cli.py`（保持根级） | 更新 import 路径 |
| `shim.py` | `shim.py`（保持根级） | 更新 import 路径 |
| `__init__.py` | `__init__.py`（保持根级） | 增加子包 re-export |
| `__main__.py` | `__main__.py`（保持根级） | 不变 |
| `_gate_sdk.py` | `_gate_sdk.py`（保持根级） | 独立脚本，不变 |
| `eval-runner.sh` | `eval-runner.sh`（保持根级） | 独立脚本，不变 |

#### 子包 `__init__.py` re-export 策略

每个子包的 `__init__.py` re-export 常用符号，使得 `cli.py` 的导入路径简洁：

```python
# eval/core/__init__.py
from .results import (DEVPACE_ROOT, EVAL_DATA_DIR, SKILLS_DIR,
                      build_metadata, eval_score, results_dir_for, save_trigger_results)
from .skill_io import description_hash, read_description, read_skill_md, replace_description

# eval/trigger/__init__.py
from .detect import DEFAULT_MAX_TURNS, DEFAULT_RUNS, DEFAULT_TIMEOUT, run_eval_set
from .loop import run_loop

# eval/regression/__init__.py
from .detect import detect_changed_skills, run_regress
from .baseline import diff_baseline, save_baseline
```

`cli.py` 的导入从：

```python
# 迁移前
from .baseline import diff_baseline, save_baseline
from .regress import detect_changed_skills, run_regress
from .results import DEVPACE_ROOT, EVAL_DATA_DIR, SKILLS_DIR, build_metadata, save_trigger_results
from .skill_io import read_description
from .trigger import DEFAULT_MAX_TURNS, DEFAULT_RUNS, DEFAULT_TIMEOUT, run_eval_set
```

变为：

```python
# 迁移后
from .core import (DEVPACE_ROOT, EVAL_DATA_DIR, SKILLS_DIR,
                   build_metadata, read_description, save_trigger_results)
from .trigger import DEFAULT_MAX_TURNS, DEFAULT_RUNS, DEFAULT_TIMEOUT, run_eval_set, run_loop
from .regression import detect_changed_skills, run_regress, diff_baseline, save_baseline
# Phase 1+ 新增
from .behavior import run_behavioral_eval, grade_all, run_benchmark
from .review import generate_dashboard, start_viewer, append_note
```

---

## 3 实施方案

### Phase 1: 行为评估管线（P0 — 核心缺口）

**目标**：让 `evals.json` 中的 107 条 assertions 可自动执行和评分。

#### 3.1 环境 Fixture 系统

evals.json 中每个场景都有 `env` 字段（如 `ENV-DEV-A`、`ENV-DEV-B`），指向不同的预置项目状态。

**设计**：

```
tests/evaluation/_fixtures/
├── ENV-DEV-A/           # 空项目 + devpace 已初始化，无 CR
│   ├── .devpace/
│   │   ├── state.md
│   │   └── backlog/
│   └── src/             # 最小项目骨架
├── ENV-DEV-B/           # 有 3 个既存 CR (CR-001~003)
│   ├── .devpace/
│   │   ├── state.md     # current-work: CR-002
│   │   └── backlog/
│   │       ├── CR-001.md  # status: merged
│   │       ├── CR-002.md  # status: developing
│   │       └── CR-003.md  # status: created
│   └── src/
└── setup-fixtures.sh    # 从模板生成 fixture（幂等）
```

**Fixture 生成策略**：脚本化生成而非静态目录。原因：
1. fixture 中包含 git 仓库状态（branch、commit history），不宜 check in
2. 需要按 evals.json 的 env_description 动态调整

```bash
# setup-fixtures.sh 伪码
create_fixture "ENV-DEV-A" \
  --devpace-init \
  --no-cr \
  --src-template "minimal-node"

create_fixture "ENV-DEV-B" \
  --devpace-init \
  --cr "CR-001:merged" "CR-002:developing" "CR-003:created" \
  --state-current "CR-002" \
  --src-template "minimal-node"
```

#### 3.2 行为执行引擎 (`behavior.py`)

**核心函数**：

```python
async def run_behavioral_eval(
    skill_name: str,
    eval_case: dict,       # evals.json 中的单个场景
    fixture_dir: Path,     # 对应 env fixture 目录
    timeout: int = 300,    # 行为 eval 比触发 eval 更长
    model: str | None = None,
) -> BehavioralResult:
    """在 fixture 环境中执行 eval prompt，收集产出。"""
```

**执行流程**：

```
1. 复制 fixture → 临时工作目录（隔离，不污染 fixture）
2. 初始化 git repo（如果 fixture 需要 git 状态）
3. 通过 Agent SDK 运行 eval prompt：
   options = ClaudeAgentOptions(
       cwd=temp_dir,
       plugins=[{"type": "local", "path": devpace_root}],
       permission_mode="bypassPermissions",
       max_turns=20,  # 行为 eval 允许更多轮次
       model=model,
   )
4. 收集执行 transcript（所有 AssistantMessage + ToolUseBlock）
5. 收集 .devpace/ 目录变更（diff fixture vs 执行后状态）
6. 收集 git log（新增 commit）
7. 计时 + token 统计
8. 返回 BehavioralResult(transcript, devpace_diff, git_log, timing)
```

**与 skill-creator 的关键差异**：
- skill-creator 用 `claude -p` subprocess，每个 eval 一个独立进程
- devpace 用 Agent SDK async，支持更细粒度的 ToolUseBlock 检查
- devpace 加载完整 plugin（19 Skill 竞争），不是单 Skill 隔离

#### 3.3 混合评分引擎 (`grader.py`)

skill-creator 完全依赖 LLM grader agent。devpace 设计**三级评分**，降低成本、提高确定性：

| 级别 | 评分方式 | 适用 assertion type | 成本 |
|------|---------|-------------------|------|
| G1 | 程序化检查 | `file_check`、`content_check` | 零 |
| G2 | 正则/结构匹配 | `output_check`（有明确格式） | 零 |
| G3 | LLM-as-judge | `behavior_check`、复杂 `output_check` | 低（Haiku） |

```python
class Grader:
    def grade(self, assertion: dict, result: BehavioralResult) -> GradingResult:
        atype = assertion.get("type", "output_check")
        if atype == "file_check":
            return self._grade_file(assertion, result)
        elif atype == "content_check":
            return self._grade_content(assertion, result)
        elif atype == "behavior_check":
            return self._grade_behavior_llm(assertion, result)
        else:
            return self._grade_output(assertion, result)

    def _grade_file(self, assertion: dict, result: BehavioralResult) -> GradingResult:
        """G1: 程序化文件检查。"""
        # 例：'New CR file created in .devpace/backlog/ with CR-xxx.md naming'
        # → 检查 devpace_diff 中是否有 backlog/CR-*.md 新增
        ...

    def _grade_content(self, assertion: dict, result: BehavioralResult) -> GradingResult:
        """G1/G2: 内容字段检查。"""
        # 例：'CR type is "feature"'
        # → 读 CR 文件，正则匹配 type: feature
        ...

    def _grade_behavior_llm(self, assertion: dict, result: BehavioralResult) -> GradingResult:
        """G3: LLM 评分，用于需要理解上下文的行为判断。"""
        # 例：'Intent checkpoint performed: asks user to confirm scope/approach'
        # → 提交 transcript 摘要 + assertion → Haiku 判断
        ...
```

**对比 skill-creator**：skill-creator 的 grader 是全 LLM（Opus 级），每条 assertion 都需要 LLM 判断。devpace 的混合方案预估 **60-70% 的 assertions 可程序化评分**，大幅降低成本。

#### 3.4 共享断言解析

devpace 独有的 `shared_pattern` 机制需要在评分时展开：

```python
# assertions 引用示例
{"text": "state.md updated with current-work", "shared_pattern": "SA-01"}

# grader 展开为 SA-01 定义的 3 条具体检查：
# 1. state.md current-work 字段反映最新操作结果
# 2. state.md next-step 字段包含下一步建议
# 3. state.md last-updated 时间戳已更新
```

这是 skill-creator 没有的——一条引用展开为多条检查，变更时一处更新。

#### 3.5 CLI 扩展

```bash
# 单场景行为 eval
python3 -m eval behavior --skill pace-dev --case 1 --timeout 300

# 全量行为 eval（pace-dev 的 15 个场景）
python3 -m eval behavior --skill pace-dev

# 冒烟（取 3 个代表性场景）
python3 -m eval behavior --skill pace-dev --smoke

# Makefile 快捷方式
make eval-behavior-one S=pace-dev CASE=1
make eval-behavior S=pace-dev
make eval-behavior-smoke
```

#### 3.6 输出格式 (grading.json)

兼容 skill-creator schema 的同时扩展 devpace 特有字段：

```json
{
  "skill": "pace-dev",
  "eval_id": 1,
  "eval_name": "new-feature-simple",
  "timestamp": "2026-03-22T14:30:00+00:00",
  "assertions": [
    {
      "text": "New CR file created in .devpace/backlog/ with CR-xxx.md naming",
      "type": "file_check",
      "grade_level": "G1",
      "passed": true,
      "evidence": "Found .devpace/backlog/CR-004.md (new file, 42 lines)",
      "shared_pattern": null
    },
    {
      "text": "Intent checkpoint performed: asks user to confirm scope/approach",
      "type": "behavior_check",
      "grade_level": "G3",
      "passed": true,
      "evidence": "Transcript turn 3: 'Before starting, let me confirm the scope...'",
      "shared_pattern": null
    },
    {
      "text": "state.md updated with current-work referencing the CR",
      "type": "file_check",
      "grade_level": "G1",
      "passed": true,
      "evidence": "state.md current-work: 'CR-004 (feature: API time endpoint)'",
      "shared_pattern": "SA-01"
    }
  ],
  "summary": {
    "total": 9, "passed": 8, "failed": 1,
    "by_grade": {"G1": {"total": 5, "passed": 5}, "G2": {"total": 1, "passed": 1}, "G3": {"total": 3, "passed": 2}}
  },
  "execution_metrics": {
    "tool_calls": {"Read": 12, "Write": 5, "Bash": 3, "Skill": 1},
    "total_turns": 8,
    "total_tokens": 45000,
    "duration_seconds": 127.3,
    "errors_encountered": 0
  },
  "devpace_diff": {
    "files_created": [".devpace/backlog/CR-004.md"],
    "files_modified": [".devpace/state.md"],
    "git_commits": 2
  }
}
```

---

### Phase 2: 基线对照 + 可视化报告

**目标**：量化 devpace 的价值（with/without 对比）+ 让评估结果可浏览。

#### 3.7 With/Without 基线对照 (`benchmark.py`)

skill-creator 的核心优势之一。devpace 适配方案：

```python
async def run_benchmark(
    skill_name: str,
    eval_cases: list[dict],
    fixture_dir: Path,
    runs_per_case: int = 3,
) -> BenchmarkResult:
    """对比 with_plugin 和 without_plugin 的行为差异。"""

    for case in eval_cases:
        for run in range(runs_per_case):
            # 并行 spawn 两个执行
            with_result = run_behavioral_eval(
                skill_name, case, fixture_dir,
                plugins=[devpace_root],  # 加载 devpace
            )
            without_result = run_behavioral_eval(
                skill_name, case, fixture_dir,
                plugins=[],  # 裸 Claude
            )
            # 分别评分
            with_grading = grader.grade_all(case["assertions"], with_result)
            without_grading = grader.grade_all(case["assertions"], without_result)
```

**聚合输出 (benchmark.json)**：

```json
{
  "skill": "pace-dev",
  "configurations": {
    "with_plugin": {
      "pass_rate": {"mean": 0.87, "stddev": 0.05, "min": 0.80, "max": 0.93},
      "duration": {"mean": 145.0, "stddev": 30.0},
      "tokens": {"mean": 52000, "stddev": 8000},
      "g1_pass_rate": 0.95,
      "g3_pass_rate": 0.72
    },
    "without_plugin": {
      "pass_rate": {"mean": 0.23, "stddev": 0.12, "min": 0.10, "max": 0.40},
      "duration": {"mean": 98.0, "stddev": 25.0},
      "tokens": {"mean": 35000, "stddev": 6000}
    },
    "delta": {
      "pass_rate": "+0.64",
      "token_overhead": "+48.6%"
    }
  }
}
```

**与 skill-creator 的差异**：
- skill-creator 对比"有 Skill 文件 vs 无 Skill 文件"
- devpace 对比"有 devpace plugin vs 裸 Claude"——度量整个 plugin 的价值，不只是单个 Skill

#### 3.8 双模式可视化（`report.py` + `viewer.py`）

评估结果需要同时服务两个场景：CI 管线（无人值守）和开发者迭代（高频交互）。用单一模式无法同时覆盖，因此设计**静态报告 + 交互 viewer 双模式**。

##### 3.8.1 静态 HTML 报告 (`report.py`)

面向 CI artifacts 和异步分享，单文件无依赖。

```python
def generate_dashboard(
    trigger_results: dict[str, dict],   # {skill_name: latest.json}
    behavior_results: dict[str, dict],  # {skill_name: grading.json}
    benchmark_results: dict | None,     # benchmark.json
    regression_report: dict | None,     # regress/latest-report.json
) -> str:
    """生成综合仪表盘 HTML（单文件，可离线打开）。"""
```

**用途**：CI artifact 上传、Slack 分享、离线查看。不需要运行 server。

##### 3.8.2 交互式 Eval Viewer (`viewer.py`)

面向开发者本地迭代——写 procedures → 跑 eval → 浏览器看结果 → 写反馈 → 改 procedures → 再跑。

```python
def start_viewer(
    workspace_dir: Path,           # tests/evaluation/<skill>/results/
    previous_workspace: Path | None = None,  # 上一轮迭代结果（可选）
    port: int = 8420,
    auto_open: bool = True,
) -> None:
    """启动交互式 eval viewer server。"""
```

**技术选型**：Python 标准库 `http.server`——零依赖，无需 npm/flask/fastapi。

```python
# viewer.py 核心结构
import http.server
import json
from pathlib import Path

class EvalViewerHandler(http.server.SimpleHTTPRequestHandler):
    """评估结果交互式浏览服务。"""

    def do_GET(self):
        if self.path == "/":
            self._serve_viewer_html()
        elif self.path == "/api/results":
            self._serve_json(self.server.results_data)
        elif self.path == "/api/previous":
            self._serve_json(self.server.previous_data)
        elif self.path == "/api/notes":
            self._serve_json(self.server.notes_data)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/feedback":
            self._handle_feedback()

    def _handle_feedback(self):
        """接收并持久化人工反馈。"""
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        # 追加到 notes.jsonl（不覆盖）
        feedback.append_note(
            skill=body["skill"],
            eval_id=body["eval_id"],
            assertion_idx=body.get("assertion_idx"),
            note=body["note"],
            author=body.get("author", "anonymous"),
        )
        self._respond_ok()
```

**Viewer 界面布局**（5 个 Tab）：

```
┌──────────────────────────────────────────────────────────┐
│ devpace Eval Viewer    pace-dev    iter-3   ← → (nav)    │
├──────────────────────────────────────────────────────────┤
│ Tab: Cases │ Benchmark │ Regression │ Notes │ Transcript │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ [Cases Tab — 逐 case 浏览]                                │
│ ┌────────────────────────────────────────────────────┐   │
│ │ Case 1: new-feature-simple           8/9 (89%)     │   │
│ │                                                    │   │
│ │ Prompt: 帮我实现一个返回当前时间的 API 接口         │   │
│ │                                                    │   │
│ │ Assertions:                                        │   │
│ │  [PASS] G1 New CR file created...                  │   │
│ │  [PASS] G1 CR type is 'feature'                    │   │
│ │  [FAIL] G3 Intent checkpoint performed  [+note]    │   │
│ │         evidence: "No checkpoint found..."         │   │
│ │                                                    │   │
│ │ [Previous iteration] (collapsed)                   │   │
│ │  iter-2: 7/9 (78%) — improved from 6/9            │   │
│ │                                                    │   │
│ │ Feedback: ┌──────────────────────────────────┐     │   │
│ │           │ S 场景不需要 intent checkpoint，  │     │   │
│ │           │ 这条 assertion 应标记为 N/A。     │     │   │
│ │           └──────────────────────────────────┘     │   │
│ │           [Save Note]                              │   │
│ └────────────────────────────────────────────────────┘   │
│                                                          │
│ [Benchmark Tab — with/without 对比]                      │
│  with_plugin: 87% ± 5%    without: 23% ± 12%            │
│  delta: +64%              token overhead: +48.6%         │
│                                                          │
│ [Transcript Tab — 原始执行记录]                           │
│  Turn 1: [Skill] pace-dev invoked                        │
│  Turn 2: [Read] .devpace/state.md                        │
│  Turn 3: [Write] .devpace/backlog/CR-004.md              │
│  ...                                                     │
│                                                          │
│ [Notes Tab — 累积反馈]                                    │
│  pace-dev#1 @assertion-3: "S 场景不需要..."  (2026-03-22)│
│  pace-dev#7 @eval: "Gate 1 缺少技术债务..."  (2026-03-21)│
└──────────────────────────────────────────────────────────┘
```

**与 skill-creator viewer 的差异**：

| 维度 | skill-creator viewer | devpace viewer |
|------|---------------------|----------------|
| 启动方式 | `generate_review.py`（每次生成新 HTML） | `viewer.py`（持久 server，热加载结果） |
| 反馈方式 | 全局文本框 → `feedback.json` 下载 | 逐 assertion 级别 → `notes.jsonl` 实时追加 |
| 历史对比 | `--previous-workspace` 参数 | 自动检测 `results/history/` 目录 |
| Transcript | 无（需要手动看文件） | 内置 Tab，格式化展示 |
| 评分明细 | 折叠显示 | 按 G1/G2/G3 分级着色 |
| 持久性 | 一次性（关掉就没了） | notes.jsonl 持久化，跨会话累积 |

#### 3.9 人工反馈闭环 (`feedback.py`)

行为评估中最有价值的改进信号来自人——自动评分发现"什么错了"，人发现"为什么错了"以及"assertion 本身是否合理"。

##### 3.9.1 反馈数据模型

```python
@dataclass
class EvalNote:
    """一条人工评估反馈。"""
    timestamp: str              # ISO 8601
    skill: str                  # pace-dev
    eval_id: int                # 1
    eval_name: str              # new-feature-simple
    assertion_idx: int | None   # 具体 assertion 索引，None 表示 eval 级别
    note: str                   # 反馈内容
    author: str                 # 反馈者
    note_type: str              # observation | fix_suggestion | assertion_issue | skip_reason
    resolved: bool              # 是否已处理
    resolved_by: str | None     # 处理方式：commit hash / "assertion_updated" / "wontfix"
```

**note_type 四种类型**：

| 类型 | 含义 | 示例 |
|------|------|------|
| `observation` | 观察到的行为问题 | "Gate 1 检查缺少技术债务观察" |
| `fix_suggestion` | 具体修复建议 | "dev-procedures-gate.md 第 15 行应增加 debt 检查步骤" |
| `assertion_issue` | assertion 本身有问题 | "S 复杂度场景不需要 intent checkpoint，应标记 N/A" |
| `skip_reason` | 本次跳过评审的原因 | "功能尚未实现，待 Phase 4" |

##### 3.9.2 存储格式 (notes.jsonl)

一行一条，追加写入，不覆盖。Git 友好（合并无冲突）。

```jsonl
{"timestamp":"2026-03-22T14:30:00Z","skill":"pace-dev","eval_id":1,"eval_name":"new-feature-simple","assertion_idx":2,"note":"S 场景不需要 intent checkpoint","author":"jinhuasu","note_type":"assertion_issue","resolved":false,"resolved_by":null}
{"timestamp":"2026-03-22T14:35:00Z","skill":"pace-dev","eval_id":7,"eval_name":"gate1-reflection","assertion_idx":null,"note":"Gate 1 缺少技术债务观察，需要在 dev-procedures-gate.md 补充","author":"jinhuasu","note_type":"fix_suggestion","resolved":false,"resolved_by":null}
```

##### 3.9.3 反馈消费路径

反馈不只是记录，更需要闭环——记录了问题就要追踪到解决。

```
notes.jsonl 写入
      │
      ├──► [自动] make eval-notes-report → 未解决反馈汇总
      │      → 按 Skill 分组、按类型排序、高亮未解决项
      │
      ├──► [自动] make eval-notes-stale → 检测过期反馈
      │      → 反馈关联的 assertion 已变更但 resolved 仍为 false
      │
      ├──► [手动] 开发者修改 procedures/assertions
      │      → git commit
      │      → make eval-note-resolve SKILL=pace-dev ID=1 BY=<commit-hash>
      │
      └──► [自动] analyzer.py 消费 notes
             → assertion_issue 类型的反馈 → 纳入区分度分析的上下文
             → fix_suggestion 类型的反馈 → 在报告中关联到对应 assertion
```

##### 3.9.4 反馈收集方式（三通道）

| 通道 | 使用场景 | 命令 |
|------|---------|------|
| **Viewer UI** | 浏览结果时随手记录 | 浏览器中点击 [+note] |
| **CLI** | 快速记录，不需要打开浏览器 | `make eval-note S=pace-dev CASE=7 NOTE="..."` |
| **批量导入** | 从 review 会议记录导入 | `python3 -m eval feedback import notes.txt` |

**CLI 快捷方式**：

```bash
# 逐条添加
make eval-note S=pace-dev CASE=7 NOTE="Gate 1 缺少技术债务观察" TYPE=fix_suggestion

# 标记已解决
make eval-note-resolve S=pace-dev CASE=7 IDX=2 BY=abc1234

# 查看未解决反馈
make eval-notes-pending

# 查看某个 Skill 的所有反馈
make eval-notes S=pace-dev
```

#### 3.10 CLI 扩展汇总

```bash
# ---- Phase 2 新增 ----

# 基线对照
make eval-benchmark S=pace-dev RUNS=3

# 静态报告（CI 用）
make eval-report                    # 生成 dashboard.html
make eval-report-open               # 生成并打开浏览器

# 交互式 viewer（开发者迭代用）
make eval-viewer S=pace-dev         # 启动 viewer server (localhost:8420)
make eval-viewer S=pace-dev PREV=1  # 启动并对比上一轮迭代

# 人工反馈
make eval-note S=pace-dev CASE=7 NOTE="..." TYPE=observation
make eval-note-resolve S=pace-dev CASE=7 IDX=2 BY=abc1234
make eval-notes-pending             # 未解决反馈汇总
make eval-notes S=pace-dev          # 某 Skill 全部反馈
make eval-notes-stale               # 过期反馈检测
```

---

### Phase 3: 评估质量保障

**目标**：让评估体系自身可验证——检测无效断言、发现覆盖盲区。

#### 3.11 Assertion 区分度分析 (`analyzer.py`)

灵感来自 skill-creator 的 "Analyst Pass"，但深化为系统化检测：

```python
def analyze_assertion_quality(
    behavior_results: list[dict],  # 多次运行的 grading.json
    benchmark_results: dict | None,
) -> AnalysisReport:
    """分析 assertions 的质量，识别需要改进的断言。"""
```

**检测维度**：

| 检测项 | 定义 | 行动 |
|--------|------|------|
| 非区分性断言 | with/without 都 100% pass | 标记为"不测 Skill 价值，仅测基础能力" |
| 永远失败断言 | 多次运行 0% pass | 可能是 assertion 写法有问题，或功能未实现 |
| 高方差断言 | 同条件下 pass 率在 30-70% 之间 | 可能 flaky，需要更精确的判定条件 |
| 无覆盖能力 | 某关键行为无任何 assertion | 从 transcript 中提取未覆盖的行为模式 |
| 冗余断言 | 两条 assertion 在所有运行中完全同步 pass/fail | 合并或删除一条 |

这是 skill-creator 的 grader "Step 6: Critique the Evals" 的系统化版本。skill-creator 靠 LLM 临场判断，devpace 基于多次运行的统计数据。

#### 3.12 盲比较（可选）(`comparator.py`)

仅在重大变更时使用（如 procedures 大改、Schema 重构）：

```python
async def blind_compare(
    skill_name: str,
    eval_case: dict,
    version_a_path: Path,  # 旧版 Skill
    version_b_path: Path,  # 新版 Skill
    fixture_dir: Path,
) -> ComparisonResult:
    """两个版本的 Skill 在同一场景下执行，匿名评分。"""
```

**设计决策**：不作为常规 CI 流程，仅通过显式命令触发：

```bash
make eval-compare S=pace-dev OLD=HEAD~5 NEW=HEAD
```

---

## 4 三层成本梯度

devpace 评估体系的独特优势——不同场景使用不同成本策略：

| 层级 | 场景 | API 调用 | 成本 | 命令 |
|------|------|---------|------|------|
| **Tier 0** | PR 自动回归 | 零 | $0 | `make eval-regress-offline` |
| **Tier 1** | 变更后触发检查 | 低（smoke 5 条 × 1 轮） | ~$0.10 | `make eval-trigger-smoke` |
| **Tier 2** | 行为 eval | 中（G1/G2 零成本 + G3 Haiku） | ~$0.50/Skill | `make eval-behavior-smoke` |
| **Tier 3** | 深度验证 | 高（全量触发 + 行为 + 基线对照） | ~$5/Skill | `make eval-deep S=pace-dev` |
| **Tier 4** | 发布前全量 | 最高（19 Skill × Tier 3） | ~$95 | `make eval-all-deep` |

skill-creator 没有成本分级概念——每次评估都是全量 subagent 运行。

---

## 5 CI 集成方案

### 5.1 PR 自动触发

```yaml
# .github/workflows/eval.yml
on:
  pull_request:
    paths: ['skills/**', 'knowledge/_schema/**', 'hooks/**', 'rules/**']

jobs:
  eval-offline:
    # Tier 0: 零成本
    runs-on: ubuntu-latest
    steps:
      - run: make eval-regress-offline
      - run: pytest tests/static/ -v

  eval-trigger-smoke:
    # Tier 1: 变更 Skill 的冒烟触发检查
    if: contains(github.event.pull_request.changed_files, 'skills/')
    runs-on: ubuntu-latest
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    steps:
      - run: make eval-trigger-changed RUNS=1

  eval-behavior-smoke:
    # Tier 2: 核心 Skill 行为冒烟（仅程序化评分）
    if: contains(github.event.pull_request.changed_files, 'skills/')
    runs-on: ubuntu-latest
    steps:
      - run: make eval-behavior-smoke-g1  # 仅 G1/G2，零 API 成本
```

### 5.2 手动深度触发

```yaml
  eval-deep:
    # Tier 3: 手动触发
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    steps:
      - run: make eval-deep S=${{ inputs.skill }}
      - run: make eval-report
      - uses: actions/upload-artifact@v4
        with:
          name: eval-dashboard
          path: tests/evaluation/_results/dashboard.html
```

---

## 6 与 skill-creator 的最终对比

实施完成后的能力对比：

| 能力维度 | devpace eval/ (优化后) | skill-creator | 胜出方 |
|---------|----------------------|---------------|--------|
| 触发精度评估 | Agent SDK + Wilson CI + 19-Skill 竞争 | `claude -p` + 临时 command | devpace |
| 触发统计严谨性 | Wilson 置信区间 + 多次运行 | 纯触发率 | devpace |
| Description 优化 | API + extended thinking + train/test | CLI + train/test | 持平 |
| 行为评估执行 | Agent SDK + env fixture + plugin 加载 | subagent + 无 fixture | devpace |
| 行为评分 | 混合三级（G1 程序化 + G2 正则 + G3 LLM） | 全 LLM grader | devpace（成本效率） |
| 共享断言复用 | SA-01~SA-06 跨 Skill 复用 | 无 | devpace |
| 基线对照 | with_plugin vs without_plugin | with_skill vs without_skill | 持平 |
| 盲比较 | 按需触发 | 完整 comparator + analyzer | skill-creator（更成熟） |
| 回归检测 | 4 维阈值 + sibling 联动 + 离线 | 无正式回归框架 | devpace |
| 评估质量分析 | 统计化区分度检测（多次运行数据） | LLM 临场判断 | devpace |
| 可视化（静态） | 单文件 HTML 仪表盘 + CI artifact | 无独立静态报告 | devpace |
| 可视化（交互） | viewer server + 逐 assertion 级导航 + transcript Tab | 双 Tab viewer + case 级导航 | devpace（更细粒度） |
| 人工反馈 | 结构化 notes.jsonl + 4 种类型 + 解决追踪 + 三通道收集 | feedback.json（全局文本框，无追踪） | devpace |
| CI 集成 | 5 级自动管线（Tier 0-4） | 无 | devpace |
| 成本控制 | 三层梯度（$0 ~ $95） | 无分级（每次全量） | devpace |
| 多 Skill 协同 | 19 Skill 竞争 + 交叉污染检测 | 单 Skill 隔离 | devpace |
| 覆盖度跟踪 | acceptance-matrix + eval-coverage | 无 | devpace |

**量化目标**：

| 指标 | 当前 | Phase 1 后 | Phase 2 后 | Phase 3 后 |
|------|------|-----------|-----------|-----------|
| 可自动评分的 assertion 类型 | 0/4 | 3/4 (G1+G2+G3) | 4/4 | 4/4 |
| 行为 eval 可执行 Skill 数 | 0/19 | 1 (pace-dev) | 3 (core) | 5+ |
| CI 自动覆盖层级 | Tier 0-1 | Tier 0-2 | Tier 0-3 | Tier 0-4 |
| 评估成本/轮（全量） | $2 (仅触发) | $5 | $15 | $95 |
| 评估报告形式 | CLI 文本 | CLI + JSON | 静态 HTML + 交互 viewer | HTML + viewer + CI badge |
| 人工反馈通道 | 无 | 无 | CLI + viewer + 批量导入 | 三通道 + 解决追踪 + 过期检测 |

---

## 7 实施排期

| Phase | 内容 | 前置依赖 | 产出 |
|-------|------|---------|------|
| **P1a** | env fixture 系统 (`setup-fixtures.sh`) | 无 | 5 个 fixture 目录 |
| **P1b** | behavior.py 执行引擎 | P1a | `make eval-behavior-one` 可用 |
| **P1c** | grader.py 混合评分 (G1+G2) | P1b | 程序化评分覆盖 60% assertions |
| **P1d** | grader.py G3 LLM 评分 | P1c + API Key | 100% assertions 可评分 |
| **P1e** | CLI + Makefile 集成 | P1b~d | `make eval-behavior` 全流程 |
| **P2a** | benchmark.py with/without 对照 | P1b | `make eval-benchmark` 可用 |
| **P2b** | report.py 静态 HTML 仪表盘 | P1e + P2a | `make eval-report-open` 可用 |
| **P2c** | viewer.py 交互式 eval server | P2b | `make eval-viewer` 可用 |
| **P2d** | feedback.py 反馈收集 + notes.jsonl | P2c | viewer 内反馈 + `make eval-note` CLI |
| **P2e** | 反馈消费路径（pending/stale/resolve） | P2d | `make eval-notes-pending` 可用 |
| **P2f** | CI 集成扩展 | P2b | PR 自动运行 Tier 0-2 |
| **P3a** | analyzer.py 区分度分析（消费 notes） | P2a + P2e（需要多次运行数据 + 人工反馈） | 断言质量报告 |
| **P3b** | comparator.py 盲比较 | P1b | `make eval-compare` 可用 |

---

## 8 风险与缓解

| 风险 | 影响 | 概率 | 缓解 |
|------|------|------|------|
| 行为 eval 耗时过长（>5min/case） | Phase 1 实用性下降 | 中 | smoke 模式 + timeout 控制 + G1/G2 优先 |
| Agent SDK 在 fixture 环境中行为不稳定 | Phase 1 可靠性 | 中 | 多次运行取多数决 + 超时 fallback |
| G3 LLM 评分与人工判断不一致 | 评分可信度 | 低 | 定期人工校准（抽样 10% 对照）；人工反馈通道补充修正 |
| fixture 维护成本随 Schema 演进增加 | 长期可维护性 | 中 | 脚本化生成 + Schema 变更时自动检测 fixture 过期 |
| with/without 对照中裸 Claude 表现波动大 | benchmark 噪声 | 高 | 增加 runs_per_case + 报告 stddev |
| viewer server 端口冲突或权限问题 | Phase 2 开发者体验 | 低 | 可配置端口 + fallback 到静态 HTML |
| notes.jsonl 反馈累积后噪声增大 | Phase 2 反馈价值衰减 | 中 | resolved 标记 + stale 过期检测 + 定期归档 |
| 反馈收集但无人消费（write-only） | 反馈闭环断裂 | 中 | `eval-notes-pending` 纳入 `validate-all.sh` 提醒；Phase 3 analyzer 自动消费 |

---

## 9 不做什么

以下能力**明确排除**，避免过度工程：

1. **不做 Skill 打包 (.skill 文件)**：devpace 是 local plugin，不需要打包分发格式。
2. **不集成 DeepEval/Promptfoo 等第三方 eval 框架**：这些框架的执行模型（prompt → response）与 devpace 的评估模型（prompt → multi-turn agent → state mutation）根本不匹配。devpace 需要的是"Agent 行为评估框架"，目前业界没有现成的开源方案适配此模式。
3. **不做 LLM 自动消费反馈生成 Skill 修改**：人工反馈（notes.jsonl）的消费者是开发者，不自动修改 procedures。原因：procedures 修改涉及设计决策（如"S 场景是否需要 intent checkpoint"），这类判断需要人的上下文和意图，不宜自动化。
4. **不做跨项目 eval 数据聚合**：viewer 和反馈机制面向单项目（devpace 自身），不设计多项目聚合仪表盘。

### 已采纳但设边界的能力

| 能力 | 采纳范围 | 明确边界 |
|------|---------|---------|
| 交互式 viewer server | Python 标准库 `http.server` 实现 | 不引入 Flask/FastAPI/前端构建链——零依赖是硬约束 |
| 人工反馈循环 | 结构化 notes.jsonl + 三通道收集 + 解决追踪 | 不做 skill-creator 式的"LLM 读 feedback 自动改 Skill"——反馈消费者是人，不是 LLM |
