#!/usr/bin/env node
/**
 * Signal collection engine for devpace.
 *
 * Evaluates signal conditions (S1-S22, S24-S25; S23 reserved) from 11 data sources,
 * replaces LLM-driven Glob+Grep+reasoning with deterministic checks.
 *
 * Usage:
 *   node skills/pace-next/scripts/collect-signals.mjs <devpace-dir>
 *   node skills/pace-next/scripts/collect-signals.mjs <devpace-dir> --role pm
 *   node skills/pace-next/scripts/collect-signals.mjs <devpace-dir> --cache
 *   node skills/pace-next/scripts/collect-signals.mjs <devpace-dir> --cache-read
 *
 * Output: JSON { triggered[], top_signal, role, cr_summary, timestamp }
 *
 * Dependencies: Node.js only. Reuses skills/scripts/extract-cr-metadata.mjs for CR scanning.
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// ── Constants ────────────────────────────────────────────────────────
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

const SIGNAL_GROUPS = ['blocking', 'in_progress', 'delivery', 'strategic', 'growth'];

const ROLE_PROMOTIONS = {
  pm:     { promote: ['S8', 'S13'] },
  biz:    { promote: ['S12', 'S13'] },
  ops:    { promote: ['S5', 'S11'] },
  tester: { promote: ['S10', 'S6'] },
  dev:    { promote: [] },
};

const SIGNAL_GROUP_MAP = {
  S1: 'blocking', S2: 'blocking',
  S3: 'in_progress', S4: 'in_progress',
  S5: 'delivery', S6: 'delivery', S7: 'delivery', S8: 'delivery',
  S9: 'strategic', S10: 'strategic', S11: 'strategic', S12: 'strategic',
  S13: 'growth', S14: 'growth', S15: 'growth', S16: 'growth',
  S17: 'growth', S18: 'growth', S19: 'growth', S20: 'idle',
  S21: 'growth', S22: 'growth', /* S23: reserved */ S24: 'growth', S25: 'blocking',
};

// ── CLI ──────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const devpaceDir = args[0];
if (!devpaceDir) {
  console.error('Usage: node collect-signals.mjs <devpace-dir> [--role dev|pm|biz|ops|tester] [--cache] [--cache-read]');
  process.exit(1);
}
const role = getFlagValue(args, '--role') || 'dev';
const writeCache = args.includes('--cache');
const cacheReadOnly = args.includes('--cache-read');

// ── Cache check ──────────────────────────────────────────────────────
if (cacheReadOnly) {
  const cached = readCache(devpaceDir);
  if (cached) {
    console.log(JSON.stringify(cached, null, 2));
    process.exit(0);
  }
  // Cache miss — fall through to full collection
}

// ── Data collection ──────────────────────────────────────────────────
const data = collectData(devpaceDir);

// ── Signal evaluation ────────────────────────────────────────────────
const triggered = evaluateSignals(data, devpaceDir);

// ── Role reordering ──────────────────────────────────────────────────
const reordered = applyRoleReorder(triggered, role);

// ── Build output ─────────────────────────────────────────────────────
const topSignal = reordered.length > 0 ? reordered[0].id : 'S20';
const now = new Date().toISOString();

const output = {
  triggered: reordered,
  top_signal: topSignal,
  role,
  role_adjusted: role !== 'dev' && reordered.some(s => s.role_promoted),
  cr_summary: data.crSummary,
  timestamp: now,
  cached: false,
};

// ── Write cache ──────────────────────────────────────────────────────
if (writeCache) {
  writeCacheFile(devpaceDir, output);
}

console.log(JSON.stringify(output, null, 2));

// ══════════════════════════════════════════════════════════════════════
// DATA COLLECTION
// ══════════════════════════════════════════════════════════════════════

