# devpace Eval Toolkit (v0.3.0)

Skill 触发评估、行为评估、description 优化、回归检测、可视化仪表盘、人工反馈闭环的完整工具链。

## 架构

```
六层评估栈：
  Layer 6: Viewer         交互式 eval server + 人工反馈
  Layer 5: Report         静态 HTML 仪表盘
  Layer 4: Regression     多维回归 + sibling 联动
  Layer 3: Behavioral     行为执行 → 评分 → 基线对照
  Layer 2: Trigger        触发精度 + description 优化
  Layer 1: Static         pytest 结构检查
```

```
eval/
├── core/                    # 共享基础设施
│   ├── skill_io.py          #   SKILL.md frontmatter 读写
│   ├── results.py           #   结果持久化、路径常量、元数据
│   └── llm_client.py        #   Anthropic API 客户端 (直连/Bedrock 自动适配)
├── trigger/                 # 触发精度评估 + description 优化
│   ├── detect.py            #   Agent SDK 触发检测引擎
│   ├── eval_hooks.py        #   eval 专用 hooks (slash 路由 + forced eval)
│   ├── improve.py           #   Anthropic API description 生成
│   ├── loop.py              #   优化循环 + train/test split
│   └── apply.py             #   description diff/apply
├── behavior/                # 行为评估
│   ├── execute.py           #   env fixture + Agent SDK 行为执行
│   ├── grader.py            #   混合三级评分 (G1/G2/G3)
│   ├── _grader_checks.py    #   G1/G2 具名检查函数注册表
│   ├── benchmark.py         #   with/without 基线对照
│   └── comparator.py        #   盲 A/B 比较
├── regression/              # 回归检测 + 基线管理
│   ├── detect.py            #   多维回归检测 + sibling 联动
│   └── baseline.py          #   基线 save/diff
├── review/                  # 人工审查 + 可视化
│   ├── report.py            #   静态 HTML 仪表盘
│   ├── viewer.py            #   交互式 eval viewer server
│   ├── feedback.py          #   结构化反馈 notes.jsonl
│   └── analyzer.py          #   断言区分度分析
├── cli.py                   # 统一 CLI（13 个子命令）
├── shim.py                  # 向后兼容层
├── _gate_sdk.py             # 快速门禁检查
└── eval-runner.sh           # 行为 eval shell 路由
```

**依赖方向**：`core/` ← `trigger/`/`behavior/`/`regression/` ← `review/` ← `cli.py`

## 安装

```bash
make setup
# 等价于: pip install -r requirements-dev.txt
```

| 包 | 用途 | 条件 |
|----|------|------|
| `claude-agent-sdk` | 触发 + 行为检测 | Python >= 3.10 |
| `anthropic` | description 优化 + G3 评分 | 需 API Key 或 AWS Bedrock |
| `pytest` | 单元测试 | 开发环境 |

## 快速开始

```bash
python3 -m eval --help          # 查看全部 13 个命令

# 触发评估
make eval-trigger-one S=pace-dev

# 行为评估
make eval-behavior S=pace-dev

# 可视化
make eval-report-open           # 静态仪表盘
make eval-viewer S=pace-dev     # 交互式 viewer

# 深度验证（触发 + 行为 + 基线对照 + 报告）
make eval-deep S=pace-dev
```

## 成本梯度

不同场景使用不同成本策略——从零成本到全量深度：

| Tier | 场景 | API 成本 | 命令 |
|:----:|------|:--------:|------|
| **0** | PR 离线回归 | $0 | `make eval-regress-offline` |
| **1** | 变更后冒烟 | ~$0.10 | `make eval-trigger-smoke` |
| **2** | 行为冒烟 | ~$0.50 | `make eval-behavior-smoke S=pace-dev` |
| **3** | 单 Skill 深度 | ~$5 | `make eval-deep S=pace-dev` |
| **4** | 全量深度 | ~$95 | `make eval-all-deep` |

**原则**：日常开发用 Tier 0-1，改 Skill 后用 Tier 2，发布前用 Tier 3-4。

## 使用场景

### 场景 A：改了 Skill 后快速验证

```bash
# Tier 0: 零成本静态检查（秒级）
pytest tests/static/ -v

# Tier 1: 变更 Skill 的触发冒烟（~1 分钟）
make eval-trigger-changed RUNS=1

# Tier 0: 离线回归（有 baseline 时）
make eval-regress-offline
```

