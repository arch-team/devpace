#!/usr/bin/env node
/**
 * Infer semantic version bump from CR metadata.
 *
 * Usage:
 *   node skills/pace-release/scripts/infer-version-bump.mjs <devpace-dir> [current-version]
 *
 * Reads merged CRs not yet in a Release, analyzes for breaking/feature/defect,
 * outputs JSON with suggested version bump.
 *
 * If current-version is not provided, attempts to read from
 * <devpace-dir>/integrations/config.md version configuration.
 *
 * Output JSON:
 * {
 *   "current": "1.2.0",
 *   "suggested": "1.3.0",
 *   "bump_type": "minor",
 *   "reasoning": ["CR-012 (feature): 新增搜索 → minor", ...],
 *   "candidates": [{ id, title, type, breaking }, ...]
 * }
 *
 * Dependencies: Node.js only (no npm packages).
 */

import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// ── Parse CLI args ───────────────────────────────────────────────────
const args = process.argv.slice(2);
const positional = args.filter(a => !a.startsWith('--'));
const devpaceDir = positional[0];
const explicitVersion = positional[1];

if (!devpaceDir) {
  console.error('Usage: node infer-version-bump.mjs <devpace-dir> [current-version]');
  process.exit(1);
}

// ── Step 1: Get candidate CRs (merged, no release) ──────────────────
const scriptDir = fileURLToPath(new URL('.', import.meta.url));
let candidates;
try {
  const output = execFileSync(
    'node',
    [join(scriptDir, '..', '..', 'scripts', 'extract-cr-metadata.mjs'), devpaceDir, '--status', 'merged', '--no-release'],
    { encoding: 'utf-8', timeout: 10000 }
  );
  candidates = JSON.parse(output);
} catch (err) {
  const errorOutput = {
    current: null,
    suggested: null,
    bump_type: null,
    reasoning: [`Error extracting CR metadata: ${err.message}`],
    candidates: [],
    error: err.message,
  };
  console.log(JSON.stringify(errorOutput, null, 2));
  process.exit(1);
}

if (candidates.length === 0) {
  console.log(JSON.stringify({
    current: null,
    suggested: null,
    bump_type: null,
    reasoning: ['没有找到已 merged 且未关联 Release 的 CR'],
    candidates: []
  }, null, 2));
  process.exit(0);
}

// ── Step 2: Determine current version ────────────────────────────────
const currentVersion = explicitVersion || readCurrentVersion(devpaceDir);

// ── Step 3: Analyze candidates for bump type ─────────────────────────
const reasoning = [];
let hasBreaking = false;
let hasFeature = false;

const candidateSummary = candidates.map(cr => {
  const summary = { id: cr.id, title: cr.title, type: cr.type, breaking: cr.breaking };

  if (cr.breaking) {
    hasBreaking = true;
    reasoning.push(`${cr.id} (${cr.type}): ${cr.title} → BREAKING CHANGE`);
  } else if (cr.type === 'feature' || cr.type === 'tech-debt') {
    hasFeature = true;
    reasoning.push(`${cr.id} (${cr.type}): ${cr.title} → minor`);
  } else {
    reasoning.push(`${cr.id} (${cr.type}): ${cr.title} → patch`);
  }

  return summary;
});

// ── Step 4: Determine bump type ──────────────────────────────────────
let bumpType;
if (hasBreaking) {
  bumpType = 'major';
  reasoning.push(`最高级别：major（包含 breaking change）`);
} else if (hasFeature) {
  bumpType = 'minor';
  reasoning.push(`最高级别：minor（包含 feature/tech-debt，无 breaking change）`);
} else {
  bumpType = 'patch';
  reasoning.push(`最高级别：patch（仅 defect/hotfix）`);
}

// ── Step 5: Calculate suggested version ──────────────────────────────
const suggested = currentVersion ? bumpVersion(currentVersion, bumpType) : null;
if (currentVersion && suggested) {
  reasoning.push(`${currentVersion} → ${suggested}`);
}

// ── Output ───────────────────────────────────────────────────────────
console.log(JSON.stringify({
  current: currentVersion,
  suggested,
  bump_type: bumpType,
  reasoning,
  candidates: candidateSummary
}, null, 2));

// ── Helpers ──────────────────────────────────────────────────────────

/**
 * Read current version from integrations/config.md.
 * Looks for version file path and reads it.
 */
function readCurrentVersion(devDir) {
  const configPath = join(devDir, 'integrations', 'config.md');
  if (!existsSync(configPath)) return null;

  try {
    const config = readFileSync(configPath, 'utf-8');

    // Look for version file path in config
    // Pattern: 版本文件路径 or version file: path
    const pathMatch = config.match(/版本文件[路径]*[：:]\s*`?([^`\n]+)`?/);
    if (!pathMatch) return null;

    const versionFilePath = pathMatch[1].trim();

    // Determine project root (parent of .devpace)
    const projectRoot = join(devDir, '..');
    const absVersionPath = join(projectRoot, versionFilePath);

    if (!existsSync(absVersionPath)) return null;

    const versionContent = readFileSync(absVersionPath, 'utf-8');

    // Try JSON format: "version": "x.y.z"
    const jsonMatch = versionContent.match(/"version"\s*:\s*"([^"]+)"/);
    if (jsonMatch) return jsonMatch[1];

    // Try TOML format: version = "x.y.z"
    const tomlMatch = versionContent.match(/version\s*=\s*"([^"]+)"/);
    if (tomlMatch) return tomlMatch[1];

    // Try YAML format: version: x.y.z
    const yamlMatch = versionContent.match(/version:\s*([^\s\n]+)/);
    if (yamlMatch) return yamlMatch[1];

    // Try plain semver
    const semverMatch = versionContent.match(/(\d+\.\d+\.\d+)/);
    if (semverMatch) return semverMatch[1];

    return null;
  } catch {
    return null;
  }
}

/**
 * Bump a semver version by the given type.
 */
function bumpVersion(version, type) {
  const parts = version.split('.').map(Number);
  if (parts.length !== 3 || parts.some(isNaN)) return null;

  switch (type) {
    case 'major':
      return `${parts[0] + 1}.0.0`;
    case 'minor':
      return `${parts[0]}.${parts[1] + 1}.0`;
    case 'patch':
      return `${parts[0]}.${parts[1]}.${parts[2] + 1}`;
    default:
      return null;
  }
}
