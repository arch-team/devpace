# devpace 技术架构可行性与演进评估

> 基于 v1.4.0 代码和设计文档的完整技术分析。

## 1. 执行摘要

devpace 在 Claude Code Plugin 系统约束下构建了一套完整的 BizDevOps 研发管理引擎。其纯 Markdown 存储 + Skill 编排 + Hook 门禁的架构选择与 LLM 驱动的运行时高度契合——LLM 天然擅长处理非结构化文本，Markdown 作为状态存储既对 LLM 友好也对人类可读。当前架构的核心优势在于**零运行时依赖**（无数据库、无后端服务、纯文件系统）和**概念模型完整性**（BR→PF→CR 价值链从初始化起就完整存在）。

主要限制来自 Claude Code Plugin 系统的固有约束：无持久化进程（每次会话独立）、无跨会话自动触发（依赖 Hook 的会话内事件）、Skill 无法嵌套调用其他 Skill。v2.x 规划的 Ops 执行层集成（CLI 部署/回滚）技术上完全可行，监控集成可行但受限于"无持久进程"（只能查询不能订阅），跨项目知识共享需要突破 Plugin 的单项目作用域。核心技术债务集中在 13 个 Schema 文件的冗余度和 17 个 Skill 间的隐式耦合。

## 2. 当前架构评估

### 2.1 架构概览

devpace 的运行时架构由五层组成：

```
+-----------------------------------------------------------+
| Rule Layer: devpace-rules.md (SS0-SS15, 自动注入会话)       |
+-----------------------------------------------------------+
| Skill Layer: 17 Skills (13 user + 2 system + SKILL.md)    |
+-----------------------------------------------------------+
| Agent Layer: 3 Agents (engineer, pm, analyst)              |
+-----------------------------------------------------------+
| Hook Layer: 8 Hook scripts (Shell + Node.js)               |
+-----------------------------------------------------------+
| Data Layer: .devpace/ (Markdown files + Git)               |
+-----------------------------------------------------------+
```

### 2.2 优势分析

**A. 纯 Markdown 存储（零运行时依赖）**

- LLM 作为"解析器"：无需 YAML/JSON 解析库，Claude 直接读写 Markdown，容错性极高
- 人类可读性：开发者可直接在 IDE 或 GitHub 中查看和编辑所有状态文件
- Git 友好：行级 diff 清晰，变更历史完整，支持 `git blame` 审计
- 可移植性：无服务端依赖，Plugin 卸载后 `.devpace/` 数据仍有独立价值
- 渐进丰富：文件结构不变、内容自然增长的设计避免了 schema migration 问题

**B. 概念模型驱动的 Skill 编排**

- 17 个 Skill 严格映射到 BizDevOps 工作流的 Phase 0-5
- `context: fork` + `agent` 字段实现了 Skill->Agent 路由，提供了近似物理隔离的效果
- Skill 分拆模式（SKILL.md + *-procedures.md）有效控制了 LLM 上下文消耗
- 子命令机制（如 /pace-release 的 12 个子命令）在单个 Skill 内实现了复杂功能集

**C. 多层次质量门禁**

- Hook 层（机制级）：`pre-tool-use.mjs` 通过 exit 2 硬阻断探索模式写入和 Gate 3 绕过
- Skill 层（prompt 级）：`pace-dev` 的 Skill-scoped Hook 用 prompt 类型验证 Write/Edit 操作
- Rule 层（行为级）：`devpace-rules.md` 通过指令约束 Claude 的行为模式
- 三层防护形成了纵深防御，单层失效不会导致核心铁律被破坏

**D. 渐进降级设计**

- 每个 Skill 都有降级路径：无 `.devpace/` -> 即时分析不写文件
- 可选功能（Release、Feedback、Integration）通过目录存在性判断条件生效
- 自主级别（辅助/标准/自主）允许用户按信任程度调整 Claude 的操作边界

### 2.3 限制与风险

**A. LLM 规则遵循的可靠性（中风险）**

Rule 层依赖 Claude 对 `devpace-rules.md` 指令的遵循。长会话、复杂上下文或 prompt injection 场景下，规则遵循可能退化。当前缓解措施：
- Hook 层硬阻断弥补了最关键的铁律（探索模式保护、Gate 3）
- `pre-tool-use.mjs` 的 Node.js 实现不依赖 LLM 判断，是确定性的

