"""HTML reporter for project analysis results.

This module provides functions to generate professional HTML reports
of the analysis findings, with a clean and responsive design.
"""

import datetime
import pathlib
from typing import Any, Dict, List


def _get_html_styles() -> List[str]:
    """Returns the CSS styles for the HTML report.

    Returns:
        A list of HTML <style> block lines.
    """
    return [
        "<style>",
        "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f4f7f9; }",
        ".header { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }",
        ".card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }",
        ".score-container { display: flex; gap: 20px; margin-top: 20px; }",
        ".score-box { flex: 1; text-align: center; padding: 15px; border-radius: 8px; background: #ecf0f1; border-bottom: 4px solid #bdc3c7; color: #2c3e50; }",
        ".score-box.high { border-color: #27ae60; }",
        ".score-box.medium { border-color: #f1c40f; }",
        ".score-box.low { border-color: #e74c3c; }",
        ".score-label { display: block; font-size: 0.9em; font-weight: bold; margin-bottom: 5px; }",
        ".score-value { font-size: 2em; font-weight: bold; display: block; }",
        ".issue { border-left: 4px solid #eee; padding-left: 15px; margin-bottom: 10px; }",
        ".issue.high { border-color: #e74c3c; }",
        ".issue.medium { border-color: #f1c40f; }",
        ".severity { font-weight: bold; text-transform: uppercase; font-size: 0.8em; }",
        ".file-path { color: #7f8c8d; font-size: 0.9em; }",
        "code { background: #f8f9fa; padding: 2px 4px; border-radius: 4px; font-size: 0.9em; }",
        "pre { background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 5px; overflow-x: auto; }",
        "h2 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }",
        ".section { margin-bottom: 30px; }",
        ".metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }",
        ".metric-card { background: #f0f4f7; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }",
        ".metric-label { display: block; font-size: 0.9em; color: #555; margin-bottom: 5px; }",
        ".metric-value { font-size: 1.8em; font-weight: bold; color: #2c3e50; }",
        "</style></head><body>",
    ]


def _build_html_header(
    project_name: str,
    project_label: str,
    now: str,
    q_score: float,
    m_score: float,
    cls_q: str,
    cls_m: str,
    c_score: float,
    cls_c: str,
    project_type: str,
) -> str:
    """Builds the HTML header section including quality scores.

    Args:
        project_name: Name of the project.
        project_label: Label describing project type.
        now: Current timestamp string.
        q_score: Module stability score.
        m_score: Maintainability score.
        cls_q: CSS class for quality score.
        cls_m: CSS class for maintainability score.
        c_score: QGIS compliance score.
        cls_c: CSS class for compliance score.
        project_type: Project type ID.

    Returns:
        The HTML string for the header.
    """
    html = [
        "<!DOCTYPE html>",
        f"<html><head><meta charset='utf-8'><title>Analysis Report - {project_name}</title>",
    ]
    html.extend(_get_html_styles())
    html.extend(
        [
            "<div class='header'>",
            f"<h1>📊 {project_label} Analysis: {project_name}</h1>",
            f"<p>Generated on: {now}</p>",
            "<div class='score-container'>",
            f"<div class='score-box {cls_q}'><span class='score-label'>Module Stability</span><span class='score-value'>{q_score}/100</span></div>",
            f"<div class='score-box {cls_m}'><span class='score-label'>Maintainability</span><span class='score-value'>{m_score}/100</span></div>",
        ]
    )

    if project_type == "qgis":
        html.append(
            f"<div class='score-box {cls_c}'><span class='score-label'>QGIS Compliance</span><span class='score-value'>{c_score}/100</span></div>"
        )

    html.append("</div></div>")
    return "".join(html)


def _build_html_qgis_findings(analyses: Dict[str, Any]) -> str:
    """Builds the QGIS standard findings section for HTML.

    Args:
        analyses: The full analysis results dictionary.

    Returns:
        The HTML string for the findings section.
    """
    html = ["<div class='card'><h2>🛠️ QGIS Standard Findings</h2>"]
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
    return "".join(html)


