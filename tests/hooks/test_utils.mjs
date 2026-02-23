/**
 * Unit tests for hooks/lib/utils.mjs
 * Run: node --test tests/hooks/test_utils.mjs
 */
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

import {
  getProjectDir,
  extractFilePath,
  isCrFile,
  readCrState,
  isDevpaceFile,
  isAdvanceMode,
  extractWriteContent,
  isStateChangeToApproved
} from '../../hooks/lib/utils.mjs';

// ── Test helpers ────────────────────────────────────────────────────

function createTmpDir() {
  const dir = join(tmpdir(), `devpace-test-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  mkdirSync(dir, { recursive: true });
  return dir;
}

function cleanupDir(dir) {
  if (existsSync(dir)) {
    rmSync(dir, { recursive: true, force: true });
  }
}

// ── extractFilePath ─────────────────────────────────────────────────

describe('extractFilePath', () => {
  it('extracts from { tool_input: { file_path } }', () => {
    const input = { tool_input: { file_path: '/foo/bar.md' } };
    assert.equal(extractFilePath(input), '/foo/bar.md');
  });

  it('extracts from flat { file_path }', () => {
    const input = { file_path: '/foo/bar.md' };
    assert.equal(extractFilePath(input), '/foo/bar.md');
  });

  it('returns empty string for missing file_path', () => {
    assert.equal(extractFilePath({}), '');
    assert.equal(extractFilePath(null), '');
    assert.equal(extractFilePath(undefined), '');
  });
});

// ── isCrFile ────────────────────────────────────────────────────────

describe('isCrFile', () => {
  const backlogDir = '/project/.devpace/backlog';

  it('returns true for CR files', () => {
    assert.equal(isCrFile('/project/.devpace/backlog/CR-001.md', backlogDir), true);
    assert.equal(isCrFile('/project/.devpace/backlog/CR-042-auth-login.md', backlogDir), true);
  });

  it('returns false for non-CR files', () => {
    assert.equal(isCrFile('/project/.devpace/state.md', backlogDir), false);
    assert.equal(isCrFile('/project/src/main.js', backlogDir), false);
    assert.equal(isCrFile('', backlogDir), false);
  });

  it('returns false for null/undefined', () => {
    assert.equal(isCrFile(null, backlogDir), false);
    assert.equal(isCrFile(undefined, backlogDir), false);
  });
});

// ── readCrState ─────────────────────────────────────────────────────

describe('readCrState', () => {
  let tmpDir;

  it('reads developing state with Chinese colon', () => {
    tmpDir = createTmpDir();
    const crFile = join(tmpDir, 'CR-001.md');
    writeFileSync(crFile, '# CR-001\n\n- **状态**：developing\n- **类型**：feature\n');
    assert.equal(readCrState(crFile), 'developing');
    cleanupDir(tmpDir);
  });

  it('reads in_review state with ASCII colon', () => {
    tmpDir = createTmpDir();
    const crFile = join(tmpDir, 'CR-002.md');
    writeFileSync(crFile, '# CR-002\n\n- **状态**: in_review\n');
    assert.equal(readCrState(crFile), 'in_review');
    cleanupDir(tmpDir);
  });

  it('returns empty string for non-existent file', () => {
    assert.equal(readCrState('/nonexistent/CR-999.md'), '');
  });

  it('returns empty string for file without state field', () => {
    tmpDir = createTmpDir();
    const crFile = join(tmpDir, 'CR-003.md');
    writeFileSync(crFile, '# CR-003\n\nSome content without state.\n');
    assert.equal(readCrState(crFile), '');
    cleanupDir(tmpDir);
  });
});

// ── isDevpaceFile ───────────────────────────────────────────────────

describe('isDevpaceFile', () => {
  it('returns true for .devpace/ paths', () => {
    assert.equal(isDevpaceFile('/project/.devpace/state.md'), true);
    assert.equal(isDevpaceFile('/project/.devpace/backlog/CR-001.md'), true);
    assert.equal(isDevpaceFile('/project/.devpace/rules/checks.md'), true);
  });

  it('returns false for non-.devpace paths', () => {
    assert.equal(isDevpaceFile('/project/src/main.js'), false);
    assert.equal(isDevpaceFile('/project/README.md'), false);
  });

  it('returns false for empty/null', () => {
    assert.equal(isDevpaceFile(''), false);
    assert.equal(isDevpaceFile(null), false);
    assert.equal(isDevpaceFile(undefined), false);
  });
});

// ── isAdvanceMode ───────────────────────────────────────────────────

describe('isAdvanceMode', () => {
  let tmpDir;

  it('returns true when state.md has active work', () => {
    tmpDir = createTmpDir();
    mkdirSync(join(tmpDir, '.devpace'), { recursive: true });
    writeFileSync(
      join(tmpDir, '.devpace/state.md'),
      '> 目标：测试项目\n\n- **进行中**：实现用户认证 → 编写中间件\n\n下一步：完成测试\n'
    );
    assert.equal(isAdvanceMode(tmpDir), true);
    cleanupDir(tmpDir);
  });

  it('returns false when state.md has no active work', () => {
    tmpDir = createTmpDir();
    mkdirSync(join(tmpDir, '.devpace'), { recursive: true });
    writeFileSync(
      join(tmpDir, '.devpace/state.md'),
      '> 目标：测试项目\n\n- 当前工作：（无）\n\n下一步：规划\n'
    );
    assert.equal(isAdvanceMode(tmpDir), false);
    cleanupDir(tmpDir);
  });

  it('returns false when state.md does not exist', () => {
    tmpDir = createTmpDir();
    assert.equal(isAdvanceMode(tmpDir), false);
    cleanupDir(tmpDir);
  });
});

// ── extractWriteContent ─────────────────────────────────────────────

describe('extractWriteContent', () => {
  it('extracts content from Write tool input', () => {
    const input = { tool_input: { file_path: '/foo.md', content: 'hello world' } };
    assert.equal(extractWriteContent(input), 'hello world');
  });

  it('extracts new_string from Edit tool input', () => {
    const input = { tool_input: { file_path: '/foo.md', old_string: 'old', new_string: 'new' } };
    assert.equal(extractWriteContent(input), 'new');
  });

  it('returns empty string for missing content', () => {
    assert.equal(extractWriteContent({}), '');
    assert.equal(extractWriteContent(null), '');
  });
});

// ── isStateChangeToApproved ─────────────────────────────────────────

describe('isStateChangeToApproved', () => {
  it('detects state change to approved with Chinese colon', () => {
    assert.equal(isStateChangeToApproved('- **状态**：approved'), true);
  });

  it('detects state change to approved with ASCII colon', () => {
    assert.equal(isStateChangeToApproved('- **状态**: approved'), true);
  });

  it('does not flag other state changes', () => {
    assert.equal(isStateChangeToApproved('- **状态**：developing'), false);
    assert.equal(isStateChangeToApproved('- **状态**：in_review'), false);
    assert.equal(isStateChangeToApproved('- **状态**：merged'), false);
  });

  it('returns false for empty/null', () => {
    assert.equal(isStateChangeToApproved(''), false);
    assert.equal(isStateChangeToApproved(null), false);
    assert.equal(isStateChangeToApproved(undefined), false);
  });
});
