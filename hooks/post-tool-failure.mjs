#!/usr/bin/env node
/**
 * devpace PostToolUseFailure hook — detect tool failures in advance mode
 *
 * Purpose: When a Write/Edit tool fails during advance mode, remind Claude
 * to check CR state consistency. Prevents CR state and file content from
 * becoming out of sync after a failed write operation.
 *
 * Advisory hook (exit 0), not blocking.
 */

import { existsSync } from 'node:fs';
import { readStdinJson, getProjectDir, extractFilePath, isCrFile, isAdvanceMode } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const backlogDir = `${projectDir}/.devpace/backlog`;

// Only act if .devpace exists and we're in advance mode
if (!existsSync(backlogDir) || !isAdvanceMode(projectDir)) {
  process.exit(0);
}

const filePath = extractFilePath(input);

// Check if the failed write was targeting a CR file
if (isCrFile(filePath, backlogDir)) {
  console.log(`devpace:tool-failure CR 文件写入失败。ACTION: 1) 读取 CR 文件确认状态字段是否仍为上次成功值 2) 若状态不一致则在事件表补记 write_failed 条目 3) 执行 git diff ${filePath} 检查部分写入，必要时 git checkout -- ${filePath} 恢复。`);
} else if (filePath && filePath.includes('.devpace/')) {
  console.log(`devpace:tool-failure .devpace/ 文件写入失败。ACTION: 读取 state.md 确认与当前进度一致；若不一致则执行 git checkout -- ${filePath} 恢复后重试写入。`);
}

process.exit(0);
