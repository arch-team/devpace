# 场景 S01: 首次初始化

**对应需求**: S1, F1.1
**验证目标**: /pace-init 对话引导、.devpace/ 生成完整性、价值功能树结构

## 前置条件

- 目标项目无 `.devpace/` 目录
- 已加载 devpace 插件

## 执行步骤

| # | 人类动作 | 期望 Claude 行为 |
|---|---------|-----------------|
| 1 | 输入 `/pace-init` | 开始对话式引导，询问项目信息 |
| 2 | 回答项目名称和定位 | 继续询问业务目标和成效指标 |
| 3 | 提供业务目标和 MoS | 继续询问实施路径/产品功能 |
| 4 | 提供 2-3 个产品功能 | 生成 .devpace/ 目录结构 |
| 5 | 确认生成结果 | 展示价值功能树并确认 |

## 验收标准

- [ ] 通过对话收集项目信息（非一次性要求所有输入）
- [ ] 自动生成 `.devpace/` 目录和所有必需文件（state.md, project.md, backlog/, iterations/current.md, rules/workflow.md, rules/checks.md, metrics/dashboard.md）
- [ ] 生成的价值功能树包含 OBJ → BR → PF 层级
- [ ] state.md ≤ 15 行
- [ ] 所有 `{{PLACEHOLDER}}` 已被替换为实际值

## 评分维度

| 维度 | Pass | Partial | Fail |
|------|------|---------|------|
| 对话引导 | 分步引导，自然 | 一次性要求过多 | 不收集信息直接生成 |
| 文件完整性 | 7 个必需文件全部生成 | 缺少 1-2 个非核心文件 | 核心文件缺失 |
| 价值树结构 | 三层完整 | 缺少一层 | 无价值树 |
| 模板替换 | 无残留占位符 | 1-2 处残留 | 大量残留 |

## 检查产物

- `.devpace/state.md` — 行数 ≤ 15，含目标/迭代/进度
- `.devpace/project.md` — 含业务目标、MoS、价值功能树
- `.devpace/rules/workflow.md` — 含 7 个状态定义
- `.devpace/rules/checks.md` — 含两个门禁 section
- `.devpace/metrics/dashboard.md` — 含指标表格
- `.devpace/iterations/current.md` — 含产品功能表
