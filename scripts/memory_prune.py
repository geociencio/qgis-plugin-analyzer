#!/usr/bin/env python3
"""Prune expired agentic memory and report stale lessons.

- Deletes ``next_steps`` snapshots older than 90 days (recoverable via git).
- Reports ``AGENT_LESSONS.md`` entries older than 90 days as pruning candidates.

Usage:
    memory_prune.py          # dry-run: report what would change
    memory_prune.py --apply  # actually delete expired snapshots
"""

from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY_DIR = ROOT / ".agent" / "history" / "next_steps"
LESSONS = ROOT / ".agent" / "memory" / "AGENT_LESSONS.md"
RETENTION_DAYS = 90

SNAPSHOT_RE = re.compile(r"next_steps_(\d{4}-\d{2}-\d{2})(?:[_].*)?[.]md")
LESSON_DATE_RE = re.compile(r"^\s*- date:\s*['\"]?(\d{4}-\d{2}-\d{2})")


def expired_snapshots() -> list[Path]:
    """Return ``next_steps`` snapshots older than the retention window."""
    cutoff = date.today() - timedelta(days=RETENTION_DAYS)
    expired: list[Path] = []
    if not HISTORY_DIR.exists():
        return expired
    for path in HISTORY_DIR.glob("next_steps_*.md"):
        match = SNAPSHOT_RE.match(path.name)
        if match and date.fromisoformat(match.group(1)) < cutoff:
            expired.append(path)
    return expired


def stale_lessons() -> list[str]:
    """Return ``AGENT_LESSONS.md`` entries older than the retention window."""
    cutoff = date.today() - timedelta(days=RETENTION_DAYS)
    stale: list[str] = []
    if not LESSONS.exists():
        return stale
    for line in LESSONS.read_text(encoding="utf-8").splitlines():
        match = LESSON_DATE_RE.match(line)
        if match and date.fromisoformat(match.group(1)) < cutoff:
            stale.append(line.strip())
    return stale


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="delete expired snapshots")
    args = parser.parse_args()

    expired = expired_snapshots()
    stale = stale_lessons()

    print(f"Expired next_steps snapshots (> {RETENTION_DAYS}d): {len(expired)}")
    for path in expired:
        print(f"  {'rm' if args.apply else '  '} {path.relative_to(ROOT)}")
        if args.apply:
            path.unlink()

    print(f"Stale AGENT_LESSONS entries (> {RETENTION_DAYS}d): {len(stale)}")
    for entry in stale:
        print(f"  candidate: {entry}")

    if not args.apply:
        print("\n(dry-run; re-run with --apply to delete snapshots)")


if __name__ == "__main__":
    main()
