#!/bin/bash
# devpace Stop hook — light reminder to save session state
#
# Design decision: Uses Stop (not SessionEnd) intentionally.
# - Stop fires every response → output is fed back to Claude as context
# - SessionEnd fires once at session end → cannot inject context (session is over)
# - devpace needs Claude to SEE the reminder and act on it, so Stop is correct
# - stop_hook_active guard below prevents infinite re-triggering

INPUT=$(cat 2>/dev/null || true)

# Prevent infinite loop on re-entry
if echo "$INPUT" | grep -q '"stop_hook_active".*true' 2>/dev/null; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Only remind if .devpace is initialized AND stop_reason is end_turn
STOP_REASON=$(echo "$INPUT" | grep -o '"stop_reason"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"stop_reason"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null)

if [ "$STOP_REASON" = "end_turn" ] && [ -f "${PROJECT_DIR}/.devpace/state.md" ]; then
  echo "devpace:stop If ending session, update .devpace/state.md and output summary."
fi

exit 0
