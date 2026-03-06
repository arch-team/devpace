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

# ── Tier 1.3: Markdown lint (markdownlint-cli2) ──────────────────────────
echo -e "${YELLOW}[Tier 1.3] Markdown lint (product layer)${NC}"

if command -v markdownlint-cli2 &>/dev/null || command -v npx &>/dev/null; then
    LINT_CMD="markdownlint-cli2"
    if ! command -v markdownlint-cli2 &>/dev/null; then
        LINT_CMD="npx markdownlint-cli2"
    fi
    if $LINT_CMD "rules/**/*.md" "skills/**/*.md" "knowledge/**/*.md" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Markdown lint passed${NC}"
    else
        echo -e "${RED}  ✗ Markdown lint failed${NC}"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${YELLOW}  ⚠ markdownlint-cli2 not found — install with: npm install -g markdownlint-cli2${NC}"
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

# ── Tier 1.7: Token budget check ─────────────────────────────────────
echo -e "${YELLOW}[Tier 1.7] Token budget check${NC}"

RULES_FILE="$PROJECT_ROOT/rules/devpace-rules.md"
RULES_LINES=$(wc -l < "$RULES_FILE" 2>/dev/null | tr -d ' ' || echo "0")
TOKEN_WARNING=600

if [ "$RULES_LINES" -gt "$TOKEN_WARNING" ]; then
    echo -e "${YELLOW}  ⚠ rules/devpace-rules.md: ${RULES_LINES} lines (>${TOKEN_WARNING}) — consider splitting conditional sections${NC}"
else
    echo -e "${GREEN}  ✓ rules/devpace-rules.md: ${RULES_LINES} lines (≤${TOKEN_WARNING})${NC}"
fi

TOTAL_PRODUCT=$(cat "$PROJECT_ROOT"/rules/*.md "$PROJECT_ROOT"/skills/*/*.md "$PROJECT_ROOT"/knowledge/*.md "$PROJECT_ROOT"/knowledge/_schema/*.md 2>/dev/null | wc -l | tr -d ' ')
echo -e "  ℹ Product layer total: ${TOTAL_PRODUCT} lines"

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

# ── Tier 3: Eval coverage check ───────────────────────────────────────
echo -e "${YELLOW}[Tier 3] Eval coverage check${NC}"

SKILLS_DIR="$PROJECT_ROOT/skills"
EVAL_DIR="$PROJECT_ROOT/tests/evaluation"
EVAL_TOTAL=0
EVAL_COVERED=0
EVAL_MISSING=""

for skill_dir in "$SKILLS_DIR"/pace-*/; do
    skill=$(basename "$skill_dir")
    # Skip workspace directories
    case "$skill" in *-workspace) continue;; esac
    EVAL_TOTAL=$((EVAL_TOTAL + 1))
    if [ -f "$EVAL_DIR/$skill/evals.json" ] && [ -f "$EVAL_DIR/$skill/trigger-evals.json" ]; then
        EVAL_COVERED=$((EVAL_COVERED + 1))
    else
        EVAL_MISSING="$EVAL_MISSING $skill"
    fi
done

if [ "$EVAL_TOTAL" -gt 0 ]; then
    echo -e "  ℹ Eval coverage: ${EVAL_COVERED}/${EVAL_TOTAL} Skills"
    if [ -n "$EVAL_MISSING" ]; then
        echo -e "${YELLOW}  ⚠ Missing evals:${EVAL_MISSING}${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ No skills found${NC}"
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
