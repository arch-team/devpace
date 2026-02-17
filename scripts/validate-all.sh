#!/bin/bash
# validate-all.sh — Run all devpace static validations
#
# Usage: bash scripts/validate-all.sh
# Exit:  0 = all pass, 1 = failures detected

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo " devpace validation suite"
echo "========================================="
echo ""

FAILURES=0

# ── Tier 1: Static tests (pytest) ──────────────────────────────────────
echo -e "${YELLOW}[Tier 1] Static validation (pytest)${NC}"

if command -v pytest &>/dev/null; then
    if pytest "$PROJECT_ROOT/tests/static/" -v --tb=short; then
        echo -e "${GREEN}  ✓ Static tests passed${NC}"
    else
        echo -e "${RED}  ✗ Static tests failed${NC}"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${YELLOW}  ⚠ pytest not found — install with: pip install pytest pyyaml${NC}"
    FAILURES=$((FAILURES + 1))
fi

echo ""

# ── Tier 1.5: Layer separation quick-check (redundant with pytest) ─────
echo -e "${YELLOW}[Tier 1.5] Layer separation grep check${NC}"

LAYER_VIOLATIONS=$(grep -r "docs/\|\.claude/" "$PROJECT_ROOT/rules/" "$PROJECT_ROOT/skills/" "$PROJECT_ROOT/knowledge/" 2>/dev/null || true)
if [ -z "$LAYER_VIOLATIONS" ]; then
    echo -e "${GREEN}  ✓ No product→dev layer references${NC}"
else
    echo -e "${RED}  ✗ Product layer references dev layer:${NC}"
    echo "$LAYER_VIOLATIONS"
    FAILURES=$((FAILURES + 1))
fi

echo ""

# ── Tier 2: Integration test (optional — requires claude CLI) ──────────
echo -e "${YELLOW}[Tier 2] Integration test (plugin loading)${NC}"

INTEGRATION_SCRIPT="$PROJECT_ROOT/tests/integration/test_plugin_loading.sh"
if [ -f "$INTEGRATION_SCRIPT" ]; then
    if bash "$INTEGRATION_SCRIPT"; then
        echo -e "${GREEN}  ✓ Plugin loading test passed${NC}"
    else
        EXIT_CODE=$?
        if [ "$EXIT_CODE" -eq 77 ]; then
            echo -e "${YELLOW}  ⚠ Skipped (claude CLI not available)${NC}"
        else
            echo -e "${RED}  ✗ Plugin loading test failed${NC}"
            FAILURES=$((FAILURES + 1))
        fi
    fi
else
    echo -e "${YELLOW}  ⚠ Integration test script not found${NC}"
fi

echo ""

# ── Summary ────────────────────────────────────────────────────────────
echo "========================================="
if [ "$FAILURES" -eq 0 ]; then
    echo -e "${GREEN}All validations passed ✓${NC}"
    exit 0
else
    echo -e "${RED}${FAILURES} validation(s) failed ✗${NC}"
    exit 1
fi
