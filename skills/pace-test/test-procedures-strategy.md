# 测试执行规程——策略与覆盖

> **职责**：/pace-test 的策略生成（§3 strategy）、需求覆盖分析（§4 coverage）、变更影响分析（§5 impact）、测试摘要报告（§6 report）。

## §3 测试策略生成（strategy）

当用户执行 `/pace-test strategy` 时，为项目的 PF 验收条件生成系统化的测试策略。

### 流程

1. **提取 PF 验收标准**：
   - 读取 `project.md` 功能规格 section → 提取所有 PF 及其验收标准
   - 功能规格 section 不存在 → **降级**：从价值功能树提取 PF 列表 + PF 行括号内的用户故事
   - 两者均无内容 → 输出"建议先通过 /pace-plan 或 /pace-change 完善 PF 验收标准"并终止
2. **检测技术栈**：按 test-procedures-core.md §0.1 共用逻辑检测
3. **扫描已有测试**：扫描项目中 `*test*`、`*spec*` 文件，建立已有测试清单
4. **生成测试映射**：对每个 PF 的每条验收条件，推荐主类型 + 辅助类型：

   **主类型判定**（每条验收条件映射 1 个最核心维度）：
   - 数据校验 / 计算逻辑 → unit
   - 模块间交互 / API 调用 → integration
   - 用户交互流 / 端到端场景 → E2E
   - 响应时间 / 吞吐量 / 并发负载条件 → performance
   - 认证 / 授权 / 输入校验 / 数据保护条件 → security
   - 屏幕阅读器 / 键盘导航 / WCAG 合规条件 → accessibility
   - 视觉效果 / 主观体验 → manual（需人工验证）

   **辅助类型触发条件**（叠加到主类型之上，每条 0-2 个辅助类型）：
   - 含安全关键词（认证/授权/加密/敏感数据）→ +security
   - 含性能关键词（响应时间/吞吐量/超时/并发）→ +performance
   - 含用户交互 + 数据操作（且主类型为 unit）→ +integration

   **输出格式**：测试类型列从 `unit` 改为 `unit [+security]`（仅在有辅助类型时添加方括号后缀）
5. **匹配已有测试**：将已有测试文件与验收条件匹配，按两级匹配策略判定状态：

   **匹配算法**：
   1. **名称匹配**（快速）：测试文件名 / describe / test 名 ↔ 验收条件关键词（提取动词+名词对，如"上传CSV" → upload_csv / csv_upload）
   2. **内容匹配**（精确）：测试 import 的模块 ↔ PF 实现代码的重叠度

   **判定标准**：
   - 名称 + 内容均匹配 → **✅ 已有**
   - 仅名称匹配 → **⚠️ 部分覆盖**（需审查内容相关性）
   - 仅内容匹配 → **⚠️ 部分覆盖**（可能间接覆盖）
   - 均不匹配 → **❌ 待建**
