# skill-creator 对比分析与借鉴采纳方案

> **产出日期**：2026-03-06
> **背景**：Anthropic 官方 [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) 是 Skill 全生命周期管理的元 Skill。devpace 已完成 18 个 Skill 开发（116/120 任务），但行为评估仅 pace-init 通过 skill-creator 评估（1/18）。本文档分析两者差异，确定采纳策略。

## 核心策略：Use, Don't Rebuild

skill-creator 的 3 个 Agent、8 个 Python 脚本、1 个 Viewer 全部可直接使用，**无需在 devpace 内重建任何等价物**。devpace 已有集成约定（`plugin-spec.md` §skill-creator 集成约定），pace-init 已成功走过 skill-creator 评估流程。应将此经验系统化推广到全部 18 个 Skill。

---

## Part 1：八维对比

| 维度 | skill-creator | devpace | 差距 | 策略 |
|------|--------------|---------|------|------|
| 行为评估 | 完整 pipeline（eval→grade→aggregate→view） | 仅 pace-init 有 evals（1/18） | 🔴 严重 | **直接用 skill-creator** |
| Description 管理 | 自动化 FP/FN 分析 + 优化循环 | CSO 规则已有，无自动化验证 | 🔴 严重 | **直接用 skill-creator** |
| 质量保障 | 迭代评估循环 | Gate 1/2/3 + Hook + 静态测试（更丰富） | 🟡 互补 | devpace 已领先，借鉴理念 |
| Agent 架构 | 3 个评估型（grader/comparator/analyzer） | 3 个角色型（engineer/pm/analyst） | 🔴 缺失维度 | **直接用 skill-creator Agent** |
| 数据契约 | 7 个 JSON Schema（eval 专用） | 14 个 Markdown Schema（无 eval 类） | 🟡 需扩展 | skill-creator Schema + 薄扩展 |
| 自动化工具 | 8 个 Python 脚本 | 4 个脚本（验证+版本） | 🔴 严重 | **直接用 skill-creator 脚本** |
| 可视化 | 自包含 HTML Viewer + feedback 机制 | 无 eval 可视化 | 🟡 中等 | **直接用 skill-creator Viewer** |
| 打包分发 | .skill 打包脚本 | Plugin marketplace | 🟢 低 | 路径不同，暂不需要 |

### devpace 领先的维度（无需借鉴）

- **静态测试体系**：14 个 pytest 文件，150+ 断言（skill-creator 仅 `quick_validate.py`）
- **Hook 运行时守卫**：8 个生命周期事件，Gate 3 人工阻断
- **Agent 记忆与角色隔离**：`memory: project`，`context: fork`
- **Schema 体系规模**：14 个 vs 7 个
- **分层架构强制隔离**：产品层/开发层，自动化检测

### skill-creator 领先的维度（需要补齐）

- **行为评估全链路**：评分→盲比→后验分析→可视化→反馈→改进
- **Description 自动化优化**：FP/FN 分析 + 扩展思考 + train/test 分割
- **证据链完整性**：每个判断必须附带 evidence
- **自审机制**：grader 反思评估方法本身的合理性

---

## Part 2：直接使用 vs 需要扩展

### 可直接使用 skill-creator 的能力（零开发）

| 能力 | skill-creator 组件 | 使用方式 |
|------|-------------------|---------|
| Eval 创建 | SKILL.md 主工作流 Phase 1 | 调用 `/skill-creator` 逐一创建 |
| 行为评估运行 | SKILL.md Phase 2 | 调用 `/skill-creator` 运行 with/without 对比 |
| 断言评分 | `agents/grader.md` | skill-creator 自动调用（8 步流程 + 自审） |
| 盲比较 | `agents/comparator.md` | Skill 版本对比时使用 |
| 后验分析 | `agents/analyzer.md` | 分析改进方向 |
| 基准聚合 | `scripts/aggregate_benchmark.py` | 生成 benchmark.json/md |
| 可视化审查 | `eval-viewer/viewer.html` | 遵循 workspace 约定 |
| Trigger 测试 | `scripts/run_eval.py` | 自动检测 FP/FN |
| Description 优化 | `scripts/run_loop.py` + `improve_description.py` | 含 train/test 分割 |

### 需要 devpace 自建的薄扩展层

| 扩展需求 | 原因 | 工作量 |
|---------|------|--------|
| Eval 定义文件 ×17 | eval 内容必须 devpace 逐 Skill 编写 | L |
| Trigger eval 定义文件 ×17 | 含跨 Skill 交叉污染测试 | M |
| validate-all.sh 集成 | 将 trigger eval 纳入验证流水线 | S |
| acceptance-matrix 联动 | eval 覆盖率反映到验收矩阵 | S |
| Makefile eval 目标 | 一键化执行 | S |
| 目录结构重组 | 平铺 → 按 Skill 子目录 | S |

### 不需要自建的

| ❌ 不需要自建 | 原因 |
|-------------|------|
| `agents/pace-eval-grader.md` | 直接用 skill-creator 的 `agents/grader.md` |
| `agents/pace-eval-comparator.md` | 直接用 skill-creator 的 `agents/comparator.md` |
| `agents/pace-eval-analyzer.md` | 直接用 skill-creator 的 `agents/analyzer.md` |
| Python eval 脚本 (×4) | 直接用 skill-creator 的脚本 |

**节省**：原方案 ~2000 行代码，现在 = **0 行代码**。

---

## Part 3：设计理念评估

