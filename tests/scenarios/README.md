# 场景测试方法论

> 本目录包含 Claude-in-the-loop 行为测试场景。每个场景需要人类测试者在目标项目中执行。

## 测试方法

1. **准备环境**：在目标项目中加载 devpace 插件（`claude --plugin-dir <path-to-devpace>`）
2. **按步骤执行**：依照场景文档的"执行步骤"进行操作
3. **观察与记录**：对比 Claude 的行为与"期望行为"
4. **评分**：按评分维度判定 Pass / Partial / Fail

## 评分标准

| 等级 | 定义 |
|------|------|
| **Pass** | 完全满足验收标准，行为符合预期 |
| **Partial** | 部分满足，核心功能正确但有瑕疵 |
| **Fail** | 未满足验收标准，核心功能缺失或行为错误 |

## 场景清单

| 场景 | 对应需求 | 文件 |
|------|---------|------|
| S01 首次初始化 | S1, F1.1 | S01-init.md |
| S02 日常推进 | S2, F1.2, F1.3, F1.6 | S02-daily-advance.md |
| S03 查看进度 | S3, F1.5, NF6, NF9 | S03-status-levels.md |
| S04 需求插入 | S4, F2.1-F2.3 | S04-change-insert.md |
| S05 需求暂停 | S5, F2.4 | S05-change-pause.md |
| S06 优先级重排 | S6, F2.5 | S06-change-reprioritize.md |
| S07 需求修改 | S7, F2.6 | S07-change-modify.md |
| S08 Code Review | S8, F1.7 | S08-review-flow.md |
| S09 迭代回顾 | S9, F3.1-F3.3 | S09-retro.md |
| S10 会话结束 | S10, F1.2, NF3 | S10-session-end.md |
| S11 自由探索 | S11, NF8 | S11-explore-mode.md |
| S12 理论参考 | S12 | S12-guide.md |
| V 新项目验证 | V2.14-V2.16 | V-new-project.md |

## 测试记录模板

每次执行后在场景文件底部追加：

```
## 测试记录

| 日期 | 目标项目 | 结果 | 备注 |
|------|---------|------|------|
| YYYY-MM-DD | [项目名] | Pass/Partial/Fail | [简述] |
```
