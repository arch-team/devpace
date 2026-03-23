# 技术约定文件格式契约

> **职责**：定义 context.md 的结构。/pace-init 创建和 Claude 更新时遵循此格式。

## §0 速查卡片

```
context.md 是项目的技术约定备忘录
核心原则：只记录 Claude 不会自动推断的非显而易见规则
与 project.md 互补：project.md = 业务全景，context.md = 技术约定
完整版包含：技术栈 + 编码规范 + 项目约定 + 架构约束
最小版（自动检测）：仅技术栈 + 已检测到的约定（< 3 条则跳过创建）
增长方式：init 时自动检测 + 开发过程中自然积累
不记录：语言默认行为、框架标准用法、IDE 能推断的设置
```

## 与 project.md 的关系

| 维度 | project.md | context.md |
|------|-----------|------------|
| 关注点 | 业务目标、价值链、功能规格 | 技术栈、编码规范、架构约束 |
| 消费场景 | 理解"做什么"和"为什么" | 理解"怎么写代码"和"遵守什么规则" |
| 主要读者 | 业务理解、需求追溯 | 代码生成、Review 判断 |
| 更新频率 | 随业务演进 | 随技术决策积累 |

两个文件不重叠：project.md 的"项目原则"侧重产品/业务级决策（如"优先移动端体验"），context.md 侧重技术实现级约定（如"API 前缀统一用 /api/v2"）。

## 最小状态（自动检测生成）

`/pace-init` 时 Claude 扫描项目代码库自动检测技术栈和约定。检测到的约定 < 3 条时跳过创建。

```markdown
# 技术约定

> [项目名称] 的技术约定 — 仅记录非显而易见的规则

## 技术栈

- 运行时：[检测到的运行时和版本]
- 框架：[检测到的框架]
- 测试：[检测到的测试框架]

## 编码规范

[从 linter/formatter 配置中提取的规则]

## 项目约定

[从代码采样中提取的模式]

## 架构约束

（随开发自然积累 — 发现重要约束时由 Claude 或用户添加）
```

## 完整内容

### 1. 头部标题和 blockquote 定位

```markdown
# 技术约定

> [项目名称] 的技术约定 — 仅记录非显而易见的规则
```

### 2. 技术栈

```markdown
## 技术栈

- 运行时：Node.js 20 + TypeScript 5
- 框架：NestJS 10
- 测试：Jest + Supertest
- 数据库：PostgreSQL 15
- 部署：Docker + AWS ECS
```

记录项目使用的核心技术和版本。仅列出主要技术栈，不罗列所有依赖。

### 3. 编码规范

```markdown
## 编码规范

- 命名：camelCase（变量/函数）、PascalCase（类/接口/类型）、UPPER_SNAKE_CASE（常量）
- 文件命名：kebab-case（`user-service.ts`）
- 缩进：2 空格（TypeScript）、4 空格（Python）
- 字符串：单引号（JS/TS）
- 分号：不使用（Prettier 配置）
```

记录命名风格、格式化偏好等 Claude 在生成代码时需要遵守的约定。不记录语言默认行为（如 Python 用 snake_case），只记录项目特定选择。

### 4. 项目约定

```markdown
## 项目约定

- API 前缀：`/api/v2`
- 所有新组件必须是函数组件（禁止 class 组件）
- 错误码格式：`ERR_[MODULE]_[CODE]`（如 `ERR_AUTH_001`）
- 日志格式：结构化 JSON（通过 winston）
- 环境变量前缀：`APP_`
```

记录项目级的编码习惯和约定——这些是 Claude 不看代码库就无法推断的规则。

### 5. 架构约束

```markdown
## 架构约束

- 不使用 ORM，直接写 SQL（使用 knex query builder）
- 数据库迁移必须可回滚（每个 up 必须有对应 down）
- 所有外部 API 调用必须经过统一的 HTTP client（`libs/http-client.ts`）
- 前端状态管理仅用 React Context，不引入 Redux/Zustand
```

记录架构级的技术决策和限制——通常来自项目早期的关键决策，违反会导致架构一致性问题。

## 精简原则

context.md 遵循"非显而易见"原则，以下内容**不应**记录：

| 不记录 | 原因 | 示例 |
|--------|------|------|
| 语言默认惯例 | Claude 已知 | Python 用 snake_case |
| 框架标准用法 | 框架文档已覆盖 | React 用 JSX |
| package.json 中可见的依赖 | Claude 会直接读取 | "项目使用 Express" |
| IDE/编辑器配置 | .editorconfig 已声明 | 缩进用 tab 还是 space（如已有 .editorconfig） |
| 通用最佳实践 | Claude 默认遵循 | "函数应该短小" |

**记录标准**：如果删除某条约定，Claude 在生成代码时有 >50% 概率猜错，则应该记录。

## 更新时机

| 时机 | 动作 | 触发者 |
|------|------|--------|
| `/pace-init` | 自动检测技术栈和约定生成初始内容 | pace-init Skill |
| 技术约定讨论 | 将确认的约定追加到对应 section | Claude 自动 |
| Code Review 发现不一致 | 将纠正的规则补充到 context.md | Claude 或用户 |
| 技术栈升级 | 更新版本号和相关约定 | 用户主动 |
| 架构决策变更 | 更新架构约束 section | 用户主动 |

## 容错规则

- **文件不存在**：context.md 完全可选，不存在时 Claude 正常工作（不报错、不提示创建）
- **section 缺失**：缺少任何 section 时跳过该维度，不补充空桩
- **格式损坏**：人类手动编辑可能引入格式不一致，读取时忽略格式差异，只关注语义内容
- **过时内容**：当发现 context.md 中的约定与实际代码不符时，提示用户确认是否更新
