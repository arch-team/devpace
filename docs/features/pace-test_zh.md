# 测试策略与质量管理（`/pace-test`）

devpace 的测试远不止"跑测试、看结果"。`/pace-test` 管理的是一条**需求驱动**的测试生命周期：Product Feature (PF) 的验收标准定义了需要验证什么，测试策略将标准映射到测试类型，覆盖分析衡量的是需求覆盖率（而非仅仅是代码覆盖率），AI 驱动的验收验证则为每条标准提供带代码级引用的证据。最终结果是一套每一步都可追溯到业务意图的测试流程。

## 前置条件

| 条件 | 用途 | 是否必须 |
|------|------|:--------:|
| `.devpace/` 已初始化 | 项目结构、PF 定义、CR 追踪 | 是 |
| `.devpace/rules/checks.md` | 为 `run` 和 `dryrun` 配置测试命令 | 推荐 |
| `.devpace/rules/test-strategy.md` | PF 到测试的映射（由 `strategy` 生成） | 推荐 |

> **优雅降级**：若未初始化 `.devpace/`，Skill 回退到纯代码模式（自动检测测试命令）。若缺少 `checks.md`，会从 `package.json`、`pyproject.toml`、`go.mod` 或 `Cargo.toml` 中自动检测常见测试命令。若缺少 `test-strategy.md`，需求级分析仍可通过直接读取 `project.md` 中的 PF 标准运作。

## 快速开始

```
1. /pace-test strategy              --> 将 PF 验收标准映射到测试类型
2. /pace-test generate PF-001 --full --> 基于标准生成测试用例
3. /pace-test coverage              --> 分析需求覆盖缺口
4. /pace-test                       --> 运行所有已配置的测试
5. /pace-test accept                --> AI 验收验证
6. /pace-test report                --> 生成可供评审的摘要报告
```

日常工作流：大多数会话只需 `/pace-test`（run）+ `/pace-test accept`。迭代期间使用 `impact --run` 可快速执行受影响的测试。

## 命令参考

### 执行层（Execution Layer）

#### `run`（默认，无参数）

执行所有已配置的测试命令并生成结构化报告。

**语法**：`/pace-test`

读取 `checks.md` 中的测试命令（回退到自动检测），按依赖顺序执行，生成按 Gate 分组的通过/失败报告。当测试失败时，分析最近的 `git diff` 推断可能的根因。配置了 `.devpace/integrations/config.md` 时会自动附加 CI 运行状态。详细步骤见 [test-procedures-core.md](../../skills/pace-test/test-procedures-core.md)。

**输出示例**：
```
| # | Check    | Gate   | Status | Time | Notes               |
|---|----------|--------|--------|------|---------------------|
| 1 | npm test | Gate 1 | PASS   | 3.2s | --                  |
| 2 | eslint . | Gate 1 | FAIL   | 1.1s | 3 errors in auth.ts |
Summary: 1/2 passed
Suggestion: run /pace-test dryrun 1 to pre-check Gate 1
```

#### `generate`

基于 PF 验收标准创建测试用例。

**语法**：`/pace-test generate [PF-title] [--full]`

默认（skeleton）模式生成带 `// TODO` 占位符的脚手架代码。`--full` 模式生成包含断言、边界条件和错误路径的完整实现（标记 `// REVIEW: AI-generated`）。自动注册到 `test-strategy.md`。在 TDD 上下文中会追加 Red-Green-Refactor 提醒。详细步骤见 [test-procedures-generate.md](../../skills/pace-test/test-procedures-generate.md)。

**输出示例**：
```
Generated 4 test cases [full] for PF "User Authentication" (4 criteria):
1. Users can log in --> test_login_email_password [3 assertions + 2 boundary]
2. Failed login error --> test_login_failure_message [2 assertions]
File: tests/test_auth.py | Mode: full (review REVIEW markers)
```

#### `dryrun`

模拟 Gate 检查，不触发状态转换。

**语法**：`/pace-test dryrun [1|2|4]`

以只读模式执行完整的 Gate 检查流程（命令检查、意图检查、Gate 2 的对抗性审查）。不产生 CR 状态变更，不写入事件日志。详细步骤见 [test-procedures-advanced.md](../../skills/pace-test/test-procedures-advanced.md)。

**输出示例**：
```
Gate 1 Dry-Run: 1 PASS / 1 FAIL
Prediction: Gate will FAIL
Fix: resolve eslint errors, then re-run /pace-test dryrun 1
```

### 策略层（Strategy Layer）

#### `strategy`

基于 PF 验收标准生成系统化测试策略。

**语法**：`/pace-test strategy`

