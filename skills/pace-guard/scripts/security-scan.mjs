#!/usr/bin/env node
/**
 * OWASP security pattern scanner for git diff output.
 *
 * Usage:
 *   git diff HEAD~1 | node skills/pace-guard/scripts/security-scan.mjs
 *   node skills/pace-guard/scripts/security-scan.mjs --cr CR-001 <devpace-dir>
 *   node skills/pace-guard/scripts/security-scan.mjs --files src/auth.js,src/db.js
 *
 * Scans new/modified lines for 6 OWASP risk categories.
 * Output: JSON { findings[], summary: { total, high, medium }, scanned_files }
 *
 * Dependencies: Node.js only (no npm packages).
 */

import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { createInterface } from 'node:readline';

// ── OWASP Pattern Registry ──────────────────────────────────────────
const PATTERNS = [
  // A03: Injection
  { category: 'A03', name: 'SQL Injection', severity: 'High',
    patterns: [
      /(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b.*["'`]\s*\+/i,
      /["'`]\s*\+\s*.*(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b/i,
      /(?:query|execute|exec)\s*\(\s*[`"'].*\$\{/i,
      /(?:query|execute|exec)\s*\(\s*.*\+\s*(?:req|input|param|body|query)/i,
    ] },
  { category: 'A03', name: 'Command Injection', severity: 'High',
    patterns: [
      /(?:exec|spawn|execSync|spawnSync)\s*\(.*\+/i,
      /(?:exec|spawn)\s*\(\s*[`"'].*\$\{/i,
      /child_process.*(?:exec|spawn)\s*\(.*(?:req|input|param|body|query)/i,
    ] },
  { category: 'A03', name: 'Template Injection', severity: 'High',
    patterns: [
      /\.innerHTML\s*=\s*.*(?:req|input|param|body|query)/i,
      /dangerouslySetInnerHTML/i,
      /eval\s*\(.*(?:req|input|param|body|query)/i,
    ] },

  // A07: Authentication Failure
  { category: 'A07', name: 'Hardcoded Credentials', severity: 'High',
    patterns: [
      /(?:password|passwd|pwd|secret|api_key|apiKey)\s*[=:]\s*['"][^'"]{4,}['"]/i,
      /(?:token|auth_token|access_token)\s*[=:]\s*['"][A-Za-z0-9+/=]{16,}['"]/i,
    ] },
  { category: 'A07', name: 'Plaintext Password', severity: 'High',
    patterns: [
      /\.(?:password|passwd)\s*===?\s*['"]|['"].*(?:password|passwd)\s*['"].*===?/i,
      /bcrypt\.compare.*===|password.*===.*password/i,
    ] },

  // A02: Sensitive Data Exposure
  { category: 'A02', name: 'Sensitive Data in Logs', severity: 'High',
    patterns: [
      /(?:console\.log|logger?\.\w+|print|fprintf)\s*\(.*(?:password|token|secret|api.?key|credential|ssn|credit.?card)/i,
    ] },
  { category: 'A02', name: 'API Key Inline', severity: 'High',
    patterns: [
      /(?:api.?key|secret.?key|access.?key)\s*[=:]\s*['"][A-Za-z0-9]{20,}['"]/i,
    ] },

  // A01: Broken Access Control
  { category: 'A01', name: 'Path Traversal', severity: 'Medium',
    patterns: [
      /(?:readFile|readFileSync|open|fopen|createReadStream|access|stat)\s*\(.*\.\.\//i,
      /(?:readFile|readFileSync|open|fopen)\s*\(.*(?:req|input|param|body|query)/i,
    ] },

  // A05: Security Misconfiguration
  { category: 'A05', name: 'Debug Mode', severity: 'Medium',
    patterns: [
      /(?:DEBUG|debug)\s*[=:]\s*(?:true|1|['"]true['"])/i,
      /app\.(?:debug|DEBUG)\s*=\s*True/i,
    ] },
  { category: 'A05', name: 'Overly Broad CORS', severity: 'Medium',
    patterns: [
      /(?:Access-Control-Allow-Origin|cors)\s*[=:]\s*['"]?\*/i,
      /origin:\s*(?:true|\*)/i,
    ] },
  { category: 'A05', name: 'Default Credentials', severity: 'Medium',
    patterns: [
      /(?:admin|root|test|default)\s*[=:]\s*['"](?:admin|root|test|password|123456|default)['"]/i,
    ] },
];

// Layer 1: Security-sensitive path keywords
const SENSITIVE_KEYWORDS = /(?:auth|crypto|secret|token|password|key|permission|session|jwt|oauth|cors|csrf|sanitize|encrypt|decrypt)/i;

// ── Main ─────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const crId = getFlagValue(args, '--cr');
const filesFlag = getFlagValue(args, '--files');
const devpaceDir = args.find(a => !a.startsWith('--') && a !== crId && a !== filesFlag);

let diffContent;

if (crId && devpaceDir) {
  // Get diff for a specific CR's branch
  diffContent = getCrDiff(crId, devpaceDir);
} else if (filesFlag) {
  // Scan specific files (read full content, treat all lines as new)
  diffContent = filesFlag.split(',').map(f => {
    try { return `+++ ${f}\n` + readFileSync(f, 'utf-8').split('\n').map(l => `+${l}`).join('\n'); }
    catch { return ''; }
  }).join('\n');
} else {
  // Read diff from stdin
  diffContent = await readStdin();
}

if (!diffContent) {
  console.log(JSON.stringify({ findings: [], summary: { total: 0, high: 0, medium: 0 }, scanned_files: 0 }, null, 2));
  process.exit(0);
}

const { findings, files } = scanDiff(diffContent);

const summary = {
  total: findings.length,
  high: findings.filter(f => f.severity === 'High').length,
  medium: findings.filter(f => f.severity === 'Medium').length,
};

console.log(JSON.stringify({ findings, summary, scanned_files: files.size, sensitive_files: countSensitiveFiles(files) }, null, 2));
process.exit(findings.length > 0 ? 1 : 0);

// ── Scanner ──────────────────────────────────────────────────────────

function scanDiff(diff) {
  const findings = [];
  const files = new Set();
  let currentFile = null;
  let lineNum = 0;

  for (const line of diff.split('\n')) {
    // Track current file
    const fileMatch = line.match(/^\+\+\+ (?:b\/)?(.+)/);
    if (fileMatch) {
      currentFile = fileMatch[1];
      files.add(currentFile);
      lineNum = 0;
      continue;
    }

    // Track line numbers from hunk headers
    const hunkMatch = line.match(/^@@ -\d+(?:,\d+)? \+(\d+)/);
    if (hunkMatch) {
      lineNum = parseInt(hunkMatch[1]) - 1;
      continue;
    }

    // Only scan added lines
    if (!line.startsWith('+') || line.startsWith('+++')) continue;
    lineNum++;

    const codeLine = line.slice(1); // Remove leading '+'

    // Skip comments and empty lines
    if (!codeLine.trim() || /^\s*(?:\/\/|#|\/\*|\*|<!--)/.test(codeLine)) continue;

    // Run patterns
    for (const rule of PATTERNS) {
      for (const pattern of rule.patterns) {
        if (pattern.test(codeLine)) {
          findings.push({
            file: currentFile || 'unknown',
            line: lineNum,
            category: rule.category,
            name: rule.name,
            severity: rule.severity,
            snippet: codeLine.trim().slice(0, 120),
          });
          break; // One finding per rule per line
        }
      }
    }
  }

  return { findings, files };
}

function countSensitiveFiles(files) {
  let count = 0;
  for (const f of files) {
    if (SENSITIVE_KEYWORDS.test(f)) count++;
  }
  return count;
}

// ── Helpers ──────────────────────────────────────────────────────────

function getCrDiff(id, devDir) {
  const crPath = join(devDir, 'backlog', `${id}.md`);
  if (!existsSync(crPath)) return null;
  try {
    const content = readFileSync(crPath, 'utf-8');
    const branchMatch = content.match(/\*\*分支\*\*[：:]\s*(.+)/);
    if (!branchMatch) return null;
    const branch = branchMatch[1].trim();
    try {
      return execFileSync('git', ['diff', `main...${branch}`], { encoding: 'utf-8', timeout: 15000 });
    } catch {
      return null; // Branch not found or diff failed — do not fallback to unrelated diff
    }
  } catch { return null; }
}

async function readStdin() {
  if (process.stdin.isTTY) return null;
  const chunks = [];
  const rl = createInterface({ input: process.stdin });
  for await (const line of rl) chunks.push(line);
  return chunks.join('\n');
}

function getFlagValue(argList, flag) {
  const idx = argList.indexOf(flag);
  return idx >= 0 && idx + 1 < argList.length ? argList[idx + 1] : null;
}
