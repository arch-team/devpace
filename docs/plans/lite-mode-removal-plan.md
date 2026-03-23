# lite 模式移除方案

> 基于 2026-03-20 文件状态验证，所有行号已确认。

## Context

### 移除理由

1. **权威设计链零锚点**：vision.md / design.md / requirements.md / roadmap.md 全链无 lite 定义
2. **与核心原则矛盾**：开发守则"概念模型始终完整，不可省略任何环节"——lite 删除了 OPP/Epic/BR 三层结构
3. **功能被既有机制覆盖**：渐进丰富（空结构+按需填充）+ P1 零摩擦 + P2 渐进暴露 + P3 副产物非前置
4. **成本远超收益**：42 文件 95 处引用 / 18 个 Skill 条件分支 / 仅省 3 个空文件

### 影响范围摘要

| 类别 | 文件数 | 层级 |
|------|--------|------|
| 删除文件 | 2 | 产品层 |
| 编辑 Skill 文件 | 15 | 产品层 |
| 编辑 Schema 文件 | 1 | 产品层 |
| 编辑特性文档 | 6 | 开发层 |
| 编辑测试文件 | 2 | 开发层 |
| 历史文档（不改） | ~9 | — |

---

## Phase 1：产品层——删除 lite 专属资产（2 文件）

| # | 操作 | 文件 | 行数 |
|---|------|------|------|
| 1.1 | 删除 | `knowledge/_guides/lite-mode-guide.md` | 28 行，整文件为 lite 专属 |
| 1.2 | 删除 | `skills/pace-init/init-procedures-lite.md` | 49 行，整文件为 lite 专属 |

---

## Phase 2：产品层——清理 Skill 条件分支（15 文件）

### 2.1 pace-init/SKILL.md（3 处）

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L4 | 编辑 | argument-hint 末尾含 `[--lite]` | 移除 `[--lite]` |
| L35 | 删除行 | `- \`--lite\` — 轻量模式：跳过 OPP/Epic/BR 层...` | 整行删除 |
| L69 | 删除行 | `\| \`--lite\` \| \`init-procedures-core.md\` + \`init-procedures-lite.md\` \|` | 整行删除 |

### 2.2 pace-biz/SKILL.md（3 处）

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L109 | 编辑 | `3. 读取 project.md 配置 section 的 \`mode\` 字段（缺省 = 完整模式，\`lite\` = 轻量模式）` | 删除此步骤，原 Step 4→3，原 Step 5→4 |
| L111 | 编辑 | `...（各 procedure 内部根据 mode 和 role 调整行为）` | 改为 `...（各 procedure 内部根据 role 调整行为）` |
| L113-125 | 删除段 | `### lite 模式子命令可用性` 至表格结束（13 行） | 整段删除 |

### 2.3 biz-procedures-discover.md（2 处）

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L19 | 删除 | `2. 读取 project.md 的 \`mode\` 字段，记录当前模式（\`lite\` 或完整）` | 删除此步骤，后续步骤 3→2, 4→3, 5→4 |
| L33-37 | 删除段 | `**lite 模式适配**：后续 Step 1-5 中...`（5 行） | 整段删除（含空行） |

### 2.4 biz-procedures-import.md（2 处）

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L20 | 删除 | `3. 读取 project.md 的 \`mode\` 字段，记录当前模式` | 删除此步骤，原 Step 4→3 |
| L23-26 | 删除段 | `**lite 模式适配**：`（4 行） | 整段删除（含空行） |

### 2.5 biz-procedures-infer.md（2 处）

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L21 | 删除 | `3. 读取 project.md 的 \`mode\` 字段，记录当前模式` | 删除此步骤，原 Step 4→3 |
| L26-29 | 删除段 | `**lite 模式适配**：`（4 行） | 整段删除（含空行） |

### 2.6 四个"Step 0 阻断"文件（各 1 处，模式相同）

每个文件的 Step 0 包含一段 lite 阻断逻辑，删除后 Step 0 标题也一并删除（因为整个 Step 0 的唯一内容就是 lite 检查）。

