/**
 * Integration tests for hooks/intent-detect.mjs
 * Run: node --test tests/hooks/test_intent_detect.mjs
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  resolveHookScript, createTmpProject, cleanupDir, runHook as _runHook, writeState,
} from './_test-helpers.mjs';

const HOOK_SCRIPT = resolveHookScript(import.meta.url, 'intent-detect.mjs');

function runHook(stdinJson, projectDir) {
  return _runHook(HOOK_SCRIPT, stdinJson, projectDir);
}

describe('intent-detect: no .devpace', () => {
  it('exits 0 when state.md does not exist', async () => {
    const dir = join(tmpdir(), `no-state-${Date.now()}`);
    mkdirSync(dir, { recursive: true });
    const result = await runHook({ content: '不做了' }, dir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
    cleanupDir(dir);
  });
});

describe('intent-detect: change trigger words', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject('intent-test', { subdirs: ['.devpace'] });
    writeState(projectDir, '> 目标：测试\n');
  });

  afterEach(() => {
    cleanupDir(projectDir);
  });

  const triggerWords = [
    '不做了', '先不搞', '加一个', '改一下',
    '优先级', '延后', '提前', '砍掉',
    '插入', '新增需求', '先做这个', '恢复之前',
  ];

  for (const word of triggerWords) {
    it(`detects change intent: "${word}"`, async () => {
      const result = await runHook({ content: `我想${word}这个功能` }, projectDir);
      assert.equal(result.exitCode, 0);
      assert.ok(result.stdout.includes('devpace:change-detected'), `Should detect "${word}" as change intent`);
    });
  }

  it('no output for non-change prompts', async () => {
    const result = await runHook({ content: '帮我看看这个文件' }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });

  it('no output for empty prompt', async () => {
    const result = await runHook({ content: '' }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });

  it('always exits 0 (advisory, never blocks)', async () => {
    const result = await runHook({ content: '不做了这个任务' }, projectDir);
    assert.equal(result.exitCode, 0, 'Intent detect should never block (exit 2)');
  });

  it('skips detection when technical context words present', async () => {
    const result = await runHook({ content: '恢复之前的 git stash' }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '', 'Should not trigger when tech context detected');
  });

  it('skips detection for code formatting requests', async () => {
    const result = await runHook({ content: '帮我格式化一下代码缩进' }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '', 'Should not trigger for code formatting');
  });
});
