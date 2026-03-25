# pace-sync Skill 评估 Benchmark — Iteration 1

## 总览

| 指标 | with-skill | baseline | Delta |
|------|-----------|----------|-------|
| 平均输出长度 | 147 行 | 68 行 | +116% |
| Assertion 通过率 | 17/17 (100%) | 4/17 (24%) | +76pp |
| 流程遵循度 | 完整 | 无 |
| 操作语义使用 | 全部 | 无 |
| 多实体类型支持 | Epic/BR/PF/CR | 仅 CR 或无结构 |

## Eval 1: 智能同步首次 (smart-sync-first-time)

### with-skill 断言评分

| Assertion | Pass | Evidence |
|-----------|:----:|---------|
| a1-script-usage: 提及运行脚本 | ✅ | 明确提及 `compute-sync-diff.mjs`，展示脚本输出数据 |
| a2-entity-coverage: 包含 Epic/BR/PF | ✅ | 列出 4 Epic + 6 BR + 8 PF = 18 实体 |
| a3-hierarchy-order: Epic→BR→PF→CR 顺序 | ✅ | 按"第一层 Epic → 第二层 BR → 第三层 PF"分层创建 |
| a4-user-confirmation: 摘要+确认 | ✅ | 呈现 18 个 new 实体摘要后提供三选项 |
| a5-output-format: 表格格式 | ✅ | 完整表格含 实体/类型/外部链接/操作/结果 |
| a6-sub-issue: 提及 sub-issue | ✅ | "14 个 sub-issue 关系已建立，2 个无层级关联" |

**Pass: 6/6 (100%)**

### baseline 断言评分

| Assertion | Pass | Evidence |
|-----------|:----:|---------|
| a1-script-usage | ❌ | 未使用任何脚本 |
| a2-entity-coverage | ⚠️ | 列出了实体但无结构化分类 |
| a3-hierarchy-order | ❌ | 无层级创建顺序概念 |
| a4-user-confirmation | ❌ | 直接给出操作建议，无确认流程 |
| a5-output-format | ❌ | 无表格输出 |
| a6-sub-issue | ❌ | 未提及 sub-issue |

**Pass: 0/6 (0%)**

### 关键差异

- **with-skill** 运行脚本获取精确实体清单（18个），按层级创建并建立 sub-issue
- **baseline** 只能给出泛泛的操作建议，无法精确列出实体或控制创建顺序

---

## Eval 2: 增量同步 (incremental-sync-changes)

### with-skill 断言评分

| Assertion | Pass | Evidence |
|-----------|:----:|---------|
| a1-incremental-detection: 区分 changed/unchanged | ✅ | 明确: "3 changed, 4 unchanged, 16 new" |
| a2-hash-based: 基于 hash 检测 | ✅ | 运行 compute-sync-diff.mjs 脚本计算 hash diff |
| a3-selective-push: 仅推送变更实体 | ✅ | 用户选"仅同步已关联"后只推送 3 个 changed |
| a4-summary-before-action: 先摘要再执行 | ✅ | 步骤 3 呈现摘要 → 步骤 4 询问 → 步骤 5 执行 |
| a5-multi-entity-type: 包含非 CR 类型 | ✅ | EPIC-001 状态变化作为 changed 实体推送 |

**Pass: 5/5 (100%)**

### baseline 断言评分

| Assertion | Pass | Evidence |
|-----------|:----:|---------|
| a1-incremental-detection | ❌ | 无 changed/unchanged 区分机制 |
| a2-hash-based | ❌ | 未使用 hash 检测 |
| a3-selective-push | ⚠️ | 建议全量推送，无选择性 |
| a4-summary-before-action | ⚠️ | 有简单描述但非结构化摘要 |
| a5-multi-entity-type | ❌ | 仅关注 CR |

**Pass: 0/5 (0%)**

### 关键差异

- **with-skill** 精确识别 3 个 changed 实体（EPIC-001 + 2 CR），每个附带 gh CLI 命令和语义 Comment
- **baseline** 无法进行增量检测，只能建议全量操作

---

## Eval 3: Link Epic (link-epic-to-existing-issue)

### with-skill 断言评分

| Assertion | Pass | Evidence |
|-----------|:----:|---------|
| a1-entity-id-parse: 识别 EPIC-001 为 Epic | ✅ | "前缀 EPIC- 匹配 Epic 类型" |
| a2-entity-verify: 验证实体文件存在 | ✅ | 读取 `.devpace/epics/EPIC-001.md` 确认 |
| a3-external-link-field: 写入外部关联 | ✅ | 在文件中追加 `**外部关联**: [github#10](URL)` |
| a4-sync-mapping-update: 更新关联记录 | ✅ | 追加 `EPIC-001 | github#10 | 时间戳` 行 |
| a5-gh-cli-command: gh issue view 验证 | ✅ | `gh issue view 10 --json state,labels,title,locked` |
| a6-confirmation-output: 确认信息 | ✅ | `EPIC-001 ↔ 外部实体 #10 ... 已关联` |

**Pass: 6/6 (100%)**

### baseline 断言评分

| Assertion | Pass | Evidence |
|-----------|:----:|---------|
| a1-entity-id-parse | ⚠️ | 读取了文件但无显式类型识别 |
| a2-entity-verify | ✅ | 读取了 EPIC-001.md |
| a3-external-link-field | ⚠️ | 自创格式 `## 外部关联` 而非规范格式 |
| a4-sync-mapping-update | ❌ | 未提及 sync-mapping.md |
| a5-gh-cli-command | ❌ | 未验证外部 Issue 存在 |
| a6-confirmation-output | ✅ | 有确认但格式非规范 |

**Pass: 2/6 (33%)**

### 关键差异

- **with-skill** 完整 8 步流程（ID解析→实体验证→外部验证→写入关联→类型标签→状态标签→mapping更新→确认）
- **baseline** 仅简单编辑文件添加 Markdown 段落，无 sync-mapping 概念

---

## 综合分析

### Skill 增益明显的维度

1. **结构化流程**：with-skill 每个场景都严格遵循 procedures 步骤，baseline 无流程概念
2. **脚本驱动检测**：hash-based 增量检测是 baseline 完全不具备的能力
3. **多实体类型**：with-skill 原生支持 Epic/BR/PF/CR，baseline 仅关注 CR 或无结构
4. **操作语义→适配器**：with-skill 使用平台无关的操作语义，baseline 直接硬编码 gh 命令
5. **层级关系**：with-skill 自动建立 sub-issue 层级，baseline 无此概念

### 无显著差异的维度

- 基本的实体文件读取（两者都能做）
- 用户意图理解（两者都能正确理解"同步"的含义）

### 建议改进点

1. **Eval 1 中** EPIC-002 缺失导致 BR-003/004 无层级关联——procedures 应增加对 project.md 中有引用但无独立文件的 Epic 的警告
2. **Eval 2** fixture 构建步骤可以标准化为独立脚本，减少评估 agent 的 setup 开销
3. **Description 触发**：当前 description 已包含"同步/sync"等关键词，3 个场景都能正确触发
