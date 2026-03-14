/**
 * Integration tests for hooks/subagent-stop.mjs
 * Run: node --test tests/hooks/test_subagent_stop.mjs
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  resolveHookScript, createTmpProject, cleanupDir, runHook as _runHook,
} from './_test-helpers.mjs';

const HOOK_SCRIPT = resolveHookScript(import.meta.url, 'subagent-stop.mjs');

function runHook(stdinJson, projectDir) {
  return _runHook(HOOK_SCRIPT, stdinJson, projectDir);
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
    projectDir = createTmpProject('subagent-test');
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
    projectDir = createTmpProject('subagent-test');
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
