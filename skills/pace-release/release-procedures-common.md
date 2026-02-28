# 发布管理共享规则

> **职责**：Release 核心操作（create/deploy/verify/close）共享的规则和推断逻辑。核心子命令执行前加载本文件。
>
> **自包含子命令不加载本文件**：wizard/changelog/tag/rollback/notes/branch/scheduling/status 各自独立。

## §0 速查卡片

- **版本推断规则**：breaking→major · feature→minor · defect/hotfix-only→patch · 始终展示推断依据
- **发布管理规则**：可选性 + 候选收集 + 状态机 + 人类确认 + 自动关闭 + 主动编排
- **Release 关闭连锁更新**：8 步链（工具操作 3 步 + 状态级联 5 步），执行规程见 close.md
- **已纳入 Release 的 CR 变更**：影响分析→高/低风险判定→deployed 不允许修改
- **集成管理规则**：手动摄入始终可用 + 集成是增强不是前置 + 编排不替代 CI/CD

## 版本推断规则（SSOT）

所有版本号推断统一使用本节规则。create 和 version 子命令引用此处，不各自维护。

### 推断优先级（从高到低）

1. **包含 breaking change** → major 版本递增（如 1.2.0 → 2.0.0）
2. **包含 feature（无 breaking）** → minor 版本递增（如 1.2.0 → 1.3.0）
3. **仅 defect/hotfix（无 feature）** → patch 版本递增（如 1.2.0 → 1.2.1）
4. 用户可自定义版本号

### Breaking change 识别

扫描候选 CR 的标题和描述，检测以下信号：
- CR 标题或描述包含关键词：`BREAKING`、`breaking change`、`不兼容`、`破坏性变更`
- CR 元数据中存在 `breaking: true` 标记（可选字段）
- 如检测到 breaking → 展示推断依据：`"建议 v2.0.0（CR-{xxx} 标记为 breaking change：{原因}）"`

### 推断依据展示

版本号建议时始终说明理由，让用户做出知情决策：
```
建议版本号：v1.3.0
推断依据：包含 2 个 feature CR（CR-001, CR-004），无 breaking change → minor bump
确认版本号？[v1.3.0 / 自定义]
```

## 发布管理规则

### Release 流程

```
/pace-release create → Gate 4 → staging → deploy确认 → deployed → verify通过 → verified → close → closed
                                              │                                      │
                                              └→ rolled_back                         └→ changelog + version + tag
```

### Release 规则

- **可选性**：`.devpace/releases/` 不存在或无 Release 文件时，所有 Release 行为静默跳过
- **候选收集**：仅 merged 且未关联 Release 的 CR 可纳入新 Release
- **状态机**：staging → deployed → verified → closed + deployed → rolled_back
- **人类确认**：deployed 和 verified 状态转换需人类确认
- **自动关闭**：verified → closed 由 Claude 自动执行（含连锁更新）
- **主动编排**：通过 git/gh 等标准工具执行发布动作，不替代 CI/CD

### Release 关闭连锁更新

Release verified → closed 时自动执行 8 步连锁更新（工具操作 3 步 + 状态级联 5 步）。

**执行规程**：详见 `release-procedures-close.md`（权威源，含进度格式、跳过逻辑、中断恢复）。

### 已纳入 Release 的 CR 变更

当用户对已纳入 Release（staging/deployed）的 CR 发起变更时：

1. **影响分析**：评估变更对 Release 稳定性的影响
2. **高风险变更**：建议从 Release 中移出该 CR，在下个 Release 中包含
3. **低风险变更**：允许原地修改，在 Release 部署记录中注明
4. **已 deployed 的 Release**：不允许修改包含的 CR，发现问题走 /pace-feedback report 创建新 defect CR

## 集成管理规则

### 集成原则

- **手动摄入始终可用**：即使无集成配置，所有功能通过手动输入可用
- **集成是增强不是前置**：集成配置提供自动化便利，但不是必需
- **编排不替代**：devpace 编排和调用用户的工具（git/gh/npm），不替代 GitHub Actions/Jenkins

### 集成配置使用

当 `integrations/config.md` 存在时：
- /pace-release create：Gate 4 系统级检查（构建/CI/完整性）
- /pace-release deploy：可选执行部署命令
- /pace-release verify：自动执行验证命令
- /pace-release version：读取版本文件配置进行 bump
- /pace-release tag：读取 Tag 前缀配置
- /pace-feedback：根据告警映射自动建议严重度
- 节奏检测：可检查部署相关信号

### 降级行为

当无集成配置时：
- 所有功能正常工作，仅需手动输入更多信息
- 不提示"请先配置集成"——集成是可选增强
- changelog 始终可用（从 CR 元数据生成，不依赖集成配置）
- version/tag 提示用户手动操作
