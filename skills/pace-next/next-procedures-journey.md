# 旅程编排输出规程

> **职责**：journey 子命令的路径生成和输出格式。建议性编排——展示路径、标识当前位置、引导下一步，但不自动执行。

## 旅程模板定义

| 模板 | 编排路径 | 适用场景 |
|------|---------|---------|
| `new-feature` | biz discover → decompose → plan next → dev → review → merged | 从零开始交付一个功能 |
| `iteration` | plan next → [dev → review → merged]* → plan close → retro | 完整迭代循环 |
| `hotfix` | feedback report → dev → review → release deploy | 紧急修复 |
| `release` | release create → deploy → verify → close | 标准发布 |
| `onboarding` | init → dev(第一个功能) → review → merged | 新用户首次体验 |

## 自动模板选择（无模板名时）

根据项目状态匹配：

| 条件 | 选择模板 | 理由 |
|------|---------|------|
| backlog/ 无 CR 且无 merged 记录 | `onboarding` | 新项目首次体验 |
| 有 deployed 未 verified Release | `release` | 发布流程待完成 |
| 有 defect/hotfix 类型 developing CR | `hotfix` | 紧急修复进行中 |
| 有活跃迭代（current.md 存在） | `iteration` | 迭代内持续推进 |
| 其他 | `new-feature` | 默认起点 |

## 路径生成逻辑

### Step J1：确定当前位置

扫描 `.devpace/` 状态，定位用户在旅程中的当前步骤：

- 读取 state.md 当前工作
- 读取 backlog/ CR 状态分布
- 读取 iterations/current.md（如有）
- 读取 releases/（如有）

### Step J2：生成路径视图

按模板的步骤顺序，标记每步的状态：

| 标记 | 含义 |
|------|------|
| ✅ | 已完成 |
| 👉 | 当前位置（下一步要做的） |
| ⏳ | 待做 |
| ⏭️ | 可选/按需 |

### Step J3：输出

```
旅程：[模板名] — [1 句话目标]

✅ 初始化 — 项目已就绪
✅ 规划迭代 — 纳入 3 个功能点
👉 开发 PF-002 — 说"帮我实现 [PF 名]"或 /pace-dev
⏳ 审批 — /pace-review
⏳ 迭代回顾 — /pace-retro

进度：2/5 步完成
```

## 规则

- **只展示不执行**：journey 是建议性的路径展示，不触发任何 Skill 执行
- **动态更新**：每次调用 journey 都重新扫描状态，路径视图反映最新进度
- **与默认模式互补**：journey 展示全局路径，默认模式推荐单步行动。用户可交替使用
- **轻量输出**：路径视图 ≤ 10 行，不展示已完成步骤的详情
- **无旅程状态文件**：不在 .devpace/ 中持久化旅程状态，完全从项目状态动态推断
