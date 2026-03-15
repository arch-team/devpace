# devpace Eval Toolkit

Skill 触发评估、description 自动优化、回归检测的完整工具链。

## 架构

```
eval/
├── __init__.py      # 包入口 (v0.2.0)
├── __main__.py      # python3 -m eval 入口
├── cli.py           # 统一 CLI：trigger / loop / regress / baseline / changed
├── skill_io.py      # SKILL.md frontmatter 读写
├── results.py       # 评估结果持久化 + 元数据
├── trigger.py       # Agent SDK 触发检测（核心引擎）
├── improve.py       # Anthropic API description 生成
├── loop.py          # 优化循环 + train/test 分割
├── regress.py       # 多维回归检测 + 变更发现
├── baseline.py      # 基线管理
├── apply.py         # description diff/apply（独立脚本）
├── _gate_sdk.py     # 快速门禁检查（独立脚本）
├── eval-runner.sh   # 行为 eval 路由（skill-creator）
└── README.md        # 本文件
```

## 安装

```bash
# 在 devpace 根目录
make setup
# 等价于: pip install -r requirements-dev.txt
```

依赖：

| 包 | 用途 | 条件 |
|----|------|------|
| `claude-agent-sdk` | 触发检测 | Python >= 3.10 |
| `anthropic` | description 优化 | Python >= 3.10，需 API Key |
| `pytest` | 单元测试 | 开发环境 |

## 快速开始

```bash
# 查看所有命令
python3 -m eval --help

# 对 pace-dev 运行触发评估
make eval-trigger-one S=pace-dev

# 查看评估覆盖率
make eval-coverage
```

## 命令参考

### 触发评估

检测 Claude 是否在给定查询下正确触发目标 Skill。

```bash
# 单 Skill（默认 runs=3, timeout=90s, max_turns=5）
make eval-trigger-one S=pace-dev

# 自定义参数
make eval-trigger-one S=pace-dev RUNS=5 TIMEOUT=120 MAX_TURNS=8

# 指定模型
make eval-trigger-one S=pace-dev MODEL=claude-sonnet-4-20250514

# 冒烟测试（runs=1, 取 5 条关键查询，适合快速验证）
make eval-trigger-smoke

# 深度测试（runs=5, 全量查询，适合发布前验证）
make eval-trigger-deep

# 全量（所有有 trigger-evals.json 的 Skill）
make eval-trigger

# 仅变更的 Skill（基于 git diff，适合 PR 验证）
make eval-trigger-changed
```

**直接调用 CLI：**

```bash
python3 -m eval trigger --skill pace-dev --runs 3 --timeout 90 --max-turns 5
python3 -m eval trigger --skill pace-dev --smoke --smoke-n 5
```

**输出**：结果保存在 `tests/evaluation/<skill>/results/latest.json`。

### Description 优化

自动生成更优的 SKILL.md description 以提升触发准确率。

**前提**：设置 `ANTHROPIC_API_KEY` 环境变量。

```bash
export ANTHROPIC_API_KEY=sk-ant-...

# 运行优化循环（默认 5 轮迭代）
make eval-fix S=pace-dev MODEL=claude-sonnet-4-20250514

# 指定迭代次数
make eval-fix S=pace-dev MODEL=claude-sonnet-4-20250514 N=10

# 查看优化结果 vs 当前 description
make eval-fix-diff S=pace-dev

# 应用最优 description 到 SKILL.md
make eval-fix-apply S=pace-dev
```

**工作原理**：
1. 将 eval 查询分为 train (70%) 和 test (30%) 两组
2. 每轮迭代：用 Anthropic API (extended thinking) 生成候选 description
3. 在 train set 上评估候选 → 保留更优的
4. 最终在 test set 上验证，检测过拟合（train-test gap > 20% 告警）

**输出**：结果保存在 `tests/evaluation/<skill>/results/loop/`。

### 回归检测

对比 baseline 和 latest 结果，检测多维度回归。

```bash
# 保存当前结果为基线
make eval-baseline-save S=pace-dev

# 离线回归检查（零 API 调用，纯 JSON diff）
make eval-regress-offline

# 全量回归（重新运行 eval + 多维对比）
make eval-regress

# 对比单个 Skill 的 baseline vs latest
make eval-baseline-diff S=pace-dev

# 批量保存所有基线
make eval-baseline-save-all
```

**回归指标与阈值**：

| 指标 | WARNING | FAILURE |
|------|---------|---------|
| 正面触发率下降 | > 10% | > 20% |
| 假正面增加 | >= 1 | >= 1 |
| 假负面增加 | >= 2 | >= 4 |
| 总体通过率下降 | > 5% | > 15% |

**输出**：报告保存在 `tests/evaluation/regress/latest-report.json`。

### 辅助命令

```bash
# 覆盖率报告
make eval-coverage

# 过期检测（Skill 变更后 eval 未更新）
make eval-stale

# 一键全量（trigger + behavior + coverage + stale）
make eval-all

# 检测哪些 Skill 有 git 变更
python3 -m eval changed --base origin/main
```

## 端到端工作流

### 场景 1：新 Skill 建立评估基线

