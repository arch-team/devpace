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

import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

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
  const filePath = join(dir, 'epics', `${id}.md`);

  if (!existsSync(filePath)) {
    throw new Error(`Epic file not found: ${filePath}`);
  }

  const content = readFileSync(filePath, 'utf-8');
  const title = extractTitle(content);
  const status = extractField(content, '状态') || '规划中';
  const obj = extractField(content, 'OBJ') || extractField(content, '关联 OBJ') || '—';
  const background = extractSection(content, '## 描述') || extractSection(content, '## 背景') || '—';
  const mosText = extractSection(content, '## 成效指标') || extractField(content, 'MoS') || '—';

  // Extract BR table rows
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
  // Try independent file first
  const filePath = join(dir, 'requirements', `${id}.md`);

  if (existsSync(filePath)) {
    return generateBRBodyFromFile(dir, id, filePath);
  } else {
    return generateBRBodyFromInline(dir, id);
  }
}

function generateBRBodyFromFile(dir, id, filePath) {
  const content = readFileSync(filePath, 'utf-8');
  const title = extractTitle(content);
  const status = extractField(content, '状态') || '待开始';
  const priority = extractField(content, '优先级') || '—';
  const epicRef = extractField(content, 'Epic') || '—';
  const context = extractSection(content, '## 业务上下文') || '—';

  // Extract Epic title if Epic reference exists
  let epicTitle = '—';
  let epicId = epicRef;
  if (epicRef !== '—' && /EPIC-\d+/.test(epicRef)) {
    const epicMatch = epicRef.match(/EPIC-\d+/);
    if (epicMatch) {
      epicId = epicMatch[0];
      epicTitle = getEpicTitle(dir, epicId);
    }
  }

  // Extract PF table rows
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

  if (!existsSync(projectPath)) {
    throw new Error(`BR ${id} not found in requirements/ or project.md`);
  }

  const content = readFileSync(projectPath, 'utf-8');
  const lines = content.split('\n');

  // Find BR line
  let title = '—';
  let status = '待开始';
  let priority = '—';
  let epicId = '—';
  let pfRefs = [];

  let currentEpic = null;
  for (const line of lines) {
    // Track Epic context
    const epicMatch = line.match(/(?:^###\s*|[└├│─\s]+)(EPIC-\d+)/);
    if (epicMatch) {
      currentEpic = epicMatch[1];
    }
    if (/^##\s/.test(line) && !line.includes('EPIC-')) {
      currentEpic = null;
    }

    // Match BR line
    const brMatch = line.match(new RegExp(`(?:\\[)?${escapeRegex(id)}[：:\\s]\\s*([^→\`\\]\\n]+)`));
    if (brMatch) {
      title = brMatch[1].trim();
      epicId = currentEpic || '—';

      // Extract tags
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

      // Extract PF references
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

  const epicTitle = epicId !== '—' ? getEpicTitle(dir, epicId) : '—';

  // Build PF rows from references
  const pfRows = pfRefs.map(pfId => {
    const pfTitle = getPFTitle(dir, pfId);
    const pfStatus = getPFStatus(dir, pfId);
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
  // Try independent file first
  const filePath = join(dir, 'features', `${id}.md`);

  if (existsSync(filePath)) {
    return generatePFBodyFromFile(dir, id, filePath);
  } else {
    return generatePFBodyFromInline(dir, id);
  }
}

function generatePFBodyFromFile(dir, id, filePath) {
  const content = readFileSync(filePath, 'utf-8');
  const title = extractTitle(content);
  const status = extractField(content, '状态') || '待开始';
  const brRef = extractField(content, 'BR') || '—';
  const userStory = extractField(content, '用户故事') || '—';
  const acText = extractSection(content, '## 验收标准') || '—';

  // Extract BR title
  let brTitle = '—';
  let brId = brRef;
  if (brRef !== '—' && /BR-\d+/.test(brRef)) {
    const brMatch = brRef.match(/BR-\d+/);
    if (brMatch) {
      brId = brMatch[0];
      brTitle = getBRTitle(dir, brId);
    }
  }

  // Extract CR table rows
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

  if (!existsSync(projectPath)) {
    throw new Error(`PF ${id} not found in features/ or project.md`);
  }

  const content = readFileSync(projectPath, 'utf-8');

  // Match PF line
  const pfPattern = new RegExp(`(?:\\[)?${escapeRegex(id)}[：:\\s]\\s*([^→,\\]\\n]+?)(?:\\])?(?:\\(([^)]*)\\))?\\s*(?=[→,\\n🚀]|$)`);
  const match = pfPattern.exec(content);

  if (!match) {
    throw new Error(`PF ${id} not found in project.md`);
  }

  const title = match[1].trim();
  const userStory = match[2] ? match[2].trim() : '—';

  // Extract status from emoji
  const lineEnd = content.indexOf('\n', match.index);
  const line = content.substring(match.index, lineEnd > -1 ? lineEnd : undefined);

  let status = '待开始';
  if (/✅/.test(line)) status = '全部CR完成';
  else if (/🔄/.test(line)) status = '进行中';
  else if (/🚀/.test(line)) status = '已发布';
  else if (/⏸️/.test(line)) status = '暂停';

  // Extract CR references
  const crRefs = [];
  const crPattern = /CR-\d+/g;
  let crMatch;
  while ((crMatch = crPattern.exec(line)) !== null) {
    crRefs.push(crMatch[0]);
  }

  // Find parent BR
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

  const brTitle = brId !== '—' ? getBRTitle(dir, brId) : '—';

  // Build CR rows
  const crRows = crRefs.map(crId => {
    const crTitle = getCRTitle(dir, crId);
    const crStatus = getCRStatus(dir, crId);
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
  const filePath = join(dir, 'backlog', `${id}.md`);

  if (!existsSync(filePath)) {
    throw new Error(`CR file not found: ${filePath}`);
  }

  const content = readFileSync(filePath, 'utf-8');
  const title = extractTitle(content);
  const status = extractField(content, '状态') || extractStatusFromMeta(content);
  const pfRef = extractField(content, '产品功能') || '—';
  const intentText = extractSection(content, '## intent') || extractSection(content, '## 意图') || '—';
  const acSection = extractSection(content, '### 验收条件') || extractSection(content, '## acceptance-criteria') || '—';

  // Extract PF title
  let pfTitle = '—';
  let pfId = pfRef;
  if (pfRef !== '—' && /PF-\d+/.test(pfRef)) {
    const pfMatch = pfRef.match(/PF-\d+/);
    if (pfMatch) {
      pfId = pfMatch[0];
      pfTitle = getPFTitle(dir, pfId);
    }
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
    const title = titleMatch ? titleMatch[1].trim() : getBRTitle(dir, brId);
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
    const title = titleMatch ? titleMatch[1].trim() : getPFTitle(dir, pfId);
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
    const status = extractFromTableCell(line, 1) || getCRStatus(dir, crId);
    const titleMatch = line.match(/\|\s*CR-\d+\s*\|\s*[^|]+\s*\|\s*([^|]+)\s*\|/);
    const title = titleMatch ? titleMatch[1].trim() : getCRTitle(dir, crId);

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
    '已完成': ['done'],
    '已搁置': ['on-hold'],
    // BR/PF
    '待开始': ['backlog'],
    '待启动': ['backlog'],
    '暂停': ['on-hold'],
    '全部CR完成': ['done'],
    '已发布': ['done', 'released'],
    '已完成': ['done']
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

function extractTitle(content) {
  const match = content.match(/^# (.+)$/m);
  return match ? match[1].trim() : '—';
}

function extractField(content, fieldName) {
  const regex = new RegExp(`^- \\*\\*${escapeRegex(fieldName)}\\*\\*[：:]\\s*(.+)$`, 'm');
  const match = content.match(regex);
  return match ? match[1].trim() : null;
}

function extractSection(content, heading) {
  const escaped = escapeRegex(heading);
  const regex = new RegExp(`${escaped}\\s*\\n([\\s\\S]*?)(?=\\n## |\\n# |$)`);
  const match = content.match(regex);
  return match ? match[1].trim() : null;
}

function extractStatusFromMeta(content) {
  const match = content.match(/^- status:\s*(.+)$/m);
  return match ? match[1].trim() : '';
}

function getEpicTitle(dir, epicId) {
  const filePath = join(dir, 'epics', `${epicId}.md`);
  if (!existsSync(filePath)) return '—';
  try {
    const content = readFileSync(filePath, 'utf-8');
    return extractTitle(content);
  } catch {
    return '—';
  }
}

function getBRTitle(dir, brId) {
  const filePath = join(dir, 'requirements', `${brId}.md`);
  if (existsSync(filePath)) {
    try {
      const content = readFileSync(filePath, 'utf-8');
      return extractTitle(content);
    } catch {
      return '—';
    }
  }

  // Try project.md
  const projectPath = join(dir, 'project.md');
  if (existsSync(projectPath)) {
    try {
      const content = readFileSync(projectPath, 'utf-8');
      const match = content.match(new RegExp(`${escapeRegex(brId)}[：:\\s]\\s*([^→\`\\]\\n]+)`));
      return match ? match[1].trim() : '—';
    } catch {
      return '—';
    }
  }

  return '—';
}

function getPFTitle(dir, pfId) {
  const filePath = join(dir, 'features', `${pfId}.md`);
  if (existsSync(filePath)) {
    try {
      const content = readFileSync(filePath, 'utf-8');
      return extractTitle(content);
    } catch {
      return '—';
    }
  }

  // Try project.md
  const projectPath = join(dir, 'project.md');
  if (existsSync(projectPath)) {
    try {
      const content = readFileSync(projectPath, 'utf-8');
      const match = content.match(new RegExp(`${escapeRegex(pfId)}[：:\\s]\\s*([^→,\\]\\n]+)`));
      return match ? match[1].trim() : '—';
    } catch {
      return '—';
    }
  }

  return '—';
}

function getPFStatus(dir, pfId) {
  const filePath = join(dir, 'features', `${pfId}.md`);
  if (existsSync(filePath)) {
    try {
      const content = readFileSync(filePath, 'utf-8');
      return extractField(content, '状态') || '待开始';
    } catch {
      return '待开始';
    }
  }

  // Try project.md
  const projectPath = join(dir, 'project.md');
  if (existsSync(projectPath)) {
    try {
      const content = readFileSync(projectPath, 'utf-8');
      const lineMatch = content.match(new RegExp(`${escapeRegex(pfId)}[^\\n]*`));
      if (!lineMatch) return '待开始';
      const line = lineMatch[0];
      if (/✅/.test(line)) return '全部CR完成';
      if (/🔄/.test(line)) return '进行中';
      if (/🚀/.test(line)) return '已发布';
      if (/⏸️/.test(line)) return '暂停';
      return '待开始';
    } catch {
      return '待开始';
    }
  }

  return '待开始';
}

function getCRTitle(dir, crId) {
  const filePath = join(dir, 'backlog', `${crId}.md`);
  if (!existsSync(filePath)) return '—';
  try {
    const content = readFileSync(filePath, 'utf-8');
    return extractTitle(content);
  } catch {
    return '—';
  }
}

function getCRStatus(dir, crId) {
  const filePath = join(dir, 'backlog', `${crId}.md`);
  if (!existsSync(filePath)) return '—';
  try {
    const content = readFileSync(filePath, 'utf-8');
    return extractField(content, '状态') || extractStatusFromMeta(content) || '—';
  } catch {
    return '—';
  }
}

function getFlagValue(argList, flag) {
  const idx = argList.indexOf(flag);
  return idx >= 0 && idx + 1 < argList.length ? argList[idx + 1] : null;
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
