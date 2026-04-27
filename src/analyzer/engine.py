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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, cast

from .aggregators import (
    build_analysis_results,
    save_reports,
)
from .scanner import (
    ModuleAnalysisResult,
    analyze_module_worker,
    audit_qgis_standards,
)
from .scoring import (
    QGISChecksResult,
    ScoringEngine,
    SemanticAnalysisResult,
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
        self,
        files: List[pathlib.Path],
        rules_config: Dict[str, Any],
        scope: str = "all",
    ) -> List[ModuleAnalysisResult]:
        """Runs parallel analysis on all Python files.

        Args:
            files: List of paths to analyze.
            rules_config: Rule-specific configuration overrides.

        Returns:
            A list of module analysis results.
        """
        from .scanner import init_worker

        tracker = ProgressTracker(len(files))
        modules_data: List[ModuleAnalysisResult] = []

        # Shared context to avoid serializing large rules multiple times
        shared_context = {
            "project_path": self.project_path,
            "rules_config": rules_config,
            "scope": scope,
        }

        with ProcessPoolExecutor(
            max_workers=self.max_workers,
            initializer=init_worker,
            initargs=(shared_context,),
        ) as executor:
            # We no longer need to pass project_path or rules_config to every call
            futures = {executor.submit(analyze_module_worker, f): f for f in files}
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
            "graph": {u: list(v) for u, v in dep_graph.adjacency_list.items()},
            "metrics": metrics,
            "missing_resources": missing_resources,
        }

    def run(self, scope: str = "all") -> bool:
        """Executes the analysis pipeline based on the specified scope.

        Args:
            scope: The scope of analysis ('all', 'i18n', 'security', 'performance',
                   'architecture', 'metadata'). Defaults to 'all'.

        Returns:
            True if analysis completed successfully, False otherwise.
        """
        logger.info(f"🔍 Analyzing: {self.project_path} [Scope: {scope}]")

        # Unified Project Discovery
        discovery = discover_project_files(self.project_path, self.matcher)
        files = discovery["python_files"]
        rules_config = self.config.rules

        # Refine Project Type based on discovered metadata
        if self.config.project_type == "auto":
            new_type = "qgis" if discovery["has_metadata"] else "generic"
            if new_type != self.project_type:
                logger.info(f"📁 Project type updated to: {new_type.upper()}")
                self.project_type = new_type

        # 1. Parallel analysis (AST/Visitors)
        # We pass the scope to filter which visitors run inside the workers
        modules_data = []
        if scope in ["all", "i18n", "security", "performance", "architecture"]:
            modules_data = self._run_parallel_analysis(files, rules_config, scope)

        # 2. Ruff audit (Generic linting)
        ruff_findings = []
        if scope in ["all", "security", "performance"]:
            ruff_result = self.run_ruff_audit()
            ruff_findings = ruff_result["findings"]

        # 3. QGIS-specific checks (Metadata, structure, constraints)
        qgis_checks: Optional[QGISChecksResult] = None
        if self.project_type == "qgis" and scope in ["all", "metadata", "performance"]:
            qgis_checks = self._run_qgis_specific_checks(
                modules_data, rules_config, discovery
            )

        # 4. Semantic Analysis (Dependencies, coupling, cycles)
        semantic: SemanticAnalysisResult = {
            "cycles": [],
            "graph": {},
            "metrics": {},
            "missing_resources": [],
        }
        if scope in ["all", "architecture"]:
            semantic = self._run_semantic_analysis(modules_data)

        # Calculate scores via ScoringEngine
        scores = self.scoring.calculate_project_scores(
            modules_data,
            ruff_findings,
            qgis_checks,
            semantic,
        )

        # Filter issues by scope before building final results
        modules_data = self._filter_issues_by_scope(modules_data, scope)

        # Build results
        analyses = build_analysis_results(
            self.project_path,
            self.project_type,
            files,
            modules_data,
            ruff_findings,
            scores,
            qgis_checks,
            semantic,
        )

        # Save reports
        save_reports(analyses, self.output_dir, self.config.generate_html)

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

    def _filter_issues_by_scope(
        self, modules_data: List[ModuleAnalysisResult], scope: str
    ) -> List[ModuleAnalysisResult]:
        """Filters issues in modules based on the analysis scope.

        Args:
            modules_data: List of module analysis results.
            scope: The analysis scope.

        Returns:
            Filtered list of module analysis results.
        """
        if scope == "all":
            return modules_data

        # Define scope-specific rule sets
        scope_rules = {
            "i18n": {"MISSING_I18N"},
            "security": {
                "UNSAFE_SUBPROCESS",
                "HARDCODED_PASSWORD",
                "SQL_INJECTION",
                "UNSAFE_YAML",
                "UNSAFE_PICKLE",
            },
            "performance": {
                "SPATIAL_INDEX",
                "BLOCKING_NETWORK_CALL",
                "UI_BLOCKING_LOOP",
                "NON_PYTHONIC_LOOP",
            },
            "architecture": {
                "QGIS_PROTECTED_MEMBER",
                "GDAL_DIRECT_IMPORT",
                "QGIS_LEGACY_IMPORT",
                "HEAVY_LOGIC_UI",
                "PYQT5_IMPORT",
                "LEGACY_GDAL_IMPORT",
            },
            "metadata": {
                "MANDATORY_CLEANUP",
                "OBSOLETE_API",
                "IFACE_AS_ARGUMENT",
            },
        }

        allowed_rules = scope_rules.get(scope, set())
        if not allowed_rules:
            return modules_data

        # Filter issues in each module
        filtered_modules = []
        for module in modules_data:
            filtered_module = module.copy()
            filtered_module["ast_issues"] = [
                issue
                for issue in module.get("ast_issues", [])
                if issue.get("type") in allowed_rules
            ]
            filtered_module["security_issues"] = [
                issue
                for issue in module.get("security_issues", [])
                if issue.get("type") in allowed_rules
            ]
            filtered_modules.append(filtered_module)

        return filtered_modules
