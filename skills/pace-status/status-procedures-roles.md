# 角色视角输出

> 由 SKILL.md 路由表加载。仅在 `biz/pm/dev/tester/ops` 子命令时读取。

## 角色联动规则（从 devpace-rules.md §13 归位）

- **自动适配**：pace-role 已设角色后，/pace-status 概览和 detail/trace/tree 自动调整关注点（Dev 突出质量门，PM 突出完成率，Biz 突出 MoS）
- **优先级规则**：显式角色子命令（`/pace-status dev`）> pace-role 自动适配——用户先 `/pace-role pm` 再 `/pace-status dev`，输出按 Dev 视角
- **首次教学**（§15 `role_adapt` 标记去重）：首次因 pace-role 自动适配时，末尾附 1 行提示切换方法
- **角色指示器**：pace-status 概览输出首行添加轻量角色指示器 `[PM 视角]`（仅非 Dev 角色时显示）

## biz（Biz Owner 视角）

```
## 业务目标进展

OBJ-1：[目标名]
- MoS 达成：M/N 指标已满足
- 价值交付：N 个功能已上线，M 个进行中
- 风险：[未达成指标和原因]
```

数据来源：project.md MoS checkbox + 功能树完成度

## pm（PM 视角）

```
## 迭代交付看板

迭代：[名称] | 进度 ████████░░ 80%
- 完成：N 功能 | 进行中：M 功能 | 阻塞：K 个
- 变更：本迭代 X 次范围变更
- 节奏：平均 CR 周期 Y 天
```

数据来源：iterations/current.md + backlog/ CR 状态分布

## dev（Dev 视角）

```
## 开发状态

进行中 CR：[标题] → [当前阶段]
质量门：M/N 项通过
待处理：K 个 CR 待开始
```

数据来源：backlog/ CR 文件 + checks.md

## tester（Tester 视角）

```
## 质量状态

缺陷概况：开放 N / 已修复 M / 逃逸 K
质量检查通过率：X%
人类打回率：Y%
高优缺陷：[critical/major 列表]
```

数据来源：backlog/ CR 文件（type:defect）+ dashboard.md

## ops（Ops 视角）

```
## 运维状态

最近 Release：[REL-xxx] [状态]（[日期]）
部署后缺陷：N 个（M 已修复）
MTTR：平均 X 天
待发布 CR：K 个 merged 未 released
```

数据来源：releases/ + backlog/ CR 文件 + dashboard.md

## 导航

输出末尾追加 1 行：`→ 切换视角：/pace-role [biz|pm|dev|tester|ops]`
