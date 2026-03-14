# devpace 同步管理规则

> **职责**：定义 CR 状态变化时的外部同步行为。从 `devpace-rules.md §16` 拆分。条件生效：`sync-mapping.md` 存在时启用。

## §0 速查卡片

- 生效条件：`.devpace/integrations/sync-mapping.md` 存在
- 手动推送为主（MVP）：CR 状态转换后提醒推送，不自动执行外部操作
- 幂等操作：重复 push 同一状态不产生副作用
- 降级静默：gh CLI 不可用时报错提示，不阻断核心工作流

## §16 同步管理（条件生效）

> **核心**：CR 状态变化时提醒同步，手动 push 为主，不自动修改外部系统。

### 生效条件

`.devpace/integrations/sync-mapping.md` 存在时生效。不存在时整个 §16 静默跳过。

### 同步行为规则

1. **手动推送为主**（Phase 18 MVP）：CR **实际状态转换**后提醒推送（sync-push Hook 缓存比对，非每次写入触发），不自动执行外部操作
2. **关联管理**：`/pace-sync link` 建立 CR ↔ 外部实体 1:1 映射，记录在 CR 文件和 sync-mapping.md；省略外部 ID 时智能匹配标题
3. **创建与解除**：`/pace-sync create` 从 CR 创建外部工作项并自动关联；`/pace-sync unlink` 解除关联并清理映射记录
4. **状态映射**：推送时按 sync-mapping.md 状态映射表翻译 devpace 状态为外部标签/操作
5. **轻量 pull**：`/pace-sync pull` 查询外部状态并提示用户是否更新（不自动修改 devpace 状态，需用户确认且符合状态机规则）
6. **幂等操作**：重复 push 同一状态不产生副作用（标签已存在则跳过）
7. **降级静默**：gh CLI 不可用时 push 报错并提示安装，不阻断核心工作流
8. **副产物非前置三阶段**（渐进消除手动前置）：
   - pace-init 检测 git remote + gh auth 通过时，默认生成 sync 配置作为自然延伸（用户可拒绝）
   - CR 创建时提议创建外部 Issue（sync-mapping.md 存在时，自主级别分化）
   - merged 时自动推送（§11 第 7 步，post-cr-update Hook 指令 + sync-push Hook 安全网双层保障）
9. **提醒降噪**：同一会话中多次状态变更时，sync-push Hook 逐次提醒；Claude 可将多次提醒归纳为会话结束前的统一推送建议（如"本会话有 3 个 CR 状态变更待推送，建议 `/pace-sync push`"），减少高频迭代中的干扰

### 与现有规则的协调

- §2 推进模式状态转换后 → sync-push Hook 缓存比对检测实际转换，输出建议性提醒（advisory，不阻断）
- §11 merged 后连锁更新第 7 步 → post-cr-update Hook 输出指令性管道（含第 7 步外部同步），sync-push Hook 作为安全网双层保障
- §14 发布管理 → Release 同步（Phase 19）
- Gate 1/2/3 结果同步：Gate 完成后若 CR 有外部关联，自动推送结果（详见 sync-procedures-push-advanced.md §2）

### 适用范围更新

§16 加入 §14 的"条件生效"模式：目录/文件存在时自动生效，不存在时静默跳过。
