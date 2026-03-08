# epic 子命令 procedures

> **职责**：从 Opportunity 转化或直接创建 Epic，定义 MoS，更新价值功能树。

## 触发

`/pace-biz epic [OPP-xxx] <描述>` 或用户要创建一个专题/Epic。

## 步骤

### Step 0：模式检查

读取 project.md 的 `mode` 字段。若为 `lite`：

> **当前为轻量模式（OBJ→PF→CR），Epic 功能需要完整模式。**
> - 升级到完整模式：`/pace-init --upgrade-mode`
> - 或直接添加功能：`/pace-change add <描述>`

终止后续步骤。

### Step 1：确定来源

- 有 `OPP-xxx` 参数 → 读取 opportunities.md 确认 OPP 存在且状态为 `评估中`
- 无 OPP 参数 → 直接创建模式（来源字段留空或标注"直接创建"）

### Step 2：确定 OBJ 关联

1. 读取 project.md 业务目标 section，列出可用 OBJ
2. 如果只有 1 个 OBJ → 自动关联
3. 如果多个 OBJ → 询问用户选择
4. 如果无 OBJ → 引导先定义业务目标（建议 /pace-init full）

### Step 3：引导定义 Epic 内容

向用户询问（如未在参数中提供）：

1. **专题名称**：一句话描述这个专题
2. **背景**：2-3 句话，为什么做这个专题
3. **成效指标（MoS）**：如何衡量这个专题的成功？（可选——渐进填充）

### Step 4：生成 EPIC 编号

1. 扫描 `.devpace/epics/` 目录（不存在则创建）
2. 取最大 EPIC 编号 +1
3. 三位补零：`EPIC-001`、`EPIC-002`...

### Step 5：创建 Epic 文件

创建 `.devpace/epics/EPIC-xxx.md`，格式遵循 `knowledge/_schema/epic-format.md`：

```markdown
# EPIC-xxx：[专题名称]

- **OBJ**：OBJ-x（[目标描述]）
- **状态**：规划中
- **来源**：OPP-xxx（[描述]）
- **时间框架**：（首次 /pace-plan 时填充）

## 背景

[用户提供的背景]

## 成效指标（MoS）

- [ ] [指标 1]
- [ ] [指标 2]

## 业务需求

| BR | 标题 | 优先级 | 状态 | PF 数 | 完成度 |
|----|------|:------:|------|:-----:|:------:|
```

MoS 为空时写：
```markdown
## 成效指标（MoS）

（待定义 — /pace-biz decompose 或讨论时填充）
```

### Step 6：更新 project.md 价值功能树

在对应 OBJ 下追加 Epic 链接行：

```markdown
OBJ-x（[目标名]）
├── ... (existing)
└── [EPIC-xxx：专题名](epics/EPIC-xxx.md)
```

### Step 7：更新 opportunities.md（如从 OPP 转化）

将对应 OPP 状态改为：`已采纳 → EPIC-xxx`

### Step 8：输出确认

```
已创建专题：EPIC-xxx — [名称]
关联：OBJ-x（[目标]）← OPP-xxx（如有）
MoS：[指标列表] 或 （待定义）
→ 下一步：/pace-biz decompose EPIC-xxx 分解为业务需求
```

## 容错

| 异常 | 处理 |
|------|------|
| OPP-xxx 不存在 | 提示 OPP 编号无效，列出可用 OPP |
| OPP 状态非"评估中" | 提示已处理，询问是否仍要创建 Epic |
| epics/ 目录不存在 | 自动创建 |
| project.md 无价值功能树 | 创建空树结构后追加 |
| 无 OBJ | 引导 /pace-init full 或先定义 OBJ |