| 文件 | 行号 | 删除内容 |
|------|------|---------|
| `biz-procedures-opportunity.md` | L11-13 | `### Step 0：模式检查` + L13 阻断段 |
| `biz-procedures-epic.md` | L11-13 | `### Step 0：模式检查` + L13 阻断段 |
| `biz-procedures-decompose-epic.md` | L11-13 | `### Step 0：模式检查` + L13 阻断段 |
| `biz-procedures-decompose-br.md` | L11-13 | `### Step 0：模式检查` + L13 阻断段 |

### 2.7 两个"Step 0 简化"文件（各 1 处）

| 文件 | 行号 | 删除内容 |
|------|------|---------|
| `biz-procedures-align.md` | L11-13 | `### Step 0：模式检查` + L13 简化段 |
| `biz-procedures-view.md` | L11-13 | `### Step 0：模式检查` + L13 简化段 |

### 2.8 biz-procedures-refine.md（1 处）

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L16-18 | 删除段 | `### Step 0：模式检查` + L18 lite 限制段（整句） | 整段删除 |

### 2.9 biz-procedures-guide.md（1 处）

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L45-50 | 删除段 | `### Step 3：lite 模式引导`（标题+4 行正文） | 整段删除 |

### 2.10 pace-change/change-procedures-degraded.md（2 处，重命名）

降级模式本身保留——仅消除 `.devpace-lite/` 命名与 lite 模式的混淆。

| 行号 | 操作 | 旧文本 | 新文本 |
|------|------|--------|--------|
| L51 | 替换 | `.devpace-lite/changes.md` | `.devpace-cache/changes.md` |
| L57 | 替换 | `.devpace-lite/changes.md` | `.devpace-cache/changes.md` |

---

## Phase 3：产品层——清理 Schema（1 文件）

**`knowledge/_schema/entity/project-format.md`**

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L11 | 删除行 | `模式：完整（默认）或 lite（OBJ→PF→CR，跳过 OPP/Epic/BR，适合个人小项目）` | 整行删除 |
| L174-190 | 删除段 | `#### mode（可选）` 子章节全部（17 行：标题+示例+值表+规则 5 条） | 整段删除 |

---

## Phase 4：开发层——更新特性文档（6 文件）

### 4.1 pace-biz 特性文档（中英文各 4 处）

**`docs/features/pace-biz.md`**：

| 行号 | 操作 | 内容标识 |
|------|------|---------|
| L44 | 删除行 | `**Lite mode note**: In lite mode (OBJ→PF→CR)...` |
| L189 | 删除行 | `> **Lite mode difference**: The candidate tree simplifies...` |
| L258 | 删除行 | `> **Lite mode difference**: \`import\` extracts PF candidates...` |
| L312 | 删除行 | `> **Lite mode difference**: \`infer\` scan results map...` |

**`docs/features/pace-biz_zh.md`**：

| 行号 | 操作 | 内容标识 |
|------|------|---------|
| L43 | 删除行 | `**lite 模式说明**：轻量模式（OBJ→PF→CR）下...` |
| L188 | 删除行 | `> **lite 模式差异**：候选树简化为...` |
| L257 | 删除行 | `> **lite 模式差异**：\`import\` 直接提取...` |
| L311 | 删除行 | `> **lite 模式差异**：\`infer\` 扫描结果...` |

### 4.2 pace-change 特性文档（中英文各 1 处，重命名）

| 文件 | 行号 | 旧文本 | 新文本 |
|------|------|--------|--------|
| `docs/features/pace-change.md` | L204 | `.devpace-lite/changes.md` | `.devpace-cache/changes.md` |
| `docs/features/pace-change_zh.md` | L206 | `.devpace-lite/changes.md` | `.devpace-cache/changes.md` |

### 4.3 用户指南（中英文各 1 处）

| 文件 | 行号 | 操作 |
|------|------|------|
| `docs/user-guide.md` | L127 | 删除 `--lite` 参数整行 |
| `docs/user-guide_zh.md` | L125 | 删除 `--lite` 参数整行 |

---

## Phase 5：开发层——更新测试（2 文件）

### 5.1 tests/static/test_pace_init.py

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L52 | 删除行 | `"init-procedures-lite.md",` | 从 EXPECTED_PROCEDURE_FILES 列表移除 |

