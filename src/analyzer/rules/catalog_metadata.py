"""Catalog entries for QGIS metadata.txt rules (portal metadata scope)."""

from __future__ import annotations

from .catalog_builder import RuleTuple, rule

RULES_METADATA: list[RuleTuple] = [
    rule(
        "METADATA_REPOSITORY",
        "medium",
        "metadata",
        "Plugin metadata does not declare a repository URL.",
        "Add `repository=https://...` to `metadata.txt` (required for the official repository).",
        ("metadata",),
        ("metadata",),
    ),
    rule(
        "METADATA_VERSION",
        "high",
        "metadata",
        "Metadata version is missing or is not a numeric `X.Y.Z` value.",
        "Use a numeric semantic version (e.g. `version=1.2.3`) in `metadata.txt`.",
        ("metadata",),
        ("metadata",),
    ),
    rule(
        "METADATA_QGIS4",
        "medium",
        "metadata",
        "`qgisMaximumVersion` is below 4.0.",
        "Set `qgisMaximumVersion=4.0` (or higher) to advertise QGIS 4 readiness.",
        ("metadata",),
        ("metadata",),
    ),
    rule(
        "METADATA_SUPPORTS_QT6",
        "low",
        "metadata",
        "The deprecated `supportsQt6` flag is present.",
        "Remove `supportsQt6`; Qt6 support is implied by the QGIS/Qt version, not this flag.",
        ("metadata",),
        ("metadata",),
    ),
    rule(
        "METADATA_CATEGORY",
        "medium",
        "metadata",
        "Metadata category is missing or is not one of Raster/Vector/Database/Mesh/Web.",
        "Set `category` to one of `Raster`, `Vector`, `Database`, `Mesh` or `Web`.",
        ("metadata",),
        ("metadata",),
    ),
]

METADATA_RULE_IDS: frozenset[str] = frozenset(row[0] for row in RULES_METADATA)
