/**
 * Shared utilities for pace-sync scripts.
 * Pure Node.js ESM — no npm dependencies.
 */

import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

// ── Configuration Constants (MEDIUM #8: no magic numbers) ───────────

export const CONFIG = Object.freeze({
  EXTRACT_TIMEOUT_MS: 30000,
  OPERATION_DELAY_MS: 1000,
  RATE_LIMIT_RETRY_MS: 60000,
  LABEL_LIST_LIMIT: 200,
});

export const ENTITY_DIR_MAP = Object.freeze({
  epic: 'epics',
  br: 'requirements',
  pf: 'features',
  cr: 'backlog',
});

// ── Input Validation (CRITICAL #1: prevent command injection) ───────

const REPO_PATTERN = /^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/;

/**
 * Validate GitHub owner/repo format.
 * @param {string} repo
 * @returns {string} validated repo string
 * @throws {Error} if format is invalid
 */
export function validateRepo(repo) {
  if (!repo || !REPO_PATTERN.test(repo)) {
    throw new Error(`Invalid repository format: "${repo}". Expected: owner/repo`);
  }
  return repo;
}

/**
 * Validate issue number is a positive integer.
 * @param {*} num
 * @returns {number} validated integer
 * @throws {Error} if not a valid issue number
 */
export function validateIssueNumber(num) {
  const n = Number(num);
  if (!Number.isInteger(n) || n <= 0) {
    throw new Error(`Invalid issue number: "${num}". Expected positive integer.`);
  }
  return n;
}

// ── Non-Busy-Wait Synchronous Sleep (HIGH #3) ───────────────────────

/**
 * Synchronous sleep without busy-wait CPU consumption.
 * Uses Atomics.wait on a SharedArrayBuffer.
 * @param {number} ms - milliseconds to sleep
 */
export function syncSleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

// ── Markdown Parsing Utilities ──────────────────────────────────────

/**
 * Extract markdown title (# heading) from content.
 * @param {string} content - Markdown file content
 * @returns {string} Title text, or empty string
 */
export function extractTitle(content) {
  const match = content.match(/^# (.+)$/m);
  return match ? match[1].trim() : '';
}

/**
 * Extract a devpace field value: - **fieldName**：value
 * @param {string} content
 * @param {string} fieldName
 * @returns {string|null}
 */
export function extractField(content, fieldName) {
  // 1. Try bullet format: - **fieldName**：value
  const regex = new RegExp(`^- \\*\\*${escapeRegex(fieldName)}\\*\\*[：:]\\s*(.+)$`, 'm');
  const match = content.match(regex);
  if (match) {
    const value = match[1].trim();
    return value || null;
  }

  // 2. Fallback: try table format | fieldName | value |
  const tableRegex = new RegExp(`\\|\\s*${escapeRegex(fieldName)}\\s*\\|\\s*([^|\\n]+?)\\s*\\|`, 'gm');
  let tableMatch;
  while ((tableMatch = tableRegex.exec(content)) !== null) {
    const val = tableMatch[1].trim();
    if (!val || /^[-:]+$/.test(val)) continue;

    // Exclude header rows: if the next line is a separator (|---|---|), skip this match
    const restAfterMatch = content.substring(tableMatch.index);
    const nlPos = restAfterMatch.indexOf('\n');
    if (nlPos >= 0) {
      const nextNl = restAfterMatch.indexOf('\n', nlPos + 1);
      const nextLine = nextNl >= 0
        ? restAfterMatch.substring(nlPos + 1, nextNl)
        : restAfterMatch.substring(nlPos + 1);
      if (/^\|[\s\-:|]+\|/.test(nextLine)) continue;
    }

    return val;
  }

  return null;
}

/**
 * Extract a markdown section from heading to next same-level heading.
 * @param {string} content
 * @param {string} heading - e.g. "## 背景"
 * @returns {string|null}
 */
export function extractSection(content, heading) {
  const escaped = escapeRegex(heading);
  const regex = new RegExp(`${escaped}\\s*\\n([\\s\\S]*?)(?=\\n## |\\n# |$)`);
  const match = content.match(regex);
  return match ? match[1].trim() : null;
}

/**
 * Escape special regex characters in a string.
 * @param {string} str
 * @returns {string}
 */
export function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ── Emoji-to-Status Inference ──────────────────────────────────────

/**
 * Infer entity status from emoji markers in a project.md line.
 * @param {string} line
 * @returns {string} status string
 */
export function inferStatusFromEmoji(line) {
  if (/✅/.test(line)) return '全部CR完成';
  if (/🔄/.test(line)) return '进行中';
  if (/🚀/.test(line)) return '已发布';
  if (/⏸️/.test(line)) return '暂停';
  return '待开始';
}

// ── CLI Argument Utilities ──────────────────────────────────────────

/**
 * Get value of a CLI flag (e.g. --type epic → "epic").
 * @param {string[]} argList
 * @param {string} flag
 * @returns {string|null}
 */
export function getFlagValue(argList, flag) {
  const idx = argList.indexOf(flag);
  return idx >= 0 && idx + 1 < argList.length ? argList[idx + 1] : null;
}

// ── File I/O Utilities ──────────────────────────────────────────────

/**
 * Read directory contents safely.
 * @param {string} dirPath
 * @returns {string[]} file names, or empty array on error
 */
export function safeReadDir(dirPath) {
  try {
    return readdirSync(dirPath);
  } catch {
    return [];
  }
}

/**
 * Read file contents safely.
 * @param {string} filePath
 * @returns {string|null} content, or null on error
 */
export function safeReadFile(filePath) {
  try {
    return readFileSync(filePath, 'utf-8');
  } catch {
    return null;
  }
}

// ── BR Status Cross-Reference ────────────────────────────────────────

/**
 * Build BR status map from Epic files' BR tables.
 * Epic files contain authoritative BR status in their "## 业务需求" table.
 * @param {string} epicsDir - Absolute path to the epics directory
 * @param {function} readFileFn - File read function (default: safeReadFile)
 * @returns {Map<string, string>} Map of BR-ID → status
 */
export function buildBRStatusFromEpics(epicsDir, readFileFn = safeReadFile) {
  const brStatusMap = new Map();
  if (!existsSync(epicsDir)) return brStatusMap;

  const files = safeReadDir(epicsDir).filter(f => /^EPIC-\d+\.md$/.test(f));
  for (const fileName of files) {
    const content = readFileFn(join(epicsDir, fileName));
    if (!content) continue;

    // Parse BR table rows: | BR-X | title | priority | status | ...
    const brRowPattern = /\|\s*(BR-\d+)\s*\|[^|]*\|[^|]*\|\s*([^|]+)/g;
    let match;
    while ((match = brRowPattern.exec(content)) !== null) {
      const brId = match[1];
      const brStatus = match[2].trim();
      if (brStatus && !/^[-:]+$/.test(brStatus) && brStatus !== '状态') {
        brStatusMap.set(brId, brStatus);
      }
    }
  }

  return brStatusMap;
}
