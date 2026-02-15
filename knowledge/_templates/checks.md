# 项目质量检查

> **职责**：定义本项目特有的质量质量检查。请根据项目实际情况填写检查项和检查方式。

## developing → verifying

<!-- 项目自定义检查（根据项目实际情况填写） -->
- [ ] **{{GATE_NAME_1}}**：{{DESCRIPTION}}
      检查方式：{{CHECK_COMMAND}}

<!-- devpace 内置检查（不可删除） -->
- [ ] **需求完整性**：CR 意图 section 与变更复杂度匹配
      检查方式：Claude 检查意图字段填充度（简单=用户原话；标准=+范围+验收条件；复杂=全部字段）

## verifying → in_review

<!-- 项目自定义检查（根据项目实际情况填写） -->
- [ ] **{{GATE_NAME_2}}**：{{DESCRIPTION}}
      检查方式：{{CHECK_COMMAND}}

<!-- devpace 内置检查（不可删除） -->
- [ ] **意图一致性**：实际变更与 CR 意图 section 的范围和验收条件一致
      检查方式：Claude 对比 git diff 与意图 section，标注偏差
