#!/usr/bin/env node
/**
 * Schema validation engine for .devpace/ files.
 *
 * Usage:
 *   node skills/pace-init/scripts/validate-schema.mjs <devpace-dir>                     # validate all known files
 *   node skills/pace-init/scripts/validate-schema.mjs <devpace-dir> --type cr           # validate all CR files
 *   node skills/pace-init/scripts/validate-schema.mjs <devpace-dir> --file <path>       # validate a specific file
 *
 * Supported file types: cr, state, project, pf, br
 *
 * Output: JSON { results: [{ file, type, valid, errors[], warnings[] }] }
 *
 * Dependencies: Node.js only (no npm packages).
 */

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, basename } from 'node:path';

// ── Main (called at end of file after all declarations) ──────────────
function main() {
  const args = process.argv.slice(2);
  const devpaceDir = args[0];
  if (!devpaceDir) {
    console.error('Usage: node validate-schema.mjs <devpace-dir> [--type cr|state|project|pf|br] [--file <path>]');
    process.exit(1);
  }

  const filterType = getFlagValue(args, '--type');
  const filterFile = getFlagValue(args, '--file');
  const results = [];

  if (filterFile) {
    const type = detectFileType(filterFile);
    if (type) {
      results.push(validateFile(filterFile, type));
    } else {
      results.push({ file: filterFile, type: 'unknown', valid: false, errors: ['Cannot detect file type'], warnings: [] });
    }
  } else {
    const targets = discoverFiles(devpaceDir, filterType);
    for (const { path, type } of targets) {
      results.push(validateFile(path, type));
    }
  }

  const allValid = results.every(r => r.valid);
  console.log(JSON.stringify({ valid: allValid, total: results.length, errors: results.reduce((n, r) => n + r.errors.length, 0), warnings: results.reduce((n, r) => n + r.warnings.length, 0), results }, null, 2));
  process.exit(allValid ? 0 : 1);
}

// ── File discovery ───────────────────────────────────────────────────

function discoverFiles(devDir, typeFilter) {
  const targets = [];

  if (!typeFilter || typeFilter === 'state') {
    const p = join(devDir, 'state.md');
    if (existsSync(p)) targets.push({ path: p, type: 'state' });
  }

  if (!typeFilter || typeFilter === 'project') {
    const p = join(devDir, 'project.md');
    if (existsSync(p)) targets.push({ path: p, type: 'project' });
  }

  if (!typeFilter || typeFilter === 'cr') {
    const backlog = join(devDir, 'backlog');
    if (existsSync(backlog)) {
      for (const f of readdirSync(backlog)) {
        if (/^CR-\d{3,}\.md$/.test(f)) targets.push({ path: join(backlog, f), type: 'cr' });
      }
    }
  }

  if (!typeFilter || typeFilter === 'pf') {
    const features = join(devDir, 'features');
    if (existsSync(features)) {
      for (const f of readdirSync(features)) {
        if (/^PF-\d{3,}\.md$/.test(f)) targets.push({ path: join(features, f), type: 'pf' });
      }
    }
  }

  if (!typeFilter || typeFilter === 'br') {
    const reqs = join(devDir, 'requirements');
    if (existsSync(reqs)) {
      for (const f of readdirSync(reqs)) {
        if (/^BR-\d{3,}\.md$/.test(f)) targets.push({ path: join(reqs, f), type: 'br' });
      }
    }
  }

  return targets;
}

function detectFileType(filePath) {
  const name = basename(filePath);
  if (name === 'state.md') return 'state';
  if (name === 'project.md') return 'project';
  if (/^CR-\d{3,}\.md$/.test(name)) return 'cr';
  if (/^PF-\d{3,}\.md$/.test(name)) return 'pf';
  if (/^BR-\d{3,}\.md$/.test(name)) return 'br';
  return null;
}

// ── Validation engine ────────────────────────────────────────────────

function validateFile(filePath, type) {
  const result = { file: filePath, type, valid: true, errors: [], warnings: [] };
  let content;
  try {
    content = readFileSync(filePath, 'utf-8');
  } catch {
    result.valid = false;
    result.errors.push(`Cannot read file: ${filePath}`);
    return result;
  }

  const rules = RULES[type];
  if (!rules) {
    result.warnings.push(`No validation rules for type: ${type}`);
    return result;
  }

  for (const rule of rules) {
    rule(content, result, filePath);
  }

  result.valid = result.errors.length === 0;
  return result;
}

// ── Rule helpers ─────────────────────────────────────────────────────

function requireSection(content, result, sectionName) {
  const pattern = new RegExp(`^##\\s+${escapeRegex(sectionName)}`, 'm');
  if (!pattern.test(content)) {
    result.errors.push(`Missing required section: ## ${sectionName}`);
  }
}

function requireField(content, result, fieldName) {
  const pattern = new RegExp(`^- \\*\\*${escapeRegex(fieldName)}\\*\\*[：:]`, 'm');
  if (!pattern.test(content)) {
    result.errors.push(`Missing required field: ${fieldName}`);
  }
}

