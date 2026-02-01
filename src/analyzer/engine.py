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
from typing import Any, Dict, List, Optional

from .reporters import (
    generate_html_report,
    generate_markdown_summary,
    save_json_context,
)
from .scanner import (
    analyze_module_worker,
    audit_qgis_standards,
)
from .semantic import DependencyGraph, ResourceValidator
from .utils import (
    IgnoreMatcher,
    ProgressTracker,
    load_ignore_patterns,
    load_profile_config,
    logger,
    safe_path_resolve,
    setup_logger,
)
from .validators import (
    calculate_package_size,
    scan_for_binaries,
    validate_metadata,
    validate_metadata_urls,
    validate_plugin_structure,
)


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

        # Load profile config
        self.config = load_profile_config(self.project_path, profile)

        # Detect project type
        self.project_type = self.config.get("project_type", "auto")
        if self.project_type == "auto":
            metadata_file = self.project_path / "metadata.txt"
            self.project_type = "qgis" if metadata_file.exists() else "generic"

        logger.info(f"📁 Project type: {self.project_type.upper()}")

        # Load .analyzerignore
        ignore_file = self.project_path / ".analyzerignore"
        patterns = load_ignore_patterns(ignore_file)
        self.matcher = IgnoreMatcher(self.project_path, patterns)

    def get_python_files(self) -> List[pathlib.Path]:
        """Scans Python files ignoring common folders and .analyzerignore patterns.

        Returns:
            A sorted list of pathlib.Path objects for all detected Python files.
        """
        python_files = []
        project_path = pathlib.Path(self.project_path)

        # Handle direct file input
        if project_path.is_file():
            if project_path.suffix == ".py":
                return [project_path]
            return []

        # Handle directory scan
        for root, dirs, files in os.walk(self.project_path):
            root_path = pathlib.Path(root)

            # Filter directories
            dirs[:] = [d for d in dirs if not self.matcher.is_ignored(root_path / d)]

            for file in files:
                file_path = root_path / file
                if file.endswith(".py") and not self.matcher.is_ignored(file_path):
                    # Skip very large files to avoid OOM
                    if file_path.stat().st_size > self.max_file_size_kb * 1024:
                        logger.warning(
                            f"⚠️ Skipping large file: {file_path.name} (> {self.max_file_size_kb}KB)"
                        )
                        continue
                    python_files.append(file_path)
        return sorted(python_files)

    def run_ruff_audit(self) -> List[Dict[str, Any]]:
        """Executes Ruff linting via subprocess.

        Returns:
            A list of dictionaries representing Ruff findings. Returns an empty
            list if Ruff is not available or errors occur.
        """
        try:
            cmd = [
                "ruff",
                "check",
                str(self.project_path),
                "--format",
                "json",
                "--quiet",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.stdout:
                data: List[Dict[str, Any]] = json.loads(result.stdout)
                return data
            return []
        except Exception as e:
            logger.error(f"Error running Ruff: {e}")
            return []

    def _run_parallel_analysis(
        self, files: List[pathlib.Path], rules_config: dict
    ) -> List[Dict[str, Any]]:
        """Runs parallel analysis on all Python files.

        Args:
            files: List of paths to analyze.
            rules_config: Rule-specific configuration overrides.

        Returns:
            A list of module analysis results.
        """
        tracker = ProgressTracker(len(files))
        modules_data = []

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
        self, modules_data: List[Dict[str, Any]], rules_config: dict
    ) -> tuple:
        """Runs QGIS-specific validation checks.

        Args:
            modules_data: List of already analyzed module data.
            rules_config: Rule-specific configuration overrides.

        Returns:
            A tuple of (compliance, structure, metadata, binaries, package_size, url_status).
        """
        compliance = audit_qgis_standards(
            modules_data, self.project_path, rules_config=rules_config
        )

        # Official repository audit
        metadata_path = safe_path_resolve(self.project_path, "metadata.txt")
        structure = validate_plugin_structure(self.project_path)
        metadata = validate_metadata(metadata_path)

        # Repository Compliance Checks
        logger.info("Running QGIS repository compliance checks...")
        binaries = scan_for_binaries(self.project_path, self.matcher)
        package_size = calculate_package_size(self.project_path, self.matcher)
        url_status = {}
        if metadata.get("is_valid") and "metadata" in metadata:
            url_status = validate_metadata_urls(metadata["metadata"])

        return compliance, structure, metadata, binaries, package_size, url_status

    def _run_semantic_analysis(self, modules_data: List[Dict[str, Any]]) -> tuple:
        """Runs semantic analysis including dependencies and resources.

        Args:
            modules_data: List of analyzed module entries.

        Returns:
            A tuple of (cycles, metrics, missing_resources).
        """
        dep_graph = DependencyGraph()
        all_resource_usages = []
        res_validator = None

        if self.project_type == "qgis":
            res_validator = ResourceValidator(self.project_path)
            res_validator.scan_project_resources(self.matcher)

        for m in modules_data:
            dep_graph.add_node(m["path"], m)
            if self.project_type == "qgis" and "resource_usages" in m:
                all_resource_usages.extend(m["resource_usages"])

        dep_graph.build_edges(self.project_path)
        cycles = dep_graph.detect_cycles()
        metrics = dep_graph.get_coupling_metrics()

        missing_resources = []
        if self.project_type == "qgis" and res_validator:
            missing_resources = res_validator.validate_usage(all_resource_usages)

        return cycles, metrics, missing_resources

    def _build_analysis_results(
        self,
        files: List[pathlib.Path],
        modules_data: List[Dict[str, Any]],
        ruff_findings: List[Dict[str, Any]],
        code_score: float,
        maint_score: float,
        qgis_score: float,
        compliance: Dict[str, Any],
        structure: Dict[str, Any],
        metadata: Dict[str, Any],
        cycles: List[List[str]],
        metrics: Dict[str, Any],
        missing_resources: List[str],
        binaries: List[str],
        package_size: float,
        url_status: Dict[str, str],
        security_score: float,
        all_security_issues: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Consolidates analysis results into a single dictionary.

        Args:
            files: List of analyzed files.
            modules_data: Detailed analysis for each module.
            ruff_findings: Results from Ruff linting.
            code_score: Calculated module stability score.
            maint_score: Calculated maintainability score.
            qgis_score: Calculated QGIS compliance score.
            compliance: Detailed QGIS compliance findings.
            structure: Plugin structure validation results.
            metadata: Metadata validation results.
            cycles: Detected circular dependency cycles.
            metrics: Coupling and complexity metrics.
            missing_resources: List of missing QRC resources.
            binaries: List of prohibited binary files.
            package_size: Size of the plugin package in MB.
            url_status: Status of URLs in metadata.txt.

        Returns:
            The final analysis results dictionary.
        """
        metrics_summary = {
            "total_files": len(files),
            "total_lines": sum(m["lines"] for m in modules_data),
            "quality_score": round(code_score, 1),
            "maintainability_score": round(maint_score, 1),
            "security_score": round(security_score, 1),
        }

        if self.project_type == "qgis":
            metrics_summary["overall_score"] = round((code_score * 0.5) + (qgis_score * 0.5), 1)

        analyses = {
            "project_name": self.project_path.name,
            "project_type": self.project_type,
            "metrics": metrics_summary,
            "ruff_findings": ruff_findings,
            "security": {
                "findings": all_security_issues,
                "count": len(all_security_issues),
                "score": round(security_score, 1),
            },
            "semantic": {"circular_dependencies": cycles, "coupling_metrics": metrics},
            "modules": modules_data,
        }

        # Aggregate research metrics for summary
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

        analyses["research_summary"] = {
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

        if self.project_type == "qgis":
            analyses["qgis_compliance"] = {
                "compliance_score": round(qgis_score, 1),
                "best_practices": compliance,
                "repository_standards": {"structure": structure, "metadata": metadata},
            }
            analyses["semantic"]["missing_resources"] = missing_resources
            analyses["repository_compliance"] = {
                "binaries": binaries,
                "package_size_mb": round(package_size, 2),
                "url_validation": url_status,
                "is_compliant": len(binaries) == 0 and package_size <= 20,
            }

        return analyses

    def _save_reports(self, analyses: Dict[str, Any]) -> None:
        """Saves all generated analysis reports to the output directory.

        Args:
            analyses: The consolidated analysis results dictionary.
        """
        generate_markdown_summary(analyses, self.output_dir / "PROJECT_SUMMARY.md")
        if self.config.get("generate_html", True):
            generate_html_report(analyses, self.output_dir / "PROJECT_SUMMARY.html")
        save_json_context(analyses, self.output_dir / "project_context.json")

    def run(self) -> bool:
        """Executes the complete analysis pipeline.

        Returns:
            True if analysis completed successfully (even if issues were found),
            False if it failed due to critical system errors or strict mode violations.
        """
        logger.info(f"🔍 Analyzing: {self.project_path}")
        files = self.get_python_files()
        rules_config = self.config.get("rules", {})

        # Parallel analysis
        modules_data = self._run_parallel_analysis(files, rules_config)

        # Ruff audit
        ruff_findings = self.run_ruff_audit()

        # Initialize defaults
        compliance: Dict[str, Any] = {"issues": [], "issues_count": 0}
        structure: Dict[str, Any] = {"is_valid": True}
        metadata: Dict[str, Any] = {"is_valid": True}
        binaries: List[str] = []
        package_size = 0
        url_status = {}

        # QGIS-specific checks
        if self.project_type == "qgis":
            compliance, structure, metadata, binaries, package_size, url_status = (
                self._run_qgis_specific_checks(modules_data, rules_config)
            )

        # Semantic Analysis
        semantic_res = self._run_semantic_analysis(modules_data)
        cycles = semantic_res[0] if len(semantic_res) > 0 else []
        metrics = semantic_res[1] if len(semantic_res) > 1 else {}
        missing_resources = semantic_res[2] if len(semantic_res) > 2 else []
        # Calculate scores
        scores = self._calculate_scores(
            modules_data,
            ruff_findings,
            compliance,
            structure,
            metadata,
            cycles,
            missing_resources,
            binaries,
            package_size,
        )

        code_score = scores[0] if len(scores) > 0 else 0.0
        maint_score = scores[1] if len(scores) > 1 else 0.0
        qgis_score = scores[2] if len(scores) > 2 else 0.0
        security_score = scores[3] if len(scores) > 3 else 0.0

        # Aggregate all security findings
        all_security_issues = []
        for m in modules_data:
            all_security_issues.extend(m.get("security_issues", []))

        # Build results
        analyses = self._build_analysis_results(
            files,
            modules_data,
            ruff_findings,
            code_score,
            maint_score,
            qgis_score,
            compliance,
            structure,
            metadata,
            cycles,
            metrics,
            missing_resources,
            binaries,
            package_size,
            url_status,
            security_score,
            all_security_issues,
        )

        # Save reports
        self._save_reports(analyses)

        logger.info(f"✅ Analysis completed. Reports in: {self.output_dir}")

        # Fail on error if strict mode is on
        if self.config.get("fail_on_error") and self.project_type == "qgis":
            if (
                int(compliance.get("issues_count", 0)) > 0
                or not structure["is_valid"]
                or not metadata["is_valid"]
            ):
                logger.error(
                    "❌ Strict Mode: Critical QGIS compliance issues detected. Failing analysis."
                )
                return False

        return True

    def _calculate_scores(
        self,
        modules_data: List[Dict[str, Any]],
        ruff_findings: List[Dict[str, Any]],
        compliance: Dict[str, Any],
        structure: Dict[str, Any],
        metadata: Dict[str, Any],
        cycles: List[List[str]],
        missing_resources: List[str],
        binaries: List[str],
        package_size: float,
    ) -> tuple:
        """Calculates project quality scores based on industry-standard formulas.

        Args:
            modules_data: Detailed analysis results for each module.
            ruff_findings: List of Ruff linting findings.
            compliance: Findings from QGIS standard audit.
            structure: Results of plugin structure validation.
            metadata: Results of metadata.txt validation.
            cycles: List of circular dependency cycles.
            missing_resources: List of missing QRC resource paths.
            binaries: List of prohibited binary files.
            package_size: Size of the plugin package in MB.

        Returns:
            A tuple of (module_stability, maintainability, qgis_compliance) scores out of 100.
        """
        if not modules_data:
            return 0.0, 0.0, 0.0, 0.0

        module_score = self._get_mi_score(modules_data)
        maintainability_score = self._get_maint_score(modules_data, ruff_findings)
        modernization_bonus = self._get_modernization_bonus(modules_data)
        maintainability_score = min(100.0, maintainability_score + modernization_bonus)

        # Security context
        security_penalty = self._get_security_penalty(modules_data)
        security_score = max(0.0, 100.0 - security_penalty)

        # Global penalties (e.g., circular dependencies)
        penalty = len(cycles) * 10
        module_score = max(0, module_score - penalty)
        maintainability_score = max(0, maintainability_score - penalty)

        if self.project_type == "generic":
            return (
                round(module_score, 1),
                round(maintainability_score, 1),
                0.0,
                round(security_score, 1),
            )

        qgis_score = self._get_qgis_score(
            compliance,
            structure,
            metadata,
            missing_resources,
            binaries,
            package_size,
            security_penalty,
        )

        return (
            round(module_score, 1),
            round(maintainability_score, 1),
            round(qgis_score, 1),
            round(security_score, 1),
        )

    def _get_mi_score(self, modules_data: List[Dict[str, Any]]) -> float:
        """Calculates module stability based on Maintainability Index (MI)."""
        mi_scores = []
        for m in modules_data:
            cc = m.get("complexity", 1)
            sloc = max(1, m.get("lines", 1))
            # Formula: MI = (171 - 0.23 * CC - 16.2 * ln(SLOC)) * 100 / 171
            mi = (171 - 0.23 * cc - 16.2 * math.log(sloc)) * 100 / 171
            mi_scores.append(max(0, mi))
        return sum(mi_scores) / len(mi_scores) if mi_scores else 0.0

    def _get_maint_score(
        self, modules_data: List[Dict[str, Any]], ruff_findings: List[Dict[str, Any]]
    ) -> float:
        """Calculates maintainability based on function complexity and linting penalties."""
        # 1. Function Complexity Score
        all_func_comp = []
        for m in modules_data:
            for f in m.get("functions", []):
                all_func_comp.append(f["complexity"])

        avg_func_comp = sum(all_func_comp) / len(all_func_comp) if all_func_comp else 1.0
        func_score = max(0, 100 - (max(0, avg_func_comp - 10) * 5))

        # 2. Lint Scoring (Pylint style)
        total_lines = sum(m.get("lines", 0) for m in modules_data)
        errors = sum(1 for f in ruff_findings if f.get("code", "").startswith(("E", "F")))
        others = len(ruff_findings) - errors

        lint_penalty = ((5 * errors + others) / max(1, total_lines / 10)) * 10
        lint_score = max(0, 100 - lint_penalty)

        return float((func_score * 0.7) + (lint_score * 0.3))

    def _get_modernization_bonus(self, modules_data: List[Dict[str, Any]]) -> float:
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

        # Security penalty
        score -= security_penalty

        return float(max(0, score))

    def _get_security_penalty(self, modules_data: List[Dict[str, Any]]) -> float:
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
