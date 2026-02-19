#!/bin/bash
# devpace Stop hook — light reminder to save session state

INPUT=$(cat 2>/dev/null || true)

# Prevent infinite loop on re-entry
if echo "$INPUT" | grep -q '"stop_hook_active".*true' 2>/dev/null; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

if [ -f "${PROJECT_DIR}/.devpace/state.md" ]; then
  echo "devpace:stop If ending session, update .devpace/state.md and output summary."
fi

exit 0
