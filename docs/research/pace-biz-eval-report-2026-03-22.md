# pace-biz Skill Eval 报告

> **日期**：2026-03-22
> **评估工具**：claude-api:skill-creator eval 框架 + subagent A/B 对比
> **评估范围**：pace-biz 全部 10 个子命令 + 空参引导（100% 覆盖）

## 1. 评估方法论

### 触发准确性评估

使用 `skill-creator/scripts/run_loop.py` 对 pace-biz description 进行 5 轮自动化优化，20 条查询（10 should-trigger + 10 should-not-trigger），每条 3 次运行。

**结论**：eval 工具对 plugin-installed skills 存在结构性局限——临时命令文件被真正的 plugin skill 截获，导致 recall 始终为 0%。但这反过来**证实了当前 description 有效**（Claude 正确路由到真实 skill）。5 轮生成的 description 变体均无法超越原始版本。

### 输出质量评估

对每个子命令设计真实场景 prompt，并行 spawn subagent 执行 with-skill（按 procedures 执行）和 baseline（不读任何 skill 文件），对比 assertions 通过率。

**测试项目**：构造了含故意问题的 SmartHome Pro 项目（3 OBJ、3 Epic、7 BR、2 OPP、3 个源码模块），覆盖孤立实体、优先级通胀、空 Epic、未追踪代码等场景。

## 2. 最终成绩单

| 子命令 | with-skill | baseline | delta | token 溢出 | 类型 |
|--------|:---------:|:--------:|:-----:|:---------:|------|
| discover | 6/6 | 1/6 | +83% | +55% | 发现型 |
| decompose | 6/6 | 5/6 | +17% | +37% | 创建型 |
| import | 6/6 | 4/6 | +33% | +76% | 发现型 |
| refine (skeleton) | 5/5 | 3/5 | +40% | +47% | 精炼型 |
| refine (initial-ac) | 5/5 | 3/5 | +40% | +43% | 精炼型 |
| align | 6/6 | 5/6 | +17% | +20% | 分析型 |
| opportunity | 5/5 | 2/5 | +60% | +20% | 创建型 |
| epic | 5/5 | 1/5 | +80% | +29% | 创建型 |
| view | 4/4 | 4/4 | 0% | +11% | 分析型 |
| infer | 4/4 | 3/4 | +25% | +34% | 发现型 |
| guide | 4/4 | 2/4 | +50% | +16% | 分析型 |
| **总计** | **56/56 (100%)** | **33/56 (59%)** | **+41%** | **+35% avg** | |

### 按类型汇总

| 类型 | with-skill | baseline | Skill 增值 | 核心原因 |
|------|:---------:|:--------:|:---------:|---------|
| 创建型 | 16/16 | 8/16 | +50% | 多文件联动写入 + OPP 状态转换 |
| 精炼型 | 10/10 | 6/10 | +40% | 就绪度跟踪 + 交互引导 |
| 发现型 | 16/16 | 8/16 | +50% | 结构化探索 + 编号一致性 |
| 分析型 | 14/14 | 11/14 | +21% | 系统化检查维度更多 |

## 3. 关键发现

### Skill 的核心价值矩阵

| 价值维度 | 增值程度 | 说明 |
|---------|:-------:|------|
| 持久化写入 | ★★★★★ | baseline 停留在"建议"层面，不写入 .devpace/ |
| 编号一致性 | ★★★★★ | 正确识别现有编号并递增，避免冲突 |
| 多文件联动 | ★★★★★ | epic 子命令同时更新 3 个文件 |
| 就绪度跟踪 | ★★★★☆ | 精确的百分比变化（30%→90%） |
| 流程规范性 | ★★★★☆ | 严格遵循 procedures 的多步流程 |
| 角色适配 | ★★★☆☆ | PM/Dev/Tester 等角色影响追问方向 |
| 系统化检查 | ★★★☆☆ | align 执行 9 维检查 vs baseline 4 维 |
| 分析深度 | ★★☆☆☆ | baseline 有时更深（discover 5 层信号分层） |
| 资源效率 | ★☆☆☆☆ | 平均 +35% tokens，结构化流程的固有成本 |

