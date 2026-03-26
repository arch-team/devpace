# Entity Schema 质量优化方案

> **日期**：2026-03-26
> **来源**：`docs/research/entity-schema-evaluation-2026-03-25.md`（评估报告）
> **性质**：结构性加固，非新功能。遵循 D11"深度优于广度"原则
> **状态**：方案已确认，待排期执行

---

## 改进项汇总

评估报告识别 1 个 P0 + 5 个 P1 + 6 个 P2，共 12 项改进。按执行批次组织：

## Batch 1：结构补全（P0 + 低风险 P2）

**预计**：5 文件，~30 行增量，1 个会话可完成

| # | 优先级 | 改进项 | 涉及文件 | 工作量 | 详细说明 |
|---|:------:|--------|---------|:------:|---------|
| 1 | **P0** | 补充 Consumers section | opportunity-format.md, epic-format.md, br-format.md, pf-format.md | 小 | 4 个中层 schema 缺失 Consumers section。参照 vision-format 格式，至少列出消费 Skill 名称。参考 `_schema/README.md` fan-in 索引确认消费者 |
| 2 | P2 | pf-format 标注风格对齐 | pf-format.md | 小 | 字段说明表列名"必填（是/否）"→"核心/渐进"，对齐其他 6 个 schema |
| 3 | P2 | project-format Consumers 完善 | project-format.md | 小 | 当前仅列 4 个消费者（rules, pace-init, pace-dev, pace-biz），实际消费者包括 pace-plan/pace-change/pace-status/pace-retro/pace-next 等 |
| 4 | P2 | OBJ "已达成"阈值量化 | obj-format.md | 小 | "MoS 全部或大部分达成"中"大部分"→量化规则（如"所有核心 MoS 达成"或"≥80% MoS 达成"） |
| 5 | P2 | vision 北极星值类型约束 | vision-format.md | 小 | 北极星指标的"当前值"和"目标值"补充推荐格式说明（自由文本，推荐"数字+单位"格式） |

### Batch 1 验证清单

- [ ] `bash dev-scripts/validate-all.sh` 通过
- [ ] 4 个新增 Consumers section 与 `_schema/README.md` fan-in 一致
- [ ] pf-format 字段说明表列名与其他 schema 一致
- [ ] project-format Consumers 列表 ≥8 个消费者

---

## Batch 2：一致性治理（P1 核心 + P2）

**预计**：5-6 文件，~120 行增量，1 个会话可完成

| # | 优先级 | 改进项 | 涉及文件 | 工作量 | 详细说明 |
|---|:------:|--------|---------|:------:|---------|
| 6 | **P1** | 跨实体状态映射表 | 新建 `_schema/entity/status-mapping.md` 或追加到 `_schema/README.md` | 中 | CR 英文状态（created/developing/...）→ PF emoji 状态（⏳/🔄/...）→ BR 中文状态（待开始/进行中/...）→ Epic 中文状态的显式映射表。聚合计算时用作参考 |
| 7 | **P1** | 4 个 schema 渐进阶段定义 | opportunity-format.md, epic-format.md, br-format.md, pf-format.md | 中 | 参照 vision-format 的渐进阶段表（桩→初始→成长→成熟），为每个 schema 补充：阶段名称、触发时机、该阶段应有的字段内容、典型大小。优先级：epic（最接近 OBJ 模式）→ br → pf → opportunity |
| 8 | P2 | project-format 字段标注表 | project-format.md | 中 | 补充系统性字段说明表（字段/核心or渐进/来源/说明），覆盖配置、愿景、战略上下文、业务目标、价值功能树、功能规格等核心 section |

### Batch 2 验证清单

- [ ] `bash dev-scripts/validate-all.sh` 通过
- [ ] 状态映射表覆盖所有 6 个有状态的实体（OBJ/OPP/Epic/BR/PF/CR）
- [ ] 4 个渐进阶段定义的阶段数和触发条件无歧义
- [ ] project-format 字段标注表覆盖所有核心 section

---

## Batch 3：复杂 Schema 加固（P1 高价值 + P2）

**预计**：3-4 文件，~150 行增量，可能需要 1-2 个会话

