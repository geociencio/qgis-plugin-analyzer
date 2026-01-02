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


def generate_markdown_summary(analyses: Dict[str, Any], output_path: pathlib.Path):
    """Generates a professional PROJECT_SUMMARY.md report."""
    metrics = analyses.get("metrics", {})
    project_type = analyses.get("project_type", "qgis")
    score = metrics.get("quality_score", 0)

    project_label = "QGIS Plugin" if project_type == "qgis" else "Python Project"

    lines = [
        f"# 📋 Project Analysis Report: {analyses.get('project_name', project_label)}",
        f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "## 📊 Quality Indicators",
        f"- **Overall Quality Score**: `{score}/100`",
    ]

    if project_type == "qgis":
        compliance = analyses.get("qgis_compliance", {})
        qgis_score = compliance.get("compliance_score", 0)
        lines.append(f"- **QGIS Compliance**: `{qgis_score}/100`")

    lines.append("")
    if project_type == "qgis":
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

    # Semantic Findings
    semantic = analyses.get("semantic", {})
    cycles = semantic.get("circular_dependencies", [])
    missing_res = semantic.get("missing_resources", [])

    lines.append("\n## 🧠 Semantic Analysis")
    if cycles:
        lines.append("🔴 **Circular Import Cycles Detected:**")
        for cycle in cycles:
            lines.append(f"  - `{' -> '.join(cycle)}`")
    else:
        lines.append("- No circular imports detected.")

    if missing_res:
         lines.append(f"\n🟡 **Missing Resources**: {len(missing_res)} found (used in code but not in QRC)")
         for res in missing_res[:10]:
             lines.append(f"  - `{res}`")
         if len(missing_res) > 10:
             lines.append(f"  - ... ({len(missing_res) - 10} more)")
    else:
        lines.append("- All resource paths validated.")

    if project_type == "qgis":
        lines.append("\n## 📦 Official Repository Standards")
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
    """Generates a professional HTML report without external dependencies."""
    metrics = analyses.get("metrics", {})
    ruff_findings = analyses.get("ruff_findings", [])
    project_type = analyses.get("project_type", "qgis")
    project_label = "QGIS Plugin" if project_type == "qgis" else "Python"
    project_name = analyses.get("project_name", project_label)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    q_score = metrics.get("quality_score", 0)
    cls_q = "high" if q_score >= 80 else "medium" if q_score >= 50 else "low"

    c_score = 0
    cls_c = "low"
    if project_type == "qgis":
        compliance = analyses.get("qgis_compliance", {})
        c_score = compliance.get("compliance_score", 0)
        cls_c = "high" if c_score >= 80 else "medium" if c_score >= 50 else "low"

    html = [
        "<!DOCTYPE html>",
        f"<html><head><meta charset='utf-8'><title>Analysis Report - {project_name}</title>",
        "<style>",
        "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f4f7f9; }",
        ".header { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }",
        ".card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }",
        ".score-container { display: flex; gap: 20px; margin-top: 20px; }",
        ".score-box { flex: 1; text-align: center; padding: 15px; border-radius: 8px; background: #ecf0f1; border-bottom: 4px solid #bdc3c7; }",
        ".score-box.high { border-color: #27ae60; }",
        ".score-box.medium { border-color: #f1c40f; }",
        ".score-box.low { border-color: #e74c3c; }",
        ".score-value { font-size: 2em; font-weight: bold; display: block; }",
        ".issue { border-left: 4px solid #eee; padding-left: 15px; margin-bottom: 10px; }",
        ".issue.high { border-color: #e74c3c; }",
        ".issue.medium { border-color: #f1c40f; }",
        ".severity { font-weight: bold; text-transform: uppercase; font-size: 0.8em; }",
        ".file-path { color: #7f8c8d; font-size: 0.9em; }",
        "code { background: #f8f9fa; padding: 2px 4px; border-radius: 4px; font-size: 0.9em; }",
        "pre { background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 5px; overflow-x: auto; }",
        "h2 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }",
        "</style></head><body>",
        "<div class='header'>",
        f"<h1>📊 {project_label} Analysis: {project_name}</h1>",
        f"<p>Generated on: {now}</p>",
        "<div class='score-container'>",
        f"<div class='score-box {cls_q}'><span class='score-label'>Overall Score</span><span class='score-value'>{q_score}/100</span></div>"
    ]

    if project_type == "qgis":
        html.append(f"<div class='score-box {cls_c}'><span class='score-label'>QGIS Compliance</span><span class='score-value'>{c_score}/100</span></div>")

    html.extend([
        "</div></div>"
    ])

    if project_type == "qgis":
        html.append("<div class='card'><h2>🛠️ QGIS Standard Findings</h2>")
        compliance = analyses.get("qgis_compliance", {})
        best_practices = compliance.get("best_practices", {})
        issues = best_practices.get("issues", [])
        if not issues:
            html.append("<p>✅ No major QGIS standard deviations found.</p>")
        else:
            for issue in issues:
                severity = issue.get("severity", "medium")
                html.append(f"<div class='issue {severity}'>")
                html.append(f"<span class='severity'>{severity}</span> - {issue['message']}<br>")
                html.append(f"<span class='file-path'>{issue['file']}:{issue['line']}</span>")
                if issue.get("code"):
                    html.append(f"<pre>{issue['code']}</pre>")
                html.append("</div>")
        html.append("</div>")

    # Semantic Section
    semantic = analyses.get("semantic", {})
    if semantic:
        html.append("<div class='card'><h2>🧠 Semantic Analysis</h2>")

        # Circular Imports
        cycles = semantic.get("circular_dependencies", [])
        if cycles:
            html.append(f"<div class='issue high'><b>Circular Dependencies Detected:</b> {len(cycles)}<br>")
            html.append("<ul>")
            for cycle in cycles:
                html.append(f"<li><code>{' -> '.join(cycle)}</code></li>")
            html.append("</ul></div>")

        # Missing Resources
        missing_res = semantic.get("missing_resources", [])
        if missing_res:
            html.append(f"<div class='issue medium'><b>Missing Resources:</b> {len(missing_res)} (Defined in code but missing in QRC)<br>")
            html.append("<ul>")
            for res in missing_res[:10]:
                html.append(f"<li>{res}</li>")
            if len(missing_res) > 10:
                html.append(f"<li>... ({len(missing_res) - 10} more)</li>")
            html.append("</ul></div>")

        # Coupling Metrics Table
        metrics = semantic.get("coupling_metrics", {})
        if metrics:
            html.append("<h3>Module Coupling</h3>")
            html.append("<table style='width:100%; border-collapse: collapse;'><thead><tr style='background:#eee;'><th>Module</th><th>Fan-In (Incoming)</th><th>Fan-Out (Outgoing)</th></tr></thead><tbody>")
            for mod, vals in sorted(metrics.items(), key=lambda x: x[1]['fan_in'], reverse=True)[:10]:
                 html.append(f"<tr><td style='border:1px solid #ddd; padding:8px;'>{mod}</td><td style='border:1px solid #ddd; padding:8px;'>{vals['fan_in']}</td><td style='border:1px solid #ddd; padding:8px;'>{vals['fan_out']}</td></tr>")
            html.append("</tbody></table>")

        html.append("</div>")

    # Repository Compliance
    repo_comp = analyses.get("repository_compliance", {})
    if repo_comp:
        is_compliant = repo_comp.get("is_compliant", False)
        status_icon = "✅" if is_compliant else "⚠️"

        html.append(f"<div class='card'><h2>{status_icon} Repository Compliance</h2>")

        # Binaries
        binaries = repo_comp.get("binaries", [])
        if binaries:
            html.append(f"<div class='issue high'><b>Prohibited Binaries Detected:</b> {len(binaries)}</div>")
            html.append("<ul>")
            for binary in binaries[:10]:
                html.append(f"<li><code>{binary}</code></li>")
            if len(binaries) > 10:
                html.append(f"<li>... ({len(binaries) - 10} more)</li>")
            html.append("</ul>")
        else:
            html.append("<div class='info'>✅ No prohibited binaries found</div>")

        # Package Size
        package_size = repo_comp.get("package_size_mb", 0)
        if package_size > 20:
            html.append(f"<div class='issue medium'><b>Package Size:</b> {package_size:.2f} MB (exceeds 20MB limit)</div>")
        else:
            html.append(f"<div class='info'><b>Package Size:</b> {package_size:.2f} MB</div>")

        # URL Validation
        url_status = repo_comp.get("url_validation", {})
        if url_status:
            ok_count = sum(1 for status in url_status.values() if status == "ok")
            total = len(url_status)
            if ok_count == total:
                html.append(f"<div class='info'>✅ <b>URL Validation:</b> All {total} links working</div>")
            else:
                html.append(f"<div class='issue medium'><b>URL Validation:</b> {ok_count}/{total} links working</div>")
                html.append("<ul>")
                for url, status in url_status.items():
                    if status != "ok":
                        html.append(f"<li>{url}: <code>{status}</code></li>")
                html.append("</ul>")

        html.append("</div>")

    if ruff_findings:
        html.append("<div class='card'><h2>🐍 Python Linting (Ruff)</h2>")
        for find in ruff_findings[:50]:
            html.append("<div class='issue medium'>")
            html.append(f"<span class='severity'>{find.get('code', 'LINT')}</span> - {find.get('message')}<br>")
            html.append(f"<span class='file-path'>{find.get('filename')}:{find.get('location', {}).get('row', 0)}</span>")
            html.append("</div>")
        html.append("</div>")

    html.append("<div class='card'><h2>📈 General Metrics</h2><ul>")
    for k, v in metrics.items():
        if k != "quality_score":
            html.append(f"<li><b>{k.replace('_', ' ').title()}</b>: {v}</li>")
    html.append("</ul></div></body></html>")

    output_path.write_text("\n".join(html), encoding="utf-8")