未覆盖的风险点：
- Skill 内容中的行为规则（如"必须等用户确认"）完全依赖 LLM 遵循
- 复杂度自适应路径（S/M/L/XL 判断）是 LLM 主观判断，无机制级校验

**B. 无持久化进程（高影响）**

Claude Code Plugin 每次会话独立启动，没有后台守护进程。这意味着：
- 无法实现"定时提醒"（如迭代截止日提醒）——只能在会话内通过 pace-pulse 检测
- 无法订阅外部事件（如 CI 完成通知、webhook 回调）——只能主动查询
- 会话间状态传递完全依赖文件系统（`.devpace/` + Git）

**C. 单项目作用域（v2.x 阻碍）**

Plugin 在单个项目目录中运行，跨项目操作受限：
- 全局经验共享（OBJ-16）需要在 Plugin 作用域外操作文件
- 多项目并行的上下文切换无原生支持

**D. 上下文窗口压力**

17 个 Skill + 1 个核心 Rules 文件 + 13 个 Schema，合计文本量大：
- `devpace-rules.md` 单文件约 800+ 行，每次会话自动注入
- Skill 分拆模式（SKILL.md + procedures）缓解了部分压力，但 LLM 仍需在会话中持有大量规则上下文
- Agent memory（project 级）可在跨会话间持久化部分上下文，但非结构化

**E. Markdown "Schema" 的松散性（中风险）**

13 个 `_schema/*.md` 文件定义了格式契约，但 Markdown 不是强类型 Schema：
- 无运行时验证——Claude 写出不合规的 CR 文件时，只能靠后续 Skill 读取时发现
- 格式演进需要手动维护向后兼容（version 标记机制部分缓解）
- 自动化测试（`tests/static/`）覆盖了结构层面，但语义一致性仍依赖 LLM

### 2.4 耦合度分析

**Skill 间的耦合关系**：

| 耦合类型 | 关系 | 评估 |
|---------|------|------|
| 数据耦合 | 所有 Skill 共享 `.devpace/` 目录下的文件 | 可接受——文件即接口 |
| 规则耦合 | 所有 Skill 共享 `devpace-rules.md` | 紧耦合——单文件变更影响全局行为 |
| 流程耦合 | pace-dev -> pace-review -> pace-learn 形成固定管道 | 设计意图，可接受 |
| 隐式耦合 | pace-pulse 依赖 pace-guard、pace-retro 依赖 pace-guard trends | 需要文档化 |
| Schema 耦合 | 多个 Skill 读写同一 CR 文件的不同 section | 中等风险——section 拼写变更影响多个 Skill |

**模块化程度评分**：7/10。Skill 边界清晰，但共享状态文件和单体 Rules 文件造成了实质耦合。

## 3. v2.x 扩展方向可行性矩阵

### 3.1 Ops 执行层集成

| 维度 | 评估 |
|------|------|
| **技术可行性** | **高** |
| **Plugin 系统支持** | 完全支持——Bash 工具可执行任意 CLI 命令 |
| **实现路径** | 通过 /pace-release 的 deploy 子命令调用 `kubectl`、`aws` CLI 等 |
| **已有基础** | Gate 4 已支持 `gh run list` 查询 CI 状态；integrations/config.md 已定义环境配置 |
| **限制** | 需要目标环境的 CLI 工具已安装且已认证；长时间部署操作可能超时 |
| **风险** | 生产环境操作的安全性——需要严格的确认门禁（当前 Gate 4 已有人类确认机制） |

**详细分析**：Claude Code 的 Bash 工具可执行任意 shell 命令。通过 `integrations/config.md` 配置部署命令（如 `kubectl apply -f deploy.yaml`、`aws ecs update-service`），/pace-release 可编排完整的部署流程。关键约束是：
1. 部署命令必须是非交互式的（Claude Code 的 Bash 不支持交互式输入）
2. 长时间运行的命令需设置合理 timeout
3. 生产操作必须通过人类确认门禁（与 Gate 3 同级的铁律）

### 3.2 监控集成

| 维度 | 评估 |
|------|------|
| **技术可行性** | **中** |
| **Plugin 系统支持** | 部分支持——可以查询，不能订阅 |
| **实现路径** | 通过 Bash 调用监控平台 CLI/API（如 `datadog-ci`、`gcloud monitoring`） |
| **可做** | 健康检查执行（`curl` 端点）、查询最近告警、指标快照 |
| **不可做** | 实时告警订阅、webhook 回调处理、持续监控守护进程 |
| **替代方案** | 会话开始时主动查询 + pace-pulse 检测异常信号 |

