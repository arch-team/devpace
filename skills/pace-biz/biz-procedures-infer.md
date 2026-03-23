# infer 子命令 procedures

> **职责**：从当前代码库推断未追踪的功能和技术债务，补充到功能树。

## 触发

`/pace-biz infer` 或用户要从代码分析需求（"看看代码里有什么功能"、"技术债务盘点"、"哪些功能没追踪"）。

## 与其他子命令的区别

- **discover**：从模糊想法出发，通过对话引导产出候选
- **import**：从文档提取需求实体
- **infer**：从代码库反向推断已有功能和技术债务

## 步骤

### Step 0：前置检查与模式检查

1. 检查 `.devpace/` 存在（不存在 → 引导 `/pace-init`）
2. 读取 `project.md` 现有功能树（获取已追踪的 PF 列表）
3. 检查 git 仓库状态：
   - git 可用 → 完整分析（含 blame/hotspot）
   - git 不可用 → 退化模式（纯目录结构 + 注释扫描）

### Step 1：代码结构分析

扫描源码目录，建立模块→功能映射：

**源码根目录检测**（按优先级）：
- `src/` → 标准源码目录
- `app/` → Next.js / Rails 风格
- `lib/` → 库项目
- 项目根目录（排除配置文件后）

**扫描规则**：

| 检测目标 | 方法 | 映射 |
|---------|------|------|
| 目录结构 | 一级子目录 → 模块 | 模块 → PF 候选分组 |
| 路由定义 | `routes/`、`@app.route`、`router.get` 等 | 路由 → API PF 候选 |
| API 端点 | `@Controller`、`@api_view`、OpenAPI 定义 | 端点 → PF 候选 |
| 数据模型 | `models/`、`@Entity`、`class.*Model` | 模型 → BR 候选（数据域） |
| UI 组件 | `components/`、`pages/`、`views/` | 页面/组件 → PF 候选 |
| CLI 命令 | `commands/`、`@click.command` | 命令 → PF 候选 |

**排除目录**：`test/`、`__tests__`、`spec/`、`fixtures/`、`node_modules/`、`.devpace/`、`vendor/`、`dist/`、`build/`。

**角色适配**（通用维度见 `knowledge/role-adaptations.md`，读取公共前置传入的 preferred-role）：
- Ops → 报告中优先展示部署/运维相关模块和技术债务
- Tester → 报告中标注缺少测试覆盖的模块
- Dev/PM/Biz Owner（默认）→ 无追加（零改变）

### Step 2：信号挖掘

在代码中搜索额外信号：

**注释信号**：

| 模式 | 信号类型 | 处理 |
|------|---------|------|
| `TODO`、`FIXME` | 技术债务 | → PF 候选（标记"技术债务"） |
| `HACK`、`XXX`、`WORKAROUND` | 技术债务（高优） | → PF 候选（标记"技术债务-高优"） |
| `#123`（Issue 引用） | 外部追踪 | 记录交叉参照（如有 tracker） |

**项目配置信号**：

| 来源 | 检测内容 | 映射 |
|------|---------|------|
| `package.json` scripts | 构建/测试/部署命令 | 运维能力 PF 候选 |
| `Makefile` / `Taskfile` | 自动化任务 | 运维能力 PF 候选 |
| `README.md` | 功能描述 section | 文档声明功能 vs 实际代码对比 |
| `Dockerfile` / `docker-compose.yml` | 服务定义 | 部署架构信息 |

**Git 增强信号**（git 可用时）：

| 分析 | 方法 | 用途 |
|------|------|------|
| 热点文件 | `git log --since="30 days" --name-only` 统计变更频率 | 活跃开发区标记 |
| 共变文件 | 同一 commit 中频繁一起出现的文件 | 耦合模块识别 |
| 贡献者分布 | `git shortlog -sn` | 知识集中度风险 |

### Step 3：差距分析

对比推断功能 vs 现有功能树，分类：

