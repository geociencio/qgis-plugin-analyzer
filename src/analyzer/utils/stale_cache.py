"""Stale-cache detection for persisted analysis results.

Extracted from :mod:`analyzer.commands` to keep the CLI module within the
project's module-size limit. Compares the cached ``project_context.json``
timestamp against the source tree to warn when a re-run is needed.
"""

import datetime
import json
import pathlib
import time
from typing import Any


def detect_stale_cache(input_path: pathlib.Path) -> str | None:
    """Detects whether cached analysis results are stale.

    Args:
        input_path: Path to the cached ``project_context.json``.

    Returns:
        A human-readable warning string if stale, otherwise None.
    """
    try:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    source_dir = pathlib.Path(data.get("project_path") or ".").resolve()
    if not source_dir.is_dir():
        return None

    analyzed_dt = _parse_analyzed_at(data.get("analyzed_at"))
    cutoff = analyzed_dt.timestamp() if analyzed_dt else input_path.stat().st_mtime

    newer_files = _find_newer_source_files(source_dir, cutoff)
    if not newer_files:
        return None

    age = _humanize_age(cutoff)
    preview = ", ".join(str(f.relative_to(source_dir)) for f in newer_files[:3])
    if len(newer_files) > 3:
        preview += ", …"

    return (
        f"⚠️  Cached results are stale (generated {age}). "
        f"{len(newer_files)} source file(s) changed after the analysis "
        f"(e.g. {preview}). Run 'qgis-analyzer analyze' to refresh."
    )


def _parse_analyzed_at(value: Any) -> datetime.datetime | None:
    """Parses the ISO 8601 ``analyzed_at`` timestamp.

    Args:
        value: Raw ``analyzed_at`` value from the analysis JSON.

    Returns:
        A timezone-aware datetime, or None if unparseable.
    """
    if not isinstance(value, str):
        return None
    try:
        return datetime.datetime.fromisoformat(value)
    except ValueError:
        return None


def _find_newer_source_files(source_dir: pathlib.Path, cutoff: float) -> list[pathlib.Path]:
    """Returns source files modified after the given cutoff timestamp.

    Args:
        source_dir: Root directory of the analyzed project.
        cutoff: Epoch seconds to compare modification times against.

    Returns:
        Up to 10 Python files modified after ``cutoff``.
    """
    excluded = {".venv", "venv", ".env", "__pycache__", ".git"}
    newer: list[pathlib.Path] = []
    for f in source_dir.rglob("*.py"):
        if any(part in excluded for part in f.parts):
            continue
        if f.is_file() and f.stat().st_mtime > cutoff:
            newer.append(f)
            if len(newer) >= 10:
                break
    return newer


def _humanize_age(timestamp: float) -> str:
    """Returns a human-readable age string for the given epoch timestamp.

    Args:
        timestamp: Epoch seconds to compute the age of.

    Returns:
        A string like ``5m ago`` or ``2d ago``.
    """
    seconds = max(0, int(time.time() - timestamp))
    if seconds < 60:
        return f"{seconds}s ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    return f"{hours // 24}d ago"
