"""Structured feedback collection and notes.jsonl management.

Human feedback is the highest-signal improvement source for eval assertions.
This module provides CRUD operations on a Git-friendly JSONL file.
"""
from __future__ import annotations

import fcntl
import json
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from eval.core import EVAL_DATA_DIR

NOTES_PATH = EVAL_DATA_DIR / "_results" / "notes.jsonl"

NOTE_TYPES = ("observation", "fix_suggestion", "assertion_issue", "skip_reason")


@dataclass
class EvalNote:
    """A single human evaluation feedback note."""
    timestamp: str
    skill: str
    eval_id: int
    eval_name: str
    assertion_idx: int | None
    note: str
    author: str
    note_type: str
    resolved: bool = False
    resolved_by: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> EvalNote:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def _ensure_notes_dir() -> None:
    NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)


def _read_all_notes() -> list[EvalNote]:
    """Read all notes from notes.jsonl."""
    if not NOTES_PATH.exists():
        return []
    notes = []
    for line in NOTES_PATH.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            notes.append(EvalNote.from_dict(json.loads(line)))
        except (json.JSONDecodeError, TypeError):
            pass
    return notes


def _write_all_notes(notes: list[EvalNote]) -> None:
    """Overwrite notes.jsonl with the given notes list."""
    _ensure_notes_dir()
    lines = [json.dumps(n.to_dict(), ensure_ascii=False) for n in notes]
    NOTES_PATH.write_text("\n".join(lines) + "\n" if lines else "")


def append_note(
    *,
    skill: str,
    eval_id: int,
    eval_name: str = "",
    assertion_idx: int | None = None,
    note: str,
    author: str = "anonymous",
    note_type: str = "observation",
) -> EvalNote:
    """Append a new feedback note to notes.jsonl.

    Returns the created EvalNote.
    """
    if note_type not in NOTE_TYPES:
        raise ValueError(f"note_type must be one of {NOTE_TYPES}, got {note_type!r}")

    entry = EvalNote(
        timestamp=datetime.now(timezone.utc).isoformat(),
        skill=skill,
        eval_id=eval_id,
        eval_name=eval_name,
        assertion_idx=assertion_idx,
        note=note,
        author=author,
        note_type=note_type,
    )
    _ensure_notes_dir()
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
    return entry


@contextmanager
def _file_lock():
    """File lock for read-modify-write operations on notes.jsonl."""
    _ensure_notes_dir()
    lock_path = NOTES_PATH.with_suffix(".lock")
    with open(lock_path, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def resolve_note(
    skill: str,
    eval_id: int,
    assertion_idx: int | None,
    resolved_by: str,
) -> bool:
    """Mark matching unresolved note(s) as resolved.

    Returns True if at least one note was resolved.
    """
    with _file_lock():
        notes = _read_all_notes()
        changed = False
        for n in notes:
            if (
                n.skill == skill
                and n.eval_id == eval_id
                and n.assertion_idx == assertion_idx
                and not n.resolved
            ):
                n.resolved = True
                n.resolved_by = resolved_by
                changed = True
        if changed:
            _write_all_notes(notes)
    return changed


def list_pending(skill: str | None = None) -> list[EvalNote]:
    """Return all unresolved notes, optionally filtered by skill."""
    notes = _read_all_notes()
    return [
        n for n in notes
        if not n.resolved and (skill is None or n.skill == skill)
    ]


def list_stale(skill: str) -> list[EvalNote]:
    """Detect stale notes: unresolved notes where the assertion may have changed.

    A note is considered stale if it targets a specific assertion index
    and remains unresolved. The caller should cross-reference with
    the current evals.json to determine if the assertion text has changed.
    """
    notes = _read_all_notes()
    return [
        n for n in notes
        if n.skill == skill
        and not n.resolved
        and n.assertion_idx is not None
    ]


def list_notes(skill: str) -> list[EvalNote]:
    """Return all notes for a given skill."""
    return [n for n in _read_all_notes() if n.skill == skill]
