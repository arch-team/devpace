# Risk Fabric — 风险织网设计文档

> **日期**：2026-02-25
> **状态**：已批准
> **关联**：能力深化 → AI 主动性 → 问题预判与预防

## 1. 背景与动机

devpace v1.3.0 已具备节奏管理、质量门、变更管理等完整的 BizDevOps 能力。但在"问题预判与预防"维度存在系统性空白：

**现有能力**（被动/浅层主动）：
- pace-pulse：7 信号节奏检查（侧重节奏异常，不是风险预判）
- 意图漂移检测 / 复杂度漂移检测（仅 CR developing 阶段，仅范围维度）
- Gate 通过反思 / 对抗审查（仅 Gate 节点，事后检查）
- insights.md 经验积累（有数据，但无主动"预测"消费路径）

**空白区**：
1. CR 开发前：无系统化风险预分析
2. CR 开发中：漂移检测仅看"范围"，不检测技术债、安全隐患、架构腐化
3. 迭代/跨迭代：无趋势分析（重复模式、质量退化信号）
4. 风险持久化：无风险登记簿，识别的风险不跨 CR/会话追踪
5. 分级自主响应：大多为"提醒"，未按风险等级分化行动

## 2. 设计目标

- **预判闭环**：覆盖"开发前风险分析 → 开发中实时监控 → 回顾时趋势识别"
- **分级自主**：低风险自动处理 → 中风险提醒+方案 → 高风险暂停等人
- **持久追踪**：风险跨 CR 和会话持久化，支持趋势分析
- **零摩擦嵌入**：主要能力嵌入现有 Skill 流程，不增加用户操作步骤
- **渐进暴露**：基础能力自动运行，高级功能通过 /pace-guard 按需调用

## 3. 风险模型

### 3.1 风险定义

任何可能影响 CR 交付质量、进度或架构健康度的已识别问题或隐患。

### 3.2 风险来源（4 类）

| 来源 | 触发时机 | 典型场景 |
|------|---------|---------|
| Pre-flight | CR 开发前 | 依赖冲突、架构兼容性、历史教训 |
| Runtime | CR 开发过程中 | 技术债引入、安全隐患、范围蔓延 |
| Retrospective | 迭代回顾 | 重复模式、质量退化趋势 |
| External | 外部信号 | CI 失败趋势、运维事件关联 |

### 3.3 风险严重度（3 级）

| 等级 | 定义 | Claude 行为（标准自主级别） |
|------|------|---------------------------|
| Low | 不影响当前 CR 交付，但值得记录 | 静默记录到风险登记簿 |
| Medium | 可能影响 CR 质量或进度 | 记录 + 提醒用户 + 给出建议方案 |
| High | 大概率导致返工、安全问题或架构损害 | 记录 + 暂停推进 + 必须用户确认后才继续 |

### 3.4 风险状态机

```
open → mitigated    （已采取缓解措施）
open → accepted     （已知风险，决定接受）
open → resolved     （风险已消除）
```

### 3.5 风险持久化

- 存储位置：`.devpace/risks/`
- 每条风险一个 Markdown 文件（命名：`RISK-NNN.md`）
- 跨会话持久追踪
- Schema 定义：`knowledge/_schema/risk-format.md`

## 4. /pace-guard Skill 设计

### 4.1 子命令

| 子命令 | 用户可调用 | 职责 | 自动触发点 |
|--------|-----------|------|-----------|
| `scan` | 是 | Pre-flight 风险扫描 | pace-dev 意图检查点（L/XL 必须，S/M 匹配 insights 时触发） |
| `monitor` | 是 | 实时风险信号汇总 | pace-pulse 第 8 信号 |
| `trends` | 是 | 跨 CR 趋势分析 | pace-retro 报告自动包含 |
| `report` | 是 | 风险全局视图 | 用户显式调用 |
| `resolve` | 是 | 更新风险状态 | 用户触发或 Gate 通过时自动提议 |

### 4.2 嵌入式触发点

```
pace-dev 意图检查点
  └── L/XL: 自动调用 scan（输出嵌入 CR 风险预评估 section）
  └── S/M: 仅在 insights.md 有匹配历史风险 pattern 时触发

pace-pulse 脉搏检查
  └── 新增第 8 信号："风险积压"（open 风险数 > 3 或 High 风险 > 0）

pace-retro 报告
  └── 新增"风险趋势"段（跨迭代风险类型分布 + 重复模式）
```

### 4.3 分级自主矩阵

| 项目自主级别 | Low 风险 | Medium 风险 | High 风险 |
|------------|---------|------------|----------|
| 辅助 | 记录+简要提醒 | 记录+详细提醒+方案 | 暂停+等用户 |
| 标准 | 静默记录 | 记录+提醒+方案 | 暂停+等用户 |
| 自主 | 静默记录 | 记录+自动缓解+报告 | 提醒+方案+等用户 |

## 5. Pre-flight 风险扫描（scan）

### 5.1 扫描维度

