# P0-1: pace-init 写入守卫 prompt Hook → command Hook

## 概述

将 `skills/pace-init/SKILL.md` 中的 `type: prompt` Hook 替换为 `type: command` Hook，从 LLM 路径判断（~10s/次）降级为 Node.js 程序化路径匹配（~5ms/次）。

## 现状分析

### 当前 Hook（SKILL.md:7-14）

```yaml
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: prompt
          prompt: "/pace-init 写入范围守卫：仅允许写入 .devpace/ 目录下的文件、项目根目录的 CLAUDE.md、项目根目录的 .gitignore。如果写入目标不在这三个范围内，必须阻止。"
          timeout: 10
```

### 问题

- pace-init 执行过程中会触发 20+ 次 Write/Edit（创建 state.md、project.md、模板文件等）
- 每次触发 ~10s LLM 评估 → 总开销 ~200s 纯等待
- 逻辑本质是**纯路径前缀匹配**（3 个允许范围），不需要 LLM 语义理解

### 允许写入的范围（精确定义）

1. `.devpace/` 目录下的任何文件（项目根目录下的 `.devpace/`）
2. 项目根目录的 `CLAUDE.md`
3. 项目根目录的 `.gitignore`

## 方案设计

### 新增文件

**`hooks/pace-init-scope-check.mjs`**（~30 行）

```javascript
#!/usr/bin/env node
/**
 * pace-init scope check — fast command Hook replacing LLM prompt Hook
 *
 * Checks: Is the target file within pace-init's allowed write scope?
 *   1. .devpace/ directory (any file)
 *   2. Project root CLAUDE.md
 *   3. Project root .gitignore
 *
 * Exit codes:
 *   0 = allow (in scope)
 *   2 = block (out of scope)
 */

import { readStdinJson, getProjectDir, extractFilePath } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const filePath = extractFilePath(input);

if (!filePath) {
  process.exit(0); // No file path — not our concern
}

// Normalize: resolve relative to project dir
const normalizedPath = filePath.startsWith('/')
  ? filePath
  : `${projectDir}/${filePath}`;

// Check 1: .devpace/ directory
if (normalizedPath.includes('.devpace/') || normalizedPath.includes('/.devpace/')) {
  process.exit(0);
}

// Check 2: Project root CLAUDE.md
if (normalizedPath.endsWith('/CLAUDE.md') || normalizedPath === 'CLAUDE.md') {
  // Ensure it's the project root CLAUDE.md, not a subdirectory one
  const expectedPath = `${projectDir}/CLAUDE.md`;
  if (normalizedPath === expectedPath || normalizedPath.endsWith('/CLAUDE.md')) {
    process.exit(0);
  }
}

// Check 3: Project root .gitignore
if (normalizedPath.endsWith('/.gitignore') || normalizedPath === '.gitignore') {
  const expectedPath = `${projectDir}/.gitignore`;
  if (normalizedPath === expectedPath || normalizedPath.endsWith('/.gitignore')) {
    process.exit(0);
  }
}

// Out of scope — block
console.error(
  `devpace:blocked /pace-init 写入范围守卫：仅允许写入 .devpace/、CLAUDE.md、.gitignore。目标文件 ${filePath} 不在允许范围内。`
);
process.exit(2);
```

### 修改文件

**`skills/pace-init/SKILL.md`** frontmatter hooks 段

```yaml
# 替换前（prompt Hook）
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: prompt
          prompt: "/pace-init 写入范围守卫：..."
          timeout: 10

# 替换后（command Hook）
hooks:
  PreToolUse:
    - matcher:
        tool_name: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/pace-init-scope-check.mjs"
          timeout: 5
```

## 设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| Hook 类型 | command（替代 prompt） | 逻辑是纯路径匹配，无需 LLM 语义 |
| 脚本语言 | Node.js ESM | 与现有 Hook 基础设施一致（pace-dev-scope-check.mjs） |
| 共享库 | 复用 hooks/lib/utils.mjs | readStdinJson、getProjectDir、extractFilePath 已有 |
| 路径匹配策略 | 字符串 includes/endsWith | 简单可靠，无需正则 |
| CLAUDE.md 范围 | 仅项目根目录 | 避免写入 `.claude/CLAUDE.md` 等非目标文件 |
| 超时 | 5s（从 10s 降低） | command Hook 实际执行 <50ms，5s 是安全余量 |

## 预期效果

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 单次 Hook 延迟 | ~10s（LLM） | ~5ms（Node.js） | **2000x** |
| pace-init 全流程 Hook 总开销 | ~200s（20 次 Write） | ~100ms | **2000x** |
| 判断可靠性 | LLM 可能误判 | 确定性匹配 | 100% 可靠 |

## 改动文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `hooks/pace-init-scope-check.mjs` | **新增** | command Hook 实现（~50 行） |
| `skills/pace-init/SKILL.md` | **修改** | frontmatter hooks 段替换 prompt → command |

## 验证方案

1. `node hooks/pace-init-scope-check.mjs` 用模拟 stdin JSON 测试路径匹配
2. `claude --plugin-dir ./` 加载后执行 `/pace-init --dry-run` 确认 Hook 不阻断正常写入
3. 手动构造越界写入路径，确认 exit 2 阻断

## 风险评估

- **风险低**：逻辑极其简单（3 个路径条件），且有现有模板（pace-dev-scope-check.mjs）
- **回退容易**：恢复 SKILL.md frontmatter 为 prompt Hook 即可
