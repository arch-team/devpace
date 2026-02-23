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
  console.log('devpace:tool-failure Write/Edit to CR file failed. Check CR state consistency: 1) Verify CR status field matches last successful state 2) Check if event table needs rollback entry 3) Consider git stash or revert if partial write occurred.');
} else if (filePath && filePath.includes('.devpace/')) {
  console.log('devpace:tool-failure Write/Edit to .devpace/ file failed. Verify state.md is still consistent with current progress.');
}

process.exit(0);
