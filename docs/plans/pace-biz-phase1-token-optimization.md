# pace-biz 优化：分阶段执行方案

> **日期**：2026-03-25
> **来源**：全新视角审视 pace-biz 实现，发现 16 个优化点
> **状态**：待审查

## Context

pace-biz 是 devpace 最大的 Skill（12 文件、10 子命令、引用 10 个 Schema）。全新视角审视发现 16 个优化点，按 P0/P1/P2/P3 分为 4 个阶段，逐阶段审查执行。

## 阶段总览

| 阶段 | 主题 | 优化项 | 预期收益 |
|------|------|--------|---------|
| **Phase 1** | Token 瘦身（低成本高回报） | T2 + T3 + O2 | 减少 ~170 行重复/冗余，缓解 Token 溢出 |
| Phase 2 | 文件整合与流程 DRY | O1 + P2 + T1 | 减少文件数，统一写入模式 |
| Phase 3 | UX 与路由优化 | F1 + I1 + P3 | 改善用户体验，降低 fork 开销 |
| Phase 4 | 深度优化（按需） | P1 + F2 + F3 + F4 + I2 + I3 + O3 | 流程自适应、边界优化 |

## 完整诊断索引（16 项）

| # | 维度 | 诊断 | 优化方向 | 阶段 |
|---|------|------|---------|------|
| T2 | Token | 角色适配 7 处重复 | 提取为引用模式 | Phase 1 |
| O2 | 文件组织 | Schema 引用链过长 | 关键字段内联摘要 | Phase 1 |
| T3 | Token | 容错/降级模式重复 | 提取通用模式到公共层 | Phase 1 |
| P2 | 流程 | 写入模式 8 处重复 | 提取共享写入规程 | Phase 2 |
| O1 | 文件组织 | guide 独立文件必要性低 | 合并入 SKILL.md | Phase 2 |
| T1 | Token | procedures 信息密度不均 | 压缩输出模板和规则表 | Phase 2 |
| F1 | 功能 | discover/import/infer 入口分离 | 统一"补充需求"入口 | Phase 3 |
| I1 | 实现 | 轻量子命令 fork 开销 | 按复杂度选择 fork/inline | Phase 3 |
| P3 | 流程 | 下游引导模板固定 | 基于产出动态生成 | Phase 3 |
| P1 | 流程 | discover 4 阶段刚性 | 自适应深度 | Phase 4 |
| F2 | 功能 | refine vs modify 边界模糊 | 入口意图识别 | Phase 4 |
| F3 | 功能 | align 9 项检查可能过全 | 按项目成熟度裁剪 | Phase 4 |
| F4 | 功能 | view vs status tree 重叠 | 展示维度差异化 | Phase 4 |
| I2 | 实现 | Epic prompt Hook 价值存疑 | 评估实际触发率 | Phase 4 |
| I3 | 实现 | import 语义精判不确定性 | 收窄阈值区间 | Phase 4 |
| O3 | 文件组织 | guide/signal-priority 重叠 | 统一条件定义源 | Phase 4 |

---

## Phase 1：Token 瘦身（本阶段详细方案）

**目标**：以最小改动减少 procedures 中的重复内容和不必要的 Schema 读取，直接降低 Token 消耗。

### 1.1 T2：角色适配段去重（7 个文件）

**问题**：discover、decompose-epic、decompose-br、refine、view、import、infer 共 7 个 procedures 各自内联了 5-8 行角色适配段，总计 ~42 行重复。已有 `knowledge/role-adaptations.md` 作为通用定义。

**方案**：

对每个 procedures 的角色适配段，分三种情况处理：

| 情况 | 处理方式 | 涉及文件 |
|------|---------|---------|
| 有子命令特有适配 | 保留 1 行引用 + 仅列差异项 | discover, decompose-epic, view, import |
| 无特有适配（默认无追加） | 完全删除角色适配段 | decompose-br, refine（Dev/PM/Ops 默认无追加的角色已在 role-adaptations.md 覆盖） |
| 仅 Biz/Tester 有追加 | 1 行引用 + 2 行差异 | infer |

