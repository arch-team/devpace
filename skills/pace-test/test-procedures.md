# 测试执行规程

> **职责**：/pace-test 的详细执行规则——基础测试执行（§1）、测试用例生成（§2）及后续 Phase 子命令规程。

## §1 基础测试执行（Layer 1）

当用户执行 `/pace-test`（无参数）时，运行已配置的测试命令并输出结构化报告。

### 前置条件

1. 读取 `.devpace/rules/checks.md`：
   - **存在** → 提取所有"检查方式"为 bash 命令的检查项（跳过意图检查和对抗审查）
   - **不存在** → 尝试项目根目录常见测试命令自动检测（见 §1.2）
2. 确定当前 CR（如在推进模式中）→ 后续报告关联到 CR

### §1.1 执行流程

1. **提取测试命令**：从 checks.md 中提取所有命令检查项，按 Gate 归属分组：
   - Gate 1（developing→verifying）：编译、测试、lint 等
   - Gate 2（verifying→in_review）：命令类检查项（如有）
2. **解析依赖顺序**：根据检查项的"依赖"字段构建执行顺序：
   - 无依赖的检查项先执行
   - 有依赖的检查项在前置通过后执行
   - 前置失败 → 被依赖项标记 ⏭️ 跳过（短路逻辑，与 Gate 执行一致）
3. **逐项执行**：
   - 执行 bash 命令，捕获 stdout/stderr 和 exit code
   - 记录每项耗时
   - exit 0 = PASS，非 0 = FAIL
4. **生成结构化报告**（见 §1.3）

### §1.2 自动检测（无 checks.md 时的降级）

当 checks.md 不存在时，按以下顺序探测项目测试命令：

| 探测文件 | 匹配条件 | 测试命令 |
|---------|---------|---------|
| `package.json` | scripts.test 存在 | `npm test` |
| `pyproject.toml` / `setup.py` / `pytest.ini` | 文件存在 | `pytest -v` |
| `Cargo.toml` | 文件存在 | `cargo test` |
| `go.mod` | 文件存在 | `go test ./...` |
| `Makefile` | test target 存在 | `make test` |

探测到多个 → 全部执行。探测到零个 → 输出"未检测到测试命令，建议在 .devpace/rules/checks.md 中配置"。

### §1.3 报告格式

```markdown
## 测试执行报告

**CR**：[CR 标题]（如有关联）
**时间**：[执行日期时间]

### 结果

| # | 检查项 | Gate | 状态 | 耗时 | 备注 |
|---|--------|------|------|------|------|
| 1 | [名称] | Gate 1 | ✅ PASS | 2.3s | — |
| 2 | [名称] | Gate 1 | ❌ FAIL | 1.1s | exit 1: [关键错误摘要] |
| 3 | [名称] | Gate 1 | ⏭️ SKIP | — | 依赖"[前置名称]"未通过 |

### 汇总

- 通过：N / 总数 M
- 失败：N（[失败项名称列表]）
- 跳过：N
- 总耗时：X.Xs

### 与 CR 意图的关联（如有）

验收条件 N 项中，有自动测试覆盖 X 项（覆盖率 Y%）。
未覆盖项：[列表]
```

### §1.4 结果写入 CR

如果当前有活跃 CR：
- 报告摘要写入 CR 事件表：`| [日期] | /pace-test 执行 | Claude | N/M passed, X failed | — |`
- 如果 CR 有"验证证据"section → 更新最新测试结果

---

## §2 测试用例生成（gen）

当用户执行 `/pace-test gen [PF标题]` 时，基于 PF 验收标准生成测试用例框架。

### 流程

1. **定位 PF 验收标准**：
   - 有 PF 参数 → 在 `project.md` 功能树中匹配
   - 无参数 → 使用当前 CR 关联的 PF
   - 未找到 → 提示用户指定
2. **提取验收条件**：从 PF 的用户故事和验收标准中提取可测试的断言
3. **检测技术栈**：
   - 读取 `.devpace/context.md`（如有，含技术栈信息）
   - 或扫描项目根目录：`package.json`（Jest/Vitest）、`pyproject.toml`（pytest）、`go.mod`（go test）、`Cargo.toml`（cargo test）
4. **生成测试框架**：
   - 按技术栈生成符合项目风格的测试文件骨架
   - 每个验收条件 → 一个测试用例（describe + it/test）
   - 包含 setup/teardown 骨架
   - 标注 `// TODO: implement` 的具体断言
5. **输出**：
   - 将生成的测试文件内容展示给用户
   - 用户确认后写入项目测试目录

### 生成规则

- 测试名称从验收标准的自然语言直接翻译（如"用户能上传 CSV" → `test_user_can_upload_csv`）
- 按验收条件编号对应测试编号，方便后续 coverage 追踪
- 包含边界条件测试建议（注释形式）
- 不生成具体实现——只生成框架和断言占位

### 输出格式

```
生成了 N 个测试用例框架，覆盖 PF "[PF标题]" 的 M 项验收条件：
1. [验收条件] → test_xxx
2. [验收条件] → test_yyy
...
文件：[测试文件路径]
```

---

## §3-§9 后续 Phase 子命令（占位）

> 以下子命令在 Phase 2/3 实现。当前调用时输出引导信息。

### §3 测试策略生成（strategy）— Phase 2

当用户执行 `/pace-test strategy` 时，输出：
"测试策略生成功能即将推出。当前可用：`/pace-test`（执行测试）和 `/pace-test verify`（AI 验收验证）。"

### §4 需求覆盖分析（coverage）— Phase 2

当用户执行 `/pace-test coverage` 时，输出：
"需求覆盖分析功能即将推出。当前可用：`/pace-test verify` 可逐条验证 PF 验收标准。"

### §5 回归风险分析（regress）— Phase 2

当用户执行 `/pace-test regress` 时，输出：
"回归风险分析功能即将推出。"

### §6 测试摘要报告（report）— Phase 2

当用户执行 `/pace-test report` 时，输出：
"测试摘要报告功能即将推出。当前 `/pace-test` 已输出结构化测试报告。"

### §7 不稳定测试分析（flaky）— Phase 3

当用户执行 `/pace-test flaky` 时，输出：
"不稳定测试分析功能即将推出。"

### §8 模拟门禁执行（gate）— Phase 3

当用户执行 `/pace-test gate [N]` 时，输出：
"模拟门禁执行功能即将推出。当前可通过 `/pace-dev` 执行完整 Gate 流程。"

### §9 测试基准线（baseline）— Phase 3

当用户执行 `/pace-test baseline` 时，输出：
"测试基准线功能即将推出。"
