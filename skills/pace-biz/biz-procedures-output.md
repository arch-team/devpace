# 业务规划域输出格式索引

> **职责**：索引 /pace-biz 各子命令的输出格式权威源。每个子命令的完整输出模板定义在其对应的 procedures 文件中。

| 子命令 | 输出摘要 | 权威源 |
|--------|---------|--------|
| opportunity | 已捕获业务机会：OPP-xxx -- [描述]，状态：评估中 | biz-procedures-opportunity.md Step 4 |
| epic | 已创建专题：EPIC-xxx -- [名称]，关联 OBJ + MoS | biz-procedures-epic.md Step 8 |
| decompose (Epic) | 已分解 EPIC-xxx：BR 列表 + 依赖关系 + 价值链 | biz-procedures-decompose-epic.md Step 6 |
| decompose (BR) | 已分解 BR-xxx：PF 列表 + 优先级 + 价值链 | biz-procedures-decompose-br.md Step 6 |
| refine | 已精炼 [BR/PF]：变更摘要 + 就绪度变化 | biz-procedures-refine.md Step 4 |
| align | 战略对齐度报告：覆盖率 + 孤立实体 + 就绪度 + 趋势 | biz-procedures-align.md Step 3 |
| view | 业务全景：OPP->EPIC->BR->PF->CR 树视图 + 统计 | biz-procedures-view.md Step 2 |
| discover | 已从发现会话创建：OPP + Epic + BR + PF 汇总 | biz-procedures-discover.md Step 6 |
| import | 导入完成：新增 + 丰富 + 跳过 汇总 | biz-procedures-import.md Step 6 |
| infer | 代码库推断完成：追踪 + 技术债务 + 未实现 汇总 | biz-procedures-infer.md Step 6 |
