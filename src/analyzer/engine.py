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

"""Analysis engine orchestrating the scanner → visitors → aggregators pipeline."""

import pathlib
from collections.abc import Mapping
from typing import Any

from . import __version__
from .aggregators import (
    build_analysis_results,
    save_reports,
)
from .engine_config import ProjectConfig
from .flake8_audit import run_flake8_audit
from .module_cache import build_cache
from .parallel_analysis import chunk_files, run_parallel_analysis
from .qgis_checks import run_qgis_checks, strict_gate_failed
from .ruff_audit import run_ruff_audit as _run_ruff_audit
from .scanner import ModuleAnalysisResult
from .scope_filter import filter_issues_by_scope
from .scoring import (
    QGISChecksResult,
    ScoringEngine,
    SemanticAnalysisResult,
)
from .security_audit import collect_native_findings, meets_fail_on
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


class ProjectAnalyzer:
    """Orchestrates the scanner → visitors → aggregators analysis pipeline."""

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
        raw_linters = raw_config.get("linters", ["ruff"])
        if isinstance(raw_linters, str):
            raw_linters = [item.strip() for item in raw_linters.split(",")]
        raw_security_tools = raw_config.get("security_tools", ["native"])
        if isinstance(raw_security_tools, str):
            raw_security_tools = [item.strip() for item in raw_security_tools.split(",")]
        raw_deep_security = raw_config.get("deep_security")
        self.config = ProjectConfig(
            strict=raw_config.get("strict", False),
            generate_html=raw_config.get("generate_html", True),
            fail_on_error=raw_config.get("fail_on_error", False),
            project_type=raw_config.get("project_type", "auto"),
            rules=raw_config.get("rules", {}),
            include_content=raw_config.get("include_content", False),
            workers=effective_workers,
            cache=raw_config.get("cache", True),
            linters=[item for item in raw_linters if item],
            deep_security=True if raw_deep_security is None else bool(raw_deep_security),
            deep_security_configured=raw_deep_security is not None,
            security_tools=[item for item in raw_security_tools if item],
            security_fail_on=raw_config.get("security_fail_on", "critical"),
            metadata_rules=bool(raw_config.get("metadata_rules", True)),
            fail_on=raw_config.get("fail_on", "none"),
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
            deep_security=self.config.deep_security,
            cache=build_cache(
                enabled=self.config.cache,
                project_path=self.project_path,
                output_dir=self.output_dir,
                analyzer_version=__version__,
                rules_config=self.config.rules,
                scope=scope,
                include_content=self.config.include_content,
                project_type=self.project_type,
                deep_security=self.config.deep_security,
            ),
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
        *,
        metadata_rules: bool = True,
    ) -> QGISChecksResult:
        """Runs QGIS-specific validation checks.

        Args:
            modules_data: Results from module analysis.
            rules_config: Configuration for rules.
            discovery: Discovery results from the project scanner.
            metadata_rules: Whether to include the catalog-backed METADATA_* rules.

        Returns:
            A QGISChecksResult containing findings from all checks.
        """
        return run_qgis_checks(
            modules_data,
            self.project_path,
            rules_config,
            discovery,
            metadata_rules=metadata_rules,
        )

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

        # Qt-specific ``MISSING_I18N`` is noise under "all" for generic projects;
        # an explicit ``analyze i18n`` and any profile override still win.
        if self.project_type == "generic":
            rules_config = {"MISSING_I18N": "ignore", **rules_config}

        # 1. Parallel analysis (AST/Visitors) and 2. lint audits
        modules_data = self._maybe_parallel_analysis(files, rules_config, scope)
        ruff_findings, ruff_metadata, flake8_findings, flake8_metadata = self._collect_linters(
            scope
        )

        # 3. QGIS-specific checks and 4. Semantic analysis
        qgis_checks = self._collect_qgis_checks(scope, modules_data, rules_config, discovery)
        semantic = self._collect_semantic(scope, modules_data)

        scores = self.scoring.calculate_project_scores(
            modules_data,
            ruff_findings,
            qgis_checks,
            semantic,
            flake8_findings=flake8_findings,
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
            flake8_findings=flake8_findings,
        )
        analyses["ruff_metadata"] = ruff_metadata
        analyses["flake8_metadata"] = flake8_metadata

        save_reports(analyses, self.output_dir, self.config.generate_html)
        logger.info(f"✅ Analysis completed. Reports in: {self.output_dir}")

        fail_on_failed = self._fail_on_gate(analyses)
        return not (self._strict_gate_failed(qgis_checks) or fail_on_failed)

    def _fail_on_gate(self, analyses: Mapping[str, Any]) -> bool:
        """Evaluate the profile ``fail_on`` security threshold.

        Args:
            analyses: The consolidated analysis result.

        Returns:
            True when a security finding reaches ``[project].fail_on``.
        """
        if self.config.fail_on in ("", "none"):
            return False
        return meets_fail_on(collect_native_findings(analyses), self.config.fail_on)

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

    def _collect_linters(
        self, scope: str
    ) -> tuple[
        list[dict[str, Any]],
        dict[str, Any],
        list[dict[str, Any]],
        dict[str, Any],
    ]:
        """Runs the configured lint audits when the scope requires them.

        Args:
            scope: The analysis scope.

        Returns:
            A tuple ``(ruff_findings, ruff_metadata, flake8_findings,
            flake8_metadata)``. Metadata is always present so the JSON output
            contract is stable even when a linter is not requested.
        """
        ruff_metadata: dict[str, Any] = {
            "exit_code": None,
            "tool_unavailable": False,
            "command": "",
        }
        flake8_metadata: dict[str, Any] = {
            "exit_code": None,
            "tool_unavailable": False,
            "command": "",
            "formatter": "",
        }
        if scope not in ("all", "security", "performance"):
            return [], ruff_metadata, [], flake8_metadata

        linters = {item.strip().lower() for item in self.config.linters if item.strip()}
        ruff_findings: list[dict[str, Any]] = []
        flake8_findings: list[dict[str, Any]] = []

        if "ruff" in linters:
            result = self.run_ruff_audit()
            ruff_findings = result["findings"]
            ruff_metadata = {
                "exit_code": result.get("exit_code"),
                "tool_unavailable": bool(result.get("tool_unavailable", False)),
                "command": result.get("command", ""),
            }

        if "flake8" in linters:
            result = run_flake8_audit(self.project_path)
            flake8_findings = result["findings"]
            flake8_metadata = {
                "exit_code": result.get("exit_code"),
                "tool_unavailable": bool(result.get("tool_unavailable", False)),
                "command": result.get("command", ""),
                "formatter": result.get("formatter", ""),
            }

        return ruff_findings, ruff_metadata, flake8_findings, flake8_metadata

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
            include_metadata = self.config.metadata_rules and scope in ("all", "metadata")
            return self._run_qgis_specific_checks(
                modules_data, rules_config, discovery, metadata_rules=include_metadata
            )
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
        return strict_gate_failed(
            fail_on_error=self.config.fail_on_error,
            project_type=self.project_type,
            qgis_checks=qgis_checks,
        )

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