function checkFieldEnum(content, result, fieldName, validValues) {
  const pattern = new RegExp(`^- \\*\\*${escapeRegex(fieldName)}\\*\\*[：:]\\s*(.+)$`, 'm');
  const match = content.match(pattern);
  if (match) {
    const value = match[1].trim();
    if (!validValues.includes(value)) {
      result.errors.push(`Invalid ${fieldName} value: "${value}". Valid: [${validValues.join(', ')}]`);
    }
  }
}

function requireTitle(content, result) {
  if (!/^# .+$/m.test(content)) {
    result.errors.push('Missing title (# heading)');
  }
}

function checkFileNaming(filePath, result, pattern, example) {
  const name = basename(filePath);
  if (!pattern.test(name)) {
    result.errors.push(`Invalid file name: ${name}. Expected: ${example}`);
  }
}

// ── Rule registry ────────────────────────────────────────────────────

const CR_STATUSES = ['created', 'developing', 'verifying', 'in_review', 'approved', 'merged', 'released', 'paused'];
const CR_TYPES = ['feature', 'defect', 'hotfix', 'tech-debt'];
const CR_SEVERITIES = ['critical', 'major', 'minor', 'trivial'];
const CR_COMPLEXITIES = ['S', 'M', 'L', 'XL'];
const CR_EVENT_TYPES = [
  'created', 'intent_set', 'developing_start',
  'gate1_pass', 'gate1_fail', 'gate2_pass', 'gate2_fail',
  'review_submit', 'approved', 'rejected', 'merged',
  'paused', 'resumed', 'change_scope', 'released'
];

const PF_STATUSES = ['进行中', '全部 CR 完成', '已发布', '暂停', '待开始'];
const BR_STATUSES = ['待开始', '进行中', '已完成', '暂停'];

