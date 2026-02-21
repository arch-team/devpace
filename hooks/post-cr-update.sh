#!/bin/bash
# devpace PostToolUse hook — detect CR merged state and trigger knowledge pipeline
#
# Purpose: After a Write/Edit to a CR file, check if the CR transitioned to 'merged'.
# If so, output a reminder for Claude to trigger the post-merge pipeline:
# knowledge extraction (pace-learn) + incremental metrics update.
#
# This is an advisory hook (exit 0), not blocking.

INPUT=$(cat 2>/dev/null || true)
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
BACKLOG_DIR="${PROJECT_DIR}/.devpace/backlog"

# Only act if .devpace exists and has backlog
if [ ! -d "$BACKLOG_DIR" ]; then
  exit 0
fi

# Extract file path from tool input
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null)

# Only check writes to CR files
if ! echo "$FILE_PATH" | grep -q '\.devpace/backlog/CR-' 2>/dev/null; then
  exit 0
fi

# Check if CR is now in 'merged' state
if [ -f "$FILE_PATH" ]; then
  CURRENT_STATE=$(grep -m1 '^\- \*\*状态\*\*' "$FILE_PATH" 2>/dev/null | sed 's/.*\*\*状态\*\*[：:][[:space:]]*//')

  if [ "$CURRENT_STATE" = "merged" ]; then
    CR_NAME=$(basename "$FILE_PATH" .md)
    echo "devpace:post-merge ${CR_NAME} merged. Execute post-merge pipeline: 1) Run pace-learn for knowledge extraction 2) Update dashboard.md metrics incrementally 3) Check PF completion for release note 4) Update state.md and iterations/current.md"
  fi
fi

exit 0
