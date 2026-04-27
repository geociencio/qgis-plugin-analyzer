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

import pathlib
from typing import Any, Dict, List, Optional, Set, TypedDict, cast

from .reporters import (
    generate_html_report,
    generate_markdown_summary,
    save_json_context,
)
from .scanner import ModuleAnalysisResult
from .scoring import (
    ProjectScores,
    QGISChecksResult,
    SemanticAnalysisResult,
)


class FullAnalysisResult(TypedDict, total=False):
    """Consolidated analysis result for the entire project."""

    project_name: str
    project_type: str
    metrics: Dict[str, Any]
    ruff_findings: List[Dict[str, Any]]
    security: Dict[str, Any]
    semantic: Dict[str, Any]
    modules: List[ModuleAnalysisResult]
    research_summary: Dict[str, Any]
    qgis_compliance: Dict[str, Any]
    repository_compliance: Dict[str, Any]
    ruff_metadata: Dict[str, Any]


def get_metrics_summary(
    files: List[pathlib.Path],
    modules_data: List[ModuleAnalysisResult],
    scores: ProjectScores,
) -> Dict[str, Any]:
    """Generates the metrics summary portion of the results."""
    return {
        "total_files": len(files),
        "total_lines": sum(m["lines"] for m in modules_data),
        "quality_score": round(scores["code_score"], 1),
        "maintainability_score": round(scores["maint_score"], 1),
        "security_score": round(scores["security_score"], 1),
    }


def get_security_summary(
    modules_data: List[ModuleAnalysisResult], scores: ProjectScores
) -> Dict[str, Any]:
    """Generates the security summary portion of the results."""
    all_security_issues = []
    for m in modules_data:
        all_security_issues.extend(m.get("security_issues", []))

    return {
        "findings": all_security_issues,
        "count": len(all_security_issues),
        "score": round(scores["security_score"], 1),
    }


def get_research_summary(modules_data: List[ModuleAnalysisResult]) -> Dict[str, Any]:
    """Aggregates research metrics for summary."""
    total_functions = 0
    total_params = 0
    annotated_params = 0
    has_return_hint = 0
    has_docstring_count = 0
    total_public_items = 0
    detected_styles = set()

    # QGIS context aggregation
    gdal_styles: Dict[str, int] = {}
    pyqt_versions: Dict[str, int] = {"PyQt5": 0, "PyQt6": 0}
    processing_usage = False
    total_legacy_signals = 0
    all_signal_leaks: Set[str] = set()

    for m in modules_data:
        r_metrics = m.get("research_metrics", {})
        d_stats = r_metrics.get("docstring_stats", {})
        total_public_items += d_stats.get("total_public_items", 0)
        has_docstring_count += d_stats.get("has_docstring", 0)

        t_stats = r_metrics.get("type_hint_stats", {})
        total_functions += t_stats.get("total_functions", 0)
        total_params += t_stats.get("total_parameters", 0)
        annotated_params += t_stats.get("annotated_parameters", 0)
        has_return_hint += t_stats.get("has_return_hint", 0)

        detected_styles.update(r_metrics.get("docstring_styles", []))

        # QGIS Context
        q_ctx = r_metrics.get("qgis_context", {})
        style = q_ctx.get("gdal_style", "Modern")
        gdal_styles[style] = gdal_styles.get(style, 0) + 1

        p_trans = q_ctx.get("pyqt_transition", {})
        if p_trans.get("PyQt5"):
            pyqt_versions["PyQt5"] += 1
        if p_trans.get("PyQt6"):
            pyqt_versions["PyQt6"] += 1

        if q_ctx.get("processing_framework"):
            processing_usage = True

        total_legacy_signals += q_ctx.get("legacy_signals_count", 0)
        all_signal_leaks.update(q_ctx.get("signal_leaks", []))

    return {
        "type_hint_coverage": (
            round((annotated_params / max(1, total_params)) * 100, 1)
            if total_params > 0
            else 0.0
        ),
        "return_hint_coverage": (
            round((has_return_hint / total_functions) * 100, 1)
            if total_functions > 0
            else 0.0
        ),
        "docstring_coverage": (
            round((has_docstring_count / max(1, total_public_items)) * 100, 1)
            if total_public_items > 0
            else 0.0
        ),
        "detected_docstring_styles": sorted(list(detected_styles)),
        "qgis_context_summary": {
            "gdal_styles": gdal_styles,
            "pyqt_usage": pyqt_versions,
            "uses_processing": processing_usage,
            "total_legacy_signals": total_legacy_signals,
            "signal_leaks": sorted(list(all_signal_leaks)),
        },
    }


def build_analysis_results(
    project_path: pathlib.Path,
    project_type: str,
    files: List[pathlib.Path],
    modules_data: List[ModuleAnalysisResult],
    ruff_findings: List[Dict[str, Any]],
    scores: ProjectScores,
    qgis_checks: Optional[QGISChecksResult],
    semantic: SemanticAnalysisResult,
) -> FullAnalysisResult:
    """Consolidates analysis results into a single dictionary."""
    analyses: FullAnalysisResult = {
        "project_name": project_path.name,
        "project_type": project_type,
        "metrics": get_metrics_summary(files, modules_data, scores),
        "ruff_findings": ruff_findings,
        "security": get_security_summary(modules_data, scores),
        "semantic": {
            "circular_dependencies": semantic["cycles"],
            "coupling_metrics": semantic["metrics"],
        },
        "modules": modules_data,
        "research_summary": get_research_summary(modules_data),
    }

    if project_type == "qgis" and qgis_checks:
        analyses["metrics"]["overall_score"] = round(
            (scores["code_score"] * 0.5) + (scores["qgis_score"] * 0.5), 1
        )
        analyses["qgis_compliance"] = {
            "compliance_score": round(scores["qgis_score"], 1),
            "best_practices": qgis_checks["compliance"],
            "repository_standards": {
                "structure": qgis_checks["structure"],
                "metadata": qgis_checks["metadata"],
            },
        }
        analyses["semantic"]["missing_resources"] = semantic["missing_resources"]
        analyses["repository_compliance"] = {
            "binaries": qgis_checks["binaries"],
            "package_size_mb": round(qgis_checks["package_size"], 2),
            "url_validation": qgis_checks["url_status"],
            "folder_name_valid": qgis_checks["structure"].get(
                "folder_name_valid", True
            ),
            "constraint_errors": qgis_checks["package_constraints"].get("errors", []),
            "is_compliant": qgis_checks["package_constraints"].get("is_valid", True)
            and qgis_checks["structure"].get("is_valid", True),
        }
        analyses["ruff_metadata"] = (
            ruff_findings.get("metadata", {}) if isinstance(ruff_findings, dict) else {}
        )

    return analyses


def save_reports(
    analyses: FullAnalysisResult, output_dir: pathlib.Path, generate_html: bool = True
) -> None:
    """Saves all generated analysis reports to the output directory.

    Args:
        analyses: The consolidated analysis results dictionary.
        output_dir: Directory where reports will be saved.
        generate_html: Whether to generate the HTML report.
    """
    data = cast(Dict[str, Any], analyses)
    generate_markdown_summary(data, output_dir / "PROJECT_SUMMARY.md")
    if generate_html:
        generate_html_report(data, output_dir / "PROJECT_SUMMARY.html")
    save_json_context(data, output_dir / "project_context.json")
