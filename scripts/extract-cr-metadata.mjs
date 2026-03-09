#!/usr/bin/env node
/**
 * Extract structured metadata from CR markdown files.
 *
 * Usage:
 *   node scripts/extract-cr-metadata.mjs <devpace-dir>
 *   node scripts/extract-cr-metadata.mjs <devpace-dir> --status merged
 *   node scripts/extract-cr-metadata.mjs <devpace-dir> --status merged --no-release
 *   node scripts/extract-cr-metadata.mjs <devpace-dir> --id CR-001
 *
 * Output: JSON array of CR metadata objects to stdout.
 *
 * Dependencies: Node.js only (no npm packages).
 */

import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

// ── Parse CLI args ───────────────────────────────────────────────────
const args = process.argv.slice(2);
const devpaceDir = args[0];

if (!devpaceDir) {
  console.error('Usage: node extract-cr-metadata.mjs <devpace-dir> [--status <status>] [--no-release] [--id <CR-ID>]');
  process.exit(1);
}

const filterStatus = getFlagValue(args, '--status');
const filterNoRelease = args.includes('--no-release');
const filterId = getFlagValue(args, '--id');

// ── Main ─────────────────────────────────────────────────────────────
const backlogDir = join(devpaceDir, 'backlog');
let crFiles;
try {
  crFiles = readdirSync(backlogDir).filter(f => /^CR-\d{3}\.md$/.test(f)).sort();
} catch {
  console.error(`Error: Cannot read ${backlogDir}`);
  process.exit(1);
}

const results = [];

for (const fileName of crFiles) {
  const filePath = join(backlogDir, fileName);
  const content = readFileSync(filePath, 'utf-8');
  const meta = parseCrContent(content, fileName);

  // Apply filters
  if (filterId && meta.id !== filterId) continue;
  if (filterStatus && meta.status !== filterStatus) continue;
  if (filterNoRelease && meta.release) continue;

  results.push(meta);
}

console.log(JSON.stringify(results, null, 2));

// ── Parser ───────────────────────────────────────────────────────────

function parseCrContent(content, fileName) {
  const meta = {
    id: extractField(content, 'ID') || fileName.replace('.md', ''),
    title: extractTitle(content),
    type: extractField(content, '类型') || 'feature',
    status: extractField(content, '状态') || '',
    severity: extractField(content, '严重度') || null,
    complexity: extractField(content, '复杂度') || null,
    pf: extractField(content, '产品功能') || null,
    release: extractField(content, '关联 Release') || null,
    branch: extractField(content, '分支') || null,
    blocked: extractField(content, '阻塞') || null,
    breaking: detectBreaking(content),
    events: extractEvents(content),
    fileName
  };

  return meta;
}

function extractTitle(content) {
  const match = content.match(/^# (.+)$/m);
  return match ? match[1].trim() : '';
}

function extractField(content, fieldName) {
  // Match: - **fieldName**：value  or  - **fieldName**: value
  const regex = new RegExp(`^- \\*\\*${escapeRegex(fieldName)}\\*\\*[：:]\\s*(.+)$`, 'm');
  const match = content.match(regex);
  if (!match) return null;
  const value = match[1].trim();
  return value || null;
}

/**
 * Detect breaking change signals in CR content.
 * Checks title, description, and explicit breaking markers.
 */
function detectBreaking(content) {
  const breakingPatterns = [
    /BREAKING/i,
    /breaking\s*change/i,
    /不兼容/,
    /破坏性变更/,
    /breaking:\s*true/i
  ];

  for (const pattern of breakingPatterns) {
    if (pattern.test(content)) {
      return true;
    }
  }
  return false;
}

/**
 * Extract events from the event table.
 * Returns array of { date, event, actor, note }.
 */
function extractEvents(content) {
  const events = [];
  // Find event table rows (skip header and separator)
  // Match: ## 事件 + optional blank lines + header row + separator row + data rows
  const tableMatch = content.match(/## 事件\s*\n+\|[^\n]+\n\|[-|\s]+\n([\s\S]*?)(?=\n## |$)/);
  if (!tableMatch) return events;

  const rows = tableMatch[1].trim().split('\n');
  for (const row of rows) {
    if (!row.startsWith('|')) continue;
    const cells = row.split('|').map(c => c.trim()).filter(Boolean);
    if (cells.length >= 3) {
      events.push({
        date: cells[0],
        event: cells[1],
        actor: cells[2] || 'Claude',
        note: cells[3] || ''
      });
    }
  }
  return events;
}

// ── Utilities ────────────────────────────────────────────────────────

function getFlagValue(argList, flag) {
  const idx = argList.indexOf(flag);
  return idx >= 0 && idx + 1 < argList.length ? argList[idx + 1] : null;
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
