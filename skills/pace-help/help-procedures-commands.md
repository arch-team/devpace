# help-procedures-commands — 动态命令列表

> 由 SKILL.md 路由表加载。`commands` 子命令时读取。

## Step 1：扫描所有 Skill

Glob `skills/pace-*/SKILL.md` 获取所有 Skill 文件列表。排除：
- `pace-help` 自身（避免递归）
- 以 `-workspace` 结尾的目录（workspace 变体，不独立列出）

## Step 2：读取 description

逐一读取每个 SKILL.md 的 frontmatter `description` 字段（仅读 YAML 头，不读全文）。

## Step 3：分层输出

按以下 5 层分组，从 description 中提取触发关键词生成中文一句话摘要。

### 默认输出（核心层）

$ARGUMENTS 为 `commands`（无 `all` 修饰）时，只输出核心层：

```
devpace 核心命令：

  /pace-init    — 初始化项目，对话式引导创建 .devpace/
  /pace-dev     — 开始开发、推进任务、通过质量门禁
  /pace-status  — 查看项目状态和进度
  /pace-review  — 提交变更审核
  /pace-next    — 获取下一步建议

输入 `/pace-help commands all` 查看全部命令（含进阶和专项）。
输入 `/pace-help <命令名>` 查看某个命令的详细用法。
```

### 完整输出（`commands all`）

$ARGUMENTS 为 `commands all` 时，输出全部 5 层：

**分层定义**（硬编码，与 rules §3 保持一致）：

| 层级 | 命令 | 说明 |
|------|------|------|
| 核心 | pace-init, pace-dev, pace-status, pace-review, pace-next | 日常开发必备 |
| 业务 | pace-biz | 业务规划与需求管理（含子命令） |
| 进阶 | pace-change, pace-plan, pace-retro, pace-guard, pace-sync, pace-role | 管理增强 |
| 专项 | pace-release, pace-test, pace-feedback, pace-theory, pace-trace, pace-help | 特定场景 |
| 系统 | pace-learn, pace-pulse | Claude 自动调用，无需手动触发 |

输出格式（每条一行）：

```
/pace-xxx — [从 description 提取的中文一句话摘要]
```

系统层命令标注"（自动调用）"，不鼓励手动触发。

## Step 4：导航提示

末尾附：`想了解某个命令的详细用法？输入 /pace-help <命令名>`