| 理念 | 增量价值 | 结论 |
|------|---------|------|
| 证据链 → Gate 2 | 低（Gate 2 已部分覆盖） | **不做** |
| 自审机制 → pace-retro | 低（通用实践，非独有） | **不做** |
| 跨 Skill 交叉污染测试 | **高**（18 Skill 关键词冲突真实风险） | **归入 trigger eval** |
| 渐进披露验证 | 低（YAGNI） | **不做** |

重点交叉测试对：
- pace-dev ↔ pace-change（"开始做" vs "加需求"）
- pace-status ↔ pace-trace（"查看状态" vs "决策追溯"）
- pace-test ↔ pace-review（"测试" vs "审核"）
- pace-guard ↔ pace-test（"风险检查" vs "测试验证"）

---

## Part 4：反模式警告

| 反模式 | 原因 |
|--------|------|
| 在 devpace 内重建 grader/comparator/analyzer | skill-creator 已提供，重建导致版本分裂 |
| 重写 Python eval 脚本 | 同上 |
| 在 `knowledge/_schema/` 新增 eval schema | eval 是开发层关注点，放入产品层违反分层约束 |
| with/without 对比作为常规门禁 | 仅对新 Skill/重大重构有价值，日常成本过高 |
| 构建 18-Skill 串行测试 runner | 应按 Skill 独立执行，不绑定单体流程 |
| 另建 feedback 反馈通道 | skill-creator viewer 的 feedback.json 已足够 |

---

## Part 5：采纳路线图

### Phase A：系统化推广 skill-creator 覆盖

为全部 18 个 Skill 建立完整三层 eval（T1 Trigger + T2 Behavioral + T3 Full Cycle）。

**核心 5 Skill**（优先）：pace-dev、pace-change、pace-status、pace-review、pace-next

**调用方式**：每个 Skill 独立会话，调用 `/skill-creator` 并指定目标 Skill 目录。

**按变更阶段选择执行深度**：

| 变更类型 | 执行层级 |
|---------|---------|
| description 修改 | T1 only |
| procedures 修改 | T1 + T2 |
| SKILL.md 主体修改 | T1 + T2 |
| 重大重构 / 新 Skill | T1 + T2 + T3 |
| 版本发布前 | T1 全量 + T2 全量 |

### Phase B：薄扩展层

| 步骤 | 任务 | 状态 |
|------|------|------|
| B.1 | 目录重组：eval 从平铺 → 按 Skill 子目录 | ✅ |
| B.2 | `tests/conftest.py` 新增 EVAL_DIRS | ✅ |
| B.3 | `scripts/validate-all.sh` Tier 3 eval 覆盖率 | ✅ |
| B.4 | `Makefile` eval 目标 | ✅ |
| B.5 | `plugin-spec.md` eval 子目录规范 | ✅ |
| B.6 | `CONTRIBUTING.md` skill-creator 前置条件 | ✅ |
| B.7 | `acceptance-matrix.md` eval 覆盖列 | ✅ |
| B.8 | `shared-assertions.md` 共享断言模式 | ✅ |

---

## Part 6：引入方式

**推荐**：skill-creator 作为开发者全局 Skill 安装，devpace 项目内仅定义集成约定。

```bash
# 安装方式（记入 CONTRIBUTING.md）
/install skill-creator               # 从 Marketplace
/install skill-creator@anthropics/skills  # 从 GitHub
```

devpace 项目内只需：
1. `plugin-spec.md` §skill-creator 集成约定（已有 + 已扩展）
2. `.gitignore` 排除 `skills/*-workspace/`（已有）
3. `CONTRIBUTING.md` 新增前置条件（已完成）
4. eval 定义文件 + 目录结构（已搭建）

---

## Part 7：目录结构

```
tests/evaluation/
├── _cross-cutting/               # 跨 Skill 全局文件
│   ├── acceptance-matrix.md
│   ├── shared-assertions.md      # 共享断言模式
│   ├── ux-rubric.md
│   └── v2-verification.md
├── pace-init/                    # per-Skill 子目录
│   ├── evals.json
│   └── trigger-evals.json
├── pace-dev/                     # Phase A 待创建
│   ├── evals.json
│   └── trigger-evals.json
└── ... (共 18 个子目录)
```

**关键决策**：
- Workspace 保留 `skills/*-workspace/`（不破坏 skill-creator 默认行为）
- Eval 按 Skill 子目录组织（支撑 18 Skill 规模）
- 不在 `knowledge/_schema/` 新增 eval schema（分层约束）

---

## Part 8：共享断言模式

| 模式 | 适用 Skill | 用途 |
|------|-----------|------|
| `state_updated` | 几乎所有 | state.md 被正确更新 |
| `cr_lifecycle` | pace-dev, pace-review, pace-change | CR 状态正确流转 |
| `natural_language` | 所有用户可见输出 | 零暴露 ID/状态机术语 |
| `p2_progressive` | pace-status, pace-next | 默认简洁，detail 展开 |
| `git_committed` | pace-dev | 原子步骤后 git commit |
| `schema_compliant` | 写入文件的 Skill | 产物符合 _schema/ 定义 |

---

## 工作量对比

| 维度 | 原方案（自建） | 修正方案（直接用） | 节省 |
|------|--------------|-------------------|------|
| Agent 定义 | ~300 行 | 0 | 100% |
| Python 脚本 | ~1200 行 | 0 | 100% |
| Viewer | ~200 行 | 0 | 100% |
| Eval 定义 | 34 文件 | 34 文件（skill-creator 创建） | 0% |
| 薄扩展层 | N/A | ~120 行更新 | — |
| **总计** | ~2000 行 + 35 文件 | 34 eval + ~120 行 | **~95%** |
