"""Summary reporter for terminal-based analysis results.

This module provides functions to display a professional summary of the
analysis findings directly in the terminal, with ANSI color support
for quality indicators.
"""

import json
import pathlib
from typing import Any, Dict, List


def print_colored_score(label: str, score: Any) -> None:
    """Prints a score with ANSI colors based on its value.

    Args:
        label: The label for the score.
        score: The numeric score value (or "N/A").
    """
    if score == "N/A":
        print(f"{label}: \033[90mN/A\033[0m")
        return

    try:
        val = float(score)
        if val >= 80:
            color = "\033[92m"  # Green
        elif val >= 50:
            color = "\033[93m"  # Yellow
        else:
            color = "\033[91m"  # Red
        print(f"{label}: {color}{val:.1f}/100\033[0m")
    except (ValueError, TypeError):
        print(f"{label}: {score}")


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


def _report_total(data: Dict[str, Any]) -> bool:
    """Prints the executive total summary."""
    print("\n\033[1m📋 QGIS Plugin Analyzer: Project Summary\033[0m")
    print("=" * 45)

    # 1. Quality Indicators
    metrics = data.get("metrics", {})
    print("\n\033[1m📊 Quality Indicators\033[0m")
    print_colored_score("- Module Stability Score", metrics.get("quality_score", "N/A"))
    print_colored_score("- Code Maintainability Score", metrics.get("maintainability_score", "N/A"))
    print_colored_score("- Security Score (Bandit)", metrics.get("security_score", "N/A"))

    # 2. Research Metrics
    research = data.get("research_summary", {})
    if research:
        print("\n\033[1m🔬 Research-based Metrics\033[0m")
        params_cov = research.get("type_hint_coverage", 0)
        returns_cov = research.get("return_hint_coverage", 0)
        doc_cov = research.get("docstring_coverage", 0)
        styles = research.get("detected_docstring_styles", [])
        style = styles[0] if styles else "Unknown"

        print(f"- Type Hint Coverage (Params): {params_cov:.1f}%")
        print(f"- Type Hint Coverage (Returns): {returns_cov:.1f}%")
        print(f"- Docstring Coverage: {doc_cov:.1f}%")
        print(f"- Documentation Style: {style}")

    # 3. Issue Summary
    issues: List[Dict[str, Any]] = []
    for module in data.get("modules", []):
        mod_path = module.get("path", "unknown")
        for issue in module.get("ast_issues", []):
            issue["file"] = mod_path
            issues.append(issue)

    # Add Security Findings
    security_findings = data.get("security", {}).get("findings", [])
    for finding in security_findings:
        finding["type"] = f"SECURITY:{finding.get('type', 'generic')}"
        issues.append(finding)

    if not issues:
        print("\n\033[92m✅ No issues detected! Your project looks great.\033[0m")
    else:
        print(f"\n\033[1m⚠️  Issue Statistics ({len(issues)} total)\033[0m")
        counts: Dict[str, int] = {}
        for i in issues:
            t = i.get("type", "unknown")
            counts[t] = counts.get(t, 0) + 1

        for t, c in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            print(f"- {t}: {c}")

        # 4. Sample Issues
        print("\n\033[1m🔍 Sample Issues\033[0m")
        for i in issues[:5]:
            severity = i.get("severity", "info").upper()
            sev_color = "\033[91m" if severity == "ERROR" else "\033[93m"
            print(
                f"{sev_color}[{severity}]\033[0m {i['file']}:{i.get('line', '?')} - {i['message']}"
            )

        if len(issues) > 5:
            print(f"... and {len(issues) - 5} more issues.")

    print("\n" + "=" * 45)
    return True


def _report_by_modules(data: Dict[str, Any]) -> bool:
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


def _report_by_functions(data: Dict[str, Any]) -> bool:
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


def _report_by_classes(data: Dict[str, Any]) -> bool:
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


def _report_security(data: Dict[str, Any]) -> bool:
    """Prints a focused security analysis report.

    Args:
        data: The full analysis results dictionary.

    Returns:
        True if the report was successfully generated.
    """
    print("\n\033[1m🛡️  QGIS Plugin Analyzer: Security Scan\033[0m")
    print("=" * 60)

    security = data.get("security", {})
    findings = security.get("findings", [])
    sec_score = security.get("score", 0.0)

    print_colored_score("Security Health Score", sec_score)
    print(f"Total vulnerabilities detected: {len(findings)}")

    if not findings:
        print("\n\033[92m✅ No security vulnerabilities found!\033[0m")
    else:
        print("\n\033[1m🛑 Detailed Findings\033[0m")
        print("-" * 60)

        # Group by severity
        by_severity: Dict[str, List[Dict[str, Any]]] = {"high": [], "medium": [], "low": []}
        for f in findings:
            sev = f.get("severity", "medium").lower()
            if sev in by_severity:
                by_severity[sev].append(f)
            else:
                by_severity.setdefault("other", []).append(f)

        for sev in ["high", "medium", "low"]:
            group = by_severity.get(sev, [])
            if not group:
                continue

            sev_color = (
                "\033[91m" if sev == "high" else ("\033[93m" if sev == "medium" else "\033[94m")
            )
            for f in group:
                print(
                    f"{sev_color}[{sev.upper()}]\033[0m {f.get('file')}:{f.get('line')} - {f.get('type')}"
                )
                print(f"  \033[2mMessage: {f.get('message')}\033[0m")
                code_snippet = f.get("code")
                if isinstance(code_snippet, str) and code_snippet.strip():
                    print(f"  \033[2mCode   : {code_snippet.strip()}\033[0m")
                print()

    print("=" * 60)
    return True
