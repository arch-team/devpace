# skill-creator 集成约定

> **按需参考**：仅在使用 `/skill-creator` 创建或评估 Skill 时加载本文件。

`/skill-creator` 的评估工作区（`skills/<name>-workspace/`）已通过 `.gitignore` 排除入库。使用时遵循以下约定：

## 产物位置规范

| 产物 | 位置 | 入库 |
|------|------|------|
| 评估工作区 | `skills/<name>-workspace/`（skill-creator 默认行为） | 否（.gitignore） |
| behavioral eval | `tests/evaluation/<name>/evals.json` | 是（权威源） |
| trigger eval | `tests/evaluation/<name>/trigger-evals.json` | 是（权威源） |
| `--static` HTML | `skills/<name>-workspace/iteration-N/review.html` | 否 |
| 跨 Skill 文件 | `tests/evaluation/_cross-cutting/` | 是 |

**`--static` 路径规则**：当 `generate_review.py` 需要使用 `--static` 模式时，输出路径必须放在工作区内：`<workspace>/iteration-N/review.html`，不要使用 `/tmp/` 或其他外部路径。

## Eval 目录结构

```
tests/evaluation/
├── _cross-cutting/            # 跨 Skill 全局文件（acceptance-matrix、shared-assertions 等）
├── pace-init/                 # per-Skill 子目录（目录名 = Skill 名）
│   ├── evals.json             # behavioral eval（统一命名，不带 Skill 名前缀）
│   └── trigger-evals.json     # trigger eval
├── pace-dev/
│   ├── evals.json
│   └── trigger-evals.json
└── ...
```

**命名规则**：
- 子目录名 = Skill 目录名（如 `pace-dev`）
- eval 文件统一命名 `evals.json` 和 `trigger-evals.json`（由目录区分 Skill）
- `_cross-cutting/` 前缀 `_` 确保排在最前

## 三层评估体系

| 层级 | 文件 | 用途 | 执行时机 |
|------|------|------|---------|
| T1 Trigger | `trigger-evals.json` | 触发精度（~20 查询/Skill） | description 修改后 |
| T2 Behavioral | `evals.json` | 行为正确性断言 | procedures/SKILL.md 修改后 |
| T3 Full Cycle | skill-creator 完整流程 | with/without 对比 + grading | 重大重构/新 Skill |

## Eval 格式权威来源

eval JSON 格式由 **skill-creator 自身**（`references/schemas.md`）定义。devpace 不在 `knowledge/_schema/` 中重复定义 eval 格式——eval 是开发层关注点，不属于产品层。

## 跨 Skill 交叉污染测试

创建 trigger eval 时，必须包含兄弟 Skill 的典型查询作为负面测试用例。重点测试对见 `tests/evaluation/_cross-cutting/shared-assertions.md`。
