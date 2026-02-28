# detail：功能树缩进可视化

> 由 SKILL.md 路由表加载。仅在 `detail` 子命令时读取。

## 输出格式

```
📦 用户系统
  ├── ✅ 登录模块 (3/3 CR) → [详情](features/PF-001.md)
  ├── 🔄 权限控制 (1/2 CR) ← 进行中
  └── ⏳ 用户管理 (0/2 CR)
📦 数据管理
  ├── ✅ 数据导入 (2/2 CR)
  └── 🔄 数据导出 (1/3 CR)
```

## 数据源

读取 `.devpace/iterations/current.md` 和 `.devpace/project.md`。

## 规则

- 每个功能组附带进度条
- 标记阻塞项和依赖关系
- 状态 emoji：✅ 完成、🔄 进行中、⏳ 待开始、⏸️ 暂停
- **PF 文件读取**：已溢出的 PF（`features/PF-xxx.md` 存在）显示 `[详情]` 链接，从 PF 文件读取精确的 CR 统计和验收标准通过率
- **同步标记**（sync-mapping.md 存在时）：已同步 CR 追加 `🔗`，待推送 CR 追加 `[↑待推送]`
- **角色适配**：pace-role 已设角色时调整侧重（Dev 突出质量门，PM 突出完成率和依赖）

## 导航

输出末尾追加 1 行：`→ 深入某功能：/pace-status trace [功能名]`