6. **生成策略文件**：输出 `.devpace/rules/test-strategy.md`（格式遵循 `knowledge/_schema/test-strategy-format.md`）
7. **输出摘要**：N 个 PF、M 条验收条件、推荐 X unit / Y integration / Z E2E / W manual
8. **后续引导**：输出"有 N 个验收条件待建测试，可执行 `/pace-test generate [PF]` 逐个生成。"
9. **非功能性测试 checks 推荐**（当识别到辅助类型时）：
   - 扫描策略中包含 `[+security]` 或 `[+performance]` 辅助类型的验收条件数量
   - 有 ≥1 个安全辅助类型 → 在输出摘要后附加安全检查推荐模板
   - 有 ≥1 个性能辅助类型 → 在输出摘要后附加性能检查推荐模板
   - 推荐模板根据 test-procedures-core.md §0.1 检测到的技术栈自适应选择工具

   **安全检查推荐模板**：
   ```
   strategy 发现 N 个验收条件含安全辅助类型 [+security]，建议在 checks.md 中添加：
   # - name: 安全依赖扫描
   #   gate: 1
   #   type: 命令
   #   check: [技术栈自适应命令]
   ```
   技术栈→命令映射：Node.js → `npm audit --audit-level=moderate` | Python → `bandit -r .` | Go → `gosec ./...` | Rust → `cargo audit`

   **性能检查推荐模板**：
   ```
   strategy 发现 N 个验收条件含性能辅助类型 [+performance]，建议在 checks.md 中添加：
   # - name: 性能基准测试
   #   gate: 1
   #   type: 命令
   #   check: [技术栈自适应命令]
   ```
   技术栈→命令映射：Node.js → `npx lighthouse --output json --quiet http://localhost:3000` 或 `npm run benchmark`（如有） | Python → `pytest --benchmark`（如有 pytest-benchmark） | Go → `go test -bench=. ./...` | 通用 → `[项目自定义性能测试命令]`

   **输出原则**：模板以注释形式输出（`#` 前缀），用户自行决定是否启用。无辅助类型时不输出。

10. **测试金字塔分析**：统计策略中各测试类型的分布比例，评估健康度：

   **统计规则**：按主类型统计（不含辅助类型后缀），计算每种类型占总验收条件的百分比。

   **健康度评估**：

   | 维度 | 健康 | 警告 | 不健康 |
   |------|------|------|--------|
   | unit 占比 | ≥50% | 30-50% | <30% |
   | E2E 占比 | ≤20% | 20-40% | >40% |
   | manual 占比 | ≤10% | 10-25% | >25% |

   **输出格式**（附加到策略摘要之后）：
   ```
   ### 测试金字塔

   | 测试类型 | 数量 | 占比 | 评估 |
   |---------|------|------|------|
   | unit | N | X% | ✅ 健康 |
   | integration | N | X% | — |
   | E2E | N | X% | ⚠️ 偏高 |
   | performance | N | X% | — |
   | security | N | X% | — |
   | accessibility | N | X% | — |
   | manual | N | X% | ✅ 健康 |

   **金字塔健康度**：[✅ 健康 / ⚠️ 需关注 / ❌ 失衡]
   [如有警告/不健康：具体调整建议]
   ```

   - 整体健康度判定：有 ≥1 个"不健康"维度 → ❌ 失衡 | 有 ≥1 个"警告" → ⚠️ 需关注 | 全部健康 → ✅ 健康
   - 仅统计有值的类型行（count=0 的不输出）

11. **测试数据策略建议**：基于验收条件和技术栈，推荐测试数据管理方案：

   **触发条件**：策略中存在 integration 或 E2E 类型的验收条件时生成（纯 unit 项目跳过）。

   **推荐规则**（按技术栈）：

   | 技术栈 | 数据准备 | 隔离策略 | 推荐工具 |
   |--------|---------|---------|---------|
   | Python | Factory 模式 | 事务回滚 / 测试数据库 | factory_boy + faker |
   | JS/TS | Builder 模式 | 内存数据库 / Mock | @faker-js/faker + testcontainers |
   | Go | Table-driven + fixtures | 独立 schema / 事务 | testify + go-txdb |
   | Rust | Builder 模式 | 独立测试数据库 | fake + sqlx test |

   **输出格式**（附加到策略文件末尾）：
   ```markdown
   ## 测试数据策略

   - **数据准备**：[推荐方式]（[推荐工具]）
   - **隔离策略**：[推荐方式]
   - **敏感数据**：测试中不使用真实用户数据，使用 [faker 工具] 生成模拟数据
   - **环境重置**：[按技术栈推荐的重置方式]
   ```

   - 无法识别技术栈时输出通用建议（Factory/Builder 模式 + 事务隔离 + faker 生成）
   - 纯 unit 项目不输出此 section

