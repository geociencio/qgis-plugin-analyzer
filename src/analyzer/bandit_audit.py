"""Bandit security audit executed via subprocess.

The analyzer keeps its native Bandit-inspired rules; this adapter runs the real
Bandit tool for portal parity and normalizes its findings into the analyzer
schema (``tool``, ``rule_id``, ``portal_severity``, ``blocking``).
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from typing import Any

from .utils import logger

_SEVERITY_MAP = {"HIGH": "critical", "MEDIUM": "warning", "LOW": "info"}


def _relative_path(filename: str, project_path: pathlib.Path) -> str:
    """Return ``filename`` relative to the project when possible."""
    try:
        return str(pathlib.Path(filename).resolve().relative_to(project_path.resolve()))
    except (OSError, ValueError):
        return filename


def _map_finding(item: dict[str, Any], project_path: pathlib.Path) -> dict[str, Any]:
    """Normalize one Bandit result to the analyzer schema."""
    raw_severity = str(item.get("issue_severity", "LOW")).upper()
    portal_severity = _SEVERITY_MAP.get(raw_severity, "info")
    rule_id = str(item.get("test_id", "UNKNOWN"))
    return {
        "file": _relative_path(str(item.get("filename", "")), project_path),
        "line": int(item.get("line_number", 0) or 0),
        "col": int(item.get("col_offset", 0) or 0),
        "type": f"BANDIT_{rule_id}",
        "rule_id": rule_id,
        "severity": portal_severity,
        "portal_severity": portal_severity,
        "blocking": portal_severity == "critical",
        "message": str(item.get("issue_text", "")),
        "confidence": str(item.get("issue_confidence", "")).lower(),
        "cwe": item.get("issue_cwe", {}).get("id")
        if isinstance(item.get("issue_cwe"), dict)
        else None,
        "tool": "bandit",
    }


def run_bandit_audit(project_path: pathlib.Path) -> dict[str, Any]:
    """Executes Bandit and normalizes its JSON findings.

    Args:
        project_path: Root path of the project to scan.

    Returns:
        A dictionary with ``findings``, ``exit_code``, ``command`` and
        ``tool_unavailable``.
    """
    cmd = [
        sys.executable,
        "-m",
        "bandit",
        "-r",
        str(project_path),
        "-f",
        "json",
        "-q",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as exc:  # pragma: no cover - defensive subprocess guard
        logger.error(f"Error running Bandit: {exc}")
        return {
            "findings": [],
            "stderr": str(exc),
            "exit_code": -1,
            "command": " ".join(cmd),
            "tool_unavailable": True,
        }

    stderr = result.stderr or ""
    payload = result.stdout or ""
    if "No module named" in stderr and not payload:
        logger.warning("⚠️  Bandit is not available; skipping the Bandit audit.")
        return {
            "findings": [],
            "stderr": stderr,
            "exit_code": result.returncode,
            "command": " ".join(cmd),
            "tool_unavailable": True,
        }

    findings: list[dict[str, Any]] = []
    if payload:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Bandit JSON output: {exc}")
            data = {}
        for item in (data.get("results") or []) if isinstance(data, dict) else []:
            if isinstance(item, dict):
                findings.append(_map_finding(item, project_path))

    return {
        "findings": findings,
        "stderr": stderr,
        "exit_code": result.returncode,
        "command": " ".join(cmd),
        "tool_unavailable": False,
    }
