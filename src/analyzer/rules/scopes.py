"""Single source of truth for analysis scope → rule-id mappings.

Consumed by both the engine's issue filtering and the visitors' reporting gate,
so adding a rule to a scope only requires editing this module.
"""

from __future__ import annotations

SCOPE_RULES: dict[str, set[str]] = {
    "i18n": {"MISSING_I18N"},
    "security": {
        # standards_visitor
        "UNSAFE_SUBPROCESS",
        # security_rules (Bandit-inspired registry)
        "B102",  # exec
        "B301",  # pickle.load
        "B307",  # eval
        "B602",  # subprocess shell=True
        "B608",  # SQL injection
        "HARDCODED_SECRET",
        # SecretScanner
        "AWS_KEY",
        "GOOGLE_API_KEY",
        "TWILIO_KEY",
        "GENERIC_SECRET",
        "HIGH_ENTROPY",
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
        "QT6_QAPP_USAGE",
        "QT6_QREGEXP_USAGE",
        "QT6_QDESKTOPWIDGET",
        "QT6_REMOVED_ENUM",
        "QT6_QFONTMETRICS_WIDTH",
        "QT6_QCOMBOBOX_ACTIVATED",
        "QT6_COMPILED_RESOURCES",
        "QT6_ADDACTION_MULTIARG",
        "QT6_QVARIANT_NULL",
        "QT6_QDATETIME_ARGS",
        "QT6_QDATETIME_QDATE",
    },
    "metadata": {
        "MANDATORY_CLEANUP",
        "OBSOLETE_API",
        "IFACE_AS_ARGUMENT",
    },
}