**详细分析**：无持久化进程是核心约束。devpace 只能在会话活跃期间进行"点查询"模式的监控：
- **可行**：`/pace-feedback` 会话中执行 `curl` 健康检查、通过 CLI 查询 Datadog/CloudWatch 最近 N 分钟告警
- **不可行**：持续监听告警流、webhook 回调、实时仪表盘更新
- **MCP Server 扩展**：通过 `.mcp.json` 配置外部 MCP Server 可能突破此限制——如果未来有 Datadog/PagerDuty 的 MCP Server，devpace 可通过 MCP 协议订阅事件

### 3.3 跨项目知识共享

| 维度 | 评估 |
|------|------|
| **技术可行性** | **中低** |
| **Plugin 系统支持** | 受限——Plugin 作用于单项目目录 |
| **当前基础** | v1.3.0 已实现 `--import-insights` 导入经验（/pace-init 参数）|
| **已有机制** | Agent memory（project 级）提供跨会话记忆；experience-reference.md 提供经验模板 |
| **阻碍** | Plugin 运行时无法直接访问其他项目目录中的 `.devpace/` |
| **替代方案** | 导出/导入模式——项目 A 导出经验文件 -> 人工/脚本拷贝 -> 项目 B 导入 |

**详细分析**：
- **短期方案（v2.0，已具雏形）**：`/pace-init --import-insights <path>` 已支持从文件导入经验。用户手动拷贝 `metrics/insights.md` 到新项目即可。简单但有效
- **中期方案（v2.x）**：全局经验库（`~/.devpace/global-insights.md`），Skill 运行时先查项目级 insights 再查全局级。技术上需要 Hook 在会话结束时自动同步高置信度经验到全局目录
- **长期方案（v3.0+）**：MCP Server 封装全局知识库，所有 devpace 项目通过 MCP 协议查询共享经验。需要开发独立的 MCP Server

### 3.4 AI 自主性增强

| 维度 | 评估 |
|------|------|
| **技术可行性** | **高** |
| **Plugin 系统支持** | 完全支持——通过 Rules + Hooks + Agent Memory |
| **当前基础** | 三级自主性（辅助/标准/自主）已实现；Agent memory 提供跨会话学习 |
| **增强方向** | 自动升级自主级别、更精准的复杂度判断、基于历史的自适应行为 |
| **约束** | Gate 3 铁律不可放松——最高自主级别下人类审批仍为阻塞门禁 |

**详细分析**：Plugin 系统对 AI 自主性增强的支持非常好：
1. **自适应自主级别**：基于连续 N 个 CR 的 Gate 3 通过率，自动建议升级自主级别（当前需用户手动修改 project.md）
2. **基于历史的预测**：Agent memory + insights.md 提供历史数据，Claude 可据此预测 CR 复杂度和风险
3. **更智能的 pace-pulse**：利用历史 pattern 预测"即将出问题"而非"已经出问题"
4. **约束**：所有增强都在 Gate 3 铁律框架内——Claude 可以更自主地推进技术闭环，但产品/业务决策点的人类审批不可绕过

### 3.5 可行性总览矩阵

| 扩展方向 | 技术可行性 | Plugin 支持 | 已有基础 | 实现难度 | 建议优先级 |
|---------|-----------|------------|---------|---------|-----------|
| Ops 执行层集成 | **高** | 完全 | Gate 4 + config.md | 低 | P0 |
| AI 自主性增强 | **高** | 完全 | 三级自主 + Agent memory | 中 | P1 |
| 监控集成（查询模式） | **中** | 部分 | /pace-feedback | 中 | P1 |
| 跨项目经验导入 | **中低** | 受限 | --import-insights | 中 | P2 |
| 监控集成（实时订阅） | **低** | 不支持 | 无 | 高 | P3（需 MCP） |
| 全局知识库 MCP | **中** | 需开发 | 无 | 高 | P3 |

## 4. Plugin 能力边界分析

### 4.1 Claude Code Plugin 系统能力边界

