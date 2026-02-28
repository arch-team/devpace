# push — 推送状态到外部（核心流程）

> **职责**：定义 /pace-sync push 子命令的核心执行步骤，含语义 Comment 和输出格式。高级特性（dry-run 预览、Gate 结果同步）见 `sync-procedures-push-advanced.md`。

## 输入

`$1` = CR-ID（可选，省略则推送所有已关联 CR）

**模式检测**：`$ARGUMENTS` 包含 `--dry-run` 时进入预览模式（加载 `sync-procedures-push-advanced.md`）。

## 执行步骤

1. 读取 sync-mapping.md 关联记录
   - 关联记录为空 → 输出"当前没有已关联的外部实体。用 /pace-sync link CR-xxx #Issue编号 创建关联。"并退出
2. 对每个目标 CR：
   a. 读取 CR 当前状态
   b. 查询状态映射表 → 获取对应外部状态
   c. 执行适配器"获取状态"操作 → 查询外部当前状态
   d. **外部实体状态预检查**：按适配器"状态预检查"规则验证外部实体可更新。不可更新 → 输出警告并跳过
   e. 比较：一致 → 跳过，不一致 → 执行更新
   f. **dry-run 模式**：见 `sync-procedures-push-advanced.md` §1
   g. 执行适配器"状态更新策略"中对应的操作
   h. 生成语义 Comment（见下方 §1）并执行适配器"添加评论"操作
   i. 更新 sync-mapping.md 最后同步时间
   j. **限流保护**：按适配器限流规则执行（含等待、重试、跳过逻辑）
3. 输出同步结果（见下方 §2）

## §1 语义 Comment 生成规则

Claude 读取 CR 上下文后生成语义丰富的 Comment，而不是套用固定模板。

**信息采集**：
1. CR 标题和意图描述
2. **状态转换上下文**：从哪个状态转换以及原因（如"从 developing 进入 verifying：所有接受标准的代码实现已完成"）
3. 最近的 Gate 结果（如有）
4. 关键验收条件达成情况（如有）
5. **变更管理摘要**（如有）：CR 经历 /pace-change 时附带变更摘要
6. **PR 链接**（如有）：CR 关联 git branch 时附带 PR 链接

**Comment 格式**：
```
🔄 [{状态}] {CR 标题}

{1-2 句上下文说明，含状态转换原因}

{可选：变更管理摘要（仅经历 /pace-change 时）}
{可选：PR 链接（仅存在时）}
{仅在 merged 时附加：关键交付摘要}
```

**约束**：
- 不超过 8 行
- 不包含 devpace 内部术语（如 checkpoint、state.md）
- 信息采集失败时回退到简单格式：`🔄 [{状态}] {CR 标题}`
- 为同一 CR 的多次 push 生成连续叙事，而非独立片段

## §2 同步结果输出格式

输出格式根据推送 CR 数量自动调整：

**单 CR push**：简化为 1 行 + 外部链接
```
CR-003 → #{编号} ✅ developing → in-progress ({完整外部URL})
```

**批量 push（2+ CR）**：表格 + 汇总行
```
| CR | 外部链接 | 状态 | 外部操作 | 结果 |
|----|---------|------|---------|------|
| CR-003 | [#42](URL) | developing | 更新标签 → in-progress | ✅ |
| CR-005 | [#18](URL) | merged | 关闭 Issue + done 标签 | ✅ |
| CR-007 | [#23](URL) | developing | — | ⏭️ 已一致 |

汇总：2 已同步 / 1 已一致（跳过） / 0 失败
```

**外部链接要求**：外部实体编号附带完整 URL，便于终端点击跳转。URL 从 sync-mapping.md 平台配置的"连接"字段拼装。

**降级**：关联记录为空 → 提示 link。平台工具不可用 → 报错并提示安装。
