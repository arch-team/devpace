---
description: Use when user says "跑测试", "测试覆盖", "验证一下", "验收", "回归", "影响分析", "test", "verify", "accept", "coverage", "测试策略", /pace-test, or wants to run tests, check requirement coverage, verify acceptance criteria, or manage testing strategy.
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Grep, Bash
argument-hint: "[accept 验收|strategy 策略|coverage 覆盖|impact 影响|report 报告|...深度] [CR编号|PF标题]"
model: sonnet
---

# /pace-test — BizDevOps 感知的测试策略与验证

基于业务上下文（BR→PF→CR 价值链），智能管理和执行测试验证——不只是"跑测试"，而是"基于需求验收标准，评估验证覆盖度和执行 AI 驱动的验收验证"。

## 与现有机制的关系

- `checks.md`：定义 Gate 1/2 要执行的**命令列表**（what to run）
- `/pace-test`：管理**测试策略**（what to test, why, how comprehensive）
- `/pace-dev` Gate 1/2：消费 checks.md 中的测试命令
- `/pace-review` Gate 2：可消费 `/pace-test accept` 的验收映射报告作为审查证据

## 输入

$ARGUMENTS：

**日常使用**（大多数场景只需这些）：
- （空）→ 对当前 CR 运行所有已配置的测试，输出结构化报告
- `accept [CR编号]` → AI 驱动的验收验证：逐条比对 PF 验收标准与实际行为
- `strategy` → 基于 PF 验收标准生成测试策略建议
- `coverage` → 分析当前测试对 PF 验收标准的覆盖度（需求覆盖率，非代码覆盖率）
- `impact [CR编号]` → 变更影响分析：基于变更范围推荐需要重跑的测试
- `report` → 生成面向人类的测试摘要报告（供 Gate 3 审批参考）

**深度功能**（按需使用）：
- `generate [PF标题]` → 基于 PF 验收标准生成测试用例框架（技术栈感知）
- `flaky` → 分析历史测试结果，识别不稳定测试并建议修复/隔离
- `dryrun [1|2|4]` → 模拟执行指定 Gate 的完整检查流程（dry-run）
- `baseline` → 建立/更新测试基准线（供 /pace-retro 度量使用）

> **向后兼容**：旧名称 `verify`/`regress`/`gen`/`gate` 仍可使用，自动映射到新名称。

## 流程

### Step 1：上下文加载

1. 检查 `.devpace/` 是否存在：
   - **存在** → 读取 `state.md` 确定当前 CR，读取 `project.md` 获取 PF 列表
   - **不存在** → 降级模式：基于代码库直接分析（无 PF→测试映射能力，仅 Layer 1 可用）
2. 如果指定了 CR 编号 → 定位对应 CR 文件
3. 如果未指定 → 读取 state.md 当前活跃 CR
4. 读取 `.devpace/rules/checks.md`（如存在）

### Step 2：路由到子命令

根据 $ARGUMENTS 第一个参数路由：

| 参数 | 流程 | 详细规程 |
|------|------|---------|
| （空） | Layer 1 基础执行 | `test-procedures.md` §1 |
| `accept`（旧名 `verify`） | Layer 3 AI 验收验证 | `verify-procedures.md` |
| `generate`（旧名 `gen`） | 测试用例生成 | `test-procedures.md` §2 |
| `strategy` | 测试策略生成 | `test-procedures.md` §3（Phase 2） |
| `coverage` | 需求覆盖分析 | `test-procedures.md` §4（Phase 2） |
| `impact`（旧名 `regress`） | 变更影响分析 | `test-procedures.md` §5（Phase 2） |
| `report` | 测试摘要报告 | `test-procedures.md` §6（Phase 2） |
| `flaky` | 不稳定测试分析 | `test-procedures.md` §7（Phase 3） |
| `dryrun`（旧名 `gate`） | 模拟门禁执行 | `test-procedures.md` §8（Phase 3） |
| `baseline` | 测试基准线 | `test-procedures.md` §9（Phase 3） |

### Step 3：执行并报告

1. 按子命令流程执行
2. 将关键结果写入 CR 文件"验证证据"section（如 verify 产出）
3. 更新 state.md（如有状态变化）

## 输出

测试/验证结果摘要（3-5 行）。verify 子命令额外输出逐条验收状态。
