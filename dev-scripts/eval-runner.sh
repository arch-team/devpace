#!/bin/bash
# Routes skill-creator eval commands through the best available runtime:
#   1. skill-creator CLI (if installed as standalone)
#   2. Direct Python call to skill-creator scripts (no permission issues)
#   3. claude -p wrapper (Claude Code CLI forwards to /skill-creator plugin)
#   4. Error with guidance
#
# Usage: bash dev-scripts/eval-runner.sh eval-trigger --skill skills/pace-dev --evals tests/evaluation/pace-dev/trigger-evals.json

set -euo pipefail

# Discover skill-creator Python scripts directory from plugin cache.
# Returns the parent directory of scripts/ (i.e. the skill-creator skill root)
# so that `python3 -m scripts.run_eval` works with correct module resolution.
find_sc_scripts_root() {
    local sc_base="$HOME/.claude/plugins/cache/claude-plugins-official/skill-creator"
    [ -d "$sc_base" ] || return 1
    # Pick the first (usually only) hash directory
    local hash_dir
    hash_dir=$(ls "$sc_base" | head -1)
    [ -n "$hash_dir" ] || return 1
    local scripts_root="$sc_base/$hash_dir/skills/skill-creator"
    [ -f "$scripts_root/scripts/run_eval.py" ] && echo "$scripts_root" && return 0
    return 1
}

# Map eval-runner subcommands to direct Python script calls.
# Returns 0 if handled, 1 if the subcommand has no Python equivalent.
try_direct_python() {
    local subcmd="$1"; shift
    local sc_root
    sc_root=$(find_sc_scripts_root) || return 1

    case "$subcmd" in
        eval-trigger)
            # Parse --skill and --evals from remaining args
            local skill_path="" evals_path=""
            while [ $# -gt 0 ]; do
                case "$1" in
                    --skill)  skill_path="$2"; shift 2 ;;
                    --evals)  evals_path="$2"; shift 2 ;;
                    *)        shift ;;
                esac
            done
            if [ -z "$skill_path" ] || [ -z "$evals_path" ]; then
                echo "Error: eval-trigger requires --skill and --evals" >&2
                return 1
            fi
            echo "  (using direct Python call to skill-creator scripts)"
            # Resolve to absolute paths before cd (skip if already absolute)
            local project_root
            project_root="$(cd "$(dirname "$0")/.." && pwd)"
            [[ "$skill_path" != /* ]] && skill_path="$project_root/$skill_path"
            [[ "$evals_path" != /* ]] && evals_path="$project_root/$evals_path"
            cd "$sc_root"
            exec python3 -m scripts.run_eval \
                --eval-set "$evals_path" \
                --skill-path "$skill_path" \
                --verbose \
                --num-workers 10 \
                --timeout 30 \
                --runs-per-query 1
            ;;
        *)
            # No Python equivalent for this subcommand
            return 1
            ;;
    esac
}

# --- Main routing ---

if command -v skill-creator >/dev/null 2>&1; then
    exec skill-creator "$@"
fi

# Priority 2: Direct Python call (faster, avoids claude -p permission issues)
subcmd="${1:-}"
if [ -n "$subcmd" ] && try_direct_python "$@"; then
    exit 0
fi

# Priority 3: claude -p wrapper
if command -v claude >/dev/null 2>&1; then
    echo "  (using claude CLI wrapper — each eval is an API call, may be slow)"
    args=""
    for arg in "$@"; do args="$args \"$arg\""; done
    exec claude -p "/skill-creator$args"
fi

echo "Error: neither skill-creator, skill-creator Python scripts, nor claude CLI found."
echo ""
echo "Options:"
echo "  1. Install Claude Code: https://docs.anthropic.com/en/docs/claude-code"
echo "  2. Run inside a Claude Code session: /skill-creator $*"
exit 1
