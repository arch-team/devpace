# 扩展同步清单

> **按需参考**：仅在新增角色或 pace-plan 子命令时加载本文件。

## pace-role 角色扩展清单

新增角色时须同步以下文件（按顺序）：

1. `skills/pace-role/role-procedures-dimensions.md`：角色定义表
2. `skills/pace-role/role-procedures-switch.md`：别名映射
3. `skills/pace-role/role-procedures-inference.md`：关键词映射
4. `skills/pace-role/role-procedures-compare.md`：输出格式加一行
5. `skills/pace-status/status-procedures-roles.md`：完整角色模板
6. `skills/pace-retro/retro-procedures.md`：角色适配表
7. `skills/pace-change/change-procedures-impact.md`：措辞模板表
8. `skills/pace-pulse/SKILL.md`：角色感知表
9. `skills/pace-theory/theory-procedures-default.md`：角色适配输出框架
10. `skills/pace-next/next-procedures.md`：视角调整表
11. `skills/pace-release/release-procedures-notes.md`：角色视角 Release Notes
12. `knowledge/_schema/project-format.md`：preferred-role 枚举
13. `docs/features/pace-role.md` + `pace-role_zh.md`：特性文档

## pace-plan 子命令扩展清单

添加新子命令时须同步以下文件（按顺序）：

1. 新建 `skills/pace-plan/<cmd>-procedures.md`
2. `skills/pace-plan/SKILL.md`：路由表 + 输入 + argument-hint
3. `knowledge/_schema/iteration-format.md`：写入规则（如新子命令写入迭代文件）
4. `rules/devpace-rules.md §11`：迭代节奏信号（如新子命令产生信号）
5. `docs/features/pace-plan.md` + `pace-plan_zh.md`：核心特性摘要 + 相关资源链接
6. `docs/user-guide.md` + `user-guide_zh.md`：参数表 + 功能描述
