/**
 * Shared test helpers for hook integration tests.
 * Eliminates duplication of runHook / createTmpProject / cleanupDir across test files.
 */
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

/**
 * Resolve the absolute path to a hook script relative to the calling test file.
 * @param {string} importMetaUrl - import.meta.url of the calling file
 * @param {string} hookRelPath - relative path from hooks/ dir, e.g. 'post-cr-update.mjs'
 */
export function resolveHookScript(importMetaUrl, hookRelPath) {
  const callerDir = dirname(fileURLToPath(importMetaUrl));
  return join(callerDir, '..', '..', 'hooks', hookRelPath);
}

/**
 * Create a temporary project directory with .devpace/ structure.
 * @param {string} prefix - prefix for the tmp dir name
 * @param {object} [options]
 * @param {string[]} [options.subdirs] - subdirs to create under .devpace/ (default: ['.devpace', 'backlog'])
 */
export function createTmpProject(prefix, { subdirs } = {}) {
  const dir = join(tmpdir(), `devpace-${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  const dirs = subdirs || ['.devpace', 'backlog'];
  // Build the deepest path: join all subdirs under .devpace if 'backlog' is present,
  // otherwise just create .devpace with the specified subdirs
  if (dirs.includes('backlog')) {
    mkdirSync(join(dir, '.devpace', 'backlog'), { recursive: true });
  } else {
    mkdirSync(join(dir, '.devpace'), { recursive: true });
  }
  // Create any additional subdirs
  for (const sub of dirs) {
    if (sub !== '.devpace' && sub !== 'backlog') {
      mkdirSync(join(dir, '.devpace', sub), { recursive: true });
    }
  }
  return dir;
}

/**
 * Remove a temporary directory.
 */
export function cleanupDir(dir) {
  if (existsSync(dir)) {
    rmSync(dir, { recursive: true, force: true });
  }
}

/**
 * Run a hook script as a subprocess with JSON on stdin.
 * @param {string} hookScript - absolute path to the hook script
 * @param {object} stdinJson - JSON object to pass on stdin
 * @param {string} projectDir - CLAUDE_PROJECT_DIR value
 * @returns {Promise<{exitCode: number, stdout: string, stderr: string}>}
 */
export function runHook(hookScript, stdinJson, projectDir) {
  return new Promise((resolve) => {
    const child = spawn('node', [hookScript], {
      env: { ...process.env, CLAUDE_PROJECT_DIR: projectDir },
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (data) => { stdout += data.toString(); });
    child.stderr.on('data', (data) => { stderr += data.toString(); });
    child.on('close', (code) => {
      resolve({ exitCode: code, stdout: stdout.trim(), stderr: stderr.trim() });
    });
    child.stdin.write(JSON.stringify(stdinJson));
    child.stdin.end();
  });
}

/**
 * Write a CR file into .devpace/backlog/.
 * @returns {string} the full path to the CR file
 */
export function writeCr(projectDir, crId, content) {
  const crPath = join(projectDir, '.devpace', 'backlog', `CR-${crId}.md`);
  writeFileSync(crPath, content);
  return crPath;
}

/**
 * Write state.md into .devpace/.
 */
export function writeState(projectDir, content) {
  writeFileSync(join(projectDir, '.devpace', 'state.md'), content);
}
