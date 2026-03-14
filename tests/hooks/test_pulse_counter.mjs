/**
 * Integration tests for hooks/pulse-counter.mjs
 * Run: node --test tests/hooks/test_pulse_counter.mjs
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync, readFileSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  resolveHookScript, createTmpProject, cleanupDir, runHook as _runHook,
} from './_test-helpers.mjs';

const HOOK_SCRIPT = resolveHookScript(import.meta.url, 'pulse-counter.mjs');

function runHook(stdinJson, projectDir) {
  return _runHook(HOOK_SCRIPT, stdinJson, projectDir);
}

describe('pulse-counter: no .devpace', () => {
  it('exits 0 when .devpace does not exist', async () => {
    const dir = join(tmpdir(), `no-devpace-pulse-${Date.now()}`);
    mkdirSync(dir, { recursive: true });
    const result = await runHook({}, dir);
    assert.equal(result.exitCode, 0);
    cleanupDir(dir);
  });
});

describe('pulse-counter: counting and reminders', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject('pulse-test', { subdirs: ['.devpace'] });
  });

  afterEach(() => { cleanupDir(projectDir); });

  it('creates counter file on first write', async () => {
    const result = await runHook({}, projectDir);
    assert.equal(result.exitCode, 0);
    const counterPath = join(projectDir, '.devpace', '.pulse-counter');
    assert.ok(existsSync(counterPath), 'Counter file should be created');
    assert.equal(readFileSync(counterPath, 'utf-8'), '1');
  });

  it('increments counter on subsequent writes', async () => {
    const counterPath = join(projectDir, '.devpace', '.pulse-counter');
    writeFileSync(counterPath, '5');
    const result = await runHook({}, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(readFileSync(counterPath, 'utf-8'), '6');
  });

  it('outputs pulse reminder at count 10', async () => {
    const counterPath = join(projectDir, '.devpace', '.pulse-counter');
    writeFileSync(counterPath, '9');
    const result = await runHook({}, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(readFileSync(counterPath, 'utf-8'), '10');
    assert.ok(result.stdout.includes('devpace:write-volume'), 'Should output pulse reminder at 10');
  });

  it('outputs pulse reminder at count 20', async () => {
    const counterPath = join(projectDir, '.devpace', '.pulse-counter');
    writeFileSync(counterPath, '19');
    const result = await runHook({}, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('devpace:write-volume'), 'Should output pulse reminder at 20');
  });

  it('no reminder at non-10 counts', async () => {
    const counterPath = join(projectDir, '.devpace', '.pulse-counter');
    writeFileSync(counterPath, '7');
    const result = await runHook({}, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '', 'Should have no output at count 8');
  });

  it('always exits 0 (advisory)', async () => {
    const counterPath = join(projectDir, '.devpace', '.pulse-counter');
    writeFileSync(counterPath, '9');
    const result = await runHook({}, projectDir);
    assert.equal(result.exitCode, 0, 'Pulse counter should never block');
  });
});