针对每条验收标准，推荐一种主要测试类型（unit、integration、E2E、performance、security、accessibility、manual）和 0-2 种辅助类型。通过名称和内容分析匹配现有测试文件。输出测试金字塔健康评估和实施指引。持久化到 `.devpace/rules/test-strategy.md`。详细步骤见 [test-procedures-strategy-gen.md](../../skills/pace-test/test-procedures-strategy-gen.md)。

**输出示例**：
```
Strategy: 3 PFs, 12 criteria --> 5 unit / 3 integration / 2 E2E / 1 perf [+security] / 1 manual
Covered: 7 | To build: 5
Pyramid health: needs attention (unit 42%, below 50% threshold)
Next: /pace-test generate [PF] to create tests for uncovered criteria
```

#### `coverage`

分析有多少 PF 验收标准已有对应测试。

**语法**：`/pace-test coverage`

交叉比对 PF 标准与 `test-strategy.md`、`checks.md` 及扫描到的测试文件。可选地收集代码覆盖率作为补充信号（Jest、pytest、go test、cargo tarpaulin）。当 `test-strategy.md` 包含阈值配置时，检查数值是否达标。详细步骤见 [test-procedures-coverage.md](../../skills/pace-test/test-procedures-coverage.md)。

**输出示例**：
```
| PF     | Feature        | Criteria | Covered | Rate |
|--------|----------------|----------|---------|------|
| PF-001 | Authentication | 5        | 3       | 60%  |
| PF-002 | Data Import    | 3        | 0       | 0%   |
Requirements coverage: 3/8 (38%)
Code coverage (supplementary): 72% line, 58% branch (Jest)
```

#### `impact`

分析变更影响并推荐回归测试范围。

**语法**：`/pace-test impact [CR-ID] [--run]`

从 `git diff` 提取变更文件，构建文件到 PF 的反向映射，识别直接和间接受影响的 PF，并评定风险等级。使用 `--run` 时，在分析后自动执行"必须运行"的测试。详细步骤见 [test-procedures-impact.md](../../skills/pace-test/test-procedures-impact.md)。

**输出示例**：
```
CR-005 "Add CSV export" | Scope: 6 files / 2 modules | Risk: MEDIUM
| PF     | Feature     | Impact  | Suggested Tests       |
|--------|-------------|---------|------------------------|
| PF-002 | Data Import | Direct  | test_import, test_csv  |
| PF-003 | Reports     | Indirect| Spot-check recommended |
Must-run: test_import, test_csv
```

### 分析层（Analysis Layer）

#### `report`

生成面向评审或发布的可读测试摘要。

**语法**：`/pace-test report [CR-ID|REL-xxx]`

**CR 模式**（默认）：聚合 Layer 1（测试执行）、Layer 2（需求覆盖）、Layer 3（AI 验收验证），生成合并/拒绝建议。**Release 模式**（`REL-xxx`）：聚合发布内所有 CR，提供逐 CR 质量摘要和发布/延期建议。遵循"有什么报什么"原则——缺失的层级会注明，但不阻断报告生成。详细步骤见 [test-procedures-report.md](../../skills/pace-test/test-procedures-report.md)。

**输出示例**（CR 模式）：
```
CR-005 | L1: 8/8 passed | L2: 3/5 covered (60%) | L3: 4/5 passed, 1 manual
Recommendation: supplement tests before merge
```

#### `flaky`

检测不稳定测试和主动维护问题。

**语法**：`/pace-test flaky`

扫描 CR 事件历史中的间歇性故障、环境依赖故障、顺序依赖故障和超时波动。执行主动维护检测：空断言、时间膨胀、长期未更新的测试和被跳过的测试。持久化到 `insights.md`，并在 `test-strategy.md` 中降级不稳定测试。详细步骤见 [test-procedures-advanced.md](../../skills/pace-test/test-procedures-advanced.md)。

**输出示例**：
```
Unstable: e2e-login 2/5 (40%) intermittent [CR-003, CR-005]
Maintenance: test_utils::helper (empty assert) | lint (+217% bloat)
Priority: fix empty assertions first (false security)
```

#### `baseline`

建立或更新测试执行基线，用于趋势追踪。

**语法**：`/pace-test baseline`

运行完整测试套件，记录通过率和执行时间，与上一次基线对比。持久化到 `.devpace/rules/test-baseline.md`。由 `/pace-retro` 消费以用于度量分析。详细步骤见 [test-procedures-advanced.md](../../skills/pace-test/test-procedures-advanced.md)。

**输出示例**：
```
Baseline updated: pass rate 85%->92% (+7%) | exec 12.3s->10.1s (-2.2s) | checks 8->10 (+2)
```

### 验证层（Verification Layer）

#### `accept`

基于 PF 标准的 AI 驱动验收验证。

**语法**：`/pace-test accept [CR-ID]`

