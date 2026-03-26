#!/usr/bin/env node
/**
 * Extract structured metadata from all devpace entity files (Epic/BR/PF/CR).
 *
 * Usage:
 *   node skills/pace-sync/scripts/extract-entity-metadata.mjs <devpace-dir>
 *   node skills/pace-sync/scripts/extract-entity-metadata.mjs <devpace-dir> --type epic
 *   node skills/pace-sync/scripts/extract-entity-metadata.mjs <devpace-dir> --type all
 *   node skills/pace-sync/scripts/extract-entity-metadata.mjs <devpace-dir> --id EPIC-001
 *
 * Output: JSON array of entity metadata objects to stdout.
 *
 * Dependencies: Node.js only (no npm packages).
 */

import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import {
  extractTitle, extractField, extractSection, escapeRegex,
  getFlagValue, safeReadDir, safeReadFile, inferStatusFromEmoji
} from './shared-utils.mjs';

// ── Parse CLI args ───────────────────────────────────────────────────
const args = process.argv.slice(2);
const devpaceDir = args[0];

if (!devpaceDir) {
  console.error('Usage: node extract-entity-metadata.mjs <devpace-dir> [--type epic|br|pf|cr|all] [--id EPIC-001]');
  process.exit(1);
}

const filterType = getFlagValue(args, '--type') || 'all';
const filterId = getFlagValue(args, '--id');

// ── Main ─────────────────────────────────────────────────────────────
const results = [];
const warnings = [];

if (['all', 'epic'].includes(filterType)) {
  results.push(...scanEpics(devpaceDir));
}
if (['all', 'br'].includes(filterType)) {
  results.push(...scanBRs(devpaceDir));
}
if (['all', 'pf'].includes(filterType)) {
  results.push(...scanPFs(devpaceDir));
}
if (['all', 'cr'].includes(filterType)) {
  results.push(...scanCRs(devpaceDir));
}

// Detect phantom entities: referenced in project.md tree but no independent file
if (filterType === 'all' || filterType === 'epic') {
  warnings.push(...detectPhantomEpics(devpaceDir, results));
}

const filtered = filterId ? results.filter(e => e.id === filterId) : results;
const output = { entities: filtered, warnings };
console.log(JSON.stringify(output, null, 2));

// ── Epic Scanner ─────────────────────────────────────────────────────
function scanEpics(dir) {
  const epicsDir = join(dir, 'epics');
  if (!existsSync(epicsDir)) return [];

  const files = safeReadDir(epicsDir).filter(f => /^EPIC-\d+\.md$/.test(f)).sort();
  return files.map(fileName => {
    const filePath = join(epicsDir, fileName);
    const content = safeReadFile(filePath);
    if (!content) return null;
    return parseEpic(content, fileName, filePath, dir);
  }).filter(Boolean);
}

function parseEpic(content, fileName, filePath, devpaceDir) {
  const id = extractField(content, 'ID') || fileName.replace('.md', '');
  // Normalize: ensure EPIC- prefix
  const normalizedId = id.startsWith('EPIC-') ? id : `EPIC-${id}`;

  const title = extractTitle(content);
  const status = extractField(content, '状态') || '规划中';
  const obj = extractField(content, 'OBJ') || null;
  const externalLink = extractField(content, '外部关联') || null;

  // Extract BR children from the BR table
  const children = extractTableColumn(content, '## 业务需求', 'BR');

  const hashInput = [title, status, children.join(',')].join('|');

  return {
    id: normalizedId,
    type: 'epic',
    title,
    status,
    filepath: relativePath(filePath, devpaceDir),
    source: 'file',
    external_link: parseExternalLink(externalLink),
    content_hash: computeHash(hashInput),
    key_fields: { obj, children }
  };
}

// ── BR Scanner ───────────────────────────────────────────────────────
function scanBRs(dir) {
  const results = [];
  const fileBRIds = new Set();

  // 1. Scan independent files
  const reqDir = join(dir, 'requirements');
  if (existsSync(reqDir)) {
    const files = safeReadDir(reqDir).filter(f => /^BR-\d+\.md$/.test(f)).sort();
    for (const fileName of files) {
      const filePath = join(reqDir, fileName);
      const content = safeReadFile(filePath);
      if (!content) continue;
      const entity = parseBR(content, fileName, filePath, dir);
      if (entity) {
        results.push(entity);
        fileBRIds.add(entity.id);
      }
    }
  }

  // 2. Scan inline BRs from project.md
  const projectPath = join(dir, 'project.md');
  if (existsSync(projectPath)) {
    const projectContent = safeReadFile(projectPath);
    if (projectContent) {
      const inlineBRs = extractInlineBRs(projectContent, dir);
      for (const br of inlineBRs) {
        if (!fileBRIds.has(br.id)) {
          results.push(br);
        }
      }
    }
  }

  return results;
}

