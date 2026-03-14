#!/usr/bin/env node
/**
 * devpace UserPromptSubmit hook — detect change management intent in user input
 *
 * Purpose: Scan user prompt for change management trigger words.
 * If detected, remind Claude to follow the change management workflow (§9).
 *
 * This is an advisory hook (exit 0), not blocking.
 */

import { existsSync } from 'node:fs';
import { readStdinJson, getProjectDir } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();

// Only act if .devpace is initialized
if (!existsSync(`${projectDir}/.devpace/state.md`)) {
  process.exit(0);
}

// Extract user prompt content
// Input structure may be { content: "..." } or nested
const userPrompt = input?.content ?? '';

// Change management trigger words
// Synced with skills/pace-change/SKILL.md description (authority source)
// Categories: add / pause / resume / reprioritize / modify + English variants
// Technical context words — if the prompt is about code/git operations, skip change detection
const techContextPattern = /注释|缩进|格式化?|配置文件|代码风格|git\s|stash|commit|branch|merge|rebase|checkout/;

const triggerPattern = new RegExp([
  // --- add ---
  '加一个', '加需求', '新增需求', '插入', '还需要', '补一个', '追加',
  // --- pause ---
  '不做了', '先不搞', '砍掉', '搁置', '放一放', '暂停', '停掉',
  '先放着', '不要这个功能了', '延后',
  // --- resume ---
  '恢复之前', '重新开始', '捡回来', '继续之前',
  // --- reprioritize ---
  '优先级', '先做这个', '提前', '排到前面', '优先', '调个顺序',
  // --- modify ---
  '改一下', '改需求', '范围变了', '调整范围', '验收条件',
  '改个需求', '需求变了', '条件改了',
  // --- English semantic variants ---
  '\\badd\\b', '\\bpause\\b', '\\bresume\\b', '\\bdrop\\b',
  '\\bdefer\\b', '\\bshelve\\b', '\\breprioritize\\b',
].join('|'));

if (triggerPattern.test(userPrompt) && !techContextPattern.test(userPrompt)) {
  console.log('devpace:change-detected Change intent detected in user prompt. Follow devpace-rules.md §9 change management workflow: classify → impact analysis → confirmation → execute.');
}

process.exit(0);
