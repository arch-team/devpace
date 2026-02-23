# 集成配置格式契约

> **职责**：定义 integrations/config.md 的结构。/pace-init 创建、人类和 Claude 维护。

## §0 速查卡片

```
文件：.devpace/integrations/config.md
可选文件——不存在时集成功能降级，核心流程不受影响
包含：环境列表 + CI/CD 配置 + 版本管理 + 发布验证 + 监控配置 + 告警映射
写入规则：/pace-init 创建初始配置，人类按需更新
```

## 文件结构

```markdown
# 集成配置

## 环境

| 环境 | 用途 | URL | 备注 |
|------|------|-----|------|
| [环境名] | [用途描述] | [URL，可选] | [备注] |

## CI/CD

- **工具**：[工具名称，如 GitHub Actions / Jenkins / GitLab CI]
- **触发方式**：[push / manual / tag]
- **构建命令**：[如 npm run build]
- **部署命令**：[如 deploy.sh，可选]
- **检查命令**：[如 gh run list --branch main --limit 1 / jenkins-cli status，可选]

## 版本管理

- **版本文件**：[文件路径，如 package.json / pyproject.toml / Cargo.toml]
- **版本格式**：[json / toml / yaml / text]
- **版本字段**：[字段路径，如 version / tool.poetry.version / package.version]
- **Tag 前缀**：[如 v，则 tag 为 v1.3.0；为空则 tag 为 1.3.0]

## 发布验证

- **验证命令**：[如 curl -sf https://api.example.com/health]
- **验证超时**：[秒数，默认 30]
- **额外验证**：[其他验证命令列表，可选]

## 发布分支

- **分支模式**：[direct / branch，默认 direct]
- **分支前缀**：[如 release/，默认 release/]
- **Release PR**：[true / false，默认 false]
- **自动合并**：[true / false，默认 false]

## CI/CD 测试报告

- **测试报告路径**：[CI 生成的测试报告路径，如 `test-results/` / `coverage/`，可选]
- **覆盖率报告命令**：[从 CI 获取覆盖率的命令，如 `gh api repos/{owner}/{repo}/actions/artifacts`，可选]
- **测试结果格式**：[junit-xml / json / custom，可选]

## 监控

- **工具**：[监控工具，如 Grafana / DataDog / CloudWatch，可选]
- **告警渠道**：[通知方式，如 Slack / Email，可选]

## 告警映射

| 告警类型 | 对应严重度 | 建议 CR 类型 |
|---------|----------|-------------|
| P0 / 生产不可用 | critical | hotfix |
| P1 / 功能受损 | major | defect |
| P2 / 次要问题 | minor | defect |
| P3 / 改进建议 | trivial | defect |
```

## 字段说明

### 环境

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 环境 | 环境名称标识 | ✅ |
| 用途 | 环境用途描述 | ✅ |
| URL | 环境访问地址 | ❌ |
| 备注 | 额外说明 | ❌ |
| 晋升顺序 | 表中行序即为晋升顺序（首行→末行） | 自动 |

### 环境晋升

当环境表中有 2+ 个环境时，devpace 按表中从上到下的顺序视为晋升路径（如 staging → canary → production）。`/pace-release deploy` 逐环境部署，每个环境独立验证。

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 晋升顺序 | 按环境表行序（首行=首环境，末行=最终环境） | 自动 |
| 每环境验证 | 是否在每个环境验证后才晋升到下一个 | ❌ |

### CI/CD

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 工具 | CI/CD 工具名称 | ✅ |
| 触发方式 | 何时触发构建 | ✅ |
| 构建命令 | 构建使用的命令 | ❌ |
| 部署命令 | 部署使用的命令 | ❌ |
| 检查命令 | CI pipeline 状态检查命令 | ❌ |

### 版本管理

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 版本文件 | 需要更新版本号的文件路径 | ✅ |
| 版本格式 | 文件格式（json/toml/yaml/text） | ✅ |
| 版本字段 | 版本号在文件中的字段路径 | ✅ |
| Tag 前缀 | Git Tag 的前缀（通常为 v） | ❌ |

### 发布验证

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 验证命令 | 部署后健康检查命令 | ❌ |
| 验证超时 | 命令超时秒数 | ❌ |
| 额外验证 | 其他验证命令 | ❌ |

### 发布分支

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 分支模式 | direct（直接 tag）或 branch（创建 release 分支） | ❌ |
| 分支前缀 | release 分支名称前缀 | ❌ |
| Release PR | 是否创建 Release PR（需 gh CLI） | ❌ |
| 自动合并 | close 时是否自动 merge release 分支回 main | ❌ |

### CI/CD 测试报告

| 字段 | 说明 | 必填 |
|------|------|:----:|
| 测试报告路径 | CI 生成的测试报告文件目录 | ❌ |
| 覆盖率报告命令 | 从 CI 系统获取覆盖率数据的命令 | ❌ |
| 测试结果格式 | 报告格式（junit-xml / json / custom） | ❌ |

当此 section 存在时，`/pace-test` 可从 CI 系统拉取测试结果和覆盖率数据，作为本地测试的补充信号。

### 告警映射

将外部告警等级映射到 devpace 的严重度和 CR 类型，供 /pace-feedback 自动设置默认值。

## 降级行为

当 `integrations/config.md` 不存在时：
- /pace-release：手动输入部署信息，不自动填充环境
- /pace-feedback：手动输入严重度，不自动映射告警等级
- 节奏检测：不检查部署相关信号
- /pace-release changelog：仍可从 CR 元数据生成 changelog，不依赖集成配置
- /pace-release version：无版本管理配置时，提示用户手动更新版本文件
- /pace-release tag：无 Tag 前缀配置时，默认使用 `v` 前缀
- /pace-release verify：无验证命令时，保持手动验证模式
- /pace-release branch：无发布分支配置时，所有操作在 main 分支完成
- /pace-release deploy：仅 1 个环境时直接部署，无晋升流程
- 核心流程（CR 状态机、质量门、变更管理）完全不受影响
