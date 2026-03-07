# devpace-cadence — BizDevOps 研发节奏可视化平台设计方案

> **状态**：已规划，待实施
> **创建日期**：2026-03-06
> **目标仓库**：独立仓库 `devpace-cadence/`

## Context

devpace 是一个 Claude Code 插件，覆盖 BizDevOps 全生命周期。用户在使用 devpace 开发软件项目时，会在项目目录的 `.devpace/` 下生成完整的研发活动追踪 Markdown 文件（BR→PF→CR→Release 价值链、迭代规划、质量门禁、风险管理、知识库等）。

**问题**：`.devpace/` 数据分散在多个 Markdown 文件中，团队成员（PM/QA/管理层）难以直观理解项目全貌、价值链流转和研发健康度。

**目标**：构建一个 Web 应用，从 Git 仓库拉取 `.devpace/` 数据，解析后提供多视图可视化——价值链追溯图、看板、仪表盘——让全团队无需阅读 Markdown 即可掌握研发全局。

**决策摘要**：

| 维度 | 决定 |
|------|------|
| 用户 | 全团队（开发/PM/QA），角色视图 |
| 部署 | Web 应用（独立仓库） |
| 数据源 | Git 仓库拉取 .devpace 目录 |
| 范围 | 多项目支持 |
| 核心视图 | 价值链图 + 看板 + 仪表盘 |
| 数据权限 | 只读可视化（MVP） |
| 认证 | 基础用户认证 + 角色 |
| 技术栈 | Next.js 全栈（TypeScript 统一） |

---

## 1. 系统架构

```
┌──────────────────────────────────────────────────────┐
│                     Browser                           │
│  ┌───────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Value Chain│  │  Kanban  │  │    Dashboard      │  │
│  │ (ReactFlow)│  │          │  │   (Recharts)      │  │
│  └───────────┘  └──────────┘  └───────────────────┘  │
└─────────────────────┬────────────────────────────────┘
                      │ HTTPS
┌─────────────────────▼────────────────────────────────┐
│                Next.js App Router                     │
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │   Pages /    │  │  API Routes │  │  NextAuth.js │ │
│  │   Layouts    │  │  /api/*     │  │              │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────────┘ │
│         │                │                            │
│  ┌──────▼────────────────▼───────────────────────┐   │
│  │              Service Layer                     │   │
│  │  ┌───────────┐ ┌───────────┐ ┌─────────────┐  │   │
│  │  │  Parser   │ │ Git Sync  │ │   Query     │  │   │
│  │  │  Service  │ │  Service  │ │   Engine    │  │   │
│  │  └───────────┘ └───────────┘ └─────────────┘  │   │
│  └───────────────────┬───────────────────────────┘   │
└──────────────────────┬───────────────────────────────┘
                       │
          ┌────────────▼─────────────┐
          │       PostgreSQL         │
          │  (parsed structured data)│
          └────────────┬─────────────┘
                       │
     ┌─────────────────▼───────────────────┐
     │   Git Repos (cloned to server)      │
     │  ┌──────┐  ┌──────┐  ┌──────┐      │
     │  │Proj A│  │Proj B│  │Proj C│      │
     │  └──────┘  └──────┘  └──────┘      │
     └─────────────────────────────────────┘
```

**数据流**：
1. 用户在 Web UI 添加 Git 仓库 URL
2. Git Sync Service clone 仓库到服务器本地存储
3. 定时 pull（可配 Webhook 实时触发）检测 `.devpace/` 变更
4. Parser Service 增量解析变更的 Markdown 文件 → 结构化数据
5. 写入 PostgreSQL（实体表 + 关系表）
6. 前端通过 API 查询展示

---

## 2. 数据模型（PostgreSQL）

### 2.1 核心实体表