12. **测试实施指导**：为策略中出现的每种测试类型生成可执行的实施指导：

   **触发条件**：始终生成（与步骤 4-8 的策略映射配套）。

   **指导内容生成规则**：

   对策略中出现的每种测试类型（去重），生成对应的实施指导块。每个指导块包含：

   #### unit 实施指导

   | 技术栈 | 框架 | 初始化命令 | 配置文件 | 运行命令 |
   |--------|------|-----------|---------|---------|
   | JS/TS | Jest | `npm i -D jest` | `jest.config.js` | `npx jest` |
   | JS/TS | Vitest | `npm i -D vitest` | `vitest.config.ts` | `npx vitest` |
   | Python | pytest | `pip install pytest` | `pytest.ini` / `pyproject.toml` | `pytest -v` |
   | Go | go test | 内置 | — | `go test ./...` |
   | Rust | cargo test | 内置 | — | `cargo test` |

   **推荐模式**：Arrange-Act-Assert (AAA)、每个测试文件对应一个源文件、测试文件命名 `test_*.py` / `*.test.ts`

   #### integration 实施指导

   | 技术栈 | 场景 | 推荐方案 | 工具 |
   |--------|------|---------|------|
   | JS/TS | API 集成 | SuperTest + Jest | `npm i -D supertest` |
   | JS/TS | 契约测试 | Pact | `npm i -D @pact-foundation/pact` |
   | Python | API 集成 | pytest + httpx/requests | `pip install httpx` |
   | Python | 契约测试 | Pact | `pip install pact-python` |
   | Go | API 集成 | httptest + testify | 内置 `net/http/httptest` |

   **推荐模式**：测试容器（testcontainers）管理外部依赖、API schema 验证（OpenAPI）、契约测试（Pact）验证服务间兼容性

   #### E2E 实施指导

   | 技术栈 | 框架 | 初始化命令 | 推荐模式 |
   |--------|------|-----------|---------|
   | 前端/全栈 | Playwright | `npm init playwright@latest` | Page Object Model |
   | 前端/全栈 | Cypress | `npm i -D cypress` | App Actions |
   | Python Web | pytest + Playwright | `pip install playwright && playwright install` | Page Object Model |

   **推荐模式**：Page Object Model 封装页面交互、数据属性选择器（`data-testid`）定位元素、视觉回归测试（可选，Playwright `toHaveScreenshot()`）

   #### performance 实施指导

   | 场景 | 工具 | 安装 | 用法 |
   |------|------|------|------|
   | HTTP 负载测试 | k6 | `brew install k6` / Docker | `k6 run script.js` |
   | Python 基准 | pytest-benchmark | `pip install pytest-benchmark` | `pytest --benchmark` |
   | Go 基准 | go test -bench | 内置 | `go test -bench=. ./...` |
   | 前端性能 | Lighthouse CI | `npm i -D @lhci/cli` | `lhci autorun` |

   **推荐模式**：建立性能基线 → 回归检测（每次测试对比基线）、响应时间 P95/P99 指标优于平均值

   #### security 实施指导

   | 场景 | 工具 | 安装 | 用法 |
   |------|------|------|------|
   | 依赖漏洞 | npm audit / pip-audit / gosec | 内置或 `pip install pip-audit` | `npm audit` / `pip-audit` / `gosec ./...` |
   | SAST 静态分析 | Semgrep | `pip install semgrep` | `semgrep --config auto .` |
   | DAST 动态扫描 | OWASP ZAP | Docker | `docker run owasp/zap2docker-stable zap-baseline.py` |
   | 密钥泄露 | gitleaks | `brew install gitleaks` | `gitleaks detect` |

   **推荐模式**：依赖扫描纳入 CI 必跑、SAST 在 Gate 1 级别检查、DAST 在集成环境运行

   #### accessibility 实施指导

   | 场景 | 工具 | 集成方式 |
   |------|------|---------|
   | 自动化检测 | axe-core | `npm i -D @axe-core/playwright` 或 `@axe-core/react` |
   | CI 集成 | pa11y | `npm i -D pa11y` → `pa11y http://localhost:3000` |
   | Lighthouse | Lighthouse a11y | `lighthouse --only-categories=accessibility` |

   **推荐模式**：axe-core 集成到 E2E 测试（每个页面测试后追加 `checkA11y()`）、WCAG 2.1 AA 合规为目标

   #### manual 标注说明

   manual 类型无自动化实施指导。在策略文件中标注以下内容供人类测试者参考：
   - 验证步骤（从验收条件推导的具体操作序列）
   - 预期结果（可观察的成功标志）
   - 测试数据建议（如需特定数据/账号/环境）

   **输出格式**（附加到策略文件末尾的"实施指导"section）：
   ```markdown
   ## 实施指导

   > 基于策略中出现的测试类型，提供框架选型和配置建议。

   ### [测试类型]

   **推荐框架**：[框架名]
   **初始化**：`[安装命令]`
   **配置**：[配置文件位置/内容]
   **运行**：`[运行命令]`
   **推荐模式**：[模式描述]

   [仅输出策略中实际出现的测试类型，未出现的类型不生成]
   ```

   **生成规则**：
   - 仅为策略中实际出现的测试类型生成指导（去重后遍历）
   - 优先匹配 test-procedures-core.md §0.1 检测到的技术栈；多技术栈时全部列出
   - 已有测试框架时（context.md 中声明或自动检测到），推荐与已有框架一致的方案
   - 项目已有同类测试配置时（如已有 `jest.config.js`），标注"已配置"并跳过初始化步骤

