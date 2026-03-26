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

import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

// ── Global cache for method detection ────────────────────────────────
let cachedMethod = null;

// ── Parse CLI args ───────────────────────────────────────────────────
const args = process.argv.slice(2);
const action = getFlagValue(args, '--action');
const childIssue = getFlagValue(args, '--child');
const parentIssue = getFlagValue(args, '--parent');
const repo = getFlagValue(args, '--repo');
const batchMode = args.includes('--batch');

if (!action) {
  console.error('Usage: node manage-sub-issues.mjs --action <add|remove|check> [--child N --parent M] --repo owner/repo [--batch]');
  process.exit(1);
}

// ── Main ─────────────────────────────────────────────────────────────
async function main() {
  if (action === 'check') {
    const method = detectMethod(repo);
    const result = {
      method,
      repo,
      timestamp: new Date().toISOString()
    };
    console.log(JSON.stringify(result, null, 2));
    process.exit(method === 'unavailable' ? 1 : 0);
  }

  if (!repo) {
    console.error('Error: --repo is required');
    process.exit(1);
  }

  let operations = [];

  if (batchMode) {
    // Read JSON array from stdin
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
  } else {
    // Single operation
    if (!childIssue || !parentIssue) {
      console.error('Error: --child and --parent are required for single operations');
      process.exit(1);
    }
    operations = [{ child: parseInt(childIssue), parent: parseInt(parentIssue) }];
  }

  // Execute operations
  const method = detectMethod(repo);
  if (method === 'unavailable') {
    console.error('Error: No available method to manage sub-issues (gh CLI not found or lacks sub-issue support)');
    process.exit(1);
  }

  const results = [];
  let okCount = 0;
  let errorCount = 0;

  for (const op of operations) {
    const result = executeOperation(action, op.child, op.parent, repo, method);
    results.push(result);
    if (result.status === 'ok') {
      okCount++;
    } else {
      errorCount++;
    }
    // Rate limiting: sleep 1 second between operations
    if (operations.length > 1) {
      sleep(1000);
    }
  }

  const output = {
    method,
    action,
    repo,
    results,
    summary: {
      total: results.length,
      ok: okCount,
      error: errorCount
    }
  };

  console.log(JSON.stringify(output, null, 2));
  process.exit(errorCount > 0 ? 1 : 0);
}

// ── Method detection ─────────────────────────────────────────────────

/**
 * Detect available method for managing sub-issues.
 * Returns: "cli" | "graphql" | "unavailable"
 * Caches result for session.
 */
function detectMethod(repo) {
  if (cachedMethod) {
    return cachedMethod;
  }

  // Step 1: Check if gh CLI supports --add-parent flag
  try {
    const helpOutput = execSync('gh issue edit --help 2>&1', { encoding: 'utf-8' });
    if (helpOutput.includes('--add-parent')) {
      cachedMethod = 'cli';
      return cachedMethod;
    }
  } catch {
    // gh CLI not available or command failed
  }

  // Step 2: Try GraphQL API
  try {
    const testQuery = 'query { viewer { login } }';
    execSync(`gh api graphql -f query='${testQuery}'`, { encoding: 'utf-8', stdio: 'pipe' });
    cachedMethod = 'graphql';
    return cachedMethod;
  } catch {
    // GraphQL not available
  }

  cachedMethod = 'unavailable';
  return cachedMethod;
}

// ── Operation execution ──────────────────────────────────────────────

/**
 * Execute a single sub-issue operation.
 * Returns: { child, parent, status: "ok"|"error", message, method }
 */
function executeOperation(action, child, parent, repo, method) {
  const result = {
    child,
    parent,
    action,
    status: 'error',
    message: '',
    method
  };

  try {
    if (method === 'cli') {
      executeCli(action, child, parent, repo);
      result.status = 'ok';
      result.message = `Successfully ${action}ed parent relationship`;
    } else if (method === 'graphql') {
      executeGraphql(action, child, parent, repo);
      result.status = 'ok';
      result.message = `Successfully ${action}ed parent relationship via GraphQL`;
    }
  } catch (err) {
    result.message = err.message;

    // Handle rate limiting
    if (err.message.includes('403') || err.message.includes('429')) {
      console.error(`Rate limit detected, sleeping 60 seconds...`, { stderr: true });
      sleep(60000);
      // Retry once
      try {
        if (method === 'cli') {
          executeCli(action, child, parent, repo);
        } else {
          executeGraphql(action, child, parent, repo);
        }
        result.status = 'ok';
        result.message = `Successfully ${action}ed parent relationship (after retry)`;
      } catch (retryErr) {
        result.message = `Failed after retry: ${retryErr.message}`;
      }
    }
  }

  return result;
}

// ── CLI method ───────────────────────────────────────────────────────

function executeCli(action, child, parent, repo) {
  const flag = action === 'add' ? '--add-parent' : '--remove-parent';
  const cmd = `gh issue edit ${child} ${flag} ${parent} --repo ${repo}`;
  execSync(cmd, { encoding: 'utf-8', stdio: 'pipe' });
}

// ── GraphQL method ───────────────────────────────────────────────────

function executeGraphql(action, child, parent, repo) {
  // Step 1: Get node IDs
  const childId = getIssueNodeId(child, repo);
  const parentId = getIssueNodeId(parent, repo);

  // Step 2: Execute mutation
  const mutation = action === 'add' ? 'addSubIssue' : 'removeSubIssue';
  const query = `mutation($p:ID!,$c:ID!){${mutation}(input:{issueId:$p,subIssueId:$c}){issue{number}subIssue{number}}}`;

  const cmd = `gh api graphql -f query='${query}' -f p='${parentId}' -f c='${childId}'`;
  execSync(cmd, { encoding: 'utf-8', stdio: 'pipe' });
}

/**
 * Get GitHub node ID for an issue number.
 */
function getIssueNodeId(issueNumber, repo) {
  const cmd = `gh issue view ${issueNumber} --repo ${repo} --json id -q .id`;
  const nodeId = execSync(cmd, { encoding: 'utf-8' }).trim();
  if (!nodeId) {
    throw new Error(`Failed to get node ID for issue #${issueNumber}`);
  }
  return nodeId;
}

// ── Utilities ────────────────────────────────────────────────────────

function getFlagValue(argList, flag) {
  const idx = argList.indexOf(flag);
  return idx >= 0 && idx + 1 < argList.length ? argList[idx + 1] : null;
}

function sleep(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    // Busy wait
  }
}

// ── Execute ──────────────────────────────────────────────────────────
main().catch(err => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
