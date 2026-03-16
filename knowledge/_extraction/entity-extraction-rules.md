# 实体提取映射规则

> **职责**：定义从文档元素到 devpace 实体的通用映射关系。/pace-init --from 和 /pace-biz import 共同依赖此参考数据。

## 通用映射表

| 文档元素 | 映射目标 | 解析方法 |
|---------|---------|---------|
| 用户故事（As a... I want... So that...） | BR（业务需求） | 模式匹配 + 语义分析 |
| 功能列表 / Features section | PF（产品功能）树 | 层级提取 |
| API 端点列表 / OpenAPI paths | PF（按资源分组） | 结构化解析（YAML/JSON） |
| 技术需求 / Non-functional requirements | project.md "项目原则" | 语义分类 |
| 优先级标记（P0/P1/Must/Should） | 优先级候选 | 标签提取 |
| 时间线 / Milestones | 迭代规划候选 | 时间点提取 |

## API 规格特殊处理

检测到 OpenAPI/Swagger 文件（.yaml/.json 含 `openapi` 或 `swagger` 关键词）：
- 提取 paths -> 按资源（/users、/orders 等）分组为 PF
- 提取 tags -> 作为 PF 分组名称
- 提取 descriptions -> 作为 PF 描述

## 消费方

| Skill | 用途 |
|-------|------|
| /pace-init --from | 初始化时从文档创建功能树 |
| /pace-biz import | 增量导入时提取实体并执行合并分析 |