### 场景 B：新 Skill 建立评估基线

```bash
# 1. 确认 eval 文件存在
ls tests/evaluation/pace-xxx/trigger-evals.json

# 2. 首次触发评估
make eval-trigger-one S=pace-xxx

# 3. 保存为基线
make eval-baseline-save S=pace-xxx
```

### 场景 C：触发率低，优化 description

```bash
# 1. 评估当前状态
make eval-trigger-one S=pace-dev RUNS=3

# 2. 运行自动优化循环（需要 API Key 或 AWS Bedrock）
export ANTHROPIC_API_KEY=sk-ant-...
make eval-fix S=pace-dev MODEL=claude-sonnet-4-20250514

# 3. 查看差异
make eval-fix-diff S=pace-dev

# 4. 应用改进
make eval-fix-apply S=pace-dev

# 5. 验证改进
make eval-trigger-one S=pace-dev RUNS=3

# 6. 更新基线
make eval-baseline-save S=pace-dev
```

**工作原理**：
1. 将 eval 查询分为 train (70%) 和 test (30%) 两组
2. 每轮迭代：用 Anthropic API (extended thinking) 生成候选 description
3. 在 train set 上评估候选 → 保留更优的
4. 最终在 test set 上验证，检测过拟合（train-test gap > 20% 告警）

### 场景 D：行为评估（Skill 逻辑是否正确）

```bash
# 1. 生成 env fixtures（首次或 Schema 变更后）
bash tests/evaluation/_fixtures/setup-fixtures.sh

# 2. 单场景行为评估
make eval-behavior-one S=pace-dev CASE=1

# 3. 全量行为评估（15 场景）
make eval-behavior S=pace-dev

# 4. 冒烟（3 个代表性场景）
make eval-behavior-smoke S=pace-dev
```

**三级评分引擎**：

| 级别 | 评分方式 | 适用 assertion type | 成本 |
|------|---------|-------------------|------|
| G1 | 程序化检查 | `file_check`、`content_check` | 零 |
| G2 | 正则/结构匹配 | `output_check`（有明确格式） | 零 |
| G3 | LLM-as-judge | `behavior_check`、复杂 `output_check` | 低（Haiku） |

约 60-70% 的 assertions 通过 G1/G2 零成本评分，仅复杂行为判断走 G3。

### 场景 E：量化 devpace 的价值

```bash
# 对比"装了 devpace" vs "裸 Claude"的行为差异
make eval-benchmark S=pace-dev RUNS=3
```

输出 benchmark.json 含 mean ± stddev 统计：pass_rate、duration、tokens、按 G1/G2/G3 分级。

### 场景 F：端到端触发率验证（双轨模式）

devpace 提供两种触发评估模式，各有不同用途：

```bash
# 基准模式：纯 description 触发率（测 description 质量）
make eval-trigger-one S=pace-dev

# E2E 模式：含 slash 路由 + forced eval hook（测真实部署效果）
make eval-trigger-e2e S=pace-dev
```

**E2E 模式的三个机制**：

| 机制 | 实现 | 解决的问题 |
|------|------|-----------|
| slash 命令重写 | `/pace-dev args` → 自然语言 Skill 调用指令 | SDK 不解析 `/` 前缀 |
| system_prompt 注入 | 指示 Claude 先评估 skill 再用其他工具 | Claude 跳过 Skill 直接编码 |
| PreToolUse 拦截 | 首次非 Skill 工具调用时 block + 提醒 | 兜底保障 |

实测对比（pace-dev, 35 queries）：
```
description-only:  20/35 (57%)   ← 反映 description 自身触发能力
with-hooks e2e:    35/35 (100%)  ← 反映真实部署效果
```

两种模式互补——基准模式驱动 `make eval-fix` 优化，E2E 模式验证端到端可靠性。

### 场景 G：查看评估结果

```bash
# 静态仪表盘（CI artifact 友好，单文件 HTML）
make eval-report-open

# 交互式 viewer（开发者迭代用）
make eval-viewer S=pace-dev
# → 浏览器打开 localhost:8420
# → 5 个 Tab: Cases / Benchmark / Regression / Notes / Transcript
```

