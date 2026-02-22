# 端到端演示：Todo App

本演示展示 devpace 管理一个完整的开发周期——从项目初始化到任务合并，包括一次中途需求变更。

## 准备

```bash
# 在你的项目目录中加载 devpace 插件
cd ~/projects/my-todo-app
claude --plugin-dir /path/to/devpace
```

## 阶段 1：初始化

**你**：`/pace-init my-todo-app`

**Claude** 问一个问题：

1. *用一句话描述这个项目做什么？*
   → "A CLI todo app with local storage"

Claude 生成最小 `.devpace/`：

```
.devpace/
├── state.md          # "目标: A CLI todo app, 无进行中工作"
├── project.md        # 项目名 + 描述（功能树随工作自动生长）
├── backlog/          # 空（任务在工作时创建）
└── rules/
    ├── workflow.md   # 标准任务状态机
    └── checks.md     # "npm test" + "npm run lint"（自动检测）
```

没有业务目标、没有功能列表、没有迭代计划。只有骨架——其他一切随工作自动生长。

> **想要完整设置？** 使用 `/pace-init my-todo-app full` 进行引导式 6 步配置（目标、功能、迭代、质量检查）。

## 阶段 2：日常开发

### 会话 1 —— 开始编码

**你**："帮我实现 task add 命令"

Claude 自动进入**推进模式**：
- 创建 `CR-001`（你不会看到这个 ID）
- 编写代码，运行测试
- Gate 1 通过（lint + 测试）
- Gate 2 通过（集成检查）
- 推进到待审批状态

**Claude**："task add 命令已准备好审批。支持 `todo add 'Buy milk' --priority high`。要审批吗？"

**你**：`/pace-review`

Claude 展示摘要：
> **变更文件**：`src/commands/add.ts`、`src/storage.ts`
> **原因**：实现带优先级支持的任务创建
> **测试**：5 个新测试，全部通过

**你**："没问题，批准"

Claude 合并任务。功能树更新：

```
MVP
├── [✅] Task CRUD
│   ├── [✅] Add command
│   ├── [ ] List command
│   └── [ ] Delete command
├── [ ] Priority levels
└── [ ] Local file storage
```

这是你的首个合并任务，devpace 展示简短回顾：

> devpace 在这次变更中做了什么：自动跟踪任务链路 → 质量检查 → 等待你审批 → 合并后更新所有关联状态。
> 下次需求变了，devpace 会先分析影响再调整，避免连锁混乱。
> 会话中断后重新开始，devpace 自动恢复上下文，无需重新解释。

## 阶段 3：需求变更

首个任务合并后，优先级发生变化。

**你**："我们需要先加上到期日功能，再做 list 和 delete。优先级功能先暂停。"

Claude 检测到两个变更并运行影响分析：

> **变更 1：插入"到期日"**
> - 在 Task CRUD 下新增功能
> - 影响：存储格式（需要迁移字段）
> - 容量：当前迭代可容纳
>
> **变更 2：暂停"优先级"**
> - 功能标记 ⏸️
> - 无进行中的任务受影响
> - 工作已保留，可随时恢复
>
> 执行这两项变更？

**你**："是的"

Claude 一次性更新所有内容：
- `project.md` — 功能树添加 ⏸️ 标记和新功能
- `state.md` — 更新下一步
- `iterations/current.md` — 重排计划

更新后的功能树：

```
MVP
├── [✅] Task CRUD
│   ├── [✅] Add command
│   ├── [ ] List command
│   ├── [ ] Delete command
│   └── [ ] Due dates         ← 新增
├── [⏸️] Priority levels      ← 已暂停
└── [ ] Local file storage
```

## 阶段 4：继续与恢复

### 会话 2 —— 无缝恢复

*第二天，新的 Claude 会话。*

**Claude**（自动）："昨天合并了 add 命令并调整了计划（新增到期日，暂停优先级）。下一个是到期日。继续？"

无需重新解释。Claude 读取了 `state.md`，准确知道当前状况。

**你**："好，继续"

Claude 为到期日创建 CR-002，实现、运行门禁、请求审批。流程相同。然后继续处理 list 和 delete 命令。

## 阶段 5：回顾与复盘

所有功能完成后：

**你**：`/pace-retro`

Claude 生成回顾报告：

> **交付**：6 个计划功能中完成 5 个（1 个按计划暂停）
> **质量**：Gate 1 通过率 100%，1 次 Gate 2 失败已捕获并修复
> **变更**：1 次插入 + 1 次暂停，全在同一会话中处理
> **周期时间**：平均任务从创建到合并：不到 1 个会话

## 核心要点

| 发生了什么 | devpace 的行为 |
|-----------|---------------|
| 项目启动 | `/pace-init` 引导设置，无需填表 |
| 编写代码 | 自动创建任务、质量门禁、状态追踪 |
| 会话中断 | 恢复时零重新解释 |
| 需求变更 | 影响分析 → 确认 → 原子化更新所有文件 |
| 功能暂停 | 工作以 ⏸️ 保留，随时可恢复 |
| 迭代结束 | 基于实际任务历史的数据驱动回顾 |

用户从未输入过任务 ID，从未编辑过状态文件，从未学过 BizDevOps 术语。devpace 管理节奏；开发者只需写代码。
