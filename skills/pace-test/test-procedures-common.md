# 测试执行规程——通用

> **职责**：跨子命令共享规则——技术栈检测（SSOT）、分层输出约定（SSOT）、智能推荐规则。按 SKILL.md 路由表按需加载。

## §0 速查卡片

| 子命令 | 文件 | 核心内容 |
|--------|------|---------|
| （空参数） | core | Layer 1 基础执行 + CI 消费 + baseline 维护 |
| accept | verify | AI 验收验证（L1/L2/L3 + 合理化审计） |
| strategy | strategy-gen | PF→测试类型映射 + 金字塔分析 |
| coverage | coverage | 需求覆盖率 + 代码覆盖率辅助 |
| impact | impact | 变更→依赖图→受影响测试 + 热点检查 |
| report | report | CR/Release 级测试摘要 |
| generate | generate（自包含） | PF→测试骨架/完整实现 |
| flaky | flaky（自包含） | 不稳定+主动维护检测 |
| dryrun | dryrun（自包含） | Gate dry-run 预检 |
| baseline | baseline（自包含） | 测试基准线建立/更新 |

- **SSOT 内容**：本文件是技术栈检测、分层输出约定、智能推荐的唯一权威源

## 技术栈检测（SSOT）

多个子命令需要检测项目技术栈。统一检测逻辑如下：

1. 读取 `.devpace/context.md`（如有）→ 获取技术栈信息（语言、测试框架、构建工具）
2. context.md 不存在或无技术栈信息时 → 自动检测项目根目录：

| 探测文件 | 语言 | 测试框架 |
|---------|------|---------|
| `package.json` | JavaScript/TypeScript | Jest / Vitest / Mocha（从 devDependencies 推断） |
| `pyproject.toml` / `setup.py` / `pytest.ini` | Python | pytest |
| `go.mod` | Go | go test |
| `Cargo.toml` | Rust | cargo test |

3. 检测到多种技术栈 → 返回全部（项目可能是多语言）
4. 无可识别技术栈 → 标注"待定"，不阻断后续流程

## 分层输出约定（SSOT）

所有子命令支持三级输出详细度，通过 `--brief` / `--detail` 参数控制：

| 层级 | 触发 | 内容 | 适用场景 |
|------|------|------|---------|
| 摘要 | `--brief` | 1-3 行核心结论（通过率、风险等级、下一步建议） | 自动化消费、快速确认 |
| 标准 | （默认） | 结构化表格 + 汇总 + 建议（当前各规程定义的输出格式） | 日常使用 |
| 详细 | `--detail` | 完整输出含实施指导、历史对比、扩展分析 | 深度审查、首次使用 |

**规则**：
- 未指定参数时使用"标准"层级（向后兼容，当前行为不变）
- `--brief` 输出可被其他 Skill 或 report 子命令程序化消费
- 各子命令的"详细"内容由各规程文件定义
- 子命令摘要行（`--brief`）统一风格：`类型：关键指标1 · 指标2 · 下一步/趋势`

## 智能推荐（SSOT）

空参数运行（`/pace-test`）报告输出后，在末尾附加 1 行"建议下一步"——根据当前 CR 状态推荐最相关的子命令：

| CR 状态 | 推荐 | 理由 |
|---------|------|------|
| developing | "建议：提交前执行 `/pace-test dryrun 1` 预检 Gate 1" | 提前发现质量问题 |
| verifying | "建议：执行 `/pace-test accept` 采集验收证据" | 为 Gate 2/3 提供精细证据 |
| in_review | "建议：执行 `/pace-test report` 生成审查报告" | 辅助人类审批决策 |
| 无活跃 CR | "建议：执行 `/pace-test strategy` 生成测试策略" | 建立测试基线 |
| approved/merged | 不输出推荐 | 已完成流程 |

**执行规则**：
- 仅空参数运行时输出，有子命令参数时不输出（用户已有明确意图）
- 推荐内容为 1 行自然语言，不阻断报告
- 无 `.devpace/` 时不输出推荐（降级模式无 CR 状态可读取）
