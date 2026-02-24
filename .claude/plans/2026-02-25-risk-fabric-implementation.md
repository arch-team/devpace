# Risk Fabric 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 devpace 增加"预判→监控→趋势"三阶段风险闭环，包含持久化风险登记簿和分级自主响应。

**Architecture:** 新增 `/pace-guard` Skill（含 guard-procedures.md）+ `risk-format.md` Schema，同时在 pace-dev/pace-pulse/pace-retro 中嵌入风险感知触发点。风险持久化到 `.devpace/risks/`，状态机 `open→mitigated|accepted|resolved`。

**Tech Stack:** Markdown（产品层资产）+ Python pytest（静态测试）

---

### Task 1: conftest.py 注册新 Skill 和 Schema

**Files:**
- Modify: `tests/conftest.py:14-33`

**Step 1: 在 SKILL_NAMES 列表添加 pace-guard**

在 `tests/conftest.py:14` 的 SKILL_NAMES 列表中，按字母序在 `"pace-feedback"` 和 `"pace-init"` 之间插入 `"pace-guard"`：

```python
SKILL_NAMES = [
    "pace-change",
    "pace-dev",
    "pace-feedback",
    "pace-guard",       # ← 新增
    "pace-init",
    ...
]
```

**Step 2: 在 SCHEMA_FILES 列表添加 risk-format.md**

在 `tests/conftest.py:33` 的 SCHEMA_FILES 列表中，按字母序在 `"release-format.md"` 之前插入 `"risk-format.md"`：

```python
SCHEMA_FILES = [..., "release-format.md", "risk-format.md", "state-format.md", ...]
```

**Step 3: 运行测试验证注册正确（预期失败）**

Run: `python -m pytest tests/static/test_conftest_sync.py -v`
Expected: FAIL — `pace-guard` 不在文件系统，`risk-format.md` 不存在

**Step 4: Commit**

```bash
git add tests/conftest.py
git commit -m "test(conftest): 注册 pace-guard Skill 和 risk-format Schema"
```

---

### Task 2: 创建 risk-format.md Schema

**Files:**
- Create: `knowledge/_schema/risk-format.md`

**Step 1: 创建 risk-format.md**

参考现有 schema 结构（如 `cr-format.md`），创建风险文件格式定义。必须包含：

- `§0 速查卡片`（代码块，含编号规则/来源/严重度/状态机/存储位置）
- `## 文件结构`（完整 RISK-NNN.md 模板）
- `## 字段合法值`（来源 4 种、严重度 3 级、状态 4 种）
- `## 状态机`（open→mitigated|accepted|resolved 的转换规则）
- `## 综合风险等级计算`（取所有维度最高等级）
- `## 命名规则`（RISK-NNN.md，NNN 从 001 递增）
- `## 更新时机`

文件结构模板：

```markdown
# RISK-{{NNN}}

> **来源**：{{pre-flight|runtime|retrospective|external}}
> **严重度**：{{Low|Medium|High}}
> **状态**：{{open|mitigated|accepted|resolved}}
> **关联 CR**：{{CR-NNN 或"无"}}

## 发现

{{问题描述}}

## 建议

{{建议的缓解/解决方案}}

## 处理记录

| 日期 | 操作 | 状态变更 | 说明 |
|------|------|---------|------|
| {{YYYY-MM-DD}} | 创建 | → open | {{初始记录}} |
```

**Step 2: 运行 conftest sync 测试**

Run: `python -m pytest tests/static/test_conftest_sync.py::TestConftestSync::test_tc_cs_03_schema_files_match_filesystem -v`
Expected: PASS — risk-format.md 现在存在

**Step 3: 运行 markdown 结构测试**

Run: `python -m pytest tests/static/test_markdown_structure.py -v -k "schema"`
Expected: PASS — §0 速查卡片存在

**Step 4: Commit**

```bash
git add knowledge/_schema/risk-format.md
git commit -m "feat(knowledge): risk-format.md 风险文件格式契约"
```

---

### Task 3: CR Schema 扩展（可选风险 section）

**Files:**
- Modify: `knowledge/_schema/cr-format.md:5-10` (§0 速查卡片) + 文件末尾追加

**Step 1: 在 §0 速查卡片中添加风险 section 说明**

在 `cr-format.md:5` 的速查卡片代码块中追加一行：

```
可选 section：根因分析（defect）| 影响分析（/pace-test impact）| 验证证据（/pace-test accept）| 风险预评估（/pace-guard scan）| 运行时风险（推进模式 checkpoint）
```

