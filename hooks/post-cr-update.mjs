#!/usr/bin/env node
/**
 * devpace PostToolUse hook — detect CR merged state and trigger knowledge pipeline
 *
 * Purpose: After a Write/Edit to a CR file, check if the CR transitioned to 'merged'.
 * If so, output a signal reference for Claude to execute the §11 post-merge pipeline.
 * Also detects gate failures and rejections as learning triggers.
 *
 * This is an advisory hook (exit 0), not blocking.
 */

import { existsSync, readFileSync } from 'node:fs';
import { basename } from 'node:path';
import { readStdinJson, getProjectDir, extractFilePath, isCrFile, readCrState, getLastEvent, CR_STATES } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const backlogDir = `${projectDir}/.devpace/backlog`;

// Only act if .devpace exists and has backlog
if (!existsSync(backlogDir)) {
  process.exit(0);
}

// Extract file path from tool input
const filePath = extractFilePath(input);

// Only check writes to CR files
if (!isCrFile(filePath, backlogDir)) {
  process.exit(0);
}

// Check CR state and recent events for learning triggers
if (existsSync(filePath)) {
  let content;
  try {
    content = readFileSync(filePath, 'utf-8');
  } catch {
    process.exit(0);
  }

  const currentState = readCrState(filePath, content);
  const crName = basename(filePath, '.md');

  if (currentState === CR_STATES.MERGED) {
    console.log(`devpace:post-merge ${crName} merged. Execute §11 post-merge pipeline.`);
  }

  // Gate fail learning trigger — gate_fail is a valuable learning opportunity
  const recentEvent = getLastEvent(filePath, content);
  if (recentEvent && (recentEvent.type === 'gate1_fail' || recentEvent.type === 'gate2_fail')) {
    const gateNum = recentEvent.type === 'gate1_fail' ? '1' : '2';
    console.log(`devpace:learn-trigger ${crName} Gate ${gateNum} failed. Consider /pace-learn to extract lessons.`);
  }

  // Rejected learning trigger — human rejection reveals understanding gaps
  if (recentEvent && recentEvent.type === 'rejected') {
    console.log(`devpace:learn-trigger ${crName} rejected. Consider /pace-learn to analyze gap.`);
  }
}

process.exit(0);
