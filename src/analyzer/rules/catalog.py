"""Declarative rule catalog for the QGIS Plugin Analyzer.

This module is the single source of truth for **rule metadata**. The entries
themselves are split across :mod:`analyzer.rules.catalog_core` and
:mod:`analyzer.rules.catalog_platform` and assembled into :data:`RAW_RULES`
here. It contains only data and stdlib imports, so it is safe to import from hot
paths (e.g. the AST visitors). The runtime objects live in
:mod:`analyzer.rules.registry`; the Markdown renderer lives in
:mod:`analyzer.rules.render`.
"""

from __future__ import annotations

from .catalog_builder import RuleTuple
from .catalog_core import RULES_CORE
from .catalog_platform import RULES_PLATFORM

# Ordered catalog sections: (key, number, title, intro-markdown).
CATEGORY_ORDER: list[tuple[str, str, str, str]] = [
    ("i18n", "1", "Internationalization (i18n)", ""),
    ("obsolete_api", "2", "Obsolete API and Precision", ""),
    ("threading_security", "3", "Threading Security & Safety", ""),
    ("security", "4", "Security", ""),
    ("resource_management", "5", "Resource Management", ""),
    ("performance_metrics", "6", "Performance & Metrics", ""),
    ("architecture_standards", "7", "Architecture & Standards", ""),
    ("qt6_migration", "7.1", "Qt6 Migration (QGS4xx parity)", ""),
    ("general_python", "8", "General Python Best Practices", ""),
    (
        "patterns",
        "9",
        "Design Patterns & Anti-patterns",
        "Detected by `PatternsVisitor` (`src/analyzer/visitors/patterns_visitor.py`). "
        "All are **informational** (`low`) and suppressible with `# noqa`.",
    ),
]

# Non-issue informational rows rendered in the trailing "Informational" table.
INFORMATIONAL_ROWS: list[tuple[str, str]] = [
    (
        "`patterns` (output field)",
        "Design patterns detected per module: `singleton`, `factory`, `observer`, "
        "`strategy`, `decorator`.",
    ),
    (
        "`optimizations` (output field)",
        "Generic suggestions: `module_too_large` (> 400 lines), `complexity_refactoring` "
        "(high-complexity module with many functions).",
    ),
    (
        "`halstead` (per-module metric)",
        "Halstead `vocabulary`, `length`, `volume`, `difficulty`, `effort`.",
    ),
]

# (id, severity, category, description, recommendation, scopes, sources, emitted)
RAW_RULES: list[RuleTuple] = [*RULES_CORE, *RULES_PLATFORM]
