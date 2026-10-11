"""Summary reporter for terminal-based analysis results.

This module provides functions to display a professional summary of the
analysis findings directly in the terminal, with ANSI color support
for quality indicators. Console primitives and the focused security report
live in sibling modules (:mod:`console`, :mod:`security_summary`) and are
re-exported here for backward compatibility.
"""

import json
import pathlib
from typing import Any

from .console import (
    print_colored_score,
    print_header,
    print_separator,
    print_success,
)
from .security_summary import group_findings_by_severity as _group_findings_by_severity
from .security_summary import report_security as _report_security

__all__ = [
    "report_summary",
    "_group_findings_by_severity",
    "_report_security",
]


def report_summary(input_path: pathlib.Path, by: str = "total") -> bool:
    """Reads analysis JSON and prints a professional terminal summary.

    Args:
        input_path: Path to the project_context.json file.
        by: Granularity level ('total', 'modules', 'functions', 'classes', 'security').

    Returns:
        True if the report was successfully generated, False otherwise.
    """
    if not input_path.exists():
        print(f"\033[91mError: Analysis file not found at {input_path}\033[0m")
        return False

    try:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)

        if by == "total":
            return _report_total(data)
        elif by == "modules":
            return _report_by_modules(data)
        elif by == "functions":
            return _report_by_functions(data)
        elif by == "classes":
            return _report_by_classes(data)
        elif by == "security":
            return _report_security(data)
        else:
            print(f"\033[91mError: Unknown summary mode '{by}'\033[0m")
            return False

    except Exception as e:
        print(f"\033[91mError reading analysis results: {e}\033[0m")
        return False


# Specialized methods for _report_total


def _print_quality_indicators(metrics: dict[str, Any]) -> None:
    """Print quality scores section.

    Args:
        metrics: Dictionary containing quality metrics.
    """
    print_header("📊 Quality Indicators")
    print_colored_score("- Module Stability Score", metrics.get("quality_score", "N/A"))
    print_colored_score("- Code Maintainability Score", metrics.get("maintainability_score", "N/A"))
    print_colored_score("- Security Score (Bandit)", metrics.get("security_score", "N/A"))


def _print_research_metrics(research: dict[str, Any]) -> None:
    """Print research-based metrics section.

    Args:
        research: Dictionary containing research metrics.
    """
    if not research:
        return

    print_header("🔬 Research-based Metrics")
    params_cov = research.get("type_hint_coverage", 0)
    returns_cov = research.get("return_hint_coverage", 0)
    doc_cov = research.get("docstring_coverage", 0)
    styles = research.get("detected_docstring_styles", [])
    style = styles[0] if styles else "Unknown"

    print(f"- Type Hint Coverage (Params): {params_cov:.1f}%")
    print(f"- Type Hint Coverage (Returns): {returns_cov:.1f}%")
    print(f"- Docstring Coverage: {doc_cov:.1f}%")
    print(f"- Documentation Style: {style}")

    # QGIS Specific context
    q_ctx = research.get("qgis_context_summary")
    if q_ctx:
        print_header("🏗️  QGIS Transition & Style")
        g_styles = q_ctx.get("gdal_styles", {})
        g_style = "Legacy" if g_styles.get("Legacy", 0) > 0 else "Modern"
        p_usage = q_ctx.get("pyqt_usage", {})
        signals = q_ctx.get("total_legacy_signals", 0)

        print(f"- GDAL Import Style: {g_style}")
        print(f"- PyQt5 Usage: {'Detected' if p_usage.get('PyQt5', 0) > 0 else 'None'}")
        print(f"- Legacy Signals/Slots: {signals}")
        if q_ctx.get("uses_processing"):
            print("- Processing Framework: Active")

        leaks = q_ctx.get("signal_leaks", [])
        if leaks:
            print(f"🚨 Signal Leaks Detected: {len(leaks)}")
            for signal in leaks:
                print(f"  - {signal}")


