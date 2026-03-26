# entity — 智能同步主流程与多实体支持

> **职责**：定义 /pace-sync 智能同步（默认行为）的完整执行流程，以及被其他子命令共用的实体 ID 解析和扫描能力。

## §1 实体 ID 解析

被 link/unlink/pull 等子命令调用，从 `$1` 参数确定实体类型和目标文件：

| 前缀 | 类型 | 文件位置 |
|------|------|---------|
| EPIC- | epic | `.devpace/epics/EPIC-xxx.md` |
| BR- | br | 优先 `.devpace/requirements/BR-xxx.md` → 回退 project.md 内联 |
| PF- | pf | 优先 `.devpace/features/PF-xxx.md` → 回退 project.md 内联 |
| CR- 或纯数字 | cr | `.devpace/backlog/CR-xxx.md` |

**纯数字默认为 CR**（向后兼容）：`003` → `CR-003`。

**验证**：解析后检查文件是否存在（独立文件）或 project.md 中是否有该 ID（内联实体）。不存在 → 报错提示。

## §2 智能同步主流程

子命令：`/pace-sync`（无参数）或 `/pace-sync sync`

### 步骤

1. **运行变更检测脚本**：
   ```bash
   node skills/scripts/compute-sync-diff.mjs <.devpace 目录路径>
   ```
   解析 JSON 输出 → 获取 `summary`、`entities`（new/changed/unchanged/orphaned）和 `warnings`

2. **呈现变更摘要**（不可跳过）：
   ```
   同步检测：
   - {changed 数} 个实体有变更（列出前 5 个：ID + 变更类型）
   - {new 数} 个新实体未关联（列出全部：ID + 类型 + 标题）
   - {unchanged 数} 个已关联且无变化
   {orphaned > 0 时} - {orphaned 数} 个关联记录对应的实体文件已不存在
   {warnings 非空时}
   ⚠️ 警告：
   - {逐条列出 warnings，如"EPIC-002 在 project.md 中被引用但无独立文件，BR-003/BR-004 无法建立层级关联。建议：运行 /pace-biz epic 创建独立文件"}
   ```

3. **处理未关联实体**（new 列表非空时）：
   - 使用 AskUserQuestion 询问用户：
     - "创建并同步"：为所有新实体创建外部 Issue 并关联
     - "仅同步已关联"：跳过新实体，只推送变更实体
     - "取消"：终止同步

4. **用户确认后执行**（按层级从顶到底）：
   a. **创建新实体的外部 Issue**（若用户选择了"创建并同步"）：
      - 按价值链顺序：Epic → BR → PF → CR
      - 对每个新实体：调用 `sync-procedures-link.md` §6 create 流程
      - 每创建一个，立即通过操作语义"建立父子关系"与已关联的上级建立 sub-issue
   b. **推送变更实体**：
      - 对每个 changed 实体：调用 `sync-procedures-push.md` 核心推送步骤
      - 推送完成后更新 sync-mapping.md 的最后同步时间和内容摘要哈希

5. **输出结果报告**（格式见 SKILL.md 输出 section）

### dry-run 模式

`$ARGUMENTS` 包含 `--dry-run` 时：
- 执行步骤 1-2（检测+呈现）
- 步骤 3 变为：展示"将执行的操作"预览（不询问确认）
  ```
  dry-run 预览：
  - 将创建 2 个 Issue（BR-003, CR-008）
  - 将推送 3 个变更（CR-003 状态更新, EPIC-001 状态更新, PF-002 内容更新）
  - 预计 API 调用：~8 次（创建 2 + 更新 3 + 标签 2 + sub-issue 1）
  ```
- 不执行步骤 4-5

### 错误处理

- 脚本执行失败 → 报错提示，建议检查 .devpace/ 目录完整性
- sync-mapping.md 不存在 → 引导运行 `/pace-sync setup`
- 平台工具不可用（gh CLI 未安装/未认证）→ 按适配器降级行为处理
- 部分实体同步失败 → 继续剩余实体，最终报告中标记失败项

## §3 内容哈希与增量检测

由 `skills/scripts/extract-entity-metadata.mjs` 和 `skills/scripts/compute-sync-diff.mjs` 脚本实现。

**哈希计算规则**（编码在脚本中，此处为参考说明）：

| 实体类型 | 参与哈希的关键字段 |
|---------|-----------------|
| Epic | 标题 + 状态 + BR 列表（编号+状态） |
| BR | 标题 + 状态 + 优先级 + PF 列表 |
| PF | 标题 + 状态 + 验收标准文本 |
| CR | 标题 + 状态 + 验收条件文本 + Gate 结果 |

哈希算法：MD5 前 8 位 hex。变更检测：当前哈希 ≠ 存储哈希 → 标记为 changed。

## §4 层级创建顺序

全量同步创建未关联实体时，严格按价值链从顶到底执行：

```
1. Epic（无父级，最先创建）
2. BR（查找所属 Epic 的外部关联 → 建立 sub-issue）
3. PF（查找所属 BR 的外部关联 → 建立 sub-issue）
4. CR（查找所属 PF 的外部关联 → 建立 sub-issue）
```

**上级关联查找**：
- CR → 从 CR 文件"产品功能"字段提取 PF-ID → 查 sync-mapping.md 关联记录
- PF → 从 PF 文件"BR"字段提取 BR-ID → 查 sync-mapping.md
- BR → 从 BR 文件"Epic"字段提取 EPIC-ID → 查 sync-mapping.md

**上级未关联时**：跳过 sub-issue 建立，仅创建 Issue。输出中标注"（无层级关联——上级未同步）"。

## §5 关联记录迁移

检测到旧格式关联记录（列名为 `CR`、无 `内容摘要哈希` 列）时：

1. 首次同步时自动将列名 `CR` 视为 `实体`（语义等价）
2. 推送成功后补填 `内容摘要哈希` 列
3. 不主动修改旧格式文件结构——仅在下次 link/sync 写入时自然迁移为新格式

## §6 操作语义使用规则

本文件步骤中使用的操作语义（平台无关），Claude 在适配器文件的操作表中查找对应命令执行：

| 操作语义 | 使用场景 |
|---------|---------|
| 创建工作项 | §2.4a 创建新实体的外部 Issue |
| 设置实体类型标记 | §2.4a 创建后标记实体类型 |
| 建立父子关系 | §2.4a/§4 建立 sub-issue 层级 |
| 获取状态 | §2.4b 推送前比对外部状态 |
| 获取实体类型状态映射 | §2.4b 查询目标外部状态 |
| 更新状态标记 | §2.4b 推送状态变更 |
| 添加评论 | §2.4b 推送语义 Comment |
| 生成工作项描述 | §2.4a 生成 Issue body（委托适配器） |

详见 `sync-procedures-common.md` §1 适配器路由 和 `sync-adapter-github.md` 操作表。
