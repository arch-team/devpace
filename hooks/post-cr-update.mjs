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

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { basename, dirname } from 'node:path';
import { readStdinJson, getProjectDir, extractFilePath, isCrFile, readCrState, getLastEvent } from './lib/utils.mjs';

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
  const currentState = readCrState(filePath);
  const crName = basename(filePath, '.md');

  if (currentState === 'merged') {
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

    // Write .learn-pending flag for session-start reminder
    try {
      const pendingPath = `${projectDir}/.devpace/.learn-pending`;
      mkdirSync(dirname(pendingPath), { recursive: true });
      const existing = existsSync(pendingPath) ? readFileSync(pendingPath, 'utf-8').trim() : '';
      const entry = `${crName} ${new Date().toISOString()}`;
      const newContent = existing ? `${existing}\n${entry}` : entry;
      writeFileSync(pendingPath, newContent + '\n', 'utf-8');
    } catch {
      // Non-critical — learn-pending write failure doesn't block pipeline
    }
  }

  // Gate fail learning trigger — gate_fail is a valuable learning opportunity
  const recentEvent = getLastEvent(filePath);
  if (recentEvent && (recentEvent.type === 'gate1_fail' || recentEvent.type === 'gate2_fail')) {
    const gateNum = recentEvent.type.includes('1') ? '1' : '2';
    console.log([
      `devpace:learn-trigger ${crName} Gate ${gateNum} 失败是学习机会。`,
      `  建议: 调用 /pace-learn 提取 Gate ${gateNum} 失败原因`,
      `  关注: 失败的检查项是否应该调整阈值，或 Claude 有可避免的盲区`,
    ].join('\n'));
  }

  // Rejected learning trigger — human rejection reveals understanding gaps
  if (recentEvent && recentEvent.type === 'rejected') {
    console.log([
      `devpace:learn-trigger ${crName} 人类打回是理解差距的信号。`,
      `  建议: 调用 /pace-learn 分析打回原因`,
      `  关注: Claude 的意图理解是否与人类预期一致`,
    ].join('\n'));
  }
}

process.exit(0);