function collectData(devDir) {
  const data = {
    crs: [],
    crSummary: { total: 0, developing: 0, in_review: 0, merged: 0, paused: 0, created: 0, verifying: 0, approved: 0, released: 0 },
    releases: [],
    risks: [],
    iteration: null,
    dashboardAge: null,
    projectMeta: { pfCount: 0, pfWithoutCr: 0, scopeExists: false, mosCheckboxes: { total: 0, checked: 0 } },
    epics: [],
    opportunities: [],
    syncMapping: null,
    projectAge: null,
  };

  // DS1: backlog CRs
  data.crs = loadCrMetadata(devDir);
  for (const cr of data.crs) {
    data.crSummary.total++;
    if (cr.status in data.crSummary) data.crSummary[cr.status]++;
  }

  // DS3: releases
  data.releases = scanReleases(devDir);

  // DS4: risks
  data.risks = scanRisks(devDir);

  // DS5: iteration/current.md
  data.iteration = readIteration(devDir);

  // DS6: dashboard age
  data.dashboardAge = getDashboardAge(devDir);

  // DS7: project.md metadata
  data.projectMeta = readProjectMeta(devDir);

  // DS8: sync-mapping
  data.syncMapping = readSyncMapping(devDir);

  // DS10: epics
  data.epics = scanEpics(devDir);

  // DS11: opportunities
  data.opportunities = readOpportunities(devDir);

  // Project age (for S18)
  data.projectAge = getProjectAge(devDir);

  return data;
}

function loadCrMetadata(devDir) {
  try {
    const scriptDir = fileURLToPath(new URL('.', import.meta.url));
    const output = execFileSync(
      'node', [join(scriptDir, '..', '..', 'scripts', 'extract-cr-metadata.mjs'), devDir],
      { encoding: 'utf-8', timeout: 10000 }
    );
    return JSON.parse(output);
  } catch {
    // Fallback: manual scan
    return manualScanCrs(devDir);
  }
}

function manualScanCrs(devDir) {
  const backlog = join(devDir, 'backlog');
  if (!existsSync(backlog)) return [];
  const crs = [];
  for (const f of readdirSync(backlog).filter(f => /^CR-\d{3,}\.md$/.test(f))) {
    try {
      const content = readFileSync(join(backlog, f), 'utf-8');
      const status = extractField(content, '状态') || '';
      const type = extractField(content, '类型') || 'feature';
      const pf = extractField(content, '产品功能') || '';
      const blocked = extractField(content, '阻塞') || '';
      const events = extractEventsBasic(content);
      crs.push({ id: f.replace('.md', ''), title: extractTitle(content), status, type, breaking: false, pf, blocked, events });
    } catch { /* skip unreadable */ }
  }
  return crs;
}

