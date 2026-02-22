# 初始化执行规程

> **职责**：初始化和迁移的详细执行规则。/pace-init 触发后，Claude 按需读取本文件。

## 最小初始化（默认）

### 生成规则

1. **state.md**：使用模板，替换占位符：
   - `{{OBJECTIVE}}` → 用户提供的一句话描述
   - `{{MOS_SUMMARY}}` → `（待定义）`
   - `{{NEXT_ACTION}}` → `说"帮我实现 X"开始第一个功能。`
2. **project.md**：使用模板，替换 `{{PROJECT_NAME}}` 和 `{{PROJECT_DESCRIPTION}}`
3. **backlog/**：创建空目录
4. **rules/workflow.md**：从 Plugin 模板复制
5. **rules/checks.md**：从项目类型自动检测生成（见"质量检查引导"章节）
6. **context.md**（可选自动生成）：扫描项目代码库检测技术栈和编码约定：
   - 检测 package.json / pyproject.toml / go.mod / Cargo.toml 确定技术栈
   - 检测 .eslintrc / .prettierrc / ruff.toml / .editorconfig 提取编码规范
   - 检测 tsconfig.json / Dockerfile / docker-compose.yml 推断架构约束
   - 从代码文件采样（3-5 个主要文件）提取命名风格和代码模式
   - 仅记录已确认的约定（检测到的），不猜测未发现的
   - 如果检测到的约定 < 3 条，跳过 context.md 创建（信息量不足）

### .gitignore 建议

初始化完成后提示：
> "建议在 .gitignore 中添加 `.devpace/`，除非你想版本控制项目状态文件。"

如果项目根目录已有 `.gitignore` 且未包含 `.devpace/`，询问是否自动添加。

## 按需目录创建

以下目录和文件在首次使用对应功能时由 Claude 自动创建，不在 init 时预创建：

| 目录/文件 | 创建时机 | 创建者 |
|-----------|---------|--------|
| `iterations/current.md` | 首次 `/pace-plan` | pace-plan Skill |
| `metrics/dashboard.md` | 首次 `/pace-retro` | pace-retro Skill |
| `metrics/insights.md` | 首次 CR merged 后 pace-learn 执行 | pace-learn（自动） |
| `releases/` | 首次 `/pace-release create` | pace-release Skill |
| `integrations/config.md` | 首次配置集成 | pace-init full 或手动 |
| `.devpace/context.md` | `/pace-init` 或首次技术约定讨论 | init-procedures / Claude 自动 |

Claude 在需要写入上述路径时，先检查目录是否存在，不存在则自动创建（mkdir -p 语义），不报错、不提示。

## 延后收集时机

最小初始化时 project.md 为桩状态。以下时机触发内容填充：

1. **首个 CR 创建时**：Claude 根据用户描述自动推断关联的 PF，在 project.md 的价值功能树中创建初始结构（一个推断的 BR + PF + CR 关联），同时为 PF 行追加括号内用户故事（从用户描述提炼）
2. **首次 `/pace-retro`**：如果 project.md 仍无业务目标，引导用户定义 OBJ 和 MoS
3. **用户主动讨论业务目标时**：Claude 引导定义 OBJ 和 MoS 并回填 project.md
4. **首次 `/pace-change` 时**：如果 project.md 的"范围"section 仍为桩状态，引导用户定义"做什么/不做什么"并回填
5. **用户主动讨论项目范围时**：Claude 引导定义范围边界并回填 project.md 的"范围"section
6. **技术/产品讨论中明确偏好时**：Claude 将确认的技术或产品决策追加到 project.md 的"项目原则"section（标注来源和日期）
7. **技术约定讨论时**：用户讨论编码规范、技术选型或架构约束时，Claude 将确认的约定追加到 context.md 对应 section

## v0.1→v0.9 迁移流程

当检测到 `.devpace/state.md` 存在但 `devpace-version` 为 0.1.0 或缺失时触发。

### 迁移步骤

1. **通知用户**："检测到 v0.1.0 项目，建议升级到 v0.9.0 以支持发布管理、缺陷追踪、角色意识、质量增强和技术约定管理。"
2. **创建新目录**（如不存在）：
   - `.devpace/releases/`
   - `.devpace/integrations/`
3. **现有 CR 兼容处理**（不修改用户已有内容）：
   - 无 `类型` 字段的 CR → 视为 `feature`（不写入，读取时默认）
   - 无 `严重度` 字段的 CR → feature 类型不需要，跳过
   - 无 `复杂度`/`执行计划`/`关联`/`checkpoint` 字段 → 全部可选，读取时跳过
4. **更新版本标记**：`state.md` 末尾 `<!-- devpace-version: 0.9.0 -->`
5. **添加教学标记**（如缺失）：`state.md` 末尾 `<!-- taught: -->`（空值，表示全部未教）
6. **更新工作流**：从 Plugin 模板覆盖 `.devpace/rules/workflow.md`（新增 released 状态和 hotfix 路径）
7. **自动扫描 context.md**（可选）：按最小初始化的 context.md 生成规则扫描项目，检测到 ≥3 条约定时自动创建 `.devpace/context.md`
8. **询问发布配置**（Step 2.5）
9. **输出迁移摘要**："升级完成 v0.1.0 → v0.9.0。新增：releases/、integrations/ 目录，教学标记，工作流更新。现有数据无损。"

### 迁移安全规则

- **只添加不删除**：迁移不删除任何现有文件或字段
- **默认值兼容**：新字段全部可选，不填写时使用默认值
- **workflow.md 覆盖确认**：覆盖前告知用户变更内容（新增 released 和 hotfix 路径）
- **回滚方案**：迁移前自动 `git commit`（如有未提交变更），迁移后可通过 `git revert` 回滚
- **跨版本安全**：v0.1.0→v0.9.0 是一次性跳跃迁移，不需要逐版本升级；所有中间版本新增的字段均为可选

## 发布配置收集

### 有发布流程时

额外收集信息：
1. **环境列表**：如 staging、production（写入 `integrations/config.md`）
2. **CI/CD 工具**（可选）：如 GitHub Actions、Jenkins、GitLab CI
3. **发布审批**：自动（CI 通过即部署）/ 手动确认（需人类审批）

生成 `.devpace/integrations/config.md`：

```markdown
# 集成配置

## 环境

| 环境 | 用途 | URL |
|------|------|-----|
| staging | 预发布验证 | [URL] |
| production | 正式环境 | [URL] |

## CI/CD

- **工具**：[工具名称]
- **触发方式**：[push/manual/tag]

## 发布审批

- **模式**：[auto/manual]
```

### 无发布流程时

- 跳过发布配置
- `releases/` 和 `integrations/` 目录不创建（按需创建策略）
- 相关功能（/pace-release、/pace-feedback 的 Release 追溯）降级

## 质量检查引导

### 默认检查项建议

根据项目类型自动建议，包括命令检查和意图检查两种方式：

| 项目类型 | 检测方式 | 命令检查建议 | 意图检查建议 | 安全检查建议 |
|---------|---------|-------------|-------------|-------------|
| Node.js | package.json 存在 | `npm test`、`npm run lint`、`npm run typecheck` | "所有导出函数有 JSDoc" | `npm audit --audit-level=high` |
| Python | pyproject.toml 或 setup.py | `pytest`、`ruff check`、`mypy` | "所有公共函数有 docstring" | `bandit -r src/` |
| Go | go.mod 存在 | `go test ./...`、`golangci-lint run` | "所有导出函数有注释" | `gosec ./...` |
| 通用 | 其他 | 询问用户自定义 | "单个函数不超过 50 行" | Claude 检查"代码中不含硬编码密钥" |

最小初始化时自动检测项目类型并生成 checks.md（包含命令检查和至少 1 条意图检查建议），不询问用户。安全检查为推荐项，生成 checks.md 时作为注释包含（`<!-- 推荐：... -->`），用户可取消注释启用。完整初始化（`full`）时引导用户确认和补充（含安全检查项）。

### 检查项格式

checks.md 支持两种检查类型（格式定义见 `knowledge/_schema/checks-format.md`）：

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
