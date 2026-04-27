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

import math
from typing import Any, Dict, List, Optional, TypedDict

from .scanner import ModuleAnalysisResult


class QGISChecksResult(TypedDict):
    """Result of QGIS-specific validation checks."""

    compliance: Dict[str, Any]
    structure: Dict[str, Any]
    metadata: Dict[str, Any]
    binaries: List[str]
    package_size: float
    package_constraints: Dict[str, Any]
    url_status: Dict[str, str]


class SemanticAnalysisResult(TypedDict):
    """Result of semantic analysis."""

    cycles: List[List[str]]
    graph: Dict[str, List[str]]
    metrics: Dict[str, Any]
    missing_resources: List[str]


class ProjectScores(TypedDict):
    """Calculated project quality scores."""

    code_score: float
    maint_score: float
    qgis_score: float
    security_score: float


class ScoringEngine:
    """Specialized engine for calculating project quality scores."""

    def __init__(self, project_type: str) -> None:
        self.project_type = project_type

    def calculate_project_scores(
        self,
        modules_data: List[ModuleAnalysisResult],
        ruff_findings: List[Dict[str, Any]],
        qgis_checks: Optional[QGISChecksResult],
        semantic: SemanticAnalysisResult,
    ) -> ProjectScores:
        """Calculates project quality scores based on industry-standard formulas."""
        if not modules_data:
            return {
                "code_score": 0.0,
                "maint_score": 0.0,
                "qgis_score": 0.0,
                "security_score": 0.0,
            }

        module_score = self._get_mi_score(modules_data)
        maintainability_score = self._get_maint_score(modules_data, ruff_findings)
        modernization_bonus = self._get_modernization_bonus(modules_data)

        # Cap modernization bonus: if there are ANY issues, limit to 99.9
        # to ensure it's not a misleading perfect score.
        any_issues = any(m.get("ast_issues") for m in modules_data) or bool(
            ruff_findings
        )
        if any_issues and (maintainability_score + modernization_bonus) >= 100.0:
            maintainability_score = 99.9
        else:
            maintainability_score = min(
                100.0, maintainability_score + modernization_bonus
            )

        # Security context
        security_penalty = self._get_security_penalty(modules_data)
        security_score = max(0.0, 100.0 - security_penalty)

        # Global penalties (e.g., circular dependencies)
        cycles = semantic["cycles"]
        penalty = len(cycles) * 10
        module_score = max(0, module_score - penalty)
        maintainability_score = max(0, maintainability_score - penalty)

        if self.project_type == "generic" or not qgis_checks:
            return {
                "code_score": round(module_score, 1),
                "maint_score": round(maintainability_score, 1),
                "qgis_score": 0.0,
                "security_score": round(security_score, 1),
            }

        qgis_score = self._get_qgis_score(
            qgis_checks["compliance"],
            qgis_checks["structure"],
            qgis_checks["metadata"],
            semantic["missing_resources"],
            qgis_checks["binaries"],
            qgis_checks["package_size"],
            security_penalty,
        )

        return {
            "code_score": round(module_score, 1),
            "maint_score": round(maintainability_score, 1),
            "qgis_score": round(qgis_score, 1),
            "security_score": round(security_score, 1),
        }

    def _get_mi_score(self, modules_data: List[ModuleAnalysisResult]) -> float:
        """Calculates module stability based on Maintainability Index (MI)."""
        mi_scores = []
        for m in modules_data:
            cc = m.get("complexity", 1)
            sloc = max(1, m.get("lines", 1))
            mi = (171 - 0.23 * cc - 16.2 * math.log(sloc)) * 100 / 171
            mi_scores.append(max(0, mi))
        return sum(mi_scores) / len(mi_scores) if mi_scores else 0.0

    def _get_maint_score(
        self,
        modules_data: List[ModuleAnalysisResult],
        ruff_findings: List[Dict[str, Any]],
    ) -> float:
        """Calculates maintainability based on function complexity and linting penalties."""
        all_func_comp = []
        for m in modules_data:
            for f in m.get("functions", []):
                all_func_comp.append(f["complexity"])

        avg_func_comp = (
            sum(all_func_comp) / len(all_func_comp) if all_func_comp else 1.0
        )
        func_score = max(0, 100 - (max(0, avg_func_comp - 10) * 5))

        total_lines = sum(m.get("lines", 0) for m in modules_data)

        # Harmonize findings from Ruff and internal AST analysis
        errors = 0
        warnings = 0
        others = 0

        # Process Ruff findings
        for f in ruff_findings:
            code = f.get("code", "")
            if code.startswith(("E", "F")):
                errors += 1
            elif code.startswith("W"):
                warnings += 1
            else:
                others += 1

        # Process internal AST issues
        for m in modules_data:
            for issue in m.get("ast_issues", []):
                severity = issue.get("severity", "medium").lower()
                if severity == "high":
                    errors += 1
                elif severity == "medium":
                    warnings += 1
                else:
                    others += 1

        # Improved penalty formula:
        # We normalize by total lines but ensure a minimum penalty for existing issues
        line_factor = max(1, total_lines / 100)
        penalty_base = 10 * errors + 3 * warnings + 1 * others

        # If there are issues, the base penalty should be at least 0.1 to avoid perfect scores
        if penalty_base > 0:
            penalty_base = max(0.1, penalty_base)

        lint_penalty = (penalty_base / line_factor) * 5
        lint_score = max(0, 100 - lint_penalty)

        return float((func_score * 0.7) + (lint_score * 0.3))

    def _get_modernization_bonus(
        self, modules_data: List[ModuleAnalysisResult]
    ) -> float:
        """Calculates modernization bonuses based on type hints and documentation styles."""
        total_functions = 0
        total_params = 0
        annotated_params = 0
        has_return_hint = 0
        detected_styles = set()

        for m in modules_data:
            metrics = m.get("research_metrics", {})
            t_stats = metrics.get("type_hint_stats", {})
            total_functions += t_stats.get("total_functions", 0)
            total_params += t_stats.get("total_parameters", 0)
            annotated_params += t_stats.get("annotated_parameters", 0)
            has_return_hint += t_stats.get("has_return_hint", 0)
            detected_styles.update(metrics.get("docstring_styles", []))

        bonus = 0.0
        if total_params > 0 or total_functions > 0:
            param_cov = annotated_params / max(1, total_params)
            ret_cov = has_return_hint / max(1, total_functions)
            if param_cov >= 0.8 and ret_cov >= 0.8:
                bonus += 5.0

        if detected_styles:
            bonus += 2.0
        return bonus

    def _get_qgis_score(
        self,
        compliance: Dict[str, Any],
        structure: Dict[str, Any],
        metadata: Dict[str, Any],
        missing_resources: List[str],
        binaries: List[str],
        package_size: float,
        security_penalty: float = 0.0,
    ) -> float:
        """Calculates QGIS-specific compliance score."""
        score = 100.0
        score -= compliance.get("issues_count", 0) * 2
        if not structure.get("is_valid", True):
            score -= 20
        if not metadata.get("is_valid", True):
            score -= 10
        score -= len(missing_resources) * 5
        score -= len(binaries) * 50
        if package_size > 20:
            score -= 10

        score -= security_penalty
        return float(max(0, score))

    def _get_security_penalty(self, modules_data: List[ModuleAnalysisResult]) -> float:
        """Calculates total penalty for security vulnerabilities."""
        penalty = 0.0
        for m in modules_data:
            for issue in m.get("security_issues", []):
                sev = issue.get("severity", "medium").lower()
                if sev == "high":
                    penalty += 10.0
                elif sev == "medium":
                    penalty += 5.0
                else:
                    penalty += 2.0
        return penalty
