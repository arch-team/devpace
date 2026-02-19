#!/bin/bash
# devpace PreToolUse hook — quality gate awareness for CR state transitions
#
# Purpose: When Claude attempts to write to CR files with state transitions,
# remind about quality gate requirements. This is an advisory hook (exit 0),
# not a blocking gate — the actual gate enforcement is in devpace-rules.md §2.
#
# Why advisory, not blocking:
#   Gate 1/2 are enforced by devpace-rules.md §2 (Claude self-checks).
#   This hook adds a safety net: if Claude is about to advance a CR state
#   without mentioning quality checks, the hook output reminds it.

INPUT=$(cat 2>/dev/null || true)
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
BACKLOG_DIR="${PROJECT_DIR}/.devpace/backlog"

# Only act if .devpace exists and has backlog
if [ ! -d "$BACKLOG_DIR" ]; then
  exit 0
fi

# Extract tool name from input
TOOL_NAME=$(echo "$INPUT" | grep -o '"tool_name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null)

# Only check Write/Edit operations on CR files
case "$TOOL_NAME" in
  Write|Edit)
    ;;
  *)
    exit 0
    ;;
esac

# Extract file path from input
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null)

# Only check writes to CR files
if ! echo "$FILE_PATH" | grep -q '\.devpace/backlog/CR-' 2>/dev/null; then
  exit 0
fi

# Check if the CR file exists and has a state transition hint
if [ -f "$FILE_PATH" ]; then
  CURRENT_STATE=$(grep -m1 '^状态:' "$FILE_PATH" 2>/dev/null | sed 's/状态:[[:space:]]*//')

  case "$CURRENT_STATE" in
    developing)
      echo "devpace:gate-reminder CR is in 'developing'. Gate 1 (code quality: lint+test+typecheck) must pass before advancing to 'verifying'."
      ;;
    verifying)
      echo "devpace:gate-reminder CR is in 'verifying'. Gate 2 (integration test + intent consistency) must pass before advancing to 'in_review'."
      ;;
    in_review)
      echo "devpace:gate-reminder CR is in 'in_review'. Gate 3 requires human approval. Do not advance without explicit user approval."
      ;;
  esac
fi

exit 0
