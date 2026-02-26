# 模板导出与应用规程

> **职责**：`/pace-init --export-template` 和 `--from-template` 的详细执行规则。

## 导出（--export-template）

**前置条件**：`.devpace/` 目录存在。

**导出内容**（创建 `.devpace-template/` 目录）：

| 源文件 | 导出处理 |
|--------|---------|
| rules/workflow.md | 直接复制 |
| rules/checks.md | 移除项目特定的 bash 命令路径，保留结构和意图检查 |
| context.md | 移除项目特定的路径和名称，保留通用约定 |
| integrations/config.md | 移除项目特定的 URL 和密钥，保留结构 |

**输出**：`".devpace-template/ 已创建，包含 N 个模板文件。新项目可使用 /pace-init --from-template .devpace-template/ 应用。"`

## 应用（--from-template）

1. 读取模板目录中的文件
2. 执行正常初始化流程（生命周期检测 + 信息收集）
3. 用模板文件覆盖默认模板（workflow.md、checks.md、context.md、integrations/config.md）
4. 继续正常流程（替换占位符、生成 state.md/project.md）
