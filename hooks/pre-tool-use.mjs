#!/usr/bin/env node
/**
 * devpace PreToolUse hook — enforcing quality gates and mode constraints
 *
 * Purpose: Enforce devpace iron rules at the mechanism level, not just text-based rules.
 *
 * Enforcement levels:
 *   1. BLOCKING (exit 2): Explore mode writes to .devpace/, Gate 3 bypass attempts
 *   2. ADVISORY (exit 0): Gate 1/2 reminders during normal development flow
 *
 * Iron rules enforced:
 *   - Explore mode: no writes to .devpace/ (devpace-rules.md §2)
 *   - Gate 3: human approval required, no automated state change to approved (devpace-rules.md §2)
 */

import { existsSync } from 'node:fs';
import {
  readStdinJson, getProjectDir, extractFilePath, extractWriteContent,
  isCrFile, readCrState, isDevpaceFile, isAdvanceMode, isStateChangeToApproved
} from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const backlogDir = `${projectDir}/.devpace/backlog`;

// Only act if .devpace exists and has backlog
if (!existsSync(backlogDir)) {
  process.exit(0);
}

const filePath = extractFilePath(input);

// ── ENFORCEMENT 1: Explore mode protection ──────────────────────────
// Iron rule: explore mode must not write to .devpace/ files
if (isDevpaceFile(filePath) && !isAdvanceMode(projectDir)) {
  // Allow writes to .devpace/rules/ (configuration, not state)
  // Allow writes to .devpace/context.md (tech convention tracking)
  const isConfigFile = filePath.includes('.devpace/rules/') || filePath.includes('.devpace/context.md');
  if (!isConfigFile) {
    console.error('devpace:blocked 探索模式下不允许修改 .devpace/ 状态文件。请先进入推进模式（说"帮我实现/修改 X"）再修改。');
    process.exit(2);
  }
}

// ── ENFORCEMENT 2: Gate 3 — human approval required ─────────────────
// Iron rule: in_review → approved transition requires explicit human approval
if (isCrFile(filePath, backlogDir) && existsSync(filePath)) {
  const currentState = readCrState(filePath);

  if (currentState === 'in_review') {
    const newContent = extractWriteContent(input);
    if (isStateChangeToApproved(newContent)) {
      console.error('devpace:blocked Gate 3 要求人类审批。不允许自动将 CR 状态从 in_review 变更为 approved。请等待用户明确批准。');
      process.exit(2);
    }
  }
}

// ── ADVISORY: Quality gate reminders (existing behavior) ────────────
if (isCrFile(filePath, backlogDir) && existsSync(filePath)) {
  const currentState = readCrState(filePath);

  switch (currentState) {
    case 'developing':
      console.log("devpace:gate-reminder CR is in 'developing'. Gate 1 (code quality: lint+test+typecheck) must pass before advancing to 'verifying'.");
      break;
    case 'verifying':
      console.log("devpace:gate-reminder CR is in 'verifying'. Gate 2 (integration test + intent consistency) must pass before advancing to 'in_review'.");
      break;
    case 'in_review':
      console.log("devpace:gate-reminder CR is in 'in_review'. Gate 3 requires human approval. Do not advance without explicit user approval.");
      break;
  }
}

process.exit(0);
