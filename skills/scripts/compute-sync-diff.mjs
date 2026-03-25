#!/usr/bin/env node
/**
 * Compute sync diff between current devpace entities and sync-mapping.md records.
 *
 * Usage:
 *   node skills/scripts/compute-sync-diff.mjs <devpace-dir>
 *
 * Output: JSON diff report to stdout.
 *   { platform, summary, entities: { new, changed, unchanged, orphaned } }
 *
 * Dependencies: Node.js only (no npm packages).
 * Requires: extract-entity-metadata.mjs (imported as shared module)
 */

import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ── Parse CLI args ───────────────────────────────────────────────────
const devpaceDir = process.argv[2];

if (!devpaceDir) {
  console.error('Usage: node compute-sync-diff.mjs <devpace-dir>');
  process.exit(1);
}

// ── Main ─────────────────────────────────────────────────────────────

// 1. Get current entity metadata via extract-entity-metadata.mjs
const extractScript = join(__dirname, 'extract-entity-metadata.mjs');
let entities;
try {
  const output = execFileSync('node', [extractScript, devpaceDir, '--type', 'all'], {
    encoding: 'utf-8',
    timeout: 30000
  });
  entities = JSON.parse(output);
} catch (err) {
  console.error(`Error running extract-entity-metadata.mjs: ${err.message}`);
  process.exit(1);
}

// 2. Parse sync-mapping.md
const syncMappingPath = join(devpaceDir, 'integrations', 'sync-mapping.md');
const { platform, records } = parseSyncMapping(syncMappingPath);

if (!platform) {
  console.error('Error: sync-mapping.md not found or missing platform config');
  process.exit(1);
}

// 3. Compute diff
const recordMap = new Map(records.map(r => [r.entity, r]));
const entityMap = new Map(entities.map(e => [e.id, e]));

const diff = { new: [], changed: [], unchanged: [], orphaned: [] };

// Check each entity against records
for (const entity of entities) {
  const record = recordMap.get(entity.id);
  if (!record) {
    // Entity exists but no sync record → new
    diff.new.push({
      id: entity.id,
      type: entity.type,
      title: entity.title,
      status: entity.status,
      source: entity.source,
      content_hash: entity.content_hash
    });
  } else if (!record.hash || record.hash !== entity.content_hash) {
    // Hash differs or missing → changed
    diff.changed.push({
      id: entity.id,
      type: entity.type,
      title: entity.title,
      external: record.external,
      old_hash: record.hash || '(none)',
      new_hash: entity.content_hash,
      status: entity.status
    });
  } else {
    // Hash matches → unchanged
    diff.unchanged.push({
      id: entity.id,
      type: entity.type,
      external: record.external,
      status: entity.status
    });
  }
}

// Check for orphaned records (record exists but entity file gone)
for (const record of records) {
  if (!entityMap.has(record.entity)) {
    diff.orphaned.push({
      id: record.entity,
      external: record.external,
      last_sync: record.last_sync
    });
  }
}

// 4. Output result
const result = {
  platform,
  summary: {
    total_entities: entities.length,
    total_linked: records.length,
    new: diff.new.length,
    changed: diff.changed.length,
    unchanged: diff.unchanged.length,
    orphaned: diff.orphaned.length
  },
  entities: diff
};

console.log(JSON.stringify(result, null, 2));

// ── sync-mapping.md Parser ───────────────────────────────────────────

function parseSyncMapping(filePath) {
  if (!existsSync(filePath)) {
    return { platform: null, records: [] };
  }

  let content;
  try {
    content = readFileSync(filePath, 'utf-8');
  } catch {
    return { platform: null, records: [] };
  }

  // Parse platform section
  const platform = {
    type: extractMappingField(content, '类型'),
    connection: extractMappingField(content, '连接'),
    sync_mode: extractMappingField(content, '同步模式'),
    auto_sync: extractMappingField(content, '自动同步') || 'suggest'
  };

  if (!platform.type) {
    return { platform: null, records: [] };
  }

  // Parse association records table
  const records = parseAssociationTable(content);

  return { platform, records };
}

function extractMappingField(content, fieldName) {
  const regex = new RegExp(`^- \\*\\*${escapeRegex(fieldName)}\\*\\*[：:]\\s*(.+)$`, 'm');
  const match = content.match(regex);
  return match ? match[1].trim() : null;
}

function parseAssociationTable(content) {
  // Find the association records table (## 关联记录)
  const sectionMatch = content.match(/## 关联记录[\s\S]*?\n(\|[^\n]+\n\|[-|\s]+\n)([\s\S]*?)(?=\n## |$)/);
  if (!sectionMatch) return [];

  const headerRow = sectionMatch[1].split('\n')[0];
  const dataSection = sectionMatch[2].trim();
  if (!dataSection) return [];

  // Detect column positions from header
  const headers = headerRow.split('|').map(h => h.trim()).filter(Boolean);
  // Support both old format (CR column) and new format (实体 column)
  const entityIdx = headers.findIndex(h => h === '实体' || h === 'CR');
  const externalIdx = headers.findIndex(h => h === '外部实体');
  const timeIdx = headers.findIndex(h => h === '关联时间');
  const syncIdx = headers.findIndex(h => h === '最后同步');
  const hashIdx = headers.findIndex(h => h === '内容摘要哈希');

  const records = [];
  const rows = dataSection.split('\n');
  for (const row of rows) {
    if (!row.startsWith('|')) continue;
    const cells = row.split('|').map(c => c.trim()).filter(Boolean);
    if (cells.length < 2) continue;

    // Skip template/placeholder rows
    const entityCell = cells[entityIdx] || '';
    if (entityCell.startsWith('[') && entityCell.includes('/')) continue; // Template row like [EPIC-xxx / BR-xxx ...]
    if (!entityCell.match(/^(?:EPIC|BR|PF|CR)-\d{3,}/)) continue;

    records.push({
      entity: entityCell.replace(/[\[\]]/g, ''),
      external: (cells[externalIdx] || '').replace(/[\[\]]/g, ''),
      link_time: cells[timeIdx] || '',
      last_sync: cells[syncIdx] || '',
      hash: hashIdx >= 0 ? (cells[hashIdx] || '').replace(/[\[\]]/g, '') : null
    });
  }

  return records;
}

// ── Utilities ────────────────────────────────────────────────────────

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
