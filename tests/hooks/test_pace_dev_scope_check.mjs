/**
 * Integration tests for hooks/skill/pace-dev-scope-check.mjs
 * Tests the hook by spawning it as a subprocess with simulated stdin JSON.
 * Run: node --test tests/hooks/test_pace_dev_scope_check.mjs
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  resolveHookScript, createTmpProject, cleanupDir,
  runHook as _sharedRunHook, writeCr, writeState,
} from './_test-helpers.mjs';

const HOOK_SCRIPT = resolveHookScript(import.meta.url, join('skill', 'pace-dev-scope-check.mjs'));

function runHook(stdinJson, projectDir) {
  return _sharedRunHook(HOOK_SCRIPT, stdinJson, projectDir);
}

/** Write state.md with an active CR reference. */
function writeActiveState(projectDir, crId) {
  writeState(projectDir, `> 目标：测试项目\n\n- **进行中**：实现功能 → CR-${crId}\n\n下一步：继续\n`);
}

// ── Tests: No .devpace → exit 0 ────────────────────────────────────

describe('pace-dev-scope-check: no .devpace', () => {
  it('exits 0 when .devpace/backlog does not exist', async () => {
    const dir = join(tmpdir(), `no-devpace-scope-${Date.now()}`);
    mkdirSync(dir, { recursive: true });
    const result = await runHook({ tool_input: { file_path: '/foo.md' } }, dir);
    assert.equal(result.exitCode, 0);
    cleanupDir(dir);
  });
});

// ── Tests: No file_path → exit 0 ───────────────────────────────────

describe('pace-dev-scope-check: no file_path', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject('scope-test'); });
  afterEach(() => { cleanupDir(projectDir); });

  it('exits 0 when tool input has no file_path', async () => {
    const result = await runHook({ tool_input: {} }, projectDir);
    assert.equal(result.exitCode, 0);
  });

  it('exits 0 for empty input', async () => {
    const result = await runHook({}, projectDir);
    assert.equal(result.exitCode, 0);
  });
});

// ── Tests: CR writes — Gate 3 delegated to global hook ───────────────

describe('pace-dev-scope-check: CR writes (Gate 3 delegated to global hook)', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject('scope-test'); });
  afterEach(() => { cleanupDir(projectDir); });

  it('allows all CR writes including approved state (Gate 3 handled by global hook)', async () => {
    const crPath = writeCr(projectDir, '001', '# CR-001\n\n- **状态**：in_review\n');
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-001\n\n- **状态**：approved\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0, 'Gate 3 is no longer enforced here — delegated to global pre-tool-use.mjs');
  });

  it('allows non-approved state change on CR file (exit 0)', async () => {
    const crPath = writeCr(projectDir, '003', '# CR-003\n\n- **状态**：developing\n');
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-003\n\n- **状态**：verifying\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
  });

  it('allows content additions to CR without state change', async () => {
    const crPath = writeCr(projectDir, '004', '# CR-004\n\n- **状态**：developing\n');
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-004\n\n- **状态**：developing\n\n## Notes\nAdded notes.\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
  });
});

// ── Tests: .devpace/ management files → fast-path exit 0 ───────────

