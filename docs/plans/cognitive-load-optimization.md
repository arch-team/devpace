# devpace 产品层认知负担优化方案

## Context

devpace 产品层（随 Plugin 分发的运行时资产）经过多轮迭代（含最近的 pace-biz 智能化重构），规模如下：

| 组件 | 文件数 | 行数 |
|------|--------|------|
| rules/ | 1 | 580 |
| skills/（19 Skill，不含 eval workspace） | ~120 .md | ~13,800 |
| knowledge/（含 _schema/） | 36 | 5,551 |
| hooks/ | 18 | 1,432 |
| agents/ + output-styles/ + 配置 | ~6 | ~210 |
| **产品层合计** | **~181** | **~21,573** |

对维护和开发此插件的开发者而言，存在严重认知负担：

- **rules/devpace-rules.md** 始终加载 580 行，同时承担行为规则+路由分发+速查索引三重职责，扇出 35-40 个文件引用
- **26 个 Schema** 合计 ~4,050 行（近期新增 merge-strategy.md、readiness-score.md），向后兼容条款在多文件中重复 ~70 处，溢出模式散布 4 个文件
- **19 个 Skill** 碎片化严重，**46 个 procedures 文件不足 50 行**（最短 13 行）
- 交叉引用网络形成认知迷宫：knowledge/ 与 skills/ 双向引用 ~60 处，修改一个信号定义需同步检查 6 处
- 共享知识放错位置：`role-procedures-dimensions.md` 被 8+ Skill 引用却放在 pace-role 目录下
- **悬空资产**：新增的 `knowledge/biz-analysis-models.md`（270 行）在 skills/ 和 rules/ 中零引用，违反 IA-9 认知清晰（无明确加载路径）

**目标**：系统性降低认知负担，提升可维护性，不破坏现有功能。

---

## 优化原则

1. **不破坏功能**：结构重组，不删减功能
2. **始终加载优先瘦身**：rules 每减 1 行 = 每次会话都省上下文
3. **合并碎片**：减少文件总数和跨文件导航
4. **共享知识归位**：被 3+ Skill 引用的内容属于 knowledge/
5. **重复管理而非消除**：合法重复标记权威源，建立同步链路
6. **遵循 IA 原则**：特别是 IA-1 单向依赖、IA-5 按需加载、IA-6 单一权威

---

## Phase 1：碎片化 procedures 合并 + 共享知识归位 + 悬空资产处理

**目标**：文件数从 ~181 降到 ~145，消除跨 Skill 路径异味和悬空资产。纯机械操作，风险最低。

### 1A. 碎片化 procedures 合并（~33 文件减少）

将同一 Skill 中功能密切相关且不足 ~40 行的小 procedures 合并为逻辑单元。合并不删内容，仅减少文件数。

| Skill | 合并方案 | 文件数变化 |
|-------|---------|-----------|
| pace-release | tag(27)+version(46)+changelog(41)→`release-procedures-close-steps.md`; rollback(37)+branch(62)→`release-procedures-advanced.md`; wizard(52)+scheduling(50)→`release-procedures-planning.md` | 16→9 |
| pace-change | apply(27)+batch(27)→并入`change-procedures-execution.md`; undo(26)+history(40)→`change-procedures-audit.md` | 12→8 |
| pace-status | tree(13)+chain(26)→并入`status-procedures-detail.md`; keyword(19)+since(40)→`status-procedures-filter.md` | 10→6 |
| pace-feedback | hotfix(41)→并入`feedback-procedures-intake.md`; status(47)→并入`feedback-procedures-common.md` | 8→6 |
| pace-role | inference(37)+compare(25)→并入`role-procedures-switch.md`→重命名`role-procedures-core.md` | 5→3 |
| pace-next | output-why(22)+output-detail(23)→并入`next-procedures-output-default.md`→重命名`next-procedures-output.md` | 6→4 |
| pace-plan | health(17)+close(18)+adjust(20)→`plan-procedures-operations.md` | 5→3 |
| pace-pulse | session-end(34)→并入`pulse-procedures-core.md` | 6→5 |
| pace-biz | output(16)→并入`SKILL.md`尾部（纯索引，16 行足够内联） | 12→11 |

