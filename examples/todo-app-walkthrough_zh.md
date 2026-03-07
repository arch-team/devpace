# 端到端演示：Todo App

本演示展示 devpace 管理一个完整的开发周期——从项目初始化到任务合并，包括一次中途需求变更。

## 前置条件 / Prerequisites

- 已安装 [Claude Code CLI](https://claude.ai/code)
- 已安装 devpace（任选一种）：
  - **Marketplace**：`/plugin marketplace add arch-team/devpace-marketplace` 然后 `/plugin install devpace@devpace`
  - **从源码**：`git clone https://github.com/arch-team/devpace.git`

## 准备

```bash
cd ~/projects/my-todo-app

# 如果通过 marketplace 安装，直接启动 Claude Code——devpace 自动加载
claude

# 如果从源码安装，用 --plugin-dir 加载
claude --plugin-dir ~/devpace    # 替换为你克隆 devpace 的实际路径
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

变更处理后，Claude 自动评估测试影响：

> 到期日涉及存储格式变更 → 影响 Task CRUD 模块（直接）+ Local Storage（间接）
> 建议重跑：add 命令相关测试（必跑）+ 存储模块测试（建议跑）

后续开发中 Claude 会基于这些影响分析确定回归测试范围，确保变更不破坏已有功能。

## 阶段 4：继续与恢复

### 会话 2 —— 无缝恢复

*第二天，新的 Claude 会话。*

**Claude**（自动）："昨天合并了 add 命令并调整了计划（新增到期日，暂停优先级）。下一个是到期日。继续？"

无需重新解释。Claude 读取了 `state.md`，准确知道当前状况。

**你**："好，继续"

Claude 创建 CR-002 开始实现到期日功能。编写代码、运行测试、Gate 1/2 通过。在请求审批前，Claude 执行验收验证：

> **accept 验证结果**：
> ✅ 用户能为任务设置到期日 — `src/commands/add.ts:45` 新增 `--due` 参数
> ✅ 过期任务在列表中高亮 — `src/display.ts:23` 渲染逻辑已实现
> ⚠️ 到期日支持相对日期（如"明天"）— 仅支持绝对日期，需补充验证

**Claude**："到期日功能准备好审批。验收验证发现 1 项需补充——相对日期目前仅支持绝对格式。要先补全还是直接审批？"

**你**："先审批，相对日期下一轮做"

审批通过后继续处理 list 和 delete 命令。

## 阶段 5：回顾与复盘

所有功能完成后：

**你**：`/pace-retro`

Claude 生成回顾报告：

> **交付**：6 个计划功能中完成 5 个（1 个按计划暂停）
> **质量**：Gate 1 通过率 100%，1 次 Gate 2 失败已捕获并修复
> **变更**：1 次插入 + 1 次暂停，全在同一会话中处理
> **周期时间**：平均任务从创建到合并：不到 1 个会话

## 阶段 6：发布

所有功能合并完毕，准备发布。

**你**："发布 v1.0.0 吧"

Claude 编排发布流程：

> 创建 Release REL-001 (v1.0.0)...
> 包含：CR-001 (add), CR-002 (到期日), CR-003 (delete), CR-004 (list), CR-005 (存储)
>
> **变更日志**（从 CR 元数据自动生成）：
> - **新功能**：添加任务、查看列表、删除任务、到期日设置、本地存储
> - **缺陷修复**：无
>
> **发布说明**（面向用户）：
> - 任务管理：创建、查看和删除任务
> - 到期日：设置截止日期，过期任务高亮显示
>
> **业务影响**：
> - "基本增删改查操作" — 3 个功能交付 ✅
> - MoS "基本增删改查可用" — 已达成 ✅

**你**："发布"

Claude 运行 Gate 4（如已配置），创建 git tag，更新版本号，标记 Release 为已部署。

## 阶段 7：测试策略

在下一个迭代之前，你想正式化测试方案。

**你**：`/pace-test strategy`

Claude 基于 PF 验收标准生成测试策略：

> **Todo App 测试策略**
> | 功能 | 测试类型 | 框架 | 覆盖 |
> |------|---------|------|------|
> | 添加任务 | 单元 + 集成 | Jest | ✅ 3 个测试 |
> | 到期日 | 单元 + E2E | Jest + Playwright | ⚠️ 1 个测试（相对日期未覆盖） |
> | 删除任务 | 单元 | Jest | ✅ 2 个测试 |
>
> **建议**：为到期日高亮添加 E2E 测试。考虑边界场景：空任务列表。

**你**：`/pace-test coverage`

> **需求覆盖率**：8/10 验收标准有测试（80%）
> **缺口**："相对日期"（PF-004）和"空列表展示"（PF-002）未覆盖

Claude 精确定位测试覆盖薄弱之处——基于产品功能而非代码行数。

## 核心要点

| 发生了什么 | devpace 的行为 |
|-----------|---------------|
| 项目启动 | `/pace-init` 引导设置，无需填表 |
| 编写代码 | 自动创建任务、质量门禁、状态追踪 |
| 会话中断 | 恢复时零重新解释 |
| 需求变更 | 影响分析 → 确认 → 原子化更新所有文件 |
| 功能暂停 | 工作以 ⏸️ 保留，随时可恢复 |
| 迭代结束 | 基于实际任务历史的数据驱动回顾 |
| 版本发布 | 自动生成变更日志、发布说明和业务影响 |
| 测试策略 | 基于需求的覆盖分析，而非代码覆盖率 |

用户从未输入过任务 ID，从未编辑过状态文件，从未学过 BizDevOps 术语。devpace 管理节奏；开发者只需写代码。
