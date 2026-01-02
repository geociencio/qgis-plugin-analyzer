"""Modernization and research-based quality rules.

This module defines rules for detecting modernization opportunities and
adherence to industry-standard Python practices (Google, Microsoft, PSF).
"""

from typing import Any, Dict, List


def get_modernization_rules() -> List[Dict[str, Any]]:
    """Returns the modernization and research-based rule catalog.

    Returns:
        A list of dictionaries defining quality and modernization rules,
        including messages and severity levels.
    """
    return [
        {
            "id": "MISSING_DOCSTRING",
            "message": "Public module, class, or function missing docstring (PEP 257).",
            "severity": "medium",
        },
        {
            "id": "MISSING_TYPE_HINTS",
            "message": "Function signature missing type annotations (PEP 484).",
            "severity": "low",
        },
        {
            "id": "NON_PYTHONIC_LOOP",
            "message": "Manual loop counter detected. Use enumerate() for clean, Pythonic code.",
            "severity": "medium",
        },
    ]
