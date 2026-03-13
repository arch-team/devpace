#!/usr/bin/env node
/**
 * pace-init scope check — fast command Hook replacing LLM prompt Hook
 *
 * Replaces the slow prompt-type Hook (~10s LLM per call) with a fast
 * programmatic check (~5ms) for write scope validation.
 *
 * Allowed write targets during /pace-init:
 *   1. .devpace/ directory (any file under it)
 *   2. Project root CLAUDE.md
 *   3. Project root .gitignore
 *
 * Exit codes:
 *   0 = allow (target is within allowed scope)
 *   2 = block (target is outside allowed scope)
 */

import { readStdinJson, getProjectDir, extractFilePath } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const filePath = extractFilePath(input);

if (!filePath) {
  // No file path in input — not a file write, allow
  process.exit(0);
}

// Normalize to absolute path for reliable comparison
const absPath = filePath.startsWith('/')
  ? filePath
  : `${projectDir}/${filePath}`;

// Normalize projectDir for comparison (remove trailing slash)
const projRoot = projectDir.endsWith('/') ? projectDir.slice(0, -1) : projectDir;

// Check 1: .devpace/ directory — any file underneath
if (absPath.includes('/.devpace/') || absPath.includes('.devpace/')) {
  process.exit(0);
}

// Check 2: Project root CLAUDE.md
if (absPath === `${projRoot}/CLAUDE.md`) {
  process.exit(0);
}

// Check 3: Project root .gitignore
if (absPath === `${projRoot}/.gitignore`) {
  process.exit(0);
}

// Out of scope — block
console.error(
  `devpace:blocked /pace-init 写入范围守卫：目标文件 ${filePath} 不在允许范围内。仅允许写入 .devpace/、CLAUDE.md、.gitignore。`
);
process.exit(2);
