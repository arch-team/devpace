#!/usr/bin/env node
/**
 * sync-push.mjs — PostToolUse Hook
 * Detects CR state changes and reminds to sync with external tools.
 * Advisory only (exit 0) — never blocks workflow.
 */

import { readFileSync, existsSync } from 'node:fs';
import { readStdinJson, getProjectDir, isCrFile, extractFilePath, readCrState } from './lib/utils.mjs';

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

// Read CR state
const state = readCrState(filePath);
if (!state) {
  process.exit(0);
}

// Check if CR has external link
try {
  const content = readFileSync(filePath, 'utf-8');
  const hasExternalLink = /\*\*外部关联\*\*[：:]/.test(content);

  if (!hasExternalLink) {
    process.exit(0);
  }

  // Extract external link info for the reminder
  const linkMatch = content.match(/\*\*外部关联\*\*[：:]\s*\[([^\]]+)\]\(([^)]+)\)/);
  const linkText = linkMatch ? linkMatch[1] : '外部实体';

  // Output advisory reminder
  console.log(`devpace:sync-push CR state=${state}, linked to ${linkText}. Consider running /pace-sync push to sync status to the external tool.`);
} catch {
  // File read error — silent exit
}

process.exit(0);
