---
description: Use when user wants to switch output perspective (视角切换), says "切换角色/视角", "以XX视角", "pace-role", "作为产品经理", "作为运维", "换个角度看", or wants to view project from a different role perspective. NOT for project status overview (use /pace-status). NOT for understanding devpace concepts (use /pace-theory).
allowed-tools: Read, Write, Glob
argument-hint: "[biz 业务视角|pm 产品视角|dev 开发视角|tester 测试视角|ops 运维视角|auto 自动推断|compare 多视角快照]"
model: haiku
---

# /pace-role — 角色视角切换

显式切换角色视角，调整 Claude 的输出关注点和术语。

## 输入

$ARGUMENTS：
- `biz` → Biz Owner（业务视角）
- `pm` → PM（产品视角）
- `dev` → Dev（开发视角，默认）
- `tester` → Tester（测试视角）
- `ops` → Ops（运维视角）
- `auto` → 回到自动推断模式（清除显式角色设置）
- `compare` → 输出多视角快照
- `set-default <角色>` → 设置跨会话默认角色（写入 project.md）
- （空）→ 显示当前角色（含来源："自动推断" / "你设置的" / "项目默认"）+ 可选角色列表

## 执行路由表

**重要**：根据 $ARGUMENTS 值，仅读取对应的 procedures 文件，不加载其他 procedures。

| 参数 | 加载文件 |
|------|---------|
| biz/pm/dev/tester/ops | `role-procedures-switch.md` |
| auto | `role-procedures-switch.md`（auto 章节） |
| set-default | `role-procedures-switch.md`（set-default 章节） |
| compare | `role-procedures-compare.md`（自包含） |
| （空） | **无外部文件**——直接输出当前角色 + 可选列表 |

角色关注维度权威定义及跨 Skill 适配原则见 `knowledge/role-adaptations.md`。

> **隐式依赖**：`role-procedures-inference.md` 不在路由表中直接路由，但由 `rules/devpace-rules.md` §10 在运行时加载（自动推断模式的关键词映射权威源）。

## 输出

- 角色切换：确认信息（1-3 行，含相关性评估摘要）
- 无参调用：当前角色（含来源）+ 可选角色列表
- `compare`：多视角快照（5 行紧凑输出）
- `auto`：回到自动推断确认（1 行）
- `set-default`：持久化确认（1 行）
