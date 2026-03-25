#!/usr/bin/env node
/**
 * sync-push.mjs — PostToolUse Hook
 * Detects CR **actual state transitions** and reminds to sync with external tools.
 * Uses a file-based cache (.devpace/.sync-state-cache) to compare old vs new state,
 * so ordinary edits that don't change state are silently ignored.
 *
 * - State unchanged → silent exit (no noise)
 * - State changed to merged → advisory suggestion (suggest sync push)
 * - State changed to other value → advisory suggestion
 *
 * Advisory only (exit 0) — never blocks workflow.
 *
 * Noise reduction design (§16 rule 9):
 * This hook fires per-transition to ensure no state change is missed.
 * Claude aggregates multiple reminders within a session and may consolidate them
 * into a single push suggestion at session end (e.g., "3 CRs pending push").
 * The hook itself remains simple and stateless; aggregation logic lives in rules.
 */

import { readFileSync, existsSync } from 'node:fs';
import { basename } from 'node:path';
import {
  readStdinJson, getProjectDir, isCrFile, extractFilePath, readCrState,
  readSyncStateCache, updateSyncStateCache, CR_STATES,
} from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const backlogDir = `${projectDir}/.devpace/backlog`;

// Only act if .devpace exists and has backlog
if (!existsSync(backlogDir)) {
  process.exit(0);
}

// Extract file path from tool input
const filePath = extractFilePath(input);

// Only care about CR files
if (!isCrFile(filePath, backlogDir)) {
  process.exit(0);
}

// No sync-mapping → no sync configured → silent exit
const syncMappingPath = `${projectDir}/.devpace/integrations/sync-mapping.md`;
if (!existsSync(syncMappingPath)) {
  process.exit(0);
}

// Read CR file once for state + external link detection
let crContent;
try {
  crContent = readFileSync(filePath, 'utf-8');
} catch {
  process.exit(0);
}

const newState = readCrState(filePath, crContent);
if (!newState) {
  process.exit(0);
}

// Compare with cached state — only act on actual transitions
const crName = basename(filePath, '.md');
const cache = readSyncStateCache(projectDir);
const oldState = cache.get(crName) || '';

if (oldState === newState) {
  // State unchanged — silent exit (resolves noise problem, F11.8)
  process.exit(0);
}

// State actually changed — update cache (pass existing cache to avoid re-read)
updateSyncStateCache(projectDir, crName, newState, cache);

// Check if CR has external link (use already-read content)
const hasExternalLink = /\*\*外部关联\*\*[：:]/.test(crContent);

if (!hasExternalLink) {
  process.exit(0);
}

// Extract external link info for the reminder
const linkMatch = crContent.match(/\*\*外部关联\*\*[：:]\s*\[([^\]]+)\]\(([^)]+)\)/);
const linkText = linkMatch ? linkMatch[1] : '外部实体';

if (newState === CR_STATES.MERGED) {
  // Advisory language for merged — close-loop
  console.log(`devpace:sync-push ${crName} 状态变更：${oldState || '(new)'}→merged，关联 ${linkText}。ACTION: 执行 /pace-sync 同步状态到外部系统（将关闭外部 Issue 并添加完成标签）；若 sync 失败则手动到外部系统关闭 Issue。`);
} else {
  // Advisory suggestion for other transitions
  console.log(`devpace:sync-push ${crName} 状态变更：${oldState || '(new)'}→${newState}，关联 ${linkText}。ACTION: 执行 /pace-sync 同步状态到外部系统；若暂不需要同步可忽略。`);
}

process.exit(0);
