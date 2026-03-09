# scan — Pre-flight 风险扫描

> **职责**：/pace-guard scan 子命令的详细执行规则。依赖 `guard-procedures-common.md`（严重度矩阵、自主权矩阵、风险文件创建规则）。

## 扫描维度与数据源

| 维度 | 检查内容 | 数据源 |
|------|---------|--------|
| 历史教训 | 相似 CR 的失败/打回 pattern | insights.md（defense 类型，置信度 ≥ 0.5）+ dashboard.md |
| 依赖影响 | 改动文件的反向依赖链 | 代码文件 import/require/from 分析 |
| 架构兼容性 | 变更是否违反项目技术约定 | .devpace/context.md（如存在） |
| 范围复杂度 | 实际工作量 vs 预期 | CR 描述 + 项目文件树（Glob 扫描） |
| 安全敏感度 | 涉及认证/授权/数据/加密/OWASP 风险模式 | 文件路径关键词 + 代码模式分析（见安全深度检查规则） |

### 安全深度检查规则

安全敏感度维度分两层检查：

**Layer 1 — 路径关键词匹配**（所有复杂度）：
- 文件路径包含：`auth`/`crypto`/`secret`/`token`/`password`/`key`/`permission`/`session`/`jwt`/`oauth`/`cors`/`csrf`/`sanitize`/`encrypt`/`decrypt`

**Layer 2 — OWASP 风险模式扫描**（L/XL 或显式 `scan --full` 时）：

**优先使用脚本**（确定性正则匹配，替代 LLM 逐行模式识别）：

```
Bash: git diff main...HEAD | node ${CLAUDE_PLUGIN_ROOT}/scripts/security-scan.mjs
# 或指定 CR：node ${CLAUDE_PLUGIN_ROOT}/scripts/security-scan.mjs --cr CR-001 .devpace
```

脚本输出 JSON `{ findings[], summary: { total, high, medium }, scanned_files }`。findings 为空时跳过 Layer 2 报告。脚本不可用时降级为以下 LLM 手动扫描：

| OWASP 分类 | 检测模式 | 严重度 |
|-----------|---------|--------|
| 注入（A03） | SQL 拼接、命令拼接、模板注入模式 | High |
| 认证失效（A07） | 硬编码密钥、明文密码存储、无速率限制 | High |
| 敏感数据暴露（A02） | API 密钥在代码中、日志输出敏感字段、无加密传输 | High |
| 访问控制（A01） | 缺少权限检查的 API 路由、路径遍历风险 | Medium |
| 安全配置（A05） | 调试模式开启、默认密码、过宽 CORS | Medium |
| 依赖漏洞（A06） | 已知 CVE 的依赖版本（如有 lockfile 可检测） | Medium |

**Layer 2 执行方式**：对 CR 涉及的代码文件执行 `git diff` → 对新增/修改行逐一匹配上述模式 → 命中时标注 OWASP 分类和严重度。

**输出**：Layer 1 命中 → 标记 "安全敏感文件 N 个"。Layer 2 命中 → 标记具体 OWASP 分类和位置。

## 复杂度自适应（A1）

显式调用 `/pace-guard scan` 和自动触发均按 CR 复杂度自适应扫描深度：

| CR 复杂度 | 扫描维度 | 触发场景 |
|-----------|---------|---------|
| S（单文件） | 不触发（自动触发时）/ 2 维：历史教训+安全敏感度（显式调用时） | 显式调用仅扫描最关键 2 维 |
| S（多文件）/ M | 仅在 insights.md 有匹配 defense pattern（置信度 ≥ 0.5）时触发历史教训维度（自动触发时）/ 3 维：历史教训+安全敏感度+依赖影响（显式调用时） | 显式调用扩展到依赖分析 |
| L / XL | 完整 5 维扫描 | 自动触发和显式调用均执行完整扫描 |

**`--full` 覆盖**：任何复杂度均可通过 `scan --full` 强制执行完整 5 维扫描。

## 异常驱动报告（A3）

scan 输出采用异常驱动策略，默认只展示需要关注的内容：

| 场景 | 标准输出 | `--detail` 输出 |
|------|---------|----------------|
| 全部 Low | 1 行：`"5 维扫描均为 Low，风险可控。"` | 完整 5 维矩阵表格 |
| 有 Medium/High | 仅展示 Medium/High 维度的详细分析 | 完整 5 维矩阵 + 历史对比 |
| 仅 1 维 Medium，其余 Low | 展示该 Medium 维度 + 1 行 Low 汇总 | 完整矩阵 |

**简要输出**（`--brief`）：`scan：[综合等级] · [Medium/High 数] 维需关注 · [下一步建议]`

## 扫描结果写入规则

1. 结果写入 CR 文件的"风险预评估"section（格式见 cr-format.md）
2. Medium/High 风险同步创建 `.devpace/risks/RISK-NNN.md`（遵循 common 风险文件创建规则）
3. 综合风险等级 = 取所有扫描维度的最高等级
4. High 综合风险：输出提醒 "**风险预评估为 High（[原因]），已在执行计划中增加防护步骤。**"

## 中断恢复（A7）

L/XL 完整 5 维扫描涉及大量文件分析。支持轻量检查点：

1. 每个维度扫描完成后，将该维度结果写入 CR "风险预评估"section，并在末尾添加标记：`<!-- scan-in-progress: [已完成维度列表] -->`
2. 下次调用 `scan` 时，检测 CR 文件中是否存在 `scan-in-progress` 标记：
   - **存在** → 提示："检测到上次未完成的扫描（已完成：[N]/5 维），续扫还是重新开始？"
   - 用户选择续扫 → 仅执行未完成的维度
   - 用户选择重新开始 → 清除标记，执行完整扫描
3. 扫描全部完成后，移除 `scan-in-progress` 标记

**S/M CR 不触发检查点**（扫描维度少，无需恢复机制）。

## 智能推荐

scan 报告末尾根据综合风险等级推荐下一步操作（使用 common.md 智能推荐模板）。
