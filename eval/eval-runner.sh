#!/bin/bash
# Routes behavioral eval commands through skill-creator.
#
# The shim (eval/shim.py) has been replaced by the modular eval package.
# Trigger/loop/regress/baseline are now handled by: python3 -m eval <subcommand>
#
# This script is retained ONLY for behavioral eval routing (evals.json).
#
# Usage:
#   bash eval/eval-runner.sh eval --skill skills/pace-dev --evals tests/evaluation/pace-dev/evals.json

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
    return 1
}

subcmd="${1:-}"

case "$subcmd" in
    eval|eval-behavior)
        shift
        local_skill_path="" evals_path=""
        while [ $# -gt 0 ]; do
            case "$1" in
                --skill)  local_skill_path="$2"; shift 2 ;;
                --evals)  evals_path="$2"; shift 2 ;;
                *)        shift ;;
            esac
        done
        if [ -z "$local_skill_path" ] || [ -z "$evals_path" ]; then
            echo "Error: eval requires --skill and --evals" >&2
            exit 1
        fi
        sc_root=$(find_sc_scripts_root) || {
            echo "Error: skill-creator scripts not found. Behavioral eval requires skill-creator plugin." >&2
            echo "  Install via: claude /install skill-creator" >&2
            exit 1
        }
        [[ "$local_skill_path" != /* ]] && local_skill_path="$PROJECT_ROOT/$local_skill_path"
        [[ "$evals_path" != /* ]] && evals_path="$PROJECT_ROOT/$evals_path"
        echo "  (using skill-creator for behavioral eval)"
        PYTHONPATH="$sc_root:${PYTHONPATH:-}" exec python3 -m scripts.run_eval \
            --eval-set "$evals_path" \
            --skill-path "$local_skill_path" \
            --verbose \
            --num-workers 10 \
            --timeout 90 \
            --runs-per-query 1
        ;;
    eval-trigger*|eval-loop|regress|baseline|changed)
        # Redirect to new modular eval package
        echo "  Note: '$subcmd' is now handled by: python3 -m eval" >&2
        echo "  Redirecting..." >&2
        exec python3 -m eval "$@"
        ;;
    *)
        echo "Usage: bash eval/eval-runner.sh eval --skill <path> --evals <path>"
        echo ""
        echo "For trigger/loop/regress/baseline, use:"
        echo "  python3 -m eval trigger --skill <name> [--runs N]"
        echo "  python3 -m eval loop    --skill <name> --model <id>"
        echo "  python3 -m eval regress"
        echo "  python3 -m eval baseline save|diff --skill <name>"
        echo "  python3 -m eval changed [--base origin/main]"
        exit 1
        ;;
esac