### 降级场景

| 条件 | 行为 |
|------|------|
| 无功能规格 section | 从价值功能树提取 PF + 用户故事 |
| 无价值功能树 | 输出引导信息并终止 |
| 无 context.md | 自动检测技术栈 |
| 无可识别技术栈 | 测试框架列填"待定"，策略仍生成 |

---

## §4 需求覆盖分析（coverage）

当用户执行 `/pace-test coverage` 时，分析 PF 验收条件的测试覆盖情况。

### 流程

1. **加载策略**：
   - 读取 `.devpace/rules/test-strategy.md`（如存在）→ 获取 PF→测试映射
   - 如果不存在 → 直接从 `project.md` 提取 PF 验收条件列表作为基准
2. **加载检查项**：读取 `.devpace/rules/checks.md` → 提取已配置的命令检查项
3. **扫描测试文件**：扫描项目中 `*test*`、`*spec*` 文件 → 建立已有测试清单
4. **覆盖映射**：对每条 PF 验收条件，判定是否有对应的测试命令或测试文件覆盖：
   - 在 test-strategy.md 中标记 ✅ 已有 → 已覆盖
   - 在 checks.md 中有对应命令检查 → 已覆盖
   - 扫描到匹配的测试文件 → 已覆盖
   - 以上均无 → 未覆盖
5. **采集代码覆盖率**（辅助信号）：
   - 检测项目是否有覆盖率工具（按技术栈匹配，见下表）
   - 有 → 执行覆盖率命令，采集行覆盖率/分支覆盖率数据
   - 无 → 跳过，不阻断流程
   - **定位**：代码覆盖率是辅助信号，不替代需求覆盖率。需求覆盖率回答"验收标准是否被测试"，代码覆盖率回答"代码是否被执行"——两者互补

   | 技术栈 | 覆盖率命令 | 输出解析 |
   |--------|----------|---------|
   | Jest (JS/TS) | `npx jest --coverage --coverageReporters=json-summary` | `coverage/coverage-summary.json` → lines/branches/functions 百分比 |
   | pytest (Python) | `pytest --cov --cov-report=json` | `coverage.json` → totals.percent_covered |
   | go test (Go) | `go test -coverprofile=coverage.out ./... && go tool cover -func=coverage.out` | 最后一行 total 百分比 |
   | cargo (Rust) | `cargo tarpaulin --out json`（如已安装） | `tarpaulin-report.json` → coverage 百分比 |