def _build_html_semantic_section(semantic: Dict[str, Any]) -> str:
    """Builds the semantic analysis HTML section (cycles, coupling).

    Args:
        semantic: The semantic analysis results dictionary.

    Returns:
        The HTML string for the semantic section.
    """
    html = ["<div class='card'><h2>🧠 Semantic Analysis</h2>"]

    cycles = semantic.get("circular_dependencies", [])
    if cycles:
        html.append(
            f"<div class='issue high'><b>Circular Dependencies Detected:</b> {len(cycles)}<br>"
        )
        html.append("<ul>")
        for cycle in cycles:
            html.append(f"<li><code>{' -> '.join(cycle)}</code></li>")
        html.append("</ul></div>")

    missing_res = semantic.get("missing_resources", [])
    if missing_res:
        html.append(
            f"<div class='issue medium'><b>Missing Resources:</b> {len(missing_res)} (Defined in code but missing in QRC)<br>"
        )
        html.append("<ul>")
        for res in missing_res[:10]:
            html.append(f"<li>{res}</li>")
        if len(missing_res) > 10:
            html.append(f"<li>... ({len(missing_res) - 10} more)</li>")
        html.append("</ul></div>")

    metrics = semantic.get("coupling_metrics", {})
    if metrics:
        html.append("<h3>Module Coupling</h3>")
        html.append(
            "<table style='width:100%; border-collapse: collapse;'><thead><tr style='background:#eee;'><th>Module</th><th>Fan-In (Incoming)</th><th>Fan-Out (Outgoing)</th></tr></thead><tbody>"
        )
        for mod, vals in sorted(metrics.items(), key=lambda x: x[1]["fan_in"], reverse=True)[:10]:
            html.append(
                f"<tr><td style='border:1px solid #ddd; padding:8px;'>{mod}</td><td style='border:1px solid #ddd; padding:8px;'>{vals['fan_in']}</td><td style='border:1px solid #ddd; padding:8px;'>{vals['fan_out']}</td></tr>"
            )
        html.append("</tbody></table>")

    html.append("</div>")
    return "".join(html)


def _build_html_repo_compliance(repo_comp: Dict[str, Any]) -> str:
    """Builds the repository compliance HTML section.

    Args:
        repo_comp: The repository compliance results dictionary.

    Returns:
        The HTML string for the repository compliance section.
    """
    is_compliant = repo_comp.get("is_compliant", False)
    status_icon = "✅" if is_compliant else "⚠️"
    html = [f"<div class='card'><h2>{status_icon} Repository Compliance</h2>"]

    binaries = repo_comp.get("binaries", [])
    if binaries:
        html.append(
            f"<div class='issue high'><b>Prohibited Binaries Detected:</b> {len(binaries)}</div>"
        )
        html.append("<ul>")
        for binary in binaries[:10]:
            html.append(f"<li><code>{binary}</code></li>")
        if len(binaries) > 10:
            html.append(f"<li>... ({len(binaries) - 10} more)</li>")
        html.append("</ul>")
    else:
        html.append("<div class='info'>✅ No prohibited binaries found</div>")

    package_size = repo_comp.get("package_size_mb", 0)
    if package_size > 20:
        html.append(
            f"<div class='issue medium'><b>Package Size:</b> {package_size:.2f} MB (exceeds 20MB limit)</div>"
        )
    else:
        html.append(f"<div class='info'><b>Package Size:</b> {package_size:.2f} MB</div>")

    url_status = repo_comp.get("url_validation", {})
    if url_status:
        ok_count = sum(1 for status in url_status.values() if status == "ok")
        total = len(url_status)
        if ok_count == total:
            html.append(
                f"<div class='info'>✅ <b>URL Validation:</b> All {total} links working</div>"
            )
        else:
            html.append(
                f"<div class='issue medium'><b>URL Validation:</b> {ok_count}/{total} links working</div>"
            )
            html.append("<ul>")
            for url, status in url_status.items():
                if status != "ok":
                    html.append(f"<li>{url}: <code>{status}</code></li>")
            html.append("</ul>")

    html.append("</div>")
    return "".join(html)


def _build_html_ruff_findings(ruff_findings: List[Dict[str, Any]]) -> str:
    """Builds the Ruff findings HTML section.

    Args:
        ruff_findings: List of Ruff finding dictionaries.

    Returns:
        The HTML string for the Ruff section.
    """
    html = ["<div class='card'><h2>🐍 Python Linting (Ruff)</h2>"]
    for find in ruff_findings[:50]:
        html.append("<div class='issue medium'>")
        html.append(
            f"<span class='severity'>{find.get('code', 'LINT')}</span> - {find.get('message')}<br>"
        )
        html.append(
            f"<span class='file-path'>{find.get('filename')}:{find.get('location', {}).get('row', 0)}</span>"
        )
        html.append("</div>")
    html.append("</div>")
    return "".join(html)


