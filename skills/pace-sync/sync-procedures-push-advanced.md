# push 高级特性

> **职责**：定义 push 的低频/被动触发特性——dry-run 预览和 Gate 结果同步。仅在需要时加载（`push --dry-run` 或 Gate 结果同步触发）。

## §1 dry-run 预览模式

`--dry-run` 预览将要执行的操作但不实际执行。

**预览输出格式**：
```
[预览] CR-{id} (#{编号}): {当前外部状态} → {目标外部状态}
  操作：{操作描述}
```

**增强特性**：
- **Before/After 视觉化**：展示外部状态变更前后对比（如 `labels: [backlog] → [in-progress]`）
- **影响预估**：输出预计 API 调用次数和耗时（基于适配器限流规则，如"预计 3 次 API 调用，约 5 秒"）
- **Selective push**：dry-run 完成后询问"是否执行全部操作？可输入 CR 编号选择性执行"，用户可指定部分 CR（如"只推送 CR-003 和 CR-005"）

**dry-run 汇总**：
```
预览完成：{N} 个 CR 需更新 / {M} 个已一致（跳过）/ {K} 个不可更新（跳过）
预计 API 调用：{X} 次，耗时约 {Y} 秒
执行？[全部 / 选择 / 取消]
```

## §2 Gate 结果同步

Gate 检查完成时，如果 CR 有外部关联，自动推送结果到外部。

**触发时机**：Gate 1 完成后 | Gate 2 完成后 | Gate 3 待处理时

**同步动作**：按 `knowledge/_schema/integration/sync-mapping-format.md` "Gate 结果同步" section 定义的 Gate→外部动作映射执行。Claude 根据 Gate 编号和结果查找对应动作，通过适配器操作表执行。

**Comment 格式**（遵循 `sync-procedures-push.md` §1 语义 Comment 规则）：
```
✅ Gate {N} 通过：{1 句摘要}
```
或
```
❌ Gate {N} 未通过：{失败项数}/{总数}，主要问题：{问题摘要}
```

**约束**：
- sync-mapping.md 不存在 → 静默跳过
- CR 无外部关联 → 静默跳过
- 平台工具不可用 → 在 Gate 结果输出中附加提醒"外部同步失败"

## §3 与现有规则的协调

> 从 `rules/devpace-rules.md` 迁入。

- 推进模式状态转换后 → sync-push Hook 缓存比对检测实际转换，输出建议性提醒（advisory，不阻断）
- merged 后连锁更新第 7 步 → post-cr-update Hook 输出指令性管道（含第 7 步外部同步），sync-push Hook 作为安全网双层保障
- 发布管理 → Release 同步（Phase 19）
- Gate 1/2/3 结果同步：Gate 完成后若 CR 有外部关联，自动推送结果（详见本文件 §2）