**每个合并的操作步骤**：
1. 读取所有待合并文件内容
2. 按逻辑顺序拼接到目标文件，用 `## ` 二级标题分隔原文件内容
3. 删除原文件
4. 更新对应 SKILL.md 路由表中的文件引用
5. grep 全产品层确认无残留旧路径引用

### 1B. 共享知识归位

**role-procedures-dimensions.md → 合并入 knowledge/role-adaptations.md**

当前状态：
- `skills/pace-role/role-procedures-dimensions.md`（19 行）：跨 Skill 角色定义（pace-status/pace-retro 关注点）
- `knowledge/role-adaptations.md`（24 行）：pace-biz 角色适配通用规则（最近未变更）

两者互补：dimensions 定义"每个角色在各 Skill 中关注什么"，adaptations 定义"角色适配的通用原则"。合并为统一的 `knowledge/role-adaptations.md`（~40 行），成为角色定义的单一权威源。

操作步骤：
1. 将 dimensions.md 的角色定义表合并入 role-adaptations.md
2. 删除 `skills/pace-role/role-procedures-dimensions.md`
3. 全局替换引用路径（约 8 处）：`grep -rn "role-procedures-dimensions" rules/ skills/ knowledge/`
4. 更新 `sync-checklists.md` 第 1 项路径

### 1C. 悬空资产处理

**`knowledge/biz-analysis-models.md`（270 行）零引用问题**

当前状态：
- 文件声称是 pace-biz 智能行为的理论锚点（四模型体系：Process/Data/Discovery/Quality）
- 但 skills/ 和 rules/ 中 **没有任何文件引用它**
- 按 IA-9 认知清晰原则，没有明确加载路径的文件会依赖 LLM 隐性推理，不可靠

操作方案（二选一，需确认）：
- **方案 A（推荐）：建立引用路径**——在 `skills/pace-biz/SKILL.md` 的路由表中添加加载指令：当 pace-biz 的 discover/import/infer/decompose 子命令执行时，引用 `knowledge/biz-analysis-models.md` 对应章节（§1 Process Model 判断当前阶段，§3 Discovery Model 指导发现策略）
- **方案 B：降级为开发参考**——移到 `docs/research/` 作为设计参考文档，不作为运行时资产分发

### Phase 1 验证

- `bash dev-scripts/validate-all.sh` 全部通过
- `grep -rn "<旧文件名>" rules/ skills/ knowledge/` 对每个被删文件返回空
- 每个涉及的 SKILL.md 路由表指向正确的新文件
- `claude --plugin-dir ./` 加载无报错

---

## Phase 2：Rules 文件瘦身（580 行 → ~330 行）

**目标**：将始终加载的 rules 从三重职责收缩为纯行为规则，减少 ~43% 上下文消耗。

### 2A. 抽取 §11 导航/管道细节到 knowledge/（约 -65 行）

§11（367-428 行）中"merged 后 7 步管道"和"全局导航集成"是执行步骤而非行为规则。

操作：
1. 创建 `knowledge/navigation-guide.md`（约 70 行）：
   - 从 §11 移入：merged 后 7 步管道详细步骤、target skill 完成后引导表、自主级别感知规则、与 session-start 去重规则
2. rules §11 保留：
   - 约束声明："merged 后自动执行连锁管道"一句话
   - 信号权威源委托："信号优先级 SSOT 见 `knowledge/signal-priority.md`"
   - "功能发现（嵌入式触发）"约束声明一句话
3. 各消费方（pace-dev/pace-review/pace-retro 等）更新引用路径

### 2B. 抽取 §2 推进细节到 pace-dev procedures（约 -55 行）

§2（111-180 行）中"简化审批条件细则""批量审批""连续推进""推进中探索连续模式"是 pace-dev 执行细节。

操作：
1. 将以下内容移入 `skills/pace-dev/dev-procedures-common.md`（部分已存在，去重合并）：
   - 简化审批完整条件和流程（145-156 行）
   - 批量审批规则（153-157 行）
   - 推进中探索连续模式（165-181 行）
2. rules §2 保留：
   - 探索模式定义 + IR-1
   - 推进模式进入条件 + 模式切换通知
   - 自主级别读取规则 + IR-2/IR-3 声明
   - 一句话权威委托："推进行为详细规则见 pace-dev procedures"

### 2C. 压缩 §0 速查卡片（约 -15 行）