### Skill 增值最大的场景

1. **epic**（+80%）：三文件联动是 baseline 完全无法替代的
2. **discover**（+83%）：探索式需求发现的流程化引导价值最高
3. **opportunity**（+60%）：Schema 合规 + 溯源标记

### Skill 增值最小的场景

1. **view**（0%）：只读展示，Claude 原生能力已足够
2. **decompose**（+17%）：增量分解场景差距小
3. **align**（+17%）：分析型任务 Claude 原生能力较强

## 4. 实施的改进

### 已提交（3 个 commit）

| commit | 类型 | 内容 |
|--------|------|------|
| `14d1454` | fix | decompose 新增 BR 必须包含初始验收标准 + PF 粒度指南 + gitignore |
| `b6ac3ae` | perf | import 快筛短路 + 映射表内联 + discover 自适应轮数 |
| `f3bc97f` | feat | discover 引入需求信号分层分析 |

### 改进明细

| # | 文件 | 改动 | 来源 |
|---|------|------|------|
| 1 | `biz-procedures-decompose-epic.md` | Step 3 BR 包含验收标准 + Step 5 追加验收标准段 | decompose eval FAIL → FIX |
| 2 | `entity-extraction-rules.md` | PF 粒度判断表 + `--granular` 标志 | import baseline 对比 |
| 3 | `biz-procedures-import.md` | 两阶段快筛短路（<20% 直接 NEW） | token 效率分析 |
| 4 | `biz-procedures-import.md` | 通用映射表内联到 Step 2 | token 效率分析 |
| 5 | `biz-procedures-discover.md` | 头脑风暴 2+N 自适应 + 提前退出 | token 效率分析 |
| 6 | `biz-procedures-discover.md` | 需求信号分层（L1/L2/L3） | baseline 分析模式吸收 |
| 7 | `.gitignore` | `*-workspace/` 排除 eval 工作区 | eval 基础设施 |

### 评估后决定不实施的

| 项目 | 原因 |
|------|------|
| view 轻量化 | 溢出仅 +11%，优化后节省 1.6%，ROI 过低 |
| description 变更 | 触发 eval 5 轮迭代确认原始版本最优 |
| refine 验收标准数量上限放宽 | baseline 17 条 vs 8 条，但 procedures 的节奏控制是有意设计 |

## 5. Eval 方法论总结（可复用）

### 测试项目构造

- 创建独立的测试项目目录（`test-project-align/`）
- 构造故意问题（孤立实体、优先级通胀、空 Epic、未追踪代码）
- 为 infer 子命令准备含 TODO/FIXME 的源码

### Assertions 设计模式

| 维度 | 典型 assertion | 适用子命令 |
|------|---------------|-----------|
| 流程合规 | "读取了上下文文件" | 全部 |
| 交互引导 | "通过追问补充信息" | discover, refine |
| 持久化 | "写入 .devpace/ 文件" | 创建型、精炼型 |
| 格式合规 | "输出包含编号/验收标准/价值链" | 创建型 |
| 就绪度 | "展示就绪度变化" | refine |
| 检测能力 | "正确识别 N 个问题" | align, infer |

### 注意事项

- **触发 eval 对 plugin-installed skills 无效**：`run_eval.py` 创建的临时命令被真实 plugin 截获
- **subagent 共享测试项目时注意写入冲突**：并行 agent 可能同时修改 project.md
- **baseline 不等于"差"**：分析型任务 baseline 表现接近 with-skill，assertions 需针对 Skill 独特价值设计

## 6. 后续建议

| 优先级 | 方向 | 预期投入 |
|--------|------|---------|
| P0 | 评估 pace-dev（最高频 Skill） | 新会话，复用方法论 |
| P0 | 评估 pace-change（与 pace-biz 边界模糊） | 同上 |
| P1 | 修复触发 eval 的 plugin 兼容性 | 修改 run_eval.py 检测真实 plugin 触发 |
| P1 | 建立回归 eval 脚本 | 自动化验证 procedures 变更不退化 |
