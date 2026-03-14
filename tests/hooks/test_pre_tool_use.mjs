/**
 * Integration tests for hooks/pre-tool-use.mjs
 * Tests the hook by spawning it as a subprocess with simulated stdin JSON.
 * Run: node --test tests/hooks/test_pre_tool_use.mjs
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
const HOOK_SCRIPT = join(__dirname, '..', '..', 'hooks', 'pre-tool-use.mjs');

// ── Test helpers ────────────────────────────────────────────────────

function createTmpProject() {
  const dir = join(tmpdir(), `devpace-hook-test-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  mkdirSync(join(dir, '.devpace', 'backlog'), { recursive: true });
  return dir;
}

function cleanupDir(dir) {
  if (existsSync(dir)) {
    rmSync(dir, { recursive: true, force: true });
  }
}

/**
 * Run the pre-tool-use hook with given stdin JSON and env.
 * Returns { exitCode, stdout, stderr }.
 */
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

// ── Tests: No .devpace → exit 0 ────────────────────────────────────

describe('pre-tool-use: no .devpace', () => {
  it('exits 0 when .devpace/backlog does not exist', async () => {
    const dir = join(tmpdir(), `no-devpace-${Date.now()}`);
    mkdirSync(dir, { recursive: true });
    const result = await runHook({ tool_input: { file_path: '/foo.md' } }, dir);
    assert.equal(result.exitCode, 0);
    cleanupDir(dir);
  });
});

// ── Tests: Explore mode enforcement ─────────────────────────────────

describe('pre-tool-use: explore mode enforcement', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject();
    // state.md with NO active work → explore mode
    writeFileSync(
      join(projectDir, '.devpace', 'state.md'),
      '> 目标：测试项目\n\n- 当前工作：（无）\n\n下一步：规划\n'
    );
  });

  afterEach(() => {
    cleanupDir(projectDir);
  });

  it('blocks write to .devpace/state.md in explore mode (exit 2)', async () => {
    const input = {
      tool_input: {
        file_path: join(projectDir, '.devpace', 'state.md'),
        content: '> 目标：修改后\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 2, `Expected exit 2 but got ${result.exitCode}. stderr: ${result.stderr}`);
    assert.ok(result.stderr.includes('devpace:blocked'), 'Should output blocked message');
  });

  it('allows write to CR file in explore mode when no state escalation', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：created\n');
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-001\n\n- **状态**：created\n- **优先级**：high\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0, `Expected exit 0 (management Skill writes allowed) but got ${result.exitCode}`);
  });

  it('blocks CR state escalation to developing in explore mode (exit 2)', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：created\n');
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-001\n\n- **状态**：developing\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 2, `Expected exit 2 (state escalation blocked) but got ${result.exitCode}`);
    assert.ok(result.stderr.includes('devpace:blocked'), 'Should output blocked message');
  });

  it('allows new CR creation in explore mode (file does not exist)', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-NEW.md');
    // File does not exist — new CR creation by pace-change
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-NEW\n\n- **状态**：created\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0, `Expected exit 0 (new CR creation allowed) but got ${result.exitCode}`);
  });

  it('allows write to .devpace/project.md in explore mode', async () => {
    const input = {
      tool_input: {
        file_path: join(projectDir, '.devpace', 'project.md'),
        content: '# Project\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0, 'Management files like project.md should be allowed in explore mode');
  });

  it('allows write to .devpace/rules/ in explore mode (config files)', async () => {
    mkdirSync(join(projectDir, '.devpace', 'rules'), { recursive: true });
    const input = {
      tool_input: {
        file_path: join(projectDir, '.devpace', 'rules', 'checks.md'),
        content: '## Quality checks\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0, `Expected exit 0 but got ${result.exitCode}`);
  });

  it('allows write to .devpace/context.md in explore mode', async () => {
    const input = {
      tool_input: {
        file_path: join(projectDir, '.devpace', 'context.md'),
        content: '# Context\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0, `Expected exit 0 but got ${result.exitCode}`);
  });

  it('allows write to non-.devpace files in explore mode', async () => {
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

// ── Tests: Advance mode allows writes ───────────────────────────────

describe('pre-tool-use: advance mode allows .devpace writes', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject();
    // state.md with active work → advance mode
    writeFileSync(
      join(projectDir, '.devpace', 'state.md'),
      '> 目标：测试项目\n\n- **进行中**：实现用户认证 → 编写中间件\n\n下一步：完成测试\n'
    );
  });

  afterEach(() => {
    cleanupDir(projectDir);
  });

  it('allows write to .devpace/state.md in advance mode', async () => {
    const input = {
      tool_input: {
        file_path: join(projectDir, '.devpace', 'state.md'),
        content: '> 目标：测试项目\n\n- **进行中**：更新\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
  });

  it('allows write to CR files in advance mode', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：developing\n');
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-001\n\n- **状态**：developing\n- Updated\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
  });
});

// ── Tests: Gate 3 enforcement ───────────────────────────────────────

describe('pre-tool-use: Gate 3 enforcement', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject();
    // Advance mode active
    writeFileSync(
      join(projectDir, '.devpace', 'state.md'),
      '> 目标：测试项目\n\n- **进行中**：审核阶段\n\n下一步：等待审批\n'
    );
  });

  afterEach(() => {
    cleanupDir(projectDir);
  });

  it('blocks state change from in_review to approved (exit 2)', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：in_review\n');
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-001\n\n- **状态**：approved\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 2, `Expected exit 2 (Gate 3 block) but got ${result.exitCode}`);
    assert.ok(result.stderr.includes('Gate 3'), 'Should mention Gate 3');
  });

  it('allows non-state-change writes to in_review CR', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：in_review\n');
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-001\n\n- **状态**：in_review\n\n## Review 摘要\n\n改了 X 因为 Y\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0, 'Should allow review content additions');
  });

  it('allows state change on non-in_review CR', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-002.md');
    writeFileSync(crPath, '# CR-002\n\n- **状态**：developing\n');
    const input = {
      tool_input: {
        file_path: crPath,
        content: '# CR-002\n\n- **状态**：verifying\n'
      }
    };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
  });
});

// ── Tests: Advisory gate reminders ──────────────────────────────────

describe('pre-tool-use: advisory gate reminders', () => {
  let projectDir;

  beforeEach(() => {
    projectDir = createTmpProject();
    writeFileSync(
      join(projectDir, '.devpace', 'state.md'),
      '> 目标：测试项目\n\n- **进行中**：开发中\n\n下一步：继续\n'
    );
  });

  afterEach(() => {
    cleanupDir(projectDir);
  });

  it('outputs Gate 1 reminder for developing CR', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：developing\n');
    const input = { tool_input: { file_path: crPath, content: '# update' } };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('Gate 1'), 'Should include Gate 1 reminder');
  });

  it('outputs Gate 2 reminder for verifying CR', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：verifying\n');
    const input = { tool_input: { file_path: crPath, content: '# update' } };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('Gate 2'), 'Should include Gate 2 reminder');
  });

  it('outputs Gate 3 reminder for in_review CR (non-blocking write)', async () => {
    const crPath = join(projectDir, '.devpace', 'backlog', 'CR-001.md');
    writeFileSync(crPath, '# CR-001\n\n- **状态**：in_review\n');
    // Write that doesn't change state to approved → advisory only
    const input = { tool_input: { file_path: crPath, content: '# CR-001\n\n- **状态**：in_review\n## Notes\n' } };
    const result = await runHook(input, projectDir);
    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('Gate 3'), 'Should include Gate 3 reminder');
  });
});
