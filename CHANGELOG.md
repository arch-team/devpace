# Changelog

本文件记录 devpace 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)。

## [1.1.0] - 2026-02-22

pace-release 从被动状态追踪器演进为主动发布编排器。基于 10 个开源项目对标分析（Changesets/Release Please/git-cliff/Nx/release-it 等）。

### Added

- **Changelog 自动生成**：从 Release 包含的 CR 元数据按类型分组（Features / Bug Fixes / Hotfixes），写入 Release 文件和用户产品的 CHANGELOG.md。包含 PF 关联信息。可选按 BR 分组生成高层 Release Notes
- **版本号自动 Bump**：读取 integrations/config.md 版本管理配置（支持 JSON/TOML/YAML/文本格式），根据 CR 类型推断 semver（feature→minor, defect/hotfix→patch），直接更新版本文件
- **Git Tag 创建**：`/pace-release tag` 自动 `git tag v{version}` + 可选 `gh release create`（附 changelog 内容）
- **GitHub Release**：close 时通过 `gh` CLI 创建 GitHub Release，附 changelog 内容
- **回滚追踪**：Release 状态机新增 `rolled_back` 状态（deployed → rolled_back），记录回滚原因，自动引导创建 defect/hotfix CR
- **Gate 4 系统级发布门禁**：Release create 后、deploy 前的系统级检查——运行构建/测试命令、检查 CI pipeline 状态、确认候选 CR 完整性。依赖 integrations/config.md，无配置时静默跳过
- **一键发布**：`/pace-release full` 按顺序执行 changelog → version → tag → close，每步可跳过
- **发布验证自动化**：integrations/config.md 新增"发布验证"配置，/pace-release verify 时自动执行验证命令
- **版本管理配置**：integrations/config.md 新增"版本管理"section（版本文件路径、格式、字段、Tag 前缀）
- **CI 检查命令**：integrations/config.md CI/CD section 新增"检查命令"字段
- **Release Notes 独立子命令**：`/pace-release notes` 从 CR+PF+BR 元数据按业务需求分组生成面向最终用户的变更说明（与按 CR 类型的 Changelog 互补），用产品语言描述
- **发布分支管理**：`/pace-release branch` 支持三种模式——直接发布（默认）、Release 分支（`release/v{version}`）、Release PR（借鉴 Release Please，生成含 changelog+version 的 PR）
- **发布分支配置**：integrations/config.md 新增"发布分支"section（分支模式/前缀/Release PR/自动合并）

### Changed

- **release-format.md**：新增 rolled_back 状态、版本信息段、Changelog 段、Release Notes 段、发布分支字段、关闭连锁更新从 5 步扩展到 8 步
- **integrations-format.md**：新增版本管理、发布验证和发布分支 section，CI/CD 新增检查命令，降级行为补充 5 项
- **SKILL.md**：8 新子命令（changelog/version/tag/rollback/full/status 增强/notes/branch），allowed-tools 新增 Bash
- **release-procedures.md**：8 新章节（Changelog 生成/Version Bump/Git Tag/Rollback/Full/Gate 4/Release Notes/发布分支管理）
- **design.md §14**：从"被动追踪"重写为"主动编排"，新增 Gate 4、回滚路径、CR 数据驱动、Release Notes、发布分支设计
- **devpace-rules.md §14**：新增发布编排能力表（8 能力+降级）、Gate 4、rolled_back 状态机、发布分支规则
- **release.md 模板**：新增版本信息段、Changelog 段和 Release Notes 段
- **integrations.md 模板**：新增版本管理、发布验证和发布分支段
- **版本号建议逻辑**：修正为"包含 feature→minor，仅 defect/hotfix→patch"（符合 semver 惯例）

### Backward Compatible

- 所有新能力通过 integrations/config.md 配置启用，无配置时降级到手动模式
- 已有 Release 文件（无版本信息段/Changelog 段）正常工作，新段在下次操作时自动补充
- rolled_back 是新增终态，不影响已有 staging → deployed → verified → closed 流程
- Gate 4 完全可选——无 integrations/config.md 时静默跳过
- Release Notes 和发布分支完全可选——无配置时静默跳过

## [1.0.0] - 2026-02-22

v1.0.0 正式版。14 个 Phase、83 个任务、26 个用户场景、48 个功能需求全部完成。148 项静态测试通过。

