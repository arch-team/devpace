#!/usr/bin/env node
/**
 * Metrics computation engine for devpace.
 *
 * Computes 8 core indicators + forecast from .devpace/ data.
 *
 * Usage:
 *   node scripts/compute-metrics.mjs <devpace-dir>                    # all metrics
 *   node scripts/compute-metrics.mjs <devpace-dir> --scope iteration  # iteration only
 *   node scripts/compute-metrics.mjs <devpace-dir> --scope forecast   # forecast only
 *
 * Output: JSON { metrics: {...}, forecast?: {...} }
 *
 * Dependencies: Node.js only. Reuses extract-cr-metadata.mjs.
 */

import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';

// ── CLI ──────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const devpaceDir = args[0];
if (!devpaceDir) {
  console.error('Usage: node compute-metrics.mjs <devpace-dir> [--scope all|iteration|forecast]');
  process.exit(1);
}
const scope = getFlagValue(args, '--scope') || 'all';

// ── Data collection ──────────────────────────────────────────────────
const crs = loadCrs(devpaceDir);
const iteration = readIteration(devpaceDir);

const output = { metrics: {} };

if (scope === 'all' || scope === 'iteration') {
  output.metrics = computeMetrics(crs, iteration, devpaceDir);
}

if (scope === 'all' || scope === 'forecast') {
  output.forecast = computeForecast(crs, iteration, devpaceDir, output.metrics);
}

console.log(JSON.stringify(output, null, 2));

// ══════════════════════════════════════════════════════════════════════
// CORE METRICS (8 indicators)
// ══════════════════════════════════════════════════════════════════════

function computeMetrics(crs, iter, devDir) {
  const m = {};

  // 1. 迭代速度
  if (iter) {
    const planned = iter.plannedPf;
    const actual = iter.actualPf;
    m.iteration_velocity = planned > 0
      ? { value: round(actual / planned, 2), actual, planned, unit: 'ratio' }
      : { value: null, reason: 'no planned PF data' };
  }

  // 2. 平均 CR 周期
  const mergedCrs = crs.filter(c => c.status === 'merged' || c.status === 'released');
  const cycles = mergedCrs.map(c => crCycleDays(c)).filter(d => d !== null);
  m.avg_cr_cycle = cycles.length > 0
    ? { value: round(avg(cycles), 1), count: cycles.length, unit: 'days' }
    : { value: null, reason: 'no merged CRs with date data' };

  // 3. Gate 首次通过率
  const gateStats = computeGateStats(crs);
  m.gate_first_pass_rate = gateStats.total > 0
    ? { value: round(gateStats.passFirst / gateStats.total * 100, 1), pass: gateStats.passFirst, total: gateStats.total, unit: '%' }
    : { value: null, reason: 'no gate data' };

  // 4. 缺陷逃逸率
  const mergedFeatures = crs.filter(c => c.type === 'feature' && (c.status === 'merged' || c.status === 'released'));
  const defectCrs = crs.filter(c => c.type === 'defect');
  m.defect_escape_rate = mergedFeatures.length > 0
    ? { value: round(defectCrs.length / mergedFeatures.length * 100, 1), defects: defectCrs.length, features: mergedFeatures.length, unit: '%' }
    : { value: null, reason: 'no merged feature CRs' };

  // 5. 变更频率
  if (iter?.changeCount != null && iter.daysElapsed > 0) {
    m.change_frequency = { value: round(iter.changeCount / iter.daysElapsed, 2), changes: iter.changeCount, days: iter.daysElapsed, unit: 'per day' };
  }

  // 6. 缺陷修复周期
  const defectMerged = defectCrs.filter(c => c.status === 'merged' || c.status === 'released');
  const defectCycles = defectMerged.map(c => crCycleDays(c)).filter(d => d !== null);
  m.defect_fix_cycle = defectCycles.length > 0
    ? { value: round(avg(defectCycles), 1), count: defectCycles.length, unit: 'days' }
    : { value: null, reason: 'no merged defect CRs' };

  // 7. 人类打回率
  const reviewStats = computeReviewStats(crs);
  m.human_rejection_rate = reviewStats.totalReviews > 0
    ? { value: round(reviewStats.rejections / reviewStats.totalReviews * 100, 1), rejections: reviewStats.rejections, reviews: reviewStats.totalReviews, unit: '%' }
    : { value: null, reason: 'no review data' };

  // 8. 缺陷严重度分布
  if (defectCrs.length > 0) {
    const dist = { critical: 0, major: 0, minor: 0, trivial: 0, unknown: 0 };
    for (const c of defectCrs) {
      const sev = c.severity?.toLowerCase() || 'unknown';
      if (sev in dist) dist[sev]++;
      else dist.unknown++;
    }
    m.defect_severity_distribution = dist;
  }

  return m;
}