| 能力 | 支持程度 | 说明 |
|------|---------|------|
| **文件读写** | 完全支持 | Read/Write/Edit/Glob/Grep 工具 |
| **Shell 命令** | 完全支持 | Bash 工具，支持 timeout |
| **事件 Hook** | 完全支持 | 8 种事件，支持 command/prompt/agent 三种类型 |
| **子 Agent** | 完全支持 | context:fork + agent 路由，maxTurns 限制 |
| **Agent Memory** | 完全支持 | user/project/local 三级持久化 |
| **Skill 级 Hook** | 完全支持 | SKILL.md frontmatter 中定义 |
| **MCP Server** | 完全支持 | .mcp.json 配置，Plugin 可内联定义 |
| **输出样式** | 支持 | outputStyles 字段，自定义输出格式 |
| **Settings** | 支持 | settings.json 定义 Plugin 默认配置 |
| **持久进程** | 不支持 | 无后台服务，每次会话独立 |
| **跨项目操作** | 不支持 | Plugin 运行在单项目目录 |
| **Skill 嵌套调用** | 不支持 | Skill 不能调用其他 Skill；子 Agent 不能嵌套调用 Task |
| **实时通知** | 不支持 | 无 push 机制，只能在会话内响应 |
| **UI 定制** | 不支持 | 无自定义 UI 组件能力 |
| **网络监听** | 不支持 | 无 webhook/socket 监听能力 |

### 4.2 能力天花板与绕过策略

**天花板 1：无持久进程**
- 影响：无法订阅外部事件、无定时任务、无后台监控
- 绕过策略：
  - SessionStart Hook 执行"晨检"（查询外部状态、检测变更）
  - MCP Server 提供持久进程——独立部署的 MCP Server 可维持连接并缓存状态
  - 外部 cron job 修改 `.devpace/` 文件，下次会话时 Claude 自动感知

**天花板 2：Skill 不能嵌套调用**
- 影响：pace-dev 不能直接调用 pace-guard scan，只能通过 Rules 引导 Claude 执行等效行为
- 绕过策略：
  - 当前方案：procedures.md 中描述"此时执行等同于 /pace-guard scan 的行为"
  - 替代方案：将共享逻辑抽取到 knowledge/ 文件中，多个 Skill 引用同一规程
  - 未来可能：Claude Code 可能支持 Skill composition 或 Skill 间消息传递

**天花板 3：单项目作用域**
- 影响：跨项目经验共享、多项目仪表盘
- 绕过策略：
  - 导出/导入文件（当前已有 `--import-insights`）
  - 全局 MCP Server 作为跨项目中介
  - 用户级 Plugin 配置（`~/.claude/` 下的全局设置）

**天花板 4：上下文窗口有限**
- 影响：大型项目的 state.md + rules + 活跃 CR 可能占用大量上下文
- 绕过策略：
  - 信息分层（L1/L2/L3）减少默认加载量——当前已实现
  - Skill 分拆模式（SKILL.md + procedures）按需加载规程
  - PreCompact Hook 在上下文压缩前提醒保存状态
  - Agent Memory 持久化高频访问的上下文片段

## 5. 技术债务清单

按优先级排序（高->低）：

### P0：高优先级（影响扩展性）

**TD-1：单体 Rules 文件**
- 描述：`devpace-rules.md` 单文件 800+ 行，覆盖 SS0-SS15 所有规则，每次会话全量注入
- 影响：上下文消耗大；修改一个 SS 需要测试全局影响；难以按功能模块独立演进
- 建议：按领域拆分为多个 Rules 文件——核心规则（SS1-SS3）始终加载，扩展规则（SS14 Release、SS15 教学等）条件加载
- 约束：Claude Code Plugin 的 rules/ 目录下所有 `.md` 文件自动加载，需要利用此机制或通过条件化内容实现

**TD-2：Skill 间隐式耦合**
- 描述：pace-pulse 依赖 pace-guard 的第 8 信号、pace-retro 依赖 pace-guard trends 的数据，但这些依赖关系只在 procedures 文件中以文本描述
- 影响：修改 pace-guard 的数据格式可能静默破坏 pace-pulse 和 pace-retro
- 建议：在 design.md 附录 B 组件依赖图中补充 Skill 间数据依赖；在 Schema 中定义共享数据格式

