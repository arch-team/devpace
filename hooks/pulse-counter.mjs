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
import { basename } from 'node:path';
import { readStdinJson, getProjectDir, extractFilePath, isCrFile, readCrState } from './lib/utils.mjs';

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

// --- Stuck detection: same CR written 5+ times without state change ---
// Throttled to every 3rd write to reduce per-write I/O (reads JSON + CR file + writes JSON).
const filePath = extractFilePath(input);
const backlogDir = `${devpaceDir}/backlog`;
if (isCrFile(filePath, backlogDir) && count % 3 === 0) {
  const crWritesPath = `${devpaceDir}/.pulse-cr-writes`;
  let writes = {};
  try { writes = JSON.parse(readFileSync(crWritesPath, 'utf-8')); } catch { /* start fresh */ }

  const crName = basename(filePath, '.md');
  const currentState = readCrState(filePath);

  if (!writes[crName] || writes[crName].last_state !== currentState) {
    writes[crName] = { count: 1, last_state: currentState };
  } else {
    writes[crName].count++;
  }

  // Prune stale entries — keep only CRs still in backlog (max 20 as safety cap)
  const keys = Object.keys(writes);
  if (keys.length > 20) {
    for (const k of keys) {
      if (!existsSync(`${backlogDir}/${k}.md`)) {
        delete writes[k];
      }
    }
  }

  try { writeFileSync(crWritesPath, JSON.stringify(writes), 'utf-8'); } catch { /* silent */ }

  if (writes[crName].count >= 5) {
    console.log(`devpace:stuck-warning ${crName} 已被写入 ${writes[crName].count} 次但状态仍为 ${currentState}，建议检查是否在空转。考虑: /pace-status 查看全局状态。`);
    console.log(`devpace:struggle-signal ${crName} 重复写入可能指示环境缺陷（Skill/procedure/Schema 不足）。CR merged 后 /pace-learn 将自动提取改进建议。`);
  }
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
