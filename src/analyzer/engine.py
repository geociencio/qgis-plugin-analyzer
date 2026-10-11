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
from dataclasses import dataclass, field
from typing import Any

from .aggregators import (
    build_analysis_results,
    save_reports,
)
from .parallel_analysis import chunk_files, run_parallel_analysis
from .qgis_checks import run_qgis_checks
from .ruff_audit import run_ruff_audit as _run_ruff_audit
from .scanner import ModuleAnalysisResult
from .scope_filter import filter_issues_by_scope
from .scoring import (
    QGISChecksResult,
    ScoringEngine,
    SemanticAnalysisResult,
)
from .semantic import run_semantic_analysis
from .utils import (
    IgnoreMatcher,
    discover_project_files,
    load_ignore_patterns,
    load_profile_config,
    logger,
    resolve_max_workers,
    setup_logger,
)

# --- Types ---


@dataclass(frozen=True)
class ProjectConfig:
    """Strongly typed project configuration."""

    strict: bool = False
    generate_html: bool = True
    fail_on_error: bool = False
    project_type: str = "auto"
    rules: dict[str, Any] = field(default_factory=dict)
    fail_on_critical: bool = False
    include_content: bool = False
    workers: int | None = None


class ProjectAnalyzer:
    def __init__(
        self,
        project_path: str,
        output_dir: str | None = None,
        profile: str = "default",
        workers: int | None = None,
    ) -> None:
        """Initializes the Project Analyzer.

        Args:
            project_path: Root path of the project to analyze.
            output_dir: Directory to save analysis reports. Defaults to "./analysis_results".
            profile: Configuration profile name from pyproject.toml. Defaults to "default".
            workers: Optional worker-process override. Takes precedence over the
                ``workers`` value from the profile config.
        """
        self.project_path = pathlib.Path(project_path).resolve()
        self.output_dir = pathlib.Path(output_dir or "./analysis_results").resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        setup_logger(self.output_dir)

        self.max_file_size_kb = 500

        # Load and wrap config
        raw_config = load_profile_config(self.project_path, profile)
        effective_workers = workers if workers is not None else raw_config.get("workers")
        self.config = ProjectConfig(
            strict=raw_config.get("strict", False),
            generate_html=raw_config.get("generate_html", True),
            fail_on_error=raw_config.get("fail_on_error", False),
            project_type=raw_config.get("project_type", "auto"),
            rules=raw_config.get("rules", {}),
            include_content=raw_config.get("include_content", False),
            workers=effective_workers,
        )

        # Resolve the worker count, keeping the anti-OOM ceiling of 4.
        self.max_workers = self._resolve_max_workers(effective_workers)

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

    @staticmethod
    def _resolve_max_workers(workers: int | None) -> int:
        """Resolves the parallel worker count with a hard ceiling of 4.

        Args:
            workers: Explicit worker count (config or CLI), or None for the default.

        Returns:
            The number of worker processes to use (``min(4, max(1, cpu-1))`` by
            default; explicit values are clamped to the ``1..4`` range).
        """
        return resolve_max_workers(workers)

    def run_ruff_audit(self) -> dict[str, Any]:
        """Executes Ruff linting via subprocess.

        Returns:
            A dictionary containing findings and metadata, including
            ``tool_unavailable``.
        """
        return _run_ruff_audit(self.project_path, strict=self.config.strict)

    def _run_parallel_analysis(
        self,
        files: list[pathlib.Path],
        rules_config: dict[str, Any],
        scope: str = "all",
    ) -> list[ModuleAnalysisResult]:
        """Runs parallel analysis on all Python files.

        Args:
            files: List of paths to analyze.
            rules_config: Rule-specific configuration overrides.

        Returns:
            A list of module analysis results.
        """
        return run_parallel_analysis(
            files,
            rules_config,
            scope,
            project_path=self.project_path,
            max_workers=self.max_workers,
            include_content=self.config.include_content,
        )

    def _chunk_files(self, files: list[pathlib.Path]) -> list[list[pathlib.Path]]:
        """Splits the file list into batches sized for the worker pool.

        Args:
            files: Files to analyze.

        Returns:
            A list of file batches (at least one, even for an empty input).
        """
        return chunk_files(files, self.max_workers)

    def _run_qgis_specific_checks(
        self,
        modules_data: list[ModuleAnalysisResult],
        rules_config: dict[str, Any],
        discovery: dict[str, Any],
    ) -> QGISChecksResult:
        """Runs QGIS-specific validation checks.

        Args:
            modules_data: Results from module analysis.
            rules_config: Configuration for rules.
            discovery: Discovery results from the project scanner.

        Returns:
            A QGISChecksResult containing findings from all checks.
        """
        return run_qgis_checks(modules_data, self.project_path, rules_config, discovery)

    def _run_semantic_analysis(
        self, modules_data: list[ModuleAnalysisResult]
    ) -> SemanticAnalysisResult:
        """Runs semantic analysis including dependencies and resources.

        Args:
            modules_data: List of analyzed module entries.

        Returns:
            A dictionary containing cycles, metrics, and missing resources.
        """
        return run_semantic_analysis(
            modules_data, self.project_path, self.project_type, self.matcher
        )

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

        self._refine_project_type(discovery)

        # 1. Parallel analysis (AST/Visitors) and 2. Ruff audit
        modules_data = self._maybe_parallel_analysis(files, rules_config, scope)
        ruff_findings, ruff_metadata = self._collect_ruff(scope)

        # 3. QGIS-specific checks and 4. Semantic analysis
        qgis_checks = self._collect_qgis_checks(scope, modules_data, rules_config, discovery)
        semantic = self._collect_semantic(scope, modules_data)

        scores = self.scoring.calculate_project_scores(
            modules_data, ruff_findings, qgis_checks, semantic
        )
        modules_data = self._filter_issues_by_scope(modules_data, scope)

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
        analyses["ruff_metadata"] = ruff_metadata

        save_reports(analyses, self.output_dir, self.config.generate_html)
        logger.info(f"✅ Analysis completed. Reports in: {self.output_dir}")

        return not self._strict_gate_failed(qgis_checks)

    def _refine_project_type(self, discovery: dict[str, Any]) -> None:
        """Refines the auto-detected project type from discovery metadata.

        Args:
            discovery: Results from :func:`discover_project_files`.
        """
        if self.config.project_type != "auto":
            return
        new_type = "qgis" if discovery["has_metadata"] else "generic"
        if new_type != self.project_type:
            logger.info(f"📁 Project type updated to: {new_type.upper()}")
            self.project_type = new_type

    def _maybe_parallel_analysis(
        self, files: list[pathlib.Path], rules_config: dict[str, Any], scope: str
    ) -> list[ModuleAnalysisResult]:
        """Runs the parallel AST analysis when the scope requires it.

        Args:
            files: Python files to analyze.
            rules_config: Rule-specific configuration overrides.
            scope: The analysis scope.

        Returns:
            The list of module analysis results (empty if out of scope).
        """
        if scope not in ("all", "i18n", "security", "performance", "architecture"):
            return []
        return self._run_parallel_analysis(files, rules_config, scope)

    def _collect_ruff(self, scope: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Runs the Ruff audit when the scope requires it.

        Args:
            scope: The analysis scope.

        Returns:
            A tuple of (findings, metadata).
        """
        metadata: dict[str, Any] = {
            "exit_code": None,
            "tool_unavailable": False,
            "command": "",
        }
        if scope not in ("all", "security", "performance"):
            return [], metadata

        result = self.run_ruff_audit()
        return (
            result["findings"],
            {
                "exit_code": result.get("exit_code"),
                "tool_unavailable": bool(result.get("tool_unavailable", False)),
                "command": result.get("command", ""),
            },
        )

    def _collect_qgis_checks(
        self,
        scope: str,
        modules_data: list[ModuleAnalysisResult],
        rules_config: dict[str, Any],
        discovery: dict[str, Any],
    ) -> QGISChecksResult | None:
        """Runs QGIS-specific checks when the scope and project type require it.

        Args:
            scope: The analysis scope.
            modules_data: Analyzed module results.
            rules_config: Rule-specific configuration overrides.
            discovery: Results from :func:`discover_project_files`.

        Returns:
            The QGIS checks result, or None when out of scope.
        """
        if self.project_type == "qgis" and scope in ("all", "metadata", "performance"):
            return self._run_qgis_specific_checks(modules_data, rules_config, discovery)
        return None

    def _collect_semantic(
        self, scope: str, modules_data: list[ModuleAnalysisResult]
    ) -> SemanticAnalysisResult:
        """Runs semantic analysis when the scope requires it.

        Args:
            scope: The analysis scope.
            modules_data: Analyzed module results.

        Returns:
            The semantic analysis result (empty when out of scope).
        """
        if scope in ("all", "architecture"):
            return self._run_semantic_analysis(modules_data)
        return {"cycles": [], "graph": {}, "metrics": {}, "missing_resources": []}

    def _strict_gate_failed(self, qgis_checks: QGISChecksResult | None) -> bool:
        """Evaluates the strict-mode gate for QGIS compliance.

        Args:
            qgis_checks: The QGIS checks result, if computed.

        Returns:
            True if strict mode is enabled and critical issues were found.
        """
        if not (self.config.fail_on_error and self.project_type == "qgis" and qgis_checks):
            return False

        compliance = qgis_checks["compliance"]
        structure = qgis_checks["structure"]
        metadata = qgis_checks["metadata"]
        failed = (
            int(compliance.get("issues_count", 0)) > 0
            or not structure.get("is_valid", True)
            or not metadata.get("is_valid", True)
            or not qgis_checks["package_constraints"].get("is_valid", True)
        )
        if failed:
            logger.error(
                "❌ Strict Mode: Critical QGIS compliance issues detected. Failing analysis."
            )
        return failed

    def _filter_issues_by_scope(
        self, modules_data: list[ModuleAnalysisResult], scope: str
    ) -> list[ModuleAnalysisResult]:
        """Filters issues in modules based on the analysis scope.

        Args:
            modules_data: List of module analysis results.
            scope: The analysis scope.

        Returns:
            Filtered list of module analysis results.
        """
        return filter_issues_by_scope(modules_data, scope)