def _build_html_research_section(research_summary: Dict[str, Any]) -> str:
    """Builds the research-based metrics HTML section.

    Args:
        research_summary: The research summary dictionary.

    Returns:
        The HTML string for the modernization section.
    """
    if not research_summary:
        return ""

    styles = ", ".join(research_summary.get("detected_docstring_styles", [])) or "PEP 257 (Default)"
    th_cov = research_summary.get("type_hint_coverage", 0)
    ds_cov = research_summary.get("docstring_coverage", 0)
    ret_cov = research_summary.get("return_hint_coverage", 0)

    return f"""
    <div class="section card">
        <h2>🔬 Research-based Modernization</h2>
        <p style="color: #7f8c8d; margin-bottom: 15px;">Metrics inspired by Google, Microsoft, and PSF standards.</p>
        <div class="metrics-grid">
            <div class="metric-card">
                <span class="metric-label">Parameters Type Hints</span>
                <span class="metric-value">{th_cov}%</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Return Type Hints</span>
                <span class="metric-value">{ret_cov}%</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Docstring Coverage</span>
                <span class="metric-value">{ds_cov}%</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Detected Style</span>
                <span class="metric-value" style="font-size: 1.2em;">{styles}</span>
            </div>
        </div>
    </div>
    """


def _build_html_general_metrics(metrics: Dict[str, Any]) -> str:
    """Builds the general metrics HTML section.

    Args:
        metrics: The general metrics dictionary.

    Returns:
        The HTML string for the general metrics section.
    """
    html = ["<div class='card'><h2>📈 General Metrics</h2><ul>"]
    for k, v in metrics.items():
        if k not in ["quality_score", "maintainability_score", "overall_score"]:
            html.append(f"<li><b>{k.replace('_', ' ').title()}</b>: {v}</li>")
    html.append("</ul></div>")
    return "".join(html)


def generate_html_report(analyses: Dict[str, Any], output_path: pathlib.Path) -> None:
    """Generates a professional HTML report.

    Args:
        analyses: The full analysis results dictionary.
        output_path: Path where the HTML file will be saved.
    """
    metrics = analyses.get("metrics", {})
    ruff_findings = analyses.get("ruff_findings", [])
    project_type = analyses.get("project_type", "qgis")
    project_label = "QGIS Plugin" if project_type == "qgis" else "Python"
    project_name = analyses.get("project_name", project_label)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    q_score = metrics.get("quality_score", 0)
    cls_q = "high" if q_score >= 80 else "medium" if q_score >= 50 else "low"

    m_score = metrics.get("maintainability_score", 0)
    cls_m = "high" if m_score >= 80 else "medium" if m_score >= 50 else "low"

    c_score = 0
    cls_c = "low"
    if project_type == "qgis":
        compliance = analyses.get("qgis_compliance", {})
        c_score = compliance.get("compliance_score", 0)
        cls_c = "high" if c_score >= 80 else "medium" if c_score >= 50 else "low"

    # Build header and scores
    html_body = _build_html_header(
        project_name,
        project_label,
        now,
        q_score,
        m_score,
        cls_q,
        cls_m,
        c_score,
        cls_c,
        project_type,
    )

    # QGIS Findings
    if analyses.get("qgis_compliance"):
        html_body += _build_html_qgis_findings(analyses)

    # Add research section
    html_body += _build_html_research_section(analyses.get("research_summary", {}))

    # Semantic Section
    semantic = analyses.get("semantic", {})
    if semantic:
        html_body += _build_html_semantic_section(semantic)

    # Repository Compliance
    repo_comp = analyses.get("repository_compliance", {})
    if repo_comp:
        html_body += _build_html_repo_compliance(repo_comp)

    # Ruff Findings
    if ruff_findings:
        html_body += _build_html_ruff_findings(ruff_findings)

    # General Metrics
    html_body += _build_html_general_metrics(metrics)

    # Footer
    html_body += "</body></html>"

    output_path.write_text(html_body, encoding="utf-8")
