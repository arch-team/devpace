#!/bin/bash
# Create historical git tags for past releases.
# This is a one-time script — delete after execution.
#
# Usage: bash scripts/create-historical-tags.sh

set -euo pipefail

echo "Creating historical tags for devpace releases..."
echo ""

create_tag() {
    local version="$1"
    local commit="$2"
    if git rev-parse "$version" >/dev/null 2>&1; then
        echo "  ⏭ $version already exists, skipping"
    else
        git tag -a "$version" "$commit" -m "Release $version"
        echo "  ✓ $version → $commit"
    fi
}

create_tag v0.1.0 4d65627
create_tag v0.9.0 0bcea9c
create_tag v0.9.1 e61a624
create_tag v1.0.0 dba9864
create_tag v1.1.0 2f06b77
create_tag v1.2.0 24b51dc
create_tag v1.3.0 a54a819

echo ""
echo "Historical tags created. v1.4.0 will be tagged after the release commit."
echo ""
echo "To push tags: git push origin --tags"
echo "To delete this script: rm scripts/create-historical-tags.sh"
