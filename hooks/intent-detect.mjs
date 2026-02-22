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

// Change management trigger words (Chinese)
const triggerPattern = /不做了|先不搞|加一个|改一下|优先级|延后|提前|砍掉|插入|新增需求|先做这个|恢复之前/;

if (triggerPattern.test(userPrompt)) {
  console.log('devpace:change-detected Change intent detected in user prompt. Follow devpace-rules.md §9 change management workflow: classify → impact analysis → confirmation → execute.');
}

process.exit(0);
