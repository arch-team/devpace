# P0-2: pace-review Gate 3 守卫 prompt Hook 优化

## 概述

优化 `skills/pace-review/SKILL.md` 的 `type: prompt` Hook。经查证 Hook 执行机制（所有 Hook 并行执行，"最严格者胜"），确认原 prompt Hook 在 approved 场景下是死代码。采用方案 B：替换为 command Hook 做快速路径放行，Gate 3 由全局 Hook 统一管理。

**查证结论**（2026-03-09）：全局 Hook 与 Skill 级 Hook 并行执行，任一 deny → 最终 deny，无 override 机制。方案 A 不可行，采用方案 B。

## 现状分析

### 当前 Skill 级 Hook（SKILL.md:6-13）

```yaml
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: prompt
          prompt: "You are a devpace review gate. During /pace-review, only the following writes are allowed: 1) Updating CR status from in_review to approved (ONLY after explicit human approval in the conversation) 2) Updating CR event table with review notes 3) Recording review rejection and returning to developing. BLOCK any write that changes CR status to approved without clear human approval text in the conversation."
          timeout: 15
```

### 全局 Hook 对比（hooks/pre-tool-use.mjs:45-57）

全局 PreToolUse Hook **已有** Gate 3 command 守卫：
- 检测 `in_review` 状态的 CR 文件
- 若新内容包含 `approved` 状态 → **无条件阻断**（exit 2）
- 没有"人类已批准则放行"的语义

### 两层 Hook 的角色差异

| Hook | 类型 | 行为 | 增量价值 |
|------|------|------|---------|
| 全局 pre-tool-use.mjs | command | 无条件阻断所有 `approved` 变更 | 防御基线（始终生效） |
| Skill 级 pace-review | prompt | 有条件阻断（无人类批准时阻断） | 允许"有人类批准的 approved"（仅 pace-review 激活时） |

**关键洞察**：全局 Hook 已经覆盖了 Gate 3 的核心防护（无条件阻断 approved）。Skill 级 prompt Hook 的增量价值是"在 pace-review 期间，允许有人类明确批准的 approved 变更"。但当前实现中，**全局 Hook 先执行**（exit 2 无条件阻断），Skill 级 prompt Hook **可能根本无法生效**。

### 问题

1. **性能**：每次 Write/Edit ~15s LLM 评估，pace-review 过程中约 5-10 次写入 → ~75-150s 开销
2. **冗余**：绝大多数写入（更新 review notes、event table）不涉及 approved 状态变更
3. **全局冲突**：全局 command Hook 可能先行阻断 approved，导致 Skill 级 prompt Hook 永远无法执行有条件放行

## 方案设计

### 方案 A：分两层（command 快速路径 + prompt 降级）— 推荐

**新增文件**：`hooks/pace-review-scope-check.mjs`

```javascript
#!/usr/bin/env node
/**
 * pace-review scope check — fast path for non-approved writes
 *
 * Quick checks:
 *   1. Not a CR file → allow (exit 0)
 *   2. CR file but no approved state change → allow (exit 0)
 *   3. CR file with approved state change → needs semantic check
 *      → output advisory and exit 0 (let prompt Hook handle)
 *
 * Exit codes:
 *   0 = allow (fast path) or needs-semantic-check (advisory)
 *   2 = block (never — blocking delegated to prompt Hook)
 */

import {
  readStdinJson, getProjectDir, extractFilePath,
  extractWriteContent, isCrFile, isStateChangeToApproved
} from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const filePath = extractFilePath(input);
const backlogDir = `${projectDir}/.devpace/backlog`;

// Fast path 1: not a CR file → no Gate 3 concern
if (!isCrFile(filePath, backlogDir)) {
  process.exit(0);
}

// Fast path 2: CR file but no approved state change
const newContent = extractWriteContent(input);
if (!isStateChangeToApproved(newContent)) {
  process.exit(0);
}

// Slow path: approved state change detected → prompt Hook will evaluate
console.log('devpace:review-gate approved 状态变更检测到，需要语义验证人类审批。');
process.exit(0);
```

**修改 SKILL.md frontmatter**：

```yaml
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/pace-review-scope-check.mjs"
          timeout: 5
        - type: prompt
          prompt: "You are a devpace review gate. ONLY evaluate if the previous hook output contains 'approved 状态变更检测到'. If it does: check if there is explicit human approval in the conversation. If human approved → allow. If no human approval → block. If the previous hook did NOT output this message, always allow."
          timeout: 15
```

**问题**：Skill 级 Hook 的多条 hooks 是串行执行还是并行？需要验证 prompt Hook 能否读取前一个 command Hook 的 stdout 输出。如果不能，此方案需要调整。

### 方案 B：简化为纯 command Hook + 移除冗余 — 备选

**分析**：全局 `pre-tool-use.mjs` 已无条件阻断所有 `approved` 变更。pace-review 的增量语义（"有人类批准则放行"）在当前架构下**可能无法生效**（全局 Hook 先执行并阻断）。

**如果确认全局 Hook 优先级高于 Skill 级 Hook**：
- Skill 级 prompt Hook 事实上是死代码（永远不会被执行到 approved 场景）
- 可以安全移除，或替换为纯 command Hook 做范围检查（如方案 A 的 fast path 部分）

**修改 SKILL.md frontmatter**：

```yaml
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/pace-review-scope-check.mjs"
          timeout: 5
```

此方案中 `pace-review-scope-check.mjs` 只做 fast path 放行（非 CR 或非 approved → exit 0），approved 场景由全局 Hook 阻断。

## 实施前需要验证的问题

1. **Hook 执行顺序**：全局 hooks.json 的 PreToolUse Hook 与 Skill 级 hooks 的执行顺序是什么？
   - 如果全局先执行 → 全局阻断 approved → Skill 级 prompt Hook 永远不会遇到 approved 场景
   - 如果 Skill 级先执行 → Skill 级 prompt Hook 可以做"有条件放行"

2. **Skill 级多 Hook 交互**：同一 matcher 下多条 hooks 是否串行执行？前一条的 stdout 是否对后一条可见？

3. **全局 Hook 覆盖/豁免**：Skill 级 Hook 能否覆盖全局 Hook 的行为？或者 Skill 级 Hook 能否为特定 Skill 豁免全局 Hook？

> **建议**：在实施前通过 `claude-code-guide` agent 查证以上 3 个问题，再决定采用方案 A 还是方案 B。

## 预期效果

| 场景 | 改进前 | 改进后（方案 A/B） |
|------|--------|-------------------|
| 非 CR 文件写入（~80% 操作） | ~15s LLM | ~5ms command |
| CR 文件非 approved 写入（~18%） | ~15s LLM | ~5ms command |
| CR 文件 approved 变更（~2%） | ~15s LLM | ~15s prompt（方案 A）/ ~5ms command + 全局阻断（方案 B） |

## 改动文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `hooks/pace-review-scope-check.mjs` | **新增** | command Hook 快速路径（~30 行） |
| `skills/pace-review/SKILL.md` | **修改** | frontmatter hooks 段替换/优化 |

## 风险评估

- **风险中**：需要先验证 Hook 执行顺序（全局 vs Skill 级），否则可能降低 Gate 3 防护强度
- **回退容易**：恢复 SKILL.md frontmatter 为原始 prompt Hook 即可
