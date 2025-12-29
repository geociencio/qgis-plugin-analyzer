# /***************************************************************************
#  QGIS Plugin Analyzer
#                                  A QGIS tool
#  Static code analysis and standards audit for QGIS plugins.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import datetime
import json
import pathlib
from typing import Any, Dict

import dominate
from dominate.tags import b, br, div, h1, h2, li, p, pre, span, style, ul


def generate_markdown_summary(analyses: Dict[str, Any], output_path: pathlib.Path):
    """Generates a professional PROJECT_SUMMARY.md report."""
    metrics = analyses.get("metrics", {})
    compliance = analyses.get("qgis_compliance", {})
    score = metrics.get("quality_score", 0)
    qgis_score = compliance.get("compliance_score", 0)

    lines = [
        f"# 📋 Project Analysis Report: {analyses.get('project_name', 'QGIS Plugin')}",
        f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "## 📊 Quality Indicators",
        f"- **Code Score**: `{score}/100`",
        f"- **QGIS Compliance**: `{qgis_score}/100`",
        "",
    ]
    # Technical findings
    best_practices = compliance.get("best_practices", {})
    lines.append("## 🛠️ QGIS Standard Findings")
    lines.append(f"Detected **{best_practices.get('issues_count', 0)}** technical deviations.")

    for issue in best_practices.get("issues", []):
        icon = "🔴" if issue["severity"] == "high" else "🟡"
        lines.append(f"- {icon} `{issue['file']}:{issue['line']}`: {issue['message']}")

    # Repository Audit
    repo_stats = compliance.get("repository_standards", {})
    lines.append("\n## 📦 Official Repository Standards")

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

    lines.append("\n## 📈 General Metrics")
    for k, v in metrics.items():
        if k != "quality_score":
            lines.append(f"- **{k.replace('_', ' ').title()}**: {v}")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def save_json_context(analyses: Dict[str, Any], output_path: pathlib.Path):
    """Saves the full context in JSON format."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analyses, f, indent=2, ensure_ascii=False)


def generate_html_report(analyses: Dict[str, Any], output_path: pathlib.Path):
    """Generates a professional HTML report using dominate."""
    metrics = analyses.get("metrics", {})
    compliance = analyses.get("qgis_compliance", {})
    ruff_findings = analyses.get("ruff_findings", [])

    doc = dominate.document(title=f"Analysis Report - {analyses.get('project_name')}")

    with doc.head:
        style("""
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f4f7f9; }
            .header { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .score-container { display: flex; gap: 20px; margin-top: 20px; }
            .score-box { flex: 1; text-align: center; padding: 15px; border-radius: 8px; background: #ecf0f1; border-bottom: 4px solid #bdc3c7; }
            .score-box.high { border-color: #27ae60; }
            .score-box.medium { border-color: #f1c40f; }
            .score-box.low { border-color: #e74c3c; }
            .score-value { font-size: 2em; font-weight: bold; display: block; }
            .issue { border-left: 4px solid #eee; padding-left: 15px; margin-bottom: 10px; }
            .issue.high { border-color: #e74c3c; }
            .issue.medium { border-color: #f1c40f; }
            .severity { font-weight: bold; text-transform: uppercase; font-size: 0.8em; }
            .file-path { color: #7f8c8d; font-size: 0.9em; }
            code { background: #f8f9fa; padding: 2px 4px; border-radius: 4px; font-size: 0.9em; }
            pre { background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 5px; overflow-x: auto; }
            h2 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        """)

    with doc:
        with div(cls="header"):
            h1(f"📊 QGIS Plugin Analysis: {analyses.get('project_name')}")
            p(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            with div(cls="score-container"):
                q_score = metrics.get("quality_score", 0)
                cls_q = "high" if q_score >= 80 else "medium" if q_score >= 50 else "low"
                with div(cls=f"score-box {cls_q}"):
                    span("Overall Score", cls="score-label")
                    span(f"{q_score}/100", cls="score-value")

                c_score = compliance.get("compliance_score", 0)
                cls_c = "high" if c_score >= 80 else "medium" if c_score >= 50 else "low"
                with div(cls=f"score-box {cls_c}"):
                    span("QGIS Compliance", cls="score-label")
                    span(f"{c_score}/100", cls="score-value")

        with div(cls="card"):
            h2("🛠️ QGIS Standard Findings")
            best_practices = compliance.get("best_practices", {})
            if not best_practices.get("issues"):
                p("✅ No major QGIS standard deviations found.")
            else:
                for issue in best_practices.get("issues"):
                    with div(cls=f"issue {issue['severity']}"):
                        span(issue["severity"], cls="severity")
                        span(f" - {issue['message']}")
                        br()
                        span(f"{issue['file']}:{issue['line']}", cls="file-path")
                        if issue.get("code"):
                            pre(issue["code"])

        if ruff_findings:
            with div(cls="card"):
                h2("🐍 Python Linting (Ruff)")
                for find in ruff_findings[:50]:  # Limit to 50 for report
                    with div(cls="issue medium"):
                        span(find.get("code", "LINT"), cls="severity")
                        span(f" - {find.get('message')}")
                        br()
                        span(
                            f"{find.get('filename')}:{find.get('location', {}).get('row', 0)}",
                            cls="file-path",
                        )

        with div(cls="card"):
            h2("📈 General Metrics")
            with ul():
                for k, v in metrics.items():
                    if k != "quality_score":
                        li(b(k.replace("_", " ").title()), f": {v}")

    output_path.write_text(doc.render(), encoding="utf-8")
