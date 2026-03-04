# 场景 S01-v2: pace-init 生命周期测试（v2）

**对应需求**: S1, F1.1
**验证目标**: 生命周期检测、CLAUDE.md 合并（Edit 工具）、幂等性、迁移、verify、dry-run
**前置条件**: 运行 `bash tests/integration/setup-init-test-envs.sh` 创建测试环境

> 本文件是 S01-init.md 的增强版，覆盖 Edit 工具修复后的验证和更多边界场景。

## 测试环境

| 环境 | 路径 | 用途 |
|------|------|------|
| ENV-A | `/tmp/devpace-test-envs/ENV-A` | 空 git 仓库（阶段 A） |
| ENV-B | `/tmp/devpace-test-envs/ENV-B` | Node.js 项目（阶段 B） |
| ENV-C | `/tmp/devpace-test-envs/ENV-C` | 成熟项目（阶段 C） |
| ENV-D | `/tmp/devpace-test-envs/ENV-D` | 已有 CLAUDE.md（合并测试） |
| ENV-E | `/tmp/devpace-test-envs/ENV-E` | 已有 .devpace/（幂等性 + verify） |
| ENV-F | `/tmp/devpace-test-envs/ENV-F` | state.md v1.5.0（迁移测试） |
| ENV-G | `/tmp/devpace-test-envs/ENV-G` | Monorepo pnpm workspace（monorepo 检测） |
| ENV-H | `/tmp/devpace-test-envs/ENV-H` | Python 项目 + PRD + OpenAPI（--from 测试） |
| ENV-I | `/tmp/devpace-test-envs/ENV-I` | 含 insights + sync-mapping（--reset 测试） |
| ENV-J | `/tmp/devpace-test-envs/ENV-J` | 非 git 项目（回退测试） |
| ENV-K | `/tmp/devpace-test-envs/ENV-K` | Go 项目（工具链检测） |

## T1: 阶段 A 最小初始化

**环境**: ENV-A
**执行**: `cd /tmp/devpace-test-envs/ENV-A && /pace-init`

### 执行步骤

| # | 动作 | 期望行为 |
|---|------|---------|
| 1 | `/pace-init` | 检测到新项目（≤5 commits），采用极简初始化 |
| 2 | 观察输出 | 自动检测项目名（目录名），最多询问 1-2 项缺失信息 |
| 3 | 提供缺失信息 | 生成 .devpace/ 目录 |

### 验收标准

- [ ] 检测为阶段 A，输出包含"新项目"相关描述
- [ ] `.devpace/state.md` 存在，内容行数 ~6 行（±2）
- [ ] `.devpace/project.md` 存在，含项目名
- [ ] `.devpace/backlog/` 目录存在
- [ ] `.devpace/rules/workflow.md` 存在
- [ ] `.devpace/rules/checks.md` 存在，至少 2 条检查项
- [ ] `CLAUDE.md` 包含 `<!-- devpace-start -->` 和 `<!-- devpace-end -->` 标记
- [ ] `state.md` 包含 `devpace-version` 标记
- [ ] 所有 `{{PLACEHOLDER}}` 已替换

## T2: 阶段 B 开发中项目初始化

**环境**: ENV-B
**执行**: `cd /tmp/devpace-test-envs/ENV-B && /pace-init`

### 执行步骤

| # | 动作 | 期望行为 |
|---|------|---------|
| 1 | `/pace-init` | 检测到开发中项目（>5 commits, 2 未合并分支） |
| 2 | 观察输出 | 自动检测项目名（package.json），识别在研工作 |
| 3 | 确认在研工作 | 生成 .devpace/ 目录，含 PF 候选 |

### 验收标准

- [ ] 检测为阶段 B，提及 commit 数和活跃分支
- [ ] `state.md` 内容行数 ~10 行（±2）
- [ ] `project.md` 价值功能树预填充 PF 候选（从 src/ 子目录推断）
- [ ] 在研工作识别列出 feature/notifications 和 feature/search
- [ ] `context.md` 存在，包含 Git 策略检测结果
- [ ] `.eslintrc.json` 检测到，checks.md 含 lint 相关检查

## T3: 阶段 C 已发布项目初始化

**环境**: ENV-C
**执行**: `cd /tmp/devpace-test-envs/ENV-C && /pace-init`

### 执行步骤

