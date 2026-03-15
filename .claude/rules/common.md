# 通用规则

## §0 速查卡片

| 规则域 | 要点 |
|--------|------|
| 语言 | 中文对话/文档，英文保留：CLI、技术术语、代码标识符、文件名 |
| Git | `<类型>(<范围>): <描述>`，类型：feat/fix/docs/refactor/test/chore |
| 命名 | 全部 kebab-case：文件、脚本、Schema、目录 |

## 响应语言

**所有对话和文档必须使用中文。**

例外（保持英文）：CLI 命令、AWS 服务名称、MCP Server 名称、技术术语、代码标识符、文件名、路径。

## Git 提交规范

格式：`<类型>(<范围>): <简短描述>`

### 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能（新 Agent 定义、新 Skill、新 Schema） |
| fix | 修复（Schema 缺陷、脚本错误、Prompt 逻辑） |
| docs | 文档变更（ADR、progress、genesis） |
| refactor | 重构（不改变行为的结构调整） |
| test | 测试（新增或修改测试） |
| chore | 杂项（配置、依赖） |

### 范围

| 范围 | 说明 |
|------|------|
| agents | Agent 定义 |
| skills | Skill 定义 |
| knowledge | Schema、模板 |
| scripts | 通用工具、脚本骨架 |
| hooks | Safety Gate Hook |
| rules | 框架工程规则 |
| docs | 文档 |
| * | 跨范围变更 |

## 文档命名

- Markdown 文件：kebab-case（`agent-engineering.md`）
- 脚本文件：kebab-case（`sanitize.sh`、`_template.sh`）
- Schema 文件：kebab-case（`pattern.json`）
- Agent/Skill 定义：kebab-case 目录名，内部 `SKILL.md` 或 Agent 名