```sql
-- 项目（对应一个 Git 仓库的 .devpace）
CREATE TABLE projects (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  repo_url      TEXT NOT NULL UNIQUE,
  local_path    TEXT,              -- 服务器上 clone 的路径
  default_branch TEXT DEFAULT 'main',
  last_synced_at TIMESTAMPTZ,
  sync_status   TEXT DEFAULT 'pending', -- pending/syncing/synced/error
  devpace_version TEXT,            -- 从 state.md 提取
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- 业务目标
CREATE TABLE objectives (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
  obj_id      TEXT NOT NULL,       -- OBJ-1, OBJ-2
  title       TEXT NOT NULL,
  description TEXT,
  UNIQUE(project_id, obj_id)
);

-- 业务需求
CREATE TABLE business_requirements (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id   UUID REFERENCES projects(id) ON DELETE CASCADE,
  objective_id UUID REFERENCES objectives(id),
  br_id        TEXT NOT NULL,      -- BR-001
  title        TEXT NOT NULL,
  source       TEXT,               -- user/claude
  UNIQUE(project_id, br_id)
);

-- 产品功能
CREATE TABLE product_functions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
  br_id       UUID REFERENCES business_requirements(id),
  pf_id       TEXT NOT NULL,       -- PF-001
  title       TEXT NOT NULL,
  status      TEXT,                -- computed from CRs
  source      TEXT,
  has_overflow BOOLEAN DEFAULT false, -- 是否有 features/PF-xxx.md
  UNIQUE(project_id, pf_id)
);

-- 变更请求（核心工作项）
CREATE TABLE change_requests (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      UUID REFERENCES projects(id) ON DELETE CASCADE,
  pf_id           UUID REFERENCES product_functions(id),
  cr_id           TEXT NOT NULL,       -- CR-001
  title           TEXT NOT NULL,
  type            TEXT DEFAULT 'feature', -- feature/defect/hotfix
  severity        TEXT,                -- critical/major/minor/trivial
  status          TEXT NOT NULL,       -- created/developing/verifying/in_review/approved/merged/released/paused
  complexity      TEXT,                -- S/M/L/XL
  branch          TEXT,
  application     TEXT,
  linked_release  TEXT,                -- REL-xxx
  external_link   TEXT,
  intent_summary  TEXT,                -- 意图摘要
  acceptance_criteria JSONB,           -- 验收条件列表
  created_at      TIMESTAMPTZ,
  updated_at      TIMESTAMPTZ,
  UNIQUE(project_id, cr_id)
);

-- CR 关系（blocks/follows/relates-to）
CREATE TABLE cr_relations (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
  from_cr_id  UUID REFERENCES change_requests(id),
  to_cr_id    UUID REFERENCES change_requests(id),
  relation    TEXT NOT NULL,       -- blocks/follows/relates-to
  UNIQUE(from_cr_id, to_cr_id, relation)
);

-- CR 事件日志
CREATE TABLE cr_events (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cr_id       UUID REFERENCES change_requests(id) ON DELETE CASCADE,
  event_date  DATE,
  event       TEXT NOT NULL,        -- created->developing, [checkpoint: gate1-passed]
  operator    TEXT,                  -- Claude/User/System
  notes       TEXT,
  handoff     TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- 发布
CREATE TABLE releases (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id   UUID REFERENCES projects(id) ON DELETE CASCADE,
  rel_id       TEXT NOT NULL,       -- REL-001
  version      TEXT,
  status       TEXT NOT NULL,       -- staging/deployed/verified/closed/rolled_back
  created_date DATE,
  target_env   TEXT,
  changelog    TEXT,
  release_notes TEXT,
  UNIQUE(project_id, rel_id)
);

-- 发布包含的 CR
CREATE TABLE release_changes (
  release_id UUID REFERENCES releases(id) ON DELETE CASCADE,
  cr_id      UUID REFERENCES change_requests(id),
  PRIMARY KEY (release_id, cr_id)
);

-- 迭代
CREATE TABLE iterations (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
  iter_id     TEXT NOT NULL,        -- Iter-1
  goal        TEXT,
  start_date  DATE,
  end_date    DATE,
  is_current  BOOLEAN DEFAULT false,
  planned_pf_count INT,
  actual_pf_count INT,
  change_count INT DEFAULT 0,
  defect_cr_count INT DEFAULT 0,
  retrospective JSONB,             -- 回顾数据
  UNIQUE(project_id, iter_id)
);

-- 迭代-PF 关联
CREATE TABLE iteration_pfs (
  iteration_id UUID REFERENCES iterations(id) ON DELETE CASCADE,
  pf_id        UUID REFERENCES product_functions(id),
  priority     TEXT,                -- P0/P1/P2
  status       TEXT,                -- emoji mapped to text
  cr_total     INT DEFAULT 0,
  cr_completed INT DEFAULT 0,
  linked_release TEXT,
  PRIMARY KEY (iteration_id, pf_id)
);

-- 风险
CREATE TABLE risks (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id   UUID REFERENCES projects(id) ON DELETE CASCADE,
  risk_id      TEXT NOT NULL,       -- RISK-001
  source       TEXT,                -- pre-flight/runtime/retrospective/external
  severity     TEXT NOT NULL,       -- Low/Medium/High
  status       TEXT NOT NULL,       -- open/mitigated/accepted/resolved
  description  TEXT,
  discovery_date DATE,
  UNIQUE(project_id, risk_id)
);

-- 风险-CR 关联
CREATE TABLE risk_crs (
  risk_id UUID REFERENCES risks(id) ON DELETE CASCADE,
  cr_id   UUID REFERENCES change_requests(id),
  PRIMARY KEY (risk_id, cr_id)
);

-- 反馈
CREATE TABLE feedbacks (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id   UUID REFERENCES projects(id) ON DELETE CASCADE,
  fb_id        TEXT NOT NULL,       -- FB-001
  category     TEXT,
  severity     TEXT,
  status       TEXT,
  linked_cr    TEXT,
  report_date  DATE,
  description  TEXT,
  impact       TEXT,
  UNIQUE(project_id, fb_id)
);

-- 知识库洞察
CREATE TABLE insights (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      UUID REFERENCES projects(id) ON DELETE CASCADE,
  title           TEXT NOT NULL,
  type            TEXT NOT NULL,     -- pattern/defense/improvement/preference
  source          TEXT,
  tags            TEXT[],
  description     TEXT,
  confidence      FLOAT,
  last_referenced DATE,
  verification_count INT DEFAULT 0,
  status          TEXT DEFAULT 'Active', -- Active/Dormant/Archived
  conflict_pair   TEXT,
  created_date    DATE
);

-- 指标快照（每次同步时从 dashboard.md 解析）
CREATE TABLE metric_snapshots (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
  iteration   TEXT,
  metrics     JSONB NOT NULL,       -- 完整指标数据
  captured_at TIMESTAMPTZ DEFAULT now()
);
```