| # | 动作 | 期望行为 |
|---|------|---------|
| 1 | `/pace-init` | 检测到已发布项目（有版本 tags, CHANGELOG, 部署配置） |
| 2 | 观察输出 | 自动配置版本管理，推荐 pace-sync |
| 3 | 拒绝 pace-sync（测试跳过） | 完成初始化 |

### 验收标准

- [ ] 检测为阶段 C，提及版本标签
- [ ] `state.md` 内容行数 ~13 行（±2）
- [ ] `integrations/config.md` 存在，含版本管理 section（tag 格式 `vX.Y.Z`）
- [ ] `metrics/dashboard.md` 存在，含 DORA 基线数据
- [ ] CHANGELOG 功能条目作为 BR/PF 种子展示
- [ ] pace-sync 推荐提议出现（措辞为"推荐"而非"可选"）
- [ ] fly.toml 被识别为部署配置

## T4: dry-run 预览

**环境**: ENV-A（重新创建或使用 T1 之前的状态）
**执行**: `/pace-init --dry-run`

### 验收标准

- [ ] 输出预览信息，显示将要生成的文件列表
- [ ] **不创建**任何文件（.devpace/ 不存在）
- [ ] 预览内容包含 state.md、project.md 等文件名
- [ ] 预览结束后提示用户可执行正式初始化

## T5: verify 健康检查

**环境**: ENV-E
**执行**: `/pace-init --verify`

### 验收标准

- [ ] 输出健康检查报告
- [ ] 检查 state.md 版本标记存在
- [ ] 检查 project.md 结构完整
- [ ] 检查 CLAUDE.md devpace 标记存在
- [ ] 报告显示"健康"或列出具体问题
- [ ] 不修改任何文件（除非 --fix）

## T6: CLAUDE.md 智能合并（Edit 工具验证）

**环境**: ENV-D
**执行**: `cd /tmp/devpace-test-envs/ENV-D && /pace-init`

> **重点验证**：此测试验证 Edit 工具修复后的 CLAUDE.md 合并功能。

### 执行步骤

| # | 动作 | 期望行为 |
|---|------|---------|
| 1 | `/pace-init` | 检测到已有 CLAUDE.md（无 devpace 标记） |
| 2 | 观察 CLAUDE.md 处理 | 在末尾追加 devpace section，保留原有内容 |

### 验收标准

- [ ] 原有 CLAUDE.md 内容完整保留（"Build Commands"、"Architecture"、"Custom Rules" 章节不变）
- [ ] 文件末尾追加了 `<!-- devpace-start -->` ... `<!-- devpace-end -->` 区间
- [ ] devpace section 内容正确（项目名、研发协作引导）
- [ ] 无内容重复或格式破坏

### 验证 Edit 工具使用

观察 Claude 的工具调用日志，确认：
- [ ] 对已有 CLAUDE.md 使用了 **Edit** 工具（非 Write 覆盖）
- [ ] 或使用 Write 但保留了原有内容（也可接受，但 Edit 更安全）

## T7: 幂等性测试

**环境**: ENV-E
**执行**: `cd /tmp/devpace-test-envs/ENV-E && /pace-init`

### 执行步骤

| # | 动作 | 期望行为 |
|---|------|---------|
| 1 | 记录 .devpace/ 文件的 MD5 | 作为基线 |
| 2 | `/pace-init` | 检测到已存在 .devpace/，执行更新 |
| 3 | 再次检查 MD5 | 核心文件内容不变或仅 devpace section 更新 |

### 验收标准

- [ ] `state.md` 内容不被破坏（已有工作项保留）
- [ ] `project.md` 已有内容保留
- [ ] CLAUDE.md 标记区间外内容不变（"My Custom Section" 保留）
- [ ] CLAUDE.md 标记区间内内容可更新（设计如此）
- [ ] 不创建重复文件

## T8: 版本迁移

**环境**: ENV-F
**执行**: `cd /tmp/devpace-test-envs/ENV-F && /pace-init`

### 验收标准

- [ ] 检测到 v1.5.0，触发迁移逻辑
- [ ] state.md 版本标记更新到当前版本
- [ ] 已有数据保留（CR-001 工作项不丢失）
- [ ] 迁移过程有输出说明（而非静默处理）

## T9: --reset 完整重置

**环境**: ENV-I
**执行**: `cd /tmp/devpace-test-envs/ENV-I && /pace-init --reset`

### 执行步骤

