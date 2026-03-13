#!/bin/bash
# test_plugin_loading.sh — Verify devpace plugin loads correctly in Claude CLI
#
# Exit codes:
#   0  = all tests passed
#   1  = test failure
#   77 = skipped (claude CLI not available)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEVPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILURES=0

# ── Pre-check: claude CLI available? ──────────────────────────────────
if ! command -v claude &>/dev/null; then
    echo -e "${YELLOW}SKIP: claude CLI not found in PATH${NC}"
    exit 77
fi

echo "=== Plugin Loading Integration Test ==="
echo "devpace root: $DEVPACE_ROOT"
echo ""

# ── TC-PL-01: Plugin loads without errors ─────────────────────────────
echo -n "TC-PL-01: Plugin loads without errors... "

# Use claude with --print and a minimal prompt to check plugin loading
LOAD_OUTPUT=$(claude --plugin-dir "$DEVPACE_ROOT" --print "exit" 2>&1 || true)

if echo "$LOAD_OUTPUT" | grep -qi "error.*plugin\|failed.*load\|cannot.*find"; then
    echo -e "${RED}FAIL${NC}"
    echo "  Plugin loading errors detected:"
    echo "$LOAD_OUTPUT" | grep -i "error\|failed\|cannot" | head -5
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}PASS${NC}"
fi

# ── TC-PL-02: All 19 skills discovered ────────────────────────────────
echo -n "TC-PL-02: All 19 skills discovered... "

EXPECTED_SKILLS=(
    "pace-biz"
    "pace-change"
    "pace-dev"
    "pace-feedback"
    "pace-guard"
    "pace-init"
    "pace-learn"
    "pace-next"
    "pace-plan"
    "pace-pulse"
    "pace-release"
    "pace-retro"
    "pace-review"
    "pace-role"
    "pace-status"
    "pace-sync"
    "pace-test"
    "pace-theory"
    "pace-trace"
)

# Check that skill directories with SKILL.md exist
MISSING_SKILLS=()
for skill in "${EXPECTED_SKILLS[@]}"; do
    if [ ! -f "$DEVPACE_ROOT/skills/$skill/SKILL.md" ]; then
        MISSING_SKILLS+=("$skill")
    fi
done

if [ ${#MISSING_SKILLS[@]} -eq 0 ]; then
    echo -e "${GREEN}PASS${NC} (19/19 skills have SKILL.md)"
else
    echo -e "${RED}FAIL${NC}"
    echo "  Missing skills: ${MISSING_SKILLS[*]}"
    FAILURES=$((FAILURES + 1))
fi

# ── Summary ───────────────────────────────────────────────────────────
echo ""
echo "=== Results ==="
if [ "$FAILURES" -eq 0 ]; then
    echo -e "${GREEN}All integration tests passed ✓${NC}"
    exit 0
else
    echo -e "${RED}${FAILURES} test(s) failed ✗${NC}"
    exit 1
fi
