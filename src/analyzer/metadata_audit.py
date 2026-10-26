"""Metadata.txt rules for the QGIS portal profile.

The structural checks in :func:`analyzer.validators.validate_metadata` stay
focused on required fields; this module emits the catalog-backed
``METADATA_*`` findings consumed by the ``metadata`` scope and the portal
profile.
"""

from __future__ import annotations

import pathlib
import re
from typing import Any

from .rules.catalog_metadata import METADATA_RULE_IDS
from .rules.registry import get_rule

_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
_VERSION_PARTS_RE = re.compile(r"^(\d+)(?:\.(\d+))?")
_ALLOWED_CATEGORIES = {"raster", "vector", "database", "mesh", "web"}
_MIN_QGIS4_VERSION = (4, 0)


def _version_key(value: str) -> tuple[int, int] | None:
    """Return the ``(major, minor)`` key of a QGIS version string."""
    match = _VERSION_PARTS_RE.match(value.strip())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2) or 0)


def _parse_metadata(path: pathlib.Path) -> dict[str, tuple[str, int]]:
    """Parse ``metadata.txt`` into ``{key: (value, line_number)}``."""
    fields: dict[str, tuple[str, int]] = {}
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        fields.setdefault(key.strip().lower(), (value.strip(), lineno))
    return fields


def _finding(rule_id: str, line: int, message: str, code: str) -> dict[str, Any]:
    """Build one metadata finding using the catalog severity."""
    rule = get_rule(rule_id)
    return {
        "file": "metadata.txt",
        "line": line,
        "type": rule_id,
        "severity": rule.severity if rule else "medium",
        "message": message,
        "code": code,
    }


def audit_metadata_rules(metadata_path: pathlib.Path) -> list[dict[str, Any]]:
    """Evaluate the ``METADATA_*`` rules against a plugin's metadata.txt.

    Args:
        metadata_path: Path to ``metadata.txt``.

    Returns:
        A list of normalized findings (empty when the file is absent).
    """
    if not metadata_path.is_file():
        return []

    fields = _parse_metadata(metadata_path)
    findings: list[dict[str, Any]] = []

    version, version_line = fields.get("version", ("", 1))
    if not version or not _VERSION_RE.match(version):
        findings.append(
            _finding(
                "METADATA_VERSION",
                version_line,
                f"Metadata version '{version or 'missing'}' is not a numeric X.Y.Z value.",
                f"version={version}",
            )
        )

    repository, repository_line = fields.get("repository", ("", 1))
    if not repository:
        findings.append(
            _finding(
                "METADATA_REPOSITORY",
                repository_line,
                "Metadata does not declare a repository URL.",
                "repository=",
            )
        )

    maximum, maximum_line = fields.get("qgismaximumversion", ("", 1))
    if maximum:
        key = _version_key(maximum)
        if key is None:
            findings.append(
                _finding(
                    "METADATA_QGIS4",
                    maximum_line,
                    f"qgisMaximumVersion='{maximum}' is not numeric.",
                    f"qgisMaximumVersion={maximum}",
                )
            )
        elif key < _MIN_QGIS4_VERSION:
            findings.append(
                _finding(
                    "METADATA_QGIS4",
                    maximum_line,
                    f"qgisMaximumVersion={maximum} is below 4.0.",
                    f"qgisMaximumVersion={maximum}",
                )
            )

    if "supportsqt6" in fields:
        value, line = fields["supportsqt6"]
        findings.append(
            _finding(
                "METADATA_SUPPORTS_QT6",
                line,
                "The deprecated supportsQt6 flag is present.",
                f"supportsQt6={value}",
            )
        )

    category, category_line = fields.get("category", ("", 1))
    if not category or category.lower() not in _ALLOWED_CATEGORIES:
        findings.append(
            _finding(
                "METADATA_CATEGORY",
                category_line,
                f"Metadata category '{category or 'missing'}' is not one of "
                "Raster/Vector/Database/Mesh/Web.",
                f"category={category}",
            )
        )

    return findings


__all__ = ["METADATA_RULE_IDS", "audit_metadata_rules"]