### 2.2 用户与权限

```sql
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       TEXT NOT NULL UNIQUE,
  name        TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role        TEXT DEFAULT 'member',  -- admin/member/viewer
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE project_members (
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
  role       TEXT DEFAULT 'member',   -- admin/member/viewer
  PRIMARY KEY (project_id, user_id)
);
```

---

## 3. Parser Service 设计

### 3.1 解析策略

每个 `.devpace/` 文件类型对应一个专用 Parser：

| 文件 | Parser | 提取内容 |
|------|--------|---------|
| `state.md` | StateParser | 项目状态快照、devpace 版本、taught 标记 |
| `project.md` | ProjectParser | OBJ/BR/PF/CR 价值树、配置、scope |
| `backlog/CR-xxx.md` | CRParser | CR 元数据、意图、执行计划、事件日志、质量检查 |
| `iterations/*.md` | IterationParser | 迭代目标/日期、PF 表、偏差快照、回顾 |
| `releases/REL-xxx.md` | ReleaseParser | 发布元数据、包含 CR、部署日志、changelog |
| `metrics/dashboard.md` | MetricsParser | 指标键值对 |
| `metrics/insights.md` | InsightsParser | 知识条目 |
| `risks/RISK-xxx.md` | RiskParser | 风险元数据、缓解方案 |
| `feedback-log.md` | FeedbackParser | 反馈条目 |
| `features/PF-xxx.md` | PFOverflowParser | PF 溢出详情 |
| `rules/checks.md` | ChecksParser | 质量门定义 |
| `rules/workflow.md` | WorkflowParser | 状态机定义 |
| `integrations/*.md` | IntegrationParser | 同步配置和映射 |