### Milestone

- **功能完成度**：26/26 用户场景、48/48 功能需求全部实现
- **OBJ 覆盖**：14 个业务目标中 12 个已验证（OBJ-9/10 为长期生态目标，不阻塞 1.0）
- **工程质量**：148 项静态测试全绿，Hook Node.js 跨平台，v0.1→v0.9 迁移路径验证通过
- **文档完备**：LICENSE + README + CONTRIBUTING + CHANGELOG + 用户指南 + 示例项目
- **开源借鉴**：30+ 项目对标分析，21 项优秀设计模式落地（Linear AI、ECC、BMAD 等）
- **实测数据**：跨 3 次会话中断需要 0 次用户纠正（手动方案需 8 次）

### Changed

- 版本号 0.9.1 → 1.0.0（plugin.json、marketplace.json、state-format.md）

### Backward Compatible

- 无功能变更，纯版本号毕业标记
- v0.9.1 项目无需迁移，state.md 版本标记会在下次会话时自动更新

## [0.9.1] - 2026-02-22

质量收尾：Skill description CSO 合规审计 + v0.1→v0.9 迁移路径修复。

### Fixed

- **Skill description CSO 审计**：14 个 Skill 的 `description` 字段全面审计，修复 8 FAIL + 1 WARN——删除"做什么"前缀，统一以触发条件开头（`Use when` / `Auto-invoked`），防止 Claude 跳过读取完整 SKILL.md。
- **迁移版本检测**：Step 0 版本检测从仅支持 v0.1.0~v0.4.0 扩展到 v0.1.0~v0.9.0 全版本范围，中间版本项目不再被错误识别。
- **迁移目标版本**：v0.1→v0.2 迁移升级为 v0.1→v0.9 一次性跳跃迁移，迁移后即为当前版本。
- **state-format 合法版本列表**：补充 0.8.0（ECC 借鉴）和 0.9.0（BMAD 借鉴）。

### Added

- **迁移 taught 标记**：迁移流程新增空 `taught` 标记（`<!-- taught: -->`），确保渐进教学在迁移项目上生效。
- **迁移 context.md 扫描**：迁移流程新增可选 context.md 自动生成，扫描项目技术栈和编码约定。
- **迁移跨版本安全规则**：明确 v0.1.0→v0.9.0 为一次性跳跃迁移，所有中间版本新增字段均为可选。

### Backward Compatible

- CSO 修复仅调整 description 文本，不改变 Skill 内部行为
- 迁移机制"只添加不删除"原则不变，现有项目数据完整保留

## [0.9.0] - 2026-02-22

BMAD-METHOD（36,900+ Stars）深度借鉴：对抗式审查、工作流自适应、步骤隔离、技术约定宪法、Agent 沟通风格差异化、智能导航。

### Added

- **对抗审查（Adversarial Review）**：Gate 2 通过后追加对抗审查（M/L/XL CR）——强制切换到"假设代码有缺陷"心态，按 4 个维度（边界/安全/性能/集成）搜寻问题，必须找出至少 1 项。发现记入 Review 摘要供人类过滤假阳性，不影响 Gate 2 判定。checks-format.md 新增 `adversarial` 检查类型（内置不可删除）。
- **复杂度自适应路径**：意图检查点完成后按复杂度提供差异化路径——S 单文件走快速模式（省略详细意图/执行计划/计划反思），S 多文件/M 走标准模式，L/XL 走完整模式。CR 状态机始终完整执行，快速模式是"省略可选步骤"而非"绕过状态机"。
- **升级守卫**：意图检查点和开发过程中持续监控复杂度——初始评估 S/M 但发现多组件依赖或架构级信号时建议升级，开发中文件/目录数超过阈值时提醒复杂度漂移。建议不阻断，已有工作不丢失。
- **步骤隔离（L/XL CR）**：借鉴 BMAD Micro-File 工作流引擎——"处理当前状态转换时，不预读后续状态的处理逻辑"。每个阶段有明确的聚焦范围和不可预读范围，防止 AI 在长上下文中合并或跳过步骤。附带合理化预防表。
- **技术约定文件（context.md）**：借鉴 BMAD project-context.md 设计。新增 `context-format.md` Schema + `context.md` 模板。/pace-init 自动扫描项目代码库检测技术栈和编码约定（检测到 < 3 条约定时跳过创建）。推进模式自动加载 context.md 确保技术决策一致性。精简原则："删除后 Claude 有 >50% 概率猜错"才记录。
- **Agent 沟通风格**：3 个 Agent 增加差异化沟通风格定义——pace-pm（决策导向，业务术语，追问 WHY）、pace-engineer（简洁精确，文件路径+编号引用，少说多做）、pace-analyst（量化分析，趋势符号，对比基线）。
- **角色相关性评估**：/pace-role 切换角色后自动静默评估当前上下文，识别与新角色最相关的 2-3 个关注维度，后续输出聚焦这些维度。
- **智能导航/建议下一步**：/pace-status 快速概览输出后自动推断并附加 1 条"建议下一步"——7 级优先级规则（in_review CR → developing CR → 未验证部署 → 迭代接近完成 → 距 retro > 7 天 → backlog 为空）。与 §1 节奏提醒互补不重复。

