# 健康检查规程

> **职责**：`/pace-init --verify [--fix]` 的详细执行规则。

## 触发

`/pace-init --verify [--fix]`

## 前置条件

检查 `.devpace/` 目录存在，不存在则提示"未找到 .devpace/ 目录，请先运行 /pace-init"。

## 校验清单

**优先使用脚本**（确定性校验，比逐文件手动检查更快更可靠）：

```
Bash: node ${CLAUDE_SKILL_DIR}/scripts/validate-schema.mjs .devpace
```

脚本覆盖 state/project/CR/PF/BR 五种文件类型的结构化校验，输出 JSON `{ valid, total, errors, warnings, results[] }`。脚本通过后，仅需对脚本未覆盖的文件类型（rules/、iterations/、releases/、integrations/、metrics/、CLAUDE.md）进行手动校验。

**脚本不可用时**：遍历 `.devpace/` 所有文件，按对应 Schema 逐一校验：

| 文件 | Schema | 校验内容 |
|------|--------|---------|
| state.md | state-format.md | 必需 section、版本标记 |
| project.md | project-format.md | 项目名、价值功能树 section |
| rules/workflow.md | — | 文件存在且非空 |
| rules/checks.md | checks-format.md | Gate section 存在、至少 2 条检查 |
| context.md | context-format.md | section 结构合规 |
| backlog/CR-*.md | cr-format.md | 必填字段存在 |
| iterations/*.md | iteration-format.md | section 结构合规 |
| releases/*.md | release-format.md | section 结构合规 |
| integrations/config.md | integrations-format.md | section 结构合规 |
| metrics/dashboard.md | — | 文件存在且非空 |
| metrics/insights.md | insights-format.md | 条目格式合规 |
| CLAUDE.md | — | devpace section 标记存在 |

## 输出格式

```
.devpace/ 健康检查报告：
✅ state.md — 正常
✅ project.md — 正常
⚠️ rules/checks.md — 缺少 Gate 2 section（可自动修复）
❌ backlog/CR-001.md — 缺少"意图"字段（需人工处理）
✅ CLAUDE.md — devpace section 存在

总计：N 个文件，M 正常，X 可修复，Y 需人工
```

## --fix 行为

当指定 `--fix` 时，自动修复可修复项：

- 缺失的 section → 补充空 section 模板
- 缺失的版本标记 → 补充当前版本标记
- 格式问题（多余空行、缺失分隔符）→ 规范化
- **不修改语义内容**（不改用户写的文本、不删除用户数据）

修复后重新输出报告。
