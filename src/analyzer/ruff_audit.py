"""Ruff lint audit executed via subprocess.

Extracted from :mod:`analyzer.engine` to keep the orchestrator within the
project's module-size limit.
"""

import json
import pathlib
import subprocess
import sys
from typing import Any

from .utils import logger


def run_ruff_audit(project_path: pathlib.Path, *, strict: bool = False) -> dict[str, Any]:
    """Executes Ruff linting via subprocess.

    Ruff is invoked through the current interpreter (``sys.executable -m
    ruff``) so the audit does not depend on ``ruff`` being on ``PATH``. When
    Ruff cannot be executed, the result is flagged with
    ``tool_unavailable=True`` instead of silently reporting zero findings.

    Args:
        project_path: Root path of the project to lint.
        strict: When True, force the extended Ruff rule selection.

    Returns:
        A dictionary containing findings and metadata, including
        ``tool_unavailable``.
    """
    cmd = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        str(project_path),
        "--output-format",
        "json",
        "--quiet",
    ]

    # In strict mode, we force extra rules if not already configured
    if strict:
        cmd.extend(
            [
                "--select",
                "E,F,W,C90,I,N,D,UP,YTT,ASYNC,S,BLE,B,A,COM,T10,EM,EXE,FA,ISC,ICN,G,INP,PIE,T20,PYI,PT,Q,RET,SLF,SIM,TID,TCH,INT,ARG,PTH,TD,ERA,PD,PGH,PL,TRY,FLY,PERF,FURB,LOG,RUFF",
            ]
        )

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as e:
        logger.error(f"Error running Ruff: {e}")
        return {
            "findings": [],
            "stderr": str(e),
            "exit_code": -1,
            "command": " ".join(cmd),
            "tool_unavailable": True,
        }

    findings: list[dict[str, Any]] = []
    tool_unavailable = False
    stderr = result.stderr or ""

    if "No module named" in stderr and not result.stdout:
        tool_unavailable = True
        logger.warning("⚠️  Ruff is not available; skipping the lint audit.")
    elif result.stdout:
        try:
            findings = json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.error("Failed to parse Ruff JSON output")

    return {
        "findings": findings,
        "stderr": stderr,
        "exit_code": result.returncode,
        "command": " ".join(cmd),
        "tool_unavailable": tool_unavailable,
    }
