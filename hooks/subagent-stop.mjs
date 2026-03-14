#!/usr/bin/env node
/**
 * devpace SubagentStop hook — state consistency check after fork agent completion
 *
 * Purpose: When a fork context subagent (pace-engineer, pace-pm, pace-analyst) stops,
 * check .devpace/ state consistency. If the subagent was interrupted mid-operation,
 * state.md and CR files may be inconsistent. This hook detects and warns about such cases.
 *
 * This is an advisory hook (exit 0) — outputs warnings for the main session to handle.
 */

import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { readStdinJson, getProjectDir, readCrState } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const devpaceDir = `${projectDir}/.devpace`;
const backlogDir = `${devpaceDir}/backlog`;

// Only act if .devpace exists
if (!existsSync(backlogDir)) {
  process.exit(0);
}

// Extract subagent info from input
// SubagentStop input shape: { agent_name, ... }
const agentName = input?.agent_name ?? input?.tool_input?.agent_name ?? '';

// Only check known devpace agents
const DEVPACE_AGENTS = ['pace-engineer', 'pace-pm', 'pace-analyst'];
if (!DEVPACE_AGENTS.includes(agentName)) {
  process.exit(0);
}

// ── State consistency checks ────────────────────────────────────────

const warnings = [];

// Check 1: Read state.md for active work
let stateContent = '';
try {
  stateContent = readFileSync(`${devpaceDir}/state.md`, 'utf-8');
} catch {
  // state.md unreadable — skip checks
  process.exit(0);
}

const hasActiveWork = /\*\*进行中\*\*/.test(stateContent);

// Check 2: Scan backlog for CR state consistency
try {
  const crFiles = readdirSync(backlogDir).filter(f => f.startsWith('CR-') && f.endsWith('.md'));

  for (const crFile of crFiles) {
    const crPath = join(backlogDir, crFile);
    const crState = readCrState(crPath);

    // Inconsistency: state.md says "进行中" but CR is not in an active state
    if (hasActiveWork && crState === 'created') {
      // Not necessarily inconsistent — there might be other developing CRs
      continue;
    }

    // Inconsistency: CR claims 'verifying' but Gate 1 checks not recorded
    if (crState === 'verifying' && agentName === 'pace-engineer') {
      // Check if the CR has Gate 1 evidence in events
      try {
        const crContent = readFileSync(crPath, 'utf-8');
        const hasGate1Event = /Gate 1/.test(crContent);
        if (!hasGate1Event) {
          warnings.push(`${crFile}: 状态为 verifying 但无 Gate 1 检查记录，可能是 pace-engineer 中断导致`);
        }
      } catch { /* skip unreadable */ }
    }

    // Inconsistency: CR claims 'in_review' but no review summary
    if (crState === 'in_review' && agentName === 'pace-engineer') {
      try {
        const crContent = readFileSync(crPath, 'utf-8');
        const hasGate2Event = /Gate 2/.test(crContent);
        if (!hasGate2Event) {
          warnings.push(`${crFile}: 状态为 in_review 但无 Gate 2 检查记录，可能是 pace-engineer 中断导致`);
        }
      } catch { /* skip unreadable */ }
    }
  }

  // Check 3: state.md says no active work but there are developing CRs
  if (!hasActiveWork) {
    const developingCrs = crFiles.filter(f => {
      const state = readCrState(join(backlogDir, f));
      return state === 'developing' || state === 'verifying';
    });
    if (developingCrs.length > 0) {
      warnings.push(`state.md 无进行中工作，但 ${developingCrs.join(', ')} 仍在活跃状态，建议更新 state.md`);
    }
  }
} catch {
  // backlog unreadable — skip
}

// Output warnings
if (warnings.length > 0) {
  console.log(`devpace:subagent-check ${agentName} 结束后状态检查发现 ${warnings.length} 项不一致：`);
  for (const w of warnings) {
    console.log(`  - ${w}`);
  }
  console.log('建议检查并修正上述状态，或执行 /pace-status 确认当前进度。');
}

process.exit(0);
