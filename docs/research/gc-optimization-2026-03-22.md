# GC 机制优化：从 3/5 到 4/5 的思考过程

> **日期**：2026-03-22 | **方法**：代码库探索 + 三轮工程质量反思 | **产出**：4 项 P0 改动 + 3 个 eval 场景

---

## 一、起点：为什么要做 GC 优化

harness-engineering-practices（2026-03-14）§3.3 将 devpace 的 GC 评为 3/5 星，指出：

> "Garbage Collection 自动化不足——缺少定期运行的'清理 Agent'扫描架构偏差、文档陈旧度"

对标 OpenAI 的做法：一组后台 Codex 任务按固定节奏运行——扫描架构偏差、更新质量评级、打开定向重构 PR、检查文档陈旧度。

四个组件被点名：pace-pulse 健康检查、pre-compact.sh compaction 前快照、pace-learn 经验萃取、confidence score 衰减机制。

## 二、现状诊断

### 已有且成熟的机制

| 组件 | 现状 | 评估 |
|------|------|------|
| pulse-procedures-gc.md | 3 项基础设施扫描（文档陈旧/Schema 漂移/孤立 CR），session-start 触发 | 检测逻辑完整，但仅输出建议 |
| pre-compact.sh | 5 部分恢复上下文输出到 stdout，advisory hook | 设计合理，不写磁盘 |
| insights 三阶段生命周期 | Active→Dormant→Archived，定义在 insights-format.md | 定义完整但缺执行步骤 |
| 置信度衰减规则 | 180 天/-0.1 月/下限 0.2，定义在两处 | 参数完整但执行依赖搭便车 |
| 统一写入管道 | pace-learn Step 3 去重+冲突检测 | SSOT 写入者，架构清晰 |

### 真实问题（有证据支撑）

1. **衰减冻结**：衰减仅在 pace-learn 写入时搭便车执行。长期无新 CR → pace-learn 不触发 → 衰减不运行 → 知识质量无声退化
2. **归档步骤缺失**：insights-format.md 定义了 Dormant→Archived 转换条件，learn-procedures.md 没有执行步骤
3. **eval-实现不同步**：evals.json 引用 prune 子命令但 SKILL.md 无路由
4. **stats 衰减预警无计算逻辑**：输出模板有占位但无计算规则（轻微）

### 非问题（探索后排除）

| 看似问题 | 为什么不是 | 排除依据 |
|---------|-----------|---------|
| backlog/ merged CR 积累 | 不影响性能或正确性 | Claude 按状态过滤读取，不遍历全目录 |
| pre-compact.sh 缺持久化 | stdout 机制已足够 | 无消费者定义，YAGNI |
| insights.md 无条目上限 | 无经验数据支撑任何数字 | 50 是拍脑袋，Evidence > assumptions |
| 全局库 GC | 全局库本身是 P2 功能 | 为未上线功能设计 GC 是过早优化 |
| 数据域膨胀检测 | 无实际数据验证阈值 | risks/adr/releases 的文件数阈值无依据 |

## 三、方案演进：v1 → v2 → v3

### v1：全面覆盖（12 项改动，~200 行增量）

初始方案试图一次性解决所有可能的 GC 缺口。

### v2：工程质量反思后精简（9 项，~108 行）

| 问题 | 违反原则 | 修正 |
|------|---------|------|
| pulse GC 直接写 insights.md | IA-6 单一权威 | GC 仅检测，ACTION 委托 pace-learn |
| pulse GC + pace-learn 双重执行衰减 | DRY | 统一为 pace-learn 执行 |
| pulse-procedures-gc.md 堆叠 6 项扫描（73→150 行） | IA-11 单一职责 | 保持原有模式，仅增 1 项检测 |
| pre-compact 持久化文件无消费者 | YAGNI | 删除 |
| merge "比较描述相似度" | HE-3 Agent Legibility | 暂缓（不可确定性执行） |
| 阈值 50/14/10/20 无依据 | Evidence > assumptions | 标注初始值+校准方法 |

### v3：需求驱动精简（4 项 P0 + eval，~54 行）