**Viewer 功能**：
- Cases Tab：逐 assertion 级导航，G1/G2/G3 着色，evidence 展示
- 每条 assertion 有 [+note] 按钮，反馈实时保存到 notes.jsonl
- 左右箭头键快速切换 case
- 自动检测 results/history/ 展示迭代对比

### 场景 H：记录和追踪评估反馈

```bash
# 三通道反馈收集

# 通道 1: CLI 快速记录
make eval-note S=pace-dev CASE=7 NOTE="Gate 1 缺少技术债务观察" TYPE=fix_suggestion

# 通道 2: Viewer UI（浏览器中点击 [+note]）

# 通道 3: 批量导入
python3 -m eval feedback import notes.txt
```

**反馈类型**：

| 类型 | 含义 | 示例 |
|------|------|------|
| `observation` | 观察到的行为问题 | "Gate 1 检查缺少技术债务观察" |
| `fix_suggestion` | 具体修复建议 | "dev-procedures-gate.md 第 15 行应增加 debt 检查步骤" |
| `assertion_issue` | assertion 本身有问题 | "S 场景不需要 intent checkpoint，应标记 N/A" |
| `skip_reason` | 本次跳过评审的原因 | "功能尚未实现，待 Phase 4" |

**反馈管理**：

```bash
make eval-notes-pending           # 查看未解决反馈
make eval-notes S=pace-dev        # 查看某 Skill 全部反馈
make eval-notes-stale             # 检测过期反馈（关联 assertion 已变更但未解决）
```

**反馈存储**：`tests/evaluation/_results/notes.jsonl`——一行一条，追加写入，Git 友好。

### 场景 I：Skill 大改后盲比较

```bash
# 两个版本的 Skill 在同一场景下执行，匿名评分
make eval-compare S=pace-dev OLD=HEAD~5 NEW=HEAD
```

6 维 rubric 评分：correctness / completeness / accuracy / organization / formatting / usability。

### 场景 J：断言质量分析

```bash
make eval-analyze S=pace-dev
```

检测 5 类问题：

| 检测项 | 定义 |
|--------|------|
| 非区分性断言 | with/without 都 100% pass（不测 Skill 价值） |
| 永远失败断言 | 多次运行 0% pass（assertion 或功能有问题） |
| 高方差断言 | 30-70% pass（可能 flaky） |
| 冗余断言 | 两条完全同步 pass/fail |
| 反馈标记 | 人工标记为 `assertion_issue` 的 |

### 场景 K：PR 提交前验证

```bash
# 快速检查（推荐写入 pre-push hook）
make eval-trigger-changed
make eval-regress-offline
```

### 场景 L：一键全量深度评估

```bash
# 单 Skill 深度（触发 + 行为 + 基线对照 + 报告）
make eval-deep S=pace-dev

# 所有 Skill 全量
make eval-all-deep

# 全量（触发 + 行为 + 覆盖率 + 报告）
make eval-all

# 覆盖率报告
make eval-coverage

# 过期 eval 检测
make eval-stale
```

## 数据文件格式

### trigger-evals.json

```json
[
  {"id": 1, "query": "帮我开始做用户认证功能", "should_trigger": true,
   "rationale": "'开始做' 在 description 触发词中"},
  {"id": 11, "query": "不做搜索功能了", "should_trigger": false,
   "rationale": "需求取消 → pace-change"}
]
```

### evals.json

```json
{
  "skill_name": "pace-dev",
  "evals": [
    {
      "id": 1, "name": "new-feature-simple",
      "prompt": "帮我实现一个返回当前时间的 API 接口",
      "env": "ENV-DEV-A",
      "assertions": [
        {"text": "New CR file created in .devpace/backlog/", "type": "file_check"},
        {"text": "CR type is 'feature'", "type": "content_check"},
        {"text": "Intent checkpoint performed", "type": "behavior_check"},
        {"text": "state.md updated", "type": "file_check", "shared_pattern": "SA-01"}
      ]
    }
  ]
}
```

**assertion type 决定评分级别**：
- `file_check` → G1 程序化
- `content_check` → G1/G2 程序化或正则
- `output_check` → G2 正则，G3 兜底
- `behavior_check` → G3 LLM 评分

