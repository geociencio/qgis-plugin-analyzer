"""Flake8 lint audit executed via subprocess.

Complements :mod:`analyzer.ruff_audit` for projects whose portal/legacy
pipeline still relies on Flake8. Flake8 is optional: when it is not installed
the result is flagged with ``tool_unavailable=True`` instead of silently
reporting zero findings.

The JSON formatter comes from the optional ``flake8-json`` plugin. When that
plugin is absent, the default ``path:row:col: CODE message`` output is parsed.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import subprocess
import sys
from typing import Any

from .utils import logger

_DEFAULT_LINE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+):\s+"
    r"(?P<code>[A-Z]\d{3,4})\s+(?P<message>.*)$"
)
_JSON_PLUGIN_MODULES = ("flake8_json_reporter", "flake8_json")


def _relative_path(filename: str, project_path: pathlib.Path) -> str:
    """Return ``filename`` relative to the project when possible."""
    try:
        return str(pathlib.Path(filename).resolve().relative_to(project_path.resolve()))
    except (OSError, ValueError):
        return filename


def _finding(
    *,
    filename: str,
    line: int,
    col: int,
    code: str,
    message: str,
    project_path: pathlib.Path,
) -> dict[str, Any]:
    """Normalize one Flake8 violation to the analyzer schema."""
    return {
        "file": _relative_path(filename, project_path),
        "line": line,
        "col": col,
        "code": code,
        "type": f"FLAKE8_{code}" if code else "FLAKE8",
        "rule_id": code,
        "severity": "info",
        "message": message,
        "tool": "flake8",
    }


def _first(entry: dict[str, Any], *keys: str) -> Any:
    """Return the first non-empty value for ``keys`` in ``entry``."""
    for key in keys:
        value = entry.get(key)
        if value not in (None, ""):
            return value
    return ""


def _entry_to_finding(entry: dict[str, Any], project_path: pathlib.Path) -> dict[str, Any]:
    """Convert one ``flake8-json`` entry into an analyzer finding."""
    return _finding(
        filename=str(_first(entry, "filename", "path")),
        line=int(_first(entry, "line_number", "line") or 0),
        col=int(_first(entry, "column_number", "col") or 0),
        code=str(_first(entry, "code")),
        message=str(_first(entry, "text", "message")),
        project_path=project_path,
    )


def _iter_json_entries(data: Any) -> list[dict[str, Any]]:
    """Flatten the mapping/list forms produced by ``flake8-json``."""
    groups: list[Any] = list(data.values()) if isinstance(data, dict) else [data]
    entries: list[dict[str, Any]] = []
    for group in groups:
        if isinstance(group, list):
            entries.extend(item for item in group if isinstance(item, dict))
        elif isinstance(group, dict):
            entries.append(group)
    return entries


def _parse_json(payload: str, project_path: pathlib.Path) -> list[dict[str, Any]]:
    """Parse ``flake8-json`` output (mapping or list forms)."""
    return [
        _entry_to_finding(entry, project_path) for entry in _iter_json_entries(json.loads(payload))
    ]


def _parse_default(payload: str, project_path: pathlib.Path) -> list[dict[str, Any]]:
    """Parse Flake8's default ``path:row:col: CODE message`` output."""
    findings: list[dict[str, Any]] = []
    for raw_line in payload.splitlines():
        match = _DEFAULT_LINE.match(raw_line.strip())
        if not match:
            continue
        findings.append(
            _finding(
                filename=match.group("file"),
                line=int(match.group("line")),
                col=int(match.group("col")),
                code=match.group("code"),
                message=match.group("message"),
                project_path=project_path,
            )
        )
    return findings


def run_flake8_audit(
    project_path: pathlib.Path, *, config: pathlib.Path | None = None
) -> dict[str, Any]:
    """Executes Flake8 via subprocess and normalizes its findings.

    Args:
        project_path: Root path of the project to lint.
        config: Optional Flake8 configuration file.

    Returns:
        A dictionary with ``findings``, ``exit_code``, ``command``,
        ``formatter`` and ``tool_unavailable``.
    """
    has_json = any(importlib.util.find_spec(module) is not None for module in _JSON_PLUGIN_MODULES)
    formatter = "json" if has_json else "default"
    cmd = [sys.executable, "-m", "flake8", str(project_path)]
    if config is not None:
        cmd += ["--config", str(config)]
    cmd += ["--format", formatter]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as exc:  # pragma: no cover - defensive subprocess guard
        logger.error(f"Error running Flake8: {exc}")
        return {
            "findings": [],
            "stderr": str(exc),
            "exit_code": -1,
            "command": " ".join(cmd),
            "formatter": formatter,
            "tool_unavailable": True,
        }

    stderr = result.stderr or ""
    payload = result.stdout or ""
    tool_unavailable = "No module named" in stderr and not payload
    if tool_unavailable:
        logger.warning("⚠️  Flake8 is not available; skipping the Flake8 audit.")
        return {
            "findings": [],
            "stderr": stderr,
            "exit_code": result.returncode,
            "command": " ".join(cmd),
            "formatter": formatter,
            "tool_unavailable": True,
        }

    findings: list[dict[str, Any]] = []
    if payload:
        try:
            findings = (
                _parse_json(payload, project_path)
                if formatter == "json"
                else _parse_default(payload, project_path)
            )
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            logger.error(f"Failed to parse Flake8 output: {exc}")

    return {
        "findings": findings,
        "stderr": stderr,
        "exit_code": result.returncode,
        "command": " ".join(cmd),
        "formatter": formatter,
        "tool_unavailable": False,
    }