6. **生成覆盖率报告**
7. **持久化覆盖数据**：如果 `.devpace/rules/test-strategy.md` 存在，将覆盖分析结果回写到策略总览表的"已覆盖"和"覆盖率"列。如果 test-strategy.md 不存在，跳过持久化（仅输出到控制台）
8. **覆盖率阈值检查**（可选门禁）：

   **触发条件**：`test-strategy.md` 存在且包含"覆盖率阈值"字段时执行。不存在或无阈值配置时静默跳过。

   **阈值配置**（在 test-strategy.md 策略总览 section 之后）：
   ```markdown
   ## 覆盖率阈值（可选）

   | 指标 | 阈值 | 当前值 | 状态 |
   |------|------|--------|------|
   | 需求覆盖率 | 80% | [自动填充] | ✅ / ❌ |
   | 代码覆盖率 | 60% | [自动填充] | ✅ / ❌ / —（未采集） |
   ```

   **检查逻辑**：
   - 读取阈值表中的目标值 → 与 Step 4/5 的实际值对比
   - 需求覆盖率 < 阈值 → 输出 `❌ 需求覆盖率 X% 低于阈值 Y%` + 列出未覆盖的高优先级条件
   - 代码覆盖率 < 阈值（且有采集数据）→ 输出 `⚠️ 代码覆盖率 X% 低于阈值 Y%`（辅助信号，用 ⚠️ 而非 ❌）
   - 代码覆盖率未采集 → 状态填"—"，不判定失败
   - 全部达标 → 输出 `✅ 覆盖率阈值检查通过`

   **与 Gate 的关系**：
   - 阈值检查是 coverage 子命令的附加输出，不阻断 Gate 流程
   - 如需将覆盖率作为 Gate 门禁，用户应在 checks.md 中添加对应的命令检查项（如 `pytest --cov --cov-fail-under=80`）
   - 此处的阈值检查定位为"可视化告警"，帮助团队感知覆盖率趋势

   **初始配置**：`/pace-test strategy` 生成策略文件时，不自动创建阈值表（零摩擦原则）。用户可手动在 test-strategy.md 中添加阈值 section。`/pace-test coverage` 检测到阈值 section 后自动执行检查并更新"当前值"和"状态"列

### 输出格式

```markdown
## 需求验证覆盖率

| PF | 功能名 | 验收条件 | 已覆盖 | 覆盖率 |
|----|--------|---------|--------|--------|
| PF-001 | 用户认证 | 5 | 3 | 60% |
| PF-002 | 数据导入 | 3 | 0 | 0% |

**需求覆盖率**：M/N (X%)

### 代码覆盖率（辅助信号）

| 指标 | 值 |
|------|---|
| 行覆盖率 | X% |
| 分支覆盖率 | Y%（如有） |
| 来源 | [工具名称] |

*（如未检测到覆盖率工具：标注"项目未配置代码覆盖率工具"）*

### 未覆盖的高优先级条件

| PF | # | 验收条件 | 推荐测试类型 |
|----|---|---------|-------------|
| PF-001 | 3 | [条件文本] | integration |

### 建议

- [按优先级排列的测试补全建议]
```

---

## §5 变更影响分析（impact）

当用户执行 `/pace-test impact [CR编号]` 时，基于代码变更范围分析变更影响和回归风险。

### 流程

1. **确定分析范围**：
   - 有 CR 参数 → 读取该 CR 的 diff（从 CR 事件表或 git log 获取）
   - 无参数 → 读取当前活跃 CR 的 diff（状态为 developing/verifying 的 CR）
   - 无活跃 CR → 使用 `git diff HEAD~1` 作为默认范围