**shared_pattern**（SA-01~SA-06）：引用 `_cross-cutting/shared-assertions.md` 中的共享断言模式，一处定义多处复用。

### latest.json（触发 eval 结果）

```json
{
  "skill": "pace-dev",
  "timestamp": "2026-03-22T14:28:21+00:00",
  "description_hash": "4d46fc722c5d",
  "summary": {"total": 35, "passed": 35, "failed": 0},
  "positive": {"total": 18, "passed": 18, "failed": 0},
  "negative": {"total": 17, "passed": 17, "failed": 0},
  "false_negatives": [],
  "false_positives": [],
  "metadata": {
    "model": null,
    "sdk_options": {"max_turns": 8, "timeout": 90},
    "duration_seconds": 245.3
  }
}
```

### grading.json（行为 eval 评分）

```json
{
  "skill": "pace-dev",
  "cases": [{
    "eval_id": 1, "eval_name": "new-feature-simple",
    "assertions": [
      {"text": "New CR file created...", "type": "file_check",
       "grade_level": "G1", "passed": true,
       "evidence": "Found .devpace/backlog/CR-004.md", "shared_pattern": null}
    ],
    "summary": {"total": 9, "passed": 8, "failed": 1,
      "by_grade": {"G1": {"total": 5, "passed": 5}, "G2": {"total": 1, "passed": 1}, "G3": {"total": 3, "passed": 2}}}
  }]
}
```

## 数据目录结构

```
tests/evaluation/
├── pace-dev/                         # 每个 Skill 一个目录
│   ├── trigger-evals.json            # 触发查询集（手动维护）
│   ├── evals.json                    # 行为场景 + assertions（手动维护）
│   └── results/                      # 自动生成
│       ├── latest.json               # 最近触发 eval 结果
│       ├── baseline.json             # 基线快照
│       ├── history/                  # 按时间戳归档
│       ├── loop/                     # description 优化结果
│       │   ├── results.json
│       │   └── best-description.txt
│       ├── grading/                  # 行为 eval 评分
│       │   └── grading.json
│       └── benchmark/                # with/without 对照
├── _fixtures/                        # 行为 eval 环境
│   ├── ENV-DEV-A ~ ENV-DEV-G/        # 预置项目状态（脚本生成，不入 git）
│   └── setup-fixtures.sh             # 幂等生成脚本
├── _results/                         # 全局报告
│   ├── dashboard.html                # 静态仪表盘
│   └── notes.jsonl                   # 人工反馈日志
├── _cross-cutting/                   # 跨 Skill 共享
│   ├── shared-assertions.md          # SA-01~SA-06 模式
│   ├── acceptance-matrix.md          # 需求→测试覆盖矩阵
│   └── ux-rubric.md                  # UX 原则评分表
└── regress/
    └── latest-report.json            # 回归检测报告
```

## CI 集成

`validate.yml` 中的 eval 相关 job：

| Job | 触发条件 | API 成本 | 作用 |
|-----|---------|:--------:|------|
| `eval-stale` | 每次 PR | $0 | 检测 Skill 变更后 eval 是否过期 |
| `eval-regress` | PR + skills/ 变更 | $0 | 离线回归 (baseline vs latest JSON diff) |
| `eval-trigger-smoke` | PR + skills/ 变更 | ~$0.10 | 变更 Skill 的触发冒烟 |
| `eval-behavior-smoke` | PR + skills/ 变更 | $0 (G1/G2) | 程序化行为评分 |
| `eval-deep` | 手动 workflow_dispatch | ~$5 | 全量深度评估 + HTML 报告 |
| `eval-live` | 手动 workflow_dispatch | ~$2 | 指定 Skill 触发评估 |

## 回归检测

```bash
make eval-regress-offline    # 零 API 调用，纯 JSON diff
make eval-regress            # 全量回归
```

| 指标 | WARNING | FAILURE |
|------|---------|---------|
| 正面触发率下降 | > 10% | > 20% |
| 假正面增加 | >= 1 | >= 1 |
| 假负面增加 | >= 2 | >= 4 |
| 总体通过率下降 | > 5% | > 15% |

**Sibling 联动检测**：修改 pace-dev 时自动检查 pace-change（触发词交叉风险）。

## 命令速查表

### 触发评估

