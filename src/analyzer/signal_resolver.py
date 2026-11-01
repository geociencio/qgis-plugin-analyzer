"""Resolve collected signal events into matched/unmatched connection records.

Resolution is project-wide and configuration-dependent, so it runs after the
per-module analysis cache and before scoring when ``emit=true``.
"""

from __future__ import annotations

import fnmatch
import pathlib
from typing import Any

from .utils import IgnoreMatcher

_CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}


def resolve_signals(
    events: list[dict[str, Any]],
    *,
    scope: str = "class",
    confidence: str = "low",
    include_benign: bool = False,
    ignore_senders: list[str] | None = None,
    ignore_paths: list[str] | None = None,
    project_root: pathlib.Path | None = None,
) -> dict[str, Any]:
    """Resolve raw signal events into connection records.

    Args:
        events: Raw events produced by :func:`analyzer.signal_analysis.collect_signal_events`.
        scope: Matching scope: ``function``, ``class`` or ``file``.
        confidence: Minimum confidence for the deprecated ``signal_leaks`` list.
        ignore_senders: Sender globs to omit.
        ignore_paths: File globs to omit; uses ``IgnoreMatcher`` semantics.
        project_root: Project root for ``ignore_paths`` and relative paths.

    Returns:
        A report with ``summary``, ``items`` and the legacy ``signal_leaks`` list.
    """
    scope = scope if scope in ("function", "class", "file") else "class"
    sender_globs = ignore_senders or []
    path_patterns = ignore_paths or []
    matcher = (
        IgnoreMatcher(project_root, path_patterns)
        if project_root is not None and path_patterns
        else None
    )

    filtered: list[dict[str, Any]] = []
    for event in events:
        sender = str(event.get("sender", ""))
        if any(fnmatch.fnmatch(sender, pattern) for pattern in sender_globs):
            continue
        if matcher is not None:
            assert project_root is not None
            if matcher.is_ignored(project_root / str(event.get("file", ""))):
                continue
        filtered.append(dict(event))

    connects = _unique_connects([event for event in filtered if event.get("kind") == "connect"])
    disconnects = [event for event in filtered if event.get("kind") == "disconnect"]
    connects = _attach_indices(connects)
    disconnects = _attach_indices(disconnects)

    pending = {record["_index"]: record for record in connects}
    matched: set[int] = set()
    for disconnect in sorted(disconnects, key=_event_sort_key):
        candidates = [
            record
            for record in pending.values()
            if _same_group(record, disconnect, scope)
            and record.get("sender") == disconnect.get("sender")
            and _receiver_matches(record, disconnect)
            and _slot_matches(record, disconnect)
        ]
        candidates.sort(key=_event_sort_key)
        for candidate in candidates if disconnect.get("slot") is None else candidates[:1]:
            matched.add(candidate["_index"])
            pending.pop(candidate["_index"], None)

    other_disconnects = {
        (disconnect.get("file"), disconnect.get("sender"))
        for disconnect in disconnects
        if disconnect.get("sender")
    }
    records = [_record(record, matched, other_disconnects) for record in connects]
    records.sort(key=_event_sort_key)
    return _build_report(records, confidence, include_benign)


def aggregate_signal_reports(modules: list[Any]) -> dict[str, Any] | None:
    """Aggregate per-module signal reports into the project summary block."""
    reports = []
    for module in modules:
        context = module.get("research_metrics", {}).get("qgis_context", {})
        report = context.get("signal_connections")
        if isinstance(report, dict):
            reports.append(report)
    if not reports:
        return None

    items = [item for report in reports for item in report.get("items", [])]
    summary = _summary(items)
    legacy = sorted(
        {
            str(item.get("sender", ""))
            for item in items
            if item.get("status") == "unmatched" and item.get("sender")
        }
    )
    return {
        "summary": summary,
        "items": items,
        "signal_leaks": legacy,
        "include_benign": any(report.get("include_benign", False) for report in reports),
    }


def report_for_file(report: dict[str, Any], file: str) -> dict[str, Any]:
    """Return the subset of a project report that belongs to one module."""
    items = [item for item in report.get("items", []) if item.get("file") == file]
    legacy = sorted(
        {
            str(item.get("sender", ""))
            for item in items
            if item.get("status") == "unmatched" and item.get("sender")
        }
    )
    return {
        "summary": _summary(items),
        "items": items,
        "signal_leaks": legacy,
        "include_benign": report.get("include_benign", False),
    }