### 3.2 解析方法

采用**正则 + 结构化模式匹配**的轻量方案（不依赖通用 Markdown AST）：

```typescript
// 核心解析工具函数
interface ParseContext {
  projectId: string;
  filePath: string;
  content: string;
}

// 元数据解析：提取 key: value 格式的头部字段
function parseMetadata(content: string): Record<string, string>;

// 表格解析：提取 Markdown 表格为对象数组
function parseTable(content: string, sectionHeader: string): Record<string, string>[];

// 价值树解析：递归解析嵌套列表（OBJ > BR > PF > CR）
function parseValueTree(content: string): ValueTreeNode[];

// 事件日志解析
function parseEventTable(content: string): CREvent[];

// Section 提取：按 ## 标题分割内容
function extractSection(content: string, heading: string): string;
```

### 3.3 增量解析

```typescript
// Git diff 检测变更文件
async function detectChanges(repoPath: string, lastCommit: string): Promise<ChangedFile[]>;

// 只解析变更的文件，不全量重扫
async function incrementalParse(project: Project, changedFiles: ChangedFile[]): Promise<void> {
  for (const file of changedFiles) {
    const parser = getParserForFile(file.path);
    if (parser) {
      const content = await readFile(file.fullPath);
      await parser.parse({ projectId: project.id, filePath: file.path, content });
    }
  }
}
```

---

## 4. Git Sync Service

```typescript
interface GitSyncService {
  // 添加新项目仓库
  addRepository(url: string, branch?: string): Promise<Project>;

  // 首次 clone
  cloneRepository(project: Project): Promise<void>;

  // 增量同步（git pull + detect changes + incremental parse）
  syncRepository(project: Project): Promise<SyncResult>;

  // 定时轮询（默认 5 分钟间隔，可配置）
  startPolling(projectId: string, intervalMs?: number): void;

  // Webhook 触发同步
  handleWebhook(payload: WebhookPayload): Promise<void>;
}
```

**同步流程**：
1. `git pull --ff-only` 获取最新代码
2. `git diff --name-only <lastSyncCommit>..HEAD -- .devpace/` 获取变更文件列表
3. 按文件类型分发到对应 Parser
4. 更新 `projects.last_synced_at` 和 `projects.sync_status`
5. 记录 `lastSyncCommit` 供下次增量使用

**存储位置**：`/data/repos/<project-id>/`（Docker volume）

---

## 5. 核心视图设计

### 5.1 价值链追溯图（Value Chain Graph）

**库**：React Flow（`@xyflow/react`）

**布局**：分层树形图，从左到右流动：

```
OBJ-1 ──→ BR-001 ──→ PF-001 ──→ CR-001 ──→ REL-001
                              ├─→ CR-002
                              └─→ CR-003
                  ├─→ PF-002 ──→ CR-004
          BR-002 ──→ PF-003 ──→ CR-005
```

**节点设计**：

| 节点类型 | 颜色 | 显示信息 | 点击展开 |
|---------|------|---------|---------|
| OBJ | 紫色 | ID + 标题 | MoS 列表 |
| BR | 蓝色 | ID + 标题 | 描述 |
| PF | 绿色 | ID + 标题 + 状态 | CR 列表、验收条件 |
| CR | 状态色 | ID + 标题 + 状态 badge | 完整详情（意图/事件/检查） |
| Release | 橙色 | ID + 版本 + 状态 | 包含 CR、changelog |
| Risk | 红色 | ID + 严重度 | 详情、关联 CR |

