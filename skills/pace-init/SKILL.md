---
description: Use when user says "初始化", "pace-init", "开始追踪", "初始化研发管理", "新项目", "项目管理", "set up devpace", "健康检查 devpace", "重置 devpace", "预览初始化", or wants to set up, verify, or reset project development tracking. NOT for current progress overview (use /pace-status) or starting development (use /pace-dev).
allowed-tools: AskUserQuestion, Write, Read, Edit, Glob, Bash
argument-hint: "[项目名称] [full] [--from <路径>...] [--import-insights <路径>] [--verify [--fix]] [--dry-run] [--reset [--keep-insights]] [--export-template] [--from-template <路径>] [--interactive] [--lite]"
model: sonnet
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/pace-init-scope-check.mjs"
          timeout: 5
---

# /pace-init — 初始化项目开发节奏管理

从模板初始化当前项目的 `.devpace/` 目录。默认执行最小初始化（自动检测项目生命周期阶段，按阶段适配行为），`full` 执行分阶段完整流程（含愿景、战略上下文、OBJ 产品维度引导），`--from` 从文档自动生成功能树（支持 Epic 解析）。支持 `--verify`（健康检查）、`--reset`（重置）、`--dry-run`（预览）等子命令。

## 输入

$ARGUMENTS：可选。格式：

- `[项目名称]` — 最小初始化（默认，生命周期感知）
- `[项目名称] full` — 分阶段完整流程
- `[项目名称] --from <路径>...` — 从文档生成功能树（支持目录和多文件）
- `--verify [--fix]` — 健康检查（可选自动修复）
- `--dry-run` — 预览初始化结果，不写入文件
- `--reset [--keep-insights]` — 重置 .devpace/
- `--export-template` — 导出当前配置为可复用模板
- `--from-template <路径>` — 从模板初始化
- `--import-insights <路径>` — 导入跨项目经验
- `--interactive` — 强制对话模式（覆盖自动检测行为）
- `--lite` — 轻量模式：跳过 OPP/Epic/BR 层，project.md 只含 OBJ→PF→CR 三层结构，适合个人小项目

## 流程

### Step 0：前置检查与路由

**子命令路由**（优先级高于初始化流程）：

- `--verify` → 健康检查流程
- `--reset` → 重置流程
- `--export-template` / `--from-template` → 模板管理流程

**标志处理**：

- `--dry-run` → 设置 dry-run 标志，继续正常流程但不写入任何文件

**版本与状态检测**：检查 `.devpace/state.md` 存在性和版本标记，决定全新初始化、增量迁移或提示重置（规则见 `init-procedures-migration.md`）。

### Step 1-4：初始化执行

根据参数读取对应规程文件执行（仅读取匹配路径的规程文件）：

| 参数 | 执行规程 |
|------|---------|
| （默认）`[项目名]` | `init-procedures-core.md` |
| `full` | `init-procedures-core.md` + `init-procedures-full.md` |
| `--from <路径>...` | `init-procedures-core.md` + `init-procedures-from.md` |
| `--import-insights <路径>` | `init-procedures-from.md`（可与初始化组合或独立使用） |
| `--verify [--fix]` | `init-procedures-verify.md` |
| `--dry-run` | `init-procedures-dryrun.md` + `init-procedures-core.md`（仅 §1 检测逻辑，不执行 §2 文件生成） |
| `--reset [--keep-insights]` | `init-procedures-reset.md` |
| `--export-template` / `--from-template` | `init-procedures-template.md` |
| （迁移触发时） | `init-procedures-migration.md` |
| （检测到 monorepo 信号时） | `init-procedures-monorepo.md` |
| `--lite` | `init-procedures-core.md` + `init-procedures-lite.md` |

## 输出

初始化完成的 `.devpace/` 目录 + 确认摘要 + 下一步引导。`--dry-run` 时仅输出预览。`--verify` 时输出健康报告。`--reset` 时输出清理确认。

### 下一步引导（仅正常初始化和 `--full` 时）

确认摘要后追加情境化引导（§15 教学标记 `init_complete` 去重）：

| 项目状态 | 引导内容 |
|---------|---------|
| 有源代码（src/ 或主语言文件 >10 个） | "项目已就绪。建议先 `/pace-biz infer` 从代码推断已有功能和技术债务，再开始规划。" |
| 有需求文档（--from 初始化，功能树已生成） | "项目已就绪。功能树已生成，说'帮我做 [功能名]'开始第一个功能，或 `/pace-plan` 规划迭代。" |
| 空项目（无源代码、无需求文档） | "项目已就绪。说'我想做...'开始头脑风暴需求（`/pace-biz discover`），或直接说'帮我做 [功能名]'快速开始。" |
| 通用（其他情况） | "项目已就绪。说'帮我做 [功能名]'开始第一个功能，`/pace-biz` 规划业务需求，或 `/pace-plan` 规划迭代。" |

**检测规则**：使用 init-procedures-core.md 的信号检测结果（源文件数、git 信号）判定项目状态，不额外扫描。
