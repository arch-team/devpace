# 业务规划域输出格式规程

> **职责**：定义 /pace-biz 各子命令的输出格式模板。

## opportunity 输出

```
已捕获业务机会：OPP-xxx — [描述]
来源：[类型]（[详情]）
状态：评估中
→ 下一步：/pace-biz epic OPP-xxx 评估并转化为 Epic
```

## epic 输出

```
已创建专题：EPIC-xxx — [名称]
关联：OBJ-x（[目标]）← OPP-xxx（如有）
MoS：[指标列表]
→ 下一步：/pace-biz decompose EPIC-xxx 分解为业务需求
```

## decompose 输出

```
已分解 [EPIC-xxx|BR-xxx]：
├── BR-001：[名称] P0
├── BR-002：[名称] P1
└── BR-003：[名称] P2

依赖关系：（有依赖时展示）
  BR-002 ──依赖──→ BR-001
  BR-003（无依赖，可并行）
  建议实施顺序：001 → 002 → 003

→ 下一步：/pace-change add 补充 PF 或 /pace-dev 开始开发
```

## refine 输出

```
已精炼 [BR-xxx|PF-xxx]：[名称]
变更摘要：
  + 新增验收标准 N 条
  + 补充异常场景 M 个
  ~ 更新用户故事描述
→ 下一步：/pace-biz decompose BR-xxx 继续分解 | /pace-dev 开始开发
```

## align 输出

```
战略对齐度报告：
- OBJ 覆盖率：N/M OBJ 有 Epic 覆盖
- 孤立实体：[列表] → [对应修复命令]
- MoS 完整性：[统计] → 缺失项附修复命令
- 优先级分布：P0/P1/P2 比例 — [健康度判断]
- 需求就绪度：就绪 N / 基本就绪 M / 需精炼 K — P0 平均 [N]%
- 利益相关者覆盖度：（有数据时展示）
- 趋势对比（vs 上次）：OBJ 覆盖率/孤立实体/P0 就绪度变化
- 对齐建议（附操作命令）：[建议 → 命令]
```

## view 输出

```
业务全景：
OPP-001（评估中）→ /pace-biz epic OPP-001
OPP-002 → EPIC-001（进行中）
  ├── BR-001 → PF-001 → CR-001 🔄
  └── BR-002 → PF-002（待开始）
OPP-003 → EPIC-002（规划中，待分解 → /pace-biz decompose EPIC-002）

[问题实体附内联操作引导]
```

## discover 输出

```
已从发现会话创建：
- 1 个业务机会（OPP-xxx）
- 1 个专题（EPIC-xxx）
- N 个业务需求（BR-xxx ~ BR-xxx）
- M 个产品功能（PF-xxx ~ PF-xxx）
→ /pace-biz decompose EPIC-xxx 继续细化
→ /pace-plan next 排入迭代
```

## import 输出

```
导入完成（来自 N 个文件）：
- 新增：X 个 BR + Y 个 PF
- 丰富：Z 个已有实体
- 跳过：W 个重复项
→ /pace-biz align 检查战略对齐度
→ /pace-plan next 排入迭代
```

## infer 输出

```
代码库推断完成：
- 新增追踪：X 个产品功能
- 技术债务：Y 个待处理项
- 未实现确认：Z 个功能状态已更新
→ /pace-biz align 检查战略对齐度
→ /pace-dev 开始处理优先项
```
