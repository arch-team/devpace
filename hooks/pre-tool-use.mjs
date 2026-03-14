#!/usr/bin/env node
/**
 * devpace PreToolUse hook — enforcing quality gates and mode constraints
 *
 * Purpose: Enforce devpace iron rules at the mechanism level, not just text-based rules.
 *
 * Enforcement levels:
 *   1. BLOCKING (exit 2): Explore mode state escalation, Gate 3 bypass attempts
 *   2. ADVISORY (exit 0): Gate 1/2 reminders during normal development flow
 *
 * Iron rules enforced:
 *   - Explore mode: block state.md writes and CR state escalation to advance-mode
 *     states (developing/verifying/in_review). Allow other .devpace/ writes so
 *     management Skills (pace-change, pace-biz, pace-plan) can operate.
 *   - Gate 3: human approval required, no automated state change to approved (devpace-rules.md §2)
 */

import { existsSync } from 'node:fs';
import {
  readStdinJson, getProjectDir, extractFilePath, extractWriteContent,
  isCrFile, readCrState, isDevpaceFile, isAdvanceMode, isStateChangeToApproved,
  isStateEscalation, CR_STATES
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
// Narrowed scope: only block high-risk state operations in explore mode.
// Management Skills (pace-change, pace-biz, pace-plan) need to write to
// .devpace/ files even without an active CR, so we only block:
//   1. state.md direct modification — progress state shouldn't change in explore mode
//   2. CR state escalation — setting developing/verifying/in_review requires advance mode
if (isDevpaceFile(filePath) && !isAdvanceMode(projectDir)) {
  const isStateMd = filePath.endsWith('/state.md') || filePath.endsWith('/.devpace/state.md');
  const isCrStateEsc = isCrFile(filePath, backlogDir)
    && isStateEscalation(extractWriteContent(input));

  if (isStateMd || isCrStateEsc) {
    console.error('devpace:blocked 探索模式禁止修改进度状态（state.md 或 CR 状态升级）。ACTION: 告知用户需要先进入推进模式，引导用户说"帮我实现 X"或"开始做 CR-NNN"以激活 /pace-dev。');
    process.exit(2);
  }
}

// ── ENFORCEMENT 2 + ADVISORY: Gate checks ───────────────────────────
// Single read for both Gate 3 enforcement and advisory reminders
if (isCrFile(filePath, backlogDir) && existsSync(filePath)) {
  const currentState = readCrState(filePath);

  // Gate 3: human approval required — in_review → approved blocked
  if (currentState === CR_STATES.IN_REVIEW) {
    const newContent = extractWriteContent(input);
    if (isStateChangeToApproved(newContent)) {
      console.error('devpace:blocked Gate 3 铁律：CR 从 in_review→approved 必须由人类明确批准。ACTION: 向用户展示 review 摘要（diff 概要+验收标准对比），然后询问是否批准该变更，等待用户回复批准/approved后再修改状态。');
      process.exit(2);
    }
  }

  // Advisory: Quality gate reminders
  switch (currentState) {
    case CR_STATES.DEVELOPING:
      console.log("devpace:gate-reminder CR 状态 developing。推进到 verifying 前须通过 Gate 1。ACTION: 执行 lint+test+typecheck，全部通过后在 CR 事件表记录 gate1_pass，再将状态改为 verifying。");
      break;
    case CR_STATES.VERIFYING:
      console.log("devpace:gate-reminder CR 状态 verifying。推进到 in_review 前须通过 Gate 2。ACTION: 执行集成测试+意图一致性检查（对比 CR 验收标准与实际实现），通过后在事件表记录 gate2_pass，再将状态改为 in_review。");
      break;
    case CR_STATES.IN_REVIEW:
      console.log("devpace:gate-reminder CR 状态 in_review。Gate 3 须人类批准。ACTION: 向用户展示变更摘要（diff 概要+验收标准对比），等待用户明确说'批准'。");
      break;
  }
}

process.exit(0);
