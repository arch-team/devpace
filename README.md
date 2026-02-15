# devpace

Claude Code 的开发节奏管理器——让人机协作下的产品迭代研发有序进行，即使需求在变。

基于价值驱动的概念模型，提供跨会话连续性、质量检查自动执行、需求变更有序处理。

## 快速开始

```bash
# 在任何项目中加载
claude --plugin-dir /path/to/devpace

# 初始化项目研发管理
/pace-init

# 查看项目状态
/pace-status

# 推进一个功能
/pace-advance <功能描述>
```

## Skills

| 命令 | 用途 |
|------|------|
| `/pace-init` | 初始化项目的 `.devpace/` 状态目录 + 项目 CLAUDE.md |
| `/pace-status` | 查看项目研发状态（支持多级粒度） |
| `/pace-advance` | 进入推进模式，开始或继续推进变更 |
| `/pace-review` | 生成 Review 摘要，等待人类审批 |
| `/pace-change` | 需求变更管理：影响分析 + 有序调整 |
| `/pace-retro` | 迭代回顾，生成度量仪表盘 |
| `/pace-guide` | 查阅 BizDevOps 方法论参考 |

## 核心理念

- **概念模型驱动**：业务需求 → 产品功能 → 变更请求，端到端可追溯
- **Claude 自治为主**：技术闭环自主推进，关键质量检查等待人类审批
- **零摩擦交互**：用户说自然语言，Claude 在背后维护结构化状态
- **变更韧性**：需求变更是一等公民，影响分析 + 有序调整，节奏不乱
- **Markdown 格式**：所有状态文件使用 Markdown，LLM 和人类都能直接读写

## 设计文档

详见 [docs/design/design.md](docs/design/design.md)。
