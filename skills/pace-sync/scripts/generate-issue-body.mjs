#!/usr/bin/env node
/**
 * Generate GitHub Issue body content for devpace entities (Epic/BR/PF/CR).
 *
 * Usage:
 *   node generate-issue-body.mjs <devpace-dir> --id <entity-ID>
 *
 * Output: JSON to stdout
 *   { id, type, title, body, labels: [...], status }
 *
 * Dependencies: Node.js only (no npm packages).
 */

import { join } from 'node:path';
import {
  extractTitle as sharedExtractTitle, extractField, extractSection,
  escapeRegex, getFlagValue, safeReadFile, inferStatusFromEmoji, ENTITY_DIR_MAP
} from './shared-utils.mjs';

// ── File Content Cache (eliminates N+1 redundant reads) ─────────────
const fileCache = new Map();
function cachedReadFile(filePath) {
  if (fileCache.has(filePath)) return fileCache.get(filePath);
  const content = safeReadFile(filePath);
  fileCache.set(filePath, content);
  return content;
}

// ── Parse CLI args ───────────────────────────────────────────────────
const args = process.argv.slice(2);
const devpaceDir = args[0];
const entityId = getFlagValue(args, '--id');

if (!devpaceDir || !entityId) {
  console.error('Usage: node generate-issue-body.mjs <devpace-dir> --id <entity-ID>');
  process.exit(1);
}

// ── Main ─────────────────────────────────────────────────────────────
try {
  const result = generateIssueBody(devpaceDir, entityId);
  console.log(JSON.stringify(result, null, 2));
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}

// ── Generate Issue Body ──────────────────────────────────────────────
function generateIssueBody(dir, id) {
  const type = detectEntityType(id);

  if (type === 'epic') {
    return generateEpicBody(dir, id);
  } else if (type === 'br') {
    return generateBRBody(dir, id);
  } else if (type === 'pf') {
    return generatePFBody(dir, id);
  } else if (type === 'cr') {
    return generateCRBody(dir, id);
  } else {
    throw new Error(`Unknown entity type for ID: ${id}`);
  }
}

// ── Epic Body Generator ──────────────────────────────────────────────
function generateEpicBody(dir, id) {
  const filePath = join(dir, ENTITY_DIR_MAP.epic, `${id}.md`);
  const content = cachedReadFile(filePath);
  if (!content) throw new Error(`Epic file not found: ${filePath}`);
  const title = extractLocalTitle(content);
  const status = extractField(content, '状态') || '规划中';
  const obj = extractField(content, 'OBJ') || extractField(content, '关联 OBJ') || '—';
  const background = extractSection(content, '## 描述') || extractSection(content, '## 背景') || '—';
  const mosText = extractSection(content, '## 成效指标') || extractField(content, 'MoS') || '—';

  const brSection = extractSection(content, '## 业务需求');
  const brRows = extractBRTableRows(brSection, dir);

  const body = `## ${title}

**业务目标**：${obj}
**状态**：${status}

### 背景
${background}

### 成效指标
${mosText}

### 业务需求
| BR | 标题 | 优先级 | 状态 |
|----|------|--------|------|
${brRows}

---
_由 devpace 自动创建 · 类型：Epic_`;

  const labels = getLabelsForEntity('epic', status);

  return {
    id,
    type: 'epic',
    title,
    body,
    labels,
    status
  };
}

// ── BR Body Generator ────────────────────────────────────────────────
function generateBRBody(dir, id) {
  const filePath = join(dir, ENTITY_DIR_MAP.br, `${id}.md`);
  const content = cachedReadFile(filePath);
  if (content) {
    return generateBRBodyFromFile(dir, id, content);
  }
  return generateBRBodyFromInline(dir, id);
}

function generateBRBodyFromFile(dir, id, content) {
  const title = extractLocalTitle(content);
  const status = extractField(content, '状态') || '待开始';
  const priority = extractField(content, '优先级') || '—';
  const epicRef = extractField(content, 'Epic') || '—';
  const context = extractSection(content, '## 业务上下文') || '—';

  let epicTitle = '—';
  let epicId = epicRef;
  const epicMatch = epicRef !== '—' ? epicRef.match(/EPIC-\d+/) : null;
  if (epicMatch) {
    epicId = epicMatch[0];
    epicTitle = getEntityTitle(dir, epicId, ENTITY_DIR_MAP.epic);
  }
  const pfSection = extractSection(content, '## 产品功能');
  const pfRows = extractPFTableRows(pfSection, dir);

  const body = `## ${title}

**Epic**：${epicTitle}（${epicId}）
**优先级**：${priority}
**状态**：${status}

### 业务上下文
${context}

### 产品功能
| PF | 标题 | 状态 |
|----|------|------|
${pfRows}

---
_由 devpace 自动创建 · 类型：BR_`;

  const labels = getLabelsForEntity('br', status);

  return {
    id,
    type: 'br',
    title,
    body,
    labels,
    status
  };
}

