# devpace 产品层——业务需求阶段 Schema 分析

> 分析日期：2026-03-28
> 范围：`knowledge/_schema/entity/` 全部 8 个 Schema + 辅助 Schema（scope-discovery-format、readiness-score）

## 一、价值链全景

业务需求阶段覆盖的 Schema 位于 `knowledge/_schema/entity/` 目录下，构成完整的价值交付链上半段：

```
Vision → OBJ → Epic → (Opportunity →) BR → PF
  │        │       │         │            │      │
vision  obj    epic    opportunity    br    pf
-format -format -format  -format    -format -format
```

辅助 Schema：`process/scope-discovery-format`（发现会话中间态）、`auxiliary/readiness-score`（就绪度评分）

## 二、各 Schema 核心特征

| Schema | 行数 | Fan-in | 文件模式 | 状态机 | 渐进阶段 |
|--------|:----:|:------:|---------|--------|---------|
| **vision-format** | 173 | 1 | 单文件 `vision.md` | 无（质量维度） | 桩→初始→成长→成熟 |
| **obj-format** | 160 | 2 | 独立文件 `OBJ-xxx.md` | 活跃→已达成/已废弃（3态） | 初始→成长→成熟 |
| **epic-format** | 153 | 1 | 独立文件 `EPIC-xxx.md` | 规划中→进行中→已完成/已搁置（4态） | — |
| **opportunity-format** | 107 | 1 | 单文件 `opportunities.md` | 评估中→已采纳/已搁置/已拒绝（4态） | — |
| **br-format** | 167 | 2 | 溢出模式（内联→独立） | 待开始→进行中→已完成/暂停（4态） | — |
| **pf-format** | 126 | 2 | 溢出模式（内联→独立） | 待开始→进行中→全部完成/已发布/暂停（5态） | — |

## 三、设计模式分析

### 1. 三种文件存在模式

| 模式 | 适用对象 | 特征 |
|------|---------|------|
| **始终独立文件** | Vision、OBJ、Epic | 创建即有独立 `.md` 文件，project.md 仅保留索引/链接 |
| **溢出模式** | BR、PF | 初始在 project.md 树视图内联一行，达到阈值后溢出为独立文件（单向不可逆） |
| **单文件集中** | Opportunity | 所有 OPP 条目集中在一个 `opportunities.md`（段落式，非表格） |

**设计理由**：

- Vision/OBJ/Epic 是战略级对象，天然信息量大 → 始终独立
- BR/PF 数量多、初始信息少 → 溢出模式避免小项目过度文件化
- Opportunity 是操作性追踪，条目短小但数量不定 → 单文件段落式

### 2. 渐进丰富（Progressive Enrichment）

这是贯穿所有 Schema 的核心 UX 原则。以 Vision 为例：

```
桩（/pace-init，3-5行）
  → 初始（核心四要素：目标用户+核心问题+差异化+成功图景，8-12行）
    → 成长（+北极星+战略上下文，15-25行）
      → 成熟（全字段完整+假设验证+北极星有当前值，20-35行）
```

**字段分为两类**：

- **核心字段**：创建时必须存在（至少占位），如 OBJ 的标题、类型、状态
- **渐进字段**：后续交互中补充，如北极星贡献、MoS 进度、外部关联

### 3. 双维度 MoS（Measures of Success）

OBJ、Epic、BR 三层统一使用 **客户价值 + 企业价值** 双维度：

```markdown
## 成效指标（MoS）
**客户价值**：
- [ ] [指标]（目标：[值]，当前：[值] → 进度 [N]%）
**企业价值**：
- [ ] [指标]（目标：[值]）
```

**层级区别**：

| 层面 | MoS 粒度 | 评估时机 |
|------|---------|---------|
| OBJ | 战略级指标（收入、MAU） | /pace-retro |
| Epic | 专题级指标 | /pace-retro |
| BR | 业务结果层面（登录成功率） | /pace-retro |
| PF | 不是 MoS，是**验收标准**（实现正确性） | Gate 2 |

### 4. 状态计算：自底向上聚合

状态不是手动设置，而是从下层自动聚合：

```
CR 状态（手动/Gate 触发）
  ↑ 聚合
PF 状态 = f(关联 CR 状态)
  ↑ 聚合
BR 状态 = f(关联 PF 状态)
  ↑ 聚合
Epic 状态 = f(关联 BR 状态)
  ↑ 人类确认
OBJ 状态（/pace-retro 建议 + 人类确认）
```

### 5. 向后兼容策略

每个 Schema 都有明确的**向后兼容**设计：

- 无 `objectives/` → project.md 保持原有内联 `### OBJ-N` 格式
- 无 `epics/` → BR 直挂 OBJ
- MoS 无维度标签 → 简单 checkbox 列表仍合法
- 旧格式"成功标准"章节名 → 仍可识别（br-format）

### 6. 容错设计统一模式

所有 Schema 遵循相同的容错思路：

| 异常 | 统一处理模式 |
|------|------------|
| 文件丢失 | 从 project.md + 下游文件**重建** |
| 目录不存在 | 写入时**自动创建** |
| 链接指向不存在文件 | 按"文件丢失"处理 |
| 文件与 project.md 不一致 | **以独立文件为准**（更详细），同步更新 project.md |
| 部分字段缺失 | 保持已有字段，缺失不阻塞——渐进填充 |

## 四、辅助 Schema

### scope-discovery-format（过程态）

- **临时文件**：discover Step 1 创建，Step 5 完成后删除
- 用 `## 阶段：xxx` 单行实现跨会话恢复
- 7 天过期自动废弃
- 3 个阶段：目标框定 → 功能头脑风暴 → 边界定义

### readiness-score（评估算法）

- 6 维度（用户故事/验收标准/优先级/上游关联/异常边界/NFR）
- BR 和 PF 权重不同（BR 侧重上游关联 15%，PF 侧重验收标准 30%）
- 4 档成熟度标签：骨架级(0-20%) → 基本级(21-59%) → 详细级(60-79%) → 就绪级(>=80%)

## 五、观察与发现

1. **设计一致性高**：命名规范（三位补零自增）、更新时机表、容错表等结构高度统一
2. **project.md 是枢纽**：价值功能树始终是入口和索引，独立文件是详情的溢出
3. **人类决策保护**：战略级状态变更（OBJ 达成/废弃）必须人类确认；Vision 内容必须来自人类，Claude 不推断
4. **MoS 双维度设计贯穿三层**：这是 devpace 区别于一般项目管理工具的关键——每个层级都同时追踪客户价值和企业价值
5. **Opportunity 相对轻量**：刻意省略了 Impact/Effort 评分——评估在 /pace-biz 对话中发生，结果体现为状态变化
