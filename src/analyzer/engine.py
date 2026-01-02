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
    ):
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
        """Scans Python files ignoring common folders and .analyzerignore patterns."""
        python_files = []
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
        """Executes Ruff via subprocess and returns findings."""
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
                return json.loads(result.stdout)
            return []
        except Exception as e:
            logger.error(f"Error running Ruff: {e}")
            return []

    def _run_parallel_analysis(
        self, files: List[pathlib.Path], rules_config: dict
    ) -> List[Dict[str, Any]]:
        """Runs parallel analysis on all Python files."""
        tracker = ProgressTracker(len(files))
        modules_data = []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    analyze_module_worker, f, self.project_path, None, rules_config
                ): f
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
        """Runs QGIS-specific validation checks."""
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
        """Runs semantic analysis (dependencies, resources)."""
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
    ) -> Dict[str, Any]:
        """Builds the analysis results dictionary."""
        metrics_summary = {
            "total_files": len(files),
            "total_lines": sum(m["lines"] for m in modules_data),
            "quality_score": round(code_score, 1),
            "maintainability_score": round(maint_score, 1),
        }

        if self.project_type == "qgis":
            metrics_summary["overall_score"] = round(
                (code_score * 0.5) + (qgis_score * 0.5), 1
            )

        analyses = {
            "project_name": self.project_path.name,
            "project_type": self.project_type,
            "metrics": metrics_summary,
            "ruff_findings": ruff_findings,
            "semantic": {"circular_dependencies": cycles, "coupling_metrics": metrics},
            "modules": modules_data,
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

    def _save_reports(self, analyses: Dict[str, Any]):
        """Saves all analysis reports."""
        generate_markdown_summary(analyses, self.output_dir / "PROJECT_SUMMARY.md")
        if self.config.get("generate_html", True):
            generate_html_report(analyses, self.output_dir / "PROJECT_SUMMARY.html")
        save_json_context(analyses, self.output_dir / "project_context.json")

    def run(self):
        """Runs the analysis pipeline."""
        logger.info(f"🔍 Analyzing: {self.project_path}")
        files = self.get_python_files()
        rules_config = self.config.get("rules", {})

        # Parallel analysis
        modules_data = self._run_parallel_analysis(files, rules_config)

        # Ruff audit
        ruff_findings = self.run_ruff_audit()

        # Initialize defaults
        compliance = {"issues": [], "issues_count": 0}
        structure = {"is_valid": True}
        metadata = {"is_valid": True}
        binaries = []
        package_size = 0
        url_status = {}

        # QGIS-specific checks
        if self.project_type == "qgis":
            compliance, structure, metadata, binaries, package_size, url_status = (
                self._run_qgis_specific_checks(modules_data, rules_config)
            )

        # Semantic Analysis
        cycles, metrics, missing_resources = self._run_semantic_analysis(modules_data)

        # Calculate scores
        code_score, maint_score, qgis_score = self._calculate_scores(
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
        )

        # Save reports
        self._save_reports(analyses)

        logger.info(f"✅ Analysis completed. Reports in: {self.output_dir}")

        # Fail on error if strict mode is on
        if self.config.get("fail_on_error") and self.project_type == "qgis":
            if (
                compliance.get("issues_count", 0) > 0
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
        modules_data,
        ruff_findings,
        compliance,
        structure,
        metadata,
        cycles,
        missing_resources,
        binaries,
        package_size,
    ) -> tuple:
        """Calculates scores based on project type and standardized metrics."""
        if not modules_data:
            return 0.0, 0.0, 0.0

        # 1. Module stability based on Maintainability Index (MI)
        # Formula: MI = max(0, (171 - 0.23 * CC - 16.2 * ln(SLOC)) * 100 / 171)
        mi_scores = []
        for m in modules_data:
            cc = m.get("complexity", 1)
            sloc = max(1, m.get("lines", 1))
            mi = (171 - 0.23 * cc - 16.2 * math.log(sloc)) * 100 / 171
            mi_scores.append(max(0, mi))

        module_score = sum(mi_scores) / len(mi_scores) if mi_scores else 0.0

        # 2. Maintainability based on Function Complexity
        all_func_comp = []
        for m in modules_data:
            for f in m.get("functions", []):
                all_func_comp.append(f["complexity"])

        avg_func_comp = (
            sum(all_func_comp) / len(all_func_comp) if all_func_comp else 1.0
        )
        # Function complexity score: 100 is perfect, -5 per point over 10
        func_score = max(0, 100 - (max(0, avg_func_comp - 10) * 5))

        # 3. Lint Scoring (Pylint style)
        # 10 - ((5*E + W + R + C) / statements) * 10
        total_lines = sum(m.get("lines", 0) for m in modules_data)
        errors = 0
        others = 0
        for find in ruff_findings:
            code = find.get("code", "")
            if code.startswith(("E", "F")):
                errors += 1
            else:
                others += 1

        lint_penalty = ((5 * errors + others) / max(1, total_lines / 10)) * 10
        lint_score = max(0, 100 - lint_penalty)

        # Composite Maintainability Score
        maintainability_score = (func_score * 0.7) + (lint_score * 0.3)

        # Global penalties
        penalty = len(cycles) * 10
        module_score = max(0, module_score - penalty)
        maintainability_score = max(0, maintainability_score - penalty)

        if self.project_type == "generic":
            return round(module_score, 1), round(maintainability_score, 1), 0.0

        # 4. QGIS Standards (only if QGIS project)
        qgis_score = 100.0
        # Penalty for technical findings
        qgis_score -= compliance.get("issues_count", 0) * 2
        # Penalty for repository missing files/metadata
        if not structure.get("is_valid", True):
            qgis_score -= 20
        if not metadata.get("is_valid", True):
            qgis_score -= 10
        # Penalty for missing resources
        qgis_score -= len(missing_resources) * 5
        # Repository compliance penalties
        qgis_score -= len(binaries) * 50
        if package_size > 20:
            qgis_score -= 10

        return (
            round(module_score, 1),
            round(maintainability_score, 1),
            round(max(0, qgis_score), 1),
        )