function extractEventsBasic(content) {
  const events = [];
  const tableMatch = content.match(/## 事件\s*\n+\|[^\n]+\n\|[-|\s]+\n([\s\S]*?)(?=\n## |$)/);
  if (!tableMatch) return events;
  const rows = tableMatch[1].trim().split('\n');
  for (const row of rows) {
    if (!row.startsWith('|')) continue;
    const cells = row.split('|').map(c => c.trim()).filter(Boolean);
    if (cells.length >= 3) {
      events.push({ date: cells[0], type: cells[1], event: cells[1], actor: cells[2] || '', note: cells[3] || '' });
    }
  }
  return events;
}

function scanReleases(devDir) {
  const dir = join(devDir, 'releases');
  if (!existsSync(dir)) return [];
  const releases = [];
  for (const f of readdirSync(dir).filter(f => f.endsWith('.md'))) {
    try {
      const content = readFileSync(join(dir, f), 'utf-8');
      releases.push({ id: f.replace('.md', ''), status: extractField(content, '状态') || '' });
    } catch { /* skip */ }
  }
  return releases;
}

function scanRisks(devDir) {
  const dir = join(devDir, 'risks');
  if (!existsSync(dir)) return [];
  const risks = [];
  for (const f of readdirSync(dir).filter(f => f.endsWith('.md'))) {
    try {
      const content = readFileSync(join(dir, f), 'utf-8');
      const severity = extractField(content, '严重度') || extractField(content, '等级') || '';
      const status = extractField(content, '状态') || '';
      risks.push({ id: f.replace('.md', ''), severity: severity.toLowerCase(), status: status.toLowerCase() });
    } catch { /* skip */ }
  }
  return risks;
}

function readIteration(devDir) {
  const p = join(devDir, 'iterations', 'current.md');
  if (!existsSync(p)) return null;
  try {
    const content = readFileSync(p, 'utf-8');
    const endMatch = content.match(/结束[日期]*[：:]\s*(\d{4}-\d{2}-\d{2})/);
    const rateMatch = content.match(/完成率[：:]\s*(\d+)%/) || content.match(/(\d+)\/(\d+)\s*(?:PF|产品功能)/);
    let completionRate = null;
    if (rateMatch) {
      completionRate = rateMatch[2] ? Math.round(parseInt(rateMatch[1]) / parseInt(rateMatch[2]) * 100) : parseInt(rateMatch[1]);
    }
    return {
      endDate: endMatch ? endMatch[1] : null,
      completionRate,
      exists: true,
    };
  } catch { return null; }
}

function getDashboardAge(devDir) {
  const p = join(devDir, 'metrics', 'dashboard.md');
  if (!existsSync(p)) return null;
  try {
    const stat = statSync(p);
    return Math.floor((Date.now() - stat.mtimeMs) / (1000 * 60 * 60 * 24)); // days
  } catch { return null; }
}

function readProjectMeta(devDir) {
  const p = join(devDir, 'project.md');
  const meta = { pfCount: 0, pfWithoutCr: 0, scopeExists: false, mosCheckboxes: { total: 0, checked: 0 } };
  if (!existsSync(p)) return meta;
  try {
    const content = readFileSync(p, 'utf-8');
    // Count PFs in tree view
    const pfMatches = content.matchAll(/PF-\d{3,}/g);
    const pfIds = new Set();
    for (const m of pfMatches) pfIds.add(m[0]);
    meta.pfCount = pfIds.size;

    // PFs without CRs: PF lines that don't have CR-xxx nearby
    const lines = content.split('\n');
    for (const line of lines) {
      const pfMatch = line.match(/PF-\d{3,}/);
      if (pfMatch && !line.includes('CR-')) {
        meta.pfWithoutCr++;
      }
    }

    // Scope section exists and is not a stub
    const scopeMatch = content.match(/^## 范围\s*\n([\s\S]*?)(?=\n## |\n$)/m);
    meta.scopeExists = scopeMatch ? !/(首次|填充|待定|（.*?）)/.test(scopeMatch[1].trim().split('\n')[0] || '') : false;

    // MoS checkboxes — only count list-item checkboxes (- [x] / - [ ])
    const mosSection = content.match(/成效指标[\s\S]*?(?=\n## |\n$)/);
    if (mosSection) {
      const mosLines = mosSection[0].split('\n');
      let checked = 0;
      let unchecked = 0;
      for (const line of mosLines) {
        const trimmed = line.trim();
        if (/^-\s+\[x\]/i.test(trimmed)) checked++;
        else if (/^-\s+\[ \]/.test(trimmed)) unchecked++;
      }
      meta.mosCheckboxes = { total: checked + unchecked, checked };
    }

    return meta;
  } catch { return meta; }
}

function readSyncMapping(devDir) {
  const p = join(devDir, 'integrations', 'sync-mapping.md');
  if (!existsSync(p)) return null;
  try {
    const stat = statSync(p);
    return { exists: true, ageHours: Math.floor((Date.now() - stat.mtimeMs) / (1000 * 60 * 60)) };
  } catch { return null; }
}

function scanEpics(devDir) {
  const dir = join(devDir, 'epics');
  if (!existsSync(dir)) return [];
  const epics = [];
  for (const f of readdirSync(dir).filter(f => f.endsWith('.md'))) {
    try {
      const content = readFileSync(join(dir, f), 'utf-8');
      const status = extractField(content, '状态') || '';
      const hasBrs = /BR-\d{3,}/.test(content);
      epics.push({ id: f.replace('.md', ''), status, hasBrs, title: extractTitle(content) });
    } catch { /* skip */ }
  }
  return epics;
}

function readOpportunities(devDir) {
  const p = join(devDir, 'opportunities.md');
  if (!existsSync(p)) return [];
  try {
    const content = readFileSync(p, 'utf-8');
    const evaluating = (content.match(/评估中/g) || []).length;
    return evaluating > 0 ? [{ count: evaluating }] : [];
  } catch { return []; }
}

function getProjectAge(devDir) {
  const p = join(devDir, 'state.md');
  if (!existsSync(p)) return null;
  try {
    const stat = statSync(p);
    return Math.floor((Date.now() - stat.birthtimeMs) / (1000 * 60 * 60 * 24)); // days
  } catch { return null; }
}

// ══════════════════════════════════════════════════════════════════════
// SIGNAL EVALUATION (24 signals)
// ══════════════════════════════════════════════════════════════════════

function evaluateSignals(data, devDir) {
  const triggered = [];
  const { crs, crSummary: cs, releases, risks, iteration, dashboardAge, projectMeta: pm, epics, opportunities, syncMapping, projectAge } = data;

  // S1: 审批阻塞
  if (cs.in_review > 0) {
    const reviewCrs = crs.filter(c => c.status === 'in_review');
    triggered.push({ id: 'S1', group: 'blocking', label: '审批阻塞', detail: `${cs.in_review} 个 CR 等待审批（${reviewCrs.map(c => c.id).join(', ')}）`, guide: '/pace-review' });
  }

  // S2: 高风险阻塞
  const highOpenRisks = risks.filter(r => r.severity === 'high' && (r.status === 'open' || r.status === ''));
  if (highOpenRisks.length > 0) {
    triggered.push({ id: 'S2', group: 'blocking', label: '高风险阻塞', detail: `${highOpenRisks.length} 个高级别风险未处理`, guide: '/pace-guard report' });
  }

  // S3: 继续开发
  if (cs.developing > 0) {
    const devCrs = crs.filter(c => c.status === 'developing');
    const top = devCrs[0];
    triggered.push({ id: 'S3', group: 'in_progress', label: '继续开发', detail: `继续 ${top.id}（${top.title}）`, guide: '/pace-dev' });
  }

  // S4: 恢复暂停（阻塞原因已解除时才触发）
  const pausedCrs = crs.filter(c => c.status === 'paused');
  if (pausedCrs.length > 0) {
    const resumable = pausedCrs.filter(cr => {
      if (!cr.blocked) return true; // No blocking reason recorded → consider resumable
      const blockerRef = cr.blocked.match(/CR-\d{3,}/)?.[0];
      if (!blockerRef) return true; // Non-CR blocking reason → can't determine programmatically, include
      const blocker = crs.find(c => c.id === blockerRef);
      return blocker && (blocker.status === 'merged' || blocker.status === 'released');
    });
    if (resumable.length > 0) {
      triggered.push({ id: 'S4', group: 'in_progress', label: '恢复暂停', detail: `${resumable.length} 个 CR 阻塞已解除（${resumable.map(c => c.id).join(', ')}）`, guide: '/pace-change resume' });
    }
  }

  // S5: Release 待验证
  const deployedReleases = releases.filter(r => r.status === 'deployed');
  if (deployedReleases.length > 0) {
    triggered.push({ id: 'S5', group: 'delivery', label: 'Release 待验证', detail: `${deployedReleases.map(r => r.id).join(', ')} 已部署待验证`, guide: '/pace-release verify' });
  }

  // S6: 风险积压
  const openNonHighRisks = risks.filter(r => r.severity !== 'high' && (r.status === 'open' || r.status === ''));
  if (openNonHighRisks.length > 3) {
    triggered.push({ id: 'S6', group: 'delivery', label: '风险积压', detail: `${openNonHighRisks.length} 个中低风险未处理`, guide: '/pace-guard report' });
  }

  // S7: 迭代时间紧迫
  if (iteration?.endDate && iteration.completionRate !== null) {
    const daysLeft = daysDiff(new Date(), new Date(iteration.endDate));
    if (daysLeft < 2 && iteration.completionRate < 50) {
      triggered.push({ id: 'S7', group: 'delivery', label: '迭代时间紧迫', detail: `距结束 ${daysLeft} 天，完成率 ${iteration.completionRate}%`, guide: '/pace-plan adjust' });
    }
  }

  // S8: 迭代接近完成
  if (iteration && iteration.completionRate != null && iteration.completionRate > 80) {
    triggered.push({ id: 'S8', group: 'delivery', label: '迭代接近完成', detail: `完成率 ${iteration.completionRate}%`, guide: '/pace-retro' });
  }

  // S9: 回顾提醒
  const hasMerged = crs.some(c => c.status === 'merged');
  if (dashboardAge !== null && dashboardAge > 7 && hasMerged) {
    triggered.push({ id: 'S9', group: 'strategic', label: '回顾提醒', detail: `Dashboard ${dashboardAge} 天未更新，有已完成工作待回顾`, guide: '/pace-retro' });
  }

  // S10: 缺陷占比高
  if (cs.total > 0) {
    const defectCount = crs.filter(c => c.type === 'defect').length;
    const defectRate = Math.round(defectCount / cs.total * 100);
    if (defectRate > 30) {
      triggered.push({ id: 'S10', group: 'strategic', label: '缺陷占比高', detail: `缺陷 CR 占比 ${defectRate}%（${defectCount}/${cs.total}）`, guide: '/pace-guard report' });
    }
  }

  // S11: 同步滞后（CR 状态变更未推送 > 24h）
  if (syncMapping) {
    // Find CRs with events more recent than sync-mapping last update
    const syncAge = syncMapping.ageHours;
    const unsyncedCrs = crs.filter(cr => {
      if (!cr.events || cr.events.length === 0) return false;
      const lastEvent = cr.events[cr.events.length - 1];
      if (!lastEvent.date) return false;
      const eventDate = new Date(lastEvent.date);
      if (isNaN(eventDate.getTime())) return false;
      const eventAgeHours = (Date.now() - eventDate.getTime()) / (1000 * 60 * 60);
      // Event happened after last sync, and sync is stale > 24h
      return eventAgeHours < syncAge && syncAge > 24;
    });
    if (unsyncedCrs.length > 0) {
      triggered.push({ id: 'S11', group: 'strategic', label: '同步滞后', detail: `${unsyncedCrs.length} 个 CR 状态变更未推送（sync-mapping ${syncAge}h 未更新）`, guide: '/pace-sync push' });
    } else if (syncAge > 24) {
      // Fallback: no event data but sync-mapping is stale
      triggered.push({ id: 'S11', group: 'strategic', label: '同步滞后', detail: `同步映射 ${syncAge}h 未更新`, guide: '/pace-sync push' });
    }
  }

  // S12: MoS 达成回顾
  if (pm.mosCheckboxes.total > 0) {
    const mosRate = Math.round(pm.mosCheckboxes.checked / pm.mosCheckboxes.total * 100);
    if (mosRate > 80) {
      triggered.push({ id: 'S12', group: 'strategic', label: 'MoS 达成回顾', detail: `成效指标达成率 ${mosRate}%`, guide: '/pace-retro' });
    }
  }

  // S13: 功能未开始
  if (pm.pfWithoutCr > 0) {
    triggered.push({ id: 'S13', group: 'growth', label: '功能未开始', detail: `${pm.pfWithoutCr} 个 PF 尚无对应 CR`, guide: '说"帮我实现 [PF 名]"' });
  }

  // S14: 规划新迭代
  if (!iteration?.exists) {
    const iterDir = join(devDir, 'iterations');
    const hasClosedIter = existsSync(iterDir) && readdirSync(iterDir).some(f => f !== 'current.md' && f.endsWith('.md'));
    if (hasClosedIter) {
      triggered.push({ id: 'S14', group: 'growth', label: '规划新迭代', detail: '上一迭代已结束，无活跃迭代', guide: '/pace-plan' });
    }
  }

  // S15: 全部完成
  if (cs.total > 0 && crs.every(c => c.status === 'merged' || c.status === 'released')) {
    triggered.push({ id: 'S15', group: 'growth', label: '全部完成', detail: `所有 ${cs.total} 个 CR 已完成`, guide: '自然语言' });
  }

  // S16: Epic 需分解
  const planningEpics = epics.filter(e => e.status.includes('规划中') && !e.hasBrs);
  if (planningEpics.length > 0) {
    triggered.push({ id: 'S16', group: 'growth', label: 'Epic 需分解', detail: `${planningEpics.map(e => e.id).join(', ')} 待分解`, guide: '/pace-biz decompose' });
  }

  // S17: 未评估机会
  if (opportunities.length > 0) {
    triggered.push({ id: 'S17', group: 'growth', label: '未评估机会', detail: `${opportunities[0].count} 个业务机会待评估`, guide: '/pace-biz epic' });
  }

  // S18: 功能树稀疏
  if (pm.pfCount < 3 && projectAge !== null && projectAge > 7) {
    triggered.push({ id: 'S18', group: 'growth', label: '功能树稀疏', detail: `仅 ${pm.pfCount} 个 PF，项目已创建 ${projectAge} 天`, guide: '/pace-biz discover' });
  }

  // S19: 范围未定义
  if (!pm.scopeExists) {
    triggered.push({ id: 'S19', group: 'growth', label: '范围未定义', detail: '项目范围 section 为桩或不存在', guide: '/pace-biz discover' });
  }

  // S21: 跨 CR 依赖阻塞（CR-B 非 merged/developing 超 3 天）
  for (const cr of crs) {
    if (cr.blocked) {
      const blockedBy = cr.blocked.match(/CR-\d{3,}/)?.[0];
      if (blockedBy) {
        const blocker = crs.find(c => c.id === blockedBy);
        if (blocker && blocker.status !== 'merged' && blocker.status !== 'released' && blocker.status !== 'developing') {
          // Check if blocker has been stagnant for > 3 days
          let stagnantDays = null;
          if (blocker.events && blocker.events.length > 0) {
            const lastEventDate = new Date(blocker.events[blocker.events.length - 1].date);
            if (!isNaN(lastEventDate.getTime())) {
              stagnantDays = Math.floor((Date.now() - lastEventDate.getTime()) / (1000 * 60 * 60 * 24));
            }
          }
          if (stagnantDays === null || stagnantDays > 3) {
            const daysInfo = stagnantDays !== null ? `（${stagnantDays} 天未推进）` : '';
            triggered.push({ id: 'S21', group: 'growth', label: '跨 CR 依赖阻塞', detail: `${cr.id} 被 ${blockedBy} 阻塞${daysInfo}`, guide: '/pace-dev' });
            break; // Only report first occurrence
          }
        }
      }
    }
  }

  // S22: 技术债积压
  if (cs.total > 0) {
    const techDebtCount = crs.filter(c => c.type === 'tech-debt').length;
    const techDebtRate = Math.round(techDebtCount / cs.total * 100);
    if (techDebtRate > 30 || techDebtCount > 5) {
      triggered.push({ id: 'S22', group: 'growth', label: '技术债积压', detail: `tech-debt CR ${techDebtCount} 个（${techDebtRate}%）`, guide: '/pace-plan adjust' });
    }
  }

  // S24: 首次循环引导
  if (cs.developing > 0 && cs.merged === 0 && cs.released === 0) {
    triggered.push({ id: 'S24', group: 'growth', label: '首次循环引导', detail: '第一个功能进行中，完成后 /pace-review 体验完整循环', guide: '自然语言' });
  }

  // S25: Gate 连续失败（从结构化事件类型提取）
  for (const cr of crs) {
    if (!cr.events || cr.events.length < 3) continue;
    const recentEvents = cr.events.slice(-5);
    const recentFails = recentEvents.filter(e => {
      const type = e.type || e.event || '';
      return type === 'gate1_fail' || type === 'gate2_fail';
    });
    if (recentFails.length >= 3) {
      triggered.push({ id: 'S25', group: 'blocking', label: 'Gate 连续失败', detail: `${cr.id} Gate 连续失败 ${recentFails.length} 次`, guide: '/pace-change modify 或检查验收条件' });
      break; // Only report first occurrence
    }
  }

  return triggered;
}

// ══════════════════════════════════════════════════════════════════════
// ROLE REORDERING
// ══════════════════════════════════════════════════════════════════════

function applyRoleReorder(triggered, role) {
  if (role === 'dev' || !ROLE_PROMOTIONS[role]) return triggered;

  const promotions = ROLE_PROMOTIONS[role].promote;
  const groupOrder = [...SIGNAL_GROUPS, 'idle'];

  // Mark promoted signals before sorting (avoid side effects inside comparator)
  for (const s of triggered) {
    if (promotions.includes(s.id) && s.group !== 'blocking') {
      s.role_promoted = true;
    }
  }

  return [...triggered].sort((a, b) => {
    let aGroupIdx = groupOrder.indexOf(a.group);
    let bGroupIdx = groupOrder.indexOf(b.group);

    // Blocking signals (S1, S2) are immune to role adjustment
    if (a.group === 'blocking') aGroupIdx = 0;
    if (b.group === 'blocking') bGroupIdx = 0;

    // Promote: move up by 1 group level
    if (a.role_promoted) aGroupIdx = Math.max(0, aGroupIdx - 1);
    if (b.role_promoted) bGroupIdx = Math.max(0, bGroupIdx - 1);

    return aGroupIdx - bGroupIdx;
  });
}

// ══════════════════════════════════════════════════════════════════════
// CACHE
// ══════════════════════════════════════════════════════════════════════

function readCache(devDir) {
  const cachePath = join(devDir, '.signal-cache');
  if (!existsSync(cachePath)) return null;
  try {
    const content = readFileSync(cachePath, 'utf-8');
    const cached = JSON.parse(content);
    const age = Date.now() - new Date(cached.timestamp).getTime();
    if (age < CACHE_TTL_MS) {
      cached.cached = true;
      return cached;
    }
    return null; // Expired
  } catch { return null; } // Format error → treat as expired
}

function writeCacheFile(devDir, output) {
  const cachePath = join(devDir, '.signal-cache');
  try {
    writeFileSync(cachePath, JSON.stringify(output, null, 2), 'utf-8');
  } catch { /* Cache write failure is non-critical */ }
}

// ══════════════════════════════════════════════════════════════════════
// UTILITIES
// ══════════════════════════════════════════════════════════════════════

function extractField(content, fieldName) {
  const regex = new RegExp(`^- \\*\\*${fieldName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\*\\*[：:]\\s*(.+)$`, 'm');
  const match = content.match(regex);
  return match ? match[1].trim() : null;
}

function extractTitle(content) {
  const match = content.match(/^# (.+)$/m);
  return match ? match[1].trim() : '';
}

function daysDiff(from, to) {
  return Math.ceil((to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24));
}

function getFlagValue(argList, flag) {
  const idx = argList.indexOf(flag);
  return idx >= 0 && idx + 1 < argList.length ? argList[idx + 1] : null;
}
