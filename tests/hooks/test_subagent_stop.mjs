/**
 * Integration tests for hooks/subagent-stop.mjs
 * Run: node --test tests/hooks/test_subagent_stop.mjs
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
const HOOK_SCRIPT = join(__dirname, '..', '..', 'hooks', 'subagent-stop.mjs');

function createTmpProject() {
  const dir = join(tmpdir(), `devpace-subagent-test-${Date.now()}-${Math.random().toString(36).slice(2)}`);
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

describe('subagent-stop: no .devpace', () => {
  it('exits 0 when .devpace does not exist', async () => {
    const dir = join(tmpdir(), `no-devpace-sub-${Date.now()}`);
    mkdirSync(dir, { recursive: true });
    const result = await runHook({ agent_name: 'pace-engineer' }, dir);
    assert.equal(result.exitCode, 0);
    cleanupDir(dir);
  });
});

describe('subagent-stop: non-devpace agents', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject();
    writeFileSync(join(projectDir, '.devpace', 'state.md'), '> 目标：测试\n');
  });

  afterEach(() => { cleanupDir(projectDir); });

  it('ignores non-devpace agents', async () => {
    const result = await runHook({ agent_name: 'some-other-agent' }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '');
  });
});

describe('subagent-stop: consistency checks', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject();
  });

  afterEach(() => { cleanupDir(projectDir); });

  it('detects developing CR with no active work in state.md', async () => {
    writeFileSync(
      join(projectDir, '.devpace', 'state.md'),
      '> 目标：测试\n\n- 当前工作：（无）\n\n下一步：规划\n'
    );
    writeFileSync(
      join(projectDir, '.devpace', 'backlog', 'CR-001.md'),
      '# CR-001\n\n- **状态**：developing\n'
    );
    const result = await runHook({ agent_name: 'pace-engineer' }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('devpace:subagent-check'), 'Should output consistency warning');
    assert.ok(result.stdout.includes('CR-001'), 'Should mention the inconsistent CR');
  });

  it('detects verifying CR without Gate 1 evidence', async () => {
    writeFileSync(
      join(projectDir, '.devpace', 'state.md'),
      '> 目标：测试\n\n- **进行中**：实现中\n\n下一步：继续\n'
    );
    writeFileSync(
      join(projectDir, '.devpace', 'backlog', 'CR-001.md'),
      '# CR-001\n\n- **状态**：verifying\n\n## 事件\n\n无记录。\n'
    );
    const result = await runHook({ agent_name: 'pace-engineer' }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('Gate 1'), 'Should warn about missing Gate 1 evidence');
  });

  it('no warnings when state is consistent', async () => {
    writeFileSync(
      join(projectDir, '.devpace', 'state.md'),
      '> 目标：测试\n\n- **进行中**：实现用户认证\n\n下一步：继续\n'
    );
    writeFileSync(
      join(projectDir, '.devpace', 'backlog', 'CR-001.md'),
      '# CR-001\n\n- **状态**：developing\n\n## 事件\n\n正在开发。\n'
    );
    const result = await runHook({ agent_name: 'pace-engineer' }, projectDir);
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, '', 'Should have no warnings when consistent');
  });

  it('always exits 0 (advisory, never blocks)', async () => {
    writeFileSync(
      join(projectDir, '.devpace', 'state.md'),
      '> 目标：测试\n\n- 当前工作：（无）\n'
    );
    writeFileSync(
      join(projectDir, '.devpace', 'backlog', 'CR-001.md'),
      '# CR-001\n\n- **状态**：developing\n'
    );
    const result = await runHook({ agent_name: 'pace-engineer' }, projectDir);
    assert.equal(result.exitCode, 0, 'SubagentStop should never block');
  });
});
