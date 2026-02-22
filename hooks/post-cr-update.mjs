#!/usr/bin/env node
/**
 * devpace PostToolUse hook — detect CR merged state and trigger knowledge pipeline
 *
 * Purpose: After a Write/Edit to a CR file, check if the CR transitioned to 'merged'.
 * If so, output a reminder for Claude to trigger the post-merge pipeline:
 * knowledge extraction (pace-learn) + incremental metrics update.
 *
 * This is an advisory hook (exit 0), not blocking.
 */

import { existsSync } from 'node:fs';
import { basename } from 'node:path';
import { readStdinJson, getProjectDir, extractFilePath, isCrFile, readCrState } from './lib/utils.mjs';

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

// Check if CR is now in 'merged' state
if (existsSync(filePath)) {
  const currentState = readCrState(filePath);

  if (currentState === 'merged') {
    const crName = basename(filePath, '.md');
    console.log(`devpace:post-merge ${crName} merged. Execute post-merge pipeline: 1) Run pace-learn for knowledge extraction 2) Update dashboard.md metrics incrementally 3) Check PF completion for release note 4) Update state.md and iterations/current.md`);
  }
}

process.exit(0);
