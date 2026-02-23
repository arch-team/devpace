/**
 * devpace Hook shared utilities
 * Pure Node.js ESM — no npm dependencies.
 */

import { readFileSync } from 'node:fs';
import { createInterface } from 'node:readline';

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
  return filePath.includes('.devpace/backlog/CR-');
}

/**
 * Read a CR markdown file and return the value of the "状态" field.
 * CR format: "- **状态**：<value>" (Markdown bold + Chinese/ASCII colon)
 * Returns empty string if not found or file unreadable.
 */
export function readCrState(filePath) {
  try {
    const content = readFileSync(filePath, 'utf-8');
    const match = content.match(/^- \*\*状态\*\*[：:]\s*(.+)$/m);
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
export function isAdvanceMode(projectDir) {
  try {
    const statePath = `${projectDir}/.devpace/state.md`;
    const content = readFileSync(statePath, 'utf-8');
    // Look for "进行中" indicator in the "当前工作" section
    return /\*\*进行中\*\*/.test(content);
  } catch {
    // state.md doesn't exist or unreadable → not initialized, not advance mode
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
