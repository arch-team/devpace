#!/bin/bash
# Routes skill-creator eval commands through the best available runtime:
#   1. skill-creator CLI (if installed as standalone)
#   2. claude -p wrapper (Claude Code CLI forwards to /skill-creator plugin)
#   3. Error with guidance
#
# Usage: bash dev-scripts/eval-runner.sh eval-trigger --skill skills/pace-dev --evals tests/evaluation/pace-dev/trigger-evals.json

set -euo pipefail

if command -v skill-creator >/dev/null 2>&1; then
    exec skill-creator "$@"
elif command -v claude >/dev/null 2>&1; then
    echo "  (using claude CLI wrapper — each eval is an API call, may be slow)"
    args=""
    for arg in "$@"; do args="$args \"$arg\""; done
    exec claude -p "/skill-creator$args"
else
    echo "Error: neither skill-creator nor claude CLI found."
    echo ""
    echo "Options:"
    echo "  1. Install Claude Code: https://docs.anthropic.com/en/docs/claude-code"
    echo "  2. Run inside a Claude Code session: /skill-creator $*"
    exit 1
fi