2. **提取变更文件列表**：从 `git diff` 提取已修改、新增、删除的文件列表
3. **建立文件→PF 反向映射**：
   - 读取 `project.md` 价值功能树 → 通过 CR 关联找到 PF
   - 如果 `.devpace/rules/test-strategy.md` 存在 → 补充测试文件→PF 的映射
4. **识别受影响的 PF**：变更文件与哪些 PF 的实现代码或测试代码相关
5. **评估间接影响**：分析变更文件的导入关系（import/require），识别间接受影响的模块
6. **提取回归测试建议**：
   - 如果 `test-strategy.md` 存在 → 从中提取受影响 PF 的推荐测试
   - 如果 `insights.md` 存在 → 检查历史 pattern（"该模块曾多次出现 X 类问题"）
7. **评估风险等级**：基于变更范围大小 × PF 重要性（优先级）综合评定
8. **快速执行模式**（`impact --run`）：
   - 如果用户指定了 `--run` 参数 → 在输出影响分析报告后，自动执行"必跑"列表中的测试
   - 执行方式：从 checks.md 中匹配"必跑"推荐的测试命令 → 逐项执行 → 附加执行结果到影响分析报告末尾
   - 如果 checks.md 中无匹配的测试命令 → 按 test-procedures-core.md §1.2 自动检测逻辑查找可用测试命令 → 执行全部（此时等价于 §1 无参数运行）
   - 未指定 `--run` → 仅输出分析报告，不执行测试（默认行为，向后兼容）

### 风险等级评定规则

| 条件 | 风险等级 |
|------|---------|
| 变更 ≤3 文件 且 仅影响 P2 功能 | 🟢 低 |
| 变更 4-10 文件 或 影响 P1 功能 | 🟡 中 |
| 变更 >10 文件 或 影响 P0 功能 或 涉及共享依赖 | 🔴 高 |

### 输出格式

```markdown
## 变更影响分析

**CR**：[CR 标题]（如有）
**变更范围**：N 文件 / M 模块

### 受影响的产品功能

| PF | 功能名 | 影响类型 | 建议测试 |
|----|--------|---------|---------|
| PF-001 | 用户认证 | 直接变更 | [测试列表] |
| PF-003 | 报表导出 | 间接影响（共享依赖 utils.py） | 建议抽查 |

### 风险评估

**风险等级**：🟡 中
**理由**：变更涉及 6 个文件，影响 P1 功能"用户认证"

### 影响测试建议

1. **必跑**：[直接受影响 PF 的核心测试]
2. **建议跑**：[间接影响模块的测试]
3. **可选**：[低风险区域的抽查]

### 快速执行结果（--run 模式）

| # | 测试命令 | 状态 | 耗时 |
|---|---------|------|------|
| 1 | [命令] | ✅ PASS | X.Xs |
| 2 | [命令] | ❌ FAIL | X.Xs |

*（仅在 `--run` 模式下输出此段）*
```

### §5.1 结果持久化

impact 分析完成后，将关键结果写入 CR 文件以支持跨会话引用：

1. **CR 事件表追加**：`| [日期] | /pace-test impact | Claude | 风险 [等级], 影响 [N] PF, 变更 [M] 文件 | — |`
2. **CR 文件可选"影响分析"section**（详情持久化）：
   - 写入内容：变更范围 + 风险等级 + 受影响 PF 表 + 测试建议 + --run 结果（如有）
   - 格式遵循 `knowledge/_schema/cr-format.md` 的"影响分析"section 定义
   - 多次执行 → 覆盖更新（保留最新分析结果）
   - 无活跃 CR → 仅控制台输出，不持久化

### 降级场景

| 条件 | 行为 |
|------|------|
| 无 CR、无 git diff | 输出"无可分析的变更范围"并终止 |
| 无 project.md 价值功能树 | 仅输出变更文件列表，无法映射到 PF |
| 无 test-strategy.md | 不输出具体测试建议，仅输出受影响 PF |
| 无 insights.md | 跳过历史 pattern 分析 |

