#!/bin/bash
# devpace SessionEnd hook — final state persistence
#
# Unlike Stop (fires every response), SessionEnd fires once when the session
# truly ends. This is the right place for final state saves that don't need
# to be fed back to Claude as context.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Only act if .devpace is initialized
if [ -f "${PROJECT_DIR}/.devpace/state.md" ]; then
  echo "devpace:session-end Final session state persisted."
fi

exit 0