**改造前（以 decompose-br 为例，6 行）**：
```markdown
**角色追加考量**（通用维度见 `knowledge/role-adaptations.md`，读取公共前置传入的 preferred-role）：
- Dev -> 提示考虑"这个 PF 的实现复杂度？有架构影响吗？"
- Tester -> 提示考虑"边界条件有哪些？需要什么测试数据？"
- Biz Owner/PM/Ops/Dev(默认) -> 无追加（零改变）
```

**改造后（1 行）**：
```markdown
**角色适配**：通用维度见 `role-adaptations.md`。Dev 追加复杂度评估，Tester 追加边界条件追问。
```

**涉及文件**（7 个）：
- `skills/pace-biz/biz-procedures-discover.md`
- `skills/pace-biz/biz-procedures-decompose-epic.md`
- `skills/pace-biz/biz-procedures-decompose-br.md`
- `skills/pace-biz/biz-procedures-refine.md`
- `skills/pace-biz/biz-procedures-view.md`
- `skills/pace-biz/biz-procedures-import.md`
- `skills/pace-biz/biz-procedures-infer.md`

**预期减少**：~35 行

---

### 1.2 T3：容错/降级模式提取到 SKILL.md 公共层

**问题**：8 个写入子命令各自包含降级模式表和容错表，其中 3 个条目在多个文件中完全相同：
- ".devpace/ 不存在 → 引导 /pace-init"（8 个文件）
- "project.md 是桩 → 正常运行"（5 个文件）
- "编号冲突 → 重新扫描最大编号"（4 个文件）

**方案**：

**Step A**：在 SKILL.md 的"流程 → 所有子命令的公共前置"章节末尾追加通用容错段：

```markdown
### 通用容错（所有子命令共享）

| 异常 | 处理 |
|------|------|
| .devpace/ 不存在 | 引导 /pace-init |
| project.md 是桩（无 OBJ 定义） | 正常运行；写入子命令填充桩内容，分析子命令简化报告 |
| 编号冲突 | 重新扫描确认最大编号后分配 |
| requirements/ 或 epics/ 目录不存在 | 触发时自动创建 |

> 各 procedures 的容错/降级表仅列本子命令特有的异常处理。
```

**Step B**：逐个 procedures 删除通用容错条目，仅保留特有项。

**改造示例（opportunity 容错表）**：

改造前（4 行）：
```markdown
| .devpace/ 不存在 | 引导 /pace-init |
| opportunities.md 格式损坏 | 在文件末尾追加，不修复已有内容 |
| 用户未提供描述 | 询问：请描述这个业务机会 |
```

改造后（2 行，删除通用项）：
```markdown
| opportunities.md 格式损坏 | 在文件末尾追加，不修复已有内容 |
| 用户未提供描述 | 询问：请描述这个业务机会 |
```

**涉及文件**（9 个）：
- `skills/pace-biz/SKILL.md`（新增公共容错段）
- `skills/pace-biz/biz-procedures-opportunity.md`
- `skills/pace-biz/biz-procedures-epic.md`
- `skills/pace-biz/biz-procedures-decompose-epic.md`
- `skills/pace-biz/biz-procedures-decompose-br.md`
- `skills/pace-biz/biz-procedures-discover.md`
- `skills/pace-biz/biz-procedures-import.md`
- `skills/pace-biz/biz-procedures-infer.md`
- `skills/pace-biz/biz-procedures-refine.md`

**预期减少**：~40 行（8 文件 × ~5 行通用项）

---

### 1.3 O2：Schema 引用链优化（Top-3 高消耗子命令）

**问题**：eval 数据显示 import +76%、discover +55%、decompose +37% 的 Token 溢出，主因是 procedures 引用多个 Schema 文件导致 agent 需要链式读取。

**方案**：对 Token 消耗 Top-3 的子命令，在 procedures 中内联 Schema 核心字段的**执行摘要**（3-5 行），并将 Schema 引用标记为"完整定义（边界情况参考）"而非"必读"。

**原则**：
- Schema 仍是格式权威源（IA-6 不违反）
- procedures 中的摘要是"执行时足够用的最小信息集"（IA-5 按需加载）
- 摘要行前标注 `> 摘要自 xxx-format.md §yyy` 保持溯源

