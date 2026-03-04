#!/usr/bin/env node
/**
 * devpace pace-dev scope check — fast command Hook replacing LLM prompt Hook
 *
 * Replaces the slow prompt-type Hook (~15s LLM per call) with a fast
 * programmatic check (~5ms) for scope validation and Gate 3 enforcement.
 *
 * Checks:
 *   1. Gate 3: Block automated state change to approved (defense-in-depth)
 *   2. Scope validation: Is target file within the active CR's scope?
 *   3. Scope drift warning: Advisory for out-of-scope writes
 *
 * Exit codes:
 *   0 = allow (in scope or advisory warning)
 *   2 = block (Gate 3 violation)
 */

import { readFileSync, existsSync } from 'node:fs';
import {
  readStdinJson, getProjectDir, extractFilePath, extractWriteContent,
  isCrFile, isStateChangeToApproved, isDevpaceFile
} from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const backlogDir = `${projectDir}/.devpace/backlog`;

// Only act if .devpace exists
if (!existsSync(backlogDir)) {
  process.exit(0);
}

const filePath = extractFilePath(input);
if (!filePath) {
  process.exit(0);
}

// ── CHECK 1: Gate 3 — block automated approved state change ──────
if (isCrFile(filePath, backlogDir)) {
  const newContent = extractWriteContent(input);
  if (isStateChangeToApproved(newContent)) {
    console.error('devpace:blocked Gate 3 要求人类审批。不允许自动将 CR 状态变更为 approved。');
    process.exit(2);
  }
  // CR file writes are always in scope during development
  process.exit(0);
}

// ── CHECK 2: Fast-path for .devpace/ management files ────────────
// state.md, project.md, rules/, checks/ — always in scope during pace-dev
if (isDevpaceFile(filePath)) {
  process.exit(0);
}

// ── CHECK 3: Scope validation against active CR intent ───────────
const activeCr = findActiveCr(projectDir);
if (!activeCr) {
  // No active CR found — can't validate scope, allow with warning
  console.log('devpace:scope-info 未找到活跃 CR，无法验证文件范围。');
  process.exit(0);
}

const scopePatterns = extractScopePatterns(activeCr.content);
if (scopePatterns.length === 0) {
  // CR has no scope patterns yet (early developing), allow all
  process.exit(0);
}

const inScope = scopePatterns.some(pattern => matchesScope(filePath, pattern));
if (!inScope) {
  // Advisory warning — do NOT block, just inform
  console.log(`devpace:scope-drift 文件 ${shortenPath(filePath)} 可能不在 CR-${activeCr.id} 的范围内。如有意为之请忽略。`);
}

process.exit(0);

// ── Helper functions ─────────────────────────────────────────────

/**
 * Find the active (developing) CR from state.md.
 * Returns { id, content } or null.
 */
function findActiveCr(projDir) {
  try {
    const statePath = `${projDir}/.devpace/state.md`;
    const stateContent = readFileSync(statePath, 'utf-8');

    // Extract CR reference from state.md "进行中" section
    // Pattern: CR-NNN appears in the active work line
    const crMatch = stateContent.match(/\*\*进行中\*\*[^\n]*?(CR-(\d{3}))/);
    if (!crMatch) return null;

    const crId = crMatch[2];
    const crFileName = `CR-${crId}.md`;
    const crPath = `${projDir}/.devpace/backlog/${crFileName}`;

    if (!existsSync(crPath)) return null;

    return {
      id: crId,
      content: readFileSync(crPath, 'utf-8')
    };
  } catch {
    return null;
  }
}

/**
 * Extract scope patterns from CR content.
 * Sources: 意图.范围, 执行计划 file paths, git branch name patterns.
 */
function extractScopePatterns(crContent) {
  const patterns = [];

  // 1. Extract from 执行计划 (execution plan) — most precise
  //    Format: **[file/path]**：[description]
  const planMatches = crContent.matchAll(/\*\*([^*]+\.[a-z]{1,10})\*\*/g);
  for (const m of planMatches) {
    const path = m[1].trim();
    // Filter out non-path bold text
    if (path.includes('/') || path.includes('.')) {
      patterns.push(path);
    }
  }

  // 2. Extract from 范围 section — broader patterns
  const scopeMatch = crContent.match(/\*\*范围\*\*[：:]\s*(.+?)(?=\n-|\n#|\n$)/s);
  if (scopeMatch) {
    const scopeText = scopeMatch[1];
    // Look for file paths and directory references
    const pathRefs = scopeText.matchAll(/(?:`([^`]+\.[a-z]{1,10})`|`([^`]+\/)`|(\S+\.[a-z]{1,10}))/g);
    for (const m of pathRefs) {
      patterns.push(m[1] || m[2] || m[3]);
    }
    // Look for directory-like patterns (e.g., "hooks/", "skills/pace-dev/")
    const dirRefs = scopeText.matchAll(/(?:^|\s)([\w-]+(?:\/[\w-]+)*\/)/gm);
    for (const m of dirRefs) {
      patterns.push(m[1]);
    }
  }

  // 3. Extract from 用户原话 — catch mentioned file paths
  const origMatch = crContent.match(/\*\*用户原话\*\*[：:]\s*(.+?)(?=\n-|\n#)/s);
  if (origMatch) {
    const origText = origMatch[1];
    const pathRefs = origText.matchAll(/`([^`]+(?:\.[a-z]{1,10}|\/))`/g);
    for (const m of pathRefs) {
      patterns.push(m[1]);
    }
  }

  return [...new Set(patterns)]; // deduplicate
}

/**
 * Check if filePath matches a scope pattern.
 * Supports: exact match, directory prefix, filename match.
 */
function matchesScope(targetPath, pattern) {
  // Normalize: remove leading ./ or /
  const normTarget = targetPath.replace(/^\.?\//, '');
  const normPattern = pattern.replace(/^\.?\//, '');

  // Directory pattern (ends with /)
  if (normPattern.endsWith('/')) {
    return normTarget.includes(normPattern);
  }

  // Exact path match
  if (normTarget.endsWith(normPattern) || normTarget.includes(normPattern)) {
    return true;
  }

  // Same directory match (file in same directory as a scope file)
  const patternDir = normPattern.substring(0, normPattern.lastIndexOf('/'));
  if (patternDir && normTarget.startsWith(patternDir)) {
    return true;
  }

  return false;
}

/**
 * Shorten a file path for display.
 */
function shortenPath(p) {
  const parts = p.split('/');
  return parts.length > 3 ? `.../${parts.slice(-3).join('/')}` : p;
}
