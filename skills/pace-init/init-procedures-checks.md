# 工具链检测参考数据

> **职责**：工具链精准检测的映射表和默认检查项建议。核心行为规则（何时触发、如何生成 checks.md）见 `init-procedures-core.md` §9。

## 生态系统精准检测表

### Node.js

| 检测源 | 检测字段 | 生成命令 |
|--------|---------|---------|
| package.json devDependencies | `vitest` | `npx vitest run` |
| package.json devDependencies | `jest` | `npx jest` |
| package.json devDependencies | `mocha` | `npx mocha` |
| package.json scripts | `test` 脚本 | `npm test`（兜底，仅当无上述工具时） |
| package.json devDependencies | `@biomejs/biome` | `npx biome check .` |
| `.eslintrc*` 或 `eslint.config.*` | 文件存在 | `npx eslint .` |
| `.prettierrc*` | 文件存在 | `npx prettier --check .` |
| package.json devDependencies | `typescript` | `npx tsc --noEmit` |

### Python

| 检测源 | 检测字段 | 生成命令 |
|--------|---------|---------|
| pyproject.toml `[tool.pytest]` | section 存在 | `pytest` |
| pyproject.toml `[tool.ruff]` | section 存在 | `ruff check .` |
| pyproject.toml `[tool.mypy]` | section 存在 | `mypy .` |
| pyproject.toml `[tool.pyright]` | section 存在 | `pyright` |
| setup.cfg `[flake8]` | section 存在 | `flake8` |
| pyproject.toml dependencies | `bandit` | `bandit -r src/` |

### Go

| 检测源 | 检测字段 | 生成命令 |
|--------|---------|---------|
| go.mod | 文件存在 | `go test ./...` |
| .golangci.yml | 文件存在 | `golangci-lint run` |
| go.mod | 文件存在 | `go vet ./...` |

### Rust

| 检测源 | 检测字段 | 生成命令 |
|--------|---------|---------|
| Cargo.toml | 文件存在 | `cargo test` |
| Cargo.toml | 文件存在 | `cargo clippy -- -D warnings` |
| Cargo.toml | 文件存在 | `cargo audit`（如 cargo-audit 可检测） |

## 通用规则

- 未检测到具体工具 → 保留通用占位符 `{{CHECK_COMMAND}}`
- 生成的命令必须直接可执行（不需要额外安装）
- 安全检查建议作为注释包含（`<!-- 推荐：... -->`），用户可取消注释启用
- 最小初始化时自动生成不询问；`--full` 模式时引导用户确认和补充

## 默认检查项建议

意图检查编写指南和更多示例见 `knowledge/_guides/checks-guide.md`。

| 项目类型 | 意图检查建议 | 安全检查建议 |
|---------|-------------|-------------|
| Node.js | "所有导出函数有 JSDoc" | `npm audit --audit-level=high` |
| Python | "所有公共函数有 docstring" | `bandit -r src/` |
| Go | "所有导出函数有注释" | `gosec ./...` |
| Rust | "所有 pub 函数有文档注释" | `cargo audit` |
| 通用 | "单个函数不超过 50 行" | Claude 检查"代码中不含硬编码密钥" |

## 检查项格式

checks.md 支持两种检查类型（格式定义见 `knowledge/_schema/process/checks-format.md`）：

- **命令检查**：`检查方式：[bash 命令]`——exit code 判定（0=通过）
- **意图检查**：`检查方式：Claude 检查 [自然语言规则]`——Claude 阅读变更代码对照规则判定

```markdown
## 质量检查

### Gate 1：代码质量（developing → verifying）
- [ ] [检查名称]：`[命令]`
- [ ] [检查名称]：Claude 检查 [自然语言规则]

### Gate 2：集成验证（verifying → in_review）
- [ ] [检查名称]：`[命令]`
- [ ] [检查名称]：Claude 检查 [自然语言规则]

### Gate 3：人类审批（in_review → approved）
- [ ] 人类审批：Code Review 通过
```
