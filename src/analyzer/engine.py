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
import math
import os
import pathlib
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict, cast

from .reporters import (
    generate_html_report,
    generate_markdown_summary,
    save_json_context,
)
from .scanner import (
    ModuleAnalysisResult,
    analyze_module_worker,
    audit_qgis_standards,
)
from .semantic import DependencyGraph, ResourceValidator
from .utils import (
    IgnoreMatcher,
    ProgressTracker,
    discover_project_files,
    load_ignore_patterns,
    load_profile_config,
    logger,
    setup_logger,
)
from .validators import (
    validate_metadata,
    validate_metadata_urls,
    validate_package_constraints,
    validate_plugin_structure,
)

# --- Types ---


@dataclass(frozen=True)
class ProjectConfig:
    """Strongly typed project configuration."""

    strict: bool = False
    generate_html: bool = True
    fail_on_error: bool = False
    project_type: str = "auto"
    rules: Dict[str, Any] = field(default_factory=dict)
    fail_on_critical: bool = False


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
    metrics: Dict[str, Any]
    missing_resources: List[str]


class ProjectScores(TypedDict):
    """Calculated project quality scores."""

    code_score: float
    maint_score: float
    qgis_score: float
    security_score: float


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

        # Cap modernization bonus: if there are linting issues, limit to 99.9
        # unless it's already a perfect score (which shouldn't happen with warnings)
        if ruff_findings and (maintainability_score + modernization_bonus) >= 100.0:
            maintainability_score = 99.9
        else:
            maintainability_score = min(100.0, maintainability_score + modernization_bonus)

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

        avg_func_comp = sum(all_func_comp) / len(all_func_comp) if all_func_comp else 1.0
        func_score = max(0, 100 - (max(0, avg_func_comp - 10) * 5))

        total_lines = sum(m.get("lines", 0) for m in modules_data)
        errors = sum(1 for f in ruff_findings if f.get("code", "").startswith(("E", "F")))
        warnings = sum(1 for f in ruff_findings if f.get("code", "").startswith("W"))
        others = len(ruff_findings) - errors - warnings

        # Improved penalty formula:
        # 1. Increase weight for errors and warnings
        # 2. Use a logarithmic-ish scale for lines to not dilute penalties too much in large projects
        line_factor = max(1, total_lines / 100)
        penalty_base = 10 * errors + 3 * warnings + others
        lint_penalty = (penalty_base / line_factor) * 5
        lint_score = max(0, 100 - lint_penalty)

        return float((func_score * 0.7) + (lint_score * 0.3))

    def _get_modernization_bonus(self, modules_data: List[ModuleAnalysisResult]) -> float:
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


