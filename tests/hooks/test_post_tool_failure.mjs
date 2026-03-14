/**
 * Integration tests for hooks/post-tool-failure.mjs
 * Tests the PostToolUseFailure hook by spawning it as a subprocess.
 * Run: node --test tests/hooks/test_post_tool_failure.mjs
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  resolveHookScript, cleanupDir, runHook as _runHook, writeState,
} from './_test-helpers.mjs';

const HOOK_SCRIPT = resolveHookScript(import.meta.url, 'post-tool-failure.mjs');

function runHook(stdinJson, projectDir) {
  return _runHook(HOOK_SCRIPT, stdinJson, projectDir);
}

/** Local variant: creates project with optional advance-mode state.md. */
function createTmpProject(advanceMode) {
  const dir = join(tmpdir(), `devpace-failure-test-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  mkdirSync(join(dir, '.devpace', 'backlog'), { recursive: true });
  if (advanceMode) {
    writeState(dir, '> 目标：测试\n\n- **进行中**：开发中 → CR-001\n\n下一步：继续\n');
  }
  return dir;
}

// ── Tests: No .devpace → silent exit ───────────────────────────────

describe('post-tool-failure: no .devpace', () => {
  it('exits 0 silently when .devpace/backlog does not exist', async () => {
    const dir = join(tmpdir(), `no-devpace-failure-${Date.now()}`);
    mkdirSync(dir, { recursive: true });
    const result = await runHook({ tool_input: { file_path: '/foo.md' } }, dir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
    cleanupDir(dir);
  });
});

// ── Tests: Not in advance mode → silent exit ───────────────────────

describe('post-tool-failure: explore mode (not advance)', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject(false); });
  afterEach(() => { cleanupDir(projectDir); });

  it('exits 0 silently when not in advance mode', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：developing\n');
    const result = await runHook({ tool_input: { file_path: crPath } }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });

  it('exits 0 silently when state.md does not exist', async () => {
    rmSync(join(projectDir, '.devpace', 'state.md'), { force: true });
    const result = await runHook(
      { tool_input: { file_path: join(projectDir, '.devpace', 'backlog', 'CR-001.md') } },
      projectDir
    );
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });
});

// ── Tests: Advance mode + CR file failure → consistency advice ─────

describe('post-tool-failure: advance mode + CR file', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject(true); });
  afterEach(() => { cleanupDir(projectDir); });

  it('outputs consistency advice for CR file write failure', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：developing\n');
    const result = await runHook({ tool_input: { file_path: crPath } }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('tool-failure'), 'Should include tool-failure prefix');
    assert.ok(result.stdout.includes('CR'), 'Should mention CR');
    assert.ok(result.stdout.includes('consistency'), 'Should mention consistency check');
  });
});

// ── Tests: Advance mode + .devpace/ file failure → state check ─────

describe('post-tool-failure: advance mode + .devpace file', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject(true); });
  afterEach(() => { cleanupDir(projectDir); });

  it('outputs state check advice for .devpace/ file failure', async () => {
    const result = await runHook(
      { tool_input: { file_path: join(projectDir, '.devpace', 'state.md') } },
      projectDir
    );
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('tool-failure'), 'Should include tool-failure prefix');
    assert.ok(result.stdout.includes('state.md'), 'Should mention state.md');
  });
});

// ── Tests: Advance mode + other file failure → silent ──────────────

describe('post-tool-failure: advance mode + non-devpace file', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject(true); });
  afterEach(() => { cleanupDir(projectDir); });

  it('exits 0 silently for non-.devpace file failure', async () => {
    const result = await runHook(
      { tool_input: { file_path: join(projectDir, 'src', 'main.js') } },
      projectDir
    );
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });

  it('exits 0 silently when file_path is empty', async () => {
    const result = await runHook({ tool_input: {} }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });
});
