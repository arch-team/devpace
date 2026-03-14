/**
 * devpace Hook shared utilities
 * Pure Node.js ESM — no npm dependencies.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createInterface } from 'node:readline';
import { dirname } from 'node:path';

/**
 * Canonical CR state values.
 * All .mjs hooks should import and use these constants instead of raw strings.
 * Shell hooks (session-end.sh, pre-compact.sh) use grep equivalents — keep in sync.
 */
export const CR_STATES = Object.freeze({
  CREATED: 'created',
  DEVELOPING: 'developing',
  VERIFYING: 'verifying',
  IN_REVIEW: 'in_review',
  APPROVED: 'approved',
  MERGED: 'merged',
  PAUSED: 'paused',
});

/**
 * Read stdin and JSON.parse it. Returns {} on any failure.
 */
export async function readStdinJson() {
  try {
    const chunks = [];
    const rl = createInterface({ input: process.stdin });
    for await (const line of rl) {
      chunks.push(line);
    }
    const raw = chunks.join('\n');
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

/**
 * Return the project directory (CLAUDE_PROJECT_DIR or '.').
 */
export function getProjectDir() {
  return process.env.CLAUDE_PROJECT_DIR || '.';
}

/**
 * Extract file_path from a tool input object.
 * Handles both { tool_input: { file_path } } and { file_path } shapes.
 */
export function extractFilePath(input) {
  const toolInput = input?.tool_input ?? input;
  return toolInput?.file_path ?? '';
}

/**
 * Check whether filePath points to a CR file under backlogDir.
 */
export function isCrFile(filePath, backlogDir) {
  if (!filePath) return false;
  if (backlogDir) {
    return filePath.startsWith(backlogDir) && filePath.includes('/CR-');
  }
  return filePath.includes('.devpace/backlog/CR-');
}

/**
 * Read a CR markdown file and return the value of the "状态" field.
 * CR format: "- **状态**：<value>" (Markdown bold + Chinese/ASCII colon)
 * Returns empty string if not found or file unreadable.
 *
 * Shell equivalents (keep in sync if format changes):
 *   session-end.sh:  grep + sed to extract state from "- **状态**：" line
 *   pre-compact.sh:  grep for active state keywords in state.md
 */
export function readCrState(filePath, content) {
  try {
    const text = content ?? readFileSync(filePath, 'utf-8');
    const match = text.match(/^- \*\*状态\*\*[：:]\s*(.+)$/m);
    return match ? match[1].trim() : '';
  } catch {
    return '';
  }
}

/**
 * Check whether filePath points to any file under .devpace/ directory.
 */
export function isDevpaceFile(filePath) {
  if (!filePath) return false;
  return filePath.includes('.devpace/');
}

/**
 * Detect whether the project is in advance mode (推进模式).
 * Advance mode is inferred from state.md: if there's an active "进行中" entry,
 * we consider the session in advance mode. Otherwise, it's explore mode (default).
 * Returns true if advance mode, false if explore mode.
 */
export function isAdvanceMode(projectDir, content) {
  try {
    const text = content ?? readFileSync(`${projectDir}/.devpace/state.md`, 'utf-8');
    return /\*\*进行中\*\*/.test(text);
  } catch {
    return false;
  }
}

/**
 * Extract the new content being written from a tool input object.
 * For Write: { tool_input: { content } }
 * For Edit: { tool_input: { new_string } }
 */
export function extractWriteContent(input) {
  const toolInput = input?.tool_input ?? input;
  return toolInput?.content ?? toolInput?.new_string ?? '';
}

/**
 * Check if write content attempts to change CR state to 'approved'.
 * This is the Gate 3 violation pattern — state should only change to approved
 * after explicit human approval.
 */
export function isStateChangeToApproved(content) {
  if (!content) return false;
  return /\*\*状态\*\*[：:]\s*approved/.test(content);
}

/**
 * Check if write content sets CR state to an advance-mode-only value.
 * These states (developing, verifying, in_review) represent active progress
 * and should not be set in explore mode — use advance mode via /pace-dev.
 * States like created and paused are allowed in explore mode (pace-change needs them).
 */
export function isStateEscalation(content) {
  if (!content) return false;
  return /\*\*状态\*\*[：:]\s*(developing|verifying|in_review)/.test(content);
}

/**
 * Read the last event from a CR file's event table.
 * Parses the structured event format: | timestamp | event_type | actor | note | handoff |
 * @param {string} crFilePath - CR file path
 * @returns {{ ts: string, type: string, actor: string, note: string } | null}
 */
export function getLastEvent(crFilePath, content) {
  try {
    const text = content ?? readFileSync(crFilePath, 'utf-8');
    const lines = text.split('\n');

    let inEventTable = false;
    let lastDataLine = null;
    for (const line of lines) {
      if (/^##\s*事件/.test(line)) { inEventTable = true; continue; }
      if (inEventTable && /^##\s/.test(line)) break;
      if (inEventTable && /^\|.*\|.*\|/.test(line) && !/^[\|\s-]+$/.test(line) && !/时间戳|事件类型|日期|事件/.test(line)) {
        lastDataLine = line;
      }
    }

    if (!lastDataLine) return null;
    const cols = lastDataLine.split('|').map(c => c.trim()).filter(Boolean);
    return {
      ts: cols[0] || '',
      type: cols[1] || '',
      actor: cols[2] || '',
      note: cols[3] || ''
    };
  } catch {
    return null;
  }
}

/**
 * Read the sync state cache (.devpace/.sync-state-cache).
 * Returns a Map<crName, state>. Returns empty Map on any failure.
 * Cache format: plain text, one "CR-xxx=state" per line.
 */
export function readSyncStateCache(projectDir) {
  const cache = new Map();
  try {
    const cachePath = `${projectDir}/.devpace/.sync-state-cache`;
    const content = readFileSync(cachePath, 'utf-8');
    for (const line of content.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      const eqIdx = trimmed.indexOf('=');
      if (eqIdx > 0) {
        cache.set(trimmed.slice(0, eqIdx), trimmed.slice(eqIdx + 1));
      }
    }
  } catch {
    // File doesn't exist or unreadable — return empty cache
  }
  return cache;
}

/**
 * Update a single entry in the sync state cache.
 * Creates the cache file and .devpace/ directory if needed.
 */
export function updateSyncStateCache(projectDir, crName, newState, existingCache) {
  try {
    const cachePath = `${projectDir}/.devpace/.sync-state-cache`;
    const cache = existingCache ?? readSyncStateCache(projectDir);
    cache.set(crName, newState);
    const lines = [];
    for (const [name, state] of cache) {
      lines.push(`${name}=${state}`);
    }
    mkdirSync(dirname(cachePath), { recursive: true });
    writeFileSync(cachePath, lines.join('\n') + '\n', 'utf-8');
  } catch {
    // Cache write failure is non-critical — silent exit
  }
}