### Changed

- **checks-format.md**：三种检查类型（命令+意图+对抗审查），速查卡片和内置检查表更新。
- **review-procedures.md**：新增对抗审查 section（4 维度审查+零发现兜底+假阳性声明），摘要格式新增对抗审查段。
- **dev-procedures.md**：新增复杂度自适应路径（快速/标准/完整）、升级守卫、复杂度漂移检测、步骤隔离执行指南。
- **devpace-rules.md §2**：Gate 2 对抗审查规则、推进模式 context.md 加载、步骤隔离铁律+合理化预防、§0 速查卡片（自适应路径+升级守卫+步骤隔离+对抗审查）。
- **devpace-rules.md §8**：context.md 维护规则。
- **init-procedures.md**：生成规则新增 context.md 可选自动生成（Step 6）、按需目录创建表更新、延后收集时机新增技术约定讨论。
- **agents/*.md**：3 个 Agent 新增"## 沟通风格"section。
- **pace-role/SKILL.md**：Step 2 新增相关性评估步骤。
- **status-procedures.md**：快速概览新增"建议下一步"子 section，三级输出递增描述更新。
- **design.md §6**：新增对抗审查、复杂度自适应路径、步骤隔离、技术约定 4 项设计段落。§11 schema 数量 6→7。

### Backward Compatible

- 对抗审查：S CR 跳过，不影响已有 Gate 2 通过/失败逻辑——发现仅供人类参考
- 自适应路径：S 多文件/M/L/XL 行为与之前完全一致——仅 S 单文件新增快速模式省略可选步骤
- 升级守卫：纯建议不阻断——用户选择继续则按原复杂度推进
- 步骤隔离：仅 L/XL 强制，S/M 不受约束
- context.md：完全可选——不存在时静默跳过，不报错不提示
- Agent 沟通风格：纯增量描述，不改变已有行为逻辑
- 智能导航：附加在概览末尾，不改变主输出格式

## [0.8.0] - 2026-02-22

Everything Claude Code (ECC 1.4.1) 深度借鉴：Hook 跨平台可靠性、检查项智能化、Model Tiering、上下文管理、Agent 交接、学习管道置信度。

### Added

- **检查项依赖（短路逻辑）**：checks.md 支持可选的 `依赖` 字段——前置检查失败时自动跳过被依赖项（如编译失败→跳过测试和 lint），避免无效检查噪声。
- **检查项阈值**：checks.md 支持可选的 `阈值` 字段——数值型检查的合格线（如覆盖率 80%）。
- **安全检查推荐**：/pace-init 根据项目技术栈自动推荐安全检查——Node.js(`npm audit`)、Python(`bandit`)、Go(`gosec`)、通用（密钥泄露检测）。推荐而非强制。
- **学习管道置信度**：insights.md 的 pattern 新增 `置信度`（0.2-0.9 动态范围）和 `最近引用` 字段。初始 0.5，验证 +0.1，存疑 -0.2。§12 经验引用按置信度过滤——>0.7 优先引用，<0.4 不主动引用。
- **上下文 compact 建议**：L/XL CR 的 Gate 1 通过后，附加 compact 建议——实现阶段上下文已持久化，压缩可释放空间给验证阶段。非强制，用户自行决定。
- **pace-pulse 上下文信号**：新增第 7 个检测信号"上下文密集"——本会话已有 3+ 个 Gate 1 通过时建议 /compact。
- **CR 事件表交接列**：可选的第 5 列——在状态转换时记录上下文传递信息（遗留事项、打回原因分类、后续注意），提升 Agent 间信息保真度。
- **打回信息结构化**：人类打回 CR 时引导结构化记录——原因类别（范围/质量/设计）+ 具体描述 + 期望方向。
- **Hook 共享工具库**：`hooks/lib/utils.mjs` 提供 JSON 解析、文件路径提取、CR 状态读取等公共函数。

### Changed

- **Hook 跨平台迁移**：`pre-tool-use`、`post-cr-update`、`intent-detect` 三个 Hook 从 Bash 迁移到 Node.js ESM（.mjs）。用 `JSON.parse` 替代 `grep+sed` 正则提取 JSON 字段，消除路径含转义字符/Unicode 时的解析失败。`session-start.sh` 和 `session-stop.sh` 保持 Bash（复杂度低）。
- **Model Tiering**：pace-pm → `opus`（变更评估和规划需最强推理）、pace-pulse → `haiku`（读数据+比阈值，轻量任务降本提速）、pace-learn → `sonnet`（显式声明，防止运行时默认值变化）。pace-engineer 和 pace-analyst 保持 `sonnet` 不变。
- **learn-procedures.md**：Step 2 提取 Pattern 增加 Gate 反思内容（`[gate1-reflection]`、`[gate2-reflection]`）和打回交接信息的读取。Step 3 Pattern 格式增加置信度和最近引用字段。置信度更新规则：吻合 +0.1、矛盾 -0.2、clamp [0.2, 0.9]。
- **devpace-rules.md §2**：推进模式新增检查项短路逻辑说明。
- **devpace-rules.md §6**：Checkpoint 新增 L/XL Gate 1 后 compact 建议。
- **devpace-rules.md §12**：经验引用新增置信度过滤规则和引用时更新最近引用日期。
- **devpace-rules.md §0**：速查卡片同步更新（短路逻辑、compact 建议）。
- **checks-format.md §0**：速查卡片新增依赖/阈值/安全检查说明。
- **insights-format.md §0**：速查卡片新增置信度规则和引用过滤说明。
- **init-procedures.md**：默认检查项建议表增加"安全检查建议"列。

### Backward Compatible

- 检查项依赖/阈值：纯可选字段——不配置时行为与之前完全一致
- 安全检查：推荐非强制——/pace-init 以注释形式包含，用户决定是否启用
- 置信度：缺失时视为 0.5（默认值）——已有 insights.md 中的 pattern 不受影响
- 交接列：可选——无交接列的事件表自动视为空（向后兼容）
- 打回结构化：引导性质——用户未提供结构化原因时 Claude 自行分类
- Hook .mjs 迁移：输出内容和语义与 .sh 版本完全一致——上层规则和 Skill 无需修改
- Model Tiering：不改变 Agent/Skill 的行为逻辑，仅调整运行时使用的模型

## [0.7.0] - 2026-02-22

开源生态深度借鉴：30+ 项目对标分析，状态机增强、执行质量层、审查质量、探索增强。累计 21 项开源借鉴落地。

### Added

- **CR 复杂度量化**：每个 CR 自动评估为 S/M/L/XL（文件数 × 目录数 × 验收条件数 × 跨模块依赖），驱动后续流程（执行计划、拆分评估、反思步骤）。
- **CR 执行计划**：L/XL CR 在意图检查点后自动生成步骤级执行计划（原子动作 + 精确文件路径 + 可验证预期 + 依赖关系），强制展示给用户确认后才进入 developing。
- **CR 间关系**：CR 之间支持阻塞（blocks）、前置（depends-on）、关联（related-to）三种关系类型，变更管理时自动遍历关联。
- **变更 Triage 分流**：变更检测后先执行结构化 Triage（Accept/Decline/Snooze），再进入详细处理。避免不值得的变更浪费分析资源。
- **PRD→功能树**：`/pace-init --from <文件>` 支持从 PRD/需求文档自动提取 BR→PF 层级结构。
- **CR Checkpoint 标记**：状态转换时在 CR 事件表记录 checkpoint 标记，支持变更恢复时精确定位断点。
- **角色约束转换**：CR 状态转换受角色约束——如 `developing→verifying` 需 Engineer 角色，`in_review→approved` 需人类。
- **累积 Diff 审查报告**：M/L/XL CR 的 Review 摘要新增累积变更报告——按模块分组统计 + 验收条件映射（"验收条件 X → 由文件 Y 实现"）+ 范围外/未覆盖检测。
- **Gate 间反思步骤**：L/XL CR 执行计划生成后执行计划反思（4 维度：需求覆盖 / 过度设计 / 拆分必要性 / 假设合理性）。Gate 1/2 通过后附加轻量反思观察（技术债+测试覆盖 / 边界场景+验收全面性），记录到 CR 事件表。
- **探索模式关注点引导**：Claude 自动推断探索关注点——架构（全局结构、依赖图）、调试（假设→缩减→验证）、评估（多维对比、风险收益），输出格式随关注点适配。与角色意识正交组合。
- **Iron Laws 合理化预防**：Gate 3 不可绕过、探索模式不改文件、L/XL 不跳过意图明确——每条铁律附带常见合理化借口和预防反驳。
- **Gate 2 独立验证**：Gate 2 执行时不信任 Gate 1 阶段的任何快照或结论，从零获取证据（重新读取验收条件 + 独立获取 git diff）。
- **Review 反表演性**：收到修改意见时先理解→评估→执行，禁止"You're absolutely right!"式表演性回应，超出 CR 范围的建议引导创建新 CR。
- **Gate 证据摘要**：Gate 1/2 checkpoint 标记附带 ≤30 字验证证据，证据必须来自本次验证运行。
- **CSO description 规则**：Skill description 只写"何时触发"不写"做什么"，防止 Claude 跳过阅读完整 SKILL.md。
- **RED-GREEN-REFACTOR**：Skill 内容质量验证方法——基线观测（无 Skill 时偏差）→ 最小规则（修正偏差）→ 漏洞补充（压力测试），写入 dev-workflow.md。

### Changed

- **devpace-rules.md §2**：推进模式新增反思行为说明（计划反思 + Gate 通过反思）。探索模式新增关注点引导规则（4 种关注点 + 触发词 + 输出格式）。§0 速查卡片同步更新。
- **dev-procedures.md**：意图检查点新增复杂度量化评估逻辑和拆分触发条件。新增执行计划生成（L/XL 必须）、方案确认门禁、计划反思、Gate 通过反思。
- **review-procedures.md**：新增独立验证原则、修改意见处理规范（反表演性）、累积 Diff 报告步骤、摘要格式增加累积变更报告段。
- **cr-format.md**：新增复杂度字段（S/M/L/XL）、关联 section（阻塞/前置/关联）、checkpoint 标记规则、操作者字段、执行计划格式。
- **change-procedures.md**：新增 Step 0.5 Triage 分流、关联遍历、Release 影响评估。
- **design.md §5**：转换门禁表增加执行角色列和 checkpoint 设计。
- **design.md §6**：质量门系统增加证据摘要和独立验证原则。
- **plugin-dev-spec.md**：新增 CSO description 编写规则。
- **dev-workflow.md §4**：新增 RED-GREEN-REFACTOR Skill 验证方法论。

### Backward Compatible

- 复杂度字段：缺失时默认按启发式规则推断，不影响已有 CR
- 关联 section：可选段落，缺失不影响流程
- 执行计划：仅 L/XL 必须，S/M 不受影响
- Triage：在完整变更流程前执行，不改变变更处理逻辑本身
- 反思步骤：S 复杂度可省略，不阻断流程
- 关注点引导：自动推断，不增加用户操作步骤
- `--from` 参数：纯新增，不影响已有 `/pace-init` 行为

## [0.6.0] - 2026-02-22

借鉴 Linear AI 核心创新：推理可验证、自主性可调、经验可学习、来源可区分。

### Added

- **溯源标记**：project.md 和 CR 意图 section 中，Claude 新增内容附带 HTML 注释标记来源（`<!-- source: user -->` / `<!-- source: claude, [原因] -->`）。日常不可见，/pace-trace 查看时展示。跨会话恢复时区分"用户明确说的"和"上次推断的"。
- **三层渐进透明**：系统行为的推理信息按需展开——默认 ≤15 字后缀（表面层），追问"为什么"展开 2-5 行推理链（中间层），`/pace-trace` 展示完整决策轨迹含溯源标记（深入层）。
- **`/pace-trace` 命令**：决策轨迹查询——读取 CR 事件表、checkpoint 标记和溯源标记，重建 Gate/意图/变更等决策的完整推理过程。
- **渐进自主性**：推进模式内 3 级自主性——辅助（Gate 失败时询问而非自动修复，M 复杂度也生成执行计划）、标准（默认，当前行为不变）、自主（简化审批条件放宽至 ≤5 文件）。通过 project.md `自主级别:` 字段配置。Gate 3 在任何级别下都是人类阻塞门禁。
- **纠正即学习（§12.5）**：用户否决简化审批、修改 PF 分解、调整影响评估等纠正行为发生时，Claude 主动提议记录为偏好——"记住这个偏好？以后 [场景] 时我会 [调整后的行为]。"用户确认后写入 insights.md，后续 §12 引用时偏好优先级高于统计 pattern。
- **insights-format.md**：新增 Schema，定义偏好（preference）条目类型——来源为用户纠正，引用优先级高于模式/防御/改进类型。
- **场景 S24-S26**：决策轨迹查询、自主级别配置、纠正即学习。
- **功能组 F7**：6 个功能点覆盖溯源标记、三层透明、pace-trace、渐进自主性、纠正即学习、偏好条目。
- **NF11 推理可验证性**：用户可按需验证 AI 的每个系统判断。

### Changed

- **§5 分级输出**：从单层推理后缀升级为三层渐进透明（表面/中间/深入）。
- **§2 推进模式**：行为按自主级别分化——辅助（多询问）、标准（默认不变）、自主（放宽审批）。
- **§12 经验驱动决策**：偏好类型条目优先级高于其他类型。新增 §12.5 纠正即学习子章节。
- **§4/§4.5/§8**：创建 CR、意图检查点、状态文件维护时添加溯源标记。
- **design.md §2**：P6 延伸从单段改为三层渐进透明表格。新增渐进自主性设计段落。
- **design.md §3**：新增溯源标记设计段落。新增经验积累闭环段落。
- **§12 映射表**：14 个 Skills（12 用户 + 2 内部）。
- **project-format.md**：新增溯源标记语法定义和 `自主级别:` 配置字段。
- **cr-format.md**：新增意图 section 溯源标记规则。
- **devpace-rules.md**：精简为核心行为规则，详细规则提取到 knowledge/ 文件。

### Backward Compatible

- 溯源标记：HTML 注释对 Markdown 渲染完全透明——无标记的既有内容不受影响
- 自主级别：默认"标准"——不增加初始配置成本，已有项目行为不变
- 偏好条目：insights.md 无偏好条目时 §12 正常引用其他类型
- /pace-trace：纯新增命令，不影响已有命令
- 三层透明：表面层行为与之前完全一致，中间/深入层仅在追问时触发

## [0.5.0] - 2026-02-21

定位优化：AI 原生研发节奏管理——渐进教学、价值可见化、独立开发者减摩。

### Added

- **渐进教学系统（§17）**：系统行为（任务创建、质量门禁、审批等待、变更检测、功能树更新、合并级联）首次出现时附带一句话解释。每个行为在项目生命周期内只教一次，通过 state.md 中的 `<!-- taught: ... -->` 标记追踪。
- **成熟度驱动功能发现（§11）**：第 3 个任务合并后推荐 `/pace-retro`，首次成功变更后推荐 `/pace-change`，第 5 个任务合并后推荐 `/pace-plan`。每个推荐只出现一次。
- **首个任务合并回顾（§11）**：首个任务合并后，展示 3 行摘要，说明 devpace 在幕后做了什么。
- **价值链视图**：`/pace-status chain` 用用户友好的术语（无 BR/PF/CR 行话）展示当前工作在目标→功能→任务树中的位置。
- **理论"why"模式**：`/pace-theory why` 解释最近 devpace 行为背后的设计理由。
- **影响分析追溯说明**：变更影响报告现在包含一行关于完整目标到代码覆盖的说明。
- **未初始化变更检测（§9）**：没有 `.devpace/` 的项目在检测到变更意图时仍可获得即时影响分析，并引导使用 `/pace-init`。
- **命令发现（§3）**："有什么命令"只显示核心 4 个；"所有命令"显示完整 3 层列表。
- **场景 S22**：渐进教学用户场景已添加到需求文档。

### Changed

- **README.md**：标语重新围绕 AI 原生节奏管理定位。痛点按差异化强度重排。新增对比表（devpace vs 手动 CLAUDE.md vs TodoWrite）。30 秒体验改为突出变更管理。
- **plugin.json**：描述移除了 "BizDevOps" 行话，改用用户可感知的能力描述。
- **简化审批（§2）**：简单任务（单个任务、≤3 个文件、门禁一次通过、0% 偏移）跳过 `in_review` 等待——改用行内确认。
- **自适应会话结束（§6）**：无 `.devpace/` 变更 = 无结束协议。简单 = 1 行。标准 = 3 行。复杂 = 5 行。
- **§0 速查卡片**：新增命令分层表和简化审批/自适应结束摘要。
- **pace-init 第 3 步**：初始化后输出现在包含"接下来会发生什么"预览。
- **state-format.md**：新增 `taught` 标记格式和 v0.5.0 版本值。
- **Todo app 演示**：变更场景从第 2 个任务后移到第 1 个任务后，更早展示差异化能力。
- **design.md §2**：P2 渐进暴露扩展了教学维度说明。

### Backward Compatible

- 教学标记：缺失 = "全部未教"——新旧项目均兼容
- 简化审批：仅在所有严格条件满足时触发；标准/复杂任务流程不变
- 自适应会话结束：标准工作量行为与之前版本一致
- 新 Skill 参数（`chain`、`why`）：纯新增，已有参数不受影响

## [0.4.0] - 2026-02-21

UX 摩擦优化：渐进初始化、推进模式 opt-in、静默角色、提醒节流。

### Changed

- **渐进初始化（B1）**：`/pace-init` 现在只问项目名称和描述。创建最小 `.devpace/`（state.md、project.md 存根、backlog/、rules/）。iterations、metrics、releases 目录在首次使用时创建。`/pace-init full` 保留完整 6 步设置。
- **推进模式 opt-in（B5）**：会话中首次编码意图触发自然确认（"要跟踪这个变更，还是只是快速修改？"）。`/pace-dev` 始终直接进入。一旦选择跟踪，本次会话后续自动进入。
- **静默角色推断（B4）**：角色自动推断不再输出切换提示。只有 `/pace-role` 显式切换才显示确认。
- **提醒节流（B6）**：会话开始时最多显示 1 条最高优先级提醒（之前：全部匹配）。脉冲间隔从 3 个检查点增加到 5 个。会话提醒总上限：3 条。
- **Schema 更新**：state-format.md 迭代行改为可选。project-format.md 新增"最小状态"段落，用于存根项目。
- **模板**：state.md 移除迭代行（在首次 `/pace-plan` 时添加）。project.md 变为存根，带有"随工作生长"占位符。
- **Rules §1/§4/§8**：健康检测容忍缺失目录。自动创建任务适配空 project.md（创建功能并回填功能树）。缺失目录在写入时自动创建。

### Backward Compatible

- 已有 v0.3.0 项目无需修改即可继续使用（所有文件已存在）
- 规则变更（opt-in、静默角色、节流）立即应用于所有项目
- 新的最小初始化使用 v0.4.0 版本标记
- `/pace-init` 检测到 v0.3.0 不会触发迁移

## [0.3.0] - 2026-02-21

完整 BizDevOps 生命周期覆盖：发布管理、运维反馈闭环、角色感知、缺陷管理和 DORA 度量。

### Added

- **3 个新命令**：`/pace-release`（发布管理）、`/pace-ops`（运维反馈）、`/pace-role`（角色切换）
- **任务类型**：`feature`（默认）、`defect`、`hotfix`，带严重性等级（critical/major/minor/trivial）
- **Released 状态**：通过 Release 管理追踪的任务的可选 `released` 终态
- **热修复加速路径**：紧急热修复走 `created → developing → verifying → merged`（跳过 in_review）
- **发布管理**：`staging → deployed → verified → closed` 生命周期，含部署追踪和验证清单
- **角色感知**：5 个概念角色（业务方 / PM / 开发 / 测试 / 运维），支持自动推断和显式切换
- **缺陷管理**：缺陷任务中的根因分析段落、引入追溯、严重性追踪
- **DORA 度量**：部署频率、变更前置时间、变更失败率、MTTR
- **缺陷根因报告**：`/pace-retro` 中自动根因分类和预防建议
- **集成框架**：可选的 CI/CD 和监控工具配置（`integrations/config.md`）
- **合并后 Hook**：存在已合并任务时提示创建/更新 Release
- **角色视图**：`/pace-status biz/pm/dev/tester/ops` 提供视角特定的仪表盘
- **成功指标评估**：`/pace-retro` 中的业务目标对齐检查
- **发布影响评估**：变更管理评估对活跃 Release 的影响
- **2 个新 Schema**：`release-format.md`、`integrations-format.md`
- **Rules §13-§16**：角色感知、发布管理、运维反馈、集成管理
- **v0.1→v0.2 迁移**：已有项目的自动升级路径

### Changed

- 任务 Schema：新增类型、严重性、Release 关联、根因分析段落
- 状态格式：新增可选的发布状态段落
- 项目格式：新增 Release 标记（📦/🚀）和缺陷标记（🐛/🔥）
- 迭代格式：功能表新增 Release 列，偏差快照新增缺陷计数
- 工作流模板：新增 `released` 状态、`merged→released` 转换、热修复加速路径
- 度量：新增缺陷管理指标和完整 DORA 维度
- 理论映射：更新 §12，新增 Release、缺陷、角色、DORA、运维闭环映射
- 会话节奏检测：新增 Release 验证、缺陷比率、成功指标达成提醒
- 变更流程：新增 Release 影响评估
- 开发流程：新增缺陷/热修复任务创建规则
- 回顾流程：新增缺陷分析维度、DORA 报告、缺陷根因报告

### Backward Compatible

- 所有新字段均为可选——已有 v0.1.0 项目无需修改即可使用
- `released` 是可选终态——`merged` 仍然有效
- `releases/` 和 `integrations/` 目录可选——缺失时优雅降级
- 任务 `type` 缺失时默认为 `feature`
- `/pace-init` 自动检测 v0.1.0 并提供引导式迁移

## [0.1.0] - 2026-02-20

首次公开发布。面向 Claude Code 的完整 BizDevOps 研发节奏管理。

### Added

- **8 个命令**：`/pace-init`、`/pace-dev`、`/pace-plan`、`/pace-status`、`/pace-review`、`/pace-change`、`/pace-retro`、`/pace-theory`
- **价值链模型**：业务目标（OBJ）→ 业务需求（BR）→ 产品功能（PF）→ 变更请求（CR）
- **任务状态机**：`created → developing → verifying → in_review → approved → merged`，含 `paused` 转换
- **质量门禁**：Gate 1（代码质量）、Gate 2（集成检查）、Gate 3（人类审批）
- **变更管理**：5 种变更类型——插入、暂停、恢复、重排优先级、修改——含影响分析和确认工作流
- **跨会话连续性**：通过 `state.md` 自动恢复，零用户重新解释
- **两种工作模式**：探索（默认，只读）和推进（代码变更，任务绑定）
- **PreToolUse Hook**：任务状态转换的质量门禁提醒
- **会话生命周期 Hook**：会话开始自动加载状态，会话结束保存提醒
- **3 个 Schema 契约**：任务格式、项目格式、状态格式（`knowledge/_schema/`）
- **8 个项目模板**：由 `/pace-init` 引导生成到 `.devpace/` 目录
- **运行时规则**：225 行行为协议（`rules/devpace-rules.md`）
- **度量定义**：质量、交付和价值对齐度量（`knowledge/metrics.md`）
- **BizDevOps 理论参考**：通过 `/pace-theory` 访问的方法论指南

### Verified

- 2 个真实项目验证（Python/diagnostic-agent-framework + TypeScript/NestJS 模拟）
- 16 项验证通过，覆盖已有和新建项目场景
- 87 个静态测试用例通过（9 个测试模块）
- 跨会话恢复：3 次会话中断需要 **0 次**用户纠正，手动维护 CLAUDE.md 方案需要 **8 次**（7 维度分析）
- 渐进丰富：8 次提交中 **0 次**手动编辑状态文件
- 状态可扩展性：12 个任务时 15 行（O(1) 增长已确认）
