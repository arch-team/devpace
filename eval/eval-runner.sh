#!/bin/bash
# Routes skill-creator eval commands through the shim or direct Python call.
#
# The shim (eval/shim.py) handles:
#   - name: injection into SKILL.md frontmatter
#   - clean project root for correct command discovery
#   - plugin disable/enable to avoid skill name competition
#   - increased timeout for MCP server initialization
#
# Usage:
#   bash eval/eval-runner.sh eval-trigger --skill skills/pace-dev --evals tests/evaluation/pace-dev/trigger-evals.json
#   bash eval/eval-runner.sh eval-trigger-shim --skill pace-dev [--runs N] [--timeout T]
#   bash eval/eval-runner.sh eval-loop --skill pace-dev --model MODEL [--iterations N]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Discover skill-creator Python scripts directory from plugin cache.
find_sc_scripts_root() {
    local sc_base="$HOME/.claude/plugins/cache/claude-plugins-official/skill-creator"
    [ -d "$sc_base" ] || return 1
    local hash_dir
    hash_dir=$(ls "$sc_base" | head -1)
    [ -n "$hash_dir" ] || return 1
    local scripts_root="$sc_base/$hash_dir/skills/skill-creator"
    [ -f "$scripts_root/scripts/run_eval.py" ] && echo "$scripts_root" && return 0
    # Vendor fallback
    [ -f "$SCRIPT_DIR/vendor/skill-creator/scripts/run_eval.py" ] && echo "$SCRIPT_DIR/vendor/skill-creator" && return 0
    return 1
}

# Route eval-trigger through PYTHONPATH (no cd) with name injection via shim
try_direct_python() {
    local subcmd="$1"; shift
    local sc_root
    sc_root=$(find_sc_scripts_root) || return 1

    case "$subcmd" in
        eval-trigger)
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
            echo "  (using direct Python call via PYTHONPATH)"
            # Resolve to absolute paths
            [[ "$skill_path" != /* ]] && skill_path="$PROJECT_ROOT/$skill_path"
            [[ "$evals_path" != /* ]] && evals_path="$PROJECT_ROOT/$evals_path"
            # Run from project root with PYTHONPATH (not cd to sc_root)
            PYTHONPATH="$sc_root:${PYTHONPATH:-}" exec python3 -m scripts.run_eval \
                --eval-set "$evals_path" \
                --skill-path "$skill_path" \
                --verbose \
                --num-workers 10 \
                --timeout 90 \
                --runs-per-query 1
            ;;
        eval-trigger-shim)
            # Route through shim.py for full fix (name injection + plugin disable)
            local skill_name="" extra_args=()
            while [ $# -gt 0 ]; do
                case "$1" in
                    --skill)  skill_name="$2"; shift 2 ;;
                    *)        extra_args+=("$1"); shift ;;
                esac
            done
            if [ -z "$skill_name" ]; then
                echo "Error: eval-trigger-shim requires --skill <name>" >&2
                return 1
            fi
            exec python3 "$SCRIPT_DIR/shim.py" trigger --skill "$skill_name" "${extra_args[@]}"
            ;;
        eval-loop)
            local skill_name="" extra_args=()
            while [ $# -gt 0 ]; do
                case "$1" in
                    --skill)  skill_name="$2"; shift 2 ;;
                    *)        extra_args+=("$1"); shift ;;
                esac
            done
            if [ -z "$skill_name" ]; then
                echo "Error: eval-loop requires --skill <name>" >&2
                return 1
            fi
            exec python3 "$SCRIPT_DIR/shim.py" loop --skill "$skill_name" "${extra_args[@]}"
            ;;
        *)
            return 1
            ;;
    esac
}

# --- Main routing ---

if command -v skill-creator >/dev/null 2>&1; then
    exec skill-creator "$@"
fi

subcmd="${1:-}"
if [ -n "$subcmd" ] && try_direct_python "$@"; then
    exit 0
fi

if command -v claude >/dev/null 2>&1; then
    echo "  (using claude CLI wrapper)"
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