---

## §6 测试摘要报告（report）

当用户执行 `/pace-test report [CR编号|REL-xxx]` 时，聚合多层测试数据生成面向人类的审查报告。

### 模式路由

| 参数 | 模式 | 说明 |
|------|------|------|
| CR 编号（CR-xxx） | CR 模式 | 单个 CR 的三层测试报告（默认） |
| Release 编号（REL-xxx） | Release 模式 | 聚合 Release 下所有 CR 的测试数据（§6.2） |
| （空） | CR 模式 | 使用当前活跃 CR |

### §6.1 CR 模式流程

1. **确定 CR**：有参数 → 指定 CR；无参数 → 当前活跃 CR
2. **聚合数据源**（按可用性，有什么用什么）：
   - **Layer 1**：最近的 `/pace-test` 执行结果（从 CR 事件表中提取）
   - **Layer 2**：`/pace-test coverage` 的需求覆盖率（如已执行过，从 test-strategy.md 读取）——当 CR 有关联 PF 时，仅展示当前 CR 关联 PF 的覆盖行（过滤非关联 PF）；CR 无关联 PF 时展示全部（项目级视图）
   - **Layer 3**：`/pace-test accept` 的验收验证报告（从 CR 验证证据 section 提取）
3. **数据不足时的处理**：
   - 无任何已有数据 → 提示用户"无测试数据，是否先执行 `/pace-test` 获取基础数据？"——用户确认后执行，用户拒绝则输出空报告模板（各 Layer 均标注"未执行"）
   - 仅缺 Layer 2/3 → 在报告中标注"未执行"，不强制补全。**同时在报告末尾附加"数据补全建议"段**：
     ```markdown
     ### 数据补全建议

     当前报告缺少 N 层数据。可执行以下命令补全：
     1. `/pace-test coverage` — 获取需求覆盖率分析（Layer 2）
     2. `/pace-test accept` — 执行 AI 验收验证（Layer 3）
     补全后重新执行 `/pace-test report` 获取完整报告。
     ```
     - 根据实际缺失情况动态列出缺失层（仅列缺失的，不列已有的）
     - 保持"有什么用什么"原则——不阻断报告生成，仅在末尾附加引导
4. **生成审查报告**（服务 Gate 3 人类审批决策）

### 输出格式

```markdown
## 测试摘要报告

**CR**：[CR 标题] | **PF**：[关联功能名] | **日期**：[生成日期]

### 自动测试结果（Layer 1）

| 状态 | 检查项 | 备注 |
|------|--------|------|
| ✅ | [检查名] | — |
| ❌ | [检查名] | [失败原因摘要] |

**汇总**：N/M passed

### 需求覆盖情况（Layer 2，当前 CR 关联功能）

验收条件覆盖率：X/Y (Z%)
未覆盖项：[列表]

*（如未执行 /pace-test coverage：标注"未评估——建议执行 /pace-test coverage"）*
*（如 CR 无关联 PF：展示全项目 PF 覆盖数据，标题改为"需求覆盖情况（Layer 2，项目级）"）*

### AI 验收验证（Layer 3）

| # | 验收条件 | 验证结果 | 备注 |
|---|---------|---------|------|
| 1 | [条件] | ✅ 通过 | — |
| 2 | [条件] | ❌ 未通过 | [原因] |

*（如未执行 /pace-test accept：标注"未验证——建议执行 /pace-test accept"）*
*（如 CR 验证证据含"降级验证"标记：附加"⚠️ 仅 CR 意图级验证，非 PF 级验收"）*

### 审批建议

**风险点**：
- [未覆盖的验收条件]
- [未通过的测试]
- [未执行的验证层]

**建议**：[可以合并 / 建议补充测试后合并 / 建议打回]
```