**Step 2: 在文件末尾追加两个可选 section 定义**

在 `cr-format.md` 文件末尾（L261 之后）追加：

```markdown
## 风险预评估（可选）

Pre-flight 风险扫描结果。由 `/pace-guard scan` 或推进模式意图检查点写入。

格式：

```markdown
## 风险预评估

| # | 维度 | 等级 | 发现 | 建议 |
|---|------|------|------|------|

**综合风险等级**：{{Low|Medium|High}}
```

维度合法值：历史教训、依赖影响、架构兼容性、范围复杂度、安全敏感度。
等级合法值：Low、Medium、High。
综合风险等级 = 取所有维度的最高等级。

## 运行时风险（可选）

推进模式中 checkpoint 实时检测到的风险信号。由 Claude 在推进模式 checkpoint 时追加。

格式：

```markdown
## 运行时风险

| 时间 | 信号类型 | 等级 | 发现 | 处理 |
|------|---------|------|------|------|
```

信号类型合法值：技术债引入、安全隐患、架构腐化。
处理合法值：已记录（Low）、已提醒（Medium）、已暂停（High）。
```

**Step 3: 运行 schema 测试**

Run: `python -m pytest tests/static/test_schema_compliance.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add knowledge/_schema/cr-format.md
git commit -m "feat(knowledge): CR Schema 扩展——风险预评估和运行时风险可选 section"
```

---

### Task 4: CR 模板文件扩展

**Files:**
- Modify: `skills/pace-init/templates/cr.md`

**Step 1: 读取当前 CR 模板确认末尾位置**

**Step 2: 在 CR 模板文件末尾追加风险 section 注释占位**

```markdown
<!-- 以下 section 由 /pace-guard 或推进模式自动写入，无需手动编辑 -->
<!-- ## 风险预评估 -->
<!-- ## 运行时风险 -->
```

**Step 3: 运行模板测试**

Run: `python -m pytest tests/static/test_schema_compliance.py -v -k "cr_template"`
Expected: PASS

**Step 4: Commit**

```bash
git add skills/pace-init/templates/cr.md
git commit -m "feat(skills): CR 模板追加风险 section 占位注释"
```

---

### Task 5: 创建 pace-guard SKILL.md

**Files:**
- Create: `skills/pace-guard/SKILL.md`

**Step 1: 创建 SKILL.md**

按 CSO description 编写规则（只写"何时触发"，不写"做什么"）：

```yaml
---
description: Use when user wants to assess risks before development, check current risk status, analyze risk trends, or says "风险/预检/预分析/guard/risk". Also auto-invoked during advance mode intent checkpoint for L/XL CRs. NOT for /pace-dev (implementation), NOT for /pace-review (quality gate).
allowed-tools: Read, Glob, Grep, Write, Edit
argument-hint: [scan|monitor|trends|report|resolve] [CR编号]
---
```

SKILL.md 正文包含：
- 标题和 1-2 行用途说明
- 子命令表（scan/monitor/trends/report/resolve）
- 输入（每个子命令的数据源）
- 流程（高层步骤，详见 guard-procedures.md）
- 输出（每个子命令的产出格式概述）

**Step 2: 运行 conftest sync 测试**

Run: `python -m pytest tests/static/test_conftest_sync.py::TestConftestSync::test_tc_cs_01_skill_names_match_filesystem -v`
Expected: PASS — pace-guard 目录含 SKILL.md

**Step 3: 运行 frontmatter 测试**

Run: `python -m pytest tests/static/test_frontmatter.py -v -k "skill"`
Expected: PASS — frontmatter 字段合法

**Step 4: Commit**

```bash
git add skills/pace-guard/SKILL.md
git commit -m "feat(skills): pace-guard SKILL.md 风险管理统一入口"
```

---

### Task 6: 创建 guard-procedures.md

**Files:**
- Create: `skills/pace-guard/guard-procedures.md`

**Step 1: 创建 guard-procedures.md**

结构化章节：

```
# pace-guard 执行规程
## §0 速查卡片
## scan — Pre-flight 风险扫描
### 5 维扫描规则
### 严重度判定矩阵
### 扫描结果写入规则
### 与意图检查点的整合
## monitor — 实时风险汇总
### 信号类型定义
### 检测触发条件
### 结果写入规则
## trends — 跨 CR 趋势分析
### 数据采集来源
### 趋势计算规则
### 输出格式
## report — 风险全局视图
### 数据源
### 输出格式
## resolve — 风险状态更新
### 状态转换规则
### 自动提议时机
## 分级自主矩阵
## 风险文件创建规则
```