| # | 动作 | 期望行为 |
|---|------|---------|
| 1 | `/pace-init --reset` | 检测到外部同步映射，提示关联 Issues 需手动处理 |
| 2 | 观察确认提示 | 二次确认，显示将删除 2 个 CR + 迭代记录 |
| 3 | 确认删除 | 删除 .devpace/，清理 CLAUDE.md devpace section |

### 验收标准

- [ ] 提示"发现外部同步映射"（检测到 sync-mapping.md）
- [ ] 二次确认，显示 CR 和数据量统计
- [ ] `.devpace/` 目录完全删除
- [ ] CLAUDE.md 中 `<!-- devpace-start -->` 到 `<!-- devpace-end -->` 区间及标记已移除
- [ ] CLAUDE.md 中其他内容保留（如标题行）
- [ ] insights.md 未保留（未使用 --keep-insights）

## T10: --reset --keep-insights

**环境**: ENV-I（重新创建）
**执行**: `cd /tmp/devpace-test-envs/ENV-I && /pace-init --reset --keep-insights`

### 验收标准

- [ ] `.devpace/` 目录删除
- [ ] `.devpace/metrics/insights.md` 恢复到新创建的 metrics/ 目录
- [ ] insights.md 内容完整（2 条 pattern）
- [ ] 提示"可运行 /pace-init 重新初始化"

## T11: --from 文档驱动初始化

**环境**: ENV-H
**执行**: `cd /tmp/devpace-test-envs/ENV-H && /pace-init py-api-service --from docs/prd.md`

### 执行步骤

| # | 动作 | 期望行为 |
|---|------|---------|
| 1 | `/pace-init py-api-service --from docs/prd.md` | 解析 PRD 文档提取用户故事和功能 |
| 2 | 观察解析结果 | 展示结构化摘要（BR + PF 候选）|
| 3 | 确认或调整 | 确认后写入 project.md |

### 验收标准

- [ ] 从用户故事提取 3 个 BR 候选（认证、用户资料、搜索）
- [ ] 优先级标记（P0/P1/P2）被识别并映射
- [ ] 非功能需求提取到 project.md "项目原则"
- [ ] 展示确认界面让用户调整
- [ ] project.md 价值功能树包含确认后的 PF 结构
- [ ] 同时完成标准初始化（state.md、checks.md 等存在）

## T12: --from OpenAPI 规格

**环境**: ENV-H
**执行**: `cd /tmp/devpace-test-envs/ENV-H && /pace-init py-api-service --from docs/api-spec.yaml`

### 验收标准

- [ ] 识别 OpenAPI 格式
- [ ] 按 tags 分组提取 PF（Users、Auth、Products）
- [ ] paths 作为 PF 的子条目或细节
- [ ] 展示确认界面

## T13: Monorepo 检测

**环境**: ENV-G
**执行**: `cd /tmp/devpace-test-envs/ENV-G && /pace-init`

### 验收标准

- [ ] 检测到 `pnpm-workspace.yaml`，触发 monorepo 增强初始化
- [ ] AskUserQuestion 询问组织方式（A 或 B）
- [ ] 选 A 后：根 .devpace/ 包含所有子包信息
- [ ] context.md 记录 monorepo 结构（3 个子包）
- [ ] 阶段检测为 B（8+ commits）

## T14: 非 git 项目

**环境**: ENV-J
**执行**: `cd /tmp/devpace-test-envs/ENV-J && /pace-init`

### 验收标准

- [ ] 默认为阶段 A（无 .git/）
- [ ] 不执行 git 相关检测（无报错）
- [ ] 从 package.json 读取项目名
- [ ] 正常生成 .devpace/ 目录
- [ ] .gitignore 建议不出现（无 git）

## T15: Go 项目工具链检测

**环境**: ENV-K
**执行**: `cd /tmp/devpace-test-envs/ENV-K && /pace-init`

### 验收标准

- [ ] 从 go.mod 检测语言和 module 名
- [ ] checks.md 包含 `go test ./...`
- [ ] checks.md 包含 `golangci-lint run`（检测到 .golangci.yml）
- [ ] context.md 包含 Go 技术栈信息
- [ ] 阶段检测为 B

## T16: full 模式分阶段引导

**环境**: ENV-B
**执行**: `cd /tmp/devpace-test-envs/ENV-B && /pace-init test-webapp full`

### 执行步骤

