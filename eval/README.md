# devpace Eval Toolkit

Skill 触发评估、行为评估、description 优化、回归检测、可视化仪表盘的完整工具链。

## 架构

```
eval/
├── core/                    # 共享基础设施
│   ├── skill_io.py          #   SKILL.md frontmatter 读写
│   └── results.py           #   结果持久化、路径常量、元数据
├── trigger/                 # 触发精度评估 + description 优化
│   ├── detect.py            #   Agent SDK 触发检测引擎
│   ├── improve.py           #   Anthropic API description 生成
│   ├── loop.py              #   优化循环 + train/test split
│   └── apply.py             #   description diff/apply
├── behavior/                # 行为评估
│   ├── execute.py           #   env fixture + Agent SDK 行为执行
│   ├── grader.py            #   混合三级评分 (G1/G2/G3)
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
| `anthropic` | description 优化 + G3 评分 | 需 API Key |
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

## 命令参考

### 触发评估 (trigger/)

```bash
make eval-trigger-one S=pace-dev          # 单 Skill
make eval-trigger-one S=pace-dev RUNS=5   # 多次运行
make eval-trigger-smoke                   # 冒烟（5 条查询）
make eval-trigger-deep                    # 深度（runs=5 全量）
make eval-trigger                         # 全量 Skill
make eval-trigger-changed                 # 仅 git 变更的 Skill
```

### Description 优化 (trigger/)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
make eval-fix S=pace-dev MODEL=claude-sonnet-4-20250514
make eval-fix-diff S=pace-dev             # 查看差异
make eval-fix-apply S=pace-dev            # 应用最优 description
```

### 行为评估 (behavior/)

```bash
make eval-behavior S=pace-dev             # 全量（15 场景）
make eval-behavior-one S=pace-dev CASE=1  # 单场景
make eval-behavior-smoke S=pace-dev       # 冒烟（3 场景）
```

三级评分：G1（程序化文件/内容检查）→ G2（正则/结构匹配）→ G3（LLM-as-judge）

### 基线对照 (behavior/)

```bash
make eval-benchmark S=pace-dev RUNS=3     # with/without plugin 对比
make eval-compare S=pace-dev OLD=HEAD~5 NEW=HEAD  # 盲 A/B 比较
```

### 回归检测 (regression/)

```bash
make eval-regress-offline                 # 零成本离线检查
make eval-regress                         # 全量回归
make eval-baseline-save S=pace-dev        # 保存基线
make eval-baseline-diff S=pace-dev        # 对比基线
```

| 指标 | WARNING | FAILURE |
|------|---------|---------|
| 正面触发率下降 | > 10% | > 20% |
| 假正面增加 | >= 1 | >= 1 |
| 假负面增加 | >= 2 | >= 4 |
| 总体通过率下降 | > 5% | > 15% |

### 可视化 (review/)

```bash
make eval-report                          # 生成静态 HTML 仪表盘
make eval-report-open                     # 生成并打开浏览器
make eval-viewer S=pace-dev               # 启动交互式 viewer (localhost:8420)
```

### 人工反馈 (review/)

```bash
make eval-note S=pace-dev CASE=7 NOTE="Gate 1 缺少技术债务观察"
make eval-notes S=pace-dev                # 某 Skill 全部反馈
make eval-notes-pending                   # 未解决反馈汇总
make eval-notes-stale                     # 过期反馈检测
```

反馈类型：`observation` | `fix_suggestion` | `assertion_issue` | `skip_reason`

### 质量分析 (review/)

```bash
make eval-analyze                         # 断言区分度分析
```

检测：非区分性断言、永远失败断言、高方差断言、冗余断言、反馈标记问题。

### 复合目标

```bash
make eval-deep S=pace-dev                 # trigger + behavior + benchmark + report
make eval-all                             # 全量触发 + 行为 + 覆盖率 + 报告
```

## 成本梯度

| Tier | 场景 | API 成本 | 命令 |
|------|------|---------|------|
| 0 | PR 离线回归 | $0 | `make eval-regress-offline` |
| 1 | 变更后冒烟 | ~$0.10 | `make eval-trigger-smoke` |
| 2 | 行为冒烟 | ~$0.50/Skill | `make eval-behavior-smoke` |
| 3 | 深度验证 | ~$5/Skill | `make eval-deep S=pace-dev` |

## 数据目录

```
tests/evaluation/
├── pace-dev/
│   ├── trigger-evals.json        # 触发查询集
│   ├── evals.json                # 行为场景 + assertions
│   └── results/
│       ├── latest.json           # 触发 eval 结果
│       ├── baseline.json         # 基线快照
│       ├── history/              # 历史归档
│       ├── loop/                 # description 优化
│       ├── grading/              # 行为 eval 评分
│       └── benchmark/            # with/without 对照
├── _fixtures/                    # 行为 eval 环境 fixture
│   ├── ENV-DEV-A ~ ENV-DEV-G/
│   └── setup-fixtures.sh
├── _results/
│   ├── dashboard.html            # 静态仪表盘
│   └── notes.jsonl               # 人工反馈
└── regress/
    └── latest-report.json
```
