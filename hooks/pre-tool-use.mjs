#!/usr/bin/env node
/**
 * devpace PreToolUse hook — quality gate awareness for CR state transitions
 *
 * Purpose: When Claude attempts to write to CR files with state transitions,
 * remind about quality gate requirements. This is an advisory hook (exit 0),
 * not a blocking gate — the actual gate enforcement is in devpace-rules.md §2.
 *
 * Why advisory, not blocking:
 *   Gate 1/2 are enforced by devpace-rules.md §2 (Claude self-checks).
 *   This hook adds a safety net: if Claude is about to advance a CR state
 *   without mentioning quality checks, the hook output reminds it.
 */

import { existsSync } from 'node:fs';
import { readStdinJson, getProjectDir, extractFilePath, isCrFile, readCrState } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const backlogDir = `${projectDir}/.devpace/backlog`;

// Only act if .devpace exists and has backlog
if (!existsSync(backlogDir)) {
  process.exit(0);
}

// Tool filtering is handled by hooks.json matcher (Write|Edit only).
const filePath = extractFilePath(input);

// Only check writes to CR files
if (!isCrFile(filePath, backlogDir)) {
  process.exit(0);
}

// Check if the CR file exists and has a state transition hint
if (existsSync(filePath)) {
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
