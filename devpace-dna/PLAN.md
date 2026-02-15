# devpace-dna：将方法论写入项目 DNA

## 问题

devpace 的行为协议 `rules/devpace-rules.md` 通过插件机制自动注入，已解决了"怎么做"的问题。但方法论（"怎么想"）没有落地到项目自身——当插件未加载时，项目不携带任何方法论上下文。

## 核心洞察

**方法论应跟着项目走，不跟着用户走。**

- 用户级 `~/.claude/` 是个人偏好和通用工程原则（SOLID、DRY），不应承载领域方法论
- 项目级 `CLAUDE.md` 是项目的 DNA——clone 项目的人自动获得方法论上下文
- `/pace-init` 是写入 DNA 的自然时机——初始化时一次性植入

## 方案

### 修改 /pace-init 流程

在现有 Step 3（生成 .devpace/ 目录）之后，新增 Step 3.5：

**Step 3.5：写入项目 CLAUDE.md**

1. 检查项目根目录是否存在 `CLAUDE.md`
2. 存在 → 读取现有内容，在末尾追加 devpace 方法论区块
3. 不存在 → 从模板创建，包含项目信息 + 方法论区块
4. 方法论区块内容来自新模板 `knowledge/_templates/claude-md-devpace.md`

### 新增模板文件

`knowledge/_templates/claude-md-devpace.md`

这是 /pace-init 写入项目 CLAUDE.md 的模板，包含：
- 项目定位（来自用户输入）
- 研发协作方法论原则（精炼版，~30 行）
- .devpace/ 目录说明
- 开发模式指引（探索 vs 推进）

### 修改 pace-init SKILL.md

在流程中添加 Step 3.5 的描述，让 Claude 知道初始化时需要写入 CLAUDE.md。

## 文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `devpace-dna/PLAN.md` | 本文件 | 方案说明 |
| `devpace-dna/PRINCIPLES_COLLAB.md` | 保留 | 完整版原则（参考文档） |
| `devpace-dna/MODE_DevPace.md` | 保留 | 完整版行为模式（参考文档） |
| `knowledge/_templates/claude-md-devpace.md` | **新建** | 项目 CLAUDE.md 的 devpace 区块模板 |
| `skills/pace-init/SKILL.md` | **修改** | 添加 Step 3.5 |

## 效果

```
/pace-init 执行后，目标项目获得：

target-project/
├── CLAUDE.md                    ← 携带方法论 DNA（新增/追加）
└── .devpace/
    ├── state.md
    ├── project.md
    ├── backlog/
    ├── iterations/current.md
    ├── rules/
    │   ├── workflow.md
    │   └── checks.md
    └── metrics/dashboard.md

任何人 clone 这个项目：
  → CLAUDE.md 自动加载方法论原则
  → 加载 devpace 插件后，rules/ 自动注入操作规程
  → 两层组合 = 完整 DNA
```

## 验证

1. 在测试项目运行 /pace-init → 确认 CLAUDE.md 被创建/追加
2. 新会话打开该项目（不加载插件）→ 确认 Claude 用价值链思维工作
3. 新会话加载插件 → 确认完整 devpace 流程可用
4. 已有 CLAUDE.md 的项目运行 /pace-init → 确认追加而非覆盖
