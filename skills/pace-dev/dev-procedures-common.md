# 推进模式通用规程

> **职责**：推进模式中始终加载的通用规则。其他 procedures 文件按 CR 状态路由加载（见 SKILL.md 执行路由表）。

## §0 速查卡片（路由索引）

| 文件 | 加载条件 | 核心内容 |
|------|---------|---------|
| `dev-procedures-common.md` | 始终 | context.md 生成 · 同步提议 · 决策记录 · 执行透明摘要 |
| `dev-procedures-intent.md` | CR 状态 = `created` | 意图检查点 · 复杂度评估 · 执行计划 · 方案确认 · CR 拆分 |
| `dev-procedures-developing.md` | CR 状态 = `developing` | 步骤隔离 · 漂移检测 · L/XL checkpoint · compact 建议 |
| `dev-procedures-gate.md` | CR 状态 = `verifying` / `in_review` | Gate 1/2 通过反思 |
| `dev-procedures-postmerge.md` | CR 新创建 或 `merged` | 功能发现 · PF 溢出检查 |
| `dev-procedures-defect.md` | CR 类型 = `defect` / `hotfix`（追加） | Defect/Hotfix 创建 · 修复后处理 |

## 上下文加载（进入推进模式时）

> 从 `rules/devpace-rules.md` 迁入。

- 读取 `project.md` 自主级别字段
- 如果 `.devpace/context.md` 存在 → 加载技术约定（编码规范、项目约定、架构约束），确保本次变更遵循项目一致的技术决策
- context.md 不存在时静默跳过，不报错、不提示创建

## 智能 context.md 自动生成

首次推进时（CR created→developing），如果 `.devpace/context.md` 不存在：

1. **静默扫描项目特征**：检查 `tsconfig.json`、`.eslintrc*`、`package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml`、`.editorconfig` 等配置文件
2. **提取技术约定**：从配置文件中提取技术栈、编码规范、项目约定
3. **阈值检查**：提取到 ≥3 条约定 → 自动创建 `context.md`（格式遵循 `knowledge/_schema/auxiliary/context-format.md`）；< 3 条 → 跳过，不创建
4. **教学触发**：首次创建时标记 `context_generated`，附教学："（根据项目配置自动生成了技术约定，推进时会参考这些规则。）"
5. **零摩擦**：不询问用户确认，不阻断推进流程

**与 /pace-init 的关系**：/pace-init Step 6 在初始化时扫描生成 context.md。本逻辑是补充路径——用户跳过 init 或 init 时项目太简单（<3 条），但后续推进时项目已有足够配置文件。两个路径生成的 context.md 格式完全一致。

## 同步关联提议（sync-mapping.md 存在时）

CR 创建完成后，如果 `.devpace/integrations/sync-mapping.md` 存在：

1. 自然语言提议："是否要为 CR-{id} 创建 GitHub Issue 并关联？"
   - 用户同意 → 执行 `/pace-sync create CR-{id}`（复用 sync-procedures §7）
   - 用户拒绝 → 静默跳过
2. 首次提议后标记教学 `sync_create`（每项目仅提议前 3 次，之后静默跳过或自动创建）

**自主级别分化**：
- 辅助级：每次询问
- 标准级：前 3 次询问，之后静默跳过
- 自主级：自动创建并关联（不询问）

**规则**：sync-mapping.md 不存在时完全跳过，不提醒配置同步。

## 决策记录

Claude 在推进过程中自动在 CR 事件表的备注列记录重要决策：

| 记录 | 不记录 |
|------|--------|
| 方案选择及原因（"用 X 而非 Y，因为 Z"） | 常规编码步骤 |
| 发现的边界条件和假设 | 测试通过/不通过（已有 checkbox） |
| 方案调整及原因 | 文件创建/修改（已有 git log） |
| 依赖发现（"发现还需要改 A 才能做 B"） | 质量检查结果（已有 checkbox） |

原则：只记"为什么"不记"做了什么"——做了什么有 git log。

## 执行透明摘要（§13.5 Human Transparency）

pace-dev 完成实现后（Gate 1 通过、代码已提交），**必须**向用户输出结构化变更摘要：

```
📋 变更摘要
- **文件**：[新增 N / 修改 M / 删除 D 个文件]
- **关键决策**：[实现中做出的技术选择，如"选择 X 方案而非 Y，因为..."]
- **质量**：[Gate 反思浓缩，≤20 字]
- **CR 状态**：[当前状态] → [下一状态]
- **注意**：[风险/遗留/需要用户关注的事项，无则省略此行]
```

**规则**：
- 简单 CR（S）：1-2 行即可（文件列表 + 状态变化），省略"质量"行
- 标准/复杂 CR（M/L/XL）：完整 5 项，"质量"行浓缩 Gate 反思为 ≤20 字（如"无新技术债，核心路径测试充分"）
- 不透明动作禁令：写入 .devpace/ 的任何文件必须在摘要中列出——用户不应在不知情的情况下发现文件被修改

## 推进中探索连续模式

> 从 `rules/devpace-rules.md` 迁入。

推进模式中检测到探索意图时，暂停推进允许自由讨论，讨论结束后无缝恢复：

**检测信号**："让我想想""还有更好方案吗""等一下""先分析一下""对比一下"
**行为**：
1. 暂停推进（不退出推进模式，CR 保持当前状态）
2. 进入类似探索模式的自由讨论——但 IR-1 仍然生效（不修改 .devpace/）
3. 用户说"继续做""好的就这样""开始"→ 直接恢复推进，无需重新 opt-in
4. 讨论中达成的新决策/约束 → 自动更新 CR 意图 section（恢复推进时写入）

**规则**：
- 不触发新 CR 创建——仍绑定当前 CR
- 不重置状态机——恢复后从暂停点继续
- 讨论内容溯源标记 `<!-- source: claude, 从推进中探索讨论提取 -->`

不确定时问用户："要正式开始改代码，还是先看看？"

## 连续推进模式（--batch）

当用户使用 `--batch` 参数或说"连续做"/"批量推进"时，启用连续推进模式：

### 进入条件

1. 当前有活跃迭代（`iterations/current.md` 存在）
2. 迭代内有 ≥2 个未开始的 PF

### 执行流程

1. 读取 `current.md`，按优先级排列未开始的 PF
2. 对每个 PF 依次执行标准 pace-dev 流程（创建 CR → 开发 → Gate 1 → Gate 2）
3. **Gate 3 延迟**：S 复杂度的 CR 通过 Gate 2 后不立即进入 Gate 3 审批，而是标记为 `batch_review_pending`（CR 状态仍为 `in_review`）
4. L/XL 复杂度的 CR 仍立即进入 Gate 3 审批（不延迟）
5. 每完成一个 PF 后，输出 1 行进度：`[N/M] PF-xxx 已完成 Gate 2，等待统一审批`

### 批量审批

所有 S 复杂度 PF 完成 Gate 2 后，一次性展示批量审批列表：

```
批量审批（共 N 个 S 复杂度变更）：
1. CR-xxx：[标题] — Gate 2 ✅
2. CR-xxx：[标题] — Gate 2 ✅
3. CR-xxx：[标题] — Gate 2 ✅

全部批准 | 逐个审批 | 取消
```

- "全部批准" → 全部标记为 merged，执行连锁更新
- "逐个审批" → 退出 batch 模式，逐个走标准 Gate 3
- 用户可选择性排除："批准除了 2 号"

### 退出条件

- 迭代内无更多未开始 PF
- 用户说"停"/"够了"/"先到这"
- 遇到 L/XL 复杂度 PF（完成该 PF 的 Gate 3 后询问是否继续 batch）
