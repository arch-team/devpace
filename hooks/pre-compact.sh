#!/bin/bash
# devpace PreCompact hook — save state snapshot and inject recovery context
#
# Purpose: Before Claude auto-compacts (context ~95%), output structured
# recovery context that will survive compression, ensuring continuity.
# Enhances cross-session continuity (OBJ-1) and long-session stability (UX4).
#
# Advisory hook (exit 0), not blocking.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="${PROJECT_DIR}/.devpace/state.md"
DEVPACE_DIR="${PROJECT_DIR}/.devpace"

if [ ! -f "$STATE_FILE" ]; then
  exit 0
fi

# Extract key context for post-compact recovery
echo "devpace:pre-compact === DEVPACE RECOVERY CONTEXT (preserve after compact) ==="

# 1. Iron Rules reminder
echo "devpace:pre-compact IR-1: state.md 是唯一会话锚点 | IR-2: 先读后写 | IR-3: 质量门不可跳过 | IR-4: 变更走流程 | IR-5: 产出可追溯"

# 2. Current state summary (extract from state.md)
if [ -f "$STATE_FILE" ]; then
  # Extract 进行中 and 下一步 from state.md
  CURRENT=$(grep -m1 "进行中\|developing\|verifying\|in_review" "$STATE_FILE" 2>/dev/null || echo "")
  NEXT_STEP=$(grep -m1 "下一步" "$STATE_FILE" 2>/dev/null || echo "")
  if [ -n "$CURRENT" ]; then
    echo "devpace:pre-compact Current: $CURRENT"
  fi
  if [ -n "$NEXT_STEP" ]; then
    echo "devpace:pre-compact Next: $NEXT_STEP"
  fi
fi

# 3. Active CR detection
if [ -d "${DEVPACE_DIR}/backlog" ]; then
  ACTIVE_CRS=$(grep -rl "developing\|verifying\|in_review" "${DEVPACE_DIR}/backlog/" 2>/dev/null | head -3)
  if [ -n "$ACTIVE_CRS" ]; then
    for cr in $ACTIVE_CRS; do
      CR_NAME=$(basename "$cr" .md)
      CR_STATUS=$(grep -m1 "状态" "$cr" 2>/dev/null | head -1)
      echo "devpace:pre-compact Active CR: $CR_NAME — $CR_STATUS"
    done
  fi
fi

echo "devpace:pre-compact Action: 1) Read .devpace/state.md to restore full context 2) Resume active CR 3) Git commit any uncommitted changes"
echo "devpace:pre-compact === END RECOVERY CONTEXT ==="

exit 0
