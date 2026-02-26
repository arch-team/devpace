---
description: Use when user says "初始化", "pace-init", "开始追踪", "初始化研发管理", "新项目", "项目管理", "set up devpace", "健康检查 devpace", "重置 devpace", "预览初始化", or wants to set up, verify, or reset project development tracking.
allowed-tools: AskUserQuestion, Write, Read, Glob, Bash
argument-hint: "[项目名称] [full] [--from <路径>...] [--import-insights <路径>] [--verify [--fix]] [--dry-run] [--reset [--keep-insights]] [--export-template] [--from-template <路径>] [--interactive]"
model: sonnet
disable-model-invocation: true
---

# /pace-init — 初始化项目开发节奏管理

从模板初始化当前项目的 `.devpace/` 目录。默认执行最小初始化（自动检测项目生命周期阶段，按阶段适配行为），`full` 执行分阶段完整流程，`--from` 从文档自动生成功能树。支持 `--verify`（健康检查）、`--reset`（重置）、`--dry-run`（预览）等子命令。

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

## 流程

### Step 0：前置检查与路由

**子命令路由**（优先级高于初始化流程）：

- `--verify` → 健康检查流程
- `--reset` → 重置流程
- `--export-template` / `--from-template` → 模板管理流程

**标志处理**：

- `--dry-run` → 设置 dry-run 标志，继续正常流程但不写入任何文件

**版本与状态检测**：检查 `.devpace/state.md` 存在性和版本标记，决定全新初始化、增量迁移或提示重置（规则见 `init-procedures-core.md` §8）。

### Step 1-4：初始化执行

根据参数读取对应规程文件执行（仅读取匹配路径的规程文件）：

| 参数 | 执行规程 |
|------|---------|
| （默认）`[项目名]` | `init-procedures-core.md` |
| `full` | `init-procedures-core.md` + `init-procedures-full.md` |
| `--from <路径>...` | `init-procedures-core.md` + `init-procedures-from.md` |
| `--import-insights <路径>` | `init-procedures-from.md`（可与初始化组合或独立使用） |
| `--verify [--fix]` | `init-procedures-verify.md` |
| `--dry-run` | `init-procedures-dryrun.md` |
| `--reset [--keep-insights]` | `init-procedures-reset.md` |
| `--export-template` / `--from-template` | `init-procedures-template.md` |
| （迁移触发时） | `init-procedures-core.md` §8 迁移框架 |

## 输出

初始化完成的 `.devpace/` 目录 + 确认摘要。`--dry-run` 时仅输出预览。`--verify` 时输出健康报告。`--reset` 时输出清理确认。