def _unique_connects(connects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop duplicate ``Qt.UniqueConnection`` connections."""
    seen: set[tuple[Any, ...]] = set()
    unique_connects: list[dict[str, Any]] = []
    for event in sorted(connects, key=_event_sort_key):
        key = (
            event.get("scope"),
            event.get("sender"),
            event.get("receiver"),
            event.get("slot"),
        )
        if event.get("connection_type") == "unique":
            if key in seen:
                continue
            seen.add(key)
        else:
            seen.add(key)
        unique_connects.append(event)
    return unique_connects


def _attach_indices(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach a stable internal index to events."""
    return [{**event, "_index": index} for index, event in enumerate(events)]


def _same_group(connect: dict[str, Any], disconnect: dict[str, Any], scope: str) -> bool:
    """Return whether two events belong to the same matching scope."""
    if scope == "file":
        return connect.get("file") == disconnect.get("file")
    if scope == "function":
        return (connect.get("file"), connect.get("scope")) == (
            disconnect.get("file"),
            disconnect.get("scope"),
        )
    connect_key = (connect.get("file"), connect.get("class_name") or connect.get("scope"))
    disconnect_key = (
        disconnect.get("file"),
        disconnect.get("class_name") or disconnect.get("scope"),
    )
    return connect_key == disconnect_key


def _receiver_matches(connect: dict[str, Any], disconnect: dict[str, Any]) -> bool:
    """Compare receivers, treating an unknown disconnect receiver as wildcard."""
    if disconnect.get("receiver") is None:
        return True
    return connect.get("receiver") == disconnect.get("receiver")


def _slot_matches(connect: dict[str, Any], disconnect: dict[str, Any]) -> bool:
    """Compare slots, treating a slot-less disconnect as wildcard."""
    if disconnect.get("slot") is None:
        return True
    return connect.get("slot") == disconnect.get("slot")


def _record(
    event: dict[str, Any],
    matched: set[int],
    other_disconnects: set[tuple[Any, Any]],
) -> dict[str, Any]:
    """Build one resolved connection record."""
    index = int(event.pop("_index"))
    lifetime = event.get("lifetime")
    if index in matched:
        status = "matched"
        reason = "matched disconnect in scope"
    elif lifetime:
        status = "benign"
        reason = f"benign lifetime: {lifetime}"
    else:
        status = "unmatched"
        reason = "no matching disconnect in scope"
        if (event.get("file"), event.get("sender")) not in other_disconnects and any(
            sender == event.get("sender") and file != event.get("file")
            for file, sender in other_disconnects
        ):
            status = "unmatched"
            reason = "cross-module disconnect not resolved"
            event["confidence"] = "low"
    return {**event, "status": status, "reason": reason, "lifetime": lifetime}


def _summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute the connection summary from resolved items."""
    return {
        "connect_sites": len(items),
        "matched": sum(1 for item in items if item.get("status") == "matched"),
        "unmatched": sum(1 for item in items if item.get("status") == "unmatched"),
        "benign": sum(1 for item in items if item.get("status") == "benign"),
        "by_confidence": {
            level: sum(1 for item in items if item.get("confidence") == level)
            for level in ("high", "medium", "low")
        },
    }


def _build_report(
    items: list[dict[str, Any]], confidence: str, include_benign: bool = False
) -> dict[str, Any]:
    """Build the final report, including the deprecated legacy list."""
    minimum = _CONFIDENCE_RANK.get(confidence, 1)
    legacy = sorted(
        {
            str(item.get("sender", ""))
            for item in items
            if item.get("status") == "unmatched"
            and _CONFIDENCE_RANK.get(str(item.get("confidence")), 1) >= minimum
            and item.get("sender")
        }
    )
    return {
        "summary": _summary(items),
        "items": items,
        "signal_leaks": legacy,
        "include_benign": include_benign,
    }


def _event_sort_key(event: dict[str, Any]) -> tuple[Any, ...]:
    """Stable ordering for events and records."""
    return (
        str(event.get("file", "")),
        int(event.get("line", 0) or 0),
        str(event.get("sender", "")),
        str(event.get("slot", "")),
        int(event.get("order", 0) or 0),
    )
