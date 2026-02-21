#!/bin/bash
# devpace UserPromptSubmit hook — detect change management intent in user input
#
# Purpose: Scan user prompt for change management trigger words.
# If detected, remind Claude to follow the change management workflow (§9).
#
# This is an advisory hook (exit 0), not blocking.

INPUT=$(cat 2>/dev/null || true)
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Only act if .devpace is initialized
if [ ! -f "${PROJECT_DIR}/.devpace/state.md" ]; then
  exit 0
fi

# Extract user prompt content
USER_PROMPT=$(echo "$INPUT" | grep -o '"content"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"content"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null)

# Change management trigger words (Chinese)
# "不做了" "先不搞" "加一个" "改一下" "优先级" "延后" "提前" "砍掉" "插入" "新增需求" "先做这个" "恢复"
if echo "$USER_PROMPT" | grep -q '不做了\|先不搞\|加一个\|改一下\|优先级\|延后\|提前\|砍掉\|插入\|新增需求\|先做这个\|恢复之前' 2>/dev/null; then
  echo "devpace:change-detected Change intent detected in user prompt. Follow devpace-rules.md §9 change management workflow: classify → impact analysis → confirmation → execute."
fi

exit 0
