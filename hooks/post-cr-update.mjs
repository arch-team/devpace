#!/usr/bin/env node
/**
 * devpace PostToolUse hook — detect CR merged state and trigger knowledge pipeline
 *
 * Purpose: After a Write/Edit to a CR file, check if the CR transitioned to 'merged'.
 * If so, output a reminder for Claude to trigger the post-merge pipeline (§11 aligned):
 * 7-step pipeline for merged CR processing, with conditional step 7 for external sync.
 *
 * This is an advisory hook (exit 0), not blocking.
 */

import { readFileSync, existsSync } from 'node:fs';
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

    // Build pipeline message — steps 1-6 always present (§11 aligned)
    const steps = [
      '1) Cascading updates (PF + project.md + state.md + iterations + Release)',
      '2) pace-learn knowledge extraction',
      '3) dashboard.md incremental metrics',
      '4) PF completion → release note',
      '5) Iteration completion check (>90% → suggest retro)',
      '6) First-CR review (teaching dedup)',
    ];

    // Step 7: conditional — only if sync-mapping exists and CR has external link
    const syncMappingPath = `${projectDir}/.devpace/integrations/sync-mapping.md`;
    if (existsSync(syncMappingPath)) {
      try {
        const content = readFileSync(filePath, 'utf-8');
        const hasExternalLink = /\*\*外部关联\*\*[：:]/.test(content);
        if (hasExternalLink) {
          steps.push(`7) External sync push: auto-execute /pace-sync push ${crName}`);
        }
      } catch {
        // Read error — skip step 7
      }
    }

    console.log(`devpace:post-merge ${crName} merged. Execute post-merge pipeline: ${steps.join(' ')}`);
  }
}

process.exit(0);
