# 状态展示规程

> **职责**：/pace-status 各模式的详细输出格式和规则。Claude 按需读取本文件。

## 快速概览：进度条可视化

**输出格式示例**：
```
认证系统 ████████░░ 80% (4/5 CR)，下一步：权限控制
阻塞：用户管理等待认证模块完成
```

进度条规则：
- `█` = 已完成比例，`░` = 未完成比例，总长 10 字符
- 括号内显示 CR merged/total
- 仅展示当前迭代的主要功能组
- 总输出 **≤ 3 行**（NF6 硬约束）

### 建议下一步（嵌入概览末尾）

快速概览输出后，基于 `.devpace/` 目录状态自动推断并附加 1 条"建议下一步"。

**推断规则**（按优先级，取最高优先级 1 条）：

| 优先级 | 条件 | 建议 |
|:------:|------|------|
| 1 | `.devpace/backlog/` 有 `in_review` 状态 CR | "有 N 个变更等待审批 → /pace-review" |
| 2 | 有 developing 状态 CR | "继续 [CR 标题] → /pace-dev" |
| 3 | 有 `deployed` 未 `verified` 的 Release | "建议验证最近部署 → /pace-release verify" |
| 4 | `iterations/current.md` 完成率 > 80% | "迭代接近完成 → /pace-retro 后 /pace-plan" |
| 5 | 距上次 retro > 7 天 且有 merged CR | "建议回顾 → /pace-retro" |
| 6 | backlog 为空 | "开始新功能 → 说'帮我实现 X'" |
| 7 | 其他 | 不附加建议 |

**输出格式**：
```
[进度条输出]
💡 建议：[建议内容]
```

**规则**：
- 概览仍保持 ≤ 3 行——建议行不计入主输出行数限制（作为附加提示）
- 与 §1 节奏提醒互补：§1 是会话开始的一次性提醒，建议下一步是 /pace-status 的持久特性
- 如果 §1 已给出相同建议（如 in_review 积压），/pace-status 不重复

### 同步状态摘要（sync-mapping.md 存在时）

当 `.devpace/integrations/sync-mapping.md` 存在时，概览末尾追加 1 行同步摘要。不存在时静默跳过。

**数据采集**：
1. 读取 sync-mapping.md 关联记录表
2. 对每个关联 CR：比较 devpace 状态与最后同步时间
3. 统计：已同步数（最后同步时间 ≥ 最近状态变更时间）、待推送数（反之）

**输出格式**：
```
[进度条输出]
💡 建议：[建议内容]
🔗 同步：{N} 个 CR 已同步，{M} 个待推送
```

**规则**：
- 同步行不计入主输出 ≤3 行限制（与建议行同级，作为附加信息）
- 全部已同步 → `🔗 同步：{N} 个 CR 已同步`（省略待推送数）
- 无关联 CR → 不显示同步行
- 无法判断一致性（如 gh 不可用）→ `🔗 同步：{N} 个 CR 已关联（状态未检查）`

## detail：功能树缩进可视化

**输出格式示例**：
```
📦 用户系统
  ├── ✅ 登录模块 (3/3 CR) → [详情](features/PF-001.md)
  ├── 🔄 权限控制 (1/2 CR) ← 进行中
  └── ⏳ 用户管理 (0/2 CR)
📦 数据管理
  ├── ✅ 数据导入 (2/2 CR)
  └── 🔄 数据导出 (1/3 CR)
```

规则：
- 每个功能组附带进度条
- 标记阻塞项和依赖关系
- 状态 emoji：✅ 完成、🔄 进行中、⏳ 待开始、⏸️ 暂停
- **PF 文件读取**：已溢出的 PF（`features/PF-xxx.md` 存在）显示 `[详情]` 链接，从 PF 文件读取精确的 CR 统计和验收标准通过率

## metrics：度量仪表盘

1. 展示 dashboard.md 度量表格
2. 如果有 `.devpace/metrics/insights.md`，附加最近 3 条经验 pattern 摘要

## trace：反向追溯视图

从指定的 BR/PF/OBJ 出发，聚合所有下游实体状态。纯只读计算视图，数据全部来自现有 project.md 和 PF 文件。

### 数据采集

1. 读取 `.devpace/project.md` 价值功能树，匹配用户提供的名称或 ID
2. 从匹配节点向下遍历，收集所有下游 PF 和 CR
3. 对已溢出的 PF（`features/PF-xxx.md` 存在），读取 PF 文件获取详细 CR 列表和验收标准通过率
4. 对未溢出的 PF，从 project.md 功能规格 section 和 backlog/ CR 文件提取信息
5. 读取 project.md MoS checkbox 统计达成率

