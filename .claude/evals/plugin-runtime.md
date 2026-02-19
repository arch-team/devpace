## EVAL: plugin-runtime
Created: 2026-02-18

> 评估 devpace Plugin 加载和 Skill 运行时行为——需要 Claude CLI，但不需要目标项目。

### Capability Evals
- [ ] **E-PR-01** Plugin 加载：`claude --plugin-dir ./` 无报错，7 个 Skill 出现在 `/` 菜单
- [ ] **E-PR-02** Skill 命名空间：所有 Skill 以 `devpace:` 前缀出现（pace-init → devpace:pace-init）
- [ ] **E-PR-03** Rules 自动加载：`rules/devpace-rules.md` 在 Plugin 加载后生效（Claude 行为符合规则）
- [ ] **E-PR-04** Knowledge 可访问：Skill 内可读取 `knowledge/theory.md` 和 `knowledge/_schema/*.md`
- [ ] **E-PR-05** allowed-tools 生效：含 Read/Glob 的 Skill 执行时不弹工具确认
- [ ] **E-PR-06** argument-hint 显示：`/devpace:pace-advance` 等命令在补全时显示参数提示

### Regression Evals
- [ ] **R-PR-01** 无 Skill 名称冲突：与常见 Plugin（superpowers、everything-claude-code）并存无冲突
- [ ] **R-PR-02** Plugin 目录外不受影响：非 Plugin 项目中 Claude 行为正常

### Success Criteria
- pass@3 > 90% for capability evals（运行时行为有 Claude 非确定性因素）
- pass^3 = 100% for regression evals

### Verification Method
```bash
# 加载 Plugin 验证
claude --plugin-dir ./

# 在 CLI 中手动测试
# 1. 输入 / 查看 Skill 列表
# 2. 执行 /devpace:pace-status 验证基本功能
```

### Notes
- E-PR-03 到 E-PR-06 需要交互式验证，无法完全自动化
- 建议结合 T8（已有项目验证）一起执行，避免重复加载