| 命令 | 作用 |
|------|------|
| `make eval-trigger-one S=pace-dev` | 单 Skill 触发测试 |
| `make eval-trigger-one S=pace-dev RUNS=5` | 多次运行（统计稳定） |
| `make eval-trigger-e2e S=pace-dev` | 端到端（含 hooks） |
| `make eval-trigger-smoke` | 全量冒烟 |
| `make eval-trigger-deep` | 全量深度 (runs=5) |
| `make eval-trigger-changed` | 仅 git 变更的 Skill |

### Description 优化

| 命令 | 作用 |
|------|------|
| `make eval-fix S=pace-dev MODEL=<id>` | 自动优化循环 |
| `make eval-fix-diff S=pace-dev` | 查看优化前后差异 |
| `make eval-fix-apply S=pace-dev` | 应用最优 description |

### 行为评估

| 命令 | 作用 |
|------|------|
| `make eval-behavior-one S=pace-dev CASE=1` | 单场景 |
| `make eval-behavior S=pace-dev` | 全量 |
| `make eval-behavior-smoke S=pace-dev` | 冒烟（3 场景） |
| `make eval-benchmark S=pace-dev RUNS=3` | with/without 对照 |
| `make eval-compare S=pace-dev OLD=HEAD~5 NEW=HEAD` | 盲比较 |

### 回归与基线

| 命令 | 作用 |
|------|------|
| `make eval-regress-offline` | 离线回归（$0） |
| `make eval-regress` | 全量回归 |
| `make eval-baseline-save S=pace-dev` | 保存基线 |
| `make eval-baseline-diff S=pace-dev` | 对比基线 |
| `make eval-baseline-save-all` | 批量保存所有基线 |

### 可视化与反馈

| 命令 | 作用 |
|------|------|
| `make eval-report` | 生成静态 HTML 仪表盘 |
| `make eval-report-open` | 生成并打开浏览器 |
| `make eval-viewer S=pace-dev` | 交互式 viewer |
| `make eval-note S=... CASE=... NOTE="..."` | 记录反馈 |
| `make eval-notes-pending` | 未解决反馈 |
| `make eval-notes S=pace-dev` | Skill 全部反馈 |
| `make eval-notes-stale` | 过期反馈检测 |
| `make eval-analyze S=pace-dev` | 断言质量分析 |

### 复合

| 命令 | 作用 |
|------|------|
| `make eval-deep S=pace-dev` | trigger + behavior + benchmark + report |
| `make eval-all` | 全量 trigger + behavior + coverage + report |
| `make eval-all-deep` | 所有 Skill 全量深度 |
| `make eval-coverage` | 评估覆盖率报告 |
| `make eval-stale` | 过期 eval 检测 |

## 故障排除

**Q: 触发率为 0%**
- 确认 `claude-agent-sdk` 已安装且版本 >= 0.1.44
- 确认不在 Claude Code 嵌套会话中运行（CLAUDECODE 环境变量会自动清除）
- 尝试增加 `MAX_TURNS=8`

**Q: G3 评分报错 "model identifier is invalid"**
- 使用 AWS Bedrock 时，模型 ID 会自动适配（`us.anthropic.claude-haiku-4-5-20251001-v1:0`）
- 如需覆盖模型，传 `MODEL=<bedrock-model-id>` 参数

**Q: `make eval-fix` 报错 ANTHROPIC_API_KEY**
- 设置环境变量：`export ANTHROPIC_API_KEY=sk-ant-...`
- 或配置 AWS Bedrock（设置 `AWS_REGION`，无需 API Key）

**Q: 回归检测无输出**
- 确认已运行过 `eval-baseline-save` 保存基线
- 确认 `tests/evaluation/<skill>/results/` 下同时有 `baseline.json` 和 `latest.json`

**Q: 行为 eval 报错 "fixture not found"**
- 运行 `bash tests/evaluation/_fixtures/setup-fixtures.sh` 生成 fixtures
- Fixtures 不入 git（含嵌入 git repo），每次需脚本生成

**Q: with-hooks 模式触发率低于预期**
- 确认 `PreToolUse` hook 生效（`UserPromptSubmit` 在 SDK 中不触发）
- 增加 `MAX_TURNS=8`（hook block 会消耗额外轮次）
