/**
 * Integration tests for hooks/intent-detect.mjs
 * Run: node --test tests/hooks/test_intent_detect.mjs
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
const HOOK_SCRIPT = join(__dirname, '..', '..', 'hooks', 'intent-detect.mjs');

function createTmpProject() {
  const dir = join(tmpdir(), `devpace-intent-test-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  mkdirSync(join(dir, '.devpace'), { recursive: true });
  writeFileSync(join(dir, '.devpace', 'state.md'), '> 目标：测试\n');
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
    projectDir = createTmpProject();
  });

  afterEach(() => {
    cleanupDir(projectDir);
  });

  const triggerWords = [
    '不做了', '先不搞', '加一个', '改一下',
    '优先级', '延后', '提前', '砍掉',
    '插入', '新增需求', '先做这个', '恢复之前'
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
});