> 注：ROUTING_TABLE（L56-68）和 DOCUMENTED_SUBCOMMANDS（L71-83）均不含 `--lite`，无需修改。

### 5.2 tests/evaluation/pace-biz/evals.json

| 行号 | 操作 | 当前内容 | 目标 |
|------|------|---------|------|
| L226-251 | 删除 | eval id=16 `refine-lite-br-blocked` 和 id=17 `discover-lite-mode` 两个完整 case | 删除两个 JSON 对象（含前置逗号） |

> 注：`ENV-BIZ-LITE` 仅作为 case 的 env 字段值使用，无独立环境定义块，随 case 删除即可。删除后 evals 数组从 18 个 case 变为 16 个，id=18 `empty-arg-guidance` 无需改编号（id 不要求连续）。

---

## 不改动的文件（历史记录）

以下文件含 "lite" 但属于历史记录，保留不改：

| 文件 | 理由 |
|------|------|
| `CHANGELOG.md` | 已发布变更日志 |
| `docs/planning/progress.md` | 任务历史记录 |
| `docs/plans/pace-biz-optimization-plan.md` | 历史分析报告 |
| `docs/plans/pace-biz-improvement-plan.md` | 历史计划 |
| `docs/plans/pace-biz-skill-review-report.md` | 历史审查报告 |
| `docs/plans/devpace-bizdevops-lifecycle-review-plan.md` | 历史计划 |
| `docs/plans/cognitive-load-optimization.md` | 历史分析 |
| `docs/plans/devpace-cadence-design.md` | 历史设计文档 |
| `docs/plans/lite-mode-removal-plan.md` | 本方案自身 |

---

## 全量验证清单

```bash
# V1：产品层 + 开发层零 lite 残留（排除历史文档和 DORA Elite）
grep -rn "lite" skills/ knowledge/ rules/ docs/features/ docs/user-guide*.md tests/ \
  --include="*.md" --include="*.py" --include="*.json" \
  | grep -iv "Elite"
# 预期：零结果

# V2：被删文件无残留引用
grep -rn "lite-mode-guide\|init-procedures-lite" skills/ knowledge/ rules/ docs/features/
# 预期：零结果

# V3：自动化合规
bash dev-scripts/validate-all.sh
# 预期：全部通过

# V4：静态测试
pytest tests/static/ -v
# 预期：全部通过
```

---

## 实施策略

### 执行顺序

Phase 1（删除文件）→ Phase 2+3（产品层编辑，可并行）→ Phase 4+5（开发层编辑，可并行）→ 全量验证 → 提交

### 并行化

| 并行组 | 文件 | 说明 |
|--------|------|------|
| A | pace-biz 12 个 procedures + SKILL.md | 互不依赖 |
| B | pace-init SKILL.md + pace-change degraded | 互不依赖 |
| C | project-format.md | 独立 |
| D | docs 6 文件 | 互不依赖 |
| E | tests 2 文件 | 互不依赖 |

Phase 1 先行；A/B/C 可全并行（Phase 2+3）；D/E 可全并行（Phase 4+5）。

### 提交信息

```
refactor(*): 移除 lite 模式——渐进丰富机制已覆盖其功能

lite 模式（OBJ→PF→CR 三层简化）与核心原则"概念模型始终完整"矛盾，
且其解决的问题（小项目认知负担）已被渐进丰富+P1/P2/P3 覆盖。

移除：2 文件删除 + 15 Skill 编辑 + 1 Schema 编辑 + 6 文档编辑 + 2 测试编辑
净减少：~180 行产品层代码 + 18 个 Skill 条件分支
```

---

## 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 遗漏 lite 引用导致运行时异常 | 低 | 中 | V1 全量 grep 验证 |
| 删除 init-procedures-lite.md 后测试失败 | 确定 | 低 | Phase 5 同步更新测试 |
| 行号偏移导致编辑错位 | 中 | 低 | 同文件多处编辑从后往前；用文本匹配而非纯行号 |
| `.devpace-lite/` 重命名影响已有用户 | 低 | 低 | 降级模式极少使用且无持久状态依赖 |
| evals.json 删除 case 后 JSON 格式错误 | 低 | 低 | 删除后验证 JSON 解析 |
