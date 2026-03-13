#!/bin/bash
# devpace SessionEnd hook — final state persistence
#
# Unlike Stop (fires every response), SessionEnd fires once when the session
# truly ends. This is the right place for final state saves that don't need
# to be fed back to Claude as context.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Only act if .devpace is initialized
if [ -f "${PROJECT_DIR}/.devpace/state.md" ]; then
  # Check for L/XL active CRs that need snapshot refresh
  if [ -d "${PROJECT_DIR}/.devpace/backlog" ]; then
    for cr_file in "${PROJECT_DIR}"/.devpace/backlog/CR-*.md; do
      [ ! -f "$cr_file" ] && continue
      state=$(grep -m1 '^- \*\*状态\*\*' "$cr_file" | sed 's/.*[：:] *//')
      complexity=$(grep -m1 '^- \*\*复杂度\*\*' "$cr_file" | sed 's/.*[：:] *//')
      if [[ "$state" =~ ^(developing|verifying)$ ]] && [[ "$complexity" =~ ^(L|XL)$ ]]; then
        echo "devpace:session-end 提醒: $(basename "$cr_file" .md) 是 ${complexity} 级活跃 CR，建议刷新执行快照的恢复建议。"
      fi
    done
  fi
  echo "devpace:session-end Final session state persisted."
fi

exit 0