| # | 动作 | 期望行为 |
|---|------|---------|
| 1 | `/pace-init test-webapp full` | 完成环境探测 + 阶段 1（基础） |
| 2 | 阶段 2 询问 | AskUserQuestion 是否定义业务目标 |
| 3 | 选"稍后再说" | 跳过阶段 2 |
| 4 | 阶段 3 询问 | AskUserQuestion 是否配置发布流程 |
| 5 | 选"稍后再说" | 跳过阶段 3，完成初始化 |

### 验收标准

- [ ] 环境探测输出摘要（技术栈、CI/CD 等）
- [ ] 阶段 2/3/4 均为可选，可跳过
- [ ] 跳过不影响基础初始化完整性
- [ ] project.md 在跳过后保持桩状态
- [ ] "够了" 可提前退出剩余阶段

## T17: --dry-run + full 组合

**环境**: ENV-B（重新创建或无 .devpace/ 状态）
**执行**: `/pace-init test-webapp --dry-run`

### 验收标准

- [ ] 输出预览信息，不写入文件
- [ ] 预览中包含生命周期阶段检测结果
- [ ] 预览中包含工具链检测结果（jest、eslint）
- [ ] 预览中列出条件创建项（context.md 因检测到约定，标注"将创建"）
- [ ] .devpace/ 不存在

## T18: --export-template / --from-template

**环境**: ENV-E（已有 .devpace/）
**执行**: `/pace-init --export-template` → 查看输出 → 在 ENV-A 使用 `/pace-init --from-template`

### 验收标准

- [ ] --export-template 生成 .devpace-template/ 目录
- [ ] 模板中移除了项目特定路径和名称
- [ ] 保留了工作流规则和检查项结构
- [ ] --from-template 在新项目中应用模板成功
- [ ] 应用后继续正常流程（替换占位符、生成 state.md）

## T19: --import-insights 跨项目经验导入

**环境**: 先在 ENV-I 执行 `--export-template`，然后在 ENV-H 导入
**执行**: `cd /tmp/devpace-test-envs/ENV-H && /pace-init py-api-service --import-insights /tmp/devpace-test-envs/ENV-I/.devpace/metrics/insights.md`

### 验收标准

- [ ] 读取 insights.md 内容
- [ ] 置信度降级 ×0.8（0.85 → 0.68，0.72 → 0.576）
- [ ] 验证次数重置为 0
- [ ] 跳过偏好类型条目（如有）
- [ ] 输出导入摘要
- [ ] `.devpace/metrics/insights.md` 存在且包含导入数据

## T20: --interactive 强制对话模式

**环境**: ENV-B
**执行**: `cd /tmp/devpace-test-envs/ENV-B && /pace-init test-webapp --interactive`

### 验收标准

- [ ] 覆盖阶段 B 的零提问行为，逐项确认
- [ ] 每个自动推断的信息（项目名、技术栈、Git 策略）都请求用户确认
- [ ] 用户可修改自动推断结果
- [ ] 最终生成结果反映用户修改

## 评分维度

| 维度 | Pass | Partial | Fail |
|------|------|---------|------|
| 生命周期检测 | 3 个阶段均正确识别 | 1 个阶段误判 | 多个阶段误判 |
| CLAUDE.md 合并 | 完美合并，使用 Edit | 合并成功但用 Write 覆盖 | 内容丢失或格式破坏 |
| 幂等性 | 重复 init 无副作用 | 小范围内容变化 | 数据丢失 |
| 版本迁移 | 无损升级 | 升级成功但有警告 | 数据丢失 |
| dry-run | 零副作用 | 创建了临时文件 | 写入了正式文件 |
| verify | 完整报告 | 报告不全 | 报告错误 |
| 模板替换 | 无残留占位符 | 1-2 处残留 | 大量残留 |
| Hook 守卫 | 阻止越界写入 | 未测试 | 允许越界写入 |
| --reset | 完整清理 + 外部关联提示 | 清理成功但无提示 | 数据残留或误删 |
| --from | 正确解析 + 用户确认 | 部分解析 | 无法解析 |
| monorepo | 检测 + 组织方式选择 | 检测但无选择 | 未检测到 |
| 工具链检测 | 覆盖 4 个生态系统 | 覆盖 2-3 个 | 未检测或误检 |
| full 模式 | 分阶段引导 + 可跳过 | 引导但不可跳过 | 无分阶段 |
| 模板导出/导入 | 往返完整 | 部分成功 | 失败 |
| 经验导入 | 置信度降级 + 去重 | 导入但无降级 | 导入失败 |
