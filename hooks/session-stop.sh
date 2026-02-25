#!/bin/bash
# devpace Stop hook — light session-end reminder
#
# Stop fires every response → output is fed back to Claude as context.
# This hook reminds Claude to save state when ending a session.
# Final state persistence is handled by session-end.sh (SessionEnd hook).
#
# stop_hook_active guard prevents infinite re-triggering.

INPUT=$(cat 2>/dev/null || true)

# Prevent infinite loop on re-entry
if echo "$INPUT" | grep -q '"stop_hook_active".*true' 2>/dev/null; then
  exit 0
fi

# Only remind on end_turn (not tool_use or other stop reasons)
STOP_REASON=$(echo "$INPUT" | grep -o '"stop_reason"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"stop_reason"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null)

if [ "$STOP_REASON" = "end_turn" ]; then
  echo "devpace:stop If ending session, update .devpace/state.md and output summary."
fi

exit 0
