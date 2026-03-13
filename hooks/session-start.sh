#!/bin/bash
# devpace SessionStart hook — reads .devpace/state.md for Claude context

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="${PROJECT_DIR}/.devpace/state.md"

if [ -f "$STATE_FILE" ]; then
  echo "devpace:session-start Active project detected. Read .devpace/state.md for details."

  # Check for pending learn extraction
  LEARN_PENDING="${PROJECT_DIR}/.devpace/.learn-pending"
  if [ -f "$LEARN_PENDING" ]; then
    PENDING_COUNT=$(wc -l < "$LEARN_PENDING" | tr -d ' ')
    echo "devpace:learn-pending ${PENDING_COUNT} 个 CR 已 merged 但经验尚未提取。建议执行 /pace-learn 提取经验。"
  fi
else
  echo "devpace:session-start No active devpace project."
fi

exit 0
