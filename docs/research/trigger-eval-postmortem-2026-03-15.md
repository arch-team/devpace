# Trigger Eval 自动化踩坑复盘

> 日期：2026-03-15 | 耗时：~4 小时 | 状态：基础设施完成，正面检测受上游限制

## 1. 背景

`make eval-trigger-one S=pace-dev` 能运行但 18/18 正面用例全部失败（trigger_rate=0）。最初假设的根因是 skill-creator 的 `parse_skill_md()` 解析空 `name:` 字段导致临时 command 名畸形。

目标：修复基础设施 + 建立 eval→fix→regress→CI 自动化体系。

## 2. 发现的根因链（7 层）

调查过程中逐层剥开了 **7 个叠加问题**，而非原计划假设的 1 个：

| # | 问题 | 发现方式 | 修复 |
|---|------|---------|------|
| 1 | SKILL.md 无 `name:` 字段 → 文件名 `-skill-<uuid>` | 读 `utils.py:parse_skill_md()` 源码 | shim 注入 `name:` |
| 2 | `eval-runner.sh` 做 `cd "$sc_root"` → `find_project_root()` 解析到 `~/.claude` 而非 devpace | 运行 `find_project_root()` 打印结果 | PYTHONPATH 替代 cd |
| 3 | 全局 plugin 的 skill 与测试 command 竞争 | 观察 `claude -p` init 输出的 skills 列表 | `claude plugin disable --all` |
| 4 | MCP 服务器初始化 ~36s > 默认 timeout 30s | `time claude -p "say hi"` 测量 | timeout 增至 90s |
| 5 | `-p` 模式默认权限阻断工具调用 | 观察 `claude -p` 挂起行为 | `--dangerously-skip-permissions` |
| 6 | 用户 `~/.claude/CLAUDE.md` 中 SuperClaude 框架强制 brainstorming 路由 | debug 脚本捕获 Skill 调用内容为 `superpowers:brainstorming` | 临时 mv CLAUDE.md |
| 7 | `run_eval.py:141` 对首个非 Skill tool_use 立即 `return False`；内置工具不受 `--allowedTools` 控制 | debug 脚本捕获完全隔离环境下 Claude 仍先调 ToolSearch/Glob/Bash | **上游限制，无法绕过** |

## 3. 关键调试时刻

### 3.1 Gate 测试的误导

原计划有一个 Step 0 Gate："用 bash 快速验证 name 注入假设，3 分钟完成"。实际执行后发现注入 name 后仍然 0/2 正面通过。**如果严格执行 gate 的 "全 0 → 停下重新分析" 规则**，反而成为了深入调查的转折点。

教训：**Gate 机制有效，但要为 "gate 失败后的调查" 预留时间预算。**

### 3.2 嵌套 `claude -p` 的不可靠性

从 Claude Code 会话内运行 `claude -p` 存在严重的管道缓冲问题：
- Bash 工具管道到 Python 解析器 → 持续超时
- 直接文件重定向 → 也超时
- ProcessPoolExecutor（run_eval.py 方式）→ 反而正常工作

原因：Claude Code 的 Bash 工具对 stdout 的处理与原生 shell 不同。`run_eval.py` 用 `subprocess.Popen` + `select.select` + `os.read` 做非阻塞读取，绕过了缓冲问题。

教训：**调试 `claude -p` 行为时，用 Python 脚本（Popen+select）而非 Bash 管道。**

### 3.3 `--allowedTools` 的边界

`--allowedTools "Skill"` 只控制用户定义工具（MCP tools 等），**不控制 Claude Code 内置工具**（ToolSearch、Glob、Bash、Read、Edit 等）。这是 CLI 的设计决策而非 bug——内置工具是 Claude Code 运行的基础。

发现方式：在完全隔离环境（无 CLAUDE.md、无插件）中用 debug 脚本观察到 Claude 仍然调用了 ToolSearch、Glob、Bash。

教训：**不要假设 CLI 标志的行为——先用最小实验验证。**

### 3.4 真正的阻塞点在上游

`run_eval.py` 第 133-141 行的检测逻辑：

```python
if cb.get("type") == "tool_use":
    tool_name = cb.get("name", "")
    if tool_name in ("Skill", "Read"):
        pending_tool_name = tool_name  # 开始追踪
    else:
        return False  # ← 首个非 Skill/Read 工具 → 立即放弃
```

这个 early-exit 设计假设 Claude 的**第一个工具调用**就是 Skill。但在实际环境中，Claude 总是先调用 ToolSearch（发现延迟加载的工具）或 Glob/Bash（探索项目），然后才考虑 Skill 路由。

