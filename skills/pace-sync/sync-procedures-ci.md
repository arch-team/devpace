# CI/CD 集成规程

> **职责**：通过 `gh` CLI 实现 GitHub Actions 的状态查询、触发和日志查看。

## 前置检测

所有 ci 子命令执行前：

1. 检查 `gh` CLI 是否可用：`which gh`（不可用 → 提示安装 GitHub CLI）
2. 检查 `gh auth status`（未认证 → 提示 `gh auth login`）
3. 检查 `.github/workflows/` 目录是否存在（不存在 → 提示无 GitHub Actions 配置）

## ci status

查看当前分支最近的 CI 运行状态。

**执行**：
```bash
gh run list --branch $(git branch --show-current) --limit 5
```

**输出格式**：
```
CI 状态（当前分支：main）：
✅ Build & Test — 2 分钟前 — 通过
❌ Deploy — 5 分钟前 — 失败（查看详情：gh run view <id>）
⏳ Lint — 进行中

最近 5 次运行中 4 次通过（80%）
```

**与 Gate 4 集成**：pace-dev Gate 4 可调用本规程的 status 逻辑替代原有的简单查询。在 status 输出末尾追加："Gate 4 CI 检查：[通过/失败]"。

## ci trigger

手动触发 GitHub Actions workflow。

**执行**：
1. 无参数 → 列出可用 workflow：`gh workflow list`
2. 有参数 → 触发指定 workflow：`gh workflow run <workflow> --ref $(git branch --show-current)`
3. 触发后轮询状态（最多 3 次，间隔 10 秒）：`gh run list --workflow <workflow> --limit 1`

**输出格式**：
```
已触发 workflow：[名称]
运行 ID：[id]
状态：⏳ 进行中（预计 2 分钟）

查看实时日志：gh run watch <id>
```

**安全约束**：
- 触发前确认："即将触发 [workflow 名] 在 [分支] 上运行。确认？"
- 用户确认后才执行

## ci logs

查看指定运行的日志摘要。

**执行**：
1. 有 run-id → `gh run view <id> --log-failed`（优先显示失败日志）
2. 无 run-id → 取最近一次运行：`gh run list --limit 1` 后自动 view

**输出格式**：
```
运行 #[id]：[workflow 名] — [状态]
失败步骤：[step 名]
错误摘要：[最后 10 行日志]

完整日志：gh run view <id> --log
```

## 容错

| 异常 | 处理 |
|------|------|
| `gh` 未安装 | 提示："需要 GitHub CLI（gh）。安装：https://cli.github.com" |
| 未认证 | 提示："运行 `gh auth login` 完成认证" |
| 无 workflow | 提示："未找到 .github/workflows/，项目尚未配置 GitHub Actions" |
| 非 GitHub 仓库 | 提示："当前项目不是 GitHub 仓库，ci 命令仅支持 GitHub Actions" |
| 网络错误 | 提示具体错误，建议检查网络连接 |

## 与现有能力的关系

- **Gate 4**：现有 Gate 4 通过 `checks-format.md` 中的 `ci-status-cmd` 查询 CI 状态。ci status 提供更丰富的信息，可作为 Gate 4 的增强数据源
- **pace-release deploy**：Release 部署步骤可在 deploy 后自动调用 ci status 确认部署 CI 是否通过
