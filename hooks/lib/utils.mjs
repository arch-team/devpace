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
