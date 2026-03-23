# 测试执行规程——核心

> **职责**：/pace-test 基础测试执行——Layer 1 执行、CI 消费、baseline 维护。按 SKILL.md 路由表按需加载。

## §0 速查卡片

- **基础执行**：checks.md 命令提取→依赖排序→逐项执行→结构化报告（§1.1-§1.3）
- **CI 消费**：自动检测 integrations/config.md 中 CI 状态并合并到报告（§1.5）
- **baseline 维护**：执行后静默追加基准数据（§1.7）
- **技术栈检测**：统一规则见 test-procedures-common.md「技术栈检测（SSOT）」

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
   - 注意：空参数（`/pace-test`）默认执行所有 Gate 的命令检查项。如只需执行特定 Gate 检查，使用 `dryrun [1|2|4]`
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

### 失败根因推理（仅测试失败时输出）

*基于最近 git diff 推理失败可能原因：*

| # | 失败测试 | 可能原因 | 相关变更 |
|---|---------|---------|---------|
| 1 | [测试名/检查项] | [基于变更内容的推理] | `[文件:行号]` 的变更 |

*（推理依据：对比失败测试涉及的模块与最近 `git diff HEAD~1` 或 CR diff 的重叠文件/函数）*
```

### §1.4 结果写入 CR

如果当前有活跃 CR：
- 报告摘要写入 CR 事件表：`| [日期] | /pace-test 执行 | Claude | N/M passed, X failed | — |`
- 如果 CR 有"验证证据"section → 更新最新测试结果

### §1.7 自动维护 baseline（静默）

无参数运行成功后，自动维护测试基准线数据——将 baseline 从"需要用户主动调用"降级为"测试执行的自然副产物"。

**流程**：

1. 检查 `.devpace/rules/test-baseline.md` 是否存在：
   - **不存在** → 基于本次运行结果自动创建初始基准线文件（格式遵循 `knowledge/_schema/process/test-baseline-format.md`）。输出 1 行："📊 测试基准线已自动建立（.devpace/rules/test-baseline.md）"
   - **已存在** → 将本次运行结果（通过率、耗时、检查项数）静默追加到历史趋势表。不输出任何提示
2. 追加格式：在 test-baseline.md 的历史趋势表末尾添加一行：`| [日期] | [通过率] | [耗时] | [检查项数] | 自动采集 |`

**规则**：
- 测试全部失败时仍记录（基准反映实际状态）
- 自动采集的数据在来源列标注"自动采集"，与用户显式执行 `/pace-test baseline` 产生的"手动建立"区分
- baseline 文件写入失败不影响测试执行流程
- 无 `.devpace/` 目录时跳过（降级模式无持久化目标）

### §1.5 CI/CD 测试结果消费

当 `.devpace/integrations/config.md` 存在且 CI/CD section 包含"检查命令"时，`/pace-test` 可消费 CI 系统的测试结果作为补充数据源。

**触发条件**：空参数运行（`/pace-test`）时自动检测，其他子命令不触发。

**流程**：

1. **检查集成配置**：读取 `integrations/config.md` → CI/CD section → 检查命令
2. **执行 CI 状态查询**：
   - GitHub Actions：`gh run list --branch [当前分支] --limit 1 --json status,conclusion,name`
   - 其他 CI：执行配置的检查命令
3. **解析 CI 结果**：
   - 提取最近一次 CI 运行的状态（passed/failed/running）
   - 如有测试步骤的详细输出，提取通过/失败数
4. **合并到报告**：在 §1.3 报告格式的末尾追加 CI 数据段：

   ```markdown
   ### CI/CD 测试结果（自动采集）

   | 指标 | 值 |
   |------|---|
   | CI 工具 | [工具名] |
   | 最近运行 | [状态] |
   | 分支 | [分支名] |
   | 来源 | integrations/config.md |

   *（CI 运行中时标注"⏳ 运行中，结果待定"）*
   ```

5. **写入 CR 事件表**：如 CI 有新的测试结果（与上次记录不同），追加事件：`| [日期] | CI 测试结果 | CI | [状态] | 自动采集 |`

**降级**：无 integrations/config.md 或无检查命令 → 静默跳过（不报错、不提示配置）。CI 命令执行失败 → 标注"CI 查询失败"，不阻断本地测试报告。

**与本地测试的关系**：CI 结果是补充信号，不替代本地测试执行。报告同时展示本地结果（§1.1-§1.3）和 CI 结果（本段）。两者不一致时（本地通过但 CI 失败，或反之），在报告中标注差异。

### §1.6 智能推荐（仅空参数运行时）

> 规则见 test-procedures-common.md「智能推荐（SSOT）」。

### --brief 输出格式

`测试：N/M passed · 耗时 Xs · 下一步：[推荐]`
