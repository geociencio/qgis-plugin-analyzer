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
import os
import pathlib
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from .reporters import generate_html_report, generate_markdown_summary, save_json_context
from .scanner import (
    analyze_module_worker,
    audit_qgis_standards,
    validate_metadata,
    validate_plugin_structure,
)
from .semantic import DependencyGraph, ResourceValidator
from .utils import (
    IgnoreMatcher,
    ProgressTracker,
    load_ignore_patterns,
    load_profile_config,
    logger,
    setup_logger,
)


class ProjectAnalyzer:
    def __init__(
        self, project_path: str, output_dir: Optional[str] = None, profile: str = "default"
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

        # Load .analyzerignore
        ignore_file = self.project_path / ".analyzerignore"
        patterns = load_ignore_patterns(ignore_file)
        self.matcher = IgnoreMatcher(self.project_path, patterns)

    def get_python_files(self) -> List[pathlib.Path]:
        """Scans Python files ignoring common folders and .analyzerignore patterns."""
        exclude = {"venv", ".venv", "__pycache__", ".git", "build", "dist"}
        python_files = []
        for root, dirs, files in os.walk(self.project_path):
            root_path = pathlib.Path(root)

            # Filter directories
            dirs[:] = [
                d for d in dirs if d not in exclude and not self.matcher.is_ignored(root_path / d)
            ]

            for file in files:
                file_path = root_path / file
                if file.endswith(".py") and not self.matcher.is_ignored(file_path):
                    # Skip very large files to avoid OOM
                    if file_path.stat().st_size > self.max_file_size_kb * 1024:
                        logger.warning(f"⚠️ Skipping large file: {file_path.name} (> {self.max_file_size_kb}KB)")
                        continue
                    python_files.append(file_path)
        return sorted(python_files)

    def run_ruff_audit(self) -> List[Dict[str, Any]]:
        """Executes Ruff via subprocess and returns findings."""
        try:
            cmd = ["ruff", "check", str(self.project_path), "--format", "json", "--quiet"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.stdout:
                return json.loads(result.stdout)
            return []
        except Exception as e:
            logger.error(f"Error running Ruff: {e}")
            return []

    def run(self):
        """Runs the analysis pipeline."""
        logger.info(f"🔍 Analyzing: {self.project_path}")
        files = self.get_python_files()
        tracker = ProgressTracker(len(files))
        modules_data = []

        # Parallel analysis
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(analyze_module_worker, f, self.project_path): f for f in files
            }
            for future in as_completed(futures):
                res = future.result()
                if res:
                    modules_data.append(res)
                tracker.update(futures[future], 0)

        # Ruff audit
        ruff_findings = self.run_ruff_audit()

        # QGIS compliance analysis
        compliance = audit_qgis_standards(modules_data, self.project_path)

        # Official repository audit
        structure = validate_plugin_structure(self.project_path)
        metadata = validate_metadata(self.project_path)

        # Semantic Analysis
        dep_graph = DependencyGraph()
        res_validator = ResourceValidator(self.project_path)
        res_validator.scan_project_resources()
        
        all_resource_usages = []

        for m in modules_data:
             dep_graph.add_node(m["path"], m)
             if "resource_usages" in m:
                 all_resource_usages.extend(m["resource_usages"])

        dep_graph.build_edges(self.project_path)
        cycles = dep_graph.detect_cycles()
        metrics = dep_graph.get_coupling_metrics()
        missing_resources = res_validator.validate_usage(all_resource_usages)

        # Calculate basic metrics
        code_score, qgis_score = self._calculate_scores(
            modules_data, compliance, structure, metadata, cycles, missing_resources
        )

        metrics_summary = {
            "total_files": len(files),
            "total_lines": sum(m["lines"] for m in modules_data),
            "quality_score": round((code_score * 0.5) + (qgis_score * 0.5), 1),
        }

        analyses = {
            "project_name": self.project_path.name,
            "metrics": metrics_summary,
            "qgis_compliance": {
                "compliance_score": round(qgis_score, 1),
                "best_practices": compliance,
                "repository_standards": {"structure": structure, "metadata": metadata},
            },
            "ruff_findings": ruff_findings,
            "semantic": {
                "circular_dependencies": cycles,
                "missing_resources": missing_resources,
                "coupling_metrics": metrics
            },
            "modules": modules_data,
        }

        # Save reports
        generate_markdown_summary(analyses, self.output_dir / "PROJECT_SUMMARY.md")
        if self.config.get("generate_html", True):
            generate_html_report(analyses, self.output_dir / "PROJECT_SUMMARY.html")
        save_json_context(analyses, self.output_dir / "project_context.json")

        tracker.complete()
        logger.info(f"✅ Analysis completed. Reports in: {self.output_dir}")

        # Fail on error if strict mode is on and there are issues
        if self.config.get("fail_on_error") and (
            compliance.get("issues_count", 0) > 0
            or not structure["is_valid"]
            or not metadata["is_valid"]
        ):
            logger.error("❌ Strict Mode: Critical QGIS compliance issues detected. Failing analysis.")
            return False

        return True

    def _calculate_scores(
        self, modules_data, compliance, structure, metadata, cycles, missing_resources
    ) -> tuple:
        """Calculates scores based on QGIS standards and code quality."""
        if not modules_data:
            return 0.0, 0.0

        # 1. Base Code Quality (50%)
        avg_comp = sum(m["complexity"] for m in modules_data) / len(modules_data)
        code_score = max(0, 100 - (avg_comp * 3))

        # Penalty for circular dependencies (major design flaw)
        code_score -= len(cycles) * 10 

        # 2. QGIS Standards (50%)
        qgis_score = 100
        # Penalty for technical findings
        qgis_score -= compliance.get("issues_count", 0) * 2
        # Penalty for repository missing files/metadata
        if not structure["is_valid"]:
            qgis_score -= 20
        if not metadata["is_valid"]:
            qgis_score -= 10
        
        # Penalty for missing resources
        qgis_score -= len(missing_resources) * 5

        return max(0, code_score), max(0, qgis_score)
