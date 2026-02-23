/**
 * Integration tests for hooks/post-cr-update.mjs
 * Run: node --test tests/hooks/test_post_cr_update.mjs
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const HOOK_SCRIPT = join(__dirname, '..', '..', 'hooks', 'post-cr-update.mjs');

function createTmpProject() {
  const dir = join(tmpdir(), `devpace-post-test-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  mkdirSync(join(dir, '.devpace', 'backlog'), { recursive: true });
  return dir;
}

function cleanupDir(dir) {
  if (existsSync(dir)) {
    rmSync(dir, { recursive: true, force: true });
  }
}

function runHook(stdinJson, projectDir) {
  return new Promise((resolve) => {
    const child = spawn('node', [HOOK_SCRIPT], {
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

describe('post-cr-update: no .devpace', () => {
  it('exits 0 when .devpace/backlog does not exist', async () => {
    const dir = join(tmpdir(), `no-devpace-post-${Date.now()}`);
    mkdirSync(dir, { recursive: true });
    const result = await runHook({ tool_input: { file_path: '/foo.md' } }, dir);
    assert.equal(result.exitCode, 0);
    cleanupDir(dir);
  });
});

describe('post-cr-update: merged CR detection', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject();
  });

  afterEach(() => {
    cleanupDir(projectDir);
  });

  it('outputs post-merge reminder when CR is merged', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：merged\n');
    const input = { tool_input: { file_path: crPath } };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('devpace:post-merge'), 'Should output post-merge reminder');
    assert.ok(result.stdout.includes('CR-001'), 'Should include CR name');
  });

  it('no output for non-merged CR', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-002.md');
    writeFileSync(crPath, '# CR-002\n\n- **状态**：developing\n');
    const input = { tool_input: { file_path: crPath } };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '', 'Should have no output for non-merged CR');
  });

  it('no output for non-CR file write', async () => {
    const input = { tool_input: { file_path: join(projectDir, 'src', 'main.js') } };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });
});
