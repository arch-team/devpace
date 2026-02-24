# 测试执行规程——策略生成

> **职责**：/pace-test strategy 的测试策略生成规程。

## §0 速查卡片

- **§3 测试策略生成**：PF 验收标准→测试类型映射（主类型+辅助类型），输出测试矩阵

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
