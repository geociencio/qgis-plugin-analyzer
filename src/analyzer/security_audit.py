"""Security report orchestration for the focused ``security`` command.

The engine owns native AST/secret detection; this module merges those findings
with optional external tools (Bandit, detect-secrets, Flake8), normalizes
severities to the cross-repository portal contract and computes the exit code.
"""

from __future__ import annotations

import pathlib
from collections.abc import Mapping
from typing import Any

from . import __version__
from .bandit_audit import run_bandit_audit
from .detect_secrets_audit import run_detect_secrets_audit
from .flake8_audit import run_flake8_audit
from .rules.scopes import SCOPE_RULES
from .utils import IgnoreMatcher

KNOWN_TOOLS = frozenset({"native", "bandit", "detect-secrets", "flake8"})
_SEVERITY_MAP = {
    "critical": "critical",
    "high": "critical",
    "warning": "warning",
    "medium": "warning",
    "info": "info",
    "low": "info",
}
_FAIL_ON = {
    "critical": {"critical"},
    "warning": {"critical", "warning"},
    "info": {"critical", "warning", "info"},
    "none": set(),
}


def parse_tools(value: str | None) -> list[str]:
    """Parse and validate the ``--tools`` comma-separated list.

    Args:
        value: Raw CLI value (``None`` means the native default).

    Returns:
        The ordered, de-duplicated tool names.

    Raises:
        ValueError: If an unknown tool is requested.
    """
    if not value:
        return ["native"]
    tools = [item.strip().lower() for item in str(value).split(",") if item.strip()]
    if not tools:
        return ["native"]
    unknown = set(tools) - KNOWN_TOOLS
    if unknown:
        raise ValueError(f"Unknown security tool(s): {', '.join(sorted(unknown))}")
    return list(dict.fromkeys(tools))


def _portal_severity(value: Any) -> str:
    """Map a native/external severity to the portal vocabulary."""
    return _SEVERITY_MAP.get(str(value or "medium").lower(), "warning")


def _normalize_native(issue: dict[str, Any]) -> dict[str, Any]:
    """Normalize a native engine finding to the security report schema."""
    severity = _portal_severity(issue.get("severity", "medium"))
    rule_id = str(issue.get("type", "UNKNOWN"))
    return {
        "file": issue.get("file", ""),
        "line": int(issue.get("line", 0) or 0),
        "col": int(issue.get("col", 0) or 0),
        "type": rule_id,
        "rule_id": rule_id,
        "severity": severity,
        "portal_severity": severity,
        "blocking": severity == "critical",
        "message": issue.get("message", ""),
        "tool": "native",
    }