**TD-3：Schema 冗余度**
- 描述：13 个 Schema 文件中部分字段定义重复（如 state-format.md、cr-format.md、project-format.md 中的状态值定义）
- 影响：更新状态值（如新增 `released`）需要同步修改多个 Schema
- 建议：抽取共享定义（状态值、复杂度枚举、关联类型）到单独的 `_schema/common.md`，其他 Schema 引用

### P1：中优先级（影响维护性）

**TD-4：Hook 脚本缺乏统一测试**
- 描述：8 个 Hook 脚本（5 个 Node.js + 3 个 Shell）缺少系统化的单元测试
- 影响：Hook 行为变更难以验证；`lib/utils.mjs` 的共享工具函数修改可能影响多个 Hook
- 建议：为 `lib/utils.mjs` 添加单元测试；为关键 Hook（pre-tool-use.mjs、intent-detect.mjs）添加集成测试

**TD-5：procedures 文件分散**
- 描述：详细规程分散在各 Skill 目录的 `*-procedures.md` 中，部分 Skill 有 4+ 个 procedures 文件（如 pace-test 有 7 个）
- 影响：相关规程之间的交叉引用增加认知负担；新开发者需要在多个文件间跳转理解完整流程
- 建议：为复杂 Skill（pace-test、pace-release）生成 procedures 索引文件

**TD-6：教学标记的扩展性**
- 描述：`state.md` 的 `taught` HTML 注释中维护已教学行为的逗号分隔列表
- 影响：随着教学项增多，这个单行标记的可维护性下降
- 建议：短期可接受；长期考虑迁移到独立的 `.devpace/teaching-state.md`

### P2：低优先级（优化空间）

**TD-7：version 标记的手动维护**
- 描述：state-format.md 中的 `devpace-version` 合法值列表随版本递增手动维护
- 建议：自动化版本兼容性检测，或简化为 semver range 匹配

**TD-8：Agent 定义的同质性**
- 描述：3 个 Agent（engineer、pm、analyst）结构高度相似，主要差异在 tools 和视角描述
- 建议：评估是否需要 3 个独立 Agent，或通过 Skill 级 prompt 参数化实现角色差异

## 6. 架构演进建议

### 6.1 短期（v2.0）：强化核心，降低债务

**目标**：在不改变整体架构的前提下提升可维护性和扩展性。

| 项目 | 描述 | 预期收益 |
|------|------|---------|
| Rules 模块化 | 将 devpace-rules.md 按 SS0-SS3（核心）、SS4-SS9（推进+变更）、SS10-SS12（节奏）、SS13-SS15（扩展）拆分为 4 个文件 | 减少单次上下文消耗 30%+；支持条件加载 |
| Schema 共享定义 | 抽取 `_schema/common.md`（状态枚举、复杂度、关联类型） | 消除 Schema 间冗余，降低同步成本 |
| Hook 测试框架 | 为 `lib/utils.mjs` 和关键 Hook 建立测试套件 | 提升 Hook 变更的安全性 |
| Skill 依赖文档化 | 在组件依赖图中补充 Skill 间数据格式依赖 | 减少隐式破坏风险 |
| Ops 执行层 MVP | /pace-release deploy 子命令支持执行 config.md 中配置的部署命令 | 补齐"merged->deployed"的自动化缺口 |

### 6.2 中期（v2.x）：扩展边界，深化智能

**目标**：突破 Plugin 系统的部分限制，增强自主性和跨项目能力。

| 项目 | 描述 | 技术路径 |
|------|------|---------|
| 全局经验库 | `~/.devpace/global-insights.md`，Skill 运行时双层查询 | SessionStart Hook 加载全局 insights；pace-learn 高置信度条目自动同步 |
| 监控查询集成 | /pace-feedback 支持通过 CLI 查询监控指标 | `integrations/config.md` 新增"监控"段，配置查询命令 |
| 自适应自主级别 | 基于 Gate 3 历史通过率自动建议升级 | Agent memory 积累通过率数据；/pace-retro 输出升级建议 |
| MCP 桥接 | 为常用集成（GitHub、CI/CD）开发 MCP Server 适配层 | .mcp.json 配置外部 MCP Server；Skill 通过 MCP 工具调用 |
| 智能 pace-pulse | 基于历史 pattern 的预测性风险检测 | insights.md defense 条目 + Agent memory 历史数据 |

### 6.3 长期（v3.0+）：平台化与生态

