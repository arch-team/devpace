# P0-3: pace-release 版本号操作脚本增强

## 概述

增强 pace-release 的版本推断和 Changelog 生成能力，将确定性计算逻辑从 LLM 推理迁移到专用脚本，提高可靠性。

## 现状分析

### 已有脚本

| 脚本 | 用途 | 当前消费者 |
|------|------|-----------|
| `scripts/bump-version.sh` | devpace 自身的版本号更新（4 文件 + CHANGELOG 占位） | devpace 开发者（手动） |
| `scripts/extract-changelog.py` | 从 git log 提取 CHANGELOG | devpace 开发者（手动） |

### pace-release 当前实现

版本推断（`release-procedures-version.md` + `release-procedures-common.md`）：
1. LLM 读取 `integrations/config.md` 获取版本文件路径
2. LLM 扫描候选 CR 标题/描述，检测 breaking change 信号
3. LLM 应用推断规则：breaking→major、feature→minor、defect-only→patch
4. LLM 展示推断依据，请用户确认

Changelog 生成（`release-procedures-changelog.md`）：
- LLM 从 `.devpace/backlog/` CR 文件提取元数据
- LLM 按 Epic→BR→PF 组织内容
- LLM 写入 CHANGELOG.md

### 问题

1. **版本推断不可靠**：breaking change 关键词检测、版本号递增计算是确定性逻辑，LLM 可能遗漏或计算错误
2. **重复造轮子**：`bump-version.sh` 已实现版本号更新但仅服务 devpace 自身，未被 pace-release 使用
3. **Changelog 效率低**：LLM 逐个读取 CR 文件、提取字段、格式化输出，大量 token 消耗在结构化数据处理上

## 方案设计

### 新增脚本 1：版本推断

**文件**：`scripts/infer-version-bump.mjs`

```javascript
#!/usr/bin/env node
/**
 * Infer semantic version bump from CR metadata.
 *
 * Usage: node scripts/infer-version-bump.mjs <devpace-dir> [current-version]
 *
 * Reads merged CRs not yet in a Release, analyzes for breaking/feature/defect,
 * outputs JSON: { current, suggested, bump_type, reasoning[] }
 */
```

**核心逻辑**：

1. 扫描 `.devpace/backlog/CR-*.md`，过滤 `状态: merged` 且未关联 Release 的 CR
2. 对每个候选 CR 提取：
   - 标题
   - 描述/意图
   - 类型（feature/defect/hotfix）
   - breaking 标记（关键词检测：`BREAKING`、`breaking change`、`不兼容`、`破坏性变更`、`breaking: true`）
3. 推断规则应用：
   - 任一 CR 有 breaking → major
   - 任一 CR 类型为 feature（无 breaking）→ minor
   - 全部为 defect/hotfix → patch
4. 读取当前版本号（从 `integrations/config.md` 指定的版本文件，或命令行参数）
5. 计算新版本号（确定性递增）
6. 输出 JSON：

```json
{
  "current": "1.2.0",
  "suggested": "1.3.0",
  "bump_type": "minor",
  "reasoning": [
    "CR-012 (feature): 新增用户搜索功能 → minor",
    "CR-015 (defect): 修复登录超时 → patch",
    "最高级别：minor → 1.2.0 → 1.3.0"
  ],
  "candidates": [
    { "id": "CR-012", "title": "用户搜索", "type": "feature", "breaking": false },
    { "id": "CR-015", "title": "登录超时修复", "type": "defect", "breaking": false }
  ]
}
```

**Skill 集成**：pace-release 的 `version` 子命令在 procedures 中调用 `Bash` 工具执行此脚本，消费 JSON 输出做格式化展示和用户确认。LLM 不再手动扫描和计算，只做展示和交互。

### 新增脚本 2：CR 元数据提取

**文件**：`scripts/extract-cr-metadata.mjs`

```javascript
#!/usr/bin/env node
/**
 * Extract structured metadata from CR markdown files.
 *
 * Usage: node scripts/extract-cr-metadata.mjs <devpace-dir> [--status <状态>] [--release <release-id>]
 *
 * Outputs JSON array of CR metadata objects.
 */
```

**核心逻辑**：

1. 扫描 `.devpace/backlog/CR-*.md`
2. 解析每个 CR 文件，提取结构化字段：
   - 编号、标题、状态、类型
   - 关联 PF、BR、Epic
   - 事件表（创建/完成日期）
   - breaking 标记
3. 支持过滤：`--status merged`、`--release REL-001`
4. 输出 JSON 数组

**复用价值**：此脚本不仅服务 pace-release，也可被 pace-retro（指标计算）、pace-status（概览）、pace-pulse（信号采集）复用。是 P1-2（信号采集引擎）和 P2-1（度量计算引擎）的基础组件。

### Skill 集成方式

pace-release procedures 文件中增加脚本调用指导：

```markdown
## 版本推断（使用脚本）

1. 执行版本推断脚本：
   ```
   Bash: node ${CLAUDE_PLUGIN_ROOT}/scripts/infer-version-bump.mjs .devpace
   ```
2. 解析 JSON 输出，向用户展示推断结果
3. 等待用户确认或自定义版本号
4. 确认后使用 Edit 工具更新版本文件
```

## 设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 脚本语言 | Node.js ESM | 与 hooks/ 基础设施一致，无额外依赖 |
| 输出格式 | JSON | 结构化数据便于 LLM 消费和格式化 |
| CR 解析 | 正则 + 行匹配 | CR 格式由 `_schema/cr-format.md` 契约保证，结构稳定 |
| 集成方式 | Skill procedures 指导 Bash 调用 | 最小侵入，保持 Skill 的 Markdown 指导模式 |
| 脚本位置 | `scripts/`（产品层） | 随 Plugin 分发，用户项目可用 |

## 改动文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `scripts/infer-version-bump.mjs` | **新增** | 版本推断脚本（~120 行） |
| `scripts/extract-cr-metadata.mjs` | **新增** | CR 元数据提取脚本（~150 行），复用基础 |
| `skills/pace-release/release-procedures-version.md` | **修改** | 增加脚本调用指导 |
| `skills/pace-release/release-procedures-common.md` | **无变更** | SSOT 推断规则保留（脚本实现与之对齐） |

## 预期效果

| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| 版本推断可靠性 | LLM 推理（可能遗漏 breaking 信号） | 确定性正则匹配 |
| 版本号计算准确性 | LLM 手动递增（可能算错） | 程序化递增（100% 正确） |
| Token 消耗 | LLM 逐个读取 CR + 推理 | 脚本一次输出 JSON，LLM 仅做展示 |
| 复用性 | 无 | extract-cr-metadata.mjs 可被 3+ Skill 复用 |

## 风险评估

- **风险低**：不改变 pace-release 的用户交互流程，仅将"LLM 手动计算"替换为"脚本计算 + LLM 展示"
- **回退容易**：移除 procedures 中的脚本调用指导即可回退到纯 LLM 模式
- **注意**：CR 文件格式变更（_schema/cr-format.md 更新）时需同步更新脚本的正则解析

## 验证方案

1. 创建测试用 CR 文件（feature/defect/breaking 各一），验证推断输出
2. 在实际 `.devpace/` 项目中执行脚本，与 LLM 推断结果对比
3. 边界测试：空 backlog、全部 defect、多个 breaking、无版本文件配置
