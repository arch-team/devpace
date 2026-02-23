#!/usr/bin/env node
/**
 * devpace PostToolUse hook — periodic pulse reminder based on write count
 *
 * Purpose: Track write operations to .devpace/ related files and periodically
 * remind Claude to check development rhythm health via pace-pulse.
 *
 * Uses .devpace/.pulse-counter as persistent counter (not version-controlled).
 * Reminder triggers every 10 write operations. Resets on session start.
 *
 * This is an advisory hook (exit 0), never blocks.
 */

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { readStdinJson, getProjectDir } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const devpaceDir = `${projectDir}/.devpace`;
const counterFile = `${devpaceDir}/.pulse-counter`;

// Only act if .devpace exists
if (!existsSync(devpaceDir)) {
  process.exit(0);
}

// Read and increment counter
let count = 0;
try {
  const raw = readFileSync(counterFile, 'utf-8').trim();
  count = parseInt(raw, 10) || 0;
} catch {
  // Counter file doesn't exist yet — start at 0
}

count += 1;

// Write updated counter
try {
  writeFileSync(counterFile, String(count), 'utf-8');
} catch {
  // Can't write counter — degrade silently
  process.exit(0);
}

// Trigger pulse reminder every 10 writes
if (count > 0 && count % 10 === 0) {
  console.log(`devpace:pulse-reminder 已执行 ${count} 次写操作，建议检查研发节奏健康度。可执行 /pace-status 查看进度。`);
}

process.exit(0);
