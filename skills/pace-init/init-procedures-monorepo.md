# Monorepo 感知初始化规程

> **职责**：Monorepo 项目的初始化增强规则。仅在检测到 monorepo 信号时由 `init-procedures-core.md` 引导加载。

## 信号检测

| 文件 | Monorepo 工具 |
|------|-------------|
| `pnpm-workspace.yaml` | pnpm workspace |
| `nx.json` | Nx |
| `turbo.json` | Turborepo |
| `lerna.json` | Lerna |
| `rush.json` | Rush |

## 组织方式选择

检测到 monorepo 信号时，使用 AskUserQuestion 询问组织方式：

**A) 根目录单一 .devpace/（推荐小型 monorepo，<5 个子包）**：
- 标准初始化流程
- context.md 记录 monorepo 结构和子包列表
- PF 树按子包组织

**B) 根共享 + 子包独立追踪（大型 monorepo，≥5 个子包）**：
- 根 `.devpace/`：rules/（共享规则）+ context.md（全局约定）
- 子包 `.devpace/`：state.md + project.md + backlog/（独立追踪）
- 子包的 rules/ 继承根目录（不重复创建）

## 子包发现

- 从 monorepo 配置文件读取 workspace 列表
- 验证子包目录存在
- 为每个子包生成独立的 state.md 和 project.md
