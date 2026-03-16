# 发布管理执行规程——Deploy

> **职责**：部署流程，含多环境晋升和路径全景展示。
>
> **加载 common.md**：本文件与 `release-procedures-common.md` 配合使用。

## §0 速查卡片

- **环境晋升**：单环境直接部署 · 多环境按序逐环境 deploy+verify
- **路径全景**：每次操作展示 `[staging ✅] → [canary 👈 当前] → [production] → [完成]`
- **状态转换**：最终环境部署后 staging → deployed

## 环境晋升模式

读取 `integrations/config.md` 的环境表（格式见 `knowledge/_schema/integration/integrations-format.md`）：

1. **单环境或无配置**：直接部署确认（当前行为不变）
2. **多环境**：按环境表行序逐环境部署
   - 从首环境开始，每个环境独立 deploy + verify
   - 当前环境验证通过后，提示晋升到下一环境
   - 最终环境部署后 Release 状态 staging → deployed

晋升流程：
```
staging → deploy(env1) → verify(env1) → deploy(env2) → verify(env2) → ... → deploy(envN) → deployed
```

每次 deploy 在部署记录表追加一行（含环境名称），更新 Release 的"当前环境"字段。

## 晋升路径全景展示

每次 deploy 或 verify 操作时，**首先展示晋升路径全景**，标记已完成和当前位置：

```
晋升路径：[staging ✅] → [canary ✅] → [production 👈 当前] → [完成]
```

标记规则：
- `✅`：该环境已完成 deploy + verify
- `👈 当前`：当前正在操作的环境
- 无标记：尚未到达的环境
- `❌`：该环境验证失败（保留在路径中）

**验证失败提示**：当某环境验证失败时，明确提示：
```
⚠️ [canary] 环境验证失败。
- 已部署环境不受影响（[staging] 仍正常运行）
- 修复问题后运行 /pace-release verify 继续验证当前环境
- 或运行 /pace-release rollback 回滚本次部署
```

## 部署确认

1. 确认 Release 处于 `staging` 状态
2. 询问部署目标环境（如有多环境配置）
   - 多环境模式：自动选择晋升路径的下一个环境
   - 单环境模式：手动选择或使用默认环境
3. 如果 integrations/config.md 配置了部署命令 → 询问用户是否让 devpace 执行
   - 用户确认 → 执行部署命令并报告结果
   - 用户拒绝或无配置 → 用户自行部署，确认已完成
4. 在 Release 部署记录表追加：

```markdown
| 日期 | 环境 | 操作 | 结果 | 备注 |
|------|------|------|------|------|
| 2026-02-21 | production | 部署 | 成功 | [用户备注] |
```

5. Release 状态 staging → deployed
6. 更新 state.md 发布状态段