function parseBR(content, fileName, filePath, devpaceDir) {
  const id = fileName.replace('.md', '');
  const title = extractTitle(content);
  const status = extractField(content, '状态') || '待开始';
  const priority = extractField(content, '优先级') || '—';
  const epic = extractField(content, 'Epic') || null;
  const externalLink = extractField(content, '外部关联') || null;

  // Extract PF children from the PF table
  const children = extractTableColumn(content, '## 产品功能', 'PF');

  const hashInput = [title, status, priority, children.join(',')].join('|');

  return {
    id,
    type: 'br',
    title,
    status,
    filepath: relativePath(filePath, devpaceDir),
    source: 'file',
    external_link: parseExternalLink(externalLink),
    content_hash: computeHash(hashInput),
    key_fields: { priority, epic, children }
  };
}

function extractInlineBRs(projectContent, devpaceDir) {
  const results = [];
  const lines = projectContent.split('\n');

  // Build Epic section → BR mapping by tracking current Epic context
  let currentEpic = null;
  for (const line of lines) {
    // Detect Epic section headers: ### EPIC-NNN: title or tree format └── EPIC-NNN title
    const epicHeader = line.match(/(?:^###\s*|[└├│─\s]+)(EPIC-\d+)/);
    if (epicHeader) {
      currentEpic = epicHeader[1];
      continue;
    }
    // Reset Epic context at next ## section (non-Epic)
    if (/^##\s/.test(line) && !line.includes('EPIC-')) {
      currentEpic = null;
    }

    // Match BR-NNN on the line (colon or space separated, with optional link brackets)
    const brMatch = line.match(/(?:\[)?(BR-\d+)[：:\s]\s*([^→`\]\n]+)/);
    if (!brMatch) continue;

    // Skip file-linked BRs (e.g., [BR-006: ...](requirements/...))
    if (/\(requirements\//.test(line)) continue;

    const id = brMatch[1];
    const title = brMatch[2].trim();

    // Extract backtick tags from this line
    const tags = [];
    const tagPattern = /`([^`]+)`/g;
    let tagMatch;
    while ((tagMatch = tagPattern.exec(line)) !== null) {
      tags.push(tagMatch[1]);
    }

    let priority = '—';
    let status = '待开始';
    for (const tag of tags) {
      if (/^P[012]$/.test(tag)) priority = tag;
      else if (['进行中', '待开始', '已完成', '暂停'].includes(tag)) status = tag;
    }

    // Extract PF references from this line
    const pfRefs = [];
    const pfRefPattern = /PF-\d+/g;
    let pfMatch;
    while ((pfMatch = pfRefPattern.exec(line)) !== null) {
      pfRefs.push(pfMatch[0]);
    }

    const hashInput = [title, status, priority, pfRefs.join(',')].join('|');

    results.push({
      id,
      type: 'br',
      title,
      status,
      filepath: 'project.md',
      source: 'inline',
      external_link: null,
      content_hash: computeHash(hashInput),
      key_fields: { priority, epic: currentEpic, children: pfRefs }
    });
  }
  return results;
}

// ── PF Scanner ───────────────────────────────────────────────────────
function scanPFs(dir) {
  const results = [];
  const filePFIds = new Set();

  // 1. Scan independent files
  const featDir = join(dir, 'features');
  if (existsSync(featDir)) {
    const files = safeReadDir(featDir).filter(f => /^PF-\d+\.md$/.test(f)).sort();
    for (const fileName of files) {
      const filePath = join(featDir, fileName);
      const content = safeReadFile(filePath);
      if (!content) continue;
      const entity = parsePF(content, fileName, filePath, dir);
      if (entity) {
        results.push(entity);
        filePFIds.add(entity.id);
      }
    }
  }

  // 2. Scan inline PFs from project.md
  const projectPath = join(dir, 'project.md');
  if (existsSync(projectPath)) {
    const projectContent = safeReadFile(projectPath);
    if (projectContent) {
      const inlinePFs = extractInlinePFs(projectContent, dir);
      for (const pf of inlinePFs) {
        if (!filePFIds.has(pf.id)) {
          results.push(pf);
        }
      }
    }
  }

  return results;
}

function parsePF(content, fileName, filePath, devpaceDir) {
  const id = fileName.replace('.md', '');
  const title = extractTitle(content);
  const status = extractField(content, '状态') || '待开始';
  const br = extractField(content, 'BR') || null;
  const userStory = extractField(content, '用户故事') || null;
  const externalLink = extractField(content, '外部关联') || null;

  // Extract acceptance criteria text
  const acText = extractSection(content, '## 验收标准') || '';

  // Extract CR children from the CR table
  const children = extractTableColumn(content, '## 关联 CR', 'CR');

  const hashInput = [title, status, acText.substring(0, 500)].join('|');

  return {
    id,
    type: 'pf',
    title,
    status,
    filepath: relativePath(filePath, devpaceDir),
    source: 'file',
    external_link: parseExternalLink(externalLink),
    content_hash: computeHash(hashInput),
    key_fields: { br, user_story: userStory, children }
  };
}

function extractInlinePFs(projectContent, devpaceDir) {
  const brToPfMap = buildBRtoPFMapping(projectContent);
  const results = [];

  const pfPattern = /(?:^[\s│├└─\-*]*|[→,]\s*)(?:\[)?(PF-\d+)[：:\s]\s*([^→,\]\n]+?)(?:\])?(?:\(([^)]*)\))?\s*(?=[→,\n🚀]|$)/gm;
  let match;
  while ((match = pfPattern.exec(projectContent)) !== null) {
    results.push(parsePFMatch(match, projectContent, brToPfMap));
  }
  return results;
}

function buildBRtoPFMapping(content) {
  const brToPfMap = new Map();
  let currentBR = null;
  for (const line of content.split('\n')) {
    const brOnLine = line.match(/(?:\[)?(BR-\d+)/);
    if (brOnLine) currentBR = brOnLine[1];
    for (const pfMatch of line.matchAll(/PF-\d+/g)) {
      brToPfMap.set(pfMatch[0], currentBR);
    }
  }
  return brToPfMap;
}

function parsePFMatch(match, projectContent, brToPfMap) {
  const id = match[1];
  const title = match[2].trim();
  const userStory = match[3] ? match[3].trim() : null;

  const lineEnd = projectContent.indexOf('\n', match.index);
  const line = projectContent.substring(match.index, lineEnd > -1 ? lineEnd : undefined);

  const crRefs = [...line.matchAll(/CR-\d+/g)].map(m => m[0]);
  const status = inferStatusFromEmoji(line);
  const parentBR = brToPfMap.get(id) || null;

  return {
    id, type: 'pf', title, status,
    filepath: 'project.md', source: 'inline', external_link: null,
    content_hash: computeHash([title, status, ''].join('|')),
    key_fields: { br: parentBR, user_story: userStory, children: crRefs }
  };
}

// ── CR Scanner ───────────────────────────────────────────────────────
function scanCRs(dir) {
  const backlogDir = join(dir, 'backlog');
  if (!existsSync(backlogDir)) return [];

  const files = safeReadDir(backlogDir).filter(f => /^CR-\d+\.md$/.test(f)).sort();
  return files.map(fileName => {
    const filePath = join(backlogDir, fileName);
    const content = safeReadFile(filePath);
    if (!content) return null;
    return parseCR(content, fileName, filePath, dir);
  }).filter(Boolean);
}

function parseCR(content, fileName, filePath, devpaceDir) {
  const id = extractField(content, 'ID') || fileName.replace('.md', '');
  const title = extractTitle(content);
  const status = extractField(content, '状态') || '';
  const pf = extractField(content, '产品功能') || null;
  const externalLink = extractField(content, '外部关联') || null;

  // Extract acceptance criteria from intent section
  const acText = extractSection(content, '### 验收条件') ||
                 extractSection(content, '## 意图') || '';

  // Detect gate results
  const gateResults = [];
  if (/gate1_pass/.test(content) || /Gate 1.*通过/.test(content)) gateResults.push('gate1_pass');
  if (/gate2_pass/.test(content) || /Gate 2.*通过/.test(content)) gateResults.push('gate2_pass');
  if (/gate3_pass/.test(content) || /Gate 3.*通过/.test(content)) gateResults.push('gate3_pass');

  const hashInput = [title, status, acText.substring(0, 500), gateResults.join(',')].join('|');

  return {
    id,
    type: 'cr',
    title,
    status,
    filepath: relativePath(filePath, devpaceDir),
    source: 'file',
    external_link: parseExternalLink(externalLink),
    content_hash: computeHash(hashInput),
    key_fields: { pf, gate_results: gateResults }
  };
}

// ── Phantom Entity Detection ─────────────────────────────────────────

/**
 * Detect Epics referenced in project.md tree view but without independent files.
 * These "phantom" Epics break sub-issue hierarchy (child BRs can't link to parent).
 */
function detectPhantomEpics(dir, scannedEntities) {
  const warnings = [];
  const projectPath = join(dir, 'project.md');
  if (!existsSync(projectPath)) return warnings;

  const content = safeReadFile(projectPath);
  if (!content) return warnings;

  // Find all EPIC-NNN references in project.md
  const epicRefs = new Set();
  const epicPattern = /EPIC-\d+/g;
  let match;
  while ((match = epicPattern.exec(content)) !== null) {
    epicRefs.add(match[0]);
  }

  // Compare with scanned file-based Epics
  const scannedEpicIds = new Set(
    scannedEntities.filter(e => e.type === 'epic' && e.source === 'file').map(e => e.id)
  );

  for (const ref of epicRefs) {
    if (!scannedEpicIds.has(ref)) {
      // Extract title from the tree line if possible
      const lineMatch = content.match(new RegExp(`${escapeRegex(ref)}[：:]\\s*([^\\]\\n]+)`));
      const title = lineMatch ? lineMatch[1].trim() : '(unknown)';

      // Find child BRs: check both key_fields.epic (file-based) and project.md tree structure (inline)
      const affectedBRSet = new Set(
        scannedEntities
          .filter(e => e.type === 'br' && e.key_fields.epic && e.key_fields.epic.includes(ref))
          .map(e => e.id)
      );

      // Also scan project.md tree structure for BRs under this Epic's section
      const sectionRegex = new RegExp(
        `###\\s*${escapeRegex(ref)}[：:][^\\n]*\\n([\\s\\S]*?)(?=\\n###\\s|\\n##\\s|$)`
      );
      const sectionMatch = content.match(sectionRegex);
      if (sectionMatch) {
        const sectionContent = sectionMatch[1];
        const brInSection = /(?:\[)?(BR-\d+)/g;
        let brMatch;
        while ((brMatch = brInSection.exec(sectionContent)) !== null) {
          affectedBRSet.add(brMatch[1]);
        }
      }
      const affectedBRs = [...affectedBRSet];

      warnings.push({
        type: 'phantom_epic',
        id: ref,
        title,
        message: `${ref} 在 project.md 树视图中被引用但无独立文件（.devpace/epics/${ref}.md），其子级 BR 无法建立 sub-issue 层级关系`,
        affected_children: affectedBRs,
        suggestion: `运行 /pace-biz epic 为 ${ref} 创建独立文件，或手动创建 .devpace/epics/${ref}.md`
      });
    }
  }

  return warnings;
}

// ── Local Utilities (not shared) ─────────────────────────────────────

function extractTableColumn(content, sectionHeading, columnPrefix) {
  const section = extractSection(content, sectionHeading);
  if (!section) return [];
  const idSet = new Set();
  const regex = new RegExp(`(${escapeRegex(columnPrefix)}-\\d+)`, 'g');
  let match;
  while ((match = regex.exec(section)) !== null) {
    idSet.add(match[1]);
  }
  return [...idSet];
}

function parseExternalLink(field) {
  if (!field) return null;
  // Extract platform#number from formats like:
  // [github:#42](https://...) or github#42
  const match = field.match(/(\w+)[:#](\d+)/);
  return match ? `${match[1]}#${match[2]}` : null;
}

function computeHash(input) {
  return createHash('md5').update(input).digest('hex').substring(0, 8);
}

function relativePath(filePath, devpaceDir) {
  return filePath.replace(devpaceDir + '/', '').replace(devpaceDir + '\\', '');
}

