/**
 * Shared utilities for pace-sync scripts.
 * Pure Node.js ESM — no npm dependencies.
 */

import { readdirSync, readFileSync } from 'node:fs';

// ── Configuration Constants (MEDIUM #8: no magic numbers) ───────────

export const CONFIG = Object.freeze({
  EXTRACT_TIMEOUT_MS: 30000,
  OPERATION_DELAY_MS: 1000,
  RATE_LIMIT_RETRY_MS: 60000,
  LABEL_LIST_LIMIT: 200,
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
  const regex = new RegExp(`^- \\*\\*${escapeRegex(fieldName)}\\*\\*[：:]\\s*(.+)$`, 'm');
  const match = content.match(regex);
  if (!match) return null;
  const value = match[1].trim();
  return value || null;
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