// ══════════════════════════════════════════════════════════════════════
// FORECAST
// ══════════════════════════════════════════════════════════════════════

function computeForecast(crs, iter, devDir, metrics) {
  if (!iter?.completionRate || !iter?.timeConsumptionRate) {
    return { probability: null, grade: null, reason: 'no iteration progress data' };
  }

  const base = iter.timeConsumptionRate > 0
    ? iter.completionRate / iter.timeConsumptionRate
    : iter.completionRate;

  // Adjustment factors
  let adjustment = 0;
  const factors = [];

  // Factor 1: CR stall — avg stay > historical mean × 1.5
  const developingCrs = crs.filter(c => c.status === 'developing');
  const avgCycle = metrics?.avg_cr_cycle?.value;
  if (developingCrs.length > 0 && avgCycle) {
    const avgStay = avg(developingCrs.map(c => crAgeDays(c)).filter(d => d !== null));
    if (avgStay > avgCycle * 1.5) {
      adjustment -= 0.15;
      factors.push(`CR 滞留（平均 ${round(avgStay, 1)} 天 > 历史均值 ${avgCycle} × 1.5）→ -15%`);
    }
  }

  // Factor 2: High risk
  const risksDir = join(devDir, 'risks');
  let highRisks = 0;
  if (existsSync(risksDir)) {
    for (const f of readdirSync(risksDir).filter(f => f.endsWith('.md'))) {
      try {
        const content = readFileSync(join(risksDir, f), 'utf-8');
        if (/(?:严重度|等级)[：:]\s*High/i.test(content) && !/状态[：:]\s*(?:resolved|mitigated)/i.test(content)) {
          highRisks++;
        }
      } catch { /* skip */ }
    }
  }
  if (highRisks > 0) {
    adjustment -= 0.20;
    factors.push(`High 风险未解决（${highRisks} 个）→ -20%`);
  }

  // Factor 3: Change frequency > 2x historical
  if (metrics?.change_frequency?.value > 0.5) {
    adjustment -= 0.10;
    factors.push(`变更频率偏高（${metrics.change_frequency.value}/天）→ -10%`);
  }

  // Factor 4: Gate pass rate > 80%
  if (metrics?.gate_first_pass_rate?.value > 80) {
    adjustment += 0.05;
    factors.push(`Gate 通过率 ${metrics.gate_first_pass_rate.value}% → +5%`);
  }

  // Calculate final probability
  const raw = base * (1 + adjustment);
  const probability = Math.round(clamp(raw * 100, 5, 95));

  let grade, emoji;
  if (probability >= 80) { grade = '高信心'; emoji = '🟢'; }
  else if (probability >= 50) { grade = '中等风险'; emoji = '🟡'; }
  else { grade = '高风险'; emoji = '🔴'; }

  // Bottleneck detection
  const bottlenecks = [];
  for (const cr of developingCrs) {
    const age = crAgeDays(cr);
    if (age !== null && avgCycle && age > avgCycle * 2) {
      bottlenecks.push({ type: 'CR 滞留', detail: `${cr.id} 开发 ${round(age, 0)} 天（历史均值 ${avgCycle} 天）` });
    }
  }

  return {
    probability,
    grade,
    emoji,
    base: round(base * 100, 1),
    adjustment: round(adjustment * 100, 1),
    factors,
    bottlenecks,
    completion_rate: round(iter.completionRate * 100, 1),
    time_consumption_rate: round(iter.timeConsumptionRate * 100, 1),
  };
}

// ══════════════════════════════════════════════════════════════════════
// DATA LOADERS
// ══════════════════════════════════════════════════════════════════════

function loadCrs(devDir) {
  try {
    const scriptDir = new URL('.', import.meta.url).pathname;
    const output = execFileSync('node', [join(scriptDir, 'extract-cr-metadata.mjs'), devDir], { encoding: 'utf-8', timeout: 10000 });
    return JSON.parse(output);
  } catch { return []; }
}