| 分类 | 条件 | 说明 |
|------|------|------|
| 未追踪 | 代码中存在功能模块，但功能树中无对应 PF | 建议补充追踪 |
| 未实现 | 功能树中有 PF，但代码中无对应实现 | 确认是计划中还是遗漏 |
| 技术债务 | TODO/FIXME 密集区域（>3 个/文件） | 建议纳入追踪 |
| 文档漂移 | README 描述的功能与实际代码不匹配 | 提醒更新文档或功能树 |

**匹配规则**：通过 PF 名称关键词与代码模块/文件名的语义关联判断。模糊匹配时列出供用户确认。

### Step 4：报告与确认

三段式输出：

```
代码库分析报告：

1. 未追踪功能（代码有，功能树无）：
   模块 [auth/]：
   + PF 候选：用户认证（routes: login, register, logout）
   + PF 候选：权限管理（middleware: checkPermission）

   模块 [api/]：
   + PF 候选：数据导出 API（endpoints: /export/csv, /export/json）

2. 未实现功能（功能树有，代码无）：
   ? PF-003：高级搜索 — 确认状态：计划中 / 已放弃 / 其他？

3. 技术债务（TODO/FIXME 集中区域）：
   ! src/utils/parser.js（8 个 TODO）— 纳入追踪？
   ! src/db/migration.py（5 个 FIXME）— 纳入追踪？

[Git 增强] 热点：src/core/engine.js（30天内 42 次变更）
[Git 增强] 耦合：auth/ ↔ session/（经常一起改动）

逐项选择：accept / skip / 调整分组
```

用户逐项选择后确认。

### Step 5：写入 .devpace/

1. 确认的"未追踪功能"：追加到 `project.md` 功能树
   - 按模块分组归入对应 BR 下（无明确归属时创建新 BR 分组）
   - PF 内联格式遵循 `knowledge/_schema/entity/pf-format.md` §内联格式
   - PF 编号自增
2. 确认的"技术债务"：追加到 `project.md` 功能树
   - PF 名称附"（技术债务）"后缀
   - 归入新建或已有的"技术债务" BR 分组下
3. "未实现功能"用户确认为"已放弃"的 → 标记 PF 状态
4. 所有内容标记溯源：`<!-- source: claude, inferred from codebase -->`
5. 触发 PF/BR 溢出检查（按 project-format.md 溢出规则）
6. git commit

### Step 6：下游引导

```
代码库推断完成：
- 新增追踪：X 个产品功能
- 技术债务：Y 个待处理项
- 未实现确认：Z 个功能状态已更新
  成熟度分布：骨架级 K 个 / 基本级 M 个 — 建议优先精炼骨架级实体

→ /pace-biz refine [最需精炼的 ID] 优先精炼关键功能
→ /pace-biz align 检查新增项的战略对齐度
→ /pace-dev 开始处理优先项
→ /pace-plan next 将新增项排入迭代
```

## 降级模式

| 场景 | 行为 |
|------|------|
| .devpace/ 不存在 | 正常执行 Step 1-4（代码分析），Step 5 输出到控制台不写文件，结尾引导 `/pace-init` |
| project.md 是桩 | 正常运行，Step 3 跳过差距分析（无功能树可对比），直接输出发现 |
| 无 Git | 退化：跳过 Step 2 的 Git 增强信号（热点/共变/贡献者），其余正常 |
| 无源码目录 | 提示"未检测到源码目录"，列出项目根目录结构供用户指定 |

## 容错

| 异常 | 处理 |
|------|------|
| 源码目录过大（>1000 文件） | 限制扫描深度为 3 层，提示用户可指定子目录 |
| 无法识别项目类型 | 仅做目录结构分析 + TODO 扫描，跳过框架特定检测 |
| Git 命令超时 | 降级到非 Git 模式，提示用户 |
| 推断结果为空 | 提示"代码库结构简单或功能树已完整覆盖" |
| 编号冲突 | 重新扫描确认最大编号后分配 |