### 匹配规则

| 输入 | 匹配方式 |
|------|---------|
| OBJ ID（如 `OBJ-1`） | 精确匹配树视图中的 OBJ 行 |
| BR ID（如 `BR-001`） | 精确匹配树视图中的 BR 行 |
| PF ID（如 `PF-001`） | 精确匹配树视图中的 PF 行 |
| 名称关键词（如 `用户认证`） | 模糊匹配 BR/PF/OBJ 名称，匹配多个时列出候选让用户选择 |

### 输出格式

**从 OBJ 追溯**：
```
目标: [OBJ 名称] (OBJ-ID)
├── 需求: [BR 名称] (BR-ID)
│   ├── [PF 名称] (PF-ID) → N/M CR ✅
│   ├── [PF 名称] (PF-ID) → N/M CR 🔄
│   └── [PF 名称] (PF-ID) → N/M CR ⏳
└── 需求: [BR 名称] (BR-ID)
    └── [PF 名称] (PF-ID) → N/M CR ✅
MoS: X/Y 达成 ([达成的指标] ✅ | [未达成] ⏳)
```

**从 BR 追溯**：
```
需求: [BR 名称] (BR-ID) → [OBJ 名称]
├── [PF 名称] (PF-ID) → N/M CR ✅
├── [PF 名称] (PF-ID) → N/M CR 🔄
└── [PF 名称] (PF-ID) → N/M CR ⏳
MoS: X/Y 达成
```

**从 PF 追溯**：
```
功能: [PF 名称] (PF-ID)
所属: [BR 名称] → [OBJ 名称]
CR 状态: N/M 完成
验收标准: X/Y 通过
关联 CR:
  ├── [CR 标题] ✅ merged
  ├── [CR 标题] 🔄 developing
  └── [CR 标题] ⏳ created
```

### 规则

- **自然语言**：不暴露 ID 除非用户以 ID 查询。用功能名称而非 ID
- **MoS 统计**：仅在追溯 OBJ 或 BR 时附加，从 project.md MoS checkbox 计算
- **已溢出 PF 标注**：从 PF 文件追溯时展示完整验收标准通过率
- **无匹配处理**：无匹配时提示"未找到匹配的业务需求/功能，请检查名称"

## tree：完整价值链路

1. 展示从业务目标到变更请求的完整链路
2. 每个节点附带状态 emoji 和进度

## 四级输出信息量递增

- 概览：≤ 3 行 + 进度条 + 建议下一步（回答"整体怎样 + 下一步做什么"）
- detail：功能树 + 状态（回答"每个功能怎样"）
- trace：从指定节点出发的聚焦追溯（回答"某个需求/功能的完整交付状态"）
- tree：完整价值链路（回答"从业务目标到代码的全貌"）

## 角色视角输出

### biz（Biz Owner 视角）

```
## 业务目标进展

OBJ-1：[目标名]
- MoS 达成：M/N 指标已满足
- 价值交付：N 个功能已上线，M 个进行中
- 风险：[未达成指标和原因]
```

数据来源：project.md MoS checkbox + 功能树完成度

### pm（PM 视角）

```
## 迭代交付看板

迭代：[名称] | 进度 ████████░░ 80%
- 完成：N 功能 | 进行中：M 功能 | 阻塞：K 个
- 变更：本迭代 X 次范围变更
- 节奏：平均 CR 周期 Y 天
```

数据来源：iterations/current.md + backlog/ CR 状态分布

### dev（Dev 视角）

```
## 开发状态

进行中 CR：[标题] → [当前阶段]
质量门：M/N 项通过
待处理：K 个 CR 待开始
```

数据来源：backlog/ CR 文件 + checks.md

### tester（Tester 视角）

```
## 质量状态

缺陷概况：开放 N / 已修复 M / 逃逸 K
质量检查通过率：X%
人类打回率：Y%
高优缺陷：[critical/major 列表]
```

数据来源：backlog/ CR 文件（type:defect）+ dashboard.md

### ops（Ops 视角）

```
## 运维状态

最近 Release：[REL-xxx] [状态]（[日期]）
部署后缺陷：N 个（M 已修复）
MTTR：平均 X 天
待发布 CR：K 个 merged 未 released
```

数据来源：releases/ + backlog/ CR 文件 + dashboard.md
