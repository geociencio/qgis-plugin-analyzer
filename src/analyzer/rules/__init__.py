"""Rules package for the QGIS Plugin Analyzer."""

from .qgis_rules import I18N_METHODS, get_qgis_audit_rules

__all__ = [
    "get_qgis_audit_rules",
    "I18N_METHODS",
]
