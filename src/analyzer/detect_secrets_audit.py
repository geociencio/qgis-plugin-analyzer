"""detect-secrets audit executed via subprocess.

Runs the real ``detect-secrets`` scanner for portal parity. Any reported
finding is treated as ``critical``/blocking (a hardcoded secret must be
resolved before release). The native entropy/regex scanner remains available
through ``--tools native``.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from typing import Any

from .utils import logger

_EXCLUDE_PATTERN = r"(\.git|\.venv|build|dist|__pycache__)/"


def _relative_path(filename: str, project_path: pathlib.Path) -> str:
    """Return ``filename`` relative to the project when possible."""
    try:
        return str(pathlib.Path(filename).resolve().relative_to(project_path.resolve()))
    except (OSError, ValueError):
        return filename


def run_detect_secrets_audit(project_path: pathlib.Path) -> dict[str, Any]:
    """Executes detect-secrets and normalizes its findings.

    Args:
        project_path: Root path of the project to scan.

    Returns:
        A dictionary with ``findings``, ``exit_code``, ``command`` and
        ``tool_unavailable``.
    """
    cmd = [
        sys.executable,
        "-m",
        "detect_secrets",
        "scan",
        "--all-files",
        "--exclude-files",
        _EXCLUDE_PATTERN,
        str(project_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as exc:  # pragma: no cover - defensive subprocess guard
        logger.error(f"Error running detect-secrets: {exc}")
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
        logger.warning("⚠️  detect-secrets is not available; skipping the scan.")
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
            logger.error(f"Failed to parse detect-secrets JSON output: {exc}")
            data = {}
        results = (data.get("results") or {}) if isinstance(data, dict) else {}
        for filename, entries in results.items():
            for entry in entries if isinstance(entries, list) else []:
                if not isinstance(entry, dict):
                    continue
                secret_type = str(entry.get("type", "UNKNOWN"))
                findings.append(
                    {
                        "file": _relative_path(str(filename), project_path),
                        "line": int(entry.get("line_number", 0) or 0),
                        "col": 0,
                        "type": f"SECRET_{secret_type.upper()}",
                        "rule_id": secret_type,
                        "severity": "critical",
                        "portal_severity": "critical",
                        "blocking": True,
                        "message": f"Potential secret detected ({secret_type})",
                        "verified": bool(entry.get("is_verified", False)),
                        "tool": "detect-secrets",
                    }
                )

    return {
        "findings": findings,
        "stderr": stderr,
        "exit_code": result.returncode,
        "command": " ".join(cmd),
        "tool_unavailable": False,
    }