**目标**：从单项目 Plugin 演进为平台级研发管理引擎。

| 方向 | 描述 | 前提条件 |
|------|------|---------|
| devpace MCP Server | 将 devpace 核心逻辑封装为 MCP Server，支持跨项目查询、全局仪表盘 | Claude Code MCP 协议稳定；有独立部署 MCP Server 的基础设施 |
| 团队协作 | 多开发者 + 多 Claude 实例共享 `.devpace/`，Git 冲突自动合并 | Agent Team 功能成熟；`.devpace/` 文件级锁或 CRDT 机制 |
| 自定义 Skill 市场 | 用户开发和分享领域特定的 Skill（如 /pace-security、/pace-a11y） | Plugin 生态成熟；Skill composition 机制可用 |
| 实时集成层 | 独立 MCP Server 维持与 CI/CD、监控平台的持久连接 | MCP Server 可独立部署和运行 |

### 6.4 架构演进路径图

```
v1.4 (当前)          v2.0                  v2.x                  v3.0+
---------------------------------------------------------------------------
Rules 单体          -> Rules 模块化          -> Rules 按需加载        -> Skill composition
Schema 冗余         -> Schema 共享定义       -> Schema 自动验证       -> 强类型 Schema
单项目              -> 导入/导出             -> 全局经验库            -> MCP 跨项目
CLI 查询            -> CLI 部署执行          -> MCP 桥接集成          -> 实时集成层
3 级自主            -> 自适应自主建议         -> 自主级别自动管理       -> 团队级自主
Hook 脚本           -> Hook 测试框架         -> Hook 动态注册         -> 声明式 Hook
```

## 7. 风险与缓解

### 7.1 技术风险

| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|---------|
| **Claude Code 原生替代跨会话连续性** | 高 | 中 | 已设计备选入口（变更管理即时价值）；护城河在价值链和度量层，非入口层 |
| **Plugin API Breaking Change** | 中 | 高 | 紧跟 Claude Code 版本发布；最小化对未文档化行为的依赖；自动化测试覆盖 Plugin 结构 |
| **上下文窗口压力随功能增长** | 高 | 中 | 信息分层（L1/L2/L3）；Rules 模块化拆分；Skill 分拆模式；PreCompact Hook |
| **LLM 规则遵循退化** | 中 | 高 | Hook 层硬阻断覆盖铁律；增加 prompt 类型 Hook 覆盖更多行为规则；定期 RED-GREEN-REFACTOR 验证 |
| **Markdown Schema 不一致** | 中 | 中 | 自动化测试（tests/static/）已覆盖结构层面；增加 PostToolUse Hook 做运行时格式校验 |
| **Hook 脚本故障影响 UX** | 低 | 中 | async Hook 非阻塞执行；Hook 超时设置合理（3-10s）；PostToolUseFailure Hook 处理异常 |

### 7.2 架构风险

| 风险 | 描述 | 缓解策略 |
|------|------|---------|
| **功能膨胀** | 17 个 Skill + 13 个 Schema 已是较大体量，继续增长会加剧维护负担 | 严格评估新增 Skill 的必要性；优先通过子命令扩展现有 Skill |
| **认知负担** | 新贡献者需要理解完整的概念模型（BR->PF->CR）+ 状态机 + 质量门 + 17 个 Skill 的关系 | CLAUDE.md 权威文件索引已建立；增加 onboarding 文档 |
| **过度设计** | 部分功能（如 5 维风险扫描、对抗审查）在单开发者场景可能过重 | 复杂度自适应已解决部分问题（S/M 跳过部分步骤）；自主级别进一步调节 |
| **Plugin 系统依赖锁定** | devpace 深度依赖 Claude Code Plugin 系统特有机制 | 核心逻辑（概念模型、状态机、变更管理）与 Plugin 机制解耦；理论文件和 Schema 独立于运行时 |

### 7.3 缓解优先级

1. **立即执行**：Rules 模块化拆分（降低上下文压力）+ Hook 测试框架（提升可靠性）
2. **v2.0 前完成**：Schema 共享定义 + Skill 依赖文档化
3. **持续观察**：Claude Code 原生能力演进、Plugin API 变更、LLM 规则遵循可靠性

---

> 本报告基于 v1.4.0 代码库、design.md、vision.md 及相关 Skill/Hook/Schema 文件的完整分析。评估时间：2026-02-25。
