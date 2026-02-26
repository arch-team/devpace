# history 变更历史查询规程

> **职责**：history 子命令的完整流程。自包含，按 SKILL.md 路由表按需加载。

> OPT-11：聚合分散在四处的变更历史。

## 触发

- `history <PF名>` → 查询单个功能的变更轨迹
- `history --all` → 项目级变更时间线
- `history --recent N` → 最近 N 条变更记录（默认 5 条）

## 数据源聚合

| 数据源 | 内容 |
|--------|------|
| iterations/iter-*.md + current.md 变更记录表 | 迭代级变更事件 |
| backlog/CR-*.md 事件表 | CR 级状态变更 |
| project.md / features/PF-*.md 的 history 注释 | PF 级变更注释 |
| git log（commit message 含 `change(`） | 代码级变更记录 |

## 输出格式

**单 PF 轨迹**：

```
「[功能名]」变更历史（共 N 条）：

[日期] [类型] [描述] — [影响摘要]
[日期] [类型] [描述] — [影响摘要]
...
```

**项目级时间线**：按日期倒序，聚合所有功能的变更事件。

**变更频率告警**：查询结果中如果同一 PF 变更 > 3 次，主动提示："功能「[名称]」已变更 [N] 次，需求可能不够稳定，建议与利益相关方确认。"

## 降级

降级模式下 history 仅可查询 git log（commit message 搜索），其他数据源不可用。
