"""QGIS-specific audit rules and patterns.

This module defines rules for detecting common pitfalls and technical debt
in PyQGIS plugins.
"""

import re
from typing import Any, Dict, List


def get_qgis_audit_rules() -> List[Dict[str, Any]]:
    """Returns the QGIS audit rule catalog.

    Returns:
        A list of dictionaries defining QGIS-specific rules, including
        patterns, messages, and severity levels.
    """
    return [
        {
            "id": "UNPRECISE_LAYER",
            "pattern": re.compile(r"mapLayersByName\("),
            "message": "mapLayersByName() can be imprecise. Consider mapLayers() or unique IDs.",
            "severity": "medium",
        },
        {
            "id": "UNSAFE_THREAD",
            "pattern": re.compile(r"\bthreading\.Thread\("),
            "message": "threading.Thread usage detected. Prefer QgsTask or QThread.",
            "severity": "high",
        },
        {
            "id": "MANUAL_RESOURCE_PATH",
            "pattern": re.compile(
                r"QIcon\(\s*['\"](?!\s*:\/)[^'\"]*?(?:icons|images|ui)/"
            ),
            "message": "Manual resource path detected. Use :/plugins/...",
            "severity": "medium",
        },
        {
            "id": "PRINT_STATEMENT",
            "pattern": re.compile(r"^[^#]*\bprint\("),
            "message": "print() usage detected. Use QgsMessageLog.",
            "severity": "low",
        },
        {
            "id": "OBSOLETE_VARIANT",
            "pattern": re.compile(
                r"QVariant\.(?:String|Int|Double|LongLong|Bool|Date|Time|DateTime)"
            ),
            "message": "Obsolete QVariant type constants detected. Use QMetaType or native types.",
            "severity": "medium",
        },
        {
            "id": "UNSAFE_SUBPROCESS",
            "pattern": re.compile(
                r"\bsubprocess\.(?:run|call|Popen|check_call|check_output)\("
            ),
            "message": "Potential unsafe subprocess usage. Avoid shell=True and ensure arguments are properly quoted.",
            "severity": "high",
        },
        {
            "id": "BLOCKING_NETWORK_CALL",
            "pattern": re.compile(
                r"\b(?:requests\.(?:get|post|put|delete|patch)|urllib\.request\.urlopen)\("
            ),
            "message": "Synchronous network call detected. UI blocking risk. Use QgsTask or QNetworkAccessManager.",
            "severity": "high",
        },
    ]


# Methods that require translation in QGIS
I18N_METHODS = {
    "setText",
    "setWindowTitle",
    "setTitle",
    "setToolTip",
    "setPlaceholderText",
    "setTabText",
}
