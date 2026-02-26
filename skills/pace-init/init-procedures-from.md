# --from / --import-insights 规程

> **职责**：`/pace-init --from` 文档驱动初始化和 `--import-insights` 跨项目经验导入的详细执行规则。核心初始化规则见 `init-procedures-core.md`。

## §1 --from 模式增强解析

### 路径处理

- **单文件**：`/pace-init --from prd.md` → 直接读取
- **目录路径**：`/pace-init --from requirements/` → 扫描目录下所有 .md/.txt 文件，综合提取
- **多文件**：`/pace-init --from prd.md --from api-spec.md` → 依次读取，合并提取结果

### 解析规则

| 文档元素 | 映射目标 | 解析方法 |
|---------|---------|---------|
| 用户故事（As a... I want... So that...） | BR（业务需求） | 模式匹配 + 语义分析 |
| 功能列表 / Features section | PF（产品功能）树 | 层级提取 |
| API 端点列表 / OpenAPI paths | PF（按资源分组） | 结构化解析（YAML/JSON） |
| 技术需求 / Non-functional requirements | project.md "项目原则" | 语义分类 |
| 优先级标记（P0/P1/Must/Should） | CR 优先级候选 | 标签提取 |
| 时间线 / Milestones | 迭代规划候选 | 时间点提取 |

### 确认流程

1. 解析完成后展示提取结果的结构化摘要
2. 用 AskUserQuestion 让用户确认或调整
3. 确认后写入 project.md
4. 目录路径解析时，若文件过多（>10），先输出文件列表让用户筛选

### API 规格特殊处理

检测到 OpenAPI/Swagger 文件（.yaml/.json 含 `openapi` 或 `swagger` 关键词）：
- 提取 paths → 按资源（/users、/orders 等）分组为 PF
- 提取 tags → 作为 PF 分组名称
- 提取 descriptions → 作为 PF 描述

## §2 跨项目经验导入（--import-insights）

当用户执行 `/pace-init --import-insights <路径>` 时，在初始化完成后执行经验导入：

1. 读取指定路径的导出文件
2. 校验格式（应符合 insights-format.md 导出文件格式）
3. 按导入规则处理每个条目：
   - 跳过偏好（preference）类型条目
   - 置信度 × 0.8 降级
   - 验证次数重置为 0
   - 追加"导入日期"字段
4. 与已有 insights.md 去重（同标题保留高置信度版本）
5. 写入 `.devpace/metrics/insights.md`（目录不存在则创建）
6. 输出摘要：`"已导入 N 条经验（来自 [项目名]），置信度已降级（×0.8），需在本项目中重新验证。跳过 M 条偏好类型条目。"`

已有 `.devpace/` 的项目也可独立使用此参数（不重新初始化，仅导入经验）。