这是 devpace 测试的核心差异化能力。针对每条 PF 验收标准，Claude 选择一个验证级别——L1 动态验证（执行测试/CLI）、L2 静态语义验证（读取代码并提供行号引用）、L3 手动验证（生成人工检查清单）——并为每条标准生成证据。同时执行 Test Oracle Check：审查现有测试是否真正验证了其声称的内容，并在 `test-strategy.md` 中降级弱覆盖或虚假覆盖。详细步骤见 [test-procedures-verify.md](../../skills/pace-test/test-procedures-verify.md)。

**输出示例**：
```
CR-005 "Add CSV export" (PF: Data Import)
| # | Criterion                  | Status  | Level  | Evidence                        |
|---|----------------------------|---------|--------|---------------------------------|
| A1| CSV parses all columns     | PASS    | L1     | test_csv_parser passed          |
| A2| Error on malformed rows    | PASS    | L2     | src/parser.ts:45 validates rows |
| A3| Progress bar during upload | PARTIAL | L2     | Complex async, needs runtime    |
| A4| Accessibility              | MANUAL  | L3     | Checklist generated             |
Summary: 2 passed, 1 needs supplement, 1 needs manual check
```

**降级行为**：若无 PF 关联，回退到 CR 意图验收标准（在报告中注明）。若两者均缺失，退出并给出明确提示。

## 核心差异化：需求驱动的测试

传统工具衡量的是**代码覆盖率**（"多少百分比的代码行被执行了"）。devpace 衡量的是**需求覆盖率**（"多少百分比的 PF 验收标准有对应验证"）。一个项目可以拥有 95% 的代码覆盖率，却有 0% 的需求覆盖率。`/pace-test` 通过 strategy-generate-coverage-accept-report 管道弥合这一缺口——每一个测试都可追溯到一条 PF 验收标准。

## 使用场景

### 场景 1：新功能测试规划（TDD）

```
/pace-test strategy         --> PF-003: 6 criteria, 3 unit / 2 integration / 1 E2E
/pace-test generate PF-003 --full --> 6 test cases. TDD: run to confirm Red phase.
/pace-test coverage         --> PF-003 requirements: 6/6 (100%). Code: 0% (expected).
```

### 场景 2：合并前质量检查

```
/pace-test accept CR-005    --> 4/5 passed, 1 manual. Oracle: weak coverage found.
/pace-test report CR-005    --> 3-layer report. Recommendation: supplement, then merge.
```

### 场景 3：发布就绪评估

```
/pace-test report REL-001   --> 5 CRs, 3 PFs. Risk: LOW. Can ship.
```

## 与其他命令的集成

| 命令 | 集成点 |
|------|--------|
| `/pace-dev` | Gate 1/2 消费 `checks.md`（与 `run` 执行相同命令）。`accept` 报告作为 Gate 2 证据。 |
| `/pace-review` | Gate 2 消费 `accept` 验证报告作为结构化评审证据。 |
| `/pace-release` | `report REL-xxx` 生成发布级质量报告。`dryrun 4` 验证发布前检查。 |
| `/pace-retro` | `baseline` 为回顾提供度量数据。`flaky` 发现写入 `insights.md`。 |
| `/pace-change` | `impact` 使用 CR 变更范围确定回归测试建议。 |

## 向后兼容

| 旧名称 | 当前名称 | 说明 |
|--------|---------|------|
| `verify` | `accept` | AI 验收验证 |
| `regress` | `impact` | 变更影响分析 |
| `gen` | `generate` | 测试用例生成 |
| `gate` | `dryrun` | Gate 模拟 |

## 相关资源

- [User Guide -- /pace-test 章节](../user-guide.md)
- [SKILL.md](../../skills/pace-test/SKILL.md) -- 入口与路由表
- [test-procedures-core.md](../../skills/pace-test/test-procedures-core.md) -- Run、CI 集成
- [test-procedures-strategy-gen.md](../../skills/pace-test/test-procedures-strategy-gen.md) -- Strategy
- [test-procedures-coverage.md](../../skills/pace-test/test-procedures-coverage.md) -- Coverage
- [test-procedures-impact.md](../../skills/pace-test/test-procedures-impact.md) -- Impact
- [test-procedures-report.md](../../skills/pace-test/test-procedures-report.md) -- Reports
- [test-procedures-verify.md](../../skills/pace-test/test-procedures-verify.md) -- 验收验证
- [test-procedures-advanced.md](../../skills/pace-test/test-procedures-advanced.md) -- Flaky、dryrun、baseline
- [test-procedures-generate.md](../../skills/pace-test/test-procedures-generate.md) -- Generate
- [devpace-rules.md](../../rules/devpace-rules.md) -- 运行时行为规则
