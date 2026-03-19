# 空参数引导 procedures

> **职责**：当用户无参数调用 `/pace-biz` 时，扫描项目上下文并给出个性化推荐。

## 触发

`/pace-biz`（无子命令参数）。

## 步骤

### Step 1：读取项目上下文

1. 读取 project.md 的 `mode` 字段判断模式
2. 按模式分支进入 Step 2 或 Step 3

### Step 2：完整模式引导

> 以下检测逻辑与 `knowledge/_signals/signal-priority.md` S16-S19 部分重叠。此处为用户直接引导版本（面向空参数场景），信号版本面向 pace-next/pace-pulse 的自动推荐。两处条件修改时需同步审查。

1. 扫描 opportunities.md 中 `评估中` 的 Opportunity 数量
2. 扫描 epics/ 中 `进行中` 和 `规划中` 的 Epic 数量
3. 扫描 project.md 树视图中未关联 Epic 的"孤立" BR 数量
4. **阶段判断**（内部逻辑，用于选择推荐策略，不直接输出阶段名称给用户）：
   - 无 OPP 且无 Epic/BR → **Sense 阶段**（需求感知期）→ 侧重发现型推荐
   - 有 OPP 未转化 或 有活跃 discover 会话 → **Ideate 阶段**（构思期）→ 侧重转化和探索
   - 有 Epic 未分解 或 有 BR 未分解出 PF → **Structure 阶段**（结构化期）→ 侧重 decompose
   - 有 BR/PF 平均就绪度 < 60% → **Refine 阶段**（精炼期）→ 侧重 refine
   - 距上次 align > 5 天 或 从未执行 → **Validate 阶段**（验证期）→ 侧重 align
   - 大部分 BR/PF 就绪度 >= 80% → **Ready 阶段**→ 推荐移交 /pace-dev
   - 多阶段条件同时满足时，按上述顺序取最早未完成的阶段
5. 推荐优先级（生命周期感知）：
   1. 未评估 Opportunity → `opportunity` 或 `epic`
   2. 规划中 Epic 需分解 → `decompose`
   3. BR/PF 平均就绪度 < 60%（扫描功能树实体的描述/验收标准丰富度）→ `refine` Top-3 最需精炼项
   4. 距上次 align 超过 5 天或从未执行 → `align`
   5. 以上均不满足 → 上下文发现型推荐（import/infer/discover）
6. 附完整子命令列表

**发现型推荐**（上下文感知）：
- 检测到 `.md`/`.txt` 文档（会议纪要、PRD 等）→ 推荐 `import <文件>`
- 检测到 `src/`、`lib/` 等代码目录 → 推荐 `infer`（代码推断）
- 有活跃 Epic 但 BR 为空 → 推荐 `decompose <EPIC-xxx>`
- 其他 → 推荐 `discover`（交互式探索）

### Step 3：lite 模式引导

1. 扫描 project.md 树视图中 OBJ 下的 PF 数量和状态
2. **上下文感知推荐**：同 Step 2 的发现型推荐逻辑
3. 隐藏 opportunity/epic/decompose（Epic→BR 路径），仅展示 lite 兼容子命令
4. 提示：如需 OPP/Epic/BR 能力，可通过 `/pace-init --upgrade-mode` 升级到完整模式