def collect_native_findings(context: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Collect native security findings from the analysis context.

    ``security_issues`` carries the Bandit-inspired and secret findings;
    ``ast_issues`` is filtered to the security scope for rules such as
    ``UNSAFE_SUBPROCESS``.
    """
    allowed = SCOPE_RULES.get("security", set())
    findings: list[dict[str, Any]] = []
    for module in context.get("modules", []):
        for issue in module.get("security_issues", []) or []:
            findings.append(_normalize_native(issue))
        for issue in module.get("ast_issues", []) or []:
            if issue.get("type") in allowed:
                findings.append(_normalize_native(issue))
    return findings


def _merge(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """De-duplicate findings, preferring external tools over native ones."""
    merged: dict[tuple[str, int, str], dict[str, Any]] = {}
    for finding in findings:
        key = (
            str(finding.get("file", "")),
            int(finding.get("line", 0) or 0),
            str(finding.get("rule_id") or finding.get("type", "")),
        )
        existing = merged.get(key)
        if existing is None or existing.get("tool") == "native":
            merged[key] = finding
    return sorted(
        merged.values(),
        key=lambda item: (
            str(item.get("file", "")),
            int(item.get("line", 0) or 0),
            str(item.get("rule_id", "")),
        ),
    )


def meets_fail_on(findings: list[dict[str, Any]], fail_on: str) -> bool:
    """Return True when any finding reaches the ``fail_on`` threshold."""
    threshold = _FAIL_ON.get(fail_on, _FAIL_ON["critical"])
    return any(item.get("portal_severity") in threshold for item in findings)


def _is_ignored(
    finding: dict[str, Any], project_path: pathlib.Path, matcher: IgnoreMatcher
) -> bool:
    """Return whether a finding's file is excluded from the scan."""
    raw_path = str(finding.get("file") or "")
    if not raw_path:
        return False
    path = pathlib.Path(raw_path)
    target = path if path.is_absolute() else project_path / path
    return matcher.is_ignored(target)


def build_security_report(
    context: dict[str, Any],
    *,
    project_path: pathlib.Path,
    tools: list[str],
    deep: bool,
    fail_on: str = "critical",
    matcher: IgnoreMatcher | None = None,
) -> dict[str, Any]:
    """Build the security report envelope and exit code.

    Args:
        context: Parsed ``project_context.json`` from the security-scope run.
        project_path: Root path of the analyzed project.
        tools: Requested tools (``native``, ``bandit``, ``detect-secrets``,
            ``flake8``).
        deep: Whether the native entropy heuristic ran.
        fail_on: Lowest severity that produces a non-zero exit code.
        matcher: Optional ignore matcher used to drop findings from excluded
            files (the external tools scan the tree themselves).

    Returns:
        A JSON-serializable report with ``findings``, ``summary``,
        ``tool_status`` and ``exit_code``.
    """
    findings = collect_native_findings(context)
    tool_status: dict[str, str] = {"native": "ok"}

    if "bandit" in tools:
        result = run_bandit_audit(project_path)
        findings.extend(result["findings"])
        tool_status["bandit"] = "unavailable" if result["tool_unavailable"] else "ok"

    if "detect-secrets" in tools:
        result = run_detect_secrets_audit(project_path)
        findings.extend(result["findings"])
        tool_status["detect-secrets"] = "unavailable" if result["tool_unavailable"] else "ok"

    if "flake8" in tools:
        result = run_flake8_audit(project_path)
        for finding in result["findings"]:
            finding.setdefault("portal_severity", "info")
            finding.setdefault("blocking", False)
        findings.extend(result["findings"])
        tool_status["flake8"] = "unavailable" if result["tool_unavailable"] else "ok"

    if matcher is not None:
        findings = [
            finding for finding in findings if not _is_ignored(finding, project_path, matcher)
        ]

    merged = _merge(findings)
    summary = {
        "total": len(merged),
        "critical": sum(1 for item in merged if item["portal_severity"] == "critical"),
        "warning": sum(1 for item in merged if item["portal_severity"] == "warning"),
        "info": sum(1 for item in merged if item["portal_severity"] == "info"),
        "blocking": sum(1 for item in merged if item.get("blocking")),
    }

    if any(status == "unavailable" for status in tool_status.values()):
        exit_code = 2
    elif meets_fail_on(merged, fail_on):
        exit_code = 1
    else:
        exit_code = 0

    return {
        "schema_version": 1,
        "schema": 1,
        "analyzer_version": __version__,
        "command": "security",
        "scope": "security",
        "project_path": str(project_path),
        "analyzed_at": context.get("analyzed_at"),
        "success": exit_code == 0,
        "exit_code": exit_code,
        "deep": deep,
        "fail_on": fail_on,
        "tools": tools,
        "tool_status": tool_status,
        "tool_unavailable": any(status == "unavailable" for status in tool_status.values()),
        "findings": merged,
        "summary": summary,
    }


def format_security_report(report: dict[str, Any]) -> list[str]:
    """Render a compact human-readable security report.

    Args:
        report: Result of :func:`build_security_report`.

    Returns:
        Lines suitable for printing to stdout.
    """
    summary = report["summary"]
    lines = [
        f"Security findings: {summary['total']} "
        f"(critical={summary['critical']}, warning={summary['warning']}, info={summary['info']})"
    ]
    unavailable = [
        name for name, status in report["tool_status"].items() if status == "unavailable"
    ]
    if unavailable:
        lines.append(f"⚠️  Unavailable tools: {', '.join(sorted(unavailable))}")
    for finding in report["findings"]:
        lines.append(
            f"  [{finding['portal_severity'].upper()}] {finding['file']}:{finding['line']} "
            f"{finding['rule_id']} - {finding['message']}"
        )
    return lines
