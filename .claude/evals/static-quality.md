## EVAL: static-quality
Created: 2026-02-18

> 评估 devpace Plugin 的静态质量——不需要 Claude CLI 运行，纯文件系统和 pytest 即可验证。

### Capability Evals
- [ ] **E-SQ-01** 分层隔离：产品层（rules/、skills/、knowledge/）零引用开发层（docs/、.claude/）
- [ ] **E-SQ-02** plugin.json 同步：声明的 Skills 与 skills/ 目录一一对应，无多余无缺失
- [ ] **E-SQ-03** Frontmatter 合规：7 个 Skill 的 SKILL.md frontmatter 仅含合法字段，description 必填
- [ ] **E-SQ-04** Schema 合规：所有模板文件符合 knowledge/_schema/ 定义的字段结构
- [ ] **E-SQ-05** 状态机一致性：CR 7 状态 + 转换规则在 design.md、schema、rules 间一致
- [ ] **E-SQ-06** 交叉引用完整：Skill 内引用的 schema 文件、procedure 文件、模板文件均存在
- [ ] **E-SQ-07** 命名规范：Markdown kebab-case、Skill 目录 kebab-case、模板文件 kebab-case
- [ ] **E-SQ-08** 模板占位符：使用 `{{UPPER_SNAKE}}` 格式，无未闭合花括号
- [ ] **E-SQ-09** Markdown 结构：rules/ 和 _schema/ 有 §0 速查卡片，Skill 分拆启发合规
- [ ] **E-SQ-10** argument-hint：所有 7 个 Skill 均声明 argument-hint

### Regression Evals
- [ ] **R-SQ-01** pytest tests/static/ 全部通过（87 passed, 7 skipped 为基线）
- [ ] **R-SQ-02** bash scripts/validate-all.sh 返回 exit 0
- [ ] **R-SQ-03** 集成测试 test_plugin_loading.sh 中 7/7 Skills 被发现

### Success Criteria
- pass@1 = 100% for capability evals（静态检查应完全确定性）
- pass^3 = 100% for regression evals（静态检查不应有 flaky）

### Verification Method
```bash
# 一键验证所有静态质量 eval
pytest tests/static/ -v && bash scripts/validate-all.sh
```
