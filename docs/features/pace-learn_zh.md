# 经验学习（`/pace-learn`）

devpace 的学习引擎——双模式知识管理，从 CR 生命周期事件中自动提取经验 pattern，同时提供手动知识库探索和管理能力。

## 前置条件

| 需求 | 用途 | 必要? |
|------|------|:-----:|
| `.devpace/` 已初始化 | 项目结构、insights 存储 | 是（自动模式） |
| `.devpace/metrics/insights.md` | Pattern 存储（首次提取时自动创建） | 自动 |

> **优雅降级**：无 `.devpace/` 时，自动模式静默退出——不报错、不提示。手动命令（`list`/`stats`）提示"未找到知识库"并建议 `/pace-init`。

## 快速开始

```
自动模式（事件驱动，无需用户操作）：
  CR 合并              --> 提取成功 pattern
  质量门修复后          --> 提取防御 pattern
  人类打回后            --> 提取改进 pattern

手动模式：
  /pace-learn note "大型重构前需要测试基准线"  --> 手动沉淀
  /pace-learn list --type defense              --> 按类型筛选
  /pace-learn stats                            --> 知识库概览
  /pace-learn export                           --> 导出复用
```

## 双模式架构

| 模式 | 触发 | 用途 | 输出 |
|------|------|------|------|
| **自动**（主体） | CR 合并、Gate 修复、人类打回 | 从 CR 生命周期事件中提取 pattern | 1 行嵌入式通知或静默 |
| **手动** | 用户调用 `/pace-learn <子命令>` | 知识库查询、手动沉淀、导出 | 按子命令输出 |

### 自动模式流程

1. **前置检查**：`.devpace/` 存在？否 → 静默退出。是 → 继续
2. **提取**：从触发 CR 的多维数据源中提炼 pattern
3. **积累**：去重、更新置信度、检测冲突 → 写入 `insights.md`
4. **通知**：新 pattern → `（经验 +N：[标题]）` | 仅验证 → `（经验验证：[标题] → X.X）` | 无发现 → 静默

### 自适应提取

提取深度按 CR 复杂度调整：

| CR 复杂度 | Checkpoint 数 | 最大 pattern 数 |
|:---:|:---:|:---:|
| S | ≤ 3 | 1 |
| M | 4–7 | 2 |
| L / XL | > 7 | 3 |

## 命令参考

### `note <描述>`

在探索模式或非 CR 场景中手动沉淀有价值经验。

```
/pace-learn note "大型重构前需要测试基准线"
→ 已记录：重构前建立测试基准线（置信度 0.5，标签：重构、测试、质量）
```

通过统一写入管道处理（去重、冲突检测）。

### `list [--type TYPE] [--tag TAG] [--confidence MIN]`

按条件筛选和浏览知识库条目。

```
/pace-learn list --type defense --confidence 0.6
→ 知识库（共 12 条，筛选 3 条）：

| # | 标题 | 类型 | 置信度 | 验证 | 最近引用 | 状态 |
|---|------|------|--------|------|---------|------|
| 1 | Auth 变更需要集成测试 | 防御 | 0.8 | 5次 | 2026-02-20 | Active |
| 2 | 大型重构有回归风险 | 防御 | 0.6 | 2次 | 2026-02-15 | Active |
| ...
```

### `stats`

知识库健康概览。

```
/pace-learn stats
→ 知识库统计：

  总条目：15（Active: 12 | Dormant: 2 | Archived: 1）
  类型分布：模式 6 · 防御 4 · 改进 3 · 偏好 2
  置信度分布：高(>0.7) 5 · 中(0.4-0.7) 7 · 低(<0.4) 3
  Top-5 高引用：[列表]
  未引用条目：3（建议关注）
  冲突对：1 组未解决
  衰减预警：2 条将在 30 天内进入 Dormant
```

### `export [--path FILE]`

导出可复用经验供跨项目共享。

- **过滤规则**：置信度 ≥ 0.7，排除偏好类型（项目特定）
- **默认输出**：`./insights-export.md`
- **渐进教学**：知识库首次积累 5+ 条高置信度 pattern 时，一次性提示导出能力

## 知识生命周期

`insights.md` 中的 pattern 遵循三阶段生命周期：

```
Active ──(置信度 < 0.4 或 180 天未引用)──> Dormant
Dormant ──(重新引用或验证)──> Active
Dormant ──(360 天 + 验证 0 次)──> Archived
```

| 阶段 | 条件 | 行为 |
|------|------|------|
| **Active** | 置信度 ≥ 0.4 且 180 天内有引用 | 参与 §12 经验驱动决策 |
| **Dormant** | 置信度 < 0.4 或超 180 天未引用 | 不主动引用；在 `stats` 和 `list` 中可见 |
| **Archived** | Dormant 超 360 天且验证 0 次 | 移至文件末尾；仅手动重新激活 |

### 置信度衰减

长期未引用的 pattern 自动降低置信度：

- **触发**：180 天未被 §12 引用
- **速率**：从第 181 天起每月 −0.1
- **下限**：0.2（保留但不主动使用）
- **重置**：任何 §12 引用停止衰减并更新"最近引用"日期

## 统一写入原则

`pace-learn` 是 `insights.md` 的**唯一写入者**（Single Writer Principle）：

| 来源 | 机制 |
|------|------|
| 自动提取 | CR 合并 / Gate 修复 / 打回事件 |
| `/pace-retro` 回顾 | 产出"学习请求" → pace-learn 管道处理 |
| §12.5 纠正即学习 | 用户确认偏好 → pace-learn 管道处理 |
| `/pace-learn note` | 手动沉淀 → pace-learn 管道处理 |

确保：格式一致、去重逻辑统一、置信度规则统一、冲突检测完备。

## 冲突检测

当新 pattern 与已有 pattern 矛盾时：

1. 两条 pattern 互标**冲突对**
2. 矛盾方置信度 −0.2
3. §12 引用时附注警告："存在矛盾经验，建议在 /pace-retro 中裁决"
4. `/pace-retro` 输出未解决冲突列表供用户裁决

## 跨 Skill 集成

| 集成点 | 行为 |
|--------|------|
| §11 merged 管道 | CR 合并后自动触发 pace-learn（第 2 步） |
| §12 经验引用 | 5 个时机消费 insights.md 辅助决策 |
| §12.5 纠正即学习 | 分级交互：轻微 → 会话结束批量确认；重大 → 即时提问 |
| `/pace-retro` | 双向：retro 批量验证 pattern + defense 汇总改进方向 |
| `/pace-retro` 元分析 | 知识库健康度报告嵌入回顾 |
| 会话开始（§1） | Top-1 防御提醒 + 可展开"还有 N 条，说'更多'查看" |
| 全局经验库 | 置信度 ≥ 0.8 + 验证 ≥ 3 → 自动同步到 `~/.devpace/global-insights.md` |

## 相关资源

- [Insights 格式定义](../../knowledge/_schema/auxiliary/insights-format.md)
- [经验引用规则](../../knowledge/_guides/experience-reference.md)
- [学习效能指标](../../knowledge/metrics.md#学习效能指标)
- [回顾整合](../../skills/pace-retro/retro-procedures.md#retro↔learn-双向整合)
