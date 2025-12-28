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

import json
import datetime
import pathlib
from typing import Any, Dict

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
    lines.append(f"## 🛠️ QGIS Standard Findings")
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
        if missing_files: lines.append(f"  - Missing: `{', '.join(missing_files)}`")
        if not struct.get("has_class_factory"): lines.append("  - Missing `classFactory` in `__init__.py`")

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
