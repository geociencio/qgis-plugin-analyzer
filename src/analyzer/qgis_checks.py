"""QGIS-specific validation checks.

Extracted from :mod:`analyzer.engine` to keep the orchestrator within the
project's module-size limit. Aggregates QGIS compliance, plugin structure,
metadata, repository constraints and metadata URL checks.
"""

import pathlib
from typing import Any

from .metadata_audit import audit_metadata_rules
from .scanner import ModuleAnalysisResult, audit_qgis_standards
from .scoring import QGISChecksResult
from .utils import logger
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
    *,
    metadata_rules: bool = True,
) -> QGISChecksResult:
    """Runs QGIS-specific validation checks.

    Args:
        modules_data: Results from module analysis.
        project_path: Root path of the project.
        rules_config: Configuration for rules.
        discovery: Discovery results from the project scanner.
        metadata_rules: Whether to append the catalog-backed ``METADATA_*``
            findings (metadata scope / portal profile).

    Returns:
        A QGISChecksResult containing findings from all checks.
    """
    metadata_file = project_path / "metadata.txt"
    compliance = audit_qgis_standards(modules_data, project_path, rules_config)
    if metadata_rules:
        metadata_findings = audit_metadata_rules(metadata_file)
        compliance["issues"].extend(metadata_findings)
        compliance["issues_count"] = len(compliance["issues"])
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


def strict_gate_failed(
    *,
    fail_on_error: bool,
    project_type: str,
    qgis_checks: QGISChecksResult | None,
) -> bool:
    """Evaluates the strict-mode gate for QGIS compliance.

    Args:
        fail_on_error: Whether strict mode is enabled.
        project_type: Detected project type.
        qgis_checks: The QGIS checks result, if computed.

    Returns:
        True if strict mode is enabled and critical issues were found.
    """
    if not (fail_on_error and project_type == "qgis" and qgis_checks):
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
        logger.error("❌ Strict Mode: Critical QGIS compliance issues detected. Failing analysis.")
    return failed
