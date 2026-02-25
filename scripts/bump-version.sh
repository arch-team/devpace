#!/bin/bash
# Bump version number across all project files.
# Usage: bash scripts/bump-version.sh <new-version>
# Example: bash scripts/bump-version.sh 1.5.0

set -euo pipefail

NEW_VERSION="${1:?Usage: bump-version.sh <new-version>}"

# Strip leading 'v' if present
NEW_VERSION="${NEW_VERSION#v}"

# Validate semver format
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Error: Version must be in semver format (e.g., 1.5.0)" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Bumping version to $NEW_VERSION..."

# 1. plugin.json
PLUGIN_JSON="$PROJECT_DIR/.claude-plugin/plugin.json"
if [ -f "$PLUGIN_JSON" ]; then
    sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$NEW_VERSION\"/" "$PLUGIN_JSON"
    rm -f "$PLUGIN_JSON.bak"
    echo "  ✓ plugin.json"
fi

# 2. marketplace.json
MARKETPLACE_JSON="$PROJECT_DIR/.claude-plugin/marketplace.json"
if [ -f "$MARKETPLACE_JSON" ]; then
    sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$NEW_VERSION\"/" "$MARKETPLACE_JSON"
    rm -f "$MARKETPLACE_JSON.bak"
    echo "  ✓ marketplace.json"
fi

# 3. README.md badge
README="$PROJECT_DIR/README.md"
if [ -f "$README" ]; then
    sed -i.bak "s/version-[0-9]*\.[0-9]*\.[0-9]*/version-$NEW_VERSION/" "$README"
    rm -f "$README.bak"
    echo "  ✓ README.md"
fi

# 4. README_zh.md badge
README_ZH="$PROJECT_DIR/README_zh.md"
if [ -f "$README_ZH" ]; then
    sed -i.bak "s/version-[0-9]*\.[0-9]*\.[0-9]*/version-$NEW_VERSION/" "$README_ZH"
    rm -f "$README_ZH.bak"
    echo "  ✓ README_zh.md"
fi

echo ""
echo "Version bumped to $NEW_VERSION"
echo "Next steps:"
echo "  1. Update CHANGELOG.md with new version section"
echo "  2. git add -A && git commit -m \"chore: bump version to $NEW_VERSION\""
echo "  3. git tag v$NEW_VERSION"
