# devpace 战略差距评估

> **创建日期**：2026-02-19
> **触发**：vision.md → design.md → requirements.md → roadmap.md 全链路差距分析

## OBJ 状态总览

| OBJ | 目标 | 状态 | 差距 |
|-----|------|------|------|
| OBJ-1 | 跑通完整工作流 | done | — |
| OBJ-2 | 跨会话连续性 | done | — |
| OBJ-3 | 质量检查有效 | partial | V2.4 拦截效果待测 |
| OBJ-4 | 变更管理有价值 | partial | T10 待完成 |
| OBJ-5 | 优于手动方案 | pending | T13 待执行 |
| OBJ-6 | 渐进丰富自然 | pending | T14 待执行 |
| OBJ-7 | 可移植性 | partial | Phase 3 |
| OBJ-8 | 度量体系可用 | not_started | Phase 3 |
| OBJ-9 | 社区可用 | not_started | Phase 4 |
| OBJ-10 | 差异化卖点 | not_started | Phase 4 |

## 战略差距

### P0 — 可靠性（Critical）

| ID | 标题 | 详情 |
|----|------|------|
| P0-1 | 实现关键 Hooks | SessionStart 读 state.md；Stop 提醒保存。Hooks 是确定性的，不依赖 LLM 判断 |
| P0-2 | 状态文件自愈 | 读取时校验必填 section、状态值合法性、CR 字段完整性。人类可手动编辑 .devpace/，必须容错 |
| P0-3 | 外部端到端验证 | 非开发者在陌生项目上从 /pace-init 到完成 2-3 个 CR |

### P1 — 用户体验（Important）

| ID | 标题 | 详情 |
|----|------|------|
| P1-1 | 用户指南 | 5 分钟上手 + 核心概念 + 场景走查 + FAQ |
| P1-2 | 首次体验打磨 | /pace-init Step 2 精简为 3 步必填 + 2 步延后 |
| P1-3 | 健康检查 | /pace-status 增加 state.md↔CR 一致性检查 |
| P1-4 | LICENSE 文件 | 创建 MIT LICENSE，plugin.json 声明但无实际文件 |
| P1-5 | marketplace.json 生产化 | 名称/描述改为正式版 |
| P1-6 | CHANGELOG | Keep a Changelog 格式 |

### P2 — 产品信任（Recommended）

| ID | 标题 | 详情 |
|----|------|------|
| P2-1 | 完成 Phase 2 验证 | T10 + T13 + T14 |
| P2-2 | 度量体系落地 | /pace-retro 实际可运行 |
| P2-3 | 示例项目 + CONTRIBUTING.md | 完整 .devpace/ 快照 + 贡献指南 |

## 战略问题

1. **LLM 遵从率**：关键路径 < 90% → 必须 Hooks 加固
2. **护城河**：跨会话连续性可能被原生替代，变更管理独立入口就绪？
3. **用户群体**：多会话多 CR 场景才有价值，需明确适用边界
4. **版本兼容**：state.md 加 devpace-version 字段

## 实施顺序

### Phase 2（当前）

P1-4 LICENSE → P0-1 Hooks → P0-2 自愈 → P1-1 用户指南 → T10/T13/T14 → P1-5/P1-6 分发元数据

### Phase 3

P2-2 度量 → P1-2 首次体验 → P1-3 健康检查

### Phase 4

P2-3 示例项目 → 社区发布

## 结论

devpace 设计和代码都做好了，距离成功还差：可靠性保证（Hooks+容错）、真实用户验证、降低新用户门槛。**可靠性最关键。**