### 审批建议判定规则

| 条件 | 建议 |
|------|------|
| Layer 1 全通过 + Layer 3 全通过 + Layer 2 覆盖率 ≥80% | ✅ 可以合并 |
| Layer 1 全通过 + Layer 3 有未通过项 ≤1 | ⚠️ 建议补充测试后合并 |
| Layer 1 有失败 或 Layer 3 有多项未通过 | ❌ 建议打回 |
| Layer 2/3 未执行 | ⚠️ 建议先完善测试覆盖再审批 |

### §6.2 Release 模式流程

当参数为 `REL-xxx` 时，生成 Release 级质量报告。

1. **定位 Release**：在 `.devpace/releases/` 中查找对应 Release 文件
   - 不存在 → 输出"未找到 Release [REL-xxx]"并终止
2. **提取关联 CR 列表**：从 Release 文件的 CR 清单中获取所有关联 CR
3. **逐 CR 聚合数据**：对每个 CR 提取：
   - 最近的测试执行结果（CR 事件表）
   - accept 验收状态（CR 验证证据 section）
   - Gate 通过状态
4. **数据完整性评估**：
   - 统计缺少 accept 或 coverage 数据的 CR 占比（未执行率）
   - 未执行率 >30% → 在报告末尾输出批量补全建议清单（见下方"补全建议"格式）
   - 未执行率 ≤30% → 在 CR 质量汇总表中标注"未测试"即可
5. **生成 Release 质量报告**

#### Release 报告格式

```markdown
## Release 质量报告

**Release**：[REL-xxx] | **版本**：[版本号] | **日期**：[生成日期]
**CR 数量**：N | **PF 覆盖**：M 个功能

### CR 质量汇总

| CR | 标题 | 测试状态 | 验收状态 | Gate | 风险 |
|----|------|---------|---------|------|------|
| CR-001 | [标题] | ✅ N/M passed | ✅ 全通过 | Gate 2 ✅ | 🟢 |
| CR-002 | [标题] | ❌ 2 failed | ⚠️ 1 项未通过 | Gate 2 ✅ | 🟡 |

### 功能覆盖

| PF | 功能名 | 关联 CR | 验收覆盖率 |
|----|--------|--------|-----------|
| PF-001 | [功能名] | CR-001, CR-003 | 100% |

### Release 风险评估

**整体风险**：[🟢 低 / 🟡 中 / 🔴 高]

**风险因素**：
- [未通过测试的 CR 数量]
- [未完成验收的 PF]
- [无测试数据的 CR]

**发布建议**：[可以发布 / 建议修复后发布 / 建议推迟]
```

#### Release 发布建议判定规则

| 条件 | 建议 |
|------|------|
| 所有 CR 测试通过 + 所有 PF 验收覆盖率 ≥80% | ✅ 可以发布 |
| 个别 CR 有测试失败但均为 P2 功能 | ⚠️ 建议修复后发布 |
| P0/P1 功能有测试失败或验收未通过 | ❌ 建议推迟 |
| 有 CR 无任何测试数据 | ⚠️ 建议补全测试后发布 |

#### 补全建议格式（未执行率 >30% 时输出）

```markdown
### 补全建议

以下 CR 缺少测试数据，建议逐个执行补全：

| CR | 缺少数据 | 补全命令 |
|----|---------|---------|
| CR-xxx | accept | `/pace-test accept CR-xxx` |
| CR-yyy | coverage | `/pace-test coverage` |
| CR-zzz | 基础测试 | `/pace-test`（在 CR-zzz 推进模式下） |
```

#### Release 模式降级

| 条件 | 行为 |
|------|------|
| 无 releases/ 目录 | 输出"Release 管理未启用，建议先执行 /pace-release create" |
| CR 无测试数据 | 该 CR 标注"未测试"，不阻断报告生成 |
| 无 test-strategy.md | 跳过验收覆盖率分析 |
