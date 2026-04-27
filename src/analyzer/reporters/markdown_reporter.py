"""Markdown reporter for project analysis results.

This module provides functions to generate professional Markdown summaries
of the analysis findings, including scores, metrics, and technical debt.
"""

import datetime
import json
import pathlib
from typing import Any, Dict, List


def _build_markdown_header(
    analyses: Dict[str, Any], module_score: float, maint_score: float, project_type: str
) -> List[str]:
    """Builds the markdown header section including quality indicators.

    Args:
        analyses: The full analysis results dictionary.
        module_score: The calculated module stability score.
        maint_score: The calculated maintainability score.
        project_type: The type of project ("qgis" or "generic").

    Returns:
        A list of Markdown lines for the header.
    """
    project_label = "QGIS Plugin" if project_type == "qgis" else "Python Project"
    lines = [
        f"# 📋 Project Analysis Report: {analyses.get('project_name', project_label)}",
        f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "## 📊 Quality Indicators",
        f"- **Module Stability Score**: `{module_score}/100` (Based on file-level complexity)",
        f"- **Code Maintainability Score**: `{maint_score}/100` (Based on function-level complexity)",
    ]

    if project_type == "qgis":
        metrics = analyses.get("metrics", {})
        overall = metrics.get("overall_score", 0)
        lines.append(f"- **Overall Plugin Score**: `{overall}/100`")

        compliance = analyses.get("qgis_compliance", {})
        qgis_score = compliance.get("compliance_score", 0)
        lines.append(f"- **QGIS Compliance**: `{qgis_score}/100`")

    # Add Security Score
    sec_score = analyses.get("security", {}).get("score", 0)
    lines.append(f"- **Security Score**: `{sec_score}/100` (Bandit-inspired)")

    lines.append("")
    return lines


def _build_markdown_qgis_findings(analyses: Dict[str, Any]) -> List[str]:
    """Builds the QGIS findings section with icons and severities.

    Args:
        analyses: The full analysis results dictionary.

    Returns:
        A list of Markdown lines for the QGIS findings section.
    """
    lines = []
    compliance = analyses.get("qgis_compliance", {})
    best_practices = compliance.get("best_practices", {})
    lines.append("## 🛠️ QGIS Standard Findings")
    lines.append(f"Detected **{best_practices.get('issues_count', 0)}** technical deviations.")

    for issue in best_practices.get("issues", []):
        icon = "🔴" if issue["severity"] == "high" else "🟡"
        lines.append(f"- {icon} `{issue['file']}:{issue['line']}`: {issue['message']}")

    repo_stats = compliance.get("repository_standards", {})
    meta = repo_stats.get("metadata", {})
    status_meta = "✅ OK" if meta.get("is_valid") else "🛠️ Needs Attention"
    lines.append(f"- **Metadata (metadata.txt)**: {status_meta}")
    if not meta.get("is_valid"):
        lines.append(f"  - Missing fields: `{', '.join(meta.get('missing', []))}`")

    return lines


def _build_markdown_semantic_section(semantic: Dict[str, Any]) -> List[str]:
    """Builds the semantic analysis section (circular imports, resources).

    Args:
        semantic: The semantic analysis dictionary.

    Returns:
        A list of Markdown lines for the semantic section.
    """
    lines = ["\n## 🧠 Semantic Analysis"]
    cycles = semantic.get("circular_dependencies", [])
    missing_res = semantic.get("missing_resources", [])

    if cycles:
        lines.append("🔴 **Circular Import Cycles Detected:**")
        for cycle in cycles:
            lines.append(f"  - `{' -> '.join(cycle)}`")
    else:
        lines.append("- No circular imports detected.")

    if missing_res:
        lines.append(
            f"\n🟡 **Missing Resources**: {len(missing_res)} found (used in code but not in QRC)"
        )
        for res in missing_res[:10]:
            lines.append(f"  - `{res}`")
        if len(missing_res) > 10:
            lines.append(f"  - ... ({len(missing_res) - 10} more)")
    else:
        lines.append("- All resource paths validated.")

    return lines


def _build_markdown_repo_standards(analyses: Dict[str, Any]) -> List[str]:
    """Builds the official repository standards compliance section.

    Args:
        analyses: The full analysis results dictionary.

    Returns:
        A list of Markdown lines for the repository standards section.
    """
    lines = ["\n## 📦 Official Repository Standards"]
    compliance = analyses.get("qgis_compliance", {})
    repo_stats = compliance.get("repository_standards", {})
    struct = repo_stats.get("structure", {})
    status = "✅ OK" if struct.get("is_valid") else "❌ Incomplete"
    lines.append(f"- **File Structure**: {status}")

    if not struct.get("is_valid"):
        missing_files = [f for f, found in struct.get("files", {}).items() if not found]
        if missing_files:
            lines.append(f"  - Missing: `{', '.join(missing_files)}`")
        if not struct.get("has_class_factory"):
            lines.append("  - Missing `classFactory` in `__init__.py`")

    meta = repo_stats.get("metadata", {})
    status_meta = "✅ OK" if meta.get("is_valid") else "🛠️ Needs Attention"
    lines.append(f"- **Metadata (metadata.txt)**: {status_meta}")
    if not meta.get("is_valid"):
        lines.append(f"  - Missing fields: `{', '.join(meta.get('missing', []))}`")

    return lines