class ProjectAnalyzer:
    def __init__(
        self,
        project_path: str,
        output_dir: Optional[str] = None,
        profile: str = "default",
    ) -> None:
        """Initializes the Project Analyzer.

        Args:
            project_path: Root path of the project to analyze.
            output_dir: Directory to save analysis reports. Defaults to "./analysis_results".
            profile: Configuration profile name from pyproject.toml. Defaults to "default".
        """
        self.project_path = pathlib.Path(project_path).resolve()
        self.output_dir = pathlib.Path(output_dir or "./analysis_results").resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        setup_logger(self.output_dir)

        # Limit workers to 4 or cpu count, whichever is smaller, to prevent OOM
        self.max_workers = min(os.cpu_count() or 4, 4)
        self.max_file_size_kb = 500

        # Load and wrap config
        raw_config = load_profile_config(self.project_path, profile)
        self.config = ProjectConfig(
            strict=raw_config.get("strict", False),
            generate_html=raw_config.get("generate_html", True),
            fail_on_error=raw_config.get("fail_on_error", False),
            project_type=raw_config.get("project_type", "auto"),
            rules=raw_config.get("rules", {}),
        )

        # Detect project type
        self.project_type = self.config.project_type
        if self.project_type == "auto":
            metadata_file = self.project_path / "metadata.txt"
            self.project_type = "qgis" if metadata_file.exists() else "generic"

        logger.info(f"📁 Project type: {self.project_type.upper()}")

        # Initialize Engines
        self.scoring = ScoringEngine(self.project_type)

        # Load .analyzerignore
        ignore_file = self.project_path / ".analyzerignore"
        patterns = load_ignore_patterns(ignore_file)
        self.matcher = IgnoreMatcher(self.project_path, patterns)

    def run_ruff_audit(self) -> Dict[str, Any]:
        """Executes Ruff linting via subprocess.

        Returns:
            A dictionary containing findings and metadata.
        """
        try:
            cmd = [
                "ruff",
                "check",
                str(self.project_path),
                "--output-format",
                "json",
                "--quiet",
            ]

            # In strict mode, we force extra rules if not already configured
            if self.config.strict:
                cmd.extend(
                    [
                        "--select",
                        "E,F,W,C90,I,N,D,UP,YTT,ASYNC,S,BLE,B,A,COM,T10,EM,EXE,FA,ISC,ICN,G,INP,PIE,T20,PYI,PT,Q,RET,SLF,SIM,TID,TCH,INT,ARG,PTH,TD,ERA,PD,PGH,PL,TRY,FLY,PERF,FURB,LOG,RUFF",
                    ]
                )

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            findings = []
            if result.stdout:
                try:
                    findings = json.loads(result.stdout)
                except json.JSONDecodeError:
                    logger.error("Failed to parse Ruff JSON output")

            return {
                "findings": findings,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "command": " ".join(cmd),
            }
        except Exception as e:
            logger.error(f"Error running Ruff: {e}")
            return {
                "findings": [],
                "stderr": str(e),
                "exit_code": -1,
                "command": "ruff check",
            }

    def _run_parallel_analysis(
        self, files: List[pathlib.Path], rules_config: Dict[str, Any]
    ) -> List[ModuleAnalysisResult]:
        """Runs parallel analysis on all Python files.

        Args:
            files: List of paths to analyze.
            rules_config: Rule-specific configuration overrides.

        Returns:
            A list of module analysis results.
        """
        tracker = ProgressTracker(len(files))
        modules_data: List[ModuleAnalysisResult] = []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(analyze_module_worker, f, self.project_path, None, rules_config): f
                for f in files
            }
            for future in as_completed(futures):
                res = future.result()
                if res:
                    modules_data.append(res)
                tracker.update(futures[future], 0)

        tracker.complete()
        return modules_data

    def _run_qgis_specific_checks(
        self,
        modules_data: List[ModuleAnalysisResult],
        rules_config: Dict[str, Any],
        discovery: Dict[str, Any],
    ) -> QGISChecksResult:
        """Runs QGIS-specific validation checks.

        Args:
            modules_data: Results from module analysis.
            rules_config: Configuration for rules.
            discovery: Discovery results from the project scanner.

        Returns:
            A QGISChecksResult containing findings from all checks.
        """
        metadata_file = self.project_path / "metadata.txt"
        compliance = audit_qgis_standards(modules_data, self.project_path, rules_config)
        structure = validate_plugin_structure(self.project_path)
        metadata = validate_metadata(metadata_file)

        # New Repository Constraints
        constraints = validate_package_constraints(
            discovery["total_size_mb"], discovery["binaries"]
        )

        return {
            "compliance": compliance,
            "structure": structure,
            "metadata": metadata,
            "binaries": discovery["binaries"],
            "package_size": discovery["total_size_mb"],
            "package_constraints": constraints,
            "url_status": validate_metadata_urls(metadata.get("metadata", {})),
        }

    def _run_semantic_analysis(
        self, modules_data: List[ModuleAnalysisResult]
    ) -> SemanticAnalysisResult:
        """Runs semantic analysis including dependencies and resources.

        Args:
            modules_data: List of analyzed module entries.

        Returns:
            A dictionary containing cycles, metrics, and missing resources.
        """
        dep_graph = DependencyGraph()
        all_resource_usages = []
        res_validator = None

        if self.project_type == "qgis":
            res_validator = ResourceValidator(self.project_path)
            res_validator.scan_project_resources(self.matcher)

        for m in modules_data:
            dep_graph.add_node(m["path"], cast(Dict[str, Any], m))
            if self.project_type == "qgis" and "resource_usages" in m:
                # Type safe usage of resource_usages from TypedDict
                resource_usages = m.get("resource_usages", [])
                all_resource_usages.extend(resource_usages)

        dep_graph.build_edges(self.project_path)
        cycles = dep_graph.detect_cycles()
        metrics = dep_graph.get_coupling_metrics()

        missing_resources = []
        if self.project_type == "qgis" and res_validator:
            missing_resources = res_validator.validate_usage(all_resource_usages)

        return {
            "cycles": cycles,
            "metrics": metrics,
            "missing_resources": missing_resources,
        }

    def _build_analysis_results(
        self,
        files: List[pathlib.Path],
        modules_data: List[ModuleAnalysisResult],
        ruff_findings: List[Dict[str, Any]],
        scores: ProjectScores,
        qgis_checks: Optional[QGISChecksResult],
        semantic: SemanticAnalysisResult,
    ) -> FullAnalysisResult:
        """Consolidates analysis results into a single dictionary."""
        analyses: FullAnalysisResult = {
            "project_name": self.project_path.name,
            "project_type": self.project_type,
            "metrics": self._get_metrics_summary(files, modules_data, scores),
            "ruff_findings": ruff_findings,
            "security": self._get_security_summary(modules_data, scores),
            "semantic": {
                "circular_dependencies": semantic["cycles"],
                "coupling_metrics": semantic["metrics"],
            },
            "modules": modules_data,
            "research_summary": self._get_research_summary(modules_data),
        }

        if self.project_type == "qgis" and qgis_checks:
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
                "folder_name_valid": qgis_checks["structure"].get("folder_name_valid", True),
                "constraint_errors": qgis_checks["package_constraints"].get("errors", []),
                "is_compliant": qgis_checks["package_constraints"].get("is_valid", True)
                and qgis_checks["structure"].get("is_valid", True),
            }
            analyses["ruff_metadata"] = ruff_findings.get(
                "metadata", {}
            )  # Placeholder for extra ruff metadata if needed

        return analyses

    def _get_metrics_summary(
        self,
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

    def _get_security_summary(
        self, modules_data: List[ModuleAnalysisResult], scores: ProjectScores
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

    def _get_research_summary(self, modules_data: List[ModuleAnalysisResult]) -> Dict[str, Any]:
        """Aggregates research metrics for summary."""
        total_functions = 0
        total_params = 0
        annotated_params = 0
        has_return_hint = 0
        has_docstring_count = 0
        total_public_items = 0
        detected_styles = set()

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

        return {
            "type_hint_coverage": round((annotated_params / max(1, total_params)) * 100, 1)
            if total_params > 0
            else 0.0,
            "return_hint_coverage": (
                round((has_return_hint / total_functions) * 100, 1) if total_functions > 0 else 0.0
            ),
            "docstring_coverage": round((has_docstring_count / max(1, total_public_items)) * 100, 1)
            if total_public_items > 0
            else 0.0,
            "detected_docstring_styles": list(detected_styles),
        }

    def _save_reports(self, analyses: FullAnalysisResult) -> None:
        """Saves all generated analysis reports to the output directory.

        Args:
            analyses: The consolidated analysis results dictionary.
        """
        data = cast(Dict[str, Any], analyses)
        generate_markdown_summary(data, self.output_dir / "PROJECT_SUMMARY.md")
        if self.config.generate_html:
            generate_html_report(data, self.output_dir / "PROJECT_SUMMARY.html")
        save_json_context(data, self.output_dir / "project_context.json")

    def run(self) -> bool:
        """Executes the complete analysis pipeline.

        Returns:
            True if analysis completed successfully (even if issues were found),
            False if it failed due to critical system errors or strict mode violations.
        """
        logger.info(f"🔍 Analyzing: {self.project_path}")

        # Unified Project Discovery
        discovery = discover_project_files(self.project_path, self.matcher)
        files = discovery["python_files"]
        rules_config = self.config.rules

        # Update Project Type if it was auto
        if self.config.project_type == "auto":
            self.project_type = "qgis" if discovery["has_metadata"] else "generic"
            logger.info(f"📁 Project type: {self.project_type.upper()}")

        # Parallel analysis
        modules_data = self._run_parallel_analysis(files, rules_config)

        # Ruff audit
        ruff_result = self.run_ruff_audit()
        ruff_findings = ruff_result["findings"]

        # Initialize defaults
        qgis_checks: Optional[QGISChecksResult] = None

        # QGIS-specific checks
        if self.project_type == "qgis":
            qgis_checks = self._run_qgis_specific_checks(modules_data, rules_config, discovery)

        # Semantic Analysis
        semantic = self._run_semantic_analysis(modules_data)

        # Calculate scores via ScoringEngine
        scores = self.scoring.calculate_project_scores(
            modules_data,
            ruff_findings,
            qgis_checks,
            semantic,
        )

        # Build results
        analyses = self._build_analysis_results(
            files,
            modules_data,
            ruff_findings,
            scores,
            qgis_checks,
            semantic,
        )
        analyses["ruff_metadata"] = {
            "stderr": ruff_result["stderr"],
            "exit_code": ruff_result["exit_code"],
            "command": ruff_result["command"],
        }

        # Save reports
        self._save_reports(analyses)

        logger.info(f"✅ Analysis completed. Reports in: {self.output_dir}")

        # Fail on error if strict mode is on
        if self.config.fail_on_error and self.project_type == "qgis" and qgis_checks:
            compliance = qgis_checks["compliance"]
            structure = qgis_checks["structure"]
            metadata = qgis_checks["metadata"]
            if (
                int(compliance.get("issues_count", 0)) > 0
                or not structure.get("is_valid", True)
                or not metadata.get("is_valid", True)
                or not qgis_checks["package_constraints"].get("is_valid", True)
            ):
                logger.error(
                    "❌ Strict Mode: Critical QGIS compliance issues detected. Failing analysis."
                )
                return False

        return True