**CR 状态色映射**：

| 状态 | 颜色 |
|------|------|
| created | 灰色 |
| developing | 蓝色 |
| verifying | 青色 |
| in_review | 黄色 |
| approved | 浅绿 |
| merged | 绿色 |
| released | 深绿 |
| paused | 橘色 |

**交互**：
- 点击节点展开详情面板（右侧 drawer）
- 高亮上下游链路（hover 时）
- 过滤器：按状态、按迭代、按 Release
- 缩放/平移/小地图

### 5.2 研发活动看板（Kanban Board）

**列（CR 状态流转）**：

```
Created → Developing → Verifying → In Review → Approved → Merged → Released
                                                                 ↕
                                                              Paused
```

**卡片内容**：
- CR ID + 标题
- 类型 badge（feature/defect/hotfix）
- 复杂度 badge（S/M/L/XL）
- 关联 PF 标签
- 最后事件时间
- 停留时长（当前状态已持续的天数）

**过滤/分组**：
- 按项目
- 按迭代
- 按 PF 分组
- 按类型（feature/defect/hotfix）
- 按复杂度

### 5.3 全景仪表盘（Dashboard）

**布局**：响应式网格，分区展示：

**区域 1：项目概览**
- 活跃项目数、总 CR 数、状态分布饼图
- 当前迭代进度条（已完成 PF / 总 PF）

**区域 2：DORA 指标（代理值）**
- 部署频率、变更前置时间、变更失败率、MTTR
- 四级评级可视化（Elite/High/Medium/Low）
- 趋势折线图（跨迭代）

**区域 3：质量门健康**
- Gate 首次通过率
- 人类拒绝率
- 缺陷逃逸率
- 柱状图对比

**区域 4：迭代速度**
- 迭代速度（实际/计划 PF）
- 平均 CR 周期时间
- 规划准确率
- 偏差快照

**区域 5：价值交付**
- MoS 达成率
- 价值链完整性
- 需求交付周期

**区域 6：风险与变更**
- 活跃风险数量（按严重度）
- 变更频率趋势
- 变更类型分布

**区域 7：知识库**
- 活跃/休眠/归档洞察统计
- 平均置信度
- 最近引用的洞察

**图表库**：Recharts（与 React 生态无缝集成）

---

## 6. API 设计

### 6.1 核心 API Routes

```
# 项目管理
POST   /api/projects                    添加项目（Git URL）
GET    /api/projects                    项目列表
GET    /api/projects/:id                项目详情
POST   /api/projects/:id/sync           触发手动同步
DELETE /api/projects/:id                删除项目

# 价值链
GET    /api/projects/:id/value-chain    完整价值链树（OBJ→BR→PF→CR→Release）
GET    /api/projects/:id/value-chain?depth=pf  截断到 PF 层级

# CR
GET    /api/projects/:id/crs            CR 列表（支持状态/类型/迭代过滤）
GET    /api/projects/:id/crs/:crId      CR 详情（含事件日志）
GET    /api/projects/:id/crs/:crId/events  CR 事件时间线

# 迭代
GET    /api/projects/:id/iterations              迭代列表
GET    /api/projects/:id/iterations/current       当前迭代
GET    /api/projects/:id/iterations/:iterId       迭代详情

# 发布
GET    /api/projects/:id/releases       发布列表
GET    /api/projects/:id/releases/:relId  发布详情

# 指标
GET    /api/projects/:id/metrics                 最新指标快照
GET    /api/projects/:id/metrics/trend            指标趋势（跨迭代）

# 风险
GET    /api/projects/:id/risks          风险列表

# 知识库
GET    /api/projects/:id/insights       知识条目列表

# Webhook
POST   /api/webhooks/github             GitHub push webhook
POST   /api/webhooks/gitlab             GitLab push webhook

# 认证
POST   /api/auth/login
POST   /api/auth/register
GET    /api/auth/me
```

