# link / create — 关联与创建

> **职责**：定义 /pace-sync link 子命令和 create 内部流程的详细执行步骤。支持全部实体类型（EPIC/BR/PF/CR）。

## §1 link 输入解析

`$1` = 实体 ID（如 EPIC-001、BR-002、PF-003、CR-003 或 003），`$2` = 外部 ID（如 #42 或 42，**可选**）

实体 ID 解析：调用 `sync-procedures-entity.md` §1。

## §2 标准 link（提供外部 ID）

**执行步骤**：
1. 验证实体存在：通过 §1 解析确认实体文件（独立文件或 project.md 内联）
2. 验证外部实体存在：执行适配器"获取状态"操作（参数：外部实体编号）
3. 写入实体文件"外部关联"字段（独立文件）；内联实体仅更新 sync-mapping.md
4. 更新 sync-mapping.md 关联记录表（追加行，含实体 ID + 外部编号 + 时间戳）
5. 输出确认：{实体ID} ↔ 外部实体 #{编号} 已关联

## §3 智能 link（省略外部 ID）

当用户仅提供实体编号时，自动搜索外部平台中标题相似的实体：

**执行步骤**：
1. 验证实体存在，读取实体标题
2. 执行适配器"列出工作项"操作，获取外部平台的开放实体列表
3. 按标题相似度排序，取前 5 个候选
4. 展示候选列表供用户选择：
   ```
   找到以下可能匹配的 Issue：
   1. #42 — 实现用户认证模块 (open, backlog)
   2. #38 — 用户登录功能 (open, in-progress)
   3. #55 — 认证系统重构 (open)
   选择编号关联（或输入外部 ID）：
   ```
5. 用户选择后执行 §2 标准 link 流程

**无匹配时**：提示"未找到匹配的外部实体。运行 /pace-sync 可自动创建。"

## §4 批量 link

`$ARGUMENTS` 包含 `--all` 时，为所有未关联实体逐个执行智能 link（§3）。

**执行步骤**：
1. 运行 `node $PLUGIN_DIR/skills/pace-sync/scripts/extract-entity-metadata.mjs <.devpace 路径> --type all` 获取全部实体
2. 读取 sync-mapping.md 关联记录，识别已关联实体
3. 筛选未关联实体，对每个执行 §3 智能 link
4. 输出汇总：`{N} 个实体已关联 / {M} 个跳过（用户取消或无匹配）`

## §5 关联记录格式

（按 `knowledge/_schema/integration/sync-mapping-format.md`）：
```markdown
| {实体ID} | {平台}#{编号} | {YYYY-MM-DD HH:mm} | — | — |
```

## §5.1 错误处理

- CR 不存在 → 提示用户
- 外部实体不存在 → 提示用户确认 ID
- CR 已有关联 → 提示已关联，确认是否覆盖

## §6 create — 从实体创建外部工作项

**输入**：实体 ID（EPIC-xxx / BR-xxx / PF-xxx / CR-xxx）

**执行步骤**：
1. 验证实体存在且无外部关联
2. 读取实体元数据（运行 `node $PLUGIN_DIR/skills/pace-sync/scripts/extract-entity-metadata.mjs <.devpace 路径> --id {实体ID}` 或直接读文件）
3. 生成 Issue body：
   ```bash
   node $PLUGIN_DIR/skills/pace-sync/scripts/generate-issue-body.mjs <.devpace 路径> --id {实体ID}
   ```
   解析 JSON 输出获取 `body`（Issue 描述）和 `labels`（标签列表）。脚本不可用时回退到直接读取实体文件并按适配器模板手动填充。
4. 执行适配器"获取实体类型状态映射"→ 获取当前状态对应的外部状态标记
5. 执行适配器"创建工作项"操作（参数：标题、描述、entity_type、状态标记）
6. 执行适配器"设置实体类型标记"操作（如适用——GitHub 添加 `devpace:{type}` 标签）
7. 自动执行 link（复用 §2 流程）
8. **层级关联**（§7）：查找上级实体的外部关联，若有则通过操作语义"建立父子关系"建立 sub-issue
9. 输出确认：{实体ID} → 外部工作项 #{编号} 已创建并关联

## §7 层级关联（Sub-Issue）

CR/PF/BR 创建或关联外部 Issue 后，自动建立父子层级关系。

**执行步骤**：
1. 确定当前实体的上级：CR → 读取关联 PF，PF → 读取关联 BR，BR → 读取关联 Epic
2. 检查上级实体是否有外部关联（从 sync-mapping.md 关联记录或对应文件的"外部关联"字段查找）
3. 上级有外部关联 → 执行适配器"添加子 Issue"操作（child=当前实体外部编号，parent=上级外部编号）
4. 操作成功 → 在输出中附加 `(sub-issue of #{父编号})`
5. 操作失败（仓库未启用 sub-issue）→ 静默跳过，输出正常确认

**层级链传递**：仅建立直接父子关系，不递归。例如 CR 只与 PF 建立 sub-issue，不与 BR 或 Epic 建立。

**错误处理**：
- CR 已有外部关联 → 提示已关联，确认是否创建新工作项并覆盖
- 平台工具不可用 → 提示安装
- CR 不存在 → 提示用户
