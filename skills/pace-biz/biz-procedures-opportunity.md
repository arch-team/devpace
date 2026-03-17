# opportunity 子命令 procedures

> **职责**：捕获业务机会到 opportunities.md。

## 触发

`/pace-biz opportunity <描述>` 或用户描述了一个业务机会/客户反馈/竞品动态。

## 步骤

### Step 0：模式检查

lite 模式不可用（见 SKILL.md lite 模式子命令可用性表）。提示升级 `/pace-init --upgrade-mode` 或 `/pace-change add`，终止。

### Step 1：解析来源

从用户输入中推断来源类型：

| 关键词 | 推断类型 |
|--------|---------|
| 用户说/客户反馈/用户反馈/投诉 | 用户反馈 |
| 竞品/竞争对手/对手 | 竞品观察 |
| 发现/技术/性能/可以用 | 技术发现 |
| 趋势/市场/行业 | 市场趋势 |
| 想到/觉得/内部/我们应该 | 内部洞察 |

推断不确定时询问用户确认。

### Step 2：生成 OPP 编号

1. 读取 `.devpace/opportunities.md`（不存在则创建空文件）
2. 扫描所有 `## OPP-xxx` 标题，取最大编号 +1
3. 三位补零：`OPP-001`、`OPP-002`...

### Step 3：写入 opportunities.md

在文件末尾追加新条目，格式遵循 `knowledge/_schema/entity/opportunity-format.md` §文件结构。

**创建时初始值**：
- **状态**：`评估中`
- **日期**：当天日期（YYYY-MM-DD）

文件不存在时先创建，以 `# 业务机会` 为标题。

### Step 4：输出确认

```
已捕获业务机会：OPP-xxx — [描述]
来源：[类型]（[详情]）
状态：评估中
→ 下一步：/pace-biz epic OPP-xxx 评估并转化为 Epic
```

## 容错

| 异常 | 处理 |
|------|------|
| .devpace/ 不存在 | 引导 /pace-init |
| opportunities.md 格式损坏 | 在文件末尾追加，不修复已有内容 |
| 用户未提供描述 | 询问：请描述这个业务机会 |