#### 1.3a import（当前引用 4 个 Schema）

当前引用链：
```
biz-procedures-import.md
├── knowledge/_schema/entity/br-format.md §内联格式
├── knowledge/_schema/entity/pf-format.md §内联格式
├── knowledge/_schema/auxiliary/merge-strategy.md（阈值+分类框架）
└── knowledge/_extraction/entity-extraction-rules.md（提取映射表）
```

优化：
- `br-format §内联格式` 和 `pf-format §内联格式` → 内联 2 行摘要（`BR-xxx：[名称] \`Px\`` 和 `PF-xxx：[名称]（[用户故事]）→ (待创建 CR)`），标注"完整格式含溢出规则见 br-format.md"
- `merge-strategy.md` → 四分类定义（NEW/DUPLICATE/ENRICHMENT/CONFLICT）和阈值默认值已在 Step 3 内联，只需删除"完整阈值范围见 merge-strategy.md"这个必读引用，改为"详细边界判断见 merge-strategy.md（可选）"
- `entity-extraction-rules.md` → Step 2 的通用提取规则表已内联了速查版，保持现状即可

**预期效果**：agent 执行 import 时减少 2 次 Schema 文件读取

#### 1.3b discover（当前引用 3 个 Schema）

当前引用链：
```
biz-procedures-discover.md
├── knowledge/_schema/entity/obj-format.md
├── knowledge/_schema/process/scope-discovery-format.md
└── knowledge/_extraction/entity-extraction-rules.md
```

优化：
- `obj-format.md` → Step 1 中 OBJ 候选仅需知道 OBJ 编号格式（`OBJ-xxx`）和 6 类型，内联 1 行即可
- `scope-discovery-format.md` → 已在各 Step 描述了中间状态写入格式，引用可降级为"可选参考"
- `entity-extraction-rules.md` → Step 2 已内联速查规则，保持现状

**预期效果**：agent 执行 discover 时减少 1-2 次 Schema 文件读取

#### 1.3c decompose-epic（当前引用 2 个 Schema + 1 个 knowledge）

当前引用链：
```
biz-procedures-decompose-epic.md
├── knowledge/_schema/entity/br-format.md §内联格式
└── knowledge/_extraction/prioritization-methods.md
```

优化：
- `br-format §内联格式` → 内联 1 行摘要（Step 4 已有格式示例 `BR-xxx：[名称] \`Px\``），将引用降级为可选
- `prioritization-methods.md` → Step 3 已内联了 VxE 默认方法，`--moscow` 和 `--kano` 作为可选标志触发时才需要读取完整文件

**预期效果**：agent 执行 decompose-epic 时默认路径减少 1 次 Schema 文件读取

**涉及文件**（3 个）：
- `skills/pace-biz/biz-procedures-import.md`
- `skills/pace-biz/biz-procedures-discover.md`
- `skills/pace-biz/biz-procedures-decompose-epic.md`

---

## Phase 1 验证

1. **分层完整性**：`bash dev-scripts/validate-all.sh` 确认无回归
2. **Schema 权威性**：`grep -r "摘要自" skills/pace-biz/` 确认所有内联摘要都标注了溯源
3. **功能不变**：逐个检查修改的 procedures 中步骤逻辑未变，仅压缩了重复内容
4. **plugin 加载**：`claude --plugin-dir ./` 确认无加载错误

---

## 后续阶段预告（待审查）

### Phase 2：文件整合与流程 DRY
- O1：guide 合并入 SKILL.md
- P2：提取共享写入规程到 `_guides/biz-write-pattern.md`
- T1：压缩 view/infer/align 的输出模板和规则表

### Phase 3：UX 与路由优化
- F1：统一 discover/import/infer 的"补充需求"入口
- I1：轻量子命令（opportunity/view/guide）改为 inline 执行
- P3：下游引导改为动态生成

### Phase 4：深度优化（按需）
- P1：discover 自适应深度
- F2：refine 入口意图识别
- F3：align 按项目成熟度裁剪检查项
- 其他 P3 项
