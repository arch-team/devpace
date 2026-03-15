#!/usr/bin/env python3
"""Apply best description from eval loop to SKILL.md.

Subcommands:
  diff   - Show difference between current and best description
  apply  - Replace SKILL.md description with the best one
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

DEVPACE_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = DEVPACE_ROOT / "skills"
EVAL_DATA_DIR = DEVPACE_ROOT / "tests" / "evaluation"


def get_current_description(skill_dir: Path) -> str:
    """Extract current description from SKILL.md frontmatter."""
    content = (skill_dir / "SKILL.md").read_text()
    lines = content.split("\n")
    if lines[0].strip() != "---":
        return ""

    desc_lines = []
    in_desc = False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                in_desc = True
                continue
            else:
                return value.strip('"').strip("'")
        elif in_desc:
            if line.startswith("  ") or line.startswith("\t"):
                desc_lines.append(line.strip())
            else:
                in_desc = False
    return " ".join(desc_lines)


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


def replace_description(skill_dir: Path, new_desc: str) -> None:
    """Replace description in SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"

    # Backup
    backup = skill_md.with_suffix(".md.bak")
    shutil.copy2(skill_md, backup)

    content = skill_md.read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        print("Error: SKILL.md has no frontmatter", file=sys.stderr)
        return

    # Find description field boundaries
    desc_start = None
    desc_end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            if desc_start is not None and desc_end is None:
                desc_end = i
            break
        if line.startswith("description:"):
            desc_start = i
            value = line[len("description:"):].strip()
            if value not in (">", "|", ">-", "|-"):
                desc_end = i + 1
            continue
        if desc_start is not None and desc_end is None:
            if line.startswith("  ") or line.startswith("\t"):
                continue
            else:
                desc_end = i

    if desc_start is None:
        print("Error: no description field found in frontmatter", file=sys.stderr)
        return

    if desc_end is None:
        desc_end = desc_start + 1

    # Format new description
    if len(new_desc) <= 200:
        new_lines = [f"description: {new_desc}"]
    else:
        # Use folded block scalar for long descriptions
        wrapped = new_desc.replace("\n", " ")
        new_lines = ["description: >"]
        # Split into ~80 char lines
        words = wrapped.split()
        current_line = "  "
        for word in words:
            if len(current_line) + len(word) + 1 > 80 and len(current_line) > 2:
                new_lines.append(current_line)
                current_line = "  " + word
            else:
                current_line += (" " if len(current_line) > 2 else "") + word
        if current_line.strip():
            new_lines.append(current_line)

    # Replace
    result_lines = lines[:desc_start] + new_lines + lines[desc_end:]
    new_content = "\n".join(result_lines)

    # Validate frontmatter is parseable
    fm_lines = new_content.split("\n")
    if fm_lines[0].strip() != "---":
        print("Error: broken frontmatter after replacement, restoring backup", file=sys.stderr)
        shutil.copy2(backup, skill_md)
        return

    has_closing = False
    for line in fm_lines[1:]:
        if line.strip() == "---":
            has_closing = True
            break
    if not has_closing:
        print("Error: broken frontmatter (no closing ---), restoring backup", file=sys.stderr)
        shutil.copy2(backup, skill_md)
        return

    skill_md.write_text(new_content)
    backup.unlink()
    print(f"  description updated in {skill_md.relative_to(DEVPACE_ROOT)}")


def cmd_diff(args: argparse.Namespace) -> int:
    """Show diff between current and best description."""
    skill_name = args.skill
    skill_dir = SKILLS_DIR / skill_name

    current = get_current_description(skill_dir)
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

    current = get_current_description(skill_dir)
    if current == best:
        print(f"  {skill_name}: description already matches best")
        return 0

    replace_description(skill_dir, best)
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