### 6.2 查询参数规范

```
# 通用分页
?page=1&limit=20

# CR 过滤
?status=developing,in_review
?type=feature
?iteration=Iter-2
?pf=PF-001
?complexity=L,XL

# 指标趋势
?from=Iter-1&to=Iter-3
```

---

## 7. 认证与角色

**方案**：NextAuth.js + Credentials Provider（MVP）

**角色**：

| 角色 | 权限 |
|------|------|
| admin | 管理项目、管理用户、查看所有数据 |
| member | 查看已加入项目的所有数据 |
| viewer | 查看已加入项目的仪表盘和高层概览（不可看 CR 详情） |

---

## 8. 技术栈详细

| 层次 | 技术 | 版本 |
|------|------|------|
| **框架** | Next.js (App Router) | 15.x |
| **语言** | TypeScript | 5.x |
| **ORM** | Prisma | 6.x |
| **数据库** | PostgreSQL | 16 |
| **认证** | NextAuth.js | 5.x |
| **可视化-图** | @xyflow/react (React Flow) | 12.x |
| **可视化-图表** | Recharts | 2.x |
| **UI 组件** | shadcn/ui + Tailwind CSS | latest |
| **Git 操作** | simple-git | 3.x |
| **Markdown 解析** | 自研正则 Parser（devpace 格式特化） | - |
| **部署** | Docker Compose | - |

---

## 9. 项目结构

```
devpace-cadence/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (auth)/                   # 认证页面组
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── (dashboard)/              # 主应用布局组
│   │   │   ├── layout.tsx            # 侧边栏 + 顶栏
│   │   │   ├── page.tsx              # 项目列表首页
│   │   │   └── projects/
│   │   │       └── [id]/
│   │   │           ├── page.tsx            # 项目概览
│   │   │           ├── value-chain/page.tsx # 价值链图
│   │   │           ├── kanban/page.tsx      # 看板
│   │   │           ├── dashboard/page.tsx   # 仪表盘
│   │   │           ├── iterations/page.tsx  # 迭代列表
│   │   │           ├── releases/page.tsx    # 发布列表
│   │   │           ├── risks/page.tsx       # 风险
│   │   │           └── insights/page.tsx    # 知识库
│   │   └── api/                      # API Routes
│   │       ├── projects/
│   │       ├── webhooks/
│   │       └── auth/
│   ├── components/
│   │   ├── value-chain/              # 价值链图组件
│   │   │   ├── ValueChainGraph.tsx
│   │   │   ├── nodes/                # 自定义节点（OBJ/BR/PF/CR/Release）
│   │   │   └── DetailDrawer.tsx
│   │   ├── kanban/                   # 看板组件
│   │   │   ├── KanbanBoard.tsx
│   │   │   ├── KanbanColumn.tsx
│   │   │   └── CRCard.tsx
│   │   ├── dashboard/                # 仪表盘组件
│   │   │   ├── DORAMetrics.tsx
│   │   │   ├── QualityGates.tsx
│   │   │   ├── IterationVelocity.tsx
│   │   │   └── ValueDelivery.tsx
│   │   └── ui/                       # shadcn/ui 组件
│   ├── lib/
│   │   ├── parsers/                  # .devpace Markdown 解析器
│   │   │   ├── state-parser.ts
│   │   │   ├── project-parser.ts
│   │   │   ├── cr-parser.ts
│   │   │   ├── iteration-parser.ts
│   │   │   ├── release-parser.ts
│   │   │   ├── metrics-parser.ts
│   │   │   ├── insights-parser.ts
│   │   │   ├── risk-parser.ts
│   │   │   ├── feedback-parser.ts
│   │   │   └── utils.ts              # 共用解析工具
│   │   ├── git/                      # Git 操作
│   │   │   ├── sync-service.ts
│   │   │   └── webhook-handler.ts
│   │   ├── db/                       # 数据库
│   │   │   └── prisma.ts
│   │   └── auth/                     # 认证配置
│   │       └── auth-options.ts
│   └── types/                        # TypeScript 类型定义
│       ├── devpace.ts                # devpace 实体类型
│       └── api.ts                    # API 请求/响应类型
├── prisma/
│   ├── schema.prisma                 # Prisma schema
│   └── migrations/
├── docker-compose.yml                # PostgreSQL + App
├── Dockerfile
├── package.json
├── tsconfig.json
└── tailwind.config.ts
```

