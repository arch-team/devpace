# full 模式增强规程

> **职责**：`/pace-init full` 专用规程。覆盖环境探测、分阶段引导和发布配置收集。核心初始化规则见 `init-procedures-core.md`。

## §1 环境探测

当 `/pace-init full` 执行时，在信息收集和生成目录之间，自动执行环境探测。探测结果用于预填 `context.md` 和 `integrations/config.md`，减少用户手动配置。

### 探测步骤

#### 1. 项目类型检测

扫描项目根目录的配置文件，识别技术栈和项目架构：

| 探测文件 | 推断信息 | 写入位置 |
|---------|---------|---------|
| `package.json` | 语言=JS/TS + 框架（react/vue/angular/next/express 从 dependencies 推断） | context.md 技术栈 |
| `pyproject.toml` / `setup.py` | 语言=Python + 框架（django/flask/fastapi 从依赖推断） | context.md 技术栈 |
| `go.mod` | 语言=Go + module 名 | context.md 技术栈 |
| `Cargo.toml` | 语言=Rust | context.md 技术栈 |
| `tsconfig.json` | TypeScript 启用 + strict 模式等配置 | context.md 技术栈 |
| `Dockerfile` / `docker-compose.yml` | 容器化部署 | context.md 架构约束 |
| `Makefile` / `justfile` | 构建系统 | context.md 构建工具 |

多技术栈项目（monorepo 等）→ 全部记录。无可识别配置文件 → 标注"待定"。

#### 2. MCP 感知

检查 Claude Code 环境中已可用的 MCP Server，预填集成建议：

| 检查路径 | 推断信息 | 写入位置 |
|---------|---------|---------|
| `.mcp.json`（项目级） | 已配置的 MCP Server 列表 | integrations/config.md MCP section |
| 全局 MCP 配置（Claude Code 用户设置） | 全局可用的 MCP Server | integrations/config.md MCP section |

**预填逻辑**：
- 检测到 Playwright MCP → 标注"可用于 E2E 测试和浏览器验收"
- 检测到 Tavily MCP → 标注"可用于研究和文档查询"
- 无 MCP 配置 → 跳过此 section

#### 3. CI/CD 检测

按 `knowledge/_schema/integration/integrations-format.md` "CI 自动检测映射表"扫描项目 CI/CD 配置。full 模式额外提取深度信息：

| CI 工具 | 额外推断 |
|---------|---------|
| GitHub Actions | 工作流名称、触发事件（push/PR/tag） |
| GitLab CI | 阶段定义 |
| 其他 | Pipeline/配置存在性 |

额外检测部署平台（非 CI 工具）：

| 探测文件 | 部署平台 |
|---------|---------|
| `vercel.json` / `.vercel/` | Vercel |
| `netlify.toml` | Netlify |

**预填逻辑**：提取工具名称和触发方式 → 写入 integrations/config.md CI/CD section。无 CI/CD 配置 → 跳过。

#### 4. Git 策略检测

按 `init-procedures-core.md` "Git 策略检测"规则执行。full 模式下探测结果在 §1 探测摘要中展示给用户确认。

### 探测输出

探测完成后，输出探测摘要给用户确认：

```
环境探测完成：
- 技术栈：[语言] + [框架]（从 [配置文件] 检测）
- CI/CD：[工具名]（[触发方式]）
- 分支策略：[策略名]
- MCP：[N] 个可用 Server
以上信息已预填到 context.md 和 integrations/config.md，你可以修改或补充。
```

### 探测安全规则

- **只检测不猜测**：仅记录从配置文件中确认的信息，不推测缺失的配置
- **不执行命令**：除 `git branch` 外不执行项目的构建/测试命令
- **用户确认**：探测结果在完整初始化流程中展示给用户确认，不自动写入
- **最小初始化不触发**：环境探测仅在 `--full` 模式中执行（但 Git 策略检测在阶段 B/C 默认执行）

## §2 分阶段引导

### 阶段 1：基础（必须）

执行生命周期检测 + 信息收集 + 生成 .devpace/（同最小初始化 + 环境探测）。完成后立即可用。

### 阶段 2：业务（可选）

使用 AskUserQuestion 询问："要现在定义业务愿景和目标吗？可稍后 /pace-biz 补充。"

用户选择"现在定义"→ 引导收集：

**2a. 愿景（写入 vision.md，格式遵循 `knowledge/_schema/entity/vision-format.md`）**：
1. 目标用户：谁会用这个产品？
2. 核心问题：他们的什么痛点？
3. 差异化：为什么选你而不是替代方案？（可选，可留空）
4. 成功图景：做成了是什么样？（可选，可留空）

**2b. 战略上下文（写入 project.md 战略上下文 section）**：
1. 核心假设：这个项目基于什么关键假设？（可选）
2. 外部约束：有什么不可改变的限制条件？（可选）

**2c. 业务目标（OBJ）（独立文件格式遵循 `knowledge/_schema/entity/obj-format.md`）**：
1. 目标描述 + 类型（引导时先提示 business/product/tech，完整 6 类见 obj-format.md §OBJ 类型定义）+ 时间维度（短期/中期/长期）
2. 成效指标（MoS）：可衡量的指标列表
3. 业务需求（BR）：高层需求分解（可选，可稍后 /pace-biz decompose）

**2d. 创建 opportunities.md**：自动创建空的业务机会看板文件。

用户选择"稍后再说"→ 跳过，project.md 保持桩状态。

### 阶段 3：发布配置（可选）

使用 AskUserQuestion 询问："检测到 [CI 工具]，要配置发布流程吗？可稍后编辑 integrations/config.md。"

用户选择"现在配置"→ 引导收集发布配置（见 §3 发布配置收集）。
用户选择"稍后再说"→ 跳过。

### 阶段 4：外部同步（可选）

使用 AskUserQuestion 询问："检测到 GitHub 仓库，要配置外部同步吗？可稍后 /pace-sync setup。"

用户选择"现在配置"→ 执行 `/pace-sync setup`。
用户选择"稍后再说"→ 跳过。

### 提前退出

用户在任何阶段可说"够了"→ 跳过剩余阶段，使用已收集的信息完成初始化。

## §3 发布配置收集

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