关键追问："为什么要添加 prune？"——发现 v1/v2 的动机链是反向的（从 eval 倒推功能）。

**反向推理**：eval 有 prune → 所以 SKILL.md 要加 → 所以要写 procedures

**正向推理**：衰减冻结需要独立触发点 → prune --decay-only 提供执行路径 + 用户需要清理入口 → 一个子命令解决两个问题

进一步追问："backlog 归档的 ACTION 委托有什么价值？"——答：几乎没有。merged CR 在 backlog/ 不影响性能或正确性，是审美问题。删除 P1-1。

## 四、最终方案

4 项改动解决 4 个真实问题，总增量 54 行（v1 的 27%）。

| 编号 | 改动 | 解决问题 | 文件 | 增量 |
|------|------|---------|------|:----:|
| P0-1 | prune 路由 | eval 不同步 + 执行路径 | SKILL.md | +2 |
| P0-2 | prune 规程（含 --decay-only） | 衰减冻结 + 清理入口 | learn-procedures-query.md | +42 |
| P0-3 | GC 衰减检测 | 衰减冻结（检测端） | pulse-procedures-gc.md | +12 |
| P0-4 | 归档执行步骤 | 定义-执行不一致 | learn-procedures.md | +6 |

**架构决策**：GC 检测 → ACTION 委托 `/pace-learn prune --decay-only` → pace-learn 执行。保持 IA-6（insights.md 唯一写入者为 pace-learn），GC 保持"检测+建议"的统一模式。

## 五、关键设计决策记录

### D1：为什么 GC 不直接写 insights.md？

**决策**：pulse-procedures-gc.md 仅读取 insights.md，通过 ACTION 委托 pace-learn 执行写入。

**理由**：IA-6 单一权威——pace-learn 是 insights.md 的指定唯一写入者（learn-procedures.md 第 136 行）。制造第二写入路径会导致衰减逻辑不同步风险。

**替代方案**：pulse GC 直接写入（v1 方案）——被否决，因违反 IA-6。

### D2：为什么选 prune 子命令而非 session-start 自动衰减？

**决策**：新增 `/pace-learn prune --decay-only` 子命令。

**理由**：一个子命令同时解决两个问题——(1) 衰减冻结需要独立触发点（--decay-only 模式），(2) 用户需要主动清理知识库的入口（完整 prune 模式）。session-start 自动衰减方案会改变 pace-learn 的触发模型（从纯事件驱动变为事件+会话启动混合），且增加 session-start 负载。

### D3：为什么删除 backlog 归档、pre-compact 持久化、数据域膨胀检测？

**决策**：全部删除或降为备忘。

**理由**：
- backlog 归档：merged CR 在 backlog/ 不影响性能或正确性——"审美问题不值得编码"
- pre-compact 持久化：`.compact-checkpoints` 无消费者——YAGNI
- 数据域膨胀：阈值（10/20）无经验数据支撑——Evidence > assumptions
- 语义去重："比较描述相似度"违反 HE-3（不可确定性执行）

### D4：为什么条目上限不编码？

**决策**：降为备忘，待实际数据。

**理由**："50"这个数字来自直觉而非证据。devpace 尚无运行足够长时间的真实项目来验证 insights.md 的实际增长模式。设无依据的阈值违反 PRINCIPLES.md 的 "Evidence > assumptions"。

## 六、反思方法论

本次优化过程中使用了三轮反思，每轮砍掉约 50% 增量：

```
v1 (200 行) --[IA-6/IA-11/YAGNI/HE-3 检查]--> v2 (108 行) --[需求驱动追问]--> v3 (54 行)
```

**有效的追问模式**：

| 追问 | 效果 |
|------|------|
| "为什么要添加 X？" | 暴露反向推理（从 eval 倒推功能） |
| "ACTION 委托有什么价值？" | 暴露审美问题被编码为功能 |
| "现有方案能达到目标吗？" | 迫使诚实评估差距（4/5 而非 5/5） |
| "这个文件什么时候创建的？" | 暴露在未验证组件上堆叠扩展的风险 |

**核心教训**：GC 优化本身也需要 GC——砍掉不必要的优化项，比添加新功能更重要。
