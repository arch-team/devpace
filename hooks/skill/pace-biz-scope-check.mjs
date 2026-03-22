#!/usr/bin/env node
/**
 * pace-biz scope check — fast command Hook for write scope validation
 *
 * pace-biz is a business planning skill that should only write to .devpace/
 * management files. It must never modify source code or other project files.
 *
 * Allowed write targets:
 *   - .devpace/ directory (any file: opportunities.md, epics/, project.md,
 *     requirements/, scope-discovery.md, state.md, etc.)
 *
 * Exit codes:
 *   0 = allow (target is within .devpace/)
 *   2 = block (target is outside .devpace/)
 */

import { readStdinJson, extractFilePath, isDevpaceFile } from '../lib/utils.mjs';

const input = await readStdinJson();
const filePath = extractFilePath(input);

if (!filePath) {
  // No file path in input — not a file write, allow
  process.exit(0);
}

// .devpace/ files are the only valid write targets for pace-biz
if (isDevpaceFile(filePath)) {
  process.exit(0);
}

// Out of scope — block
console.error(
  `devpace:blocked /pace-biz 写入范围守卫：目标文件 ${filePath} 不在允许范围内。业务规划域仅允许写入 .devpace/ 目录。ACTION: 将写入目标调整到 .devpace/ 目录下；若确需修改非 .devpace/ 文件则退出 /pace-biz 使用 /pace-dev。`
);
process.exit(2);
