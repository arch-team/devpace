# 发布管理执行规程——Release Notes 生成

> **职责**：面向用户的发布说明，按 BR/PF 组织，支持角色视角（`--role biz|ops|pm`）。
>
> **自包含**：本文件独立执行，不需要加载其他 procedures 文件。

## §0 速查卡片

- **与 Changelog 的区别**：Changelog 按 CR 类型/开发者视角 · Notes 按 BR→PF/产品用户视角
- **生成条件**：≥1 feature CR 或 ≥2 CR 或用户明确请求
- **角色视角**：`--role biz`（业务影响报告）· `--role ops`（部署手册）· `--role pm`（功能交付清单）

## 与 Changelog 的区别

| 维度 | Changelog | Release Notes |
|------|-----------|---------------|
| 受众 | 开发者 | 产品用户 |
| 组织方式 | 按 CR 类型（Features/Bug Fixes/Hotfixes） | 按 BR→PF（业务需求→产品功能） |
| 粒度 | CR 级别（每个变更一行） | PF 级别（每个功能一段描述） |
| 语言 | 技术语言（含 CR/PF 编号） | 产品语言（无技术编号） |
| 生成时机 | close 时自动 | 用户请求或 close 时提示 |

## 生成流程

1. 读取 Release 包含的 CR 列表
2. 对每个 CR 提取关联的 PF 和 BR
3. 按 BR 分组，BR 下按 PF 聚合 CR：
   - BR 标题作为分组标题
   - PF 标题作为功能描述
   - 同一 PF 下的多个 CR 合并为一段描述
4. 用产品语言重写（去除 CR/PF 编号，改为用户可读的描述）

### Release Notes 格式

```
## What's New in v{version}

### 用户体验提升
- **用户认证**：新增登录功能，支持邮箱和手机号两种方式
- **搜索功能**：修复了搜索结果排序不正确的问题

### 系统稳定性
- **支付系统**：修复了在高并发场景下的崩溃问题
```

## 业务影响摘要

Release Notes 末尾追加"业务影响"段，向上追溯 Release 对业务目标的贡献：

```
### Business Impact

- **OBJ-1 "用户体验"**：PF-001 ✅ + PF-002 ✅（2 个功能交付）
- **MoS 推进**："安全登录可用" 达成 ✅ · "OAuth 支持" 仍在进行中
```

**生成流程**：
1. 从 Release 包含的 CR 向上追溯 PF → BR → OBJ
2. 按 OBJ 分组，统计每个 OBJ 下本 Release 交付的 PF 数
3. 读取 project.md MoS checkbox，标注哪些 MoS 因本 Release 而达标或推进
4. 无 MoS 数据时仅输出 PF 交付统计

**规则**：
- **生成条件**（满足任一即可生成）：
  - Release 包含至少 1 个 feature CR（即使只有 1 个 CR，feature 也值得向用户沟通）
  - Release 包含 2+ CR（任何类型组合）
  - 用户明确请求生成
- **单个 defect-only CR 的 Release**：默认不生成（修复类信息对用户价值较低），但 close 时提示"是否为此修复生成 Release Notes？"让用户决定
- 使用产品语言（与 Release Notes 一致，不含 CR/PF 编号）
- 附加到 Release Notes 末尾，不单独成 section

## 角色视角 Release Notes（Communication Kit）

`/pace-release notes` 支持可选的角色参数，生成面向不同利益相关者的发布通知：

### `notes --role biz`（业务视角）

面向管理层/业务方，聚焦 OBJ 推进和 MoS 达成：

```
## Release v{version} — 业务影响报告

### 目标推进
- **OBJ-1 "用户体验"**：达成 MoS "安全登录可用" ✅，OAuth 支持推进至 80%
- **OBJ-2 "系统稳定性"**：紧急修复 1 项，系统可用性恢复

### 关键成果
- 本 Release 交付 N 个产品功能，覆盖 M 个业务需求
- 变更前置时间：平均 X 天（对比上个 Release：↑/↓）
```

### `notes --role ops`（运维视角）

面向运维/SRE 团队，聚焦部署风险和操作要点：

```
## Release v{version} — 部署手册

### 部署信息
- 版本号：v{old} → v{new}
- 包含变更：N 个 CR（feature:A, defect:B, hotfix:C）
- 变更范围：{涉及目录/模块列表}

### 风险评估
- Gate 4 结果：{通过/部分通过}
- 高风险区域：{多 CR 修改的模块}
- 建议监控项：{根据变更内容推荐}

### 回滚方案
- 回滚版本：v{previous}
- 回滚命令：{根据 integrations/config.md 推荐}
- 回滚影响：{列出将失效的功能}
```

### `notes --role pm`（产品视角）

面向产品经理，聚焦功能交付和用户影响：

```
## Release v{version} — 功能交付清单

### 新功能
- **PF-001 用户认证**：完成度 100%（CR-001 ✅）— 用户影响：新增登录功能
- **PF-003 数据管理**：完成度 60%（CR-004 ✅，CR-006 待做）— 导出功能可用

### 修复项
- 搜索排序问题已修复（影响约 15% 搜索请求）

### 下一 Release 预告
- PF-003 剩余 CR 预计下个 Release 完成
```

### 默认行为

不带 `--role` 时沿用现有行为（按 BR/PF 组织的通用 Release Notes）。

## 输出位置

1. 写入 Release 文件的 `## Release Notes` section（含业务影响段）
2. 角色视角 Notes 写入 `## Release Notes ({role})` 独立 section
3. 可选：输出到用户产品根目录的 RELEASE_NOTES.md（用户确认）
