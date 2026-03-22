#!/usr/bin/env python3
"""Apply best description from eval loop to SKILL.md.

Subcommands:
  diff   - Show difference between current and best description
  apply  - Replace SKILL.md description with the best one

Delegates to core/skill_io.py for description read/write (single authority).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from ..core.results import DEVPACE_ROOT, EVAL_DATA_DIR, SKILLS_DIR
from ..core.skill_io import read_description, replace_description


def get_best_description(skill_name: str) -> str | None:
    """Read best description from eval loop results."""
    best_file = EVAL_DATA_DIR / skill_name / "results" / "loop" / "best-description.txt"
    if best_file.exists():
        return best_file.read_text().strip()

    results_file = EVAL_DATA_DIR / skill_name / "results" / "loop" / "results.json"
    if results_file.exists():
        data = json.loads(results_file.read_text())
        return data.get("best_description")

    return None


def apply_description(skill_dir: Path, new_desc: str) -> None:
    """Replace description in SKILL.md with backup and validation."""
    skill_md = skill_dir / "SKILL.md"

    # Backup
    backup = skill_md.with_suffix(".md.bak")
    shutil.copy2(skill_md, backup)

    original = replace_description(skill_md, new_desc)

    # Validate frontmatter integrity after replacement
    new_content = skill_md.read_text()
    lines = new_content.split("\n")
    valid = lines[0].strip() == "---"
    if valid:
        valid = any(line.strip() == "---" for line in lines[1:])

    if not valid:
        print("Error: broken frontmatter after replacement, restoring backup", file=sys.stderr)
        skill_md.write_text(original)
        backup.unlink()
        return

    backup.unlink()
    print(f"  description updated in {skill_md.relative_to(DEVPACE_ROOT)}")


def cmd_diff(args: argparse.Namespace) -> int:
    """Show diff between current and best description."""
    skill_name = args.skill
    skill_dir = SKILLS_DIR / skill_name

    current = read_description(skill_dir)
    best = get_best_description(skill_name)

    if best is None:
        print(f"No best description found for {skill_name}. Run eval-fix first.", file=sys.stderr)
        return 1

    print(f"--- current ({skill_name})")
    print(current)
    print()
    print(f"+++ best ({skill_name})")
    print(best)
    print()

    if current == best:
        print("  (identical)")
    else:
        print(f"  current: {len(current)} chars")
        print(f"  best:    {len(best)} chars")

    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    """Apply best description to SKILL.md."""
    skill_name = args.skill
    skill_dir = SKILLS_DIR / skill_name

    best = get_best_description(skill_name)
    if best is None:
        print(f"No best description found for {skill_name}. Run eval-fix first.", file=sys.stderr)
        return 1

    current = read_description(skill_dir)
    if current == best:
        print(f"  {skill_name}: description already matches best")
        return 0

    apply_description(skill_dir, best)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Apply eval results to SKILL.md")
    sub = parser.add_subparsers(dest="action", required=True)

    p_diff = sub.add_parser("diff", help="Show diff between current and best")
    p_diff.add_argument("--skill", "-s", required=True)

    p_apply = sub.add_parser("apply", help="Apply best description")
    p_apply.add_argument("--skill", "-s", required=True)

    args = parser.parse_args()
    if args.action == "diff":
        return cmd_diff(args)
    elif args.action == "apply":
        return cmd_apply(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
