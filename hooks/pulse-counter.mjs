#!/usr/bin/env node
/**
 * devpace PostToolUse hook — periodic write-count reminder
 *
 * Purpose: Track write operations and periodically remind Claude to check
 * project status. This is a WRITE VOLUME reminder, complementary to but
 * distinct from pace-pulse (rhythm health detection).
 *
 * Coordination with pace-pulse:
 * - pulse-counter: triggers every 10 writes → suggests /pace-status (write volume)
 * - pace-pulse: triggers every 5 checkpoints or 30min → detects rhythm anomalies
 * - If pace-pulse ran recently (< 5 min), this hook skips its reminder to avoid
 *   double-reminding the user in a short window.
 *
 * Uses .devpace/.pulse-counter as persistent counter (not version-controlled).
 * Uses .devpace/.pulse-last-run as pace-pulse timestamp (written by advance mode).
 *
 * This is an advisory hook (exit 0), never blocks.
 */

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { readStdinJson, getProjectDir } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const devpaceDir = `${projectDir}/.devpace`;
const counterFile = `${devpaceDir}/.pulse-counter`;
const pulseLastRunFile = `${devpaceDir}/.pulse-last-run`;

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

// Trigger write-volume reminder every 10 writes
if (count > 0 && count % 10 === 0) {
  // Check if pace-pulse ran recently (< 5 min) — skip if so to avoid double-remind
  let skipReminder = false;
  try {
    const lastRunStr = readFileSync(pulseLastRunFile, 'utf-8').trim();
    const lastRunMs = parseInt(lastRunStr, 10) || 0;
    if (lastRunMs > 0 && (Date.now() - lastRunMs) < 5 * 60 * 1000) {
      skipReminder = true;
    }
  } catch {
    // No pulse-last-run file — pace-pulse hasn't run, proceed normally
  }

  if (!skipReminder) {
    console.log(`devpace:write-volume 已执行 ${count} 次写操作。查看项目进度——\`/pace-status\``);
  }
}

process.exit(0);
