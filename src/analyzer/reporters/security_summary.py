"""Focused security summary reporter for the terminal.

Extracted from :mod:`analyzer.reporters.summary_reporter` to keep that module
within the project's size limit. Uses the shared console primitives.
"""

from typing import Any

from .console import print_colored_score, print_header, print_separator, print_success


def group_findings_by_severity(
    findings: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group security findings by severity level.

    Args:
        findings: List of security findings.

    Returns:
        Dictionary mapping severity levels to lists of findings.
    """
    by_severity: dict[str, list[dict[str, Any]]] = {"high": [], "medium": [], "low": []}
    for finding in findings:
        sev = finding.get("severity", "medium").lower()
        if sev in by_severity:
            by_severity[sev].append(finding)
        else:
            by_severity.setdefault("other", []).append(finding)
    return by_severity


def _print_security_finding(finding: dict[str, Any], severity: str) -> None:
    """Print a single security finding with formatting.

    Args:
        finding: The security finding dictionary.
        severity: The severity level (high, medium, low).
    """
    sev_color = (
        "\033[91m" if severity == "high" else ("\033[93m" if severity == "medium" else "\033[94m")
    )
    print(
        f"{sev_color}[{severity.upper()}]\033[0m {finding.get('file')}:{finding.get('line')} - {finding.get('type')}"
    )
    print(f"  \033[2mMessage: {finding.get('message')}\033[0m")
    code_snippet = finding.get("code")
    if isinstance(code_snippet, str) and code_snippet.strip():
        print(f"  \033[2mCode   : {code_snippet.strip()}\033[0m")
    print()


def _print_security_findings_by_severity(
    by_severity: dict[str, list[dict[str, Any]]],
) -> None:
    """Print all findings grouped by severity.

    Args:
        by_severity: Dictionary mapping severity levels to findings.
    """
    print_header("🛑 Detailed Findings")
    print_separator("-", 60)

    for severity in ["high", "medium", "low"]:
        group = by_severity.get(severity, [])
        if not group:
            continue

        for finding in group:
            _print_security_finding(finding, severity)


def report_security(data: dict[str, Any]) -> bool:
    """Prints a focused security analysis report.

    Args:
        data: The full analysis results dictionary.

    Returns:
        True if the report was successfully generated.
    """
    print_header("🛡️  QGIS Plugin Analyzer: Security Scan")
    print_separator("=", 60)

    security = data.get("security", {})
    findings = security.get("findings", [])
    sec_score = security.get("score", 0.0)

    print_colored_score("Security Health Score", sec_score)
    print(f"Total vulnerabilities detected: {len(findings)}")

    if not findings:
        print_success("✅ No security vulnerabilities found!")
    else:
        by_severity = group_findings_by_severity(findings)
        _print_security_findings_by_severity(by_severity)

    print_separator("=", 60)
    return True
