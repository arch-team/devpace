# 测试执行规程——模拟门禁执行（dryrun）

> **职责**：/pace-test dryrun Gate 模拟预检——dry-run 执行，不转换状态。自包含。

## §0 速查卡片

- **模拟门禁**：在非 Gate 阶段预执行 Gate 1/2/4 检查，输出模拟报告（不变更状态）
- **与 /pace-dev Gate 的区别**：不转换状态、不自动修复、不写入 CR 事件记录
- **用途**：预检/调试/确认 Gate 通过性

## 流程

当用户执行 `/pace-test dryrun [1|2|4]` 时，以 dry-run 模式执行指定 Gate 的完整检查流程，不触发状态转换。

1. **确定目标 Gate**：
   - 有参数 → 执行指定 Gate（1 / 2 / 4）
   - 无参数 → 根据当前 CR 状态推断下一个 Gate：
     - developing → Gate 1
     - verifying → Gate 2
     - approved/merged → Gate 4（如有 Release）
   - 无活跃 CR → 提示用户指定 Gate 编号
2. **加载检查项**：
   - 读取 `.devpace/rules/checks.md` → 提取目标 Gate 的所有检查项
   - Gate 4：从 `skills/pace-release/release-procedures-create-enhanced.md` Gate 4 段落提取发布检查项
3. **执行检查（dry-run 模式）**：
   - 命令检查：实际执行 bash 命令，记录结果
   - 意图检查：Claude 按规则判定，输出结论
   - 对抗审查（Gate 2）：执行对抗审查，输出发现
   - 浏览器验收（Gate 2，前端项目 + Playwright MCP 可用时）：按 `test-procedures-verify.md` L1+ 流程执行，标注"🖥️ 浏览器验收"
   - **不触发 CR 状态转换**——仅输出结果
4. **生成模拟报告**

### 与 /pace-dev Gate 的区别

| 维度 | /pace-test dryrun | /pace-dev Gate |
|------|----------------|----------------|
| 状态转换 | 不转换（dry-run） | 转换 CR 状态 |
| 自动修复 | 不修复（仅报告） | 失败时自动修复+重试 |
| 用途 | 预检/调试/确认 | 正式门禁流程 |
| CR 事件记录 | 不写入 | 写入事件表 |

## 输出格式

```markdown
## Gate [N] 模拟执行报告（Dry-Run）

**CR**：[CR 标题]（如有）
**模式**：🔍 仅检查，不转换状态

### 检查结果

| # | 检查项 | 类型 | 状态 | 备注 |
|---|--------|------|------|------|
| 1 | [名称] | 命令 | ✅ PASS | — |
| 2 | [名称] | 意图 | ❌ FAIL | [判定理由] |
| 3 | [名称] | 命令 | ⏭️ SKIP | 依赖"[前置名称]"未通过 |

### 汇总

- 通过：N/M
- **预判**：[Gate 将通过 ✅ / Gate 将失败 ❌]
- 需修复项：[列表]

*提示：修复后可再次执行 `/pace-test dryrun [N]` 确认，或执行 `/pace-dev` 进入正式 Gate 流程。*
```

### --brief 输出格式

`预检 Gate N：X/Y passed · 预判 [通过/失败]`

## 降级场景

| 条件 | 行为 |
|------|------|
| 无 checks.md | 使用 `test-procedures-core.md` §1.2 自动检测逻辑获取测试命令，仅执行命令检查 |
| Gate 编号无效 | 输出"支持的 Gate：1（developing→verifying）、2（verifying→in_review）、4（Release 发布）"|
| 无活跃 CR 且无参数 | 提示"请指定 Gate 编号：/pace-test dryrun 1" |