const RULES = {
  // ── CR rules ─────────────────────────────────────────────────────
  cr: [
    (c, r, p) => checkFileNaming(p, r, /^CR-\d{3,}\.md$/, 'CR-xxx.md'),
    (c, r) => requireTitle(c, r),
    (c, r) => requireField(c, r, 'ID'),
    (c, r) => requireField(c, r, '状态'),
    (c, r) => checkFieldEnum(c, r, '状态', CR_STATUSES),
    (c, r) => {
      // Type is optional (defaults to feature), but if present must be valid
      const match = c.match(/^- \*\*类型\*\*[：:]\s*(.+)$/m);
      if (match && !CR_TYPES.includes(match[1].trim())) {
        r.errors.push(`Invalid 类型 value: "${match[1].trim()}". Valid: [${CR_TYPES.join(', ')}]`);
      }
    },
    (c, r) => {
      // Severity required for defect/hotfix
      const typeMatch = c.match(/^- \*\*类型\*\*[：:]\s*(.+)$/m);
      const type = typeMatch ? typeMatch[1].trim() : 'feature';
      if ((type === 'defect' || type === 'hotfix') && !/^- \*\*严重度\*\*[：:]/m.test(c)) {
        r.warnings.push(`${type} CR should have 严重度 field`);
      }
      // If severity present, validate enum
      const sevMatch = c.match(/^- \*\*严重度\*\*[：:]\s*(.+)$/m);
      if (sevMatch && !CR_SEVERITIES.includes(sevMatch[1].trim())) {
        r.errors.push(`Invalid 严重度 value: "${sevMatch[1].trim()}". Valid: [${CR_SEVERITIES.join(', ')}]`);
      }
    },
    (c, r) => {
      // Complexity if present must be valid
      const match = c.match(/^- \*\*复杂度\*\*[：:]\s*(.+)$/m);
      if (match && !CR_COMPLEXITIES.includes(match[1].trim())) {
        r.errors.push(`Invalid 复杂度 value: "${match[1].trim()}". Valid: [${CR_COMPLEXITIES.join(', ')}]`);
      }
    },
    (c, r) => requireSection(c, r, '意图'),
    (c, r) => requireSection(c, r, '事件'),
    (c, r) => {
      // Validate event types in event table rows
      const tableMatch = c.match(/## 事件\s*\n+\|[^\n]+\n\|[-|\s]+\n([\s\S]*?)(?=\n## |$)/);
      if (!tableMatch) return;
      const rows = tableMatch[1].trim().split('\n').filter(l => l.startsWith('|'));
      for (const row of rows) {
        const cells = row.split('|').map(cell => cell.trim()).filter(Boolean);
        if (cells.length >= 2) {
          const eventType = cells[1];
          if (CR_EVENT_TYPES.includes(eventType)) continue;
          if (/^step_\d+_done$/.test(eventType)) continue;
          r.warnings.push(`Event type "${eventType}" is not a known enum value`);
        }
      }
    },
    (c, r) => {
      // 质量检查 section — required but may be absent in early CR
      if (!/^## 质量检查/m.test(c)) {
        r.warnings.push('Missing section: ## 质量检查 (expected for verifying+ CRs)');
      }
    },
    (c, r) => {
      // ID format check: CR-xxx
      const match = c.match(/^- \*\*ID\*\*[：:]\s*(.+)$/m);
      if (match && !/^CR-\d{3,}$/.test(match[1].trim())) {
        r.errors.push(`Invalid ID format: "${match[1].trim()}". Expected: CR-xxx (3+ digits)`);
      }
    },
  ],

  // ── state.md rules ───────────────────────────────────────────────
  state: [
    (c, r) => {
      // Must have blockquote header with 目标
      if (!/^>\s*目标[：:]/m.test(c)) {
        r.errors.push('Missing blockquote header with 目标');
      }
    },
    (c, r) => {
      // Must have 进行中 or 当前工作 indicator
      if (!/\*\*进行中\*\*/.test(c) && !/（无）/.test(c)) {
        r.warnings.push('No 进行中 work items or （无） placeholder found');
      }
    },
    (c, r) => {
      // Must have 下一步
      if (!/下一步/m.test(c)) {
        r.errors.push('Missing 下一步 section');
      }
    },
    (c, r) => {
      // Max 15 content lines (exclude comments and empty lines)
      const contentLines = c.split('\n').filter(l => l.trim() && !l.trim().startsWith('<!--'));
      if (contentLines.length > 15) {
        r.warnings.push(`state.md has ${contentLines.length} content lines (max recommended: 15)`);
      }
    },
    (c, r) => {
      // Should have devpace-version comment
      if (!/devpace-version/.test(c)) {
        r.warnings.push('Missing devpace-version marker');
      }
    },
  ],

  // ── project.md rules ─────────────────────────────────────────────
  project: [
    (c, r) => requireTitle(c, r),
    (c, r) => {
      // Must have blockquote description
      if (!/^>\s*.+/m.test(c)) {
        r.warnings.push('Missing blockquote project description');
      }
    },
    (c, r) => {
      // Key sections (can be placeholders)
      for (const section of ['价值功能树']) {
        if (!new RegExp(`^##\\s+${escapeRegex(section)}`, 'm').test(c)) {
          r.warnings.push(`Missing section: ## ${section}`);
        }
      }
    },
    (c, r) => {
      // CR emoji status consistency in tree view
      const crRefs = c.matchAll(/CR-(\d{3,})\s*(🔄|✅|⏳|🚀|⏸️)?/g);
      for (const m of crRefs) {
        if (!m[2]) {
          r.warnings.push(`CR-${m[1]} in tree view missing status emoji`);
          break; // Only warn once
        }
      }
    },
  ],

  // ── PF rules ─────────────────────────────────────────────────────
  pf: [
    (c, r, p) => checkFileNaming(p, r, /^PF-\d{3,}\.md$/, 'PF-xxx.md'),
    (c, r) => requireTitle(c, r),
    (c, r) => {
      // Title should contain PF-xxx
      const titleMatch = c.match(/^# (.+)$/m);
      if (titleMatch && !/PF-\d{3,}/.test(titleMatch[1])) {
        r.warnings.push('Title does not contain PF-xxx identifier');
      }
    },
    (c, r) => requireField(c, r, 'BR'),
    (c, r) => requireField(c, r, '状态'),
    (c, r) => requireSection(c, r, '关联 CR'),
    (c, r) => {
      // 验收标准 — important but may not be filled yet
      if (!/^## 验收标准/m.test(c)) {
        r.warnings.push('Missing section: ## 验收标准');
      }
    },
  ],

  // ── BR rules ─────────────────────────────────────────────────────
  br: [
    (c, r, p) => checkFileNaming(p, r, /^BR-\d{3,}\.md$/, 'BR-xxx.md'),
    (c, r) => requireTitle(c, r),
    (c, r) => {
      // Title should contain BR-xxx
      const titleMatch = c.match(/^# (.+)$/m);
      if (titleMatch && !/BR-\d{3,}/.test(titleMatch[1])) {
        r.warnings.push('Title does not contain BR-xxx identifier');
      }
    },
    (c, r) => requireField(c, r, 'OBJ'),
    (c, r) => requireField(c, r, '状态'),
    (c, r) => requireSection(c, r, '产品功能'),
    (c, r) => {
      // 业务上下文 — expected for overflow files
      if (!/^## 业务上下文/m.test(c)) {
        r.warnings.push('Missing section: ## 业务上下文 (expected for overflow BR files)');
      }
    },
  ],
};

// ── Utilities ────────────────────────────────────────────────────────

function getFlagValue(argList, flag) {
  const idx = argList.indexOf(flag);
  return idx >= 0 && idx + 1 < argList.length ? argList[idx + 1] : null;
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ── Entry point ──────────────────────────────────────────────────────
main();
