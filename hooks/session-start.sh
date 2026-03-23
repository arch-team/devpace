#!/bin/bash
# devpace SessionStart hook — reads .devpace/state.md for Claude context

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="${PROJECT_DIR}/.devpace/state.md"

if [ -f "$STATE_FILE" ]; then
  echo "devpace:session-start Active project detected. ACTION: Read .devpace/state.md to restore project context and identify active CRs; then resume in-progress work."
else
  echo "devpace:session-start No active devpace project."
fi

exit 0