操作：
- 移除 §0 中的子命令详表（第 55 行，子命令权威在各 SKILL.md）
- 压缩命令分层表为一行摘要："核心 5 + 业务 1 + 进阶 6 + 专项 5 + 系统 2 — 详见各 SKILL.md"
- 保留：铁律、会话生命周期、双模式、节奏+风险+导航+质量索引

### 2D. 精简 §10/§14/§16 权威委托（约 -30 行）

操作：
- §10（335-366 行）：移除跨 Skill 风险集成表（重复 Skill procedures 内容），保留触发规则 + 一句话委托
- §14（491-513 行）：压缩为生效条件表（4 行）+ "详见对应 Skill"，移除重复的 Release 状态机和 Gate 4 描述
- §16（548-580 行）：压缩为生效条件 + 核心约束 3 条，移除重复的详细同步行为规则

### Phase 2 验证

- `wc -l rules/devpace-rules.md` ≤ 350
- 被移出的内容在目标文件中存在且无遗漏
- 手动场景验证：会话开始→探索→推进→Gate 1→Gate 2→merged 全流程，确认行为不变
- `bash dev-scripts/validate-all.sh` 全部通过

---

## Phase 3：Schema 体系简化

**目标**：向后兼容条款从 ~70 处/15+ 文件统一到 1 文件，project-format.md 从 550 行降至 ~430 行。Schema 总数 26 个（含新增的 merge-strategy.md 和 readiness-score.md），合计 ~4,050 行。

### 3A. 创建 knowledge/_schema/compatibility-rules.md（新文件，约 80 行）

统一定义所有向后兼容策略和溢出模式：

```
§1 向后兼容策略矩阵（表格）
  - 每行：特性名 | 存在时行为 | 不存在时默认值/降级策略
  - 覆盖：vision.md, objectives/, Epic, features/, requirements/, 自主级别, preferred-role, tech-debt-budget, mode(lite), 溯源标记, Release, sync-mapping 等

§2 溢出模式统一定义
  - PF 溢出：触发条件 + 执行步骤 + 规则
  - BR 溢出：触发条件 + 执行步骤 + 规则
  - 通用规则：单向、零摩擦、向后兼容

§3 溯源标记语法（统一定义，cr-format.md 和 project-format.md 共享引用）

§4 通用向后兼容原则
  - 缺失字段默认值规则
  - 新旧格式共存规则
```

### 3B. 各 Schema 文件替换内联兼容条款

操作（逐文件）：
1. `project-format.md`：移除 PF/BR 溢出模式完整描述（~60 行）→引用 compatibility-rules.md §2；替换 18 处内联兼容条款→引用 §1（~-40 行）；精简能力边界矩阵保留核心 5 维度（~-20 行）
2. `cr-format.md`：溯源标记语法改为引用 compatibility-rules.md §3（~-10 行）
3. `pf-format.md`/`br-format.md`/`epic-format.md`：溢出触发条件改为引用（各 ~-10 行）
4. 其余 Schema：每个文件的"向后兼容"段落替换为一行引用（平均每文件 -3 行，约 15 文件）

### 3C. theory.md §12 映射表精简（611 行 → ~530 行）

操作：
- §12 映射表（89 行）压缩为概念分组索引（~30 行）：只列概念类别 + "权威定义在哪个 Schema 文件"，不重复展开实现细节
- §14 SDD 参考保留核心对照表（10 行），移除详细解释段落（~-20 行）

### Phase 3 验证

- `wc -l knowledge/_schema/project-format.md` ≤ 450
- Schema 总行数 ≤ 3,600（含新增的 compatibility-rules.md，基数已从 3,970 增至 ~4,050）
- `bash dev-scripts/validate-all.sh` 全部通过
- 手动验证：/pace-init 初始化→CR 创建→PF 溢出触发→格式合规

---

## Phase 4：同步基础设施完善

**目标**：为所有合法重复建立可追溯的源→派生标记，扩展同步清单。

### 4A. 添加权威源注释标记

在产品层所有合法重复处添加 HTML 注释：`<!-- authority: <权威文件路径> -->`

重点覆盖：
- rules §0 中的命令层级列表 → authority: 各 SKILL.md
- 各 Schema §0 中的概念摘要 → authority: 对应 Schema 详细章节
- theory.md §12 概念索引 → authority: 各 _schema/ 文件

### 4B. 扩展 sync-checklists.md

