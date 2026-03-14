#!/usr/bin/env python3
"""Extract a specific version's changelog section from CHANGELOG.md."""

import re
import sys
from pathlib import Path


def extract_changelog(changelog_path: str, version: str) -> str:
    """Extract changelog content for a specific version.

    Args:
        changelog_path: Path to CHANGELOG.md
        version: Version string (e.g., "1.4.0", without "v" prefix)

    Returns:
        The changelog content for that version, or empty string if not found.
    """
    content = Path(changelog_path).read_text(encoding="utf-8")

    # Match ## [version] header and capture until next ## [version] or end
    pattern = rf"## \[{re.escape(version)}\][^\n]*\n(.*?)(?=\n## \[|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return ""

    return match.group(1).strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: extract-changelog.py <version> [changelog-path]", file=sys.stderr)
        print("  version: e.g., 1.4.0 (without 'v' prefix)", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1].lstrip("v")
    changelog_path = sys.argv[2] if len(sys.argv) > 2 else "CHANGELOG.md"

    if not Path(changelog_path).exists():
        print(f"Error: {changelog_path} not found", file=sys.stderr)
        sys.exit(1)

    result = extract_changelog(changelog_path, version)
    if not result:
        print(f"Error: Version {version} not found in {changelog_path}", file=sys.stderr)
        sys.exit(1)

    print(result)


if __name__ == "__main__":
    main()