def _collect_all_issues(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect and merge AST issues and security findings.

    Args:
        data: The full analysis results dictionary.

    Returns:
        List of all issues with file paths added.
    """
    issues: list[dict[str, Any]] = []

    # Collect AST issues
    for module in data.get("modules", []):
        mod_path = module.get("path", "unknown")
        for issue in module.get("ast_issues", []):
            issue["file"] = mod_path
            issues.append(issue)

    # Add security findings
    security_findings = data.get("security", {}).get("findings", [])
    for finding in security_findings:
        finding["type"] = f"SECURITY:{finding.get('type', 'generic')}"
        issues.append(finding)

    return issues


def _print_issue_statistics(issues: list[dict[str, Any]]) -> None:
    """Print issue counts grouped by type.

    Args:
        issues: List of all issues.
    """
    print(f"\n\033[1m⚠️  Issue Statistics ({len(issues)} total)\033[0m")
    counts: dict[str, int] = {}
    for issue in issues:
        issue_type = issue.get("type", "unknown")
        counts[issue_type] = counts.get(issue_type, 0) + 1

    for issue_type, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"- {issue_type}: {count}")


def _print_sample_issues(issues: list[dict[str, Any]], limit: int = 5) -> None:
    """Print sample issues with formatting.

    Args:
        issues: List of all issues.
        limit: Maximum number of issues to display.
    """
    print_header("🔍 Sample Issues")
    for issue in issues[:limit]:
        severity = issue.get("severity", "info").upper()
        sev_color = "\033[91m" if severity == "ERROR" else "\033[93m"
        print(
            f"{sev_color}[{severity}]\033[0m {issue['file']}:{issue.get('line', '?')} - {issue['message']}"
        )

    if len(issues) > limit:
        print(f"... and {len(issues) - limit} more issues.")


def _report_total(data: dict[str, Any]) -> bool:
    """Prints the executive total summary."""
    print_header("📋 QGIS Plugin Analyzer: Project Summary")
    print_separator()

    _print_quality_indicators(data.get("metrics", {}))
    _print_research_metrics(data.get("research_summary", {}))

    issues = _collect_all_issues(data)
    if not issues:
        print_success("✅ No issues detected! Your project looks great.")
    else:
        _print_issue_statistics(issues)
        _print_sample_issues(issues)

    print()
    print_separator()
    return True


def _report_by_modules(data: dict[str, Any]) -> bool:
    """Prints summary grouped by modules."""
    print("\n\033[1m📁 Summary by Modules (Top 10 by Issues)\033[0m")
    print("=" * 60)

    modules = data.get("modules", [])
    if not modules:
        print("No module data found.")
        return True

    # Calculate issues per module
    mod_stats = []
    for m in modules:
        mod_stats.append(
            {
                "path": m.get("path"),
                "issues": len(m.get("ast_issues", [])) + len(m.get("security_issues", [])),
                "complexity": m.get("complexity", 1),
                "lines": m.get("lines", 0),
            }
        )

    # Sort by issues (descending)
    mod_stats.sort(key=lambda x: x["issues"], reverse=True)

    print(f"{'Module Path':<40} | {'Issues':<6} | {'CC':<3} | {'Lines':<5}")
    print("-" * 60)
    for m in mod_stats[:10]:
        print(f"{m['path']:<40} | {m['issues']:<6} | {m['complexity']:<3} | {m['lines']:<5}")

    print("\n" + "=" * 60)
    return True


def _report_by_functions(data: dict[str, Any]) -> bool:
    """Prints summary grouped by functions (Top 10 by Complexity)."""
    print("\n\033[1m⚡ Summary by Functions (Top 10 by Complexity)\033[0m")
    print("=" * 70)

    all_funcs = []
    for m in data.get("modules", []):
        mod_path = m.get("path")
        for f in m.get("functions", []):
            f["module"] = mod_path
            all_funcs.append(f)

    if not all_funcs:
        print("No function data found.")
        return True

    # Sort by complexity
    all_funcs.sort(key=lambda x: x.get("complexity", 1), reverse=True)

    print(f"{'Function Name':<30} | {'Complexity':<10} | {'Module'}")
    print("-" * 70)
    for f in all_funcs[:10]:
        cc = f.get("complexity", 1)
        color = "\033[91m" if cc > 15 else ("\033[93m" if cc > 8 else "")
        reset = "\033[0m" if color else ""
        print(f"{f.get('name'):<30} | {color}{cc:<10}{reset} | {f.get('module')}")

    print("\n" + "=" * 70)
    return True


def _report_by_classes(data: dict[str, Any]) -> bool:
    """Prints summary grouped by classes."""
    print("\n\033[1m🏛️ Summary by Classes\033[0m")
    print("=" * 60)

    all_classes = []
    for m in data.get("modules", []):
        mod_path = m.get("path")
        for c in m.get("classes", []):
            all_classes.append({"name": c, "module": mod_path})

    if not all_classes:
        print("No class data found.")
        return True

    print(f"{'Class Name':<30} | {'Module'}")
    print("-" * 60)
    for c in all_classes:
        print(f"{c['name']:<30} | {c['module']}")

    print(f"\nTotal: {len(all_classes)} classes found.")
    print("=" * 60)
    return True