正确的检测应该：扫描所有 turn 的所有 content block，找到任何包含目标 command 名的 Skill 调用即判定为触发。

## 4. 最终交付物

### 4.1 shim 基础设施（完整可用）

```
eval/
├── shim.py          # 核心适配层（trigger/loop/regress/baseline/smoke）
├── eval-runner.sh   # 路由入口（从 dev-scripts 迁移）
└── apply.py         # description diff/apply
```

Makefile 新增 18 个 target：trigger-one/trigger/smoke/deep/fix/fix-diff/fix-apply/regress/baseline-save/diff/save-all 等。

### 4.2 实际验证结果

| 指标 | 结果 |
|------|------|
| 负面用例（should_trigger=false） | **17/17 通过 (100%)** |
| 正面用例（should_trigger=true） | 0/18 通过 (0%) — 上游限制 |
| 基础设施稳定性 | 35 条查询全部完成运行，不再超时/挂起 |
| 结果持久化 | latest.json + history/ 正确生成 |
| 环境恢复 | 插件和 CLAUDE.md 在 finally 中正确恢复 |

## 5. 经验教训

### 5.1 递归调试的成本

原计划预估 Phase 1（核心修复）约 1-2 小时。实际花了 ~4 小时，因为每修一层都揭露下一层：

```
name 注入 → 还是 0
  → 调查 project_root → 还是 0
    → 调查 plugin 竞争 → 还是 0
      → 调查 timeout → 还是 0
        → 调查权限阻断 → 还是 0
          → 调查 CLAUDE.md → 还是 0
            → 最终定位到上游检测逻辑 → 无法绕过
```

教训：**对涉及多进程+外部 CLI+模型行为的集成问题，调试时间应按 3-5x 预估。**

### 5.2 "修了一个但没好" 的陷阱

每一层修复在逻辑上都是正确的（name 确实需要注入、project_root 确实指错了地方）。但因为是叠加问题，单独修任何一个都看不到效果。这容易导致：
- 怀疑自己的修复是否正确（实际上是正确的）
- 反复尝试同一层面的变体（浪费时间）
- 过早放弃正确方向

教训：**当修复逻辑确认正确但效果未显现时，应假设存在更深层阻塞，而非反复调整当前层。**

### 5.3 可观测性是第一优先级

突破性进展来自两个观测手段：
1. `time claude -p "say hi"` — 一行命令揭示 36s 初始化时间
2. `_debug_single_query.py` — 用 Popen+select 捕获 stream 事件

如果一开始就写好 debug 工具而不是反复用 Bash 管道试错，可以节省至少 1 小时。

教训：**对黑盒系统（`claude -p`），先投资 10 分钟建观测工具，再开始修复。**

### 5.4 环境隔离的完整性

需要隔离的不只是 "明显的依赖"（plugins），还包括：
- 用户级配置（`~/.claude/CLAUDE.md`）
- 框架级指令（SuperClaude 的 brainstorming 强制指令）
- CLI 内置行为（ToolSearch 不受 allowedTools 控制）

教训：**自动化测试的环境隔离必须是 "全部白名单" 而非 "逐个黑名单"。**

### 5.5 最终根因：`claude -p` 不触发 skill 自动路由

在尝试了 7 层环境修复 + 自建检测逻辑 + 3 种 project 隔离策略后，最终确认：

**`claude -p` 是单轮无状态 API，不复现交互模式的 skill 自动触发管线。**

在交互式 Claude Code 会话中，`using-superpowers` 等系统 skill 在会话开始时被激活，其 "MUST invoke skills before ANY response" 指令持续整个会话，驱动 Claude 对每个用户消息检查 skill 匹配。而 `-p` 模式跳过了这个启动流程——每个查询是独立的，没有持久化的 skill 路由上下文。

这意味着：**基于 `claude -p` 的 trigger eval 是不可行的设计**，无论检测逻辑多么完善。skill-creator 的 run_eval.py 能工作的前提是一个极简环境（无 plugin、无 system prompt），而在生产级 Claude Code 环境中这个前提不成立。

教训：**在投入 N 小时修复 "怎么做" 之前，先花 30 分钟验证 "能不能做"。**

## 6. 后续行动

| 优先级 | 行动 | 状态 |
|--------|------|------|
| P0 | 向 skill-creator 提 issue：`claude -p` 不触发 skill 自动路由，trigger eval 需要交互模式 API | 待提交 |
| P1 | 探索替代方案：Claude Code SDK 的 Agent API 是否支持 skill 触发检测 | 待调研 |
| P2 | 行为 eval（evals.json）不依赖触发检测，优先完善这条路径 | 可立即推进 |
| P3 | Phase 6 CI 集成（等 P0/P1 有结论后） | 阻塞中 |
