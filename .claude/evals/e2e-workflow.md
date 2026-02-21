## EVAL: e2e-workflow
Created: 2026-02-18

> 评估 devpace 端到端 BizDevOps 工作流——需要在目标项目中实际运行，覆盖 Phase 2 验证计划 V2.1-V2.16。

### Capability Evals — 核心工作流（V2.1-V2.2, V2.14-V2.15）
- [ ] **E-WF-01** /pace-init 已有项目：diagnostic-agent-framework 中执行，.devpace/ 结构完整（state.md + project.md + crs/）
- [ ] **E-WF-02** /pace-init 新项目：空目录执行，对话引导正常，BR→PF→CR 价值链建立
- [ ] **E-WF-03** CR 全生命周期（已有项目）：created→developing→verifying→in_review→merged 全流程走通
- [ ] **E-WF-04** CR 全生命周期（新项目）：同上，在新初始化项目中验证
- [ ] **E-WF-05** /pace-dev 状态推进：每次推进触发正确的质量门禁检查

### Capability Evals — 会话连续性（V2.3, V2.11, V2.16）
- [ ] **E-WF-06** 跨会话恢复（已有项目）：中断 3 次，每次新会话自动恢复上下文，零手动解释
- [ ] **E-WF-07** 跨会话恢复（新项目）：中断后新会话自动读取 .devpace/ 状态
- [ ] **E-WF-08** 会话结束保存：说"结束"后 state.md 更新、CR 文件最新、输出 3-5 行总结

### Capability Evals — 质量检查（V2.4）
- [ ] **E-WF-09** 质量门禁拦截：故意引入不合格代码，质量检查拦截不跳过
- [ ] **E-WF-10** /pace-review 审批流程：CR 进入 in_review 后审批→merged 自动更新
- [ ] **E-WF-11** /pace-review 打回流程：打回→developing 并记录原因

### Capability Evals — 变更管理（V2.5-V2.8）
- [ ] **E-WF-12** 需求插入：中途加入新 PF，影响分析准确，功能树更新
- [ ] **E-WF-13** 需求暂停：暂停进行中 CR，工作保留，依赖调整
- [ ] **E-WF-14** 优先级调整：重排迭代优先级，state.md 和迭代计划更新
- [ ] **E-WF-15** /pace-change 变更报告：输出格式符合 change-procedure.md 定义

### Capability Evals — 辅助功能（V2.12-V2.13）
- [ ] **E-WF-16** /pace-theory 理论参考：返回与当前阶段相关的理论指导，不修改状态文件
- [ ] **E-WF-17** /pace-status 默认输出：≤3 行，核心状态一目了然
- [ ] **E-WF-18** /pace-status detail/tree：分级输出粒度正确

### Capability Evals — 高阶验证（V2.9-V2.10）
- [ ] **E-WF-19** 优于手动方案（OBJ-5）：3 次会话中断恢复，devpace 所需用户纠正次数 < 手动 CLAUDE.md
- [ ] **E-WF-20** 渐进丰富自然（OBJ-6）：从 1 个 CR 增长到 3+ CR，用户未主动修改 devpace 生成的结构

### Regression Evals
- [ ] **R-WF-01** /pace-init 幂等安全：已初始化项目重复执行不覆盖已有数据
- [ ] **R-WF-02** 状态一致性：任何操作后 state.md 与 CR 文件状态一致
- [ ] **R-WF-03** 静态检查不退化：端到端验证过程中 pytest tests/static/ 持续通过

### Success Criteria
- pass@3 > 90% for capability evals（Claude 行为有非确定性，允许重试）
- pass^3 = 100% for regression evals
- E-WF-19 需要定量数据支撑（纠正次数对比）

### Verification Method
```bash
# 已有项目验证（T8-T10）
cd /Users/jinhuasu/Project_Workspace/Anker-Projects/diagnostic-agent-framework
claude --plugin-dir ../ml-platform-research/llm-platform-solution/claude-code-forge/devpace

# 新项目验证（T11-T12 已完成，可参考 devpace-verify-newproject 结果）
```

### Eval-Task 映射
| Eval 项 | 对应 Progress 任务 | 对应验证计划 |
|---------|-------------------|-------------|
| E-WF-01, E-WF-03, E-WF-05 | T8 | V2.1, V2.2 |
| E-WF-02, E-WF-04 | T11 ✅ | V2.14, V2.15 |
| E-WF-06, E-WF-08, E-WF-09, E-WF-10, E-WF-11 | T9 | V2.3, V2.4, V2.11 |
| E-WF-07 | T12 ✅ | V2.16 |
| E-WF-12 ~ E-WF-18 | T10 | V2.5-V2.8, V2.12-V2.13 |
| E-WF-19, E-WF-20 | Phase 2 综合 | V2.9, V2.10 |

### Current Status
- T11 ✅ T12 ✅ 已完成：E-WF-02, E-WF-04, E-WF-07 可标记 PASS
- T8, T9, T10 待执行：其余 eval 项待验证
