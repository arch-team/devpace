# 发布管理执行规程——Create 增强功能

> **职责**：Create 的可选增强——CR 依赖检测、Readiness Check、影响预览、Gate 4。
>
> **条件加载**：CR > 3 或有 integrations/config.md 时追加加载。简单 Release（1-2 CR）不加载。

## §0 速查卡片

- **CR 依赖检测**：功能级（PF 关联）+ 代码级（文件交叉）→ 纳入建议
- **Readiness Check**：代码卫生扫描 + 测试覆盖联动 → 就绪评分 A/B/C
- **影响预览**：代码变更统计 + 模块热图 + 风险标记 + 业务推进度
- **Gate 4**：构建验证 + CI 状态 + 候选完整性 + 测试报告 → 结果持久化

## CR 依赖检测（候选分析）

在候选 CR 展示时，自动检测候选 CR 之间的依赖关系：

1. **功能级依赖**：检查候选 CR 的 PF 关联
   - 同一 PF 下的多个 CR → 标记为"功能关联"（建议同时纳入或排除）
   - 一个 PF 的 defect CR 和另一个 PF 的 feature CR 无直接关联 → 不标记

2. **代码级依赖**（如可获取变更文件列表）：
   - 多个 CR 修改同一文件 → 标记为"代码交叉"（需审查交互风险）
   - CR-A 修改了被 CR-B 引用的文件 → 标记为"潜在依赖"

3. **依赖图展示**（仅在检测到依赖时展示）：
   ```
   CR 依赖分析：
   🔗 功能关联：CR-001 ↔ CR-004（同属 PF-001 用户认证）— 建议同时纳入
   ⚠️ 代码交叉：CR-001 和 CR-003 均修改 src/auth/login.ts — 请审查交互
   ✅ CR-005 无依赖关系（可独立纳入/排除）
   ```

4. **纳入建议**：
   - 有功能关联的 CR 组 → "建议整组纳入（拆分可能导致功能不完整）"
   - 有代码交叉的 CR 组 → "建议同时纳入并关注集成测试"
   - 无依赖的 CR → 可自由选择纳入/排除

**规则**：
- 依赖检测是信息性的，不阻断用户选择
- 无法获取 git 数据时仅做功能级（PF）检测
- 候选 CR ≤ 2 个时跳过依赖检测（无分析价值）

## Release Readiness Check（候选预验证）

在候选 CR 确认后、Release 文件创建前，可选执行"发布就绪性"预检：

1. **代码卫生扫描**：检测各 CR 变更文件中的临时代码标记
   - `TODO`、`FIXME`、`HACK`、`XXX` 注释
   - `console.log`、`console.debug`、`debugger`、`print()` 调试语句
   - 临时禁用标记：`@ts-ignore`、`# noqa`、`// eslint-disable`
   - 检测方式：对每个 CR 的变更文件执行 Grep 搜索（仅搜索变更行，通过 `git diff` 获取）
   - 无 git 数据时跳过此项

2. **测试覆盖联动**（如 pace-test 可用）：
   - 读取各 CR 的 accept 记录，检查是否有测试覆盖
   - 无 accept 记录的 CR 标记为"缺少测试验证"
   - pace-test 不可用时跳过此项

3. **Readiness 评分与输出**：
   ```
   Release Readiness Check：
   ✅ 代码卫生：通过（无临时代码标记）
   ⚠️ 测试覆盖：CR-003 缺少 accept 记录
   ⚠️ 发现 2 处 TODO（CR-001: src/auth.ts:45, CR-004: src/api.ts:12）

   就绪评分：B（建议处理 ⚠️ 项后再发布，或确认这些是已知的可接受项）
   继续创建 Release？[Y/n]
   ```

**规则**：
- 预检是增强不是阻断——用户确认后可带着 ⚠️ 继续创建 Release
- 预检结果写入 Release 文件的 `## Readiness Check` section
- 评分规则：全部 ✅ = A，有 ⚠️ 无 ❌ = B，有 ❌ = C

## Release 影响预览

Create 完成后、Gate 4 之前，自动生成 Release 级别的影响预览：

