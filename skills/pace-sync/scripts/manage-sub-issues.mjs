#!/usr/bin/env node
/**
 * Manage GitHub sub-issue relationships using gh CLI.
 *
 * Usage:
 *   # Single operation
 *   node manage-sub-issues.mjs --action add --child 6 --parent 2 --repo owner/repo
 *   node manage-sub-issues.mjs --action remove --child 6 --parent 2 --repo owner/repo
 *
 *   # Batch operations (stdin JSON)
 *   echo '[{"child":6,"parent":2},{"child":7,"parent":2}]' | node manage-sub-issues.mjs --action add --repo owner/repo --batch
 *
 *   # Method detection
 *   node manage-sub-issues.mjs --action check --repo owner/repo
 *
 * Output: JSON to stdout
 *   { method: "cli"|"graphql"|"unavailable", results: [...], summary: { total, ok, error } }
 *
 * Dependencies: Node.js only (requires gh CLI installed).
 */

import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { validateRepo, validateIssueNumber, syncSleep, getFlagValue, CONFIG } from './shared-utils.mjs';

// ── Global cache for method detection ────────────────────────────────
let cachedMethod = null;

// ── Parse CLI args ───────────────────────────────────────────────────
const args = process.argv.slice(2);
const action = getFlagValue(args, '--action');
const childIssue = getFlagValue(args, '--child');
const parentIssue = getFlagValue(args, '--parent');
const rawRepo = getFlagValue(args, '--repo');
const batchMode = args.includes('--batch');

if (!action) {
  console.error('Usage: node manage-sub-issues.mjs --action <add|remove|check> [--child N --parent M] --repo owner/repo [--batch]');
  process.exit(1);
}

// ── Main ─────────────────────────────────────────────────────────────
function main() {
  if (action === 'check') {
    const repo = rawRepo ? validateRepo(rawRepo) : null;
    const method = detectMethod();
    console.log(JSON.stringify({ method, repo, timestamp: new Date().toISOString() }, null, 2));
    process.exit(method === 'unavailable' ? 1 : 0);
  }

  if (!rawRepo) {
    console.error('Error: --repo is required');
    process.exit(1);
  }
  const repo = validateRepo(rawRepo);

  let operations = [];

  if (batchMode) {
    const stdin = readFileSync(0, 'utf-8').trim();
    if (!stdin) {
      console.error('Error: No batch data provided on stdin');
      process.exit(1);
    }
    try {
      operations = JSON.parse(stdin);
      if (!Array.isArray(operations)) {
        throw new Error('Batch data must be a JSON array');
      }
    } catch (err) {
      console.error(`Error: Invalid JSON on stdin: ${err.message}`);
      process.exit(1);
    }
    // Validate all entries
    operations = operations.map(op => ({
      child: validateIssueNumber(op.child),
      parent: validateIssueNumber(op.parent),
    }));
  } else {
    if (!childIssue || !parentIssue) {
      console.error('Error: --child and --parent are required for single operations');
      process.exit(1);
    }
    operations = [{ child: validateIssueNumber(childIssue), parent: validateIssueNumber(parentIssue) }];
  }

  const method = detectMethod();
  if (method === 'unavailable') {
    console.error('Error: No available method to manage sub-issues');
    process.exit(1);
  }

  const results = [];
  let okCount = 0;
  let errorCount = 0;

  for (let i = 0; i < operations.length; i++) {
    const op = operations[i];
    const result = executeOperation(action, op.child, op.parent, repo, method);
    results.push(result);
    if (result.status === 'ok') okCount++;
    else errorCount++;
    if (operations.length > 1 && i < operations.length - 1) syncSleep(CONFIG.OPERATION_DELAY_MS);
  }

  console.log(JSON.stringify({
    method, action, repo, results,
    summary: { total: results.length, ok: okCount, error: errorCount }
  }, null, 2));
  process.exit(errorCount > 0 ? 1 : 0);
}

// ── Method detection ─────────────────────────────────────────────────

function detectMethod() {
  if (cachedMethod) return cachedMethod;

  // Step 1: Check if gh CLI supports --add-parent
  try {
    const helpOutput = execFileSync('gh', ['issue', 'edit', '--help'], { encoding: 'utf-8', stdio: 'pipe' });
    if (helpOutput.includes('--add-parent')) {
      cachedMethod = 'cli';
      return cachedMethod;
    }
  } catch (err) {
    console.error(`Warning: gh CLI check failed: ${err.message}`);
  }

  // Step 2: Try GraphQL API
  try {
    execFileSync('gh', ['api', 'graphql', '-f', 'query=query { viewer { login } }'], { encoding: 'utf-8', stdio: 'pipe' });
    cachedMethod = 'graphql';
    return cachedMethod;
  } catch (err) {
    console.error(`Warning: GraphQL check failed: ${err.message}`);
  }

  cachedMethod = 'unavailable';
  return cachedMethod;
}

// ── Operation execution ──────────────────────────────────────────────

function executeOperation(action, child, parent, repo, method) {
  const result = { child, parent, action, status: 'error', message: '', method };

  try {
    if (method === 'cli') {
      executeCli(action, child, parent, repo);
    } else {
      executeGraphql(action, child, parent, repo);
    }
    result.status = 'ok';
    result.message = `Successfully ${action}ed parent relationship`;
  } catch (err) {
    result.message = err.message;
    if (err.message.includes('403') || err.message.includes('429')) {
      console.error(`Rate limit detected, retrying after ${CONFIG.RATE_LIMIT_RETRY_MS / 1000}s...`);
      syncSleep(CONFIG.RATE_LIMIT_RETRY_MS);
      try {
        if (method === 'cli') executeCli(action, child, parent, repo);
        else executeGraphql(action, child, parent, repo);
        result.status = 'ok';
        result.message = `Successfully ${action}ed parent relationship (after retry)`;
      } catch (retryErr) {
        result.message = `Failed after retry: ${retryErr.message}`;
      }
    }
  }

  return result;
}

// ── CLI method (uses execFileSync — no shell injection) ─────────────

function executeCli(action, child, parent, repo) {
  const flag = action === 'add' ? '--add-parent' : '--remove-parent';
  execFileSync('gh', ['issue', 'edit', String(child), flag, String(parent), '--repo', repo], {
    encoding: 'utf-8', stdio: 'pipe'
  });
}

// ── GraphQL method (uses execFileSync array args) ───────────────────

function executeGraphql(action, child, parent, repo) {
  const childId = getIssueNodeId(child, repo);
  const parentId = getIssueNodeId(parent, repo);

  const mutation = action === 'add' ? 'addSubIssue' : 'removeSubIssue';
  const query = `mutation($p:ID!,$c:ID!){${mutation}(input:{issueId:$p,subIssueId:$c}){issue{number}subIssue{number}}}`;

  execFileSync('gh', ['api', 'graphql', '-f', `query=${query}`, '-f', `p=${parentId}`, '-f', `c=${childId}`], {
    encoding: 'utf-8', stdio: 'pipe'
  });
}

function getIssueNodeId(issueNumber, repo) {
  const output = execFileSync('gh', ['issue', 'view', String(issueNumber), '--repo', repo, '--json', 'id', '-q', '.id'], {
    encoding: 'utf-8', stdio: 'pipe'
  }).trim();
  if (!output) throw new Error(`Failed to get node ID for issue #${issueNumber}`);
  return output;
}

// ── Execute ──────────────────────────────────────────────────────────
try {
  main();
} catch (err) {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
}
