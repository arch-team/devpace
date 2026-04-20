#!/usr/bin/env node
/**
 * pace-init reset guard — block deletion of .devpace/ without user confirmation.
 *
 * /pace-init --reset uses `rm -rf .devpace/` which bypasses Write|Edit hooks.
 * This hook intercepts Bash commands that delete .devpace/ and requires a
 * confirmation marker file (.devpace/.reset-confirmed) to exist before allowing.
 *
 * The marker is written by Claude after AskUserQuestion confirmation (see
 * init-procedures-reset.md step 3) and is ephemeral — deleted with .devpace/.
 *
 * Exit codes:
 *   0 = allow (not a delete command, or confirmation marker exists)
 *   2 = block (delete command detected but no confirmation marker)
 */

import { readStdinJson, getProjectDir } from '../lib/utils.mjs';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

const input = await readStdinJson();
const command = input?.tool_input?.command || '';

// Only intercept commands that delete .devpace
if (!/\brm\b.*\.devpace\b/.test(command)) {
  process.exit(0);
}

// Check for confirmation marker
const projectDir = getProjectDir();
const marker = resolve(projectDir, '.devpace', '.reset-confirmed');

if (existsSync(marker)) {
  process.exit(0);
}

// Block with actionable message (HE-4 format)
console.error(
  'devpace:reset-guard 检测到删除 .devpace/ 但未找到确认标记。' +
  'ACTION: 先使用 AskUserQuestion 向用户确认重置操作；' +
  '用户确认后写入 .devpace/.reset-confirmed 文件（内容任意）；' +
  '然后再执行删除命令。'
);
process.exit(2);
