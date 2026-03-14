# 发布管理执行规程——Version Bump

> **职责**：语义化版本号读取、推断和更新。
>
> **独立可用**：单独调用 `/pace-release version` 时只需加载本文件。推断规则精简内联，完整 SSOT 在 common.md。

## §0 速查卡片

- **读取**：integrations/config.md → 版本文件路径/格式/字段/Tag 前缀
- **推断**：breaking→major · feature→minor · defect/hotfix-only→patch（详见 common.md SSOT）
- **更新**：Edit 工具替换版本号（json/toml/yaml/text）

## 读取版本配置

1. 读取 `integrations/config.md` 的"版本管理"段
2. 提取：版本文件路径、版本格式、版本字段路径、Tag 前缀
3. 无版本管理配置 → 提示用户手动更新版本文件，跳过后续步骤

## 推断版本号

**优先使用脚本**（确定性推断，比 LLM 推理更可靠）：

1. 执行版本推断脚本：
   ```
   Bash: node ${CLAUDE_SKILL_DIR}/scripts/infer-version-bump.mjs .devpace [当前版本号]
   ```
   - 脚本自动扫描 merged 且未关联 Release 的 CR，检测 breaking/feature/defect 信号
   - 输出 JSON：`{ current, suggested, bump_type, reasoning[], candidates[] }`
2. 向用户展示脚本输出的推断结果（reasoning 数组逐行展示）
3. 等待用户确认版本号或自定义

**脚本不可用时的降级流程**：

1. 读取当前版本号：
   - json/toml/yaml/text 格式（同上"读取版本配置"）
2. 推断规则：breaking→major · feature→minor · defect/hotfix-only→patch（完整规则见 `release-procedures-common.md`「版本推断规则（SSOT）」章节）
3. 展示推断依据后请用户确认版本号

## 更新版本文件

1. 使用 `Edit` 工具替换版本文件中的版本号
   - json：替换 `"version": "旧版本"` → `"version": "新版本"`
   - toml：替换 `version = "旧版本"` → `version = "新版本"`
   - yaml：替换 `version: 旧版本` → `version: 新版本`
   - text：替换旧版本号字符串
2. 更新 Release 文件的版本号字段
