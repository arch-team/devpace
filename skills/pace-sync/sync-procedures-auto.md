# auto — 自动关联与自动创建

> **职责**：CR 创建后自动尝试关联已有外部 Issue 或创建新 Issue。遵循副产物非前置三阶段模型（suggest→auto→off）。仅在 sync-mapping.md 存在时激活。

## §1 触发条件

**场景**：CR 文件首次写入 `.devpace/backlog/`（状态为 `created`）且 sync-mapping.md 存在。

**触发源**：
- post-cr-update.mjs Hook 检测到新 CR → 输出 ACTION 建议
- Claude 按建议执行本文件步骤

**前置条件**：
1. `.devpace/integrations/sync-mapping.md` 存在
2. CR 状态为 `created`
3. CR 无外部关联（`**外部关联**` 字段为空或不存在）

不满足任一条件 → 静默跳过。

## §2 Auto-link（优先执行）

尝试在外部平台匹配已有 Issue。

**执行步骤**：

1. 读取 CR 标题
2. 执行适配器"列出工作项"操作，获取外部平台 open 状态的实体列表
3. 按标题关键词匹配，筛选相似候选（前 3 个）
4. **有候选**：
   - 展示候选列表：
     ```
     CR-{id} 创建成功。找到可能匹配的外部 Issue：
     1. #{编号} — {标题} ({状态})
     2. #{编号} — {标题} ({状态})
     关联？输入编号选择，或输入 n 创建新 Issue，或直接忽略。
     ```
   - 用户选择 → 执行 `sync-procedures-link.md` §2 标准 link 流程
   - 用户输入 `n` → 执行 §3 Auto-create
   - 用户忽略（无响应/继续其他操作）→ 静默结束
5. **无候选** → 执行 §3 Auto-create

## §3 Auto-create

外部无匹配 Issue 时，建议或自动创建。

**执行步骤**：

1. 读取 sync-mapping.md "自动同步"偏好（§5 配置字段）
2. **偏好为 `suggest`（默认）**：
   ```
   未找到匹配的外部 Issue。是否为 CR-{id} 创建新 Issue？[y/n]
   ```
   - 用户确认 → 步骤 3
   - 用户拒绝 → 静默结束
3. **偏好为 `auto`**：直接执行步骤 4，无需确认
4. **偏好为 `off`**：静默跳过
5. 执行 `sync-procedures-link.md` §6 create 流程（从 CR 元数据创建 Issue 并自动关联）
6. 输出确认：`CR-{id} → #{编号} 已创建并关联`

## §4 首次教学

CR 首次触发 auto-link/create 时（项目范围内首次），在输出前附加教学段落：

```
💡 devpace 检测到同步配置，自动匹配外部 Issue。
   - 修改偏好：编辑 .devpace/integrations/sync-mapping.md "自动同步"字段
   - suggest（默认）：每次询问 | auto：自动创建 | off：关闭自动同步
```

教学仅展示一次。通过 `.devpace/.sync-auto-taught` 标记文件控制（存在则跳过教学）。

## §5 配置字段

sync-mapping-format.md "平台" section 新增字段：

| 字段 | 值 | 说明 |
|------|---|------|
| 自动同步 | `suggest` / `auto` / `off` | CR 创建时的外部同步行为。默认 `suggest` |

- `suggest`：匹配候选后询问用户确认
- `auto`：无候选时自动创建 Issue，有候选时仍询问（避免误关联）
- `off`：不触发自动关联/创建

## §6 降级与容错

| 场景 | 行为 |
|------|------|
| sync-mapping.md 不存在 | 静默跳过（不影响 CR 创建） |
| 平台工具（gh）不可用 | 输出提醒"外部同步不可用：gh CLI 未安装或未认证"，CR 创建正常完成 |
| 网络错误 / API 限流 | 输出提醒"外部同步暂时不可用"，CR 创建正常完成 |
| auto-link 候选搜索失败 | 回退到 auto-create 建议 |

**核心原则**：自动同步失败不阻断 CR 创建流程。