describe('pace-dev-scope-check: .devpace fast-path', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject('scope-test'); });
  afterEach(() => { cleanupDir(projectDir); });

  it('allows write to .devpace/state.md', async () => {
    const input = {
      tool_input: {
        file_path: join(projectDir, '.devpace', 'state.md'),
        content: '> updated'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
  });

  it('allows write to .devpace/project.md', async () => {
    const input = {
      tool_input: {
        file_path: join(projectDir, '.devpace', 'project.md'),
        content: '# Project'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
  });
});

// ── Tests: No active CR → allow with info ──────────────────────────

describe('pace-dev-scope-check: no active CR', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject('scope-test'); });
  afterEach(() => { cleanupDir(projectDir); });

  it('allows file write when no state.md exists', async () => {
    const input = {
      tool_input: {
        file_path: join(projectDir, 'src', 'main.js'),
        content: 'console.log("hi")'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('scope-info'), 'Should output scope-info message');
  });

  it('allows file write when state.md has no active CR', async () => {
    writeState(projectDir, '> 目标：测试\n\n- 当前工作：（无）\n');
    const input = {
      tool_input: {
        file_path: join(projectDir, 'src', 'main.js'),
        content: 'console.log("hi")'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
  });
});

// ── Tests: Scope validation with active CR ─────────────────────────

describe('pace-dev-scope-check: scope validation', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject('scope-test');
    writeActiveState(projectDir, '010');
  });
  afterEach(() => { cleanupDir(projectDir); });

  it('allows in-scope file (execution plan path match)', async () => {
    writeCr(projectDir, '010',
      '# CR-010\n\n- **状态**：developing\n\n## 执行计划\n\n**src/auth/login.js**：实现登录逻辑\n'
    );
    const input = {
      tool_input: {
        file_path: join(projectDir, 'src', 'auth', 'login.js'),
        content: 'module.exports = {}'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(!result.stdout.includes('scope-drift'), 'Should NOT warn about scope drift');
  });

  it('allows in-scope file (scope section path match)', async () => {
    writeCr(projectDir, '010',
      '# CR-010\n\n- **状态**：developing\n- **范围**：`hooks/` 目录下的所有文件\n\n## 执行计划\n'
    );
    const input = {
      tool_input: {
        file_path: join(projectDir, 'hooks', 'some-hook.mjs'),
        content: 'export default {}'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(!result.stdout.includes('scope-drift'), 'Should NOT warn about scope drift');
  });

  it('warns (advisory, exit 0) for out-of-scope file', async () => {
    writeCr(projectDir, '010',
      '# CR-010\n\n- **状态**：developing\n\n## 执行计划\n\n**src/auth/login.js**：实现登录逻辑\n'
    );
    const input = {
      tool_input: {
        file_path: join(projectDir, 'docs', 'README.md'),
        content: '# Docs'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0, 'Scope drift is advisory, should not block');
    assert.ok(result.stdout.includes('scope-drift'), 'Should warn about scope drift');
  });

  it('allows all files when CR has no scope patterns yet', async () => {
    writeCr(projectDir, '010',
      '# CR-010\n\n- **状态**：developing\n\n## 意图\n\n概述：初步探索\n'
    );
    const input = {
      tool_input: {
        file_path: join(projectDir, 'anywhere', 'file.txt'),
        content: 'content'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(!result.stdout.includes('scope-drift'), 'No scope patterns → no drift warning');
  });

  it('warns for different file in same directory (startsWith needs prefix match)', async () => {
    writeCr(projectDir, '010',
      '# CR-010\n\n- **状态**：developing\n\n## 执行计划\n\n**src/auth/login.js**：实现登录逻辑\n'
    );
    const input = {
      tool_input: {
        file_path: join(projectDir, 'src', 'auth', 'register.js'),
        content: 'module.exports = {}'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0, 'Should not block, only advisory');
    assert.ok(result.stdout.includes('scope-drift'), 'Different file triggers scope-drift advisory');
  });

  it('allows file matching via includes (substring in path)', async () => {
    writeCr(projectDir, '010',
      '# CR-010\n\n- **状态**：developing\n\n## 执行计划\n\n**src/auth/**：认证模块目录\n'
    );
    const input = {
      tool_input: {
        file_path: join(projectDir, 'src', 'auth', 'register.js'),
        content: 'module.exports = {}'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(!result.stdout.includes('scope-drift'), 'Directory pattern should match via includes');
  });
});

// ── Tests: Degraded state → allow ──────────────────────────────────

describe('pace-dev-scope-check: degradation', () => {
  let projectDir;

  beforeEach(() => { projectDir = createTmpProject('scope-test'); });
  afterEach(() => { cleanupDir(projectDir); });

  it('allows when state.md references non-existent CR', async () => {
    writeState(projectDir, '> 目标：测试\n\n- **进行中**：实现功能 → CR-999\n');
    // CR-999.md does not exist
    const input = {
      tool_input: {
        file_path: join(projectDir, 'src', 'main.js'),
        content: 'code'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
  });
});
