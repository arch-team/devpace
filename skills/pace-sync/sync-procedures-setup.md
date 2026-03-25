# setup — 引导式配置

> **职责**：定义 /pace-sync setup 子命令的详细执行步骤。

## 输入

`$ARGUMENTS` 可包含 `--auto`（跳过交互确认，CI/CD 场景友好）。

## 前置检查

1. 检查平台工具是否可用（不可用 → 提示安装，不阻断）
2. 检查 `.devpace/` 是否存在（不存在 → 引导 /pace-init）
3. 检查 `sync-mapping.md` 是否已存在（已存在 → 提示"同步已配置，是否重新配置？"，确认后继续，否则退出）

## 执行步骤

1. 读取 git remote：`git remote get-url origin` → 提取 owner/repo
2. **适配器自动选择**：根据 remote URL 域名匹配 `sync-procedures-common.md` §1 适配器路由表的"域名匹配"列
   - 匹配到 → 自动选择对应适配器
   - 未匹配 → 询问用户选择平台
3. **确认配置**（`--auto` 时跳过，使用默认值）：
   - 仓库：{owner}/{repo}
   - 同步模式：push（推荐 MVP，`--auto` 默认值）
   - 冲突策略：ask-user（推荐 MVP，`--auto` 默认值）
   - 自动同步：suggest（推荐，`--auto` 默认值。CR 创建时询问是否关联/创建外部 Issue）
4. 执行适配器"验证连接"操作
5. 生成 `.devpace/integrations/sync-mapping.md`（按 Plugin `knowledge/_schema/integration/sync-mapping-format.md` Schema）
6. 执行适配器 setup 补充步骤（如预创建状态标记等平台初始化操作）
   - 平台工具不可用时跳过，在配置摘要中标注
7. 更新 `.devpace/integrations/config.md` 的"外部同步"section（如 config.md 存在）
8. 输出配置摘要

## pace-init 自动延伸

当 `/pace-init` 检测到 git remote 为已支持平台（如 github.com）且 `gh auth status` 验证通过时：
- 默认将 sync 配置作为 init 的自然延伸，自动生成 sync-mapping.md（push-only 模式）
- 用户明确拒绝时跳过
- 这符合 P3（副产物非前置）——sync 配置是 init 的副产物，不应成为额外步骤

## 输出格式

```
同步配置完成：
- 平台：{平台类型} ({连接标识})
- 同步模式：push
- 连接状态：✅ 已验证 / ⚠️ 未验证（平台工具不可用）
- 初始化状态：✅ 已完成 / ⚠️ 未完成（平台工具不可用）
下一步：用 /pace-sync link CR-xxx #外部编号 关联变更请求
```

**降级**：平台工具不可用时仍生成配置文件，标注"连接未验证"。
