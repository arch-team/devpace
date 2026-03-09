#!/usr/bin/env node
/**
 * PostToolUse hook — automatic Schema validation after .devpace/ file writes.
 *
 * Advisory only (exit 0) — outputs warnings/errors but never blocks.
 * Runs validate-schema.mjs on the written file if it's a validatable type
 * (CR, state, project, PF, BR).
 *
 * Exit codes:
 *   0 = always (advisory, non-blocking)
 */

import { existsSync } from 'node:fs';
import { basename, join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { readStdinJson, getProjectDir, extractFilePath, isDevpaceFile } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const filePath = extractFilePath(input);

// Only check .devpace/ files
if (!filePath || !isDevpaceFile(filePath)) {
  process.exit(0);
}

// Only check validatable file types
const name = basename(filePath);
const isValidatable =
  name === 'state.md' ||
  name === 'project.md' ||
  /^CR-\d{3}\.md$/.test(name) ||
  /^PF-\d{3}\.md$/.test(name) ||
  /^BR-\d{3}\.md$/.test(name);

if (!isValidatable) {
  process.exit(0);
}

// Find .devpace directory from file path
const devpaceMatch = filePath.match(/(.+\/.devpace)\//);
if (!devpaceMatch) {
  process.exit(0);
}
const devpaceDir = devpaceMatch[1];

// Run validation
try {
  const scriptDir = new URL('.', import.meta.url).pathname;
  const scriptPath = join(scriptDir, '..', 'scripts', 'validate-schema.mjs');

  if (!existsSync(scriptPath)) {
    process.exit(0); // Script not available, skip silently
  }

  let output;
  try {
    output = execFileSync(
      'node', [scriptPath, devpaceDir, '--file', filePath],
      { encoding: 'utf-8', timeout: 5000, stdio: ['pipe', 'pipe', 'pipe'] }
    );
  } catch (execErr) {
    // validate-schema.mjs exits 1 on errors — capture stdout from the error
    output = execErr.stdout || '';
  }

  if (!output) { process.exit(0); }
  const result = JSON.parse(output);
  if (!result.valid) {
    const r = result.results[0];
    const issues = [...r.errors.map(e => `error: ${e}`), ...r.warnings.map(w => `warning: ${w}`)];
    console.log(`devpace:schema-check ${name} 校验发现 ${r.errors.length} 个错误、${r.warnings.length} 个警告：${issues.slice(0, 3).join('; ')}${issues.length > 3 ? ` (+${issues.length - 3} more)` : ''}`);
  }
} catch {
  // Validation failure is non-critical — skip silently
}

process.exit(0);
