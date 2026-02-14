# 变更请求文件格式契约

> **职责**：定义 CR-xxx.md 文件的结构。Claude 自动创建 CR 时遵循此格式。

## §0 速查卡片

```
文件名：CR-xxx.md（xxx 为自增数字，三位补零）
标题：自然语言描述（不含 ID）
必含：元信息 + 门禁 checkbox + 事件表
门禁从项目 bizdevops/rules/gates.md 复制
```

## 文件结构

```markdown
# [自然语言标题]

- **ID**：CR-xxx
- **产品功能**：[PF 标题]（[PF-ID]）→ [BR 标题]（[BR-ID]）
- **应用**：[应用名称]
- **分支**：[feature/branch-name]
- **状态**：[created | developing | verifying | review_ready | approved | merged]

## 门禁

<!-- 从项目 bizdevops/rules/gates.md 复制对应阶段的检查项 -->
- [ ] [门禁名称]：[描述]
- [ ] ...
- [ ] 人类审批：Code Review 通过

## 事件

| 日期 | 事件 | 备注 |
|------|------|------|
| [日期] | [事件描述] | [备注] |
```

## 状态值

| 状态 | 含义 | 执行者 |
|------|------|--------|
| created | 已创建，未开始 | — |
| developing | 编码、测试中 | Claude 自治 |
| verifying | 集成验证中 | Claude 自治 |
| review_ready | 等待人类审核 | 人类 |
| approved | 已审核，待合并 | Claude |
| merged | 已合并 | — |
| paused | 暂停（保留工作成果，不推进） | 需求变更触发 |

`paused` 状态说明：
- 任何状态都可以转到 paused（需求暂停/砍掉时）
- 恢复时回到暂停前的状态
- 暂停期间保留：分支、代码、门禁进度、事件记录
- CR 文件中增加 `暂停前状态` 字段记录恢复目标

## 命名规则

- 文件名：`CR-001.md`、`CR-002.md`...（三位补零自增）
- ID 自增：扫描 `bizdevops/backlog/` 中现有 CR 文件的最大编号 +1
- 分支名：`feature/` + 标题的 kebab-case 缩写
