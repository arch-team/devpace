#!/bin/bash
# Bump version number across all project files and optionally commit + tag.
#
# Usage:
#   bash scripts/bump-version.sh <new-version>              # bump only
#   bash scripts/bump-version.sh <new-version> --commit     # bump + commit
#   bash scripts/bump-version.sh <new-version> --tag        # bump + commit + tag
#   bash scripts/bump-version.sh <new-version> --release    # bump + commit + tag + push + trigger CI release
#
# Example: bash scripts/bump-version.sh 1.5.1 --release

set -euo pipefail

NEW_VERSION="${1:?Usage: bump-version.sh <new-version> [--commit|--tag|--release]}"
ACTION="${2:-}"

# Strip leading 'v' if present
NEW_VERSION="${NEW_VERSION#v}"

# Validate semver format
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Error: Version must be in semver format (e.g., 1.5.1)" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TODAY=$(date +%Y-%m-%d)

echo "Bumping version to $NEW_VERSION..."
echo ""

# --- Step 1: Update version in all files ---

# 1a. plugin.json — version field
PLUGIN_JSON="$PROJECT_DIR/.claude-plugin/plugin.json"
if [ -f "$PLUGIN_JSON" ]; then
    python3 -c "
import json, sys
with open('$PLUGIN_JSON', 'r') as f:
    data = json.load(f)
data['version'] = '$NEW_VERSION'
with open('$PLUGIN_JSON', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
    echo "  ✓ plugin.json (version)"
fi

# 1b. marketplace.json — version + ref fields
MARKETPLACE_JSON="$PROJECT_DIR/.claude-plugin/marketplace.json"
if [ -f "$MARKETPLACE_JSON" ]; then
    python3 -c "
import json
with open('$MARKETPLACE_JSON', 'r') as f:
    data = json.load(f)
for plugin in data.get('plugins', []):
    plugin['version'] = '$NEW_VERSION'
    if 'source' in plugin:
        plugin['source']['ref'] = 'v$NEW_VERSION'
with open('$MARKETPLACE_JSON', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
    echo "  ✓ marketplace.json (version + ref)"
fi

# 1c. README.md badge
README="$PROJECT_DIR/README.md"
if [ -f "$README" ]; then
    sed -i.bak "s/version-[0-9]*\.[0-9]*\.[0-9]*/version-$NEW_VERSION/" "$README"
    rm -f "$README.bak"
    echo "  ✓ README.md (badge)"
fi

# 1d. README_zh.md badge
README_ZH="$PROJECT_DIR/README_zh.md"
if [ -f "$README_ZH" ]; then
    sed -i.bak "s/version-[0-9]*\.[0-9]*\.[0-9]*/version-$NEW_VERSION/" "$README_ZH"
    rm -f "$README_ZH.bak"
    echo "  ✓ README_zh.md (badge)"
fi

# --- Step 2: Insert CHANGELOG.md placeholder ---

CHANGELOG="$PROJECT_DIR/CHANGELOG.md"
if [ -f "$CHANGELOG" ]; then
    # Check if version already exists
    if grep -q "## \[$NEW_VERSION\]" "$CHANGELOG"; then
        echo "  ⊘ CHANGELOG.md (v$NEW_VERSION already exists)"
    else
        # Insert new version section after ## [Unreleased] and add to Version Overview table
        python3 -c "
import re

with open('$CHANGELOG', 'r') as f:
    content = f.read()

# Insert version entry after ## [Unreleased]
new_section = '''## [$NEW_VERSION] - $TODAY

<!-- TODO: Add changelog content before release -->

### Changed

- Version bump to $NEW_VERSION
'''
content = content.replace(
    '## [Unreleased]\n',
    '## [Unreleased]\n\n' + new_section + '\n'
)

# Add to Version Overview table (after header row)
anchor = '$NEW_VERSION'.replace('.', '')
table_row = '| [$NEW_VERSION](#' + anchor + '---$TODAY) | $TODAY | <!-- TODO: highlights --> |'
# Insert after the first table row (which is the separator |---|---|---|)
lines = content.split('\n')
inserted = False
for i, line in enumerate(lines):
    if line.startswith('|------') and not inserted:
        # Find if we're in the Version Overview table
        if i > 0 and 'Version' in lines[i-1]:
            lines.insert(i + 1, table_row)
            inserted = True
            break
content = '\n'.join(lines)

with open('$CHANGELOG', 'w') as f:
    f.write(content)
"
        echo "  ✓ CHANGELOG.md (placeholder inserted — fill before releasing)"
    fi
fi

# --- Step 3: Summary ---

echo ""
echo "━━━ Version $NEW_VERSION bumped across all files ━━━"
echo ""

# Verify consistency
PLUGIN_V=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])")
MARKET_V=$(python3 -c "import json; print(json.load(open('$MARKETPLACE_JSON'))['plugins'][0]['version'])")
MARKET_REF=$(python3 -c "import json; print(json.load(open('$MARKETPLACE_JSON'))['plugins'][0]['source']['ref'])")

echo "Verification:"
echo "  plugin.json:      $PLUGIN_V"
echo "  marketplace.json: $MARKET_V (ref: $MARKET_REF)"

if [ "$PLUGIN_V" != "$NEW_VERSION" ] || [ "$MARKET_V" != "$NEW_VERSION" ] || [ "$MARKET_REF" != "v$NEW_VERSION" ]; then
    echo ""
    echo "⚠ Version mismatch detected!" >&2
    exit 1
fi
echo "  ✓ All versions consistent"
echo ""

# --- Step 4: Optional git operations ---

if [ "$ACTION" = "--commit" ] || [ "$ACTION" = "--tag" ] || [ "$ACTION" = "--release" ]; then
    cd "$PROJECT_DIR"
    git add .claude-plugin/plugin.json .claude-plugin/marketplace.json README.md README_zh.md CHANGELOG.md
    git commit -m "chore(*): bump version to v$NEW_VERSION"
    echo "  ✓ Committed"
fi

if [ "$ACTION" = "--tag" ] || [ "$ACTION" = "--release" ]; then
    cd "$PROJECT_DIR"
    git tag "v$NEW_VERSION"
    echo "  ✓ Tagged v$NEW_VERSION"
fi

if [ "$ACTION" = "--release" ]; then
    cd "$PROJECT_DIR"
    git push
    git push origin "v$NEW_VERSION"
    echo "  ✓ Pushed (CI release workflow will trigger)"
    echo ""
    echo "Monitor: gh run watch"
fi

# --- Step 5: Next steps ---

if [ -z "$ACTION" ]; then
    echo "Next steps:"
    echo "  1. Edit CHANGELOG.md — fill the v$NEW_VERSION section"
    echo "  2. bash scripts/bump-version.sh $NEW_VERSION --release"
    echo "     (or manually: git commit → git tag v$NEW_VERSION → git push --tags)"
fi