每个子命令的详细规则按设计文档 §5-§7 的内容填充。

**Step 2: 运行 markdown 结构测试**

Run: `python -m pytest tests/static/test_markdown_structure.py -v -k "section0"`
Expected: PASS — §0 速查卡片存在

**Step 3: Commit**

```bash
git add skills/pace-guard/guard-procedures.md
git commit -m "feat(skills): guard-procedures.md 风险管理执行规程"
```

---

### Task 7: 意图检查点嵌入 scan 触发

**Files:**
- Modify: `skills/pace-dev/dev-procedures.md:16-90` (意图检查点章节)

**Step 1: 在意图检查点规则区域追加 scan 触发规则**

在 `dev-procedures.md` 的意图检查点规则（约 L26-L31 之后）追加：

```markdown
### 风险预扫描（scan 触发）

意图检查点完成后，根据复杂度评估自动触发风险预扫描：

| 复杂度 | 触发条件 | 行为 |
|--------|---------|------|
| S（单文件） | 不触发 | — |
| S（多文件）/ M | 仅在 insights.md 有匹配的防御 pattern（defense 类型，置信度 ≥ 0.5）时触发 | 轻量扫描（仅历史教训维度） |
| L / XL | 必须触发 | 完整 5 维扫描 |

扫描规则详见 `guard-procedures.md` scan 章节。扫描结果写入 CR "风险预评估" section。

若综合风险等级为 High：
- 执行计划中增加对应防护步骤
- 输出提醒："⚠️ 风险预评估为 High（[原因]），已在执行计划中增加防护步骤。"
```

**Step 2: 在 §0 速查卡片中追加风险预扫描描述**

在 `dev-procedures.md:5` 速查卡片的最后追加：
```
- **风险预扫描**：L/XL 必须 + S 多文件/M 按 insights 匹配触发（guard-procedures.md scan）
```

**Step 3: 运行全部测试验证无回归**

Run: `python -m pytest tests/static/ -v`
Expected: ALL PASS

**Step 4: Commit**

```bash
git add skills/pace-dev/dev-procedures.md
git commit -m "feat(skills): dev-procedures 意图检查点嵌入风险预扫描触发"
```

---

### Task 8: pace-pulse 新增第 8 信号

**Files:**
- Modify: `skills/pace-pulse/pulse-procedures.md:6-16` (信号评估表)
- Modify: `skills/pace-pulse/SKILL.md` (触发条件描述更新，如需要)

**Step 1: 在信号评估表追加第 8 行**

在 `pulse-procedures.md:15`（第 7 信号之后）追加：

```markdown
| 8 | 风险积压 | `.devpace/risks/` 中 open 风险数 > 3 或 High 风险 > 0 | Medium | "有 [N] 个未处理风险（含 [M] 个高级别），建议运行 `/pace-guard report` 评估。" |
```

**Step 2: 在建议模板章节追加对应模板**

在 `pulse-procedures.md` 的"建议模板"章节（约 L17-L35）追加信号 8 的建议模板。

**Step 3: 更新 §1 会话开始节奏检测（如需要）**

检查"会话开始节奏检测"章节（L42）的信号优先级表，评估是否需要在会话开始时也检测风险积压信号。若是，在 L52-L61 的信号优先级列表中追加。

**Step 4: 运行测试**

Run: `python -m pytest tests/static/ -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add skills/pace-pulse/pulse-procedures.md
git commit -m "feat(skills): pulse-procedures 新增第 8 信号——风险积压"
```

---

### Task 9: pace-retro 新增风险趋势段

**Files:**
- Modify: `skills/pace-retro/retro-procedures.md:58-73` (回顾报告格式)

**Step 1: 在回顾报告格式中追加风险趋势 section**

在 `retro-procedures.md` 的"回顾报告格式"模板（L58-L73）中，在现有内容之后（DORA 报告之前）追加：

```markdown
### 风险趋势（`.devpace/risks/` 存在时）

数据采集：扫描 `.devpace/risks/` 所有风险文件 + `insights.md` 中 defense 类型条目。

输出格式：

```markdown
## 风险趋势

### 跨迭代模式（最近 3 迭代）
| 风险类型 | Iter-N-2 | Iter-N-1 | Iter-N | 趋势 |
|---------|---------|---------|--------|------|

### 重复 Pattern Top 3
1. "[pattern 描述]" → 建议：[行动]

