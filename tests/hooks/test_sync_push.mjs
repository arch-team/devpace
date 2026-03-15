/**
 * Integration tests for hooks/sync-push.mjs
 * Tests the PostToolUse hook by spawning it as a subprocess with simulated stdin JSON.
 * Run: node --test tests/hooks/test_sync_push.mjs
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  resolveHookScript, createTmpProject, cleanupDir, runHook as _runHook, writeCr,
} from './_test-helpers.mjs';

const HOOK_SCRIPT = resolveHookScript(import.meta.url, 'sync-push.mjs');

function runHook(stdinJson, projectDir) {
  return _runHook(HOOK_SCRIPT, stdinJson, projectDir);
}

// ── Local helpers (sync-push specific) ──────────────────────────────

function writeSyncMapping(projectDir, content) {
  writeFileSync(
    join(projectDir, '.devpace', 'integrations', 'sync-mapping.md'),
    content || '# Sync Mapping\n\n| CR | External |\n|----|---------|\n| CR-001 | #123 |\n'
  );
}

function writeSyncCache(projectDir, entries) {
  mkdirSync(join(projectDir, '.devpace'), { recursive: true });
  const lines = Object.entries(entries).map(([k, v]) => `${k}=${v}`).join('\n');
  writeFileSync(join(projectDir, '.devpace', '.sync-state-cache'), lines + '\n');
}

// ── Tests: No .devpace → silent exit ───────────────────────────────

describe('sync-push: no .devpace', () => {
  it('exits 0 silently when .devpace/backlog does not exist', async () => {
    const dir = join(tmpdir(), `no-devpace-sync-${Date.now()}`);
    mkdirSync(dir, { recursive: true });
    const result = await runHook({ tool_input: { file_path: '/foo.md' } }, dir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
    cleanupDir(dir);
  });
});

// ── Tests: Non-CR file → silent exit ───────────────────────────────

describe('sync-push: non-CR file', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject('sync-test', { subdirs: ['backlog', 'integrations'] }); });
  afterEach(() => { cleanupDir(projectDir); });

  it('exits 0 silently for non-CR file path', async () => {
    const result = await runHook(
      { tool_input: { file_path: join(projectDir, 'src', 'main.js') } },
      projectDir
    );
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });

  it('exits 0 silently for .devpace/state.md', async () => {
    const result = await runHook(
      { tool_input: { file_path: join(projectDir, '.devpace', 'state.md') } },
      projectDir
    );
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });
});

// ── Tests: No sync-mapping → silent exit ───────────────────────────

describe('sync-push: no sync-mapping', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject('sync-test', { subdirs: ['backlog', 'integrations'] });
    // Remove default integrations dir to simulate no sync-mapping
    rmSync(join(projectDir, '.devpace', 'integrations'), { recursive: true, force: true });
  });
  afterEach(() => { cleanupDir(projectDir); });

  it('exits 0 silently when sync-mapping.md does not exist', async () => {
    const crPath = writeCr(projectDir, '001', '# CR-001\n\n- **状态**：developing\n');
    const result = await runHook({ tool_input: { file_path: crPath } }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });
});

// ── Tests: Cache hit (state unchanged) → silent exit ───────────────

describe('sync-push: cache hit (state unchanged)', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject('sync-test', { subdirs: ['backlog', 'integrations'] });
    writeSyncMapping(projectDir);
  });
  afterEach(() => { cleanupDir(projectDir); });

  it('exits 0 silently when CR state matches cached state', async () => {
    const crPath = writeCr(projectDir, '001',
      '# CR-001\n\n- **状态**：developing\n- **外部关联**：[Issue #123](https://example.com/123)\n'
    );
    writeSyncCache(projectDir, { 'CR-001': 'developing' });
    const result = await runHook({ tool_input: { file_path: crPath } }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '', 'Should be silent when state unchanged');
  });
});

// ── Tests: State transition to merged + external link → directive ──

describe('sync-push: merged transition with external link', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject('sync-test', { subdirs: ['backlog', 'integrations'] });
    writeSyncMapping(projectDir);
  });
  afterEach(() => { cleanupDir(projectDir); });

  it('outputs directive message for merged state with external link', async () => {
    const crPath = writeCr(projectDir, '001',
      '# CR-001\n\n- **状态**：merged\n- **外部关联**：[Issue #123](https://github.com/org/repo/issues/123)\n'
    );
    writeSyncCache(projectDir, { 'CR-001': 'in_review' });
    const result = await runHook({ tool_input: { file_path: crPath } }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('sync-push'), 'Should include sync-push prefix');
    assert.ok(result.stdout.includes('merged'), 'Should mention merged state');
    assert.ok(result.stdout.includes('Issue #123'), 'Should include external link text');
    assert.ok(result.stdout.includes('Suggest'), 'Should use advisory language for merged');
  });

  it('outputs directive for new CR (no cached state) transitioning to merged', async () => {
    const crPath = writeCr(projectDir, '002',
      '# CR-002\n\n- **状态**：merged\n- **外部关联**：[Task ABC](https://linear.app/task/ABC)\n'
    );
    // No cache entry for CR-002
    const result = await runHook({ tool_input: { file_path: crPath } }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('sync-push'));
    assert.ok(result.stdout.includes('merged'));
  });
});

// ── Tests: Other state change + external link → advisory ───────────

describe('sync-push: other state transitions with external link', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject('sync-test', { subdirs: ['backlog', 'integrations'] });
    writeSyncMapping(projectDir);
  });
  afterEach(() => { cleanupDir(projectDir); });

  it('outputs advisory for developing→verifying transition', async () => {
    const crPath = writeCr(projectDir, '001',
      '# CR-001\n\n- **状态**：verifying\n- **外部关联**：[Issue #1](https://example.com/1)\n'
    );
    writeSyncCache(projectDir, { 'CR-001': 'developing' });
    const result = await runHook({ tool_input: { file_path: crPath } }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('sync-push'), 'Should include sync-push prefix');
    assert.ok(result.stdout.includes('verifying'), 'Should mention new state');
    assert.ok(result.stdout.includes('Consider'), 'Should use advisory language');
  });
});

// ── Tests: No external link → silent exit ──────────────────────────

describe('sync-push: no external link', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject('sync-test', { subdirs: ['backlog', 'integrations'] });
    writeSyncMapping(projectDir);
  });
  afterEach(() => { cleanupDir(projectDir); });

  it('exits 0 silently for state change without external link', async () => {
    const crPath = writeCr(projectDir, '001',
      '# CR-001\n\n- **状态**：merged\n'
    );
    writeSyncCache(projectDir, { 'CR-001': 'in_review' });
    const result = await runHook({ tool_input: { file_path: crPath } }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '', 'Should be silent without external link');
  });
});

// ── Tests: CR with no state field → silent exit ────────────────────

describe('sync-push: no state field in CR', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject('sync-test', { subdirs: ['backlog', 'integrations'] });
    writeSyncMapping(projectDir);
  });
  afterEach(() => { cleanupDir(projectDir); });

  it('exits 0 silently when CR has no state field', async () => {
    const crPath = writeCr(projectDir, '001', '# CR-001\n\nNo state field here.\n');
    const result = await runHook({ tool_input: { file_path: crPath } }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });
});