在现有清单基础上新增：
- **向后兼容策略扩展清单**：新增实体/特性时 → compatibility-rules.md + 对应 Schema + rules §0
- **溢出模式变更清单**：修改溢出条件时 → compatibility-rules.md + project-format.md 树视图格式
- **信号定义变更清单**：修改信号时 → signal-priority.md + signal-collection.md + pace-next/pace-pulse/pace-status 消费方
- **导航规则变更清单**：修改 merged 后管道时 → navigation-guide.md + rules §11 约束声明

### 4C. pulse 信号评估表归位

将 `pulse-procedures-core.md` 中的信号评估表（阈值定义部分，约 40 行）合并入 `knowledge/signal-collection.md`。pulse-procedures-core.md 保留执行逻辑，信号定义引用 knowledge/signal-collection.md。

### Phase 4 验证

- `grep -rn "authority:" rules/ skills/ knowledge/ | wc -l` ≥ 15（覆盖主要合法重复点）
- sync-checklists.md 新增 4 个清单
- `bash dev-scripts/validate-all.sh` 全部通过

---

## 预期总体效果

| 指标 | 优化前 | 优化后 | 变化 |
|------|--------|--------|------|
| rules/ 行数（始终加载） | 580 | ~330 | **-43%** |
| skills/ 文件数（不含 eval workspace） | ~120 | ~87 | **-28%** |
| project-format.md 行数 | 550 | ~430 | **-22%** |
| Schema 总行数（26 文件） | ~4,050 | ~3,600 | -11% |
| theory.md 行数 | 611 | ~530 | -13% |
| 向后兼容散布点 | ~70 处/15+ 文件 | 1 文件集中 | **-97%** |
| 溢出模式散布点 | 4 文件 | 1 文件集中 | -75% |
| 跨 Skill 共享文件异味 | 2 处 | 0 处 | -100% |
| 悬空资产（零引用 knowledge 文件） | 1 处（270 行） | 0 处 | -100% |
| 产品层总行数 | ~21,573 | ~20,000 | -7% |

**核心收益不是行数减少，而是**：
1. **认知入口简化**：rules 瘦身 43% 让每次会话的认知起点更低
2. **维护定位加速**：向后兼容/溢出模式统一后，修改只需改 1 个文件而非 4-15 个
3. **导航成本降低**：碎片 procedures 合并后平均每 Skill 文件数显著下降
4. **同步链路可见**：authority 标记 + 扩展的 sync-checklists 让"还需要同步哪里"有据可查
5. **资产健康度**：消除悬空资产，所有 knowledge 文件都有明确的加载路径

---

## 关键修改文件清单

| 文件 | 涉及 Phase | 操作 |
|------|-----------|------|
| `rules/devpace-rules.md` | P2 | 瘦身 580→~330 行 |
| `knowledge/_schema/project-format.md` | P3 | 重组 550→~430 行 |
| `knowledge/_schema/compatibility-rules.md` | P3 | **新建** ~80 行 |
| `knowledge/navigation-guide.md` | P2 | **新建** ~70 行 |
| `knowledge/role-adaptations.md` | P1 | 合并扩展 24→~40 行 |
| `knowledge/biz-analysis-models.md` | P1 | 建立引用路径（或降级为开发参考） |
| `knowledge/signal-collection.md` | P4 | 扩展 98→~140 行 |
| `knowledge/theory.md` | P3 | 精简 611→~530 行 |
| `.claude/references/sync-checklists.md` | P4 | 扩展（+4 个清单） |
| 涉及合并的 SKILL.md（~10 个） | P1 | 更新路由表引用 |
| ~33 个被合并的 procedures | P1 | **删除** |
| `skills/pace-biz/biz-procedures-output.md` | P1 | **删除**（16 行索引并入 SKILL.md） |
| `skills/pace-role/role-procedures-dimensions.md` | P1 | **删除**（内容并入 knowledge/） |
| `skills/pace-dev/dev-procedures-common.md` | P2 | 扩展（接收 rules §2 移出内容） |
| `knowledge/_schema/cr-format.md` | P3 | 溯源标记引用化（~-10 行） |
| `knowledge/_schema/pf-format.md` | P3 | 溢出引用化（~-10 行） |
| `knowledge/_schema/br-format.md` | P3 | 溢出引用化（~-10 行） |