### 风险登记簿状态
- Open: [N]（High: [H], Medium: [M], Low: [L]）
- 本迭代解决: [R]
```

条件渐进暴露：`.devpace/risks/` 不存在时静默跳过。
趋势判定：连续 2 迭代同类型风险增加 = ↑ 恶化；连续 2 迭代减少 = ↓ 改善；其他 = → 稳定。
```

**Step 2: 运行测试**

Run: `python -m pytest tests/static/ -v`
Expected: ALL PASS

**Step 3: Commit**

```bash
git add skills/pace-retro/retro-procedures.md
git commit -m "feat(skills): retro-procedures 新增风险趋势分析段"
```

---

### Task 10: devpace-rules.md §10 + §0 更新

**Files:**
- Modify: `rules/devpace-rules.md:15-68` (§0 速查卡片) + `rules/devpace-rules.md:322-333` (§10)

**Step 1: 更新 §10 主动节奏管理**

在 `devpace-rules.md:322` 的 §10 章节中，追加风险相关内容：

```markdown
### 风险感知（`.devpace/risks/` 存在时生效）

- **Pre-flight**：L/XL CR 意图检查点自动触发风险预扫描（详见 dev-procedures.md）
- **Runtime**：推进模式 checkpoint 增加轻量风险信号检测（技术债/安全/架构 3 类）
- **脉搏第 8 信号**：open 风险 > 3 或 High 风险 > 0 时提醒（详见 pulse-procedures.md）

### 分级自主响应

| 项目自主级别 | Low | Medium | High |
|------------|-----|--------|------|
| 辅助 | 记录+简要提醒 | 记录+详细提醒+方案 | 暂停+等用户 |
| 标准 | 静默记录 | 记录+提醒+方案 | 暂停+等用户 |
| 自主 | 静默记录 | 记录+自动缓解+报告 | 提醒+方案+等用户 |
```

**Step 2: 更新 §0 速查卡片**

在 §0 速查卡片的"主动节奏"行（约 L46）更新：

```
主动节奏 + 风险
每 5 checkpoint 脉搏检查 | 8 信号（含风险积压）| 每会话最多 3 条提醒 | L/XL 意图检查点风险预扫描
分级响应：Low 静默 | Medium 提醒+方案 | High 暂停等人
```

在"命令分层"表（约 L49-L57）的"进阶"行追加 `/pace-guard`：

```
| 进阶 | /pace-change · /pace-plan · /pace-retro · /pace-guard |
```

**Step 3: 运行全部测试**

Run: `python -m pytest tests/static/ -v && python -m pytest tests/static/test_markdown_structure.py -v`
Expected: ALL PASS

**Step 4: Commit**

```bash
git add rules/devpace-rules.md
git commit -m "feat(rules): §10 风险感知 + 分级自主响应 + §0 速查卡片更新"
```

---

### Task 11: 运行全量测试 + 验证

**Files:** 无新文件

**Step 1: 运行全部静态测试**

Run: `python -m pytest tests/static/ -v`
Expected: ALL PASS，测试数量应 ≥ 215（原有）

**Step 2: 运行 markdownlint**

Run: `npx markdownlint-cli2 "knowledge/_schema/risk-format.md" "skills/pace-guard/*.md"`
Expected: 0 errors

**Step 3: 验证分层完整性**

Run: `grep -r "docs/\|\.claude/" rules/ skills/ knowledge/`
Expected: 空结果（产品层不引用开发层）

**Step 4: 验证 plugin.json 无需手动更新**

确认 `pace-guard` 通过 `skills/` 目录自动发现注册，plugin.json 无需修改。

**Step 5: Commit（如有修复）**

```bash
git commit -m "fix(*): Risk Fabric 全量测试修复"
```

---

### Task 12: progress.md + roadmap.md 更新

**Files:**
- Modify: `docs/planning/progress.md`
- Modify: `docs/planning/roadmap.md`（如需添加新 Phase/里程碑）

**Step 1: 更新 progress.md**

- 快照：版本更新为 v1.4.0（或待定）
- 当前任务表：添加 Risk Fabric 任务（T105+）
- 变更记录：添加本次变更条目

**Step 2: 评估是否需要更新 roadmap.md**

如果 Risk Fabric 构成新的 Phase 17，在 roadmap.md 中添加对应 Phase 和里程碑。

**Step 3: Commit**

```bash
git add docs/planning/progress.md docs/planning/roadmap.md
git commit -m "docs(planning): Risk Fabric 任务注册和进度更新"
```
