"""SKILL.md read/write utilities.

Handles frontmatter parsing, description extraction, replacement,
and hashing for devpace skill files.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def read_description(skill_dir: Path) -> str:
    """Extract description from SKILL.md frontmatter.

    Supports both inline and multi-line (folded/literal block) descriptions.
    Returns empty string if SKILL.md does not exist.
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ""
    content = skill_md.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                parts = []
                for cont in lines[i + 1:]:
                    if cont.startswith("  ") or cont.startswith("\t"):
                        parts.append(cont.strip())
                    else:
                        break
                return " ".join(parts)
            # Only strip wrapping quotes if fully quoted
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                return value[1:-1]
            return value
    return ""


def read_skill_md(skill_dir: Path) -> str:
    """Read full SKILL.md content."""
    return (skill_dir / "SKILL.md").read_text()


def description_hash(skill_dir: Path) -> str:
    """SHA256 prefix (16 chars) of the current description."""
    return hashlib.sha256(read_description(skill_dir).encode()).hexdigest()[:16]


def _format_description_lines(desc: str) -> list[str]:
    """Format a description string into YAML frontmatter lines."""
    if len(desc) <= 200:
        return [f"description: {desc}"]

    new_lines = ["description: >"]
    words = desc.split()
    current_line = "  "
    for word in words:
        if len(current_line) + len(word) + 1 > 80 and len(current_line) > 2:
            new_lines.append(current_line)
            current_line = "  " + word
        else:
            current_line += (" " if len(current_line) > 2 else "") + word
    if current_line.strip():
        new_lines.append(current_line)
    return new_lines


def replace_description(skill_md: Path, new_desc: str) -> str:
    """Replace description in SKILL.md frontmatter.

    Returns the original file content (for rollback).
    """
    original = skill_md.read_text()
    lines = original.split("\n")
    if lines[0].strip() != "---":
        return original

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
        return original
    if desc_end is None:
        desc_end = desc_start + 1

    new_lines = _format_description_lines(new_desc)
    result_lines = lines[:desc_start] + new_lines + lines[desc_end:]
    skill_md.write_text("\n".join(result_lines))
    return original