function generateBRBodyFromInline(dir, id) {
  const projectPath = join(dir, 'project.md');
  const content = cachedReadFile(projectPath);
  if (!content) throw new Error(`BR ${id} not found in requirements/ or project.md`);
  const lines = content.split('\n');

  let title = '—';
  let status = '待开始';
  let priority = '—';
  let epicId = '—';
  let pfRefs = [];

  const brIdRegex = new RegExp(`(?:\\[)?${escapeRegex(id)}[：:\\s]\\s*([^→\`\\]\\n]+)`);
  let currentEpic = null;
  for (const line of lines) {
    const epicMatch = line.match(/(?:^###\s*|[└├│─\s]+)(EPIC-\d+)/);
    if (epicMatch) {
      currentEpic = epicMatch[1];
    }
    if (/^##\s/.test(line) && !line.includes('EPIC-')) {
      currentEpic = null;
    }

    const brMatch = line.match(brIdRegex);
    if (brMatch) {
      title = brMatch[1].trim();
      epicId = currentEpic || '—';

      const tags = [];
      const tagPattern = /`([^`]+)`/g;
      let tagMatch;
      while ((tagMatch = tagPattern.exec(line)) !== null) {
        tags.push(tagMatch[1]);
      }

      for (const tag of tags) {
        if (/^P[012]$/.test(tag)) priority = tag;
        else if (['进行中', '待开始', '已完成', '暂停'].includes(tag)) status = tag;
      }

      const pfPattern = /PF-\d+/g;
      let pfMatch;
      while ((pfMatch = pfPattern.exec(line)) !== null) {
        pfRefs.push(pfMatch[0]);
      }
      break;
    }
  }

  if (title === '—') {
    throw new Error(`BR ${id} not found in project.md`);
  }

  const epicTitle = epicId !== '—' ? getEntityTitle(dir, epicId, ENTITY_DIR_MAP.epic) : '—';

  const pfRows = pfRefs.map(pfId => {
    const pfTitle = getEntityTitle(dir, pfId, ENTITY_DIR_MAP.pf);
    const pfStatus = getEntityStatus(dir, pfId, ENTITY_DIR_MAP.pf, '待开始');
    return `| ${pfId} | ${pfTitle} | ${pfStatus} |`;
  }).join('\n') || '| — | — | — |';

  const body = `## ${title}

**Epic**：${epicTitle}（${epicId}）
**优先级**：${priority}
**状态**：${status}

### 业务上下文
—

### 产品功能
| PF | 标题 | 状态 |
|----|------|------|
${pfRows}

---
_由 devpace 自动创建 · 类型：BR_`;

  const labels = getLabelsForEntity('br', status);

  return {
    id,
    type: 'br',
    title,
    body,
    labels,
    status
  };
}

// ── PF Body Generator ────────────────────────────────────────────────
function generatePFBody(dir, id) {
  const filePath = join(dir, ENTITY_DIR_MAP.pf, `${id}.md`);
  const content = cachedReadFile(filePath);
  if (content) {
    return generatePFBodyFromFile(dir, id, content);
  }
  return generatePFBodyFromInline(dir, id);
}

function generatePFBodyFromFile(dir, id, content) {
  const title = extractLocalTitle(content);
  const status = extractField(content, '状态') || '待开始';
  const brRef = extractField(content, 'BR') || '—';
  const userStory = extractField(content, '用户故事') || '—';
  const acText = extractSection(content, '## 验收标准') || '—';

  let brTitle = '—';
  let brId = brRef;
  const brMatch = brRef !== '—' ? brRef.match(/BR-\d+/) : null;
  if (brMatch) {
    brId = brMatch[0];
    brTitle = getEntityTitle(dir, brId, ENTITY_DIR_MAP.br);
  }
  const crSection = extractSection(content, '## 关联 CR');
  const crRows = extractCRTableRows(crSection, dir);

  const body = `## ${title}

**业务需求**：${brTitle}（${brId}）
**用户故事**：${userStory}
**状态**：${status}

### 验收标准
${acText}

### 关联 CR
| CR | 状态 | 标题 |
|----|------|------|
${crRows}

---
_由 devpace 自动创建 · 类型：PF_`;

  const labels = getLabelsForEntity('pf', status);

  return {
    id,
    type: 'pf',
    title,
    body,
    labels,
    status
  };
}

function generatePFBodyFromInline(dir, id) {
  const projectPath = join(dir, 'project.md');
  const content = cachedReadFile(projectPath);
  if (!content) throw new Error(`PF ${id} not found in features/ or project.md`);

  const pfPattern = new RegExp(`(?:\\[)?${escapeRegex(id)}[：:\\s]\\s*([^→,\\]\\n]+?)(?:\\])?(?:\\(([^)]*)\\))?\\s*(?=[→,\\n🚀]|$)`);
  const match = pfPattern.exec(content);

  if (!match) {
    throw new Error(`PF ${id} not found in project.md`);
  }

  const title = match[1].trim();
  const userStory = match[2] ? match[2].trim() : '—';

  const lineEnd = content.indexOf('\n', match.index);
  const line = content.substring(match.index, lineEnd > -1 ? lineEnd : undefined);
  const status = inferStatusFromEmoji(line);
  const crRefs = [];
  const crPattern = /CR-\d+/g;
  let crMatch;
  while ((crMatch = crPattern.exec(line)) !== null) {
    crRefs.push(crMatch[0]);
  }

  const lines = content.split('\n');
  let brId = '—';
  let currentBR = null;
  for (const l of lines) {
    const brOnLine = l.match(/(?:\[)?(BR-\d+)/);
    if (brOnLine) currentBR = brOnLine[1];
    if (l.includes(id)) {
      brId = currentBR || '—';
      break;
    }
  }

  const brTitle = brId !== '—' ? getEntityTitle(dir, brId, ENTITY_DIR_MAP.br) : '—';

  const crRows = crRefs.map(crId => {
    const crTitle = getEntityTitle(dir, crId, ENTITY_DIR_MAP.cr);
    const crStatus = getEntityStatus(dir, crId, ENTITY_DIR_MAP.cr, '—');
    return `| ${crId} | ${crStatus} | ${crTitle} |`;
  }).join('\n') || '| — | — | — |';

  const body = `## ${title}

**业务需求**：${brTitle}（${brId}）
**用户故事**：${userStory}
**状态**：${status}

### 验收标准
—

### 关联 CR
| CR | 状态 | 标题 |
|----|------|------|
${crRows}

---
_由 devpace 自动创建 · 类型：PF_`;

  const labels = getLabelsForEntity('pf', status);

  return {
    id,
    type: 'pf',
    title,
    body,
    labels,
    status
  };
}

// ── CR Body Generator ────────────────────────────────────────────────
function generateCRBody(dir, id) {
  const filePath = join(dir, ENTITY_DIR_MAP.cr, `${id}.md`);
  const content = cachedReadFile(filePath);
  if (!content) throw new Error(`CR file not found: ${filePath}`);
  const title = extractLocalTitle(content);
  const status = extractField(content, '状态') || extractStatusFromMeta(content);
  const pfRef = extractField(content, '产品功能') || '—';
  const intentText = extractSection(content, '## intent') || extractSection(content, '## 意图') || '—';
  const acSection = extractSection(content, '### 验收条件') || extractSection(content, '## acceptance-criteria') || '—';

  let pfTitle = '—';
  let pfId = pfRef;
  const pfMatch = pfRef !== '—' ? pfRef.match(/PF-\d+/) : null;
  if (pfMatch) {
    pfId = pfMatch[0];
    pfTitle = getEntityTitle(dir, pfId, ENTITY_DIR_MAP.pf);
  }

  const body = `## ${title}

**意图**：${intentText}

**验收条件**：
${acSection}

**关联功能**：${pfTitle}

---
_由 devpace 自动创建 · 类型：CR_`;

  const labels = getLabelsForEntity('cr', status);

  return {
    id,
    type: 'cr',
    title,
    body,
    labels,
    status
  };
}

// ── Table Row Extractors ─────────────────────────────────────────────
function extractBRTableRows(section, dir) {
  if (!section) return '| — | — | — | — |';

  const rows = [];
  const lines = section.split('\n');

  for (const line of lines) {
    const match = line.match(/\|\s*(BR-\d+)/);
    if (!match) continue;

    const brId = match[1];
    const titleMatch = line.match(/\|\s*BR-\d+\s*\|\s*([^|]+)\s*\|/);
    const title = titleMatch ? titleMatch[1].trim() : getEntityTitle(dir, brId, ENTITY_DIR_MAP.br);
    const priority = extractFromTableCell(line, 2) || '—';
    const status = extractFromTableCell(line, 3) || '待开始';

    rows.push(`| ${brId} | ${title} | ${priority} | ${status} |`);
  }

  return rows.join('\n') || '| — | — | — | — |';
}

function extractPFTableRows(section, dir) {
  if (!section) return '| — | — | — |';

  const rows = [];
  const lines = section.split('\n');

  for (const line of lines) {
    const match = line.match(/\|\s*(PF-\d+)/);
    if (!match) continue;

    const pfId = match[1];
    const titleMatch = line.match(/\|\s*PF-\d+\s*\|\s*([^|]+)\s*\|/);
    const title = titleMatch ? titleMatch[1].trim() : getEntityTitle(dir, pfId, ENTITY_DIR_MAP.pf);
    const status = extractFromTableCell(line, 2) || '待开始';

    rows.push(`| ${pfId} | ${title} | ${status} |`);
  }

  return rows.join('\n') || '| — | — | — |';
}

function extractCRTableRows(section, dir) {
  if (!section) return '| — | — | — |';

  const rows = [];
  const lines = section.split('\n');

  for (const line of lines) {
    const match = line.match(/\|\s*(CR-\d+)/);
    if (!match) continue;

    const crId = match[1];
    const status = extractFromTableCell(line, 1) || getEntityStatus(dir, crId, ENTITY_DIR_MAP.cr, '—');
    const titleMatch = line.match(/\|\s*CR-\d+\s*\|\s*[^|]+\s*\|\s*([^|]+)\s*\|/);
    const title = titleMatch ? titleMatch[1].trim() : getEntityTitle(dir, crId, ENTITY_DIR_MAP.cr);

    rows.push(`| ${crId} | ${status} | ${title} |`);
  }

  return rows.join('\n') || '| — | — | — |';
}

function extractFromTableCell(line, cellIndex) {
  const cells = line.split('|').map(c => c.trim()).filter(c => c);
  return cells[cellIndex] || null;
}

// ── Label Mapping ────────────────────────────────────────────────────
function getLabelsForEntity(type, status) {
  const labels = [`devpace:${type}`];

  const statusLabels = {
    // CR
    'created': ['backlog'],
    'developing': ['in-progress'],
    'verifying': ['needs-review'],
    'in_review': ['awaiting-approval'],
    'approved': ['approved'],
    'merged': ['done'],
    'released': ['done', 'released'],
    'paused': ['on-hold'],
    // Epic
    '规划中': ['planning'],
    '进行中': ['in-progress'],
    '已搁置': ['on-hold'],
    // BR/PF/Epic shared
    '已完成': ['done'],
    '待开始': ['backlog'],
    '待启动': ['backlog'],
    '暂停': ['on-hold'],
    '全部CR完成': ['done'],
    '已发布': ['done', 'released']
  };

  const statusLabel = statusLabels[status] || ['backlog'];
  return [...labels, ...statusLabel];
}

// ── Helper Functions ─────────────────────────────────────────────────
function detectEntityType(id) {
  if (/^EPIC-\d+/.test(id)) return 'epic';
  if (/^BR-\d+/.test(id)) return 'br';
  if (/^PF-\d+/.test(id)) return 'pf';
  if (/^CR-\d+/.test(id)) return 'cr';
  return null;
}

function extractLocalTitle(content) {
  return sharedExtractTitle(content) || '—';
}

function extractStatusFromMeta(content) {
  const match = content.match(/^- status:\s*(.+)$/m);
  return match ? match[1].trim() : '';
}

// Unified entity title lookup: file → project.md fallback → '—'
function getEntityTitle(dir, entityId, subdir) {
  const filePath = join(dir, subdir, `${entityId}.md`);
  const content = cachedReadFile(filePath);
  if (content) return extractLocalTitle(content);

  // BR and PF have project.md fallback
  if (subdir === ENTITY_DIR_MAP.br || subdir === ENTITY_DIR_MAP.pf) {
    const projectContent = cachedReadFile(join(dir, 'project.md'));
    if (projectContent) {
      const sep = subdir === ENTITY_DIR_MAP.br ? '[：:\\s]\\s*([^→`\\]\\n]+)' : '[：:\\s]\\s*([^→,\\]\\n]+)';
      const match = projectContent.match(new RegExp(`${escapeRegex(entityId)}${sep}`));
      if (match) return match[1].trim();
    }
  }
  return '—';
}

// Unified entity status lookup: file → project.md emoji fallback → default
function getEntityStatus(dir, entityId, subdir, defaultStatus) {
  const filePath = join(dir, subdir, `${entityId}.md`);
  const content = cachedReadFile(filePath);
  if (content) {
    return extractField(content, '状态') || extractStatusFromMeta(content) || defaultStatus;
  }

  // PF has project.md emoji fallback
  if (subdir === ENTITY_DIR_MAP.pf) {
    const projectContent = cachedReadFile(join(dir, 'project.md'));
    if (projectContent) {
      const lineMatch = projectContent.match(new RegExp(`${escapeRegex(entityId)}[^\\n]*`));
      if (lineMatch) return inferStatusFromEmoji(lineMatch[0]);
    }
  }
  return defaultStatus;
}