function readIteration(devDir) {
  const p = join(devDir, 'iterations', 'current.md');
  if (!existsSync(p)) return null;
  try {
    const content = readFileSync(p, 'utf-8');
    const startMatch = content.match(/开始[日期]*\*{0,2}[：:]\s*(\d{4}-\d{2}-\d{2})/);
    const endMatch = content.match(/结束[日期]*\*{0,2}[：:]\s*(\d{4}-\d{2}-\d{2})/);
    const plannedMatch = content.match(/计划\s*\*{0,2}(?:PF|产品功能)\*{0,2}[：:]\s*(\d+)/);
    const actualMatch = content.match(/(?:已完成|实际)\s*\*{0,2}(?:PF|产品功能)\*{0,2}[：:]\s*(\d+)/);
    const rateMatch = content.match(/(\d+)\/(\d+)\s*(?:PF|产品功能)/);
    const changeLines = (content.match(/\|\s*\d{2,4}-\d{2}/g) || []).length;

    const startDate = startMatch ? new Date(startMatch[1]) : null;
    const endDate = endMatch ? new Date(endMatch[1]) : null;
    const now = new Date();

    const totalDays = startDate && endDate ? Math.max(1, daysDiff(startDate, endDate)) : null;
    const daysElapsed = startDate ? Math.max(0, daysDiff(startDate, now)) : null;

    let plannedPf = plannedMatch ? parseInt(plannedMatch[1]) : (rateMatch ? parseInt(rateMatch[2]) : 0);
    let actualPf = actualMatch ? parseInt(actualMatch[1]) : (rateMatch ? parseInt(rateMatch[1]) : 0);

    return {
      exists: true,
      plannedPf,
      actualPf,
      completionRate: plannedPf > 0 ? actualPf / plannedPf : 0,
      timeConsumptionRate: totalDays && daysElapsed != null ? daysElapsed / totalDays : 0,
      daysElapsed: daysElapsed || 0,
      totalDays: totalDays || 0,
      changeCount: changeLines,
    };
  } catch { return null; }
}

// ══════════════════════════════════════════════════════════════════════
// CR ANALYTICS
// ══════════════════════════════════════════════════════════════════════

function crCycleDays(cr) {
  if (!cr.events || cr.events.length < 2) return null;
  const created = cr.events[0]?.date;
  const lastEvent = cr.events[cr.events.length - 1]?.date;
  if (!created || !lastEvent) return null;
  return daysBetweenShortDates(created, lastEvent);
}

function crAgeDays(cr) {
  if (!cr.events || cr.events.length === 0) return null;
  const created = cr.events[0]?.date;
  if (!created) return null;
  const createdDate = parseShortDate(created);
  if (!createdDate) return null;
  return daysDiff(createdDate, new Date());
}

function computeGateStats(crs) {
  let total = 0, passFirst = 0;
  for (const cr of crs) {
    if (!cr.events) continue;
    let gateAttempts = 0;
    let gatePassed = false;
    for (const evt of cr.events) {
      if (evt.note?.includes('gate1-passed') || evt.note?.includes('gate2-passed')) {
        gatePassed = true;
        total++;
        if (gateAttempts === 0) passFirst++;
        break;
      }
      if (evt.event?.includes('→developing') && evt.event?.includes('in_review')) {
        gateAttempts++; // rejection = failed gate
      }
    }
  }
  return { total, passFirst };
}

function computeReviewStats(crs) {
  let totalReviews = 0, rejections = 0;
  for (const cr of crs) {
    if (!cr.events) continue;
    for (const evt of cr.events) {
      if (evt.event?.includes('in_review')) totalReviews++;
      if (evt.event?.includes('in_review→developing') || evt.event?.includes('in_review → developing')) {
        rejections++;
      }
    }
  }
  return { totalReviews, rejections };
}

// ══════════════════════════════════════════════════════════════════════
// UTILITIES
// ══════════════════════════════════════════════════════════════════════

function parseShortDate(dateStr) {
  if (!dateStr) return null;
  // Handle MM-DD format (assume current year)
  const shortMatch = dateStr.match(/^(\d{2})-(\d{2})$/);
  if (shortMatch) {
    const year = new Date().getFullYear();
    return new Date(year, parseInt(shortMatch[1]) - 1, parseInt(shortMatch[2]));
  }
  // Handle YYYY-MM-DD
  const fullMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (fullMatch) return new Date(fullMatch[1], parseInt(fullMatch[2]) - 1, parseInt(fullMatch[3]));
  return null;
}

function daysBetweenShortDates(d1, d2) {
  const date1 = parseShortDate(d1);
  const date2 = parseShortDate(d2);
  if (!date1 || !date2) return null;
  return Math.abs(daysDiff(date1, date2));
}

function daysDiff(from, to) {
  return Math.ceil((to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24));
}

function avg(arr) { return arr.length > 0 ? arr.reduce((s, v) => s + v, 0) / arr.length : 0; }
function round(v, d) { const f = Math.pow(10, d); return Math.round(v * f) / f; }
function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

function getFlagValue(argList, flag) {
  const idx = argList.indexOf(flag);
  return idx >= 0 && idx + 1 < argList.length ? argList[idx + 1] : null;
}
