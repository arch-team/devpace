#!/usr/bin/env node
/**
 * devpace PostToolUse hook — detect CR state transitions and trigger pipelines
 *
 * Purpose: After a Write/Edit to a CR file, detect state transitions and output
 * appropriate ACTION signals:
 * - merged → post-merge pipeline (§11)
 * - created → auto-link/create suggestion (sync-procedures-auto.md)
 * - gate failures / rejections → learning triggers
 *
 * This is an advisory hook (exit 0), not blocking.
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { basename, dirname } from 'node:path';
import { readStdinJson, getProjectDir, extractFilePath, isCrFile, readCrState, getLastEvent, CR_STATES } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const backlogDir = `${projectDir}/.devpace/backlog`;

// Only act if .devpace exists and has backlog
if (!existsSync(backlogDir)) {
  process.exit(0);
}

// Extract file path from tool input
const filePath = extractFilePath(input);

// Only check writes to CR files
if (!isCrFile(filePath, backlogDir)) {
  process.exit(0);
}

// Check CR state and recent events for learning triggers
if (existsSync(filePath)) {
  let content;
  try {
    content = readFileSync(filePath, 'utf-8');
  } catch {
    process.exit(0);
  }

  const currentState = readCrState(filePath, content);
  const crName = basename(filePath, '.md');

  if (currentState === CR_STATES.MERGED) {
    console.log(`devpace:post-merge ${crName} 已 merge。ACTION: 执行 post-merge 管线——1) 更新 state.md 移除该 CR 的进行中标记 2) 若 CR 有外部关联则执行 /pace-sync push ${crName} 关闭 Issue 3) 执行 /pace-learn merge ${crName} 萃取经验。`);
  }

  // Auto-link/create trigger — new CR created with sync configured
  // Uses a marker file to avoid re-suggesting on subsequent edits to the same CR
  if (currentState === CR_STATES.CREATED) {
    const syncMappingPath = `${projectDir}/.devpace/integrations/sync-mapping.md`;
    const hasExternalLink = /\*\*外部关联\*\*[：:]\s*\[/.test(content);
    const autoSuggestMark = `${projectDir}/.devpace/.sync-auto-suggested-${crName}`;
    if (existsSync(syncMappingPath) && !hasExternalLink && !existsSync(autoSuggestMark)) {
      try {
        mkdirSync(dirname(autoSuggestMark), { recursive: true });
        writeFileSync(autoSuggestMark, new Date().toISOString(), 'utf-8');
      } catch { /* non-critical */ }
      console.log(`devpace:auto-sync ${crName} 已创建且同步已配置。ACTION: 加载 sync-procedures-auto.md，为 ${crName} 执行自动关联/创建外部 Issue 流程（§2 auto-link 优先，无匹配则 §3 auto-create）。`);
    }
  }

  // Gate fail learning trigger — gate_fail is a valuable learning opportunity
  const recentEvent = getLastEvent(filePath, content);
  if (recentEvent && (recentEvent.type === 'gate1_fail' || recentEvent.type === 'gate2_fail')) {
    const gateNum = recentEvent.type === 'gate1_fail' ? '1' : '2';
    console.log(`devpace:learn-trigger ${crName} Gate ${gateNum} 未通过。ACTION: 先修复 Gate 失败原因并重试；Gate 通过后执行 /pace-learn gate-failure ${crName} 萃取教训。`);
  }

  // Rejected learning trigger — human rejection reveals understanding gaps
  if (recentEvent && recentEvent.type === 'rejected') {
    console.log(`devpace:learn-trigger ${crName} 被人类驳回。ACTION: 查看 CR 事件表最新 rejected 记录确认驳回原因，修复后重新提交 review；完成后执行 /pace-learn rejection ${crName} 分析认知差距。`);
  }

  // Gate result sync trigger — push Gate results to external platform
  if (recentEvent && /^gate[123]_(pass|fail)$/.test(recentEvent.type)) {
    const syncMappingPath = `${projectDir}/.devpace/integrations/sync-mapping.md`;
    const hasExternalLink = /\*\*外部关联\*\*[：:]\s*\[/.test(content);
    if (existsSync(syncMappingPath) && hasExternalLink) {
      const gateMatch = recentEvent.type.match(/^gate(\d)_(pass|fail)$/);
      const gateNum = gateMatch[1];
      const gateResult = gateMatch[2] === 'pass' ? '通过' : '未通过';
      console.log(`devpace:gate-sync ${crName} Gate ${gateNum} ${gateResult}。ACTION: 加载 sync-procedures-push-advanced.md §2，为 ${crName} 推送 Gate ${gateNum} 结果到外部平台（Comment + 标签）。`);
    }
  }
}

process.exit(0);