1. **代码变更统计**：汇总各 CR 的代码变更（如果可获取 `git diff --stat`）
   - 总变更行数（增/删）、涉及文件数
   - 无 git 数据时跳过此项

2. **模块变更热图**：按目录聚合变更文件数
   ```
   变更热图：
   - src/auth/     ███░░ 3 个文件（CR-001, CR-003）
   - src/payment/  █░░░░ 1 个文件（CR-005）
   - tests/        ██░░░ 2 个文件
   ```

3. **风险区域标记**：
   - 🔴 高风险：多个 CR 修改同一文件（合并冲突/交互风险）
   - 🟡 中风险：修改了关键路径（检测 config/、auth/、payment/ 等目录）
   - 🟢 低风险：变更分散在独立模块

4. **业务推进度**：向上追溯展示 Release 对 OBJ/BR 的贡献
   ```
   业务推进：
   - OBJ-1 "用户体验"：+2 PF（PF-001 ✅ 完成, PF-002 部分推进）
   - OBJ-2 "系统稳定性"：+1 hotfix
   ```

**规则**：
- 影响预览自动生成，但标记为信息性（不阻断流程）
- 无 git 数据或 CR 关联不完整时优雅降级（只展示可获取的维度）
- 写入 Release 文件的 `## 影响预览` section，供后续决策参考

## Gate 4 系统级发布门禁

Release create 完成后、deploy 之前执行（可选，格式见 `knowledge/_schema/integration/integrations-format.md`）：

**CI 自动感知**：如果 `integrations/config.md` 不存在或无 CI/CD section，Gate 4 先按"CI 自动检测映射表"（integrations-format.md）扫描项目根目录。检测到 CI 配置时，使用默认检查命令执行状态检查（不持久化到 config.md，仅本次使用）。建议用户运行 `/pace-init` 持久化检测结果。

1. **构建验证**：读取 `integrations/config.md` 的 CI/CD 构建命令 → 执行（如 `npm run build`）
   - 命令成功 → ✅ 构建通过
   - 命令失败 → ❌ 展示最后 10 行错误输出 + 建议修复步骤
   - 未配置构建命令 → 跳过
2. **CI 状态检查**：读取检查命令 → 执行。命令来源优先级：① integrations/config.md 配置 → ② CI 自动检测默认命令 → ③ 均无则跳过
   - 最近一次运行成功 → ✅ CI 绿色
   - 运行失败或进行中 → ⚠️ 展示失败概要 + 提供 CI 运行链接
   - 检查命令对应 CLI 不可用 → 跳过并提示安装
3. **候选完整性检查**：遍历 Release 包含的 CR，确认全部 Gate 1/2/3 已通过
   - 检查 CR 状态为 merged（已经过全部 Gate）
   - 任何 CR 状态异常 → ❌ 列出具体哪些 CR 未通过哪个 Gate

Gate 4 不通过时不阻断 Release 创建（Release 已经创建为 staging），但提示用户在 deploy 前修复问题。

### Gate 4 结果持久化

Gate 4 检查完成后（不论通过与否），将检查结果写入 Release 文件的 `## Gate 4 检查结果` section：

```markdown
## Gate 4 检查结果

| 检查项 | 结果 | 详情 |
|--------|------|------|
| 构建验证 | ✅ 通过 | `npm run build` 成功 |
| CI 状态 | ⚠️ 进行中 | [查看 CI 运行](URL) |
| 候选完整性 | ❌ 失败 | CR-003 状态为 verifying（未通过 Gate 3） |
| 测试报告 | ✅ 已生成 | 整体评分 B |

检查时间：YYYY-MM-DD HH:MM
```

4. **自动生成 Release 测试报告**：Gate 4 检查完成后，自动执行 `/pace-test report REL-xxx`
   - 报告内容：CR 质量汇总 + 功能覆盖 + 风险评估 + 发布建议
   - 如报告返回"数据不足"信息，在 Release 文件备注"部分 CR 缺少测试数据，建议补全"
   - 无 `/pace-test` Skill 可用时静默跳过
