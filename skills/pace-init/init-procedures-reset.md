# 重置规程

> **职责**：`/pace-init --reset [--keep-insights]` 的详细执行规则。

## 触发

`/pace-init --reset [--keep-insights]`

## 流程

1. **前置检查**：确认 `.devpace/` 存在
2. **外部关联检测**：
   - 检查 `.devpace/integrations/sync-mapping.md` 是否存在
   - 存在 → 提示："发现外部同步映射，关联的 GitHub Issues 需手动处理。"
3. **二次确认**（Hook 强制，不可跳过）：使用 AskUserQuestion 确认："即将删除 .devpace/ 及所有追踪数据（N 个 CR、M 个迭代记录），此操作不可逆。确认删除？"
   - 用户确认后，写入确认标记：`echo "confirmed" > .devpace/.reset-confirmed`
   - 用户拒绝 → 中止流程，输出"已取消重置"
4. **保留 insights**（如 `--keep-insights`）：
   - 备份 `.devpace/metrics/insights.md` 到临时位置
5. **删除 .devpace/**：删除整个目录
6. **清理 CLAUDE.md**：
   - 读取 CLAUDE.md，删除 `<!-- devpace-start -->` 到 `<!-- devpace-end -->` 之间的内容（含标记本身）
   - 清理可能遗留的多余空行
7. **恢复 insights**（如 `--keep-insights`）：
   - 创建 `.devpace/metrics/` 目录
   - 将备份的 insights.md 恢复
8. **完成提示**："已清除 .devpace/。可运行 /pace-init 重新初始化。"

## 安全规则

- 必须二次确认，不可静默删除
- 不删除 .devpace/ 以外的文件（除 CLAUDE.md devpace section 外）
- `--keep-insights` 保留经验数据（经验是跨项目资产）
