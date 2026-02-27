# 发布管理执行规程——Create

> **职责**：创建新 Release，收集候选 CR，版本号建议，生成 Release 文件。
>
> **加载 common.md**：本文件与 `release-procedures-common.md` 配合使用。版本推断规则在 common.md 中（SSOT）。
>
> **可选追加**：CR > 3 或有 integrations/config.md 时追加加载 `release-procedures-create-enhanced.md`（依赖检测 + Readiness Check + 影响预览 + Gate 4）。

## §0 速查卡片

- **候选收集**：扫描 `.devpace/backlog/` → merged 且未关联 Release → 按类型排序展示
- **创建流程**：用户确认范围 → REL-xxx.md → 状态 staging → 更新 CR 关联 → 更新 state.md
- **版本建议**：引用 common.md 版本推断规则（SSOT） → 展示推断依据 → 用户确认

## 候选 CR 收集

1. 扫描 `.devpace/backlog/` 所有 CR 文件
2. 筛选条件：状态为 `merged` 且无"关联 Release"字段（或字段为空）
3. 按类型排序展示：hotfix > defect > feature

## 候选展示格式

```
## Release 候选 CR

| CR | 标题 | 类型 | PF | 合并日期 |
|----|------|------|-----|---------|
| CR-001 | [标题] | feature | PF-001 | 2026-02-20 |
| CR-003 | [标题] | defect | PF-002 | 2026-02-21 |

共 N 个候选 CR。全部纳入还是选择部分？
```

## Release 创建

1. 用户确认纳入范围后，创建 REL-xxx.md
2. ID 自增：扫描 `.devpace/releases/` 最大编号 +1
3. 状态初始化为 `staging`
4. 自动填充验证清单（默认 4 项 + 项目自定义）
5. 更新各 CR 文件的"关联 Release"字段为 REL-xxx
6. 更新 state.md 发布状态段
7. 可选：如果 integrations/config.md 配置了发布分支模式，创建 `release/v{version}` 分支

## 回滚后候选预填

当扫描到 `.devpace/releases/` 中存在 `rolled_back` 状态的 Release 时，自动预填候选 CR：

1. 读取最近 rolled_back Release 包含的 CR 列表
2. 读取因回滚创建的 defect/hotfix CR（关联该 Release 的修复 CR）
3. 预填候选列表（区分原有 CR 和修复 CR）：

```
## Release 候选 CR

### 来自 REL-{xxx}（已回滚）的可复用 CR
| CR | 标题 | 类型 | PF | 说明 |
|----|------|------|-----|------|
| CR-001 | [标题] | feature | PF-001 | 原 Release 包含，非问题来源 |
| CR-003 | [标题] | defect | PF-002 | 原 Release 包含，非问题来源 |

### 修复 CR（关联回滚原因）
| CR | 标题 | 类型 | PF | 状态 |
|----|------|------|-----|------|
| CR-006 | [标题] | hotfix | PF-004 | merged ✅ |

### 新增 merged CR
| CR | 标题 | 类型 | PF | 合并日期 |
|----|------|------|-----|---------|
| CR-007 | [标题] | feature | PF-005 | 2026-02-25 |

全部纳入还是选择部分？
```

4. 用户可自由选择/取消任何 CR（预填仅为建议，不强制）
5. 如果回滚后的 defect/hotfix CR 尚未 merged → 在修复 CR 列表中标注"⏳ 未完成"并建议先完成修复

## 版本号建议

使用 common.md 的"版本推断规则（SSOT）"章节进行版本号推断。

推断流程：
1. 扫描候选 CR 的标题和描述，检测 breaking change 信号
2. 根据 CR 类型组合确定推断级别（major/minor/patch）
3. 展示推断依据后请用户确认版本号