| 维度 | 检查内容 | 数据源 | 严重度判定 |
|------|---------|--------|-----------|
| 历史教训 | 相似 CR 的失败/打回 pattern | insights.md + dashboard.md | 有打回 pattern → Medium；同一模块连续打回 → High |
| 依赖影响 | 改动文件的反向依赖链 | 代码 import/require 分析 | ≤3 引用 → Low；4-10 → Medium；>10 → High |
| 架构兼容性 | 变更是否违反项目技术约定 | context.md | 违反明确约定 → High；边界模糊 → Medium |
| 范围复杂度 | 实际工作量 vs 预期 | CR 描述 + 文件树 | 实际 > 预期 1 级 → Medium；> 2 级 → High |
| 安全敏感度 | 涉及认证/授权/数据/加密 | 文件路径 + 关键词 | 涉及安全模块 → Medium；涉及加密/权限 → High |

### 5.2 扫描结果格式

写入 CR 文件的"风险预评估"section：

```markdown
## 风险预评估

| # | 维度 | 等级 | 发现 | 建议 |
|---|------|------|------|------|
| R1 | 历史教训 | Medium | 类似 CR-003 曾因缺少 E2E 测试被打回 | 优先编写 E2E 测试 |
| R2 | 依赖影响 | Low | auth.ts 被 5 文件引用，均为读取 | 无需额外操作 |

**综合风险等级**：Medium
```

### 5.3 与意图检查点整合

- scan 输出写入 CR "风险预评估" section
- 意图检查点读取 scan 结果，调整执行计划
- High 风险维度 → 执行计划增加对应防护步骤
- 不是串行阻塞：scan 是意图检查点的子步骤

## 6. Runtime 风险监控

### 6.1 新增监控信号

| 信号 | 检测方式 | 触发条件 | 默认行为 |
|------|---------|---------|---------|
| 技术债引入 | 每次文件变更后扫描：硬编码值、TODO/FIXME 新增、重复代码块、过长函数 | 单次变更新增 ≥ 2 个信号 | Low: 静默记录 / Medium: 提醒 |
| 安全隐患 | 敏感数据硬编码、未转义输入、不安全加密、权限提升路径 | 任何安全信号 | 一律 High → 暂停提醒 |
| 架构腐化 | 跨层调用、循环依赖新增、违反 context.md 约定 | 违反已声明的架构约定 | Medium: 提醒+方案 |

### 6.2 实现方式

- 嵌入现有 checkpoint 流程，不新增 Hook
- 每个 checkpoint 增加轻量扫描
- 结果追加到当前 CR 的"运行时风险"section
- 累积风险写入 `.devpace/risks/` 持久化

## 7. 趋势分析

### 7.1 pace-retro 新增"风险趋势"段

```markdown
## 风险趋势

### 跨迭代模式（最近 3 迭代）
| 风险类型 | Iter-1 | Iter-2 | Iter-3 | 趋势 |
|---------|--------|--------|--------|------|
| 测试覆盖不足 | 2 次 | 1 次 | 3 次 | ↑ 恶化 |
| 依赖冲突 | 1 次 | 0 次 | 0 次 | ↓ 改善 |

### 重复 Pattern Top 3
1. "认证相关 CR 被打回率 60%" → 建议：认证模块变更时强制 E2E
2. "跨层调用每迭代增加 1-2 处" → 建议：下迭代安排架构清理 CR

### 风险登记簿状态
- Open: 3（High: 0, Medium: 2, Low: 1）
- 本迭代解决: 2
```

### 7.2 数据流

```
Pre-flight scan → CR risk section → Runtime signals → CR risk section 追加
                                                    ↓
                                          insights.md risk patterns
                                                    ↓
                                    pace-retro 趋势分析 ← dashboard.md
```

## 8. Schema 新增

### 8.1 risk-format.md

新增 `knowledge/_schema/risk-format.md`，定义风险文件格式：

- 编号（RISK-NNN）
- 来源（pre-flight / runtime / retrospective / external）
- 严重度（Low / Medium / High）
- 状态（open / mitigated / accepted / resolved）
- 关联 CR
- 发现描述
- 建议动作
- 处理记录（状态变更历史）

### 8.2 CR Schema 扩展

cr-format.md 新增两个可选 section：
- "风险预评估"（Pre-flight scan 输出）
- "运行时风险"（Runtime 监控累积）

## 9. 实现影响评估

### 9.1 新增文件

| 文件 | 类型 |
|------|------|
| `knowledge/_schema/risk-format.md` | Schema |
| `knowledge/_templates/risk.md` | 模板 |
| `skills/pace-guard/SKILL.md` | Skill 入口 |
| `skills/pace-guard/guard-procedures.md` | 执行规程 |

### 9.2 修改文件

| 文件 | 修改内容 |
|------|---------|
| `knowledge/_schema/cr-format.md` | 新增风险预评估 + 运行时风险 section |
| `skills/pace-dev/dev-procedures.md` | 意图检查点嵌入 scan 触发 |
| `skills/pace-pulse/pulse-procedures.md` | 新增第 8 信号 |
| `skills/pace-retro/retro-procedures.md` | 新增风险趋势段 |
| `rules/devpace-rules.md` | §10 新增风险信号 + §0 速查更新 |
| `.claude-plugin/plugin.json` | 注册 pace-guard Skill |

### 9.3 不变的部分

- 风险状态机独立于 CR 状态机（不增加 CR 状态复杂度）
- 现有 Gate 1/2/3 流程不变（风险信息作为 Gate 2 的额外参考）
- 现有自主级别模型不变（风险响应复用三级框架）