def _build_markdown_research_metrics(research: Dict[str, Any]) -> List[str]:
    """Builds the research-based metrics section.

    Args:
        research: The research summary dictionary.

    Returns:
        A list of Markdown lines for the research metrics section.
    """
    if not research:
        return []

    lines = [
        "\n## 🔬 Research-based Metrics",
        f"- **Type Hint Coverage (Params)**: {research.get('type_hint_coverage')}% (Microsoft/Dropbox Std)",
        f"- **Type Hint Coverage (Returns)**: {research.get('return_hint_coverage')}%",
        f"- **Docstring Coverage**: {research.get('docstring_coverage')}% (PEP 257)",
    ]
    styles = ", ".join(research.get("detected_docstring_styles", [])) or "PEP 257 (Default)"
    lines.append(f"- **Detected Documentation Style**: {styles}")
    return lines


def _build_markdown_general_metrics(metrics: Dict[str, Any]) -> List[str]:
    """Builds the general metrics section.

    Args:
        metrics: The metrics dictionary.

    Returns:
        A list of Markdown lines for the general metrics section.
    """
    lines = ["\n## 📊 General Metrics"]
    for k, v in metrics.items():
        if k not in ["quality_score", "maintainability_score", "overall_score"]:
            lines.append(f"- **{k.replace('_', ' ').title()}**: {v}")
    return lines


def _build_markdown_security_section(security: Dict[str, Any]) -> List[str]:
    """Builds the security analysis section with findings.

    Args:
        security: The security analysis dictionary.

    Returns:
        A list of Markdown lines for the security section.
    """
    lines = ["\n## 🛡️ Security Analysis"]
    findings = security.get("findings", [])
    score = security.get("score", 0)

    lines.append(f"Security score: `{score}/100` (Based on AST and secret scanning)")
    lines.append(f"Detected **{len(findings)}** potential security risks.")

    if not findings:
        lines.append("- ✅ No security vulnerabilities detected.")
    else:
        for finding in findings:
            severity = finding.get("severity", "medium").upper()
            icon = "🛑" if severity == "HIGH" else "⚠️"
            lines.append(
                f"- {icon} **[{severity}]** `{finding.get('file')}:{finding.get('line')}`: {finding.get('message')}"
            )
            if finding.get("code"):
                lines.append(f"  - Code: `{finding.get('code')}`")

    return lines


def generate_markdown_summary(analyses: Dict[str, Any], output_path: pathlib.Path) -> None:
    """Generates a professional PROJECT_SUMMARY.md report.

    Args:
        analyses: The full analysis results dictionary.
        output_path: Path where the Markdown file will be saved.
    """
    metrics = analyses["metrics"]
    research = analyses.get("research_summary", {})
    project_type = analyses.get("project_type", "qgis")

    with open(output_path, "w", encoding="utf-8") as f:
        # Re-use header and quality scores
        f.write(
            "\n".join(
                _build_markdown_header(
                    analyses,
                    metrics.get("quality_score", 0),
                    metrics.get("maintainability_score", 0),
                    project_type,
                )
            )
        )
        f.write("\n")

        # Research-based metrics
        if research:
            research_lines = _build_markdown_research_metrics(research)
            f.write("\n".join(research_lines))
            f.write("\n")

        # General metrics
        general_metrics_lines = _build_markdown_general_metrics(metrics)
        f.write("\n".join(general_metrics_lines))
        f.write("\n")

        # QGIS-specific findings
        if project_type == "qgis":
            qgis_findings_lines = _build_markdown_qgis_findings(analyses)
            f.write("\n".join(qgis_findings_lines))

        # Semantic analysis
        semantic = analyses.get("semantic", {})
        if semantic:
            semantic_lines = _build_markdown_semantic_section(semantic)
            f.write("\n".join(semantic_lines))

        # Security analysis
        security = analyses.get("security", {})
        if security:
            security_lines = _build_markdown_security_section(security)
            f.write("\n".join(security_lines))

        # Repository standards (QGIS only)
        if project_type == "qgis":
            repo_standards_lines = _build_markdown_repo_standards(analyses)
            f.write("\n".join(repo_standards_lines))


def save_json_context(analyses: Dict[str, Any], output_path: pathlib.Path) -> None:
    """Saves the full context in JSON format.

    Args:
        analyses: The full analysis results dictionary.
        output_path: Path where the JSON file will be saved.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analyses, f, indent=2, ensure_ascii=False)