| # | 优先级 | 改进项 | 涉及文件 | 工作量 | 详细说明 |
|---|:------:|--------|---------|:------:|---------|
| 9 | **P1** | cr-format 容错章节 | cr-format.md | 中 | 参照 obj-format 穷举式容错表，补充独立容错章节。覆盖：CR 文件丢失重建路径、事件表格式损坏恢复、意图 section 格式异常处理、复杂度评估与实际不符调整 |
| 10 | **P1** | cr-format 更新时机表 | cr-format.md | 中 | 将散落在 ~15 处的更新逻辑整合为结构化的"更新时机"表格。格式对齐其他 schema（事件→更新内容→涉及字段）。当前散落位置：方案字段约第 63 行、执行快照约第 384 行、歧义标记约第 109 行等 |
| 11 | **P1** | project-format 容错章节 | project-format.md | 中 | 补充独立容错章节。覆盖：project.md 文件丢失/损坏时从各实体文件重建、价值功能树格式异常修复、配置字段值非法时的默认行为 |
| 12 | P2 | MoS 聚合路径形式化 | 新建 `knowledge/_guides/mos-aggregation.md` | 中 | 定义 BR MoS → Epic MoS → OBJ MoS → Vision 北极星的聚合/映射规则。当前依赖 /pace-retro 时 Claude 推断，缺少确定性定义 |

### Batch 3 注意事项

- **cr-format.md fan-in=10**：修改前查 `references/sync-checklists.md`，确认消费者兼容性
- **新增章节不改变现有字段语义**：仅补充缺失的容错和更新时机信息，不修改现有字段定义
- **MoS 聚合规则**需与 `knowledge/metrics.md` 对齐，避免度量定义冲突

### Batch 3 验证清单

- [ ] `bash dev-scripts/validate-all.sh` 通过
- [ ] cr-format 容错表覆盖 ≥5 种异常场景（参照 obj-format 的 7 种）
- [ ] cr-format 更新时机表条数 ≥12（从散落的 ~15 处整合）
- [ ] project-format 容错表覆盖 ≥4 种异常场景
- [ ] MoS 聚合规则与 metrics.md 度量定义无冲突
- [ ] plugin 加载测试通过：`claude --plugin-dir ./`

---

## 排期建议

| 批次 | 风险 | 建议时机 |
|------|:----:|---------|
| Batch 1 | 低 | 任何空闲会话即可执行，1 会话完成 |
| Batch 2 | 中 | 建议在 Batch 1 之后，1 会话完成 |
| Batch 3 | 中 | 建议在 Batch 2 之后。cr-format 修改需额外审慎（fan-in=10），可拆为 2 个子会话 |

不建议与 Phase 19（T109 Issue 生命周期）或 Phase 24（devpace-cadence MVP）混合执行，避免 Schema 改动与功能开发交叉冲突。

## 与 progress.md 的集成

执行时新增 3 个任务到 progress.md "当前任务"表：

```
| T134 | Entity Schema P0 结构补全 + P2 快速修复 | -- | OBJ-3, OBJ-6 | 待做 | Batch 1：5 文件 Consumers/标注/阈值修复 |
| T135 | Entity Schema P1 一致性治理 | -- | OBJ-3, OBJ-6 | 待做 | Batch 2：状态映射表 + 渐进阶段 + 字段标注 |
| T136 | Entity Schema P1 复杂加固 + MoS 聚合 | -- | OBJ-3, OBJ-6 | 待做 | Batch 3：cr/project 容错+更新时机 + MoS 聚合规则 |
```

## 参考文件

| 文件 | 用途 |
|------|------|
| `docs/research/entity-schema-evaluation-2026-03-25.md` | 评估报告（改进项来源） |
| `knowledge/_schema/entity/*.md` (8 个) | 待优化的 schema 文件 |
| `knowledge/_schema/README.md` | fan-in 索引和消费者信息 |
| `.claude/references/sync-checklists.md` | Batch 3 cr-format 修改的同步检查 |
| `knowledge/metrics.md` | Batch 3 MoS 聚合规则的对齐基准 |
