# apply 变更模板规程

> **职责**：apply 子命令的完整流程。自包含，按 SKILL.md 路由表按需加载。

> OPT-16：支持预定义的变更模板，减少重复操作。

## 模板存储

`.devpace/rules/change-templates.md`（用户可手动创建或由 pace-learn 建议创建）。

## 模板格式

```markdown
## 模板名称

- **类型**：[add|pause|resume|reprioritize|modify]
- **描述**：[模板描述]
- **参数**：[需要用户填写的变量，如 {{功能名}}]
- **动作**：
  1. [预定义步骤 1]
  2. [预定义步骤 2]
```

## 触发

- `apply <模板名>` → 加载模板，填入参数后执行标准流程
- 模板文件不存在 → 提示 "无变更模板。模板文件位于 .devpace/rules/change-templates.md，可手动创建或等 pace-learn 建议。"
