# dry-run 规程

> **职责**：`/pace-init --dry-run` 的详细执行规则。

## 触发

`/pace-init --dry-run [其他参数]`

## 行为

执行完整的检测和规划逻辑（生命周期检测、工具链检测、信息收集等），但不写入任何文件。

## 输出格式

```
/pace-init 预览（dry-run 模式，不写入文件）：

检测结果：
- 项目阶段：[阶段描述]
- 项目名称：[名称]（来源：[package.json/目录名/...]）
- 项目描述：[描述]（来源：[...]）
- 技术栈：[语言] + [框架]
- 工具链：[测试/lint/typecheck 工具]

将创建的文件：
.devpace/
├── state.md          — 项目状态追踪（[N] 行）
├── project.md        — 项目定义和价值功能树
├── backlog/          — CR 存放目录
├── rules/
│   ├── workflow.md   — 工作流规则
│   └── checks.md     — 质量检查（[M] 条检查项）
├── context.md        — 技术约定（[K] 条约定）
└── integrations/
    └── config.md     — 集成配置（CI/CD + 版本管理）

CLAUDE.md — 将注入 devpace 研发协作 section

确认初始化？运行 `/pace-init [项目名称]` 开始。
```
