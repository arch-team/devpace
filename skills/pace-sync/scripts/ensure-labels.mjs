#!/usr/bin/env node
/**
 * Idempotent GitHub label precheck and creation for devpace sync.
 *
 * Usage: node ensure-labels.mjs <owner/repo>
 * Output: JSON { status: "ok"|"partial"|"unavailable", created: [...], existing: [...], failed: [] }
 *
 * Dependencies: Node.js only (requires gh CLI installed).
 */

import { execFileSync } from 'node:child_process';
import { validateRepo, CONFIG } from './shared-utils.mjs';

const REQUIRED_LABELS = [
  { name: 'backlog', color: 'ededed' },
  { name: 'in-progress', color: 'ededed' },
  { name: 'needs-review', color: 'ededed' },
  { name: 'awaiting-approval', color: 'ededed' },
  { name: 'approved', color: 'ededed' },
  { name: 'done', color: 'ededed' },
  { name: 'released', color: 'ededed' },
  { name: 'on-hold', color: 'ededed' },
  { name: 'planning', color: 'ededed' },
  { name: 'gate-1-passed', color: 'ededed' },
  { name: 'gate-2-passed', color: 'ededed' },
  { name: 'gate-3-passed', color: 'ededed' },
  { name: 'devpace:epic', color: '7057ff' },
  { name: 'devpace:br', color: '0075ca' },
  { name: 'devpace:pf', color: '1a7f37' },
  { name: 'devpace:cr', color: 'e4e669' },
];

function main() {
  const args = process.argv.slice(2);
  if (args.length !== 1) {
    console.error('Usage: node ensure-labels.mjs <owner/repo>');
    process.exit(1);
  }

  const repo = validateRepo(args[0]);
  const result = { status: 'ok', created: [], existing: [], failed: [] };

  // Step 1: Check gh CLI
  try {
    execFileSync('gh', ['auth', 'status'], { stdio: 'pipe', encoding: 'utf-8' });
  } catch {
    result.status = 'unavailable';
    console.log(JSON.stringify(result));
    process.exit(0);
  }

  // Step 2: Get existing labels
  let existingLabels = [];
  try {
    const output = execFileSync('gh', [
      'label', 'list', '--repo', repo, '--json', 'name', '--limit', String(CONFIG.LABEL_LIST_LIMIT)
    ], { encoding: 'utf-8', stdio: 'pipe' });
    existingLabels = JSON.parse(output).map(l => l.name);
  } catch {
    result.status = 'unavailable';
    console.log(JSON.stringify(result));
    process.exit(0);
  }

  // Step 3: Create missing labels
  for (const label of REQUIRED_LABELS) {
    if (existingLabels.includes(label.name)) {
      result.existing.push(label.name);
    } else {
      try {
        execFileSync('gh', [
          'label', 'create', label.name,
          '--description', 'devpace sync',
          '--color', label.color,
          '--repo', repo
        ], { encoding: 'utf-8', stdio: 'pipe' });
        result.created.push(label.name);
      } catch {
        result.failed.push(label.name);
      }
    }
  }

  if (result.failed.length > 0) result.status = 'partial';
  console.log(JSON.stringify(result));
  process.exit(0);
}

main();