---

## 10. 实现里程碑

### M1：基础骨架（Week 1）
- Next.js 项目初始化 + Prisma + PostgreSQL
- NextAuth.js 认证
- 项目管理 CRUD（添加 Git 仓库）
- Git clone + 基础同步

### M2：Parser 核心（Week 2）
- state-parser + project-parser（价值树）
- cr-parser（元数据 + 事件）
- 增量解析机制

### M3：价值链图（Week 3）
- React Flow 集成
- 自定义节点（OBJ/BR/PF/CR/Release）
- 详情 Drawer
- 交互（高亮链路、过滤）

### M4：看板 + 仪表盘（Week 4）
- Kanban Board（CR 状态列）
- 仪表盘区域 1-4（概览 + DORA + 质量 + 速度）

### M5：完善（Week 5）
- 剩余 Parser（iteration/release/risk/feedback/insights）
- 仪表盘区域 5-7
- Webhook 实时同步
- 多项目切换
- 部署 Docker Compose

---

## 11. 验证方案

### 功能验证
1. **Parser 单元测试**：对每种 Parser 用 `.devpace/` 样例数据编写测试，验证解析结果与预期结构一致
2. **端到端验证**：用真实 `.devpace/` 数据作为测试数据，验证完整流程（clone → parse → 展示）
3. **价值链完整性**：验证 OBJ→BR→PF→CR→Release 链路无断链

### 可视化验证
1. 价值链图：节点数量与 project.md 树一致，边关系正确
2. 看板：CR 卡片在正确的状态列中，总数与 backlog/ 文件数一致
3. 仪表盘：指标数值与 dashboard.md 原始数据一致

### 同步验证
1. 修改 `.devpace/` 中某个 CR 的状态 → git push → 验证 Web 端同步更新
2. 新增 CR 文件 → 验证自动识别并解析

### 测试命令
```bash
# 单元测试
npm test

# 端到端测试
npm run test:e2e

# 开发环境启动
docker compose up -d db
npm run dev

# 生产部署
docker compose up -d
```

---

## 12. 实施说明

### 并行化策略

实施时推荐以下并行工作流：

| 工作流 | 内容 | 依赖 |
|--------|------|------|
| Stream 1 | 项目骨架 + Prisma schema + Auth + Docker | 无 |
| Stream 2 | Parser 服务（全部 Parser） | 依赖 devpace schema 定义（已有） |
| Stream 3 | 前端组件（Value Chain + Kanban + Dashboard） | 依赖 Stream 1 骨架 |
| Stream 4 | API Routes | 依赖 Stream 1 Prisma schema |
| Stream 5 | Git Sync Service | 依赖 Stream 1 骨架 |

Stream 2（Parser）可与 Stream 1 完全并行开发，因为 Parser 是纯函数，输入是 Markdown 字符串，输出是结构化数据。

### devpace Schema 参考

Parser 开发需参考 `devpace/knowledge/_schema/` 下的格式定义文件：
- `state-format.md` → StateParser
- `project-format.md` → ProjectParser
- `cr-format.md` → CRParser
- `iteration-format.md` → IterationParser
- `release-format.md` → ReleaseParser
- `insights-format.md` → InsightsParser
- `risk-format.md` → RiskParser
- `pf-format.md` → PFOverflowParser
