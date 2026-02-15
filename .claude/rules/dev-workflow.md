# devpace 开发工作流规则

> **职责**：定义开发 devpace 本身时 Claude 必须遵循的会话生命周期规则。覆盖会话启动、任务执行、质量检查、跨会话连续性和文档级联。

## §0 速查卡片

```
会话开始 → roadmap.md 当前任务 → 上游变更检测 → 1 句话报告 → 等指令
选任务   → roadmap 待做列表 → 加载关联文档 → 实现 → 质量检查 → 更新 roadmap
文档变更 → dev-cascade.md → 影响分析 → 级联更新 → 记录到变更记录
会话结束 → 更新 roadmap.md（任务状态 + 变更记录）→ 3 行摘要
中断恢复 → roadmap.md "当前任务"表 = 恢复点
权威链   → vision.md → design.md → requirements.md → roadmap.md
```

## §1 会话开始协议

1. 读 `docs/planning/roadmap.md` "当前任务"表，识别"进行中"和"待做"任务
2. 上游变更检测：对比 roadmap.md 变更记录最后日期与 vision.md / design.md / requirements.md 的 git 修改时间（`git log -1 --format=%ci <file>`）
   - 发现更新 → 提示："注意：[文件] 在上次会话后有变更，建议先评估影响"
   - 无变更 → 正常推进
3. 用 1 句话报告：当前进度 + 下一步建议
4. 等待用户指令

## §2 任务选取与准备

1. 从 roadmap.md "当前任务"表选取最高优先级的"待做"任务
2. 追溯关联链：任务 → 关联里程碑 → 对应 OBJ → design.md 相关章节 → requirements.md 相关场景/功能条目
3. 加载必要参考文档（仅加载本次任务所需的章节，不全量读取）
4. 更新任务状态为"🔄 进行中"

**参考加载表**（按任务类型）：

| 任务类型 | 必读 | 按需 |
|---------|------|------|
| Skill 开发 | design.md 对应 Phase 章节、requirements.md 对应 S/F 条目、相关 _schema/ | theory.md 对应章节 |
| Rules 更新 | design.md 对应章节、devpace-rules.md 已有规则 | requirements.md NF 条目 |
| Schema 修改 | design.md §3/§5 概念模型、现有 schema 文件 | 相关 Skill 的 SKILL.md |
| 模板更新 | 对应 schema、design.md 相关章节 | 现有模板文件 |

## §3 开发执行

1. 按 design.md 规格和 requirements.md 验收标准实现
2. 遵循开发守则（CLAUDE.md "开发守则"章节的 7 条）
3. 实现过程中若发现 design.md/requirements.md 有歧义或缺失，先提出问题，不自行猜测
4. 每完成一个有意义的工作单元，git commit（遵循 common.md 提交规范）

## §4 完成质量检查

任务完成前必须通过以下检查：

- [ ] 分层完整性：`grep -r "docs/\|\.claude/" rules/ skills/ knowledge/` 无输出
- [ ] plugin.json 同步：新增/删除 Skill 后已更新 `.claude-plugin/plugin.json`
- [ ] Schema 合规：产出文件符合 `knowledge/_schema/` 中的格式契约
- [ ] §0 速查卡片：新增/修改的 rules/ 和 _schema/ 文件有速查卡片
- [ ] 模板占位符：模板文件使用 `{{PLACEHOLDER}}` 标记
- [ ] Frontmatter 合规：Skill 的 SKILL.md 遵循 claude-code-forge 规范
- [ ] Skill 分拆：详细规则超 ~50 行时拆出 `*-procedures.md`
- [ ] 验收标准：对照 requirements.md 相关场景的验收标准检查

## §5 任务完成与更新

1. 更新 roadmap.md "当前任务"表：状态 → "✅ 完成"
2. 检查里程碑：若该里程碑所有任务完成，更新里程碑状态 → "✅ 完成"
3. 若实现过程中修改了设计文档，在 roadmap.md "变更记录"添加条目
4. 检查是否有新任务需要添加到 roadmap.md（实现中发现的额外工作）

## §6 会话结束协议

1. 更新 roadmap.md 所有进行中任务的状态
2. 若任务未完成：在"说明"列记录进度（格式："继续：[具体步骤]"）
3. 输出 3 行摘要：完成了什么 / 未完成什么 / 下次建议从哪开始
4. git commit（若有未提交变更）

## §7 跨会话连续性

- roadmap.md "当前任务"表 = 唯一恢复点，不需要额外状态文件
- "进行中"任务的"说明"列 = 中断点描述
- 下次会话 §1 读取 roadmap.md 即可定位继续点
- 若"说明"列为空但状态为"进行中"，先 `git log` 查看最近提交确认进度

## §8 文档级联处理

当检测到上游文档变更（§1 自动检测）或用户主动修改设计文档时：

读取 `dev-cascade.md` 执行完整的影响分析和级联更新流程。
