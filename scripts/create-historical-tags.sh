#!/bin/bash
# Create historical git tags for past releases.
# This is a one-time script — delete after execution.
#
# Usage: bash scripts/create-historical-tags.sh

set -euo pipefail

echo "Creating historical tags for devpace releases..."
echo ""

declare -A TAGS=(
    ["v0.1.0"]="4d65627"
    ["v0.9.0"]="0bcea9c"
    ["v0.9.1"]="e61a624"
    ["v1.0.0"]="dba9864"
    ["v1.1.0"]="2f06b77"
    ["v1.2.0"]="24b51dc"
    ["v1.3.0"]="a54a819"
)

# Process in version order
for version in v0.1.0 v0.9.0 v0.9.1 v1.0.0 v1.1.0 v1.2.0 v1.3.0; do
    commit="${TAGS[$version]}"
    if git rev-parse "$version" >/dev/null 2>&1; then
        echo "  ⏭ $version already exists, skipping"
    else
        git tag -a "$version" "$commit" -m "Release $version"
        echo "  ✓ $version → $commit"
    fi
done

echo ""
echo "Historical tags created. v1.4.0 will be tagged after the release commit."
echo ""
echo "To push tags: git push origin --tags"
echo "To delete this script: rm scripts/create-historical-tags.sh"
