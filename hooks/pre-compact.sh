#!/bin/bash
# devpace PreCompact hook — remind to save state before context compression
#
# Purpose: Before Claude auto-compacts (context ~95%), output a reminder
# to ensure state.md and CR files reflect the latest progress.
# This preserves cross-session continuity (OBJ-1).
#
# Advisory hook (exit 0), not blocking.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="${PROJECT_DIR}/.devpace/state.md"

if [ -f "$STATE_FILE" ]; then
  echo "devpace:pre-compact Context compression imminent. Ensure state.md and any active CR files reflect current progress before compacting. Key items: 1) Update state.md '进行中' and '下一步' 2) Git commit any uncommitted changes 3) Update CR event table if in advance mode."
fi

exit 0
