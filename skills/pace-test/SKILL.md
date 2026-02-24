---
description: Use when user says "跑测试", "测试覆盖", "验证一下", "验收", "回归", "影响分析", "test", "verify", "accept", "coverage", "测试策略", /pace-test, or when test results, coverage gaps, or acceptance readiness are discussed.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Grep, Bash
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

### accept 提升审批质量（与 Gate 2 的精细度差异）

Gate 2 判定"代码是否与计划一致"（通过/不通过）。accept 提供 Gate 2 做不到的 4 项精细能力：
1. **逐条验收标准附代码行号证据**（Gate 2 仅判定整体一致性）
2. **三级判定**：✅通过 / ⚠️需补充验证 / ❌未通过（Gate 2 仅二元判定）
3. **测试预言审查**：已有测试是否真的验了它声称覆盖的验收条件（Gate 2 不检查测试质量）
4. **弱覆盖/虚假覆盖自动降级测试策略**（accept↔strategy 双向闭环）

**定位**：不做 accept 也能过 Gate 2，但做了 accept 的 CR 在 Gate 3 人类审批时有更充分的证据支撑。

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

```
首次：strategy → generate [--full] → (编写/审查实现) → coverage → (开发中) → 无参数运行 → accept → report
日常：大多数场景只需 accept + 无参数运行。迭代中用 impact --run 快速执行受影响测试。
深度：flaky（稳定性+维护分析）· dryrun（Gate 预检）· baseline（基准线建立）按需使用。
发布：report REL-xxx 生成 Release 级质量报告。
```

## 流程

### Step 1：上下文加载

1. 检查 `.devpace/` 是否存在：
   - **存在** → 读取 `state.md` 确定当前 CR，读取 `project.md` 获取 PF 列表
   - **不存在** → 降级模式：基于代码库直接分析（无 PF→测试映射能力，仅 Layer 1 可用）
2. 如果指定了 CR 编号 → 定位对应 CR 文件
3. 如果未指定 → 读取 state.md 当前活跃 CR
4. 读取 `.devpace/rules/checks.md`（如存在）

### Step 2：路由到子命令

根据 $ARGUMENTS 第一个参数路由（**仅读取匹配子命令的规程文件**，不加载全部规程）：

| 参数 | 流程 | 详细规程 |
|------|------|---------|
| （空） | Layer 1 基础执行 | `test-procedures-core.md` §1 |
| `accept`（旧名 `verify`） | Layer 3 AI 验收验证 | `verify-procedures.md` |
| `generate`（旧名 `gen`） | 测试用例生成 | `test-procedures-generate.md` §2 |
| `strategy` | 测试策略生成 | `test-procedures-strategy-gen.md` |
| `coverage` | 需求覆盖分析 | `test-procedures-coverage.md` |
| `impact`（旧名 `regress`） | 变更影响分析 | `test-procedures-impact.md` |
| `report` | 测试摘要报告（CR 级/Release 级） | `test-procedures-report.md` |
| `flaky` | 不稳定测试分析 | `test-procedures-advanced.md` §7 |
| `dryrun`（旧名 `gate`） | 模拟门禁执行 | `test-procedures-advanced.md` §8 |
| `baseline` | 测试基准线 | `test-procedures-advanced.md` §9 |

### Step 3：执行并报告

1. 按子命令流程执行
2. 将关键结果写入 CR 文件"验证证据"section（如 verify 产出）
3. 更新 state.md（如有状态变化）
4. **智能推荐**（仅空参数运行时）：报告末尾根据当前 CR 状态推荐下一步操作：
   - CR 在 developing → "建议：提交前执行 `/pace-test dryrun 1` 预检 Gate 1"
   - CR 在 verifying → "建议：执行 `/pace-test accept` 采集验收证据"
   - CR 在 in_review → "建议：执行 `/pace-test report` 生成审查报告"
   - 无活跃 CR → "建议：执行 `/pace-test strategy` 生成测试策略"
   - 有子命令参数时不输出推荐（用户已明确意图）

## 输出

测试/验证结果摘要（3-5 行）。verify 子命令额外输出逐条验收状态。
