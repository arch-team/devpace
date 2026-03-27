---
description: Use when user says "跑测试", "测试覆盖", "验证一下", "验收", "回归", "影响分析", "test", "verify", "accept", "coverage", "测试策略", /pace-test, or when test results, coverage gaps, or acceptance readiness are discussed. NOT for code implementation (use /pace-dev). NOT for code review or approval (use /pace-review).
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[accept|strategy|coverage|impact|report|generate|...] [目标]"
model: sonnet
context: fork
agent: pace-engineer
---

# /pace-test — BizDevOps 感知的测试策略与验证

基于业务上下文（BR→PF→CR 价值链），智能管理和执行测试验证——不只是"跑测试"，而是"基于需求验收标准，评估验证覆盖度和执行 AI 驱动的验收验证"。

## 与现有机制的关系

- `checks.md`：定义 Gate 1/2 要执行的**命令列表**（what to run）
- `/pace-test`：管理**测试策略**（what to test, why, how comprehensive）
- `/pace-dev` Gate 1/2：消费 checks.md 中的测试命令
- `/pace-review` Gate 2：可消费 `/pace-test accept` 的验收映射报告作为审查证据

### accept 的定位

Gate 2 仅二元判定整体一致性。accept 提供精细能力：逐条验收标准附证据、三级判定（✅/⚠️/❌）、测试预言审查断言实质性、弱覆盖自动降级策略。不做 accept 也能过 Gate 2，但做了的 CR 在 Gate 3 有更充分的证据支撑（详见 skills/pace-test/test-procedures-verify.md）。

## 输入

$ARGUMENTS：

**日常使用**（大多数场景只需这些）：
- （空）→ 对当前 CR 运行所有已配置的测试，输出结构化报告
- `accept [CR编号]` → AI 驱动的验收验证：逐条比对 PF 验收标准与实际行为
- `strategy` → 基于 PF 验收标准生成测试策略建议
- `coverage` → 分析当前测试对 PF 验收标准的覆盖度（需求覆盖率 + 代码覆盖率辅助信号）
- `impact [CR编号] [--run]` → 变更影响分析：基于变更范围推荐需要重跑的测试（`--run` 自动执行必跑测试）
- `report [CR编号|REL-xxx]` → 生成面向人类的测试摘要报告（支持 CR 级和 Release 级）

**深度功能**（按需使用）：
- `generate [PF标题] [--full]` → 基于 PF 验收标准生成测试用例（默认骨架，`--full` 生成完整实现）
- `flaky` → 分析历史测试结果，识别不稳定测试并建议修复/隔离
- `dryrun [1|2|4]` → 模拟执行指定 Gate 的完整检查流程（dry-run）
- `baseline` → 建立/更新测试基准线（供 /pace-retro 度量使用）

> **向后兼容**：旧名称 `verify`/`regress`/`gen`/`gate` 仍可使用，自动映射到新名称。

## 推荐使用流程

- **首次**：strategy → generate → coverage → 无参数运行 → accept → report
- **日常**：accept + 无参数运行。迭代中 impact --run 快速执行受影响测试
- **深度**：flaky · dryrun · baseline 按需使用。**发布**：report REL-xxx

## 流程

### Step 1：上下文加载

1. 检查 `.devpace/` 是否存在：
   - **存在** → 读取 `state.md` 确定当前 CR，读取 `project.md` 获取 PF 列表
   - **不存在** → 降级模式：基于代码库直接分析（无 PF→测试映射能力，仅 Layer 1 可用）
2. 如果指定了 CR 编号 → 定位对应 CR 文件
3. 如果未指定 → 读取 state.md 当前活跃 CR
4. 读取 `.devpace/rules/checks.md`（如存在）

### Step 2：路由到子命令

根据 $ARGUMENTS 第一个参数路由（**仅读取匹配子命令的规程文件**，不加载全部规程）。非自包含子命令执行前加载 skills/pace-test/test-procedures-common.md（分层输出约定 + 技术栈检测 SSOT）。

| 参数 | 流程 | 详细规程 |
|------|------|---------|
| （空） | Layer 1 基础执行 | `skills/pace-test/test-procedures-core.md` §1 |
| `accept`（旧名 `verify`） | Layer 3 AI 验收验证 | `skills/pace-test/test-procedures-verify.md` |
| `generate`（旧名 `gen`） | 测试用例生成 | `skills/pace-test/test-procedures-generate.md`（自包含） |
| `strategy` | 测试策略生成 | `skills/pace-test/test-procedures-strategy-gen.md` |
| `coverage` | 需求覆盖分析 | `skills/pace-test/test-procedures-coverage.md` |
| `impact`（旧名 `regress`） | 变更影响分析 | `skills/pace-test/test-procedures-impact.md` |
| `report` | 测试摘要报告（CR 级/Release 级） | `skills/pace-test/test-procedures-report.md` |
| `flaky` | 不稳定测试分析 | `skills/pace-test/test-procedures-flaky.md`（自包含） |
| `dryrun`（旧名 `gate`） | 模拟门禁执行 | `skills/pace-test/test-procedures-dryrun.md`（自包含） |
| `baseline` | 测试基准线 | `skills/pace-test/test-procedures-baseline.md`（自包含） |

### Step 3：执行并报告

1. 按子命令流程执行
2. 将关键结果写入 CR 文件"验证证据"section（如 verify 产出）
3. 更新 state.md（如有状态变化）
4. **智能推荐**（仅空参数运行时）：根据 CR 状态推荐下一步（规则见 skills/pace-test/test-procedures-common.md）

## 输出

分阶段输出：子命令执行结果 + 下一步建议。支持 --brief / --detail 三级输出详细度（规则见 skills/pace-test/test-procedures-common.md）。
