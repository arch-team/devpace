# decompose 子命令 procedures

> **职责**：分解 Epic→BR 或 BR→PF，填充价值链中间层。

## 触发

`/pace-biz decompose <EPIC-xxx|BR-xxx>` 或用户要分解专题/需求。

## 步骤

### Step 1：确定分解目标

根据参数判断分解方向：
- `EPIC-xxx` → Epic→BR 分解
- `BR-xxx` → BR→PF 分解
- 无参数 → 列出可分解的 Epic/BR，引导选择

### Epic→BR 分解路径

#### Step 2E：读取 Epic 信息

1. 读取 `epics/EPIC-xxx.md`
2. 确认状态为 `规划中` 或 `进行中`（`已搁置` 需先 resume）
3. 读取 Epic 背景和 MoS

#### Step 3E：引导需求分解

向用户展示 Epic 背景和 MoS，然后引导分解：

1. 基于 Epic 背景，Claude 建议 BR 分解方案（2-5 个 BR）
2. 每个 BR 包含：名称 + 优先级建议 + 一句话描述
3. 用户确认/调整分解方案

#### Step 4E：创建 BR 条目

对每个确认的 BR：

1. 在 project.md 价值功能树中，在对应 Epic 下追加 BR 行：
   ```
   BR-xxx：[名称] `Px`
   ```
2. BR 编号自增（扫描 project.md 树中最大 BR 编号 +1）
3. 更新 Epic 文件的"业务需求"表格

#### Step 5E：更新 Epic 状态

如果 Epic 当前为 `规划中` 且有了 BR → 状态改为 `进行中`

### BR→PF 分解路径

#### Step 2P：读取 BR 信息

1. 从 project.md 树视图或 `requirements/BR-xxx.md` 读取 BR 信息
2. 读取关联 Epic 和 OBJ 上下文

#### Step 3P：引导功能分解

向用户展示 BR 上下文，然后引导分解：

1. 基于 BR 描述，Claude 建议 PF 分解方案（1-3 个 PF）
2. 每个 PF 包含：名称 + 用户故事建议
3. 用户确认/调整分解方案

#### Step 4P：创建 PF 条目

对每个确认的 PF：

1. 在 project.md 价值功能树中，在对应 BR 下追加 PF 行：
   ```
   PF-xxx：[名称]（[用户故事]）→ (待创建 CR)
   ```
2. PF 编号自增（扫描 project.md 树中最大 PF 编号 +1）

#### Step 5P：更新 BR 状态

如果 BR 有溢出文件 → 更新 `requirements/BR-xxx.md` 的 PF 列表

### 公共结束步骤

#### Step 6：输出分解结果

```
已分解 [EPIC-xxx|BR-xxx]：
├── [BR|PF]-001：[名称] [优先级]
├── [BR|PF]-002：[名称] [优先级]
└── [BR|PF]-003：[名称] [优先级]

价值链：OBJ-x → EPIC-xxx → BR-xxx → PF-xxx
→ 下一步：[继续分解建议或 /pace-dev 开始开发]
```

## 容错

| 异常 | 处理 |
|------|------|
| EPIC/BR 编号不存在 | 提示无效编号，列出可用选项 |
| Epic 状态为"已搁置" | 提示需先 /pace-change resume |
| 已有 BR/PF 的重复分解 | 展示现有分解，询问是否追加 |
| project.md 无树结构 | 创建树结构后执行分解 |