```bash
# 1. 确认 trigger-evals.json 存在
ls tests/evaluation/pace-xxx/trigger-evals.json

# 2. 首次评估
make eval-trigger-one S=pace-xxx

# 3. 保存为基线
make eval-baseline-save S=pace-xxx
```

### 场景 2：优化低触发率 Skill

```bash
# 1. 评估当前状态
make eval-trigger-one S=pace-dev RUNS=5

# 2. 运行优化循环
export ANTHROPIC_API_KEY=sk-ant-...
make eval-fix S=pace-dev MODEL=claude-sonnet-4-20250514 N=5

# 3. 查看差异
make eval-fix-diff S=pace-dev

# 4. 应用改进
make eval-fix-apply S=pace-dev

# 5. 验证改进
make eval-trigger-one S=pace-dev RUNS=5

# 6. 确认无回归后更新基线
make eval-baseline-save S=pace-dev
```

### 场景 3：PR 提交前验证

```bash
# 快速检查变更的 Skill 是否回归
make eval-trigger-changed
make eval-regress-offline
```

## CI 集成

### 自动触发（PR）

修改 `skills/` 下的文件时，CI 自动运行离线回归检查：
- Job: `eval-regress` — 对比 committed baseline.json vs latest.json
- 零 API 调用，无成本
- 失败时在 PR 上标注 `::error`

### 手动触发（workflow_dispatch）

在 GitHub Actions 页面手动触发 live eval：
1. 进入 Actions → Validate → Run workflow
2. 填写 `eval_skill`（Skill 名称或 `all`）和 `eval_runs`
3. 需要 `ANTHROPIC_API_KEY` 作为 Repository Secret

## 数据目录结构

```
tests/evaluation/
├── pace-dev/
│   ├── trigger-evals.json      # 触发评估查询集（手动维护）
│   ├── evals.json              # 行为评估用例（手动维护）
│   └── results/
│       ├── latest.json         # 最近一次评估结果
│       ├── baseline.json       # 基线快照
│       ├── history/            # 按时间戳归档的历史结果
│       │   └── 2026-03-15T14-30.json
│       └── loop/
│           ├── results.json    # 优化循环结果
│           └── best-description.txt
├── pace-change/
│   └── ...
└── regress/
    └── latest-report.json      # 回归检测报告
```

### trigger-evals.json 格式

```json
[
  {"query": "帮我开始做用户认证功能", "should_trigger": true},
  {"query": "帮我实现登录页面", "should_trigger": true},
  {"query": "今天天气怎么样", "should_trigger": false},
  {"query": "查看项目进度", "should_trigger": false}
]
```

### latest.json 关键字段

```json
{
  "skill": "pace-dev",
  "timestamp": "2026-03-15T14:30:00+00:00",
  "description_hash": "a1b2c3d4e5f67890",
  "summary": {"total": 35, "passed": 28, "failed": 7},
  "positive": {"total": 20, "passed": 16, "failed": 4},
  "negative": {"total": 15, "passed": 12, "failed": 3},
  "false_negatives": [{"id": 3, "query": "..."}],
  "false_positives": [{"id": 7, "query": "..."}],
  "metadata": {
    "model": "claude-sonnet-4-20250514",
    "sdk_options": {"max_turns": 5, "timeout": 90},
    "environment": {"python": "3.13", "sdk": "0.1.44"},
    "duration_seconds": 245.3
  }
}
```

## 参数速查

| 参数 | Make 变量 | CLI 参数 | 默认值 | 说明 |
|------|-----------|----------|--------|------|
| 运行次数 | `RUNS` | `--runs` | 3 | 每条查询重复运行次数 |
| 超时 | `TIMEOUT` | `--timeout` | 90s | 单次查询超时 |
| 最大轮次 | `MAX_TURNS` | `--max-turns` | 5 | Agent SDK 最大对话轮次 |
| 冒烟数量 | `SMOKE_N` | `--smoke-n` | 5 | 冒烟测试查询数量 |
| 模型 | `MODEL` | `--model` | (默认) | 指定 Claude 模型 ID |
| 测试集比例 | — | `--holdout` | 0.3 | loop 中 test set 占比 |
| 随机种子 | — | `--seed` | 42 | train/test 分割种子 |

## 故障排除

**Q: 触发率为 0%**
- 确认 `claude-agent-sdk` 已安装且版本 >= 0.1.44
- 确认不在 Claude Code 嵌套会话中运行（CLAUDECODE 环境变量会自动清除）
- 尝试增加 `MAX_TURNS=8`

**Q: `make eval-fix` 报错 ANTHROPIC_API_KEY**
- 设置环境变量：`export ANTHROPIC_API_KEY=sk-ant-...`
- 或配置 AWS Bedrock（设置 `AWS_REGION`，无需 API Key）

**Q: 回归检测无输出**
- 确认已运行过 `eval-baseline-save` 保存基线
- 确认 `tests/evaluation/<skill>/results/` 下同时有 `baseline.json` 和 `latest.json`

**Q: CI eval-regress 未触发**
- 仅在 PR 且 `skills/` 有变更时触发
- Push 到 main 不触发此 job
