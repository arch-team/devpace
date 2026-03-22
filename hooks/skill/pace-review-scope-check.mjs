#!/usr/bin/env node
/**
 * pace-review scope check — fast command Hook replacing LLM prompt Hook
 *
 * Replaces the slow prompt-type Hook (~15s LLM per call) with a fast
 * programmatic check (~5ms) for write scope validation during /pace-review.
 *
 * Background: The global PreToolUse hook (pre-tool-use.mjs) already enforces
 * Gate 3 unconditionally — it blocks ALL automated state changes to "approved"
 * regardless of context. Hooks run in parallel and "most restrictive wins",
 * so a skill-level prompt Hook cannot override the global block.
 *
 * This command Hook replaces the (effectively dead) prompt Hook with a fast
 * path that validates writes are within pace-review's expected scope:
 *   - CR files: status updates (except approved, handled by global hook),
 *     event table entries, review notes
 *   - Non-CR .devpace/ files: always allowed
 *   - Non-.devpace/ files: advisory warning (pace-review shouldn't write outside)
 *
 * Exit codes:
 *   0 = allow
 *   2 = block (unexpected write target during review)
 */

import {
  readStdinJson, getProjectDir, extractFilePath,
  isDevpaceFile
} from '../lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();
const filePath = extractFilePath(input);

if (!filePath) {
  process.exit(0);
}

// .devpace/ files are expected during review (CR updates, state changes, etc.)
// Gate 3 (approved blocking) is handled by the global pre-tool-use.mjs hook
if (isDevpaceFile(filePath)) {
  process.exit(0);
}

// Non-.devpace/ files: advisory warning — pace-review shouldn't typically
// modify source files, but don't block (review might fix minor issues)
console.log(
  `devpace:review-scope-info /pace-review 通常仅修改 .devpace/ 文件，当前写入目标：${filePath}。ACTION: 确认此写入是否为 review 必要修复；若非必要则跳过该文件修改。`
);
process.exit(0);
