"""QGIS-specific validation checks.

Extracted from :mod:`analyzer.engine` to keep the orchestrator within the
project's module-size limit. Aggregates QGIS compliance, plugin structure,
metadata, repository constraints and metadata URL checks.
"""

import pathlib
from typing import Any

from .scanner import ModuleAnalysisResult, audit_qgis_standards
from .scoring import QGISChecksResult
from .validators import (
    validate_metadata,
    validate_metadata_urls,
    validate_package_constraints,
    validate_plugin_structure,
)


def run_qgis_checks(
    modules_data: list[ModuleAnalysisResult],
    project_path: pathlib.Path,
    rules_config: dict[str, Any],
    discovery: dict[str, Any],
) -> QGISChecksResult:
    """Runs QGIS-specific validation checks.

    Args:
        modules_data: Results from module analysis.
        project_path: Root path of the project.
        rules_config: Configuration for rules.
        discovery: Discovery results from the project scanner.

    Returns:
        A QGISChecksResult containing findings from all checks.
    """
    metadata_file = project_path / "metadata.txt"
    compliance = audit_qgis_standards(modules_data, project_path, rules_config)
    structure = validate_plugin_structure(project_path)
    metadata = validate_metadata(metadata_file)

    # New Repository Constraints
    constraints = validate_package_constraints(discovery["total_size_mb"], discovery["binaries"])

    return {
        "compliance": compliance,
        "structure": structure,
        "metadata": metadata,
        "binaries": discovery["binaries"],
        "package_size": discovery["total_size_mb"],
        "package_constraints": constraints,
        "url_status": validate_metadata_urls(metadata.get("metadata", {})),
    }
